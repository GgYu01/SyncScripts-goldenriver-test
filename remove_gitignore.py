import os
import logging

# 设置日志
log_path = '/mnt/sso/two_78/yocto/log.log'
logging.basicConfig(filename=log_path, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def delete_gitignore_files(base_path):
    try:
        for root, dirs, files in os.walk(base_path, topdown=True):
            # 跳过.repo目录及其子目录
            if '.repo' in root.split(os.sep):
                continue

            # 删除.gitignore文件
            for file in files:
                if file == '.gitignore':
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        logging.info(f"Deleted: {file_path}")
                    except Exception as e:
                        logging.error(f"Error deleting {file_path}: {e}")

    except Exception as e:
        logging.error(f"Error walking through directory {base_path}: {e}")

# 指定路径
base_path = '/mnt/sso/two_78/yocto'

# 执行函数
delete_gitignore_files(base_path)
