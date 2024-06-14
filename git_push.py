import os
import subprocess
import logging

# 配置日志记录
log_file = '/mnt/sso/two_78/alps/log.log'
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def push_git_remote(base_path, remote_name, branch_name):
    for root, dirs, files in os.walk(base_path):
        # 跳过 .repo 目录及其子目录
        if '.repo' in root:
            continue
        
        if '.git' in dirs:
            git_dir = os.path.join(root, '.git')
            print(f"Processing path: {root}")
            logging.info(f"Processing path: {root}")
            try:
                result = subprocess.run(
                    ['git', '--git-dir', git_dir, '--work-tree', root, 'push', remote_name, branch_name],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logging.info(f"Successfully pushed {branch_name} to {remote_name} in {root}")
                logging.info(result.stdout)
                print(f"Successfully pushed {branch_name} to {remote_name} in {root}")
            except subprocess.CalledProcessError as e:
                logging.warning(f"Failed to push {branch_name} to {remote_name} in {root}")
                logging.warning(e.stdout)
                logging.warning(e.stderr)
                print(f"Warning: Failed to push {branch_name} to {remote_name} in {root}. Check log for details.")

if __name__ == "__main__":
    base_path = "/mnt/sso/two_78/alps"
    remote_name = "grt-mt8678"
    branch_name = "master"
    
    push_git_remote(base_path, remote_name, branch_name)
