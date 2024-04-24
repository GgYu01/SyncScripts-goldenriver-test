import os
import xml.etree.ElementTree as ET
import threading
from queue import Queue
import subprocess
import shutil
from rich.console import Console
from rich.traceback import install
from zipfile import ZipFile

# Install rich traceback for better error handling
install()
console = Console()

# Constants and default values
DEFAULT_THREAD_COUNT = 32
DEFAULT_MANIFEST_PATH = '/home/gaoyx/san_78/yocto_mt8678/.repo/manifests/yocto.xml'
DEFAULT_PATCH_OUTPUT_PATH = '/mnt/d/patch/yocto'
DEFAULT_TAG1 = 'release-spm.mt8678_2024_04_09'
DEFAULT_TAG2 = 'release-spm.mt8678_2024_04_03'

# Function to parse the manifest file and get repository paths
def parse_manifest(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    repo_paths = [os.path.join('/home/gaoyx/san_78/yocto_mt8678', project.get('path')) for project in root.findall('project')]
    return repo_paths

# Function to generate patches between tags
def generate_patches(repo_path, tag1, tag2, output_path):
    try:
        # Check for changes between tags
        changes_output = subprocess.run(['git', 'diff', '--name-only', tag2, tag1], cwd=repo_path, capture_output=True, text=True, check=True)
        changes = changes_output.stdout.strip()
        if changes:
            # Generate patches only if there are changes
            subprocess.run(['git', 'format-patch', f'{tag2}..{tag1}', '-o', output_path], cwd=repo_path, check=True)
            console.log(f'Patches generated for repository: {repo_path}')
        else:
            console.log(f'No changes to generate patches for repository: {repo_path}')
    except subprocess.CalledProcessError as e:
        console.log(f'Error generating patches for repository: {repo_path}', style="bold red")

# Worker function for threading
def worker(repo_queue, tag1, tag2, patch_output_path, tag_repos):
    while not repo_queue.empty():
        repo_path = repo_queue.get()
        if tag_repos:
            try:
                # Tagging the repository
                subprocess.run(['git', 'tag', tag1], cwd=repo_path, check=True)
            except subprocess.CalledProcessError as e:
                console.log(f'Error tagging repository: {repo_path}', style="bold red")
        # Call the generate_patches function
        generate_patches(repo_path, tag1, tag2, patch_output_path)
        repo_queue.task_done()

# Function to copy patches to the output path and zip them
def copy_and_zip_patches(repo_paths, patch_output_path, tag1):
    zip_file_path = os.path.join(patch_output_path, f'{tag1}_patches.zip')
    with ZipFile(zip_file_path, 'w') as zipf:
        for repo_path in repo_paths:
            patch_file = os.path.join(repo_path, f'{tag1}_patch.patch')
            if os.path.exists(patch_file):
                relative_patch_path = os.path.relpath(repo_path, '/home/gaoyx/san_78/yocto_mt8678')
                target_dir = os.path.join(patch_output_path, relative_patch_path)
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy(patch_file, target_dir)
                zipf.write(patch_file, os.path.join(relative_patch_path, f'{tag1}_patch.patch'))
                console.log(f'Patch copied and added to zip: {patch_file}')
    console.log(f'All patches zipped into: {zip_file_path}')

# Function to generate snapshot manifest
def generate_snapshot_manifest(repo_paths, snapshot_path):
    snapshot_file_path = os.path.join(snapshot_path, 'snapshot.xml')
    root = ET.Element('manifest')

    for repo_path in repo_paths:
        project = ET.SubElement(root, 'project')
        project.set('path', os.path.relpath(repo_path, '/home/gaoyx/san_78/yocto_mt8678'))
        project.set('revision', subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo_path, capture_output=True, text=True, check=True).stdout.strip())

    tree = ET.ElementTree(root)
    tree.write(snapshot_file_path)
    console.log(f'Snapshot manifest generated at: {snapshot_file_path}')

# Main function to orchestrate the script execution
def main(manifest_path=DEFAULT_MANIFEST_PATH, patch_output_path=DEFAULT_PATCH_OUTPUT_PATH, tag1=DEFAULT_TAG1, tag2=DEFAULT_TAG2, tag_repos=False):
    repo_paths = parse_manifest(manifest_path)
    repo_queue = Queue()

    # Enqueue repository paths
    for repo_path in repo_paths:
        repo_queue.put(repo_path)  # Changed from tuple to single repo_path

    # Start threading
    threads = []
    for _ in range(DEFAULT_THREAD_COUNT):
        thread = threading.Thread(target=worker, args=(repo_queue, tag1, tag2, patch_output_path, tag_repos))  # Added missing arguments
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Copy patches and zip them
    copy_and_zip_patches(repo_paths, patch_output_path, tag1)

    # Generate snapshot manifest
    generate_snapshot_manifest(repo_paths, os.getcwd())

    console.log('Script execution completed.')

if __name__ == '__main__':
    # Example usage: python script.py --manifest_path '/path/to/manifest.xml' --patch_output_path '/path/to/output' --tag1 'v1.0' --tag2 'v0.9'
    main()

# End of code
