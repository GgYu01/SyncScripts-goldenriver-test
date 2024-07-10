#!/bin/bash
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/boot.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/dtbo.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/init_boot.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/super.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/userdata.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/vendor_boot.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/vbmeta.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/vbmeta_system.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp
cp ~/alps/out/target/product/auto8678p1_64_bsp_vm/merged/vbmeta_vendor.img ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp


rm -rf ~/78images
mkdir ~/78images
cp -Lr ~/yocto/build/tmp/deploy/images/auto8678p1_64_hyp ~/78images
scp -r ~/78images/auto8678p1_64_hyp/* Administrator@192.168.50.50:D:/78images/auto8678p1_64_hyp_gpu_0628_newmtk

