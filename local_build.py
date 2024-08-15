#!/usr/bin/env python3

import os
import subprocess
import shutil
import paramiko
import asyncio
from git import Repo
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable
import time
from rich.console import Console
from rich.progress import Progress
from dataclasses import dataclass, field

# 全局变量与数据结构
MAX_CONCURRENT_QUEUES: int = 4  # 最大并发队列数
TASK_QUEUES: List[List['CompileTask']] = [[] for _ in range(MAX_CONCURRENT_QUEUES)]  # 任务队列数组

console = Console()

@dataclass
class CompileTask:
    """
    Base class for all compile tasks.
    Manages execution of compile commands, logging, and time tracking.
    """
    name: str
    log_file: str = field(init=False)
    start_time: float = field(default=0.0, init=False)
    end_time: float = field(default=0.0, init=False)

    def __post_init__(self):
        """
        Initialize the log file path based on the task name.
        """
        self.log_file = f"{self.name}.log"

    def log_message(self, message: str) -> None:
        """
        Log a message to both the console and the log file.

        Parameters:
            message (str): The message to log.
        """
        console.log(message)
        with open(self.log_file, "a") as log:
            log.write(message + "\n")

    def run_command(self, command: List[str], capture_env: bool = False, cwd: Path = None) -> None:
        """
        Run a command, log its output, and optionally capture environment variables.

        Parameters:
            command (List[str]): The command to execute as a list of strings.
            capture_env (bool): Whether to capture environment variables from the command.
            cwd (Path): The working directory for the command.
        """
        self.log_message(f"[Executing] {' '.join(command)}")
        
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd, env=os.environ
        )

        stdout, stderr = process.communicate()

        with open(self.log_file, "a") as log:
            if stdout:
                log.write("[Output]\n" + stdout + "\n")
            if stderr:
                log.write("[Error]\n" + stderr + "\n")

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        # Capture and update environment variables if required
        if capture_env:
            for line in stdout.splitlines():
                key, _, value = line.partition("=")
                os.environ[key] = value

    def run(self) -> None:
        """
        Execute the compile task by running all specified commands sequentially.
        Logs output to a file and tracks execution time.
        """
        self.start_time = time.time()
        self.log_message(f"Starting task: {self.name}")

        try:
            self.execute_steps()
        except subprocess.CalledProcessError as e:
            self.log_message(f"[Error] Task {self.name} failed: {e}")
            return
        
        self.end_time = time.time()
        self.log_message(f"Completed task: {self.name} in {self.end_time - self.start_time:.2f} seconds")

    def execute_steps(self) -> None:
        """
        Execute all steps for the task.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement the execute_steps method")


class NebulaCompileTask(CompileTask):
    """
    Compile task for Nebula module.
    Handles the entire compilation process with detailed logging.
    """
    def execute_steps(self) -> None:
        """
        Execute all steps for the Nebula compile task.
        """
        # Step 1: Set environment variable
        os.environ['NO_PIPENV_SHELL'] = '1'
        self.log_message("Set NO_PIPENV_SHELL=1")

        # Step 2: Source the environment setup script and capture environment variables
        script_path = Path.home() / "grpower/scripts/env.sh"
        if not script_path.exists():
            raise FileNotFoundError(f"Script {script_path} not found.")
        self.run_command(["bash", "-c", f"source {script_path} && env"], capture_env=True)

        # Step 3: Clean workspace directories
        workspace_path = Path.home() / "grpower/workspace"
        paths_to_remove = [
            workspace_path / "buildroot-pvt8675",
            workspace_path / "nebula-ree",
            workspace_path / "nebula/out"
        ]
        for path in paths_to_remove:
            if path.exists():
                shutil.rmtree(path)
                self.log_message(f"Removed directory {path}")

        # Step 4: Clean the GRT repository
        grt_path = Path.home() / "grt"
        if grt_path.exists():
            repo = Repo(grt_path)
            repo.git.reset('--hard')
            repo.git.clean('-ffd')
            self.log_message(f"Cleaned repository at {grt_path}")

        # Step 5: Build Nebula
        grpower_path = Path.home() / "grpower"
        if grpower_path.exists():
            self.run_command(["gr-nebula.py", "build"], cwd=grpower_path)
            self.run_command(["gr-nebula.py", "export-buildroot"], cwd=grpower_path)

class HeeExportTask(CompileTask):
    """
    Compile task for Hee module.
    Handles the export of Hee images.
    """
    def execute_steps(self) -> None:
        """
        Execute all steps for the Hee export task.
        """
        # Set product name
        self.run_command(["gr-android.py", "set-product", "--product-name", "pvt8675"])

        # Export Nebula images
        self.run_command([
            "gr-android.py", "buildroot", "export_nebula_images", 
            "-o", "/home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images"
        ])

class SDKCompileTask(CompileTask):
    """
    Compile task for SDK module.
    Handles the configuration, building, and packaging of SDK and Hee images.
    """
    def execute_steps(self) -> None:
        """
        Execute all steps for the SDK compile task.
        """
        sdk_path = Path.home() / "grt/thyp-sdk"

        # Clean the workspace
        repo = Repo(sdk_path)
        repo.git.clean('-ffd')
        self.log_message(f"Cleaned workspace at {sdk_path}")

        # Configure SDK
        self.run_command(["./configure.sh", "/home/nebula/grt/nebula-sdk/"], cwd=sdk_path)

        # Build SDK and package Hee images
        self.run_command(["./build_all.sh"], cwd=sdk_path)

class SdkHeeExportTask(CompileTask):
    """
    Task for exporting SDK and Hee images.
    Handles copying multiple files to the specified directories.
    """
    def execute_steps(self) -> None:
        """
        Execute all steps for exporting SDK and Hee images.
        """
        temp_dir = Path.home() / "grt/teetemp"
        sdk_path = Path.home() / "grt/thyp-sdk"
        yocto_prebuilt_path = Path.home() / "yocto/prebuilt"

        copy_tasks = [
            (sdk_path / "products/mt8678-mix/out/gz.img", yocto_prebuilt_path / "bsp/collect-bins/mt6991/"),
            (sdk_path / "products/mt8678-mix/out/gz.img", yocto_prebuilt_path / "bsp/collect-bins/mt6991/auto8678p1_64_hyp/"),
            (sdk_path / "products/mt8678-mix/out/gz.img", yocto_prebuilt_path / "bsp/collect-bins/mt6991/auto8678p1_64_kde_hyp/"),
            (sdk_path / "vmm/out/nbl_vmm", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "vmm/out/nbl_vm_ctl", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "vmm/out/nbl_vm_srv", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "vmm/out/tipc_server", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "vmm/out/libvmm.so", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "./third_party/prebuilts/libluajit/lib64/libluajit.so", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "products/mt8678-mix/guest-configs/uos_alps_pv8678.json", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "./products/mt8678-mix/guest-configs/uos_alps_pv8678.lua", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "vmm/nbl_vm_srv/data/vm_srv_cfg_8678.pb.txt", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "vmm/nbl_vmm/data/uos_mtk8678/uos_bootloader_lk2.pb.txt", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "vmm/nbl_vmm/data/vm_audio_cfg.pb.txt", yocto_prebuilt_path / "hypervisor/grt/"),
            (sdk_path / "vmm/nbl_vmm/data/vm_audio_shared_irq.pb.txt", yocto_prebuilt_path / "hypervisor/grt/"),
        ]

        for src, dst in copy_tasks:
            dst.parent.mkdir(parents=True, exist_ok=True)  # Ensure destination directory exists
            shutil.copy(src, dst)
            self.log_message(f"Copied {src} to {dst}")

class TeeExportTask(CompileTask):
    """
    Compile task for Tee module.
    Handles the export and packaging of Tee images.
    """
    def execute_steps(self) -> None:
        """
        Execute all steps for the Tee export and packaging task.
        """
        # Set product name
        self.run_command(["gr-android.py", "set-product", "--product-name", "pvt8675_tee"])

        # Create temporary directory
        temp_dir = Path.home() / "grt/teetemp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        self.log_message(f"Created directory {temp_dir}")

        # Export Nebula images
        self.run_command([
            "gr-android.py", "buildroot", "export_nebula_images", 
            "-o", str(temp_dir)
        ])

        # Copy exported files
        dest_dir = Path.home() / "alps/vendor/mediatek/proprietary/trustzone/grt/source/common/kernel/"
        for file in temp_dir.glob("nebula*.bin"):
            shutil.copy(file, dest_dir)
            self.log_message(f"Copied {file} to {dest_dir}")

        # Clean and prepare for building
        alps_path = Path.home() / "alps"
        out_dir = alps_path / "out"
        if out_dir.exists():
            shutil.rmtree(out_dir)
            self.log_message(f"Removed directory {out_dir}")
        self.run_command(["bash", "-c", "source build/envsetup.sh && export OUT_DIR=out && lunch vext_auto8678p1_64_bsp_vm-userdebug && make vext_images"], cwd=alps_path)

        # Split build images
        self.run_command([
            "python", "out_sys/target/product/mssi_auto_64_cn_armv82/images/split_build.py", 
            "--system-dir", "out_sys/target/product/mssi_auto_64_cn_armv82/images", 
            "--vendor-dir", "out_hal/target/product/mgvi_auto_64_armv82_wifi_vm/images", 
            "--kernel-dir", "out_krn/target/product/mgk_64_k61_auto_vm/images", 
            "--vext-dir", "out/target/product/auto8678p1_64_bsp_vm/images", 
            "--output-dir", "out/target/product/auto8678p1_64_bsp_vm/merged"
        ], cwd=alps_path)

class GrtBeCompileTask(CompileTask):
    """
    Compile task for Grt_be module.
    Handles the cleaning, building, and exporting of Grt_be.
    """
    def execute_steps(self) -> None:
        """
        Execute all steps for the Grt_be compile task.
        """
        grt_be_path = Path.home() / "grt_be/workspace"

        # Clean and reset the repository
        repo = Repo(grt_be_path)
        repo.git.reset('--hard')
        repo.git.clean('-ffd')
        self.log_message(f"Cleaned repository at {grt_be_path}")

        # Build the Grt_be module
        build_script = grt_be_path / "build.sh"
        self.run_command([str(build_script)])

        # Copy the built files
        sdk_path = Path.home() / "grt/thyp-sdk"
        shutil.copy(grt_be_path / "out/gpu_server", sdk_path / "../../yocto/prebuilt/hypervisor/grt/")
        shutil.copy(grt_be_path / "out/video_server", sdk_path / "../../yocto/prebuilt/hypervisor/grt/")
        self.log_message(f"Copied files to {sdk_path / '../../yocto/prebuilt/hypervisor/grt/'}")

class AndroidCompileTask(CompileTask):
    """
    Compile task for Android module.
    Handles the cleaning, compilation, and packaging of Android components.
    """
    def __init__(self):
        super().__init__(name="Android Compile")

    def execute_steps(self) -> None:
        """
        Execute all steps for the Android compile task, including cleaning, compiling, and packaging.
        """
        alps_path = Path.home() / "alps"
        
        # Step 1: Clean directories and reset git repositories
        paths_to_clean = [
            alps_path / "out",
            alps_path / "out_hal",
            alps_path / "out_krn",
            alps_path / "out_sys"
        ]
        logs_to_remove = [
            alps_path / "hal.log",
            alps_path / "krn.log",
            alps_path / "out.log",
            alps_path / "sys.log",
            alps_path / "vext.log"
        ]

        for path in paths_to_clean:
            if path.exists():
                shutil.rmtree(path)
                self.log_message(f"Removed directory {path}")

        for log in logs_to_remove:
            if log.exists():
                log.unlink()
                self.log_message(f"Removed log file {log}")

        # Reset and clean all git repositories
        repo = Repo(alps_path)
        repo.git.reset('--hard')
        repo.git.clean('-ffd')
        self.log_message(f"Reset and cleaned repository at {alps_path}")

        # Step 2: Concurrently execute compile commands
        compile_commands = [
            "source build/envsetup.sh && export OUT_DIR=out_sys && lunch sys_mssi_auto_64_cn_armv82-userdebug && make sys_images",
            "source build/envsetup.sh && export OUT_DIR=out_hal && lunch hal_mgvi_auto_64_armv82_wifi_vm-userdebug && make hal_images",
            "source build/envsetup.sh && export OUT_DIR=out_krn && lunch krn_mgk_64_k61_auto_vm-userdebug && make krn_images",
            "source build/envsetup.sh && export OUT_DIR=out && lunch vext_auto8678p1_64_bsp_vm-userdebug && make vext_images"
        ]

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.run_command, cmd, cwd=alps_path) for cmd in compile_commands]
            for future in as_completed(futures):
                if future.result().returncode != 0:
                    raise subprocess.CalledProcessError(future.result().returncode, future.result().args)

        # Step 3: Execute packaging command
        package_command = [
            "python", "out_sys/target/product/mssi_auto_64_cn_armv82/images/split_build.py",
            "--system-dir", "out_sys/target/product/mssi_auto_64_cn_armv82/images",
            "--vendor-dir", "out_hal/target/product/mgvi_auto_64_armv82_wifi_vm/images",
            "--kernel-dir", "out_krn/target/product/mgk_64_k61_auto_vm/images",
            "--vext-dir", "out/target/product/auto8678p1_64_bsp_vm/images",
            "--output-dir", "out/target/product/auto8678p1_64_bsp_vm/merged"
        ]
        self.run_command(package_command, cwd=alps_path)

class YoctoCompileTask(CompileTask):
    """
    Compile task for Yocto module.
    Handles the cleaning, resetting, and compiling of Yocto, and exporting the images.
    """
    def execute_steps(self) -> None:
        """
        Execute all steps for the Yocto compile task, including cleaning, resetting, and compiling.
        """
        yocto_path = Path.home() / "yocto"

        # Step 1: Clean directories
        paths_to_clean = [
            yocto_path / "build",
            yocto_path / "sstate-cache"
        ]
        for path in paths_to_clean:
            if path.exists():
                shutil.rmtree(path)
                self.log_message(f"Removed directory {path}")

        # Step 2: Reset and clean all git repositories
        repo = Repo(yocto_path)
        repo.git.reset('--hard')
        repo.git.clean('-ffd')
        self.log_message(f"Reset and cleaned repository at {yocto_path}")

        # Step 3: Set environment variables for Yocto
        template_conf = yocto_path / "meta/meta-mediatek-mt8678/conf/templates/auto8678p1_64_hyp"
        os.environ['TEMPLATECONF'] = str(template_conf)
        self.log_message(f"Set TEMPLATECONF={template_conf}")

        os.environ['BB_DISABLE_NETWORK'] = '1'
        self.log_message("Set BB_DISABLE_NETWORK=1")

        # Step 4: Define and run the source and bitbake commands
        commands = (
            "source meta/poky/oe-init-build-env",
            "bitbake -k mtk-core-image-auto8678-hyp"
        )
        
        full_command = " && ".join(commands)
        
        self.run_command(["bash", "-c", full_command], cwd=yocto_path)

class ImageExportToHostTask(CompileTask):
    """
    Task for exporting images to the host and transferring them to a remote server via SCP with async support.
    """
    def __init__(self, max_workers: int = 2):
        """
        Initialize the task with a specific number of workers for concurrent SCP transfers.
        
        Parameters:
            max_workers (int): The maximum number of concurrent SCP transfers.
        """
        super().__init__(name="Image Export to Host")
        self.max_workers = max_workers

    def execute_steps(self) -> None:
        """
        Execute all steps for exporting images to the host and transferring them via SCP.
        """
        alps_merged_path = Path.home() / "alps/out/target/product/auto8678p1_64_bsp_vm/merged"
        yocto_images_path = Path.home() / "yocto/build/tmp/deploy/images/auto8678p1_64_hyp"
        
        # Files to copy
        files_to_copy = [
            "boot.img",
            "dtbo.img",
            "init_boot.img",
            "super.img",
            "userdata.img",
            "vendor_boot.img",
            "vbmeta.img",
            "vbmeta_system.img",
            "vbmeta_vendor.img",
            "scp.img",
            "tee.img"
        ]

        # Copy files to yocto images directory
        for file_name in files_to_copy:
            src = alps_merged_path / file_name
            dst = yocto_images_path / file_name
            shutil.copy(src, dst)
            self.log_message(f"Copied {src} to {dst}")

        # Prepare directory for SCP transfer
        scp_dir = Path.home() / "78images"
        if scp_dir.exists():
            shutil.rmtree(scp_dir)
        scp_dir.mkdir(parents=True, exist_ok=True)
        
        shutil.copytree(yocto_images_path, scp_dir / yocto_images_path.name, symlinks=True)
        self.log_message(f"Prepared {scp_dir} for SCP transfer")

        # Run asynchronous SCP transfer
        asyncio.run(self.async_scp_transfer(scp_dir / yocto_images_path.name, "Administrator@100.64.0.3", "D:/78images/auto8678p1_64_hyp_gpu_0813_zhoubo"))

    async def async_scp_transfer(self, source_path: Path, remote_user_host: str, remote_path: str) -> None:
        """
        Asynchronously transfer files via SCP to a remote server.

        Parameters:
            source_path (Path): The local source path to transfer.
            remote_user_host (str): The remote user and host (e.g., user@hostname).
            remote_path (str): The remote destination path.
        """
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(remote_user_host.split("@")[1], username=remote_user_host.split("@")[0])
        
        sftp = ssh.open_sftp()

        async def transfer_file(local_path: Path, remote_path: str):
            sftp.put(str(local_path), remote_path)
            self.log_message(f"Transferred {local_path} to {remote_path}")

        try:
            tasks = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                loop = asyncio.get_event_loop()
                for item in source_path.glob("**/*"):
                    if item.is_file():
                        remote_item_path = f"{remote_path}/{item.relative_to(source_path.parent)}"
                        tasks.append(loop.run_in_executor(executor, transfer_file, item, remote_item_path))
                
                await asyncio.gather(*tasks)
        finally:
            sftp.close()
            ssh.close()


def run_queue(queue: List[CompileTask]) -> None:
    """
    Execute all tasks in a single queue sequentially.
    
    Parameters:
        queue (List[CompileTask]): A list of tasks to execute in sequence.
    """
    for task in queue:
        task.run()

def execute_all_queues_concurrently(task_queues: List[List[CompileTask]], max_concurrent_queues: int) -> None:
    """
    Execute multiple task queues concurrently, with each queue running its tasks sequentially.
    
    Parameters:
        task_queues (List[List[CompileTask]]): List of task queues to execute.
        max_concurrent_queues (int): Maximum number of task queues to execute concurrently.
    """
    with ThreadPoolExecutor(max_workers=max_concurrent_queues) as executor:
        futures = {executor.submit(run_queue, queue): queue for queue in task_queues if queue}
        for future in as_completed(futures):
            queue = futures[future]
            try:
                future.result()
            except Exception as e:
                console.log(f"[bold red]Error in queue execution: {e}[/bold red]")

if __name__ == "__main__":
    # 示例：手动将需要执行的模块任务添加到不同的队列中
    TASK_QUEUES[0].append(NebulaCompileTask())
    # TASK_QUEUES[0].append(HeeExportTask())
    # TASK_QUEUES[0].append(SDKCompileTask())
    # TASK_QUEUES[0].append(SdkHeeExportTask())
    # TASK_QUEUES[0].append(TeeExportTask())    
    # TASK_QUEUES[0].append(GrtBeCompileTask())  # 可与 Nebula 任务在同一个队列中顺序执行
    # TASK_QUEUES[0].append(YoctoCompileTask())  # Yocto 编译及导出任务
    # TASK_QUEUES[0].append(ImageExportToHostTask())
    # TASK_QUEUES[1].append(AndroidCompileTask())  # Android 编译任务
    # 执行所有任务队列，最多并发 MAX_CONCURRENT_QUEUES 个任务队列
    execute_all_queues_concurrently(TASK_QUEUES, MAX_CONCURRENT_QUEUES)
