import asyncio
import os
import subprocess
import shutil
from rich.console import Console
from rich.traceback import install

# Install rich traceback globally for better error visibility
install()

console = Console()

class RepositorySync:
    """Class to handle synchronization of repositories using both git and repo tools.

    Attributes:
        user (str): Username used in the SSH URL.
        domain (str): Domain of the repository server.
        port (int): Port number for SSH connection.
        base_dir (str): Base directory for all repository operations.
        project_name (str): Name of the code synchronization project.
        branch (str): Branch name to be used across all repositories.
    """

    def __init__(self, user: str, domain: str, port: int, base_dir: str, project_name: str, branch: str):
        self.user = user
        self.domain = domain
        self.port = port
        self.base_dir = base_dir
        self.project_name = project_name
        self.branch = branch

    async def run_cmd(self, cmd: list, cwd: str) -> bool:
        """Execute a shell command in a subprocess and handle the output."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            console.log(f"Success: {' '.join(cmd)}", style="green")
            return True
        else:
            console.log(f"Error: {' '.join(cmd)} | {stderr.decode().strip()}", style="red")
            return False

    async def sync_repo(self, disk: str, repo_name: str):
        """Synchronize a repository using the `repo` tool."""
        path = os.path.join(self.base_dir, disk, self.project_name, repo_name)
        manifest = f"{repo_name}.xml"
        os.makedirs(path, exist_ok=True)

        init_success = False
        for _ in range(6):
            if await self.run_cmd([
                'repo', 'init', '-u', f"ssh://{self.user}@{self.domain}:{self.port}/manifest",
                '-b', self.branch, '-m', manifest
            ], cwd=path):
                init_success = True
                break
            await asyncio.sleep(10)

        if not init_success:
            console.log(f"Failed to initialize repo at {path}.", style="bold red")
            return

        while not await self.run_cmd(['repo', 'sync', '-j2048'], cwd=path):
            await asyncio.sleep(10)

    async def sync_git(self, disk: str, repo_path: str, repo_name: str):
        """Clone a git repository."""
        full_path = os.path.join(self.base_dir, disk, self.project_name, repo_path, repo_name)
        if os.path.exists(full_path):
            console.log(f"Repository already synchronized: {full_path}", style="green")
            return

        clone_cmd = [
            'git', 'clone', '--branch', self.branch,
            f"ssh://{self.user}@{self.domain}:{self.port}/{repo_path}/{repo_name}", full_path
        ]
        if not await self.run_cmd(clone_cmd, cwd=os.path.dirname(full_path)):
            shutil.rmtree(full_path, ignore_errors=True)
            await asyncio.sleep(10)
            await self.run_cmd(clone_cmd, cwd=os.path.dirname(full_path))

    async def main_sync(self):
        """Coordinate the synchronization of all repositories."""
        tasks = [
            self.sync_repo('sst', 'alps'),
            self.sync_repo('sso', 'yocto'),
            self.sync_git('sso', 'yocto/src/hypervisor', 'grt'),
            self.sync_git('sso', 'yocto/src/hypervisor', 'grt_be')
        ]
        await asyncio.gather(*tasks)
        console.log("All repositories have been synchronized successfully.", style="bold green")

if __name__ == "__main__":
    syncer = RepositorySync(
        user="gaoyx",
        domain="www.goldenriver.com.cn",
        port=29420,
        base_dir="/mnt",
        project_name="one_78",
        branch="release-spm.mt8678_2024_0524"
    )
    asyncio.run(syncer.main_sync())
