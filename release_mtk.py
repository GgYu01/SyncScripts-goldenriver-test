#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Professional Python script for automating tag management, compilation, export,
and binary submission for multiple source code repositories.

Author: [Your Name]
Date: [Date]

This script automates the process of managing tags, compiling source code,
exporting binaries, and submitting changes to remote repositories for projects
including grpower, nebula, grt, yocto, alps, tee, and nebula-sdk.

It includes configurations to determine which repositories are involved in the
current operation and adjusts the workflow accordingly. The script ensures that
commands involving 'source' are executed in the same sub-shell to maintain
environment variables.

Detailed logging is provided for all operations, and the script captures all
output from build commands into log files.

Usage:
    python3 script.py \
        --cr-number "CR123456" \
        --title "这里是标题信息" \
        --tag-date "2024_1023_03" \
        --repos grpower nebula nebula-sdk tee grt yocto alps \
        --grt-branch "release-spm.mt8678_2024_1001" \
        --yocto-branch "release-spm.mt8678_2024_1001" \
        --alps-branch "release-spm.mt8678_2024_1001" \
        --zircon-branch "release-branch" \
        --garnet-branch "release-branch" \
        --description "Update nebula prebuilt binary."
"""

import os
import sys
import subprocess
import argparse
import logging
import shutil
from dataclasses import dataclass, field
from typing import List
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("script.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def log_execution(func):
    """Decorator for logging the execution of methods."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Starting '{func.__name__}'")
        result = func(*args, **kwargs)
        logging.info(f"Finished '{func.__name__}'")
        return result
    return wrapper

@dataclass
class Config:
    """Configuration data class for storing global settings."""
    tag_date: str = "2024_1107_04"
    repos: List[str] = field(default_factory=lambda: ["grpower", "grt", "alps", "yocto"])
    grt_branch: str = "release-spm.mt8678_2024_1001"
    yocto_branch: str = "release-spm.mt8678_2024_1001"
    alps_branch: str = "release-spm.mt8678_2024_1001"
    zircon_branch: str = "release-spm.mt8678_mtk"
    garnet_branch: str = "release-spm.mt8678_mtk"
    description: str = "1.hyp-tipc: kick vqs needs to determine the status of the vcpu\n2.nblruncmd: support query the version"
    cr_number: str = "ALPS"
    title: str = "nblruncmd"
    max_sync_attempts: int = 5
    commit_messages: dict = field(default_factory=lambda: {
        'nebula': "[{cr_number}] thyp-sdk: {title}\n\n[Description]\n{description}\n\n[Test]\nBuild pass and test ok.",
        'nebula-sdk': "[{cr_number}] nebula-sdk: {title}\n\n[Description]\n{description}\n\n[Test]\nBuild pass and test ok.",
        'tee': "[{cr_number}] tee: {title}\n\n[Description]\n{description}\n\n[Test]\nBuild pass and test ok."
    })

class RepositoryManager:
    """Class for managing repository operations."""
    def __init__(self, config: Config):
        self.config = config

    @log_execution
    def create_and_push_tag(self, repo_path: str, tag_name: str):
        """Create and push a tag in the specified repository."""
        try:
            os.chdir(os.path.expanduser(repo_path))
            subprocess.check_call(["git", "pull"])
            subprocess.check_call(["git", "tag", tag_name])
            subprocess.check_call(["git", "push", "origin", tag_name])
            logging.info(f"Tag '{tag_name}' pushed to repository at '{repo_path}'")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in create_and_push_tag: {e}")
            sys.exit(1)

    @log_execution
    def sync_repo(self, repo_path: str):
        """Synchronize the repository using repo sync."""
        attempts = 0
        while attempts < self.config.max_sync_attempts:
            try:
                os.chdir(os.path.expanduser(repo_path))
                subprocess.check_call([
                    "repo", "sync", "--no-repo-verify", "--force-sync",
                    "--jobs", "1", "--force-checkout", "--force-remove-dirty",
                    "--tags", "--retry-fetches=5", "--prune", "--verbose"
                ])
                logging.info(f"Repository at '{repo_path}' synchronized successfully")
                return
            except subprocess.CalledProcessError:
                attempts += 1
                logging.warning(f"Sync attempt {attempts} failed for '{repo_path}'")
        logging.error(f"Failed to sync repository at '{repo_path}' after {self.config.max_sync_attempts} attempts")
        sys.exit(1)

    @log_execution
    def tag_and_push_all(self, repo_path: str, tag_name: str):
        """Tag and push all repositories managed by repo."""
        try:
            os.chdir(os.path.expanduser(repo_path))
            subprocess.check_call(["repo", "forall", "-c", f"git tag {tag_name}"])
            subprocess.check_call(["repo", "forall", "-c", f"git push grt-mt8678 {tag_name}"])
            logging.info(f"All repositories under '{repo_path}' tagged and pushed with '{tag_name}'")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in tag_and_push_all: {e}")
            sys.exit(1)

    @log_execution
    def wait_for_user_confirmation(self, message: str):
        """Wait for user confirmation before proceeding."""
        input(message)

class BuildManager:
    """Class for managing build operations."""
    def __init__(self, config: Config):
        self.config = config

    @log_execution
    def clean_previous_build(self):
        """Clean previous build artifacts."""
        try:
            commands = [
                "cd ~/grpower/workspace && rm -rf buildroot-pvt8675/ nebula-ree/ buildroot-pvt8675_tee/",
                "cd ~/grpower/workspace/nebula && rm -rf out"
            ]
            for cmd in commands:
                subprocess.check_call(cmd, shell=True, executable='/bin/bash')
            logging.info("Previous build artifacts cleaned successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in clean_previous_build: {e}")
            sys.exit(1)

    @log_execution
    def build_nebula(self):
        """Build nebula."""
        try:
            build_script = """
            export NO_PIPENV_SHELL=1
            cd ~/grpower/
            source scripts/env.sh
            cd ~/grpower/
            gr-nebula.py build
            gr-nebula.py export-buildroot
            gr-android.py set-product --product-name pvt8675
            gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images
            cp -fv /home/nebula/grpower/workspace/nebula/out/build-zircon/build-venus-hee/zircon.elf ~/grt/thyp-sdk/products/mt8678-mix/prebuilt-images/nebula_kernel.elf
            cd ~/grt/thyp-sdk
            ./configure.sh /home/nebula/grt/nebula-sdk/ > /dev/null
            ./build_all.sh
            """
            # Change log file path to ~ directory
            log_file_path = os.path.expanduser('~/nebula_build.log')
            with open(log_file_path, 'w') as log_file:
                subprocess.check_call(build_script, shell=True, executable='/bin/bash', stdout=log_file, stderr=subprocess.STDOUT)
            logging.info("Nebula built successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in build_nebula: {e}")
            sys.exit(1)

    @log_execution
    def build_nebula_sdk(self):
        """Build nebula-sdk."""
        try:
            build_script = """
            export NO_PIPENV_SHELL=1
            cd ~/grpower/
            source scripts/env.sh
            cd ~/grpower/
            gr-nebula.py build
            gr-nebula.py export-buildroot
            gr-android.py set-product --product-name pvt8675
            gr-nebula.py export-sdk -o /home/nebula/grt/nebula-sdk
            """
            with open('nebula_sdk_build.log', 'w') as log_file:
                subprocess.check_call(build_script, shell=True, executable='/bin/bash', stdout=log_file, stderr=subprocess.STDOUT)
            logging.info("Nebula SDK built successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in build_nebula_sdk: {e}")
            sys.exit(1)

    @log_execution
    def build_tee(self):
        """Build TEE."""
        try:
            build_script = """
            export NO_PIPENV_SHELL=1
            cd ~/grpower/workspace && rm -rf buildroot-pvt8675/ nebula-ree/ buildroot-pvt8675_tee/
            cd ~/grpower/workspace/nebula && rm -rf out
            cd ~/grpower/
            source scripts/env.sh
            cd ~/grpower/
            gr-nebula.py build
            gr-nebula.py export-buildroot
            gr-android.py set-product --product-name pvt8675_tee
            mkdir -p ~/grt/teetemp
            gr-android.py buildroot export_nebula_images -o ~/grt/teetemp
            cp -v ~/grt/teetemp/nebula*.bin ~/alps/vendor/mediatek/proprietary/trustzone/grt/source/common/kernel/
            """
            with open('tee_build.log', 'w') as log_file:
                subprocess.check_call(build_script, shell=True, executable='/bin/bash', stdout=log_file, stderr=subprocess.STDOUT)
            logging.info("TEE built successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in build_tee: {e}")
            sys.exit(1)

    @log_execution
    def copy_files(self):
        """Copy build artifacts to the destination directories."""
        try:
            source_destination_pairs = [
                ("/home/nebula/grt/thyp-sdk/products/mt8678-mix/out/gz.img", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/out/nbl_vmm", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/out/nbl_vm_ctl", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/out/nbl_vm_srv", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/out/libvmm.so", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/out/symbols/", "~/yocto/prebuilt/hypervisor/grt/symbols/"),
                ("/home/nebula/grt/thyp-sdk/third_party/prebuilts/libluajit/lib64/libluajit.so", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/products/mt8678-mix/guest-configs/uos_alps_pv8678.lua", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/nbl_vm_srv/data/vm_srv_cfg_8678.pb.txt", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/nbl_vmm/data/uos_mtk8678/uos_bootloader_lk2.pb.txt", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/nbl_vmm/data/vm_audio_cfg.pb.txt", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/nbl_vmm/data/vm_audio_shared_irq.pb.txt", "~/yocto/prebuilt/hypervisor/grt/"),
                ("/home/nebula/grt/thyp-sdk/vmm/nbl_vm_srv/data/nbl_ta_monitor", "~/yocto/prebuilt/hypervisor/grt/")
            ]
            for src, dest in source_destination_pairs:
                src_path = os.path.expanduser(src)
                dest_path = os.path.expanduser(dest)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dest_path)
                logging.info(f"Copied {src_path} to {dest_path}")
            logging.info("All files copied successfully")
        except Exception as e:
            logging.error(f"Error in copy_files: {e}")
            sys.exit(1)

    @log_execution
    def commit_and_push_changes(self, repo_path: str, commit_message: str, branch: str):
        """Commit changes and push to remote repository."""
        try:
            os.chdir(os.path.expanduser(repo_path))
            subprocess.check_call(["git", "add", "."])
            subprocess.check_call(["git", "commit", "-m", commit_message])
            subprocess.check_call(["git", "push", "origin", f"HEAD:refs/for/{branch}"])
            logging.info(f"Changes in '{repo_path}' committed and pushed to branch '{branch}'")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in commit_and_push_changes: {e}")
            sys.exit(1)

    @log_execution
    def commit_and_push_changes_nebula(self):
        """Commit and push changes for nebula."""
        commit_message = self.config.commit_messages['nebula'].format(
            cr_number=self.config.cr_number,
            title=self.config.title,
            description=self.config.description
        )
        
        # Commit changes in ~/grt repository
        grt_repo_path = os.path.expanduser("~/grt")
        try:
            os.chdir(grt_repo_path)
            # Only add specific path
            add_path = os.path.expanduser("~/grt/thyp-sdk/products/mt8678-mix/prebuilt-images")
            subprocess.check_call(["git", "add", add_path])
            subprocess.check_call(["git", "commit", "-m", commit_message])
            subprocess.check_call(["git", "push", "origin", f"HEAD:refs/for/{self.config.grt_branch}"])
            logging.info(f"Changes in '{grt_repo_path}' committed and pushed to branch '{self.config.grt_branch}'")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in committing changes in '{grt_repo_path}': {e}")
            sys.exit(1)

        # Commit changes in ~/yocto/prebuilt/hypervisor/grt repository
        yocto_repo_path = os.path.expanduser("~/yocto/prebuilt/hypervisor/grt")
        try:
            os.chdir(yocto_repo_path)
            subprocess.check_call(["git", "add", "."])
            subprocess.check_call(["git", "commit", "-m", commit_message])
            subprocess.check_call(["git", "push", "grt-mt8678", f"HEAD:refs/for/{self.config.grt_branch}"])
            logging.info(f"Changes in '{yocto_repo_path}' committed and pushed to branch '{self.config.grt_branch}'")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in committing changes in '{yocto_repo_path}': {e}")
            sys.exit(1)

    @log_execution
    def commit_and_push_changes_nebula_sdk(self):
        """Commit and push changes for nebula-sdk."""
        commit_message = self.config.commit_messages['nebula-sdk'].format(
            cr_number=self.config.cr_number,
            title=self.config.title,
            description=self.config.description
        )
        repo_path = os.path.expanduser("~/grt/nebula-sdk")
        dirs_to_add = ['android', 'cmake', 'docs', 'examples', 'hee', 'host', 'make', 'ree', 'test_suite']
        try:
            os.chdir(repo_path)
            # Only add specific directories
            for dir_name in dirs_to_add:
                dir_path = os.path.join(repo_path, dir_name)
                subprocess.check_call(["git", "add", dir_path])
            subprocess.check_call(["git", "commit", "-m", commit_message])
            subprocess.check_call(["git", "push", "origin", f"HEAD:refs/for/{self.config.grt_branch}"])
            logging.info(f"Changes in '{repo_path}' committed and pushed to branch '{self.config.grt_branch}'")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in commit_and_push_changes_nebula_sdk: {e}")
            sys.exit(1)

    @log_execution
    def commit_and_push_changes_tee(self):
        """Commit and push changes for TEE."""
        commit_message = self.config.commit_messages['tee'].format(
            cr_number=self.config.cr_number,
            title=self.config.title,
            description=self.config.description
        )
        repo_path = os.path.expanduser("~/alps/vendor/mediatek/proprietary/trustzone/grt")
        try:
            os.chdir(repo_path)
            # Only add specific path
            add_path = os.path.expanduser("~/alps/vendor/mediatek/proprietary/trustzone/grt/source/common/kernel")
            subprocess.check_call(["git", "add", add_path])
            subprocess.check_call(["git", "commit", "-m", commit_message])
            subprocess.check_call(["git", "push", "grt-mt8678", f"HEAD:refs/for/{self.config.grt_branch}"])
            logging.info(f"Changes in '{repo_path}' committed and pushed to branch '{self.config.grt_branch}'")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in commit_and_push_changes_tee: {e}")
            sys.exit(1)

    @log_execution
    def update_nebula_sources(self):
        """Update nebula sources for zircon and garnet."""
        try:
            commands = [
                f"cd ~/grpower/workspace/nebula/zircon && git checkout -f {self.config.zircon_branch} && git pull",
                f"cd ~/grpower/workspace/nebula/garnet && git checkout -f {self.config.garnet_branch} && git pull",
                "cd ~/grpower && git pull"
            ]
            for cmd in commands:
                subprocess.check_call(cmd, shell=True, executable='/bin/bash')
            logging.info("Nebula sources updated successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error in update_nebula_sources: {e}")
            sys.exit(1)

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Automate tag management and build processes.")
    parser.add_argument('--tag-date', help="Date part of the tag in format YYYY_MMDD_NN", default=None)
    parser.add_argument('--repos', nargs='+', help="List of repositories to include", default=None)
    parser.add_argument('--grt-branch', help="Branch name for GRT", default=None)
    parser.add_argument('--yocto-branch', help="Branch name for Yocto", default=None)
    parser.add_argument('--alps-branch', help="Branch name for ALPS", default=None)
    parser.add_argument('--zircon-branch', help="Branch name for zircon", default=None)
    parser.add_argument('--garnet-branch', help="Branch name for garnet", default=None)
    parser.add_argument('--description', help="Description for commit messages", default=None)
    args = parser.parse_args()

    # Create a default Config instance
    default_config = Config()

    # Instantiate the Config with command-line arguments or default values
    config = Config(
        tag_date=args.tag_date or default_config.tag_date,
        repos=args.repos or default_config.repos,
        grt_branch=args.grt_branch or default_config.grt_branch,
        yocto_branch=args.yocto_branch or default_config.yocto_branch,
        alps_branch=args.alps_branch or default_config.alps_branch,
        zircon_branch=args.zircon_branch or default_config.zircon_branch,
        garnet_branch=args.garnet_branch or default_config.garnet_branch,
        description=args.description or default_config.description,
        cr_number=args.cr_number or default_config.description,
        title=args.title or default_config.description
    )

    repo_manager = RepositoryManager(config)
    build_manager = BuildManager(config)

    # Step 1: Tagging nebula
    logging.info("Starting Step 1: Tagging 'nebula'")
    try:
        os.chdir(os.path.expanduser("~/grpower/workspace/nebula"))
        subprocess.check_call("rm snapshot.xml", shell=True)
        build_manager.update_nebula_sources()
        tagging_script = f"""
        export NO_PIPENV_SHELL=1
        source scripts/env.sh
        jiri runp -j=1 'git tag release-spm.mt8678_mt8676_{config.tag_date}'
        jiri runp 'git push origin release-spm.mt8678_mt8676_{config.tag_date}'
        jiri snapshot snapshot.xml
        """
        subprocess.check_call(tagging_script, shell=True, executable='/bin/bash')
        logging.info(f"Tag 'release-spm.mt8678_mt8676_{config.tag_date}' created and pushed for 'nebula'")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in tagging 'nebula': {e}")
        sys.exit(1)

    # Step 2: Build and commit if necessary
    if any(repo in config.repos for repo in ['nebula', 'nebula-sdk', 'tee']):
        logging.info("Starting Step 2: Build and commit changes")
        build_manager.clean_previous_build()
        if 'nebula' in config.repos:
            build_manager.build_nebula()
            build_manager.copy_files()
            build_manager.commit_and_push_changes_nebula()
            repo_manager.wait_for_user_confirmation("Please confirm that the remote repository has merged the changes for 'nebula'. Press Enter to continue...")
        if 'nebula-sdk' in config.repos:
            build_manager.build_nebula_sdk()
            build_manager.commit_and_push_changes_nebula_sdk()
            repo_manager.wait_for_user_confirmation("Please confirm that the remote repository has merged the changes for 'nebula-sdk'. Press Enter to continue...")
        if 'tee' in config.repos:
            build_manager.build_tee()
            build_manager.commit_and_push_changes_tee()
            repo_manager.wait_for_user_confirmation("Please confirm that the remote repository has merged the changes for 'tee'. Press Enter to continue...")
    else:
        logging.info("Skipping Step 2: No relevant repositories specified")

    # Step 3: Final tagging and pushing for other repositories
    logging.info("Starting Step 3: Final tagging and pushing")
    tag_name = f"release-spm.mt8678_{config.tag_date}"

    # # Ensure tagging for 'nebula' regardless of update status
    # repo_manager.create_and_push_tag(
    #     repo_path="~/grpower",
    #     tag_name=tag_name
    # )

    if 'grpower' in config.repos:
        repo_manager.create_and_push_tag(
            repo_path="~/grpower",
            tag_name=tag_name
        )

    if 'grt' in config.repos:
        repo_manager.create_and_push_tag(
            repo_path="~/grt",
            tag_name=tag_name
        )

    if 'yocto' in config.repos:
        repo_manager.sync_repo(repo_path="~/yocto")
        repo_manager.tag_and_push_all(
            repo_path="~/yocto",
            tag_name=tag_name
        )

    if 'alps' in config.repos:
        repo_manager.sync_repo(repo_path="~/alps")
        repo_manager.tag_and_push_all(
            repo_path="~/alps",
            tag_name=tag_name
        )

if __name__ == "__main__":
    main()
