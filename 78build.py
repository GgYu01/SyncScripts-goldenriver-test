import os
import pickle
import subprocess
import time
from tabulate import tabulate
from termcolor import colored


# Default parameters
PARAMETERS_FILE = 'Compile_parameters.pkl'

# Function to load or prompt for parameters
def load_or_prompt_parameters():
    if os.path.exists(PARAMETERS_FILE):
        with open(PARAMETERS_FILE, 'rb') as f:
            parameters = pickle.load(f)
    else:
        parameters = {
            'android_src_path': input("Enter the Android source code path: "),
            'yocto_src_path': input("Enter the Yocto source code path: "),
            'flash_image_output_path': input("Enter the final output path of the flash image: ")
        }
        with open(PARAMETERS_FILE, 'wb') as f:
            pickle.dump(parameters, f)
    return parameters

def execute_command(command, cwd):
    process = subprocess.Popen(command, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)
    stdout, _ = process.communicate()
    if process.returncode != 0:
        print(f"Command failed with return code {process.returncode}")
        print(stdout.decode())
        exit(process.returncode)
    else:
        print(f"Command executed successfully: {command}")
        return stdout.decode()

def compile_android():
    os.chdir(android_src_path)  # Change to Android root directory
    commands = [
        "source build/envsetup.sh && export OUT_DIR=out_sys && lunch sys_mssi_auto_64_cn_armv82-userdebug && make sys_images",
        "source build/envsetup.sh && export OUT_DIR=out_hal && lunch hal_mgvi_auto_64_armv82-userdebug && make hal_images",
        "source build/envsetup.sh && export OUT_DIR=out_krn && lunch krn_mgk_64_k61_auto_vm-userdebug && make krn_images",
        "source build/envsetup.sh && export OUT_DIR=out && lunch vext_auto8678p1_64_bsp_vm-userdebug && make vext_images",
        "python out_sys/target/product/mssi_auto_64_cn_armv82/images/split_build.py --system-dir out_sys/target/product/mssi_auto_64_cn_armv82/images --vendor-dir out_hal/target/product/mgvi_auto_64_armv82/images --kernel-dir=out_krn/ target/product/mgk_64_k61_auto_vm/images --vext-dir out/target/product/auto8678p1_64_bsp_vm/images --output-dir out/target/product/auto8678p1_64_bsp_vm/merged"
    ]
    for cmd in commands:
        log_file = cmd.split('&&')[-1].split()[1] + '.log'
        with open(log_file, 'w') as log:
            log.write(execute_command(cmd, android_src_path))

def compile_yocto():
    os.chdir(yocto_src_path)  # Change to Yocto root directory
    env_vars = "BB_NO_NETWORK=\"1\""
    setup_cmd = "TEMPLATECONF=${PWD}/meta/meta-mediatek-mt8678/conf/base/auto8678p1_64_hyp_gpu source meta/poky/oe-init-build-env"
    bitbake_cmd = "time bitbake -k mtk-core-image-auto8678-hyp"
    execute_command(env_vars, yocto_src_path)
    execute_command(setup_cmd, yocto_src_path)
    if not os.path.exists('conf/site.conf'):
        execute_command("ln -s /proj/srv_gerrit_central_mirror/lib/sources/kirkstone/site.conf conf/site.conf", yocto_src_path)
    with open('build.log', 'w') as log:
        log.write(execute_command(bitbake_cmd, yocto_src_path))

def rename_and_copy_files():
    yocto_boot_img_path = os.path.join(yocto_src_path, 'build/tmp/deploy/images/auto8678p1_64_hyp_gpu/boot.img')
    android_merged_path = os.path.join(android_src_path, 'out/target/product/auto8678p1_64_bsp_vm/merged')
    os.rename(yocto_boot_img_path, yocto_boot_img_path.replace('boot.img', 'yocto-boot.img'))
    file_names = ['userdata.img', 'super.img', 'dtbo.img', 'init_boot.img', 'vendor_boot.img', 'boot.img']
    for file_name in file_names:
        src = os.path.join(android_merged_path, file_name)
        dst = os.path.join(yocto_src_path, 'build/tmp/deploy/images/auto8678p1_64_hyp_gpu/', file_name)
        shutil.copy(src, dst)
    yocto_images_path = os.path.join(yocto_src_path, 'build/tmp/deploy/images/auto8678p1_64_hyp_gpu')
    shutil.copytree(yocto_images_path, flash_image_output_path)

# Main function
def main():
    parameters = load_or_prompt_parameters()
    headers = ["Parameter", "Value"]
    data = [(k, v) for k, v in parameters.items()]
    table = tabulate(data, headers, tablefmt="grid")
    print(colored(table, 'cyan'))
    time.sleep(50)  # Wait for 10 seconds before proceeding
    compile_android()
    compile_yocto()
    rename_and_copy_files()



# Main execution
if __name__ == "__main__":
    main()

# End of code
