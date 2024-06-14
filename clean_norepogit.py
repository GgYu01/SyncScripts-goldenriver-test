import os
import shutil

def clear_directories(base_path):
    for root, dirs, files in os.walk(base_path, topdown=False):
        if '.git' in dirs:
            git_parent_dir = os.path.abspath(os.path.join(root, '.git', os.pardir))
            # Check if .git is inside .repo, if so, skip processing
            if '.repo' not in os.path.relpath(git_parent_dir, base_path).split(os.sep):
                # Do not delete the .git directory itself
                dirs.remove('.git')
                print(f"Skipping .git directory: {os.path.join(root, '.git')}")
                # Now, remove all subdirectories and files in the parent directory of .git
                for item in os.listdir(git_parent_dir):
                    item_path = os.path.join(git_parent_dir, item)
                    if os.path.isdir(item_path) and not os.path.islink(item_path) and item != '.git' and item != '.repo':
                        print(f"Deleting directory: {item_path}")
                        shutil.rmtree(item_path)
                    elif os.path.isfile(item_path) and not os.path.islink(item_path):
                        print(f"Deleting file: {item_path}")
                        os.remove(item_path)
        elif '.repo' in dirs:
            # Skip processing for .repo directory and all its subdirectories
            dirs.remove('.repo')
            print(f"Skipping .repo directory: {os.path.join(root, '.repo')}")

# Replace '/path/to/base/directory' with the actual path to the base directory
base_directory = '/mnt/sso/san_78/alps'
clear_directories(base_directory)
