#!/usr/bin/env python3

import os
import subprocess
import multiprocessing
import zipfile
from pathlib import Path
from shutil import copy2
import xml.etree.ElementTree as ET
from prompt_toolkit import print_formatted_text, HTML
from rich.console import Console
from rich.traceback import install
from IPython.display import display

# Install rich traceback
install()

# Define the console for rich library output
console = Console()
from paramiko import SSHClient, AutoAddPolicy
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import clear

# Global variables
CODE_ROOT_DIR = "/mnt/"
OUTPUT_DIR = "/mnt/hdo/78image/patch_release/MTK_{}"
REPO_PATHS = {
    'alps': './sst/one_78/alps',
    'yocto': './sso/one_78/yocto'
}
GIT_PATHS = {
    'grt': './sso/one_78/grt',
    'zircon': './sso/one_78/grpower/workspace/nebula/zircon',
    'garnet': './sso/one_78/grpower/workspace/nebula/garnet'
}
CATEGORY_A_REPOS = ['grt']
CATEGORY_B_REPOS = ['zircon', 'garnet']
NUM_PROCESSES = 64
REMOTE_SERVER = '192.168.50.50'
REMOTE_USER = 'Administrator'
REMOTE_FILE_PATH = 'C:/Users/Administrator/Downloads/MT8678 Hypervisor Release Note.pdf'
LOCAL_FILE_NAME = 'MT8678_Hypervisor_Release_Note.pdf'

# Function to get the latest two tags from a git repository
def get_latest_two_tags(repo_path):
    """
    Get the latest two tags from a git repository.

    Parameters:
    repo_path (str): The file system path to the git repository.

    Returns:
    tuple: A tuple containing the latest and second latest tag names.
    """
    try:
        # Change to the repository directory
        os.chdir(repo_path)

        # Get the latest two tags, sorted by creation date
        latest_tags = subprocess.check_output(
            ['git', 'tag', '--sort=-creatordate'],
            encoding='utf-8'
        ).split('\n')[:2]

        if len(latest_tags) < 2:
            print_formatted_text(HTML("<red>Error:</red> Not enough tags found in the repository."))
            return None, None

        # Return the latest and second latest tag names
        return latest_tags[0], latest_tags[1]
    except subprocess.CalledProcessError as e:
        print_formatted_text(HTML("<red>An error occurred while fetching tags.</red>"))
        return None, None
    except Exception as e:
        print_formatted_text(HTML("<red>An unexpected error occurred:</red>"))
        return None, None

def create_output_dir(tag_name):
    """
    Create the output directory for the given tag name.
    If the directory already exists, exit with an error.

    Parameters:
    tag_name (str): The name of the latest tag to create the directory for.

    Returns:
    str: The path to the created directory or None if an error occurred.
    """
    try:
        # Format the directory path with the latest tag name
        dir_path = OUTPUT_DIR.format(tag_name)

        # Check if the directory already exists
        if os.path.exists(dir_path):
            print_formatted_text(HTML(f"<red>Error: The directory {dir_path} already exists.</red>"))
            return None

        # Create the directory
        os.makedirs(dir_path)
        print_formatted_text(HTML(f"<green>Success: Created the directory {dir_path}.</green>"))
        return dir_path

    except Exception as e:
        print_formatted_text(HTML("<red>An unexpected error occurred while creating the directory:</red>"))
        return None

def add_file_to_zip(zip_file, file_path, arcname):
    zip_file.write(file_path, arcname)
    print_formatted_text(HTML(f"<green>Added {file_path} to zip archive as {arcname}</green>"))

def handle_repo_warehouse(repo_name, repo_path, output_subdir, latest_tag, second_latest_tag, zip_file):
    """
    Handle operations for a repo warehouse.

    Parameters:
    repo_name (str): The name of the repo warehouse.
    repo_path (str): The file system path to the repo warehouse.
    output_subdir (str): The subdirectory name for the output.
    latest_tag (str): The latest tag name.
    second_latest_tag (str): The second latest tag name.

    Returns:
    bool: True if the operation was successful, False otherwise.
    """
    try:
        # Change to the repo warehouse directory
        os.chdir(repo_path)

        # Read the manifest file to get all git repository paths
        manifest_path = os.path.join('.repo', 'manifests', f'{repo_name}.xml')
        tree = ET.parse(manifest_path)
        root = tree.getroot()

        # Iterate over the project elements to get the path attributes
        for project in root.findall('project'):
            git_repo_path = project.get('path')
            full_git_repo_path = os.path.join(repo_path, git_repo_path)
            os.chdir(full_git_repo_path)
            try:
                # Generate patch files between the latest and penultimate tags
                patch_files = subprocess.check_output(['git', 'format-patch', f'{second_latest_tag}..{latest_tag}'], text=True)
                patch_files_list = patch_files.splitlines()

                # Create corresponding subdirectories in the output directory and copy patch files
                for patch_file in patch_files_list:
                    patch_file_path = os.path.join(full_git_repo_path, patch_file)
                    relative_patch_path = os.path.relpath(patch_file_path, repo_path)
                    output_patch_path = os.path.join(output_subdir, relative_patch_path)
                    os.makedirs(os.path.dirname(output_patch_path), exist_ok=True)
                    copy2(patch_file_path, output_patch_path)
                    zip_file.write(output_patch_path, os.path.join(repo_name, os.path.relpath(output_patch_path, output_subdir)))
                    print_formatted_text(HTML(f"<green>Copied and compressed patch file: {patch_file}</green>"))
            except subprocess.CalledProcessError:
                print_formatted_text(HTML(f"<yellow>Warning: Patch generation failed at {git_repo_path}</yellow>"))

        # Check if the output directory for the snapshot exists, create if not
        os.makedirs(output_subdir, exist_ok=True)

        # Generate snapshot manifest files
        snapshot_path = os.path.join(output_subdir, 'snapshot.xml')
        subprocess.run([os.path.expanduser('~/bin/repo'), 'manifest', '-r', '-o', snapshot_path], check=True)

        zip_file.write(snapshot_path, os.path.join(repo_name, os.path.relpath(snapshot_path, output_subdir)))
        print_formatted_text(HTML(f"<green>Success: Handled the repo warehouse {repo_name}.</green>"))
        return True
    except ET.ParseError as e:
        print_formatted_text(HTML("<red>An error occurred while parsing the manifest file.</red>"))
        return False
    except Exception as e:
        print_formatted_text(HTML("<red>An unexpected error occurred while handling the repo warehouse.</red>"))
        return False

def handle_git_warehouse(repo_name, repo_path, category, output_subdir, latest_tag, second_latest_tag, zip_file):
    """
    Handle operations for an independent git warehouse.

    Parameters:
    repo_name (str): The name of the git warehouse.
    repo_path (str): The file system path to the git warehouse.
    category (str): The category of the git warehouse ('A' or 'B').
    output_subdir (str): The subdirectory name for the output.
    latest_tag (str): The latest tag name.
    second_latest_tag (str): The second latest tag name.

    Returns:
    bool: True if the operation was successful, False otherwise.
    """
    try:
        # Change to the git warehouse directory
        os.chdir(repo_path)

        if category == 'A':
            # Generate patch files between the latest and penultimate tags
            # subprocess.run(['git', 'format-patch', f'{second_latest_tag}..{latest_tag}', '-o', output_subdir], check=True)
            # print_formatted_text(HTML(f"<green>Patches created for {repo_name}.</green>"))
            patch_files = subprocess.check_output(['git', 'format-patch', f'{second_latest_tag}..{latest_tag}'], text=True)
            patch_files_list = patch_files.splitlines()

            # Create corresponding subdirectories in the output directory and copy patch files
            for patch_file in patch_files_list:
                patch_file_path = os.path.join(repo_path, patch_file)
                relative_patch_path = os.path.relpath(patch_file_path, repo_path)
                output_patch_path = os.path.join(output_subdir, relative_patch_path)
                os.makedirs(os.path.dirname(output_patch_path), exist_ok=True)
                copy2(patch_file_path, output_patch_path)
                zip_file.write(output_patch_path, os.path.join(repo_name, os.path.relpath(output_patch_path, output_subdir)))
                print_formatted_text(HTML(f"<green>Copied and compressed patch file: {patch_file}</green>"))

            # Copy all files from the specified source directory to the output directory
            source_dir = os.path.join(repo_path, 'thyp-sdk/products/mt8678-mix/prebuilt-images/')
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(source_dir, repo_path)
                    target_dir = os.path.join(output_subdir, relative_path)
                    os.makedirs(target_dir, exist_ok=True)
                    copy2(file_path, os.path.join(target_dir, file))
                    zip_file.write(os.path.join(target_dir, file), os.path.join(repo_name, os.path.relpath(os.path.join(target_dir, file), output_subdir)))
                    print_formatted_text(HTML(f"<green>Copied and compressed file: {file}</green>"))
            copy2('/mnt/sso/one_78/grpower/workspace/nebula/out/build-zircon/build-venus-hee/zircon.elf', os.path.join(target_dir, 'nebula_kernel.elf'))
            zip_file.write(os.path.join(target_dir, 'nebula_kernel.elf'), os.path.join(repo_name, os.path.relpath(os.path.join(target_dir, 'nebula_kernel.elf'), output_subdir)))
            copy2('/home/nebula/grpower/workspace/nebula/snapshot.xml', os.path.join(target_dir, f'Nebula_MTK_{latest_tag}.xml'))

        elif category == 'B':
            # For category B, only tagging is needed
            print_formatted_text(HTML(f"<yellow>No patches to generate for {repo_name} (Category B).</yellow>"))

        print_formatted_text(HTML(f"<green>Success: Handled the git warehouse {repo_name}.</green>"))
        return True

    except subprocess.CalledProcessError as e:
        print_formatted_text(HTML("<red>An error occurred while executing a subprocess command.</red>"))
        return False
    except Exception as e:
        print_formatted_text(HTML("<red>An unexpected error occurred while handling the git warehouse.</red>"))
        return False

def copy_file_from_remote(output_dir):
    """
    Copy a file from a remote server to the local output directory.
    """
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(REMOTE_SERVER, username=REMOTE_USER)

        sftp = ssh.open_sftp()
        remote_path = REMOTE_FILE_PATH.replace('\\', '/')
        local_path = os.path.join(output_dir, LOCAL_FILE_NAME)

        print_formatted_text(HTML(f"<blue>Attempting to copy file from {remote_path} to {local_path}</blue>"))

        sftp.get(remote_path, local_path)
        sftp.close()
        ssh.close()
        
        print_formatted_text(HTML(f"<green>Successfully copied file from {REMOTE_SERVER} to {local_path}</green>"))

        print_formatted_text(
            HTML(f"<green>File {local_path} added to zip as {os.path.relpath(local_path, output_dir)}</green>"))

        return local_path
    except FileNotFoundError:
        print_formatted_text(HTML(f"<red>File not found: {REMOTE_FILE_PATH}</red>"))
        return None
    except Exception as e:
        print_formatted_text(HTML(f"<red>Failed to copy file from remote server: {str(e)}</red>"))
        return None

def main():
    clear()
    # Get the latest two tags from the Class A git repository
    class_a_repo_path = os.path.join(CODE_ROOT_DIR, GIT_PATHS[CATEGORY_A_REPOS[0]])
    latest_tag, second_latest_tag = get_latest_two_tags(class_a_repo_path)
    if not latest_tag or not second_latest_tag:
        print_formatted_text(HTML("<red>Error: Failed to retrieve tags.</red>"))
        return

    # Create the output directory
    output_dir = create_output_dir(latest_tag)
    if not output_dir:
        return

    # zip_output_dir = OUTPUT_DIR.format(latest_tag)
    # os.makedirs(zip_output_dir, exist_ok=True)  # Ensure the directory for the zip file exists
    zip_output_path = os.path.join(OUTPUT_DIR.format(latest_tag), f'MTK_{latest_tag}.zip')
    # Process the repo and independent git repositories
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 处理repo仓库
        for repo_name, repo_rel_path in REPO_PATHS.items():
            repo_path = os.path.join(CODE_ROOT_DIR, repo_rel_path)
            output_subdir = os.path.join(output_dir, repo_name)
            handle_repo_warehouse(repo_name, repo_path, output_subdir, latest_tag, second_latest_tag, zip_file)

        # 处理git仓库
        for repo_name, repo_rel_path in GIT_PATHS.items():
            category = 'A' if repo_name in CATEGORY_A_REPOS else 'B'
            repo_path = os.path.join(CODE_ROOT_DIR, repo_rel_path)
            output_subdir = os.path.join(output_dir, repo_name)
            handle_git_warehouse(repo_name, repo_path, category, output_subdir, latest_tag, second_latest_tag, zip_file)

        # 复制远程文件并压缩
        copied_file_path = copy_file_from_remote(output_dir)
        if copied_file_path:
            zip_file.write(copied_file_path, os.path.relpath(copied_file_path, output_dir))

    print_formatted_text(HTML(f"<green>Zip archive created at: {zip_output_path}</green>"))

if __name__ == "__main__":
    main()