cd ~/grt/thyp-sdk && git clean -ffd && cd ~/grpower/workspace && rm -rf buildroot-pvt8675/ nebula-ree/ && cd ~/grpower/workspace/nebula && rm -rf out && cd ~/grpower/ && source scripts/genv.sh && cd ~/grpower/ && gr-nebula.py build && gr-nebula.py export-buildroot && gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images 
cd ~/grt/thyp-sdk && git clean -ffd && ./build_all.sh
scp products/mt8678-mix/out/gz.img Administrator@100.64.0.3:D:/78images
cd ~/grpower/ && source scripts/genv.sh && gr-nebula.py update-source --branch-name main
cd ~/grt && git pull && cd ~/grt_be && git pull && cd ~/yocto && repo sync --force-sync --force-broken -j256 && cd ~/alps && repo sync --force-sync --force-broken -j256
# 下载源码
git clone "ssh://gaoyx@gerrit.grt.sy:29418/grpower"
cd ~/grpower/
source scripts/env.sh
gr-nebula.py update-source --branch-name main

# 执行这个编译nebula:
cd ~/grpower/
gr-nebula.py build

gr-android.py set-product --product-name pvt8675
gr-nebula.py export-buildroot
gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images
exit

cd ~/grpower/workspace/nebula && rm snapshot.xml && source scripts/env.sh && jiri runp 'git tag release-spm.mt8678_mt8676_2024_0814' && jiri runp 'git push origin release-spm.mt8678_mt8676_2024_0814 ' && jiri snapshot snapshot.xml

git tag release-spm.mt8678_2024_0814
git push origin release-spm.mt8678_2024_0814
git push origin :refs/tags/<tagname>
git push origin HEAD:refs/for/release-spm.mt8678_2024_0726

cd ~/grt/thyp-sdk
git clean -ffd 
./build_all.sh

cd ~/grt_be/workspace
git clean -ffd 
./build.sh

cd /home/nebula/grt/thyp-sdk
cp -f products/mt8678-mix/out/gz.img ../../yocto/prebuilt/bsp/collect-bins/mt6991/auto8678p1_64_hyp/
cp -f vmm/out/nbl_vmm ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/nbl_vm_ctl ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/nbl_vm_srv ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/libvmm.so ../../yocto/prebuilt/hypervisor/grt/
cp -f ./third_party/prebuilts/libluajit/lib64/libluajit.so ../../yocto/prebuilt/hypervisor/grt/
cp -f products/mt8678-mix/guest-configs/uos_alps_pv8678.json ../../yocto/prebuilt/hypervisor/grt/
cp -f ./products/mt8678-mix/guest-configs/uos_alps_pv8678.lua ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vm_srv/data/vm_srv_cfg_8678.pb.txt ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vmm/data/uos_mtk8678/uos_bootloader_lk2.pb.txt ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vmm/data/vm_audio_cfg.pb.txt ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vmm/data/vm_audio_shared_irq.pb.txt ../../yocto/prebuilt/hypervisor/grt/

cp -f ../../grt_be/workspace/out/gpu_server ../../yocto/prebuilt/hypervisor/grt/
cp -f ../../grt_be/workspace/out/video_server ../../yocto/prebuilt/hypervisor/grt/


git push grt-mt8678 HEAD:refs/for/release-spm.mt8678_2024_0726%topic=lua_dynamic_dram_size
git push grt-mt8678 HEAD:refs/for/main

repo forall -c "git tag release-spm.mt8678_2024_0814"
repo forall -c "git push grt-mt8678 release-spm.mt8678_2024_0814"

grep -r -n -w .patch --include=".gitignore"

adb -s YOCTO push nbl_vmm /usr/bin/
adb -s YOCTO push nbl_vm_ctl /usr/bin/
adb -s YOCTO push nbl_vm_srv /usr/bin/
adb -s YOCTO push libvmm.so /usr/lib64/
adb -s YOCTO push uos_alps_pv8678.json /vendor/etc/hyper_android/
adb -s YOCTO shell 'chmod 777 /usr/bin/nbl_vmm'
adb -s YOCTO shell 'chmod 777 /usr/bin/nbl_vm_ctl'
adb -s YOCTO shell 'chmod 777 /usr/bin/nbl_vm_srv'
adb -s YOCTO shell 'chmod 777 /usr/lib64/libvmm.so'
adb -s YOCTO shell 'chmod 777 /vendor/etc/hyper_android/uos_alps_pv8678.json'
adb -s YOCTO push gpu_server /usr/bin/
adb -s YOCTO push video_server /usr/bin/
adb -s YOCTO shell 'chmod 777 /usr/bin/gpu_server'
adb -s YOCTO shell 'chmod 777 /usr/bin/video_server'
chmod 777 /usr/bin/nbl_vmm
chmod 777 /usr/bin/nbl_vm_ctl
chmod 777 /usr/bin/nbl_vm_srv
chmod 777 /usr/lib64/libvmm.so
chmod 777 /vendor/etc/hyper_android/uos_alps_pv8678.json
chmod 777 /usr/bin/gpu_server
chmod 777 /usr/bin/video_server
# 创建目录
sudo mkdir -p /etc/docker
# 写入镜像配置
在 /etc/docker/daemon.json 文件中输入
{
    "registry-mirrors": [
        "https://docker.m.daocloud.io",
        "https://dockerproxy.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://docker.nju.edu.cn"
    ]
}

# 重启docker服务
sudo systemctl daemon-reload
sudo systemctl restart docker

repo init "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b master -m mt8678/grt/0726/alps.xml && repo sync --force-sync --force-broken -j256 
repo init "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b master -m mt8678/grt/0726/yocto.xml && repo sync --force-sync --force-broken -j256 

https://syofficenas01.cn1.quickconnect.cn/oo/r/z96z2COzgLupO37auxXknALNaVUIrxKZ

# 筛选 ：status:merged branch:nebula (project:garnet OR project:zircon)

scp gpu_server libvmm.so nbl_vm_ctl nbl_vm_srv nbl_vmm uos_alps_pv8678.json video_server Administrator@100.64.0.3:D:/78images/auto8678p1_64_hyp_gpu_0802_allpatch