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

# android reboot --> shurui 
# MTBF grt_be debug
# grt be patch
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


MT8678 2024/09/12测试情况
0904基线：
add product ID  owner：李志健 James 测试通过，已合入
CVE             owner：陶杰 正在验证
CPU性能优化     owner：陈平平
fix: hw interrupt inject issue  owner：李加春 测试通过，已合入
fix coverity report  owner：武阳 测试通过，已合入
0904 8+8 版本 reboot 8次Android reboot系统重启
部分情况下Android reboot5次后 ，UOS持续重启，yocto正常。Android启动后ADB无法连接

0726_patch（BYD0802）
无HWT改动情况下byd load 5次Android reboot系统重启

# 为了Secure boot 加入公钥平台id判断
# cpu freq
# DhryStone 优化
# 8676 wdt workaround
# 春阳 utrace

gr-nebula.py export-sdk -o /home/nebula/grt/nebula-sdk

git fetch ssh://gaoyx@gerrit.grt.sy:29418/zircon refs/changes/93/11293/5 && git cherry-pick FETCH_HEAD
cd7b3c16fa7e56db48c59797530efaa05cb65ea0
ec065a79fa90a25cbbc174bdcd2de10430223510