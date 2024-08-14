import os
import subprocess
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Define paths for git, repo, and jiri repositories
GIT_REPOS = [
    "/mnt/sso/one_78/grt", "/mnt/sso/two_78/grt", "/mnt/sso/san_78/grt",
    "/mnt/sso/four_78/grt", "/mnt/sso/wu_78/grt", "/mnt/sso/one_78/grt_be",
    "/mnt/sso/two_78/grt_be", "/mnt/sso/san_78/grt_be", "/mnt/sso/four_78/grt_be",
    "/mnt/sso/wu_78/grt_be"
]

REPO_REPOS = [
    "/mnt/sso/one_78/yocto", "/mnt/sso/two_78/yocto", "/mnt/sso/san_78/yocto",
    "/mnt/sso/four_78/yocto", "/mnt/sso/wu_78/yocto", "/mnt/sst/one_78/alps",
    "/mnt/sst/two_78/alps", "/mnt/sst/san_78/alps", "/mnt/sst/four_78/alps",
    "/mnt/sst/wu_78/alps"
]

JIRI_REPOS = [
    "/mnt/sso/one_78/grpower/workspace/nebula", "/mnt/sso/two_78/grpower/workspace/nebula",
    "/mnt/sso/san_78/grpower/workspace/nebula", "/mnt/sso/four_78/grpower/workspace/nebula",
    "/mnt/sso/wu_78/grpower/workspace/nebula"
]

async def run_git_gc(repo_path: str):
    """Run 'git gc' in the given repository path."""
    process = await asyncio.create_subprocess_exec(
        'git', 'gc',
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        print(f"'git gc' completed successfully in {repo_path}")
    else:
        print(f"Error running 'git gc' in {repo_path}: {stderr.decode().strip()}")

async def run_repo_gc(repo_path: str):
    """Run 'git gc' in repo-managed repository."""
    process = await asyncio.create_subprocess_exec(
        'sh', '-c', f'cd {repo_path} && git gc',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        print(f"'git gc' completed successfully in {repo_path}")
    else:
        print(f"Error running 'git gc' in {repo_path}: {stderr.decode().strip()}")

def run_jiri_gc(jiri_repos: list):
    """Run 'jiri runp' to execute 'git gc' concurrently in jiri repositories."""
    command = ["jiri", "runp", "git", "gc"]
    for repo in jiri_repos:
        command.append(repo)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("'jiri runp git gc' completed successfully")
    else:
        print(f"Error running 'jiri runp git gc': {result.stderr.decode().strip()}")

async def main():
    # Run 'git gc' on git repositories concurrently
    git_tasks = [run_git_gc(repo) for repo in GIT_REPOS]
    
    # Run 'git gc' on repo-managed repositories concurrently
    repo_tasks = [run_repo_gc(repo) for repo in REPO_REPOS]
    
    # Use ThreadPoolExecutor to run 'jiri runp git gc' concurrently
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(executor, run_jiri_gc, JIRI_REPOS)

    # Wait for all tasks to complete
    await asyncio.gather(*git_tasks, *repo_tasks)

if __name__ == "__main__":
    asyncio.run(main())
