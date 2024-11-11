cd ~/grt/thyp-sdk && git clean -ffd && cd ~/grpower/workspace && rm -rf buildroot-pvt8675/ nebula-ree/ && cd ~/grpower/workspace/nebula && rm -rf out && cd ~/grpower/ && source scripts/genv.sh && cd ~/grpower/ && gr-nebula.py build && gr-nebula.py export-buildroot && gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images 
cd ~/grt/thyp-sdk && git clean -ffd && ./build_all.sh
scp ~/grt/thyp-sdk/products/mt8678-mix/out/gz.img ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/tee.img Administrator@100.64.0.1:D:/78images
export NO_PIPENV_SHELL=1 && cd ~/grpower/ && source scripts/env.sh && gr-nebula.py update-source --branch-name main
cd ~/grt && git reset --hard && git clean -fdx && git pull && \
cd ~/grt_be && git pull && \
cd ~/yocto && repo forall -c "git reset --hard && git clean -fd" > /dev/null 2>&1 && \
repo sync --no-repo-verify --force-sync --jobs 1 --force-checkout --force-remove-dirty --tags --retry-fetches=15 --prune --verbose   && \
cd ~/alps && repo forall -c "git reset --hard && git clean -fd " > /dev/null 2>&1 && \
repo sync --no-repo-verify --force-sync --jobs 1 --force-checkout --force-remove-dirty --tags --retry-fetches=15 --prune --verbose 
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

cd ~/grpower/workspace/nebula && rm snapshot.xml && source scripts/env.sh && jiri runp 'git tag release-spm.mt8678_mt8676_2024_0903' && jiri runp 'git push origin release-spm.mt8678_mt8676_2024_0903 ' && jiri snapshot snapshot.xml

git tag release-spm.mt8678_2024_0903
git push origin release-spm.mt8678_2024_0903
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

repo forall -c "git tag release-spm.mt8678_2024_0903"
repo forall -c "git push grt-mt8678 release-spm.mt8678_2024_0903"

grep -r -n -w .patch --include=".gitignore"

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

repo init -u "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b master -m mt8678/grt/1001/alps.xml && repo sync --force-sync --jobs 30 --jobs-network=30 --jobs-checkout=32 --force-checkout --force-remove-dirty --tags --retry-fetches=15 --prune --verbose --no-repo-verify
repo init -u "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b master -m mt8678/grt/1001/yocto.xml && repo sync --force-sync --jobs 30 --jobs-network=30 --jobs-checkout=32 --force-checkout --force-remove-dirty --tags --retry-fetches=15 --prune --verbose --no-repo-verify
git clone "ssh://gaoyx@www.goldenriver.com.cn:29420/yocto/src/hypervisor/grt" --depth 2 -j 60 --single-branch --branch release-spm.mt8678_2024_1001
jiri update -j=8 --attempts=10 --force-autoupdate=true --rebase-all=false --rebase-tracked=false --rebase-untracked=false --show-progress=true --color=auto -autoupdate=false -vv=true 
--repo-url=https://gerrit-googlesource.proxy.ustclug.org/git-repo 

https://syofficenas01.cn1.quickconnect.cn/oo/r/z96z2COzgLupO37auxXknALNaVUIrxKZ

# 筛选 ：status:merged branch:nebula (project:garnet OR project:zircon)

git rebase --onto origin/nebula a0d9d81cc^ 6fcb672db


sudo docker save goldenriver/thyp-sdk:focal-0.4 -o thyp-sdk-focal-0.4.tar
sudo ctr -n=k8s.io images import thyp-sdk-focal-0.4.tar
sudo ctr -n=k8s.io images ls

python3 -m pip install --upgrade --force-reinstall pip setuptools wheel
python3 -m pip install --upgrade pip setuptools wheel 


rm -rf /home/nebula/alps/vendor/mediatek/proprietary/scripts/sign-image_v2/out/*
cp ~/grt/thyp-sdk/products/mt8678-mix/out/gz.img /home/nebula/alps/vendor/mediatek/proprietary/scripts/sign-image_v2/out

cd ~/alps
python vendor/mediatek/proprietary/scripts/sign-image_v2/sign_flow.py mt6991 auto8678p1_64_bsp

cd ~/alps/vendor/mediatek/proprietary/scripts/sign-image_v2/out/resign/bin/multi_tmp

# 切换到 Nebula 源码目录
mkdir -p ~/grpower/workspace/nebula
cd ~/grpower/workspace/nebula
mkdir -p ~/grpower/workspace/nebula/.jiri_root/bin


# 删除一些旧的配置文件
rm -f .jiri_manifest .config .prebuilts_config

# 执行 jiri 命令以从 gerrit 仓库中获取最新的 manifest 文件，并更新到指定的分支
~/grpower/bin/jiri -j=2 import -remote-branch="master" "cci/nebula-main" ssh://gerrit:29418/manifest

# 使用 jiri 执行代码检出并强制覆盖
~/grpower/bin/jiri -j=8 runp git checkout -f JIRI_HEAD --detach 

# 更新代码仓库
~/grpower/bin/jiri -j=2 update -gc -autoupdate=false -run-hooks=false --attempts=10 --force-autoupdate=true --rebase-all=false --rebase-tracked=false --rebase-untracked=false --show-progress=true --color=auto  

# 如果需要清理未提交的本地更改，可以执行以下命令
~/grpower/bin/jiri -j=8 runp git clean -f -d -x
~/grpower/bin/jiri -j=8 runp "git tag -l | xargs git tag -d && git fetch -t"

# 再次执行更新命令
~/grpower/bin/jiri -j=8 update -gc -autoupdate=false -hook-timeout=30

# 设置 git 的推送 URL
~/grpower/bin/jiri -j=8 runp "git remote get-url origin | sed 's/gerrit/gerrit-review/' | xargs git remote set-url --push origin"