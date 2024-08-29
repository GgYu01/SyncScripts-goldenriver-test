#!/usr/bin/env python3

import time
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
import paramiko
from rich.progress import Progress
import asyncio
import subprocess

# Configuration Manager with detailed comments and type annotations
class ConfigurationManager:
    DEFAULTS = {
        'source': '/mnt/sso/san_78/yocto/downloads/',
        'destination': 'D:/downloads',
        'ip': '100.64.0.3',  # Assuming this is the Windows IP you need to transfer files to
        'username': 'Administrator',  # Assuming this is the Windows username
        'include_source_dir': False,  # Default to not including the source directory itself
        'concurrency': 16
    }
    
    def __init__(self, args: list):
        """
        Initializes the ConfigurationManager with command line arguments.

        :param args: Command line arguments provided to the script.
        """
        self.config = self.parse_args(args)

    @staticmethod
    def parse_args(args: list) -> dict:
        """
        Parses the command line arguments or uses default settings.
        
        :param args: List of command-line arguments.
        :return: Dictionary with configuration settings.
        """
        parser = argparse.ArgumentParser(description="Configure file transfer settings.")
        parser.add_argument('--source', type=str, default=ConfigurationManager.DEFAULTS['source'], help='Source directory path')
        parser.add_argument('--destination', type=str, default=ConfigurationManager.DEFAULTS['destination'], help='Destination directory path')
        parser.add_argument('--ip', type=str, default=ConfigurationManager.DEFAULTS['ip'], help='IP address of the destination server')
        parser.add_argument('--username', type=str, default=ConfigurationManager.DEFAULTS['username'], help='Username for SSH authentication')
        parser.add_argument('--include_source_dir', type=bool, default=ConfigurationManager.DEFAULTS['include_source_dir'], help='Include the source directory itself in the transfer')
        parser.add_argument('--concurrency', type=int, default=ConfigurationManager.DEFAULTS['concurrency'], help='Concurrency level for file transfers')

        if args:
            return vars(parser.parse_args(args))
        else:
            return ConfigurationManager.DEFAULTS


    def get(self, key: str) -> any:
        """
        Retrieves a configuration value for a given key.

        :param key: Configuration key.
        :return: Configuration value.
        """
        return self.config.get(key)

# SSH Manager with detailed annotations and comments
class SSHManager:
    def __init__(self, config: ConfigurationManager):
        """
        Initialize the SSHManager with configuration settings.

        :param config: A ConfigurationManager instance containing all necessary SSH configurations.
        """
        self.config = config
        self.ip = self.config.get('ip')
        self.username = self.config.get('username')
        self.client = paramiko.SSHClient()

    def connect(self) -> None:
        """
        Establishes an SSH connection using the IP and username from the configuration.

        Attempts to connect to the SSH server and handles any SSH-specific exceptions
        by printing an error message and re-raising the exception for further handling.
        """
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(self.ip, username=self.username)
        except paramiko.SSHException as e:
            print(f"Connection Failed: {e}")
            raise Exception(f"Failed to connect to {self.ip} as {self.username}")

    def disconnect(self) -> None:
        """

        Closes the SSH connection.
        """
        if self.client:
            self.client.close()

    def execute_command(self, command: str) -> str:
        """
        Executes a command on the remote machine via SSH.

        :param command: Command to execute.
        :return: Output from the command, if the connection has been established.

        Raises an exception if the connection is not established.
        """
        if self.client:
            stdin, stdout, stderr = self.client.exec_command(command)
            return stdout.read().decode()  # Ensure output is decoded to string
        else:
            raise Exception("Connection not established")

# File Transfer Manager
class FileTransferManager:
    def __init__(self, ssh_manager: SSHManager, config: ConfigurationManager):
        """
        Manages the transfer of files using the SSH connection.
        
        :param ssh_manager: An instance of SSHManager.
        :param config: An instance of ConfigurationManager.
        """
        self.ssh_manager = ssh_manager
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=self.config.get('concurrency'))

    def list_files(self) -> list:
        """
        Lists files and directories under the source path for transfer.
        
        :return: List of file paths.
        """
        source_dir = self.config.get('source')
        return [os.path.join(source_dir, file) for file in os.listdir(source_dir)]

    async def transfer_files(self, progress) -> None:
        """
        Asynchronously transfers files and directories to the destination.
        
        :param progress: Instance of ProgressManager to update transfer progress.
        """
        files = self.list_files()
        tasks = [asyncio.get_event_loop().run_in_executor(self.executor, self.transfer_file, file, progress) for file in files]
        await asyncio.gather(*tasks)

    def transfer_file(self, file: str, progress) -> None:
        """
        Transfers a single file or directory using SCP.
        
        :param file: Full path of the file or directory to transfer.
        :param progress: Progress manager instance to update the progress bar.
        """
        destination_dir = self.config.get('destination')
        remote_path = f"{self.config.get('username')}@{self.config.get('ip')}:{destination_dir}"

        # 如果是目录，则使用 scp 的 -r 选项进行递归复制
        scp_command = ['scp', '-Cr', file, remote_path]
                
        # 使用 subprocess 调用 scp 进行文件传输
        try:
            subprocess.run(scp_command, check=True)
            print(f"Transferred {file} to {remote_path}")
            progress.update_progress()
        except subprocess.CalledProcessError as e:
            print(f"Error transferring {file}: {e}")

# Progress and Output Manager
class ProgressManager:
    def __init__(self):
        """
        Initializes the progress manager.
        """
        self.progress = Progress()

    def start_progress(self, total_files: int) -> None:
        """
        Starts the progress bar for file transfers.

        :param total_files: Total number of files to transfer.

        """
        self.task = self.progress.add_task("[cyan]Transferring files...", total=total_files)

    def update_progress(self) -> None:
        """
        Updates the progress bar by incrementing it.
        """
        self.progress.update(self.task, advance=1)

    def complete_progress(self) -> None:
        """
        Completes the progress and ensures the bar reaches 100%.
        """
        self.progress.stop()

def main() -> None:
    """
    The main entry point of the script that orchestrates the SSH connection,
    file transfer, and progress reporting.

    It initializes all necessary managers, connects to the SSH server,
    performs the file transfer, and handles any errors that occur during the process.
    """
    start_time = time.time()  # 开始时间统计

    # Initialize configuration manager with command-line arguments or defaults
    config_manager = ConfigurationManager(sys.argv[1:])

    # Setup SSH manager with the configuration
    ssh_manager = SSHManager(config=config_manager)

    # Setup progress manager for tracking progress of file transfers
    progress_manager = ProgressManager()

    # Connect to the SSH server with error handling
    try:
        ssh_manager.connect()
        print("SSH connection established.")
    except Exception as error:
        print(f"Failed to establish SSH connection: {error}")
        return  # Exit if connection fails

    # Initialize file transfer manager
    file_transfer_manager = FileTransferManager(ssh_manager=ssh_manager, config=config_manager)

    # List files to transfer and start progress bar
    files_to_transfer = file_transfer_manager.list_files()
    progress_manager.start_progress(total_files=len(files_to_transfer))

    # Perform file transfer asynchronously
    try:
        asyncio.run(file_transfer_manager.transfer_files(progress=progress_manager))
    except Exception as error:
        print(f"Error during file transfer: {error}")
    finally:
        # Cleanup: Disconnect SSH and complete progress bar
        ssh_manager.disconnect()
        progress_manager.complete_progress()
        print("File transfer process completed.")

    end_time = time.time()  # 结束时间统计
    total_time = end_time - start_time  # 计算总用时
    print(f"File transfer process completed in {total_time:.2f} seconds.")

if __name__ == "__main__":
    main()