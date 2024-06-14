cd ~/grt/thyp-sdk && git clean -ffd && cd ~/grpower/workspace && rm -rf buildroot-pvt8675/ nebula-ree/ && cd ~/grpower/workspace/nebula && rm -rf out && cd ~/grpower/ && source scripts/genv.sh && cd ~/grpower/ && gr-nebula.py build && gr-nebula.py export-buildroot && gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images 
cd ~/grt/thyp-sdk && git clean -ffd && ./build_all.sh
scp products/mt8678-mix/out/gz.img Administrator@192.168.50.50:D:/78images
# 下载源码
git clone "ssh://gaoyx@gerrit.grt.sy:29418/grpower"
cd ~/grpower/
source scripts/env.sh
gr-nebula.py update-source --branch-name main

# 执行这个编译nebula:
# http://gerrit.grt.sy/c/zircon/+/9706
cd ~/grpower/workspace/nebula/zircon
git fetch ssh://gaoyx@gerrit.grt.sy:29418/zircon refs/changes/06/9706/9 && git cherry-pick FETCH_HEAD

# for mtk 
cd ~/grpower/workspace/nebula/zircon
git fetch ssh://gaoyx@gerrit.grt.sy:29418/zircon refs/changes/60/10060/5 && git cherry-pick FETCH_HEAD

cd ~/grpower/
gr-nebula.py build

gr-android.py set-product --product-name pvt8675
gr-nebula.py export-buildroot
gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images
exit

git tag release-spm.mt8678_2024_0525
git push origin release-spm.mt8678_2024_0525
git push origin HEAD:refs/for/main

cd ~/grt/thyp-sdk
git clean -ffd 
./build_all.sh

cd /home/nebula/grt/thyp-sdk
cp -f products/mt8678-mix/out/gz.img ../../yocto/prebuilt/bsp/collect-bins/mt8678/auto8678p1_64_kde_hyp/
cp -f vmm/out/nbl_vmm ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/nbl_vm_ctl ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/nbl_vm_srv ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/libvmm.so ../../yocto/prebuilt/hypervisor/grt/
cp -f products/mt8678-mix/guest-configs/uos_alps_pv8678.json ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vm_srv/data/vm_srv_cfg_8678.pb.txt ../../yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vmm/data/uos_mtk8678/uos_bootloader_lk2.pb.txt ../../yocto/prebuilt/hypervisor/grt/

git push grt-mt8678 HEAD:refs/for/main%topic=nebulalog_AEE_dump
git push grt-mt8678 HEAD:refs/for/main

repo forall -c "git tag release-spm.mt8678_2024_0525"
repo forall -c "git push grt-mt8678 release-spm.mt8678_2024_0525"

grep -r -n -w .patch --include=".gitignore"