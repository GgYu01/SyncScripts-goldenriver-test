#!/usr/bin/env python3

import os
import asyncio
import subprocess

# Git repository paths
GIT_REPOS = [
    '/mnt/sso/one_78/grt', '/mnt/sso/two_78/grt', '/mnt/sso/san_78/grt', '/mnt/sso/four_78/grt', '/mnt/sso/wu_78/grt',
    '/mnt/sso/one_78/grt_be', '/mnt/sso/two_78/grt_be', '/mnt/sso/san_78/grt_be', '/mnt/sso/four_78/grt_be', '/mnt/sso/wu_78/grt_be'
]

# Repo paths
REPO_PATHS = [
    '/mnt/sso/one_78/yocto', '/mnt/sso/two_78/yocto', '/mnt/sso/san_78/yocto', '/mnt/sso/four_78/yocto', '/mnt/sso/wu_78/yocto',
    '/mnt/sst/two_78/alps', '/mnt/sst/san_78/alps', '/mnt/sst/four_78/alps', '/mnt/sst/wu_78/alps'
]

# Jiri paths
JIRI_PATHS = [
    '/mnt/sso/one_78/grpower/workspace/nebula', '/mnt/sso/two_78/grpower/workspace/nebula',
    '/mnt/sso/san_78/grpower/workspace/nebula', '/mnt/sso/four_78/grpower/workspace/nebula',
    '/mnt/sso/wu_78/grpower/workspace/nebula'
]

async def run_command(command):
    """
    Run a shell command asynchronously.
    
    :param command: Command to run.
    """
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"[INFO] Command succeeded: {command}")
        print(stdout.decode())
    else:
        print(f"[ERROR] Command failed: {command}")
        print(stderr.decode())

async def git_gc(repo_path):
    """
    Perform garbage collection on a git repository.
    
    :param repo_path: Path to the git repository.
    """
    await run_command(f"git -C {repo_path} gc")

async def repo_gc(repo_path):
    """
    Perform garbage collection on a repo repository using parallel execution.
    
    :param repo_path: Path to the repo repository.
    """
    # Get list of projects
    process = await asyncio.create_subprocess_shell(
        f"repo forall -c 'echo $REPO_PATH'",
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"[ERROR] Failed to list projects in repo: {repo_path}")
        print(stderr.decode())
        return

    project_paths = stdout.decode().splitlines()

    # Perform git gc concurrently for all projects
    tasks = [run_command(f"git -C {os.path.join(repo_path, project_path)} gc") for project_path in project_paths]
    await asyncio.gather(*tasks)

async def jiri_gc(jiri_path):
    """
    Perform garbage collection on a jiri repository using parallel execution.
    
    :param jiri_path: Path to the jiri repository.
    """
    await run_command(f"cd {jiri_path} && /mnt/sso/one_78/grpower/bin/jiri runp 'git gc'")

async def main():
    """
    Main function to run garbage collection on all repositories.
    """
    tasks = []

    Schedule git gc tasks
    for path in GIT_REPOS:
        tasks.append(git_gc(path))

    # Schedule repo gc tasks
    for path in REPO_PATHS:
        tasks.append(repo_gc(path))

    # Schedule jiri gc tasks
    for path in JIRI_PATHS:
        tasks.append(jiri_gc(path))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
