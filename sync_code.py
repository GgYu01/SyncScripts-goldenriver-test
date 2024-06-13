import asyncio
import os
import subprocess
import shutil
from rich.console import Console
from rich.traceback import install

# Install rich traceback globally for better error visibility
install()

# Structured and modular configuration for repository synchronization
config = {
    'connection': {
        'user': 'gaoyx',
        'domain': 'www.goldenriver.com.cn',
        'port': 29420,
    },
    'base_dir': '/mnt',
    'project_name': 'two_78',
    'branch': 'release-spm.mt8678_2024_0524',
    'repositories': {
        'repo': [
            {
                'disk': 'sst',
                'repo_name': 'alps',
                'manifest': 'alps.xml',
            },
            {
                'disk': 'sso',
                'repo_name': 'yocto',
                'manifest': 'yocto.xml',
            }
        ],
        'git': [
            {
                'disk': 'sso',
                'repo_path': 'yocto/src/hypervisor',
                'repo_name': 'grt',
            },
            {
                'disk': 'sso',
                'repo_path': 'yocto/src/hypervisor',
                'repo_name': 'grt_be',
            }
        ]
    }
}

console = Console()

class RepositorySync:
    """Class to handle synchronization of repositories using both git and repo tools."""

    def __init__(self, config):
        self.config = config

    async def run_cmd(self, cmd: list, cwd: str, repo_name: str) -> bool:
        """Execute a shell command in a subprocess and handle the output."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            console.log(f"[{repo_name}] Success: {' '.join(cmd)}", style="green")
            return True
        else:
            console.log(f"[{repo_name}] Error: {' '.join(cmd)} | {stderr.decode().strip()}", style="red")
            return False

    async def sync_repo(self, disk: str, repo_name: str, manifest: str):
        """Synchronize a repository using the `repo` tool."""
        path = os.path.join(self.config['base_dir'], disk, self.config['project_name'], repo_name)
        if not os.path.exists(path):
            for i in range(6):
                console.log(f"Folder not found, will create in {60 - i * 10} seconds: {path}", style="yellow")
                await asyncio.sleep(10)
            os.makedirs(path, exist_ok=True)

        while not await self.run_cmd([
            'repo', 'init', '-u', f"ssh://{self.config['connection']['user']}@{self.config['connection']['domain']}:{self.config['connection']['port']}/manifest",
            '-b', self.config['branch'], '-m', manifest
        ], cwd=path, repo_name=repo_name):
            console.log(f"repo init failed, retrying: {path}", style="bold red")
            await asyncio.sleep(10)

        while not await self.run_cmd(['repo', 'sync', '-j8'], cwd=path, repo_name=repo_name):
            await asyncio.sleep(10)

    async def sync_git(self, disk: str, repo_path: str, repo_name: str):
        """Clone a git repository."""
        full_path = os.path.join(self.config['base_dir'], disk, self.config['project_name'], repo_name)
        if os.path.exists(full_path):
            console.log(f"Repository already synchronized: {full_path}", style="green")
            return

        clone_cmd = [
            'git', 'clone', '--branch', self.config['branch'],
            f"ssh://{self.config['connection']['user']}@{self.config['connection']['domain']}:{self.config['connection']['port']}/{repo_path}/{repo_name}", full_path
        ]
        if not await self.run_cmd(clone_cmd, cwd=os.path.dirname(full_path), repo_name=repo_name):
            shutil.rmtree(full_path, ignore_errors=True)
            await asyncio.sleep(10)
            await self.run_cmd(clone_cmd, cwd=os.path.dirname(full_path), repo_name=repo_name)

    async def main_sync(self):
        """Coordinate the synchronization of all repositories."""
        repo_tasks = [self.sync_repo(**repo) for repo in self.config['repositories']['repo']]
        git_tasks = [self.sync_git(**git) for git in self.config['repositories']['git']]
        tasks = repo_tasks + git_tasks
        await asyncio.gather(*tasks)
        console.log("All repositories have been synchronized successfully.", style="bold green")

if __name__ == "__main__":
    syncer = RepositorySync(config)
    asyncio.run(syncer.main_sync())
