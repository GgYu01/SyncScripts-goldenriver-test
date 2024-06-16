
请在回答我文字内容时使用简体中文，使用专业的英文编写代码中的内容，包括注释、和说明以及描述。
我需要一个专业、复杂且高度模块化的 Python3.12 脚本，用于在 Ubuntu 24 上远程编译代码。远程服务器的 SSH 信息如下：IP 为 192.168.50.45，端口号 8021，密码为 nebula。

**任务要求：**

1. **SSH 密钥验证：**
   - 检查远端服务器是否已有本地公钥，如果没有则上传。
   - 自动信任远端服务器的主机密钥。

2. **代码仓库：**
   - **alps** 路径：`/home/nebula/alps`
   - **yocto** 路径：`/home/nebula/yocto`

3. **编译命令：**
   - **alps** 仓库：在路径 `/home/nebula/alps` 下异步并发执行以下命令，并将输出分别保存到 `sys.log`、`hal.log`、`krn.log` 和 `vext.log` 中。如果所有命令成功，则执行最后一个命令并将输出保存到 `out.log` 中。
     ```shell
     source build/envsetup.sh && export OUT_DIR=out_sys && lunch sys_mssi_auto_64_cn_armv82-userdebug && make sys_images
     source build/envsetup.sh && export OUT_DIR=out_hal && lunch hal_mgvi_auto_64_armv82_wifi_vm-userdebug && make hal_images
     source build/envsetup.sh && export OUT_DIR=out_krn && lunch krn_mgk_64_k61_auto_vm-userdebug && make krn_images
     source build/envsetup.sh && export OUT_DIR=out && lunch vext_auto8678p1_64_bsp_vm-userdebug && make vext_images
     python out_sys/target/product/mssi_auto_64_cn_armv82/images/split_build.py --system-dir out_sys/target/product/mssi_auto_64_cn_armv82/images --vendor-dir out_hal/target/product/mgvi_auto_64_armv82_wifi_vm/images --kernel-dir out_krn/target/product/mgk_64_k61_auto_vm/images --vext-dir out/target/product/auto8678p1_64_bsp_vm/images --output-dir out/target/product/auto8678p1_64_bsp_vm/merged
     ```
   - **yocto** 仓库：在路径 `/home/nebula/yocto` 下顺序执行以下命令，并将输出保存到相应日志文件中。命令之间可能有依赖关系，甚至可能影响后续命令执行路径，请考虑合并命令。
     ```shell
     export BB_NO_NETWORK="1"
     TEMPLATECONF=${PWD}/meta/meta-mediatek-mt8678/conf/base/auto8678p1_64_kde_hyp
     source meta/poky/oe-init-build-env
     bitbake mtk-core-image-auto8678-kde-hyp
     ```

4. **代码结构：**
   - 模块化设计，定义全局变量和数据结构用于路径、仓库名、编译命令、日志输出等。
   - 使用多个变量拼接形成最终参数，保证参数和代码功能模块化。
   - 动态输出每个编译命令的最后 3-10 行信息至终端，行数作为参数定义。
   - 捕获所有编译命令的输出信息，分别保存到独立的日志文件，并记录整体编译时间。

5. **代码要求：**
   - 排版工整、逻辑清晰，使用英文专业的描述函数方法的作用、参数、返回值及对代码添加专业的注释。
   - 在方法定义中使用 `->` 补充说明返回值。
   - 使用装饰器和定义多个类模块化优化代码结构，确保逻辑清晰严谨。
   - 加入详细的执行过程判断，输出脚本执行步骤状态。
   - 使用 Urwid、rich、Asciimatics 优化界面输出及错误追踪。
   - 编写高级、结构复杂的测试代码，优先使用高级的 Python 特性和第三方库。
   - 尽量使用 Python 实现功能，避免使用 Bash。

**库选择：**
请考虑使用 `asyncssh` 或 `fabric` 库。

请根据以上描述编写脚本，并确保其符合高度专业化和模块化的要求。