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
nbl_vm_ctl shell
rsync -aP --remove-source-files --info=progress2 line_home /mnt/DATA/
rsync -av /mnt/sst/new/alps /mnt/sso/two_78/

du -h --max-depth=1
sudo docker image prune -a
sudo docker system prune -a
sudo apt remove git git-man
sudo apt install git=1:2.25.1-1ubuntu3 git-man=1:2.25.1-1ubuntu3
du -d 1 -h DATA/
vnstat -i eth0 -l
sudo apt install -y linux-tools-5.15.0-91-generic linux-cloud-tools-5.15.0-91-generic
watch -n 1 sudo cpupower monitor
# 内存
cat /proc/sys/vm/swappiness
sudo sysctl vm.swappiness=100
sudo gedit /etc/sysctl.conf
sync && sync && echo 1 > /proc/sys/vm/drop_caches && echo 2 > /proc/sys/vm/drop_caches && echo 3 > /proc/sys/vm/drop_caches && sync

7z a -t7z -v20g -mx=9 -m0=LZMA2 -mmt=32 MT8675_Hyper.7z MT8675_Hyper
7z x yocto.7z.001 -r -o./output
7z a -t7z -mx=0 -m0=Copy -mmt=32 /mnt/DATA/output-tbox-user.7z /mnt/DATA/mmio_home/mt8675/out/tbox/user/output_load_spm8675/
7z a -v20g -ttar -m0=Copy -mmt=32 yocto.tar yocto
tar -zcvf

# repo安装
mkdir -p ~/bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo

# thermal测试、定频
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
# mtk 公版编译 8675
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

mtk公版的adb Android需要使用alps/kernel-4.14/arch/arm64/configs/spm8675p1_64_mix_defconfig 的CONFIG_VIRTIO_CONSOLE=n 修改后打开

# suspend resume 流程
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

# 临时 8675 gfxbench测试

cd /mnt/hdo/MDesktop && adb root && adb remount && adb push stress /data && adb shell "chown 1000:1000 /data/stress" && adb install gfxbench_gl-4.0.0+corporate.armeabi-v7a.apk && adb shell
cd /mnt/hdo/MDesktop && adb root && adb remount && adb push stress /data && adb shell "chown 1000:1000 /data/stress" && adb install /mnt/hdo/mtktestimage/gfxbench_gl-4.0.0+corporate.armeabi-v7a.apk && adb shell


/data/stress --cpu 1

/mnt/hdo/android_tools/SP_Flash_Tool_v6.2228_Linux/SPFlashToolV6 -c format-download -f /mnt/hdo/78image/auto8678p1_64_hyp_gpu/flash.xml
cibot  密码 cibotpw


# 分批push
git log -1 --skip=990000
git push grt-mt8678 019132ff3daf36c97a4006655dfd00ee42f2b590:refs/heads/master > /mnt/sst/test/yocto/log.log 2>&1
repo init -u "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b release-spm.mt8678_2024_0524 -m alps.xml && repo sync -j2048
repo init -u "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b release-spm.mt8678_2024_0524 -m yocto.xml && repo sync -j2048
repo init -u <URL to Manifest repository> --reference=/path/to/local-mirror

# 78 android 解压
tar zxf ALPS-DEV-U0.MP1-LIBER.AUTO-OF.P52.PRE.1_AUTO8678P1_64_BSP_WIFI_KERNEL.tar.gz -C /mnt/sso/temp
cat ALPS-DEV-U0.MP1-LIBER.AUTO-OF.P52.PRE.1_AUTO8678P1_64_BSP_WIFI_INHOUSE.tar.gz* | tar zxf - -C /mnt/sso/temp

git remote add origin ssh://gaoyx@www.goldenriver.com.cn:29420/yocto/src/hypervisor/grt
git checkout -b release-spm.mt8678_2024_0524
git branch -avv 
git push -u --force origin master:refs/heads/master --verbose
git push -u --force origin release-spm.mt8678_2024_0524:refs/heads/release-spm.mt8678_2024_0524 --verbose

rm -f .git/hooks
# 压缩tar.7z
tar -cf - yocto | 7z a -si -v1g -mmt=32 /mnt/hdo/78image/goldriver-code-base/yocto.7z
7z x /mnt/hdo/78image/goldriver-code-base/yocto.7z.001 -so | tar -xvf - -C /mnt/sst/
7z x -so yocto-release-spm.mt8678_2024_05_23_19.tar.7z | tar xf -
tar cf - test/ | 7z a -si test.tar.7z -mmt=32
7z x test.tar.7z -so | tar xf - -C destination_folder

sudo e4defrag /path/to/directory  # 对特定目录进行碎片整理
sudo e4defrag /dev/sdXY  # 对整个分区进行碎片整理