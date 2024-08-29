# SyncScripts-goldenriver-test

https://syofficenas01.cn5.quickconnect.cn/oo/r/z96z2COzgLupO37auxXknALNaVUIrxKZ#tid=1

8678 0726 版 hyp build cmd 如下
1. Yocto build cmd
TEMPLATECONF=${PWD}/meta/meta-mediatek-mt8678/conf/templates/auto8678p1_64_hyp source meta/poky/oe-init-build-env
bitbake -k mtk-core-image-auto8678-hyp
# image out: build/tmp/deploy/images/auto8678p1_64_hyp/
2. Android build cmd
python vendor/mediatek/proprietary/scripts/releasetools/split_build_helper.py --run full_auto8678p1_64_bsp_vm-userdebug --target -j24
# image out: out/target/product/auto8678p1_64_bsp_vm/merged/
3. 基于 yocto build out image 烧录, 烧录前需要copy 如下 11个 android image 至 yocto
boot.img
dtbo.img
init_boot.img
super.img
userdata.img
vendor_boot.img
vbmeta.img
vbmeta_system.img
vbmeta_vendor.img
scp.img	(新增)
tee.img	(新增)

repo init "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b master -m mt8678/grt/0726/alps.xml
repo init "ssh://gaoyx@www.goldenriver.com.cn:29420/manifest" -b master -m mt8678/grt/0726/yocto.xml 

# CVE
git fetch ssh://gaoyx@www.goldenriver.com.cn:29420/yocto/src/hypervisor/grt refs/changes/60/460/2 && git cherry-pick FETCH_HEAD

# 吴杰
git fetch ssh://gaoyx@gerrit.grt.sy:29418/zircon refs/changes/40/11040/1 && git cherry-pick FETCH_HEAD
git fetch ssh://gaoyx@gerrit.grt.sy:29418/zircon refs/changes/41/11041/1 && git cherry-pick FETCH_HEAD
git fetch ssh://gaoyx@www.goldenriver.com.cn:29420/yocto/src/kernel/modules/mt8678/virt/grt refs/changes/16/616/1 && git cherry-pick FETCH_HEAD
git fetch ssh://gaoyx@www.goldenriver.com.cn:29420/alps/vendor/mediatek/kernel_modules/virt refs/changes/15/615/1 && git cherry-pick FETCH_HEAD


# docker 4 : liujian
# docker 6 : shengjp wangzhimian
network:
  version: 2
  ethernets:
    enp6s0:
      dhcp4: true
      dhcp6: true
      routes:
        - to: default
          via: 192.168.50.20    # 手动指定IPv4网关
      nameservers:
        addresses:
          - 192.168.50.20       # 手动指定DNS服务器

http://192.168.170.7:5000/oo/r/zOhdvZdCKBvh2nMQGhzgg84EONhvPukR#heading_id=G3RtEZygMN