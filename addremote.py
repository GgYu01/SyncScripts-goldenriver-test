import os
import subprocess

def add_git_remote(base_path, remote_name, remote_url_base):
    for root, dirs, files in os.walk(base_path):
        if '.repo' in root:
            continue
        
        if '.git' in dirs:
            repo_relative_path = os.path.relpath(root, base_path)
            remote_url = f"{remote_url_base}/{repo_relative_path}"
            git_dir = os.path.join(root, '.git')
            
            try:
                subprocess.run(['git', '--git-dir', git_dir, '--work-tree', root, 'remote', 'add', remote_name, remote_url], check=True)
                print(f"Added remote {remote_name} to {root}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to add remote {remote_name} to {root}: {e}")

def remove_git_remote(base_path, remote_name):
    for root, dirs, files in os.walk(base_path):
        if '.repo' in root:
            continue
        
        if '.git' in dirs:
            git_dir = os.path.join(root, '.git')
            
            try:
                subprocess.run(['git', '--git-dir', git_dir, '--work-tree', root, 'remote', 'remove', remote_name], check=True)
                print(f"Removed remote {remote_name} from {root}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to remove remote {remote_name} from {root}: {e}")

if __name__ == "__main__":
    base_path = "/mnt/sst/test/"
    remote_name = "grt-mt8678"
    remote_url_base = "ssh://gaoyx@www.goldenriver.com.cn:29420"
    
    action = input("Enter 'add' to add remote or 'remove' to remove remote: ").strip().lower()
    
    if action == 'add':
        add_git_remote(base_path, remote_name, remote_url_base)
    elif action == 'remove':
        remove_git_remote(base_path, remote_name)
    else:
        print("Invalid action. Please enter 'add' or 'remove'.")
