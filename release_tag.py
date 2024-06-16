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
DEFAULT_THREAD_COUNT = 64
REPO_INFO = {
    'alps': {
        'repo_path': '/home/gaoyx/san_78/alps',
        'manifest_path': '/home/gaoyx/san_78/alps/.repo/manifests/alps.xml',
        'output_path': '/mnt/d/78image/test/alps'
    },
    'yocto': {
        'repo_path': '/home/gaoyx/san_78/yocto',
        'manifest_path': '/home/gaoyx/san_78/yocto/.repo/manifests/yocto.xml',
        'output_path': '/mnt/d/78image/test/yocto'
    }
}
DEFAULT_TAG1 = ''
DEFAULT_TAG2 = ''
REPO_TOOL_PATH = '/home/gaoyx/.bin/repo'

# Function to get the latest and second latest tags from the first repo
def get_tags(repo_root_path, manifest_path):
    # Parse the manifest to get the first project path
    repo_paths = parse_manifest(manifest_path, repo_root_path)
    first_repo_path = os.path.join(repo_root_path, repo_paths[0])
    # Change directory to the first repo path
    os.chdir(first_repo_path)
    # Get the latest tag
    latest_tag = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], capture_output=True, text=True, check=True).stdout.strip()
    # Get the list of tags, sorted by creation date
    tags = subprocess.run(['git', 'tag', '--sort=-creatordate'], capture_output=True, text=True, check=True).stdout.strip().split('\n')
    # The second latest tag is the one before the latest
    second_latest_tag = tags[tags.index(latest_tag) - 1]
    return latest_tag, second_latest_tag

# Function to generate snapshot manifest using repo command and move it to the output path
def generate_snapshot_manifest_with_repo(repo_tool_path, repo_root_path, patch_output_path):
    # Change directory to the repo root
    os.chdir(repo_root_path)
    # Generate the snapshot manifest
    subprocess.run([repo_tool_path, 'manifest', '-r', '-o', 'snapshot.xml'], check=True)
    snapshot_manifest_path = os.path.join(repo_root_path, "snapshot.xml")
    console.log(f'Snapshot manifest generated at: {snapshot_manifest_path}')
    
    # Move the snapshot manifest to the patch output directory
    shutil.move(snapshot_manifest_path, patch_output_path)
    console.log(f'Snapshot manifest moved to: {os.path.join(patch_output_path, "snapshot.xml")}')

# Function to parse the manifest file and get repository paths
def parse_manifest(manifest_path, repo_root_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    repo_paths = [os.path.join(repo_root_path, project.get('path')) for project in root.findall('project')]
    return repo_paths

# Function to generate patches between tags and return the list of new patch files
def generate_patches(repo_path, tag1, tag2, output_path):
    # Get the list of patch files before generating new ones
    existing_patches = set(os.listdir(repo_path))
    
    try:
        # Generate patches only if there are changes
        subprocess.run(['git', 'format-patch', f'{tag1}..{tag2}', '-o', output_path], cwd=repo_path, check=True)
        console.log(f'Patches generated for repository: {repo_path}')
    except subprocess.CalledProcessError as e:
        console.log(f'Error generating patches for repository: {repo_path}', style="bold red")
        return []

    # Get the list of all patch files after generating new ones
    all_patches = set(os.listdir(repo_path))
    # Determine the new patches by subtracting the existing ones from all patches
    new_patches = list(all_patches - existing_patches)
    # Return the full paths of the new patch files
    return [os.path.join(repo_path, f) for f in new_patches]

# Function to copy new patches to the output path and zip them
def copy_and_zip_patches(new_patches, patch_output_path, repo_root_path):
    # Ensure the output directory exists
    os.makedirs(patch_output_path, exist_ok=True)
    
    zip_file_path = os.path.join(patch_output_path, 'patches.zip')
    with ZipFile(zip_file_path, 'w') as zipf:
        for patch_full_path in new_patches:
            relative_patch_path = os.path.relpath(os.path.dirname(patch_full_path), repo_root_path)
            target_dir = os.path.join(patch_output_path, relative_patch_path)
            # Ensure the target directory exists
            os.makedirs(target_dir, exist_ok=True)
            shutil.copy(patch_full_path, target_dir)
            zipf.write(patch_full_path, os.path.join(relative_patch_path, os.path.basename(patch_full_path)))
            console.log(f'Patch copied and added to zip: {patch_full_path}')
    console.log(f'All patches zipped into: {zip_file_path}')

# Worker function for threading
def worker(repo_queue, tag1, tag2, patch_output_path, tag_repos, generated_patches):
    while not repo_queue.empty():
        repo_path = repo_queue.get()
        if tag_repos:
            try:
                # Tagging the repository
                subprocess.run(['git', 'tag', tag1], cwd=repo_path, check=True)
            except subprocess.CalledProcessError as e:
                console.log(f'Error tagging repository: {repo_path}', style="bold red")
        # Call the generate_patches function and collect generated patches
        generated_patches.extend(generate_patches(repo_path, tag1, tag2, repo_path))
        repo_queue.task_done()

# Main function to orchestrate the script execution for all repos
def main(tag1=DEFAULT_TAG1, tag2=DEFAULT_TAG2, tag_repos=False):
    for repo_id, info in REPO_INFO.items():
        repo_root_path = info['repo_path']
        manifest_path = info['manifest_path']
        patch_output_path = info['output_path']
        repo_paths = parse_manifest(manifest_path, repo_root_path)
        repo_queue = Queue()
        generated_patches = []  # List to track generated patches

        # Get tags if not provided
        if not tag1 or not tag2:
            tag1, tag2 = get_tags(repo_root_path, manifest_path)

        # Enqueue repository paths
        for repo_path in repo_paths:
            repo_queue.put(repo_path)

        # Start threading
        threads = []
        for _ in range(DEFAULT_THREAD_COUNT):
            thread = threading.Thread(target=worker, args=(repo_queue, tag1, tag2, patch_output_path, tag_repos, generated_patches))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Copy patches and zip them
        copy_and_zip_patches(generated_patches, patch_output_path, repo_root_path)

        # Generate snapshot manifest with repo
        generate_snapshot_manifest_with_repo(REPO_TOOL_PATH, repo_root_path, patch_output_path)

    console.log('Script execution completed for all repositories.')

if __name__ == '__main__':
    # Example usage: python script.py --manifest_path '/path/to/manifest.xml' --patch_output_path '/path/to/output' --tag1 'v1.0' --tag2 'v0.9'
    main()

# End of code
