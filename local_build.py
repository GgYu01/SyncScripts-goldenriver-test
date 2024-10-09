#!/usr/bin/env python3
import os
import subprocess
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Callable
from rich.console import Console
from rich.progress import Progress
from dataclasses import dataclass

# Console setup for better output visualization
console = Console()

# Global Variables and Paths
grpower_path = os.path.expanduser("~/grpower")
grt_path = os.path.expanduser("~/grt")
grt_be_path = os.path.expanduser("~/grt_be")
alps_path = os.path.expanduser("~/alps")
yocto_path = os.path.expanduser("~/yocto")

# Preset configurations
MODULE_SEQUENCE_PRESETS = {
    "custom": {
        "queue1": ["clean_nebula", "compile_nebula"],
        "queue2": ["clean_sdk", "compile_sdk", "compile_hee"],
        "queue3": ["compile_android", "compile_yocto", {"module": "push_changes", "branch_and_topic": "release-spm.mt8678_2024_0904%topic=test"}]
    }
}

@dataclass
class ModuleConfig:
    name: str
    clean_command: List[str]
    build_command: List[str]
    log_file: str
    async_mode: bool = False

# Define configurations for different modules
MODULE_CONFIGS = {
    "nebula": ModuleConfig(
        name="nebula",
        clean_command=[
            f"cd {grpower_path}/workspace && rm -rf buildroot-pvt8675/ nebula-ree/ buildroot-pvt8675_tee/",
            f"cd {grpower_path}/workspace/nebula && rm -rf out"
        ],
        build_command=[
            "export NO_PIPENV_SHELL=1 && " + 
            f"cd {grpower_path} && source scripts/env.sh && " + 
            f"cd {grpower_path} && gr-nebula.py build"
        ],
        log_file=f"{grt_path}/hee.log",
        async_mode=False
    ),
    "hee": ModuleConfig(
        name="hee",
        clean_command=[],
        build_command=[
            "export NO_PIPENV_SHELL=1 && " + 
            f"cd {grpower_path} && source scripts/env.sh && " + 
            "gr-nebula.py export-buildroot && " + 
            "gr-android.py set-product --product-name pvt8675 && " +
            "gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images"
        ],
        log_file=f"{grt_path}/hee.log",
        async_mode=False
    ),
    "sdk": ModuleConfig(
        name="sdk",
        clean_command=[
            f"cd {grt_path}/ && git clean -fdx && git reset --hard",
            f"cd {yocto_path}/prebuilt/hypervisor/grt && git clean -fd"
        ],
        build_command=[
            f"cd {grt_path}/thyp-sdk && ./configure.sh /home/nebula/grt/nebula-sdk/ > /dev/null",
            "./build_all.sh",
            f"cp -fv products/mt8678-mix/out/gz.img {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/out/nbl_vmm {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/out/nbl_vm_ctl {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/out/nbl_vm_srv {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/out/libvmm.so {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/out/symbols/*  {yocto_path}/prebuilt/hypervisor/grt/symbols/",
            f"cp -fv ./third_party/prebuilts/libluajit/lib64/libluajit.so {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv ./products/mt8678-mix/guest-configs/uos_alps_pv8678.lua {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/nbl_vm_srv/data/vm_srv_cfg_8678.pb.txt {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/nbl_vmm/data/uos_mtk8678/uos_bootloader_lk2.pb.txt {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/nbl_vmm/data/vm_audio_cfg.pb.txt {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv vmm/nbl_vmm/data/vm_audio_shared_irq.pb.txt {yocto_path}/prebuilt/hypervisor/grt/",
        ],
        log_file=f"{grt_path}/sdk.log",
        async_mode=False
    ),
    "tee": ModuleConfig(
        name="tee",
        clean_command=[],
        build_command=[
            "export NO_PIPENV_SHELL=1 && " + 
            f"cd {grpower_path} && source scripts/env.sh && " + 
            "gr-nebula.py export-buildroot && " +
            "gr-android.py set-product --product-name pvt8675_tee && " +
            f"mkdir -p {grt_path}/teetemp && " + 
            f"gr-android.py buildroot export_nebula_images -o {grt_path}/teetemp && " + 
            f"cp -v {grt_path}/teetemp/nebula*.bin {alps_path}/vendor/mediatek/proprietary/trustzone/grt/source/common/kernel/",
            f"cd {alps_path} && rm -rf out",
            "source build/envsetup.sh && export OUT_DIR=out && lunch vext_auto8678p1_64_bsp_vm-userdebug && make vext_images",
            "python out_sys/target/product/mssi_auto_64_cn_armv82/images/split_build.py --system-dir out_sys/target/product/mssi_auto_64_cn_armv82/images --vendor-dir out_hal/target/product/mgvi_auto_64_armv82_wifi_vm/images --kernel-dir out_krn/target/product/mgk_64_k61_auto_vm/images --vext-dir out/target/product/auto8678p1_64_bsp_vm/images --output-dir out/target/product/auto8678p1_64_bsp_vm/merged"
        ],
        log_file=f"{grt_path}/tee.log",
        async_mode=False
    ),
    "grt_be": ModuleConfig(
        name="grt_be",
        clean_command=[
            f"cd {grt_be_path}/workspace && git reset --hard && git clean -ffd"
        ],
        build_command=[
            f"{grt_be_path}/workspace/build.sh",
            "cd /home/nebula/grt/thyp-sdk",
            f"cp -fv ../../grt_be/workspace/out/gpu_server {yocto_path}/prebuilt/hypervisor/grt/",
            f"cp -fv ../../grt_be/workspace/out/video_server {yocto_path}/prebuilt/hypervisor/grt/"
        ],
        log_file=f"{grt_path}/grt_be.log",
        async_mode=False
    ),
    "android": ModuleConfig(
        name="android",
        clean_command=[
            f"cd {alps_path}",
            "rm -rf out out_hal out_krn out_sys",
            "rm -f hal.log krn.log out.log sys.log vext.log",
            "repo forall -c \"git reset --hard && git clean -ffd\""
        ],
        build_command=[
            "source build/envsetup.sh && export OUT_DIR=out_sys && lunch sys_mssi_auto_64_cn_armv82-userdebug && make sys_images > ~/grt/android_sys.log 2>&1",
            "source build/envsetup.sh && export OUT_DIR=out_hal && lunch hal_mgvi_auto_64_armv82_wifi_vm-userdebug && make hal_images > ~/grt/android_hal.log 2>&1",
            "source build/envsetup.sh && export OUT_DIR=out_krn && lunch krn_mgk_64_k61_auto_vm-userdebug && make krn_images > ~/grt/android_krn.log 2>&1",
            "source build/envsetup.sh && export OUT_DIR=out && lunch vext_auto8678p1_64_bsp_vm-userdebug && make vext_images > ~/grt/android_vext.log 2>&1",
            "python out_sys/target/product/mssi_auto_64_cn_armv82/images/split_build.py --system-dir out_sys/target/product/mssi_auto_64_cn_armv82/images --vendor-dir out_hal/target/product/mgvi_auto_64_armv82_wifi_vm/images --kernel-dir out_krn/target/product/mgk_64_k61_auto_vm/images --vext-dir out/target/product/auto8678p1_64_bsp_vm/images --output-dir out/target/product/auto8678p1_64_bsp_vm/merged > ~/grt/android_merge.log 2>&1"
        ],
        log_file=f"{grt_path}/android.log",
        async_mode=False
    ),
    "yocto": ModuleConfig(
        name="yocto",
        clean_command=[
            f"cd {yocto_path}",
            "rm -rf build sstate-cache",
            "repo forall -c \"git reset --hard && git clean -ffd\""
        ],
        build_command=[
            f"cd {yocto_path} && " +
            "export TEMPLATECONF=${PWD}/meta/meta-mediatek-mt8678/conf/templates/auto8678p1_64_hyp && " +
            "source meta/poky/oe-init-build-env && " +
            "export BB_DISABLE_NETWORK=\"1\" && " +
            "bitbake -k mtk-core-image-auto8678-hyp"
        ],
        log_file=f"{grt_path}/yocto.log",
        async_mode=False
    ),
    "git_add_sdk": ModuleConfig(
        name="git_add_sdk",
        clean_command=[],
        build_command=[
            "cd ~/grt && git add ~/grt/thyp-sdk/products/mt8678-mix/prebuilt-images"
        ],
        log_file="~/grt/git_add_sdk.log",
        async_mode=False
    ),
        "commit_changes": ModuleConfig(
        name="commit_changes",
        clean_command=[],
        build_command=[
            "git commit -m \"Update nebula prebuilt binary.\n\n[Description]\n1.fix android destroys init partition, lk-an restarts several times, yocto reports rcu error and hwt occurs\n\n[Test]\nBuild pass and test ok.\""
        ],
        log_file="~/grt/commit_changes.log",
        async_mode=False
    ),
    "push_changes": ModuleConfig(
        name="push_changes",
        clean_command=[],
        build_command=[
            "git push origin HEAD:refs/for/{branch_and_topic}"
        ],
        log_file="~/grt/push_changes.log",
        async_mode=False
    ),
    "git_add_yocto": ModuleConfig(
        name="git_add_yocto",
        clean_command=[],
        build_command=[
            "cd ~/yocto/prebuilt/hypervisor/grt && git add ."
        ],
        log_file="~/grt/git_add_yocto.log",
        async_mode=False
    )
}

async def run_command(command: str, log_file: str) -> None:
    """
    Run a command asynchronously and log the output to a file.
    :param command: The command to be executed.
    :param log_file: The path to the log file where the output will be saved.
    :return: None
    """
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    with open(os.path.expanduser(log_file), "a") as log:
        if stdout:
            log.write(stdout.decode())
        if stderr:
            log.write(stderr.decode())

async def clean_module(module_config: ModuleConfig) -> None:
    """
    Clean the module based on the provided module configuration.
    :param module_config: Configuration details for the module to be cleaned.
    :return: None
    """
    for cmd in module_config.clean_command:
        await run_command(cmd, module_config.log_file)

async def build_module(module_config: ModuleConfig) -> None:
    """
    Build the module based on the provided module configuration.
    :param module_config: Configuration details for the module to be built.
    :return: None
    """
    for cmd in module_config.build_command:
        await run_command(cmd, module_config.log_file)

async def handle_module(module_name: str, **kwargs) -> None:
    """
    Execute the cleaning and building process for a specified module.
    :param module_name: Name of the module to be processed.
    :param kwargs: Additional arguments that might be needed for the module configuration.
    :return: None
    """
    if module_name in MODULE_CONFIGS:
        module_config = MODULE_CONFIGS[module_name]
        if module_name == "push_changes" and "branch_and_topic" in kwargs:
            # Replace placeholder with provided branch and topic
            module_config.build_command = [cmd.format(branch_and_topic=kwargs["branch_and_topic"]) for cmd in module_config.build_command]
        await clean_module(module_config)
        await build_module(module_config)
    else:
        console.print(f"[red]Error: Module '{module_name}' configuration not found.[/red]")

async def run_sequence(sequence: List[str]) -> None:
    """
    Execute a sequence of module processes, either synchronously or asynchronously.
    :param sequence: List of module names to be processed.
    :return: None
    """
    tasks = []
    for module_name in sequence:
        module_config = MODULE_CONFIGS.get(module_name)
        if module_config and module_config.async_mode:
            tasks.append(handle_module(module_name))
        else:
            await handle_module(module_name)
    if tasks:
        await asyncio.gather(*tasks)

def main(sequence_preset: str) -> None:
    """
    Main function to run the build process based on a sequence preset.
    :param sequence_preset: Preset name to define the execution order of modules.
    :return: None
    """
    sequence = MODULE_SEQUENCE_PRESETS.get(sequence_preset, MODULE_SEQUENCE_PRESETS["default"])
    with Progress() as progress:
        task = progress.add_task("[green]Compiling Modules...[/green]", total=len(sequence))
        try:
            asyncio.run(run_sequence(sequence))
        except Exception as e:
            console.print(f"[red]An error occurred: {e}[/red]")
        finally:
            progress.update(task, advance=1)
            progress.console.print(f"[cyan]Compilation process for preset '{sequence_preset}' completed.[/cyan]")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compile various modules for the system.")
    parser.add_argument(
        "--sequence", 
        type=str, 
        default="default", 
        help="The preset sequence name to define the execution order of modules."
    )
    # python build_script.py --sequence custom
    args = parser.parse_args()
    main(args.sequence)
