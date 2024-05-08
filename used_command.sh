export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/hpvr/Downloads/SP_Flash_Tool_v5.2228_Linux
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/hpvr/Downloads/SP_Flash_Tool_v5.2228_Linux/lib
OUTPUT_LOAD_PATH="/mnt/DATA/output_mix_user"
chmod 777 $OUTPUT_LOAD_PATH -R
chown hpvr:hpvr $OUTPUT_LOAD_PATH -R

adb wait-for-device reboot
ssh -o StrictHostKeyChecking=no root@192.168.1.101 nohup reboot
/home/hpvr/Downloads/SP_Flash_Tool_v5.2228_Linux/flash_tool -d /home/hpvr/Downloads/SP_Flash_Tool_v5.2228_Linux/MTK_mt8675_diagnose_AllInOne_DA.bin -s $OUTPUT_LOAD_PATH/MT6873_Android_scatter.txt -c format-download

dmesg -n 4 
echo 0 > /proc/sys/kernel/printk
nbl_vm_ctl shell 0
rsync -aP --remove-source-files --info=progress2 line_home /mnt/DATA/
7z a -t7z -v20g -mx=9 -m0=LZMA2 -mmt=32 MT8675_Hyper.7z MT8675_Hyper
7z x yocto.7z.001 -r -o./output
du -h --max-depth=1
sudo docker image prune -a
sudo docker system prune -a
sudo apt remove git git-man
sudo apt install git=1:2.25.1-1ubuntu3 git-man=1:2.25.1-1ubuntu3
du -d 1 -h DATA/
vnstat -i eth0 -l
cat /proc/sys/vm/swappiness
sudo sysctl vm.swappiness=100
sudo gedit /etc/sysctl.conf

7z a -t7z -mx=0 -m0=Copy -mmt=32 /mnt/DATA/output-tbox-user.7z /mnt/DATA/mmio_home/mt8675/out/tbox/user/output_load_spm8675/
7z a -v20g -ttar -m0=Copy -mmt=32 yocto.tar yocto
tar -zcvf

tinymix 'UL2_CH1 I2S8_CH1' 1
tinymix 'UL2_CH2 I2S8_CH2' 1
tinymix I2S8_HD_Mux Low_Jitter
tinycap /sdcard/i2s8-1.wav -D 0 -d 11 -r 96000 -b 16 -c 2

taskset -a 1 /data/dhry/dhry32 && \
taskset -a 2 /data/dhry/dhry32 && \
taskset -a 4 /data/dhry/dhry32 && \
taskset -a 8 /data/dhry/dhry32 && \
taskset -a 10 /data/dhry/dhry32 && \
taskset -a 20 /data/dhry/dhry32 && \
taskset -a 40 /data/dhry/dhry32 && \
taskset -a 80 /data/dhry/dhry32

1000000000

200851558

CPU定频(Android)
echo 4 4 > /proc/ppm/policy/ut_fix_core_num
echo 0 0 > /proc/ppm/policy/ut_fix_freq_idx
 
GPU定频(Yocto)
echo 902000 > /proc/gpufreq/gpufreq_opp_freq
 
DRAM定频
echo 0 > /sys/devices/platform/10012000.dvfsrc/helio-dvfsrc/dvfsrc_force_vcore_dvfs_opp
 
Disable thermal 
echo 1 117000 0 mtktscpu-sysrst 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 250 1 > /proc/driver/thermal/tzcpu
echo 1 100000 0 mtktsAP-sysrst 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 1000 1 > /proc/driver/thermal/tzbts
echo 1 120000 0 mtk-cl-shutdown02 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 0 0 no-cooler 1000 1 > /proc/driver/thermal/tzbtspa


thermal:
while true; do cat /sys/devices/system/cpu/cpufreq/policy?/scaling_governor | xargs echo -n; echo -n ' '; cat /sys/devices/system/cpu/cpufreq/policy?/scaling_cur_freq | xargs echo -n; echo -n ' '; cat /sys/class/thermal/thermal_zone4/temp; sleep 2; done


236的密码：goldenriver_123  PVT 智晔
192.168.170.235 nebula nebula

cd /home/gaoyx/yocto/src/hypervisor/thyp-sdk/products/common
./install.sh mt8675-mix /home/gaoyx/alps /home/gaoyx/yocto
cd /home/gaoyx/alps 
./build.sh mix /home/gaoyx/yocto

cd /home/gaoyx/yocto/src/hypervisor/thyp-sdk/products/common
./install.sh mt8675-tbox /home/gaoyx/alps /home/gaoyx/yocto
cd /home/gaoyx/alps 
./build.sh tbox /home/gaoyx/yocto

cd /home/gaoyx/alps
/home/gaoyx/alps/build.sh alps

cd /home/gaoyx/yocto
export TEMPLATECONF=${PWD}/meta/meta-mediatek-mt8675/conf/base/spm8675p1_64
source meta/poky/oe-init-build-env
time bitbake mtk-core-image-spm8675 2>&1 | tee build.log

sudo apt install -y linux-tools-5.15.0-91-generic linux-cloud-tools-5.15.0-91-generic
watch -n 1 sudo cpupower monitor

git_alps.sh clean -ffd && git_yocto.sh clean -ffd && git_thyp_sdk.sh clean -ffd && git_be_sdk.sh clean -ffd && git -C ~/grpower/workspace/thyp-docker clean -ffd
git_alps.sh checkout -- . && git_yocto.sh checkout -- . && git_thyp_sdk.sh checkout -- . && git_be_sdk.sh checkout -- . && git -C ~/grpower/workspace/thyp-docker checkout -- .

mtk公版的adb Android需要使用alps/kernel-4.14/arch/arm64/configs/spm8675p1_64_mix_defconfig 的CONFIG_VIRTIO_CONSOLE=n 修改后打开

suspend resume 流程
nbl_vm_ctl shell 0
su
input keyevent 26
  
echo 0 > /sys/module/printk/parameters/console_suspend
echo 1 > /proc/mtprintk
echo 7       4       7      7 > proc/sys/kernel/printk
android system suspend
cpuhotplug halt cpu 0
  
echo mem >/sys/power/state
echo timer_val_cust 28000 > /sys/power/spm/suspend_ctrl
echo 2 > /sys/guest_os/android/resume

cd thyp-sdk/
source scripts/env.sh
gx set --sdk /home/gaoyx/grpower/workspace/thyp-docker/user_home/nebula-sdk

adb push 4K-30fps.mp4 1080-60fps.mp4 敲鼓.avi l-mkv.mkv /mnt/runtime/default/emulated/0/Download

git_alps.sh clean -ffd && git_yocto.sh clean -ffd && git_thyp_sdk.sh clean -ffd && git -C ~/grpower/workspace/thyp-docker clean -ffd
git_alps.sh checkout -- . && git_yocto.sh checkout -- . && git_thyp_sdk.sh checkout -- . && git -C ~/grpower/workspace/thyp-docker checkout -- .