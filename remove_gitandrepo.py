import os
import shutil

def remove_directories(base_path, directories):
    """
    删除指定路径下的目录及其子文件夹和子目录，包括符号链接。
    :param base_path: 基础路径
    :param directories: 要删除的目录名列表
    """
    for root, dirs, files in os.walk(base_path, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            if name in directories:
                if os.path.islink(dir_path):
                    print(f"正在删除符号链接: {dir_path}")
                    os.unlink(dir_path)
                else:
                    print(f"正在删除目录: {dir_path}")
                    shutil.rmtree(dir_path)

if __name__ == "__main__":
    # 指定要处理的基础路径
    base_path = "/mnt/sso/temp/yocto/"  # 修改此行以设置目标路径

    # 要删除的目录列表
    directories_to_remove = ['.git', '.repo']
    
    # 删除指定目录及其子目录中的指定文件夹
    remove_directories(base_path, directories_to_remove)
