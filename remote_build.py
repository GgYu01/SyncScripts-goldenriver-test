#!/usr/bin/env python3

import asyncssh
import asyncio
import sys
import logging
from pathlib import Path
from rich.console import Console
from rich.traceback import install
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.INFO, filename='compile.log', 
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
console = Console()
install(show_locals=True)  # Setup rich traceback

# Configuration for SSH and repository details
SSH_CONFIG = {
    "host": "192.168.50.45",
    "port": 8022,
    "username": "nebula",
    "password": "nebula",
    "ssh_key_path": "~/.ssh/id_rsa.pub"
}

REPOSITORIES = {
    "yocto": {
        "path": "/home/nebula/yocto",
        "commands": [
            "export BB_NO_NETWORK='1'",
            "TEMPLATECONF={path}/meta/meta-mediatek-mt8678/conf/base/auto8678p1_64_kde_hyp",
            "source meta/poky/oe-init-build-env",
            "bitbake mtk-core-image-auto8678-kde-hyp"
        ],
        "log_path": "yocto_build.log"
    },
    "alps": {
        "path": "/home/nebula/alps",
        "commands": [
            "source build/envsetup.sh && export OUT_DIR=out_sys && lunch sys_mssi_auto_64_cn_armv82-userdebug && make sys_images",
            "source build/envsetup.sh && export OUT_DIR=out_hal && lunch hal_mgvi_auto_64_armv82_wifi_vm-userdebug && make hal_images",
            "source build/envsetup.sh && export OUT_DIR=out_krn && lunch krn_mgk_64_k61_auto_vm-userdebug && make krn_images",
            "source build/envsetup.sh && export OUT_DIR=out && lunch vext_auto8678p1_64_bsp_vm-userdebug && make vext_images"
        ],
        "log_paths": ["sys.log", "hal.log", "krn.log", "vext.log"],
        "final_command": "python out_sys/target/product/mssi_auto_64_cn_armv82/images/split_build.py --system-dir out_sys/target/product/mssi_auto_64_cn_armv82/images --vendor-dir out_hal/target/product/mgvi_auto_64_armv82_wifi_vm/images --kernel-dir out_krn/target/product/mgk_64_k61_auto_vm/images --vext-dir out/target/product/auto8678p1_64_bsp_vm/images --output-dir out/target/product/auto8678p1_64_bsp_vm/merged",
        "final_log": "out.log"
    }
}

class SSHConnection:
    """Manage SSH connections."""
    def __init__(self, config: dict):
        """
        Initialize the SSH connection object with the configuration.

        :param config: A dictionary containing SSH configuration details like host, port, username, password, and ssh_key_path.
        """
        self.config = config
        self.conn = None

    async def connect(self) -> None:
        """Establish an SSH connection."""
        try:
            self.conn = await asyncssh.connect(
                host=self.config['host'],
                port=self.config['port'],
                username=self.config['username'],
                password=self.config['password'],
                known_hosts=None  # Automatically trust all hosts
            )
            console.log("SSH connection established.")
            logging.info("SSH connection established.")
        except (asyncssh.Error, OSError) as e:
            console.log(f"SSH connection failed: {e}")
            logging.error(f"SSH connection failed: {e}")
            sys.exit(1)

    async def disconnect(self) -> None:
        """Close the SSH connection."""
        if self.conn:
            self.conn.close()
            console.log("SSH connection closed.")
            logging.info("SSH connection closed.")

    async def check_and_upload_ssh_key(self) -> None:
        """Ensure the SSH public key is uploaded to the server."""
        remote_path = ".ssh/authorized_keys"
        local_key_path = os.path.expanduser(self.config['ssh_key_path'])  # Expand user path
        try:
            local_key = Path(local_key_path).read_text()
            existing_keys = await self.conn.run(f"cat {remote_path}", check=False)
            if local_key not in existing_keys.stdout:
                await self.conn.run(f'echo "{local_key}" >> {remote_path}', check=True)
                console.log("SSH public key uploaded.")
                logging.info("SSH public key uploaded.")
            else:
                console.log("SSH public key already present.")
                logging.info("SSH public key already present.")
        except (asyncssh.Error, OSError) as e:
            console.log(f"Failed to upload SSH public key: {e}")
            logging.error(f"Failed to upload SSH public key: {e}")
            sys.exit(1)

class Compiler:
    """Handle compilation tasks."""
    def __init__(self, connection: SSHConnection, repo_key: str):
        """
        Initialize the compiler with an SSH connection and a repository key.

        :param connection: An instance of SSHConnection.
        :param repo_key: The key string which identifies the repository in the REPOSITORIES dictionary.
        """
        self.connection = connection.conn
        self.repo_info = REPOSITORIES[repo_key]

    async def execute_commands(self) -> None:
        """Execute compilation commands with special handling for the alps repository."""
        if self.repo_info['path'].endswith("alps"):
            await self.execute_alps_commands()
        else:
            await self.execute_yocto_commands()

    async def execute_alps_commands(self) -> None:
        """Execute alps compilation commands asynchronously and handle the final command upon success."""
        path = self.repo_info['path']
        commands = self.repo_info['commands']
        log_paths = self.repo_info['log_paths']
        tasks = [self.run_command_with_logging(path, cmd, log) for cmd, log in zip(commands, log_paths)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        if all(result == True for result in results):
            final_command = self.repo_info['final_command']
            final_log = self.repo_info['final_log']
            await self.run_command_with_logging(path, final_command, final_log)
            console.log("All alps commands executed successfully, final output logged.")
            logging.info("All alps commands executed successfully, final output logged.")
        else:
            console.log("Some alps commands failed, skipping the final command.")
            logging.warning("Some alps commands failed, skipping the final command.")

    async def execute_yocto_commands(self) -> None:
        """Execute yocto compilation commands sequentially."""
        path = self.repo_info['path']
        commands = [cmd.format(path=path) for cmd in self.repo_info['commands']]
        script_path = f"{path}/temp_script.sh"
        log_path = self.repo_info['log_path']
        remote_log_path = f"{path}/yocto_build.log"

        # Create the temporary script
        script_lines = [
            "#!/bin/bash",
            "set -x"
        ]
        for cmd in commands:
            script_lines.append(f"echo 'Running: {cmd}' >> {remote_log_path} 2>&1")
            script_lines.append(f"{cmd} >> {remote_log_path} 2>&1 || echo 'Failed to run: {cmd}' >> {remote_log_path} 2>&1")

        script_content = "\n".join(script_lines)

        try:
            await self.connection.run(f'echo "{script_content}" > {script_path}')
            await self.connection.run(f'chmod 777 {script_path}')
            console.log(f"Temporary script created at {script_path}")
            logging.info(f"Temporary script created at {script_path}")
        except asyncssh.Error as e:
            console.log(f"Failed to create temporary script: {e}")
            logging.error(f"Failed to create temporary script: {e}")
            return

        # Execute the temporary script
        if not await self.run_command_with_logging(path, f'{script_path}', log_path):
            console.log(f"Error executing Yocto temporary script: {script_path}")
            logging.error(f"Error executing Yocto temporary script: {script_path}")
        else:
            console.log("Yocto commands executed successfully.")
            logging.info("Yocto commands executed successfully.")

        # Delete the temporary script
        try:
            await self.connection.run(f'rm {script_path}')
            console.log(f"Temporary script {script_path} deleted")
            logging.info(f"Temporary script {script_path} deleted")
        except asyncssh.Error as e:
            console.log(f"Failed to delete temporary script: {e}")
            logging.error(f"Failed to delete temporary script: {e}")            

    async def run_command_with_logging(self, repo_path: str, command: str, log_path: str) -> bool:
        """
        Run a specified command in the repository path and log the output.

        :param repo_path: The directory path of the repository.
        :param command: The shell command to execute.
        :param log_path: The path to the log file where command output is saved.
        :return: True if the command executes successfully, False otherwise.
        """
        try:
            result = await self.connection.run(f'cd {repo_path} && {command}', check=True)
            with open(log_path, 'a') as log_file:
                log_file.write(result.stdout)
                log_file.write(result.stderr)
                log_file.flush()
            console.log(f"Command executed successfully: {command}")
            logging.info(f"Command executed successfully: {command}")
            return True
        except asyncssh.Error as e:
            console.log(f"Failed to execute command: {command}. Error: {e}")
            logging.error(f"Failed to execute command: {command}. Error: {e}")
            with open(log_path, 'a') as log_file:
                log_file.write(f"Failed to execute command: {command}. Error: {e}\n")
                log_file.flush()
            return False

# Main asynchronous function to manage SSH connection and compilation
async def main():
    try:
        ssh_connection = SSHConnection(SSH_CONFIG)
        await ssh_connection.connect()
        await ssh_connection.check_and_upload_ssh_key()

        # Compiler instances for alps and yocto
        alps_compiler = Compiler(ssh_connection, 'alps')
        yocto_compiler = Compiler(ssh_connection, 'yocto')

        # Execute both alps and yocto compilation concurrently
        await asyncio.gather(
            # alps_compiler.execute_commands(),
            yocto_compiler.execute_commands()
        )

    except Exception as e:
        console.log(f"An unexpected error occurred: {e}")
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        await ssh_connection.disconnect()

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())

