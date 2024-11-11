
# 开发需求文档

## 项目概述

本项目旨在开发一个专业、高度模块化且复杂的Python 3.8.10脚本，用于自动化管理多个源码仓库的标签（tag）创建、编译、导出、提交二进制文件及其他相关操作。脚本将涵盖 `grpower`、`nebula`、`grt`、`yocto`、`alps`、`tee` 及 `nebula-sdk` 等源码部分，确保开发人员能够统一、规范地进行版本管理和发布流程。

## 目标

- **自动化标签管理**：实现自动化的标签创建与推送，确保各仓库版本的一致性。
- **灵活的编译流程**：根据不同仓库的特性，执行相应的编译和导出操作。
- **参数化配置**：提供灵活的参数配置，支持不同的发布需求。
- **高可维护性**：确保脚本具备高度的模块化和可维护性，方便后续扩展和修改。
- **专业注释**：提供详尽的英文注释，提升代码的可读性和专业性。

## 功能需求

1. **标签管理**
   - 支持为 `grpower`、`nebula`、`grt`、`yocto`、`alps` 等仓库创建和推送标签。
   - 标签名称格式：
     - `grpower`、`grt`、`yocto`、`alps` 示例：`release-spm.mt8678_2024_1023_03`
     - `nebula` 示例：`release-spm.mt8678_mt8676_2024_1023_03`
   - 标签中的日期部分（如 `2024_1023_03`）应为可调参数。

2. **源码更新**
   - 支持更新 `nebula`、`grt`、`yocto`、`alps` 等源码的分支，分支名称应为可定义参数。
   - 示例命令：
     ```bash
     export NO_PIPENV_SHELL=1 && cd ~/grpower/ && source scripts/env.sh && gr-nebula.py update-source --branch-name main
     cd ~/grpower/workspace/nebula/zircon 
     git checkout -f release-spm.mt8678_mtk
     git pull
     cd ~/grpower/workspace/nebula/garnet 
     git checkout -f release-spm.mt8678_mtk
     git pull
     cd ~/grpower
     git pull
     ```

3. **编译与导出**
   - 根据涉及的源码部分（如 `nebula`、`nebula-sdk`、`TEE`），执行相应的编译、导出操作。
   - 编译命令需根据不同源码的要求进行调整，编译方法应作为可定义参数。
   - 支持二进制文件的拷贝和提交到远端仓库。

4. **仓库同步与推送**
   - 支持定义需要参与本次发布的仓库列表作为参数。
   - 执行仓库的同步操作，默认尝试最大次数为五次，若五次均失败则退出。
   - 支持对 `yocto`、`alps` 等使用 `repo` 工具进行批量操作。

5. **用户交互**
   - 在推送到远端仓库后，等待用户确认远端已合并，才能继续执行后续步骤。
   - 提供交互式提示，确保用户知晓当前操作状态。


## 详细执行步骤

### 第一步：为 `nebula` 部分打标签

1. **进入 `nebula` 工作目录并清理旧快照文件**
   ```bash
   cd ~/grpower/workspace/nebula
   rm snapshot.xml
   ```
2. **加载环境变量并创建标签**
   ```bash
   source scripts/env.sh
   jiri runp -j=1 'git tag release-spm.mt8678_mt8676_${TAG_DATE}'
   ```
3. **推送标签到远端仓库**
   ```bash
   jiri runp 'git push origin release-spm.mt8678_mt8676_${TAG_DATE}'
   ```
4. **创建快照**
   ```bash
   jiri snapshot snapshot.xml
   ```

### 第二步：根据涉及的源码部分执行编译、导出和提交操作

#### 2.1 如果涉及 `nebula`、`nebula-sdk`、`TEE` 则执行以下步骤：

1. **编译 `nebula`**
   - **切换分支并确保仓库干净**
     ```bash
     cd ~/grt
     git checkout -f release-spm.mt8678_2024_1001
     git clean -fdx
     git reset --hard
     cd ~/yocto/prebuilt/hypervisor/grt
     git clean -fdx
     ```
   - **删除旧编译产物并开始编译**
     ```bash
     export NO_PIPENV_SHELL=1
     cd ~/grpower/workspace
     rm -rf buildroot-pvt8675/ nebula-ree/ buildroot-pvt8675_tee/
     cd ~/grpower/workspace/nebula
     rm -rf out
     cd ~/grpower/
     source scripts/env.sh
     gr-nebula.py build > ~/grt/hee.log 2>&1
     gr-nebula.py export-buildroot >> ~/grt/hee.log 2>&1
     gr-android.py set-product --product-name pvt8675 >> ~/grt/hee.log 2>&1
     gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images >> ~/grt/hee.log 2>&1
     cd ~/grt/thyp-sdk
     ./configure.sh /home/nebula/grt/nebula-sdk/ > /dev/null
     ./build_all.sh > ~/grt/sdk.log 2>&1
     ```
   - **拷贝编译生成的文件**
     ```bash
     cd /home/nebula/grt/thyp-sdk
     cp -fv products/mt8678-mix/out/gz.img ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/out/nbl_vmm ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/out/nbl_vm_ctl ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/out/nbl_vm_srv ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/out/libvmm.so ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/out/symbols/*  ../../yocto/prebuilt/hypervisor/grt/symbols/
     cp -fv ./third_party/prebuilts/libluajit/lib64/libluajit.so ../../yocto/prebuilt/hypervisor/grt/
     cp -fv ./products/mt8678-mix/guest-configs/uos_alps_pv8678.lua ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/nbl_vm_srv/data/vm_srv_cfg_8678.pb.txt ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/nbl_vmm/data/uos_mtk8678/uos_bootloader_lk2.pb.txt ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/nbl_vmm/data/vm_audio_cfg.pb.txt ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/nbl_vmm/data/vm_audio_shared_irq.pb.txt ../../yocto/prebuilt/hypervisor/grt/
     cp -fv vmm/nbl_vm_srv/data/nbl_ta_monitor ../../yocto/prebuilt/hypervisor/grt/
     ```

2. **提交修改到远端仓库**
   - **提交到 `thyp-sdk` 仓库**
     ```bash
     cd ~/grt
     git add ~/grt/thyp-sdk/products/mt8678-mix/prebuilt-images
     git commit -m "Update nebula prebuilt binary.

     [Description]
     ${DESCRIPTION}

     [Test]
     Build pass and test ok."
     git push origin HEAD:refs/for/release-spm.mt8678_2024_1001
     ```
   - **提交到 `grt` 仓库**
     ```bash
     cd ~/yocto/prebuilt/hypervisor/grt
     git add .
     git commit -m "Update nebula prebuilt binary.

     [Description]
     1. ${DESCRIPTION}

     [Test]
     Build pass and test ok."
     git push grt-mt8678 HEAD:refs/for/release-spm.mt8678_2024_1001
     ```

#### 2.2 如果涉及 `TEE` 改动：

1. **编译 `TEE`**
   - **删除旧编译产物并编译**
     ```bash
     export NO_PIPENV_SHELL=1
     cd ~/grpower/workspace
     rm -rf buildroot-pvt8675/ nebula-ree/ buildroot-pvt8675_tee/
     cd ~/grpower/workspace/nebula
     rm -rf out
     cd ~/grpower/
     source scripts/env.sh
     gr-nebula.py build > ~/grt/tee.log 2>&1
     gr-nebula.py export-buildroot >> ~/grt/tee.log 2>&1
     gr-android.py set-product --product-name pvt8675_tee >> ~/grt/tee.log 2>&1
     mkdir -p ~/grt/teetemp
     gr-android.py buildroot export_nebula_images -o ~/grt/teetemp >> ~/grt/tee.log 2>&1
     cp -v ~/grt/teetemp/nebula*.bin ~/alps/vendor/mediatek/proprietary/trustzone/grt/source/common/kernel/
     ```
2. **提交修改到 `TEE` 仓库**
   ```bash
   cd ~/alps/vendor/mediatek/proprietary/trustzone/grt
   git add .
   git commit -m "Update nebula prebuilt binary.

   [Description]
   1. ${DESCRIPTION}

   [Test]
   Build pass and test ok."
   git push grt-mt8678 HEAD:refs/for/release-spm.mt8678_2024_1001
   ```

#### 2.3 编译 `nebula-sdk`

1. **编译 `nebula-sdk`**
   ```bash
   export NO_PIPENV_SHELL=1
   cd ~/grpower/workspace
   rm -rf buildroot-pvt8675/ nebula-ree/ buildroot-pvt8675_tee/
   cd ~/grpower/workspace/nebula
   rm -rf out
   cd ~/grpower/
   source scripts/env.sh
   gr-nebula.py build > ~/grt/hee.log 2>&1
   gr-nebula.py export-buildroot >> ~/grt/hee.log 2>&1
   gr-android.py set-product --product-name pvt8675 >> ~/grt/hee.log 2>&1
   gr-nebula.py export-sdk -o /home/nebula/grt/nebula-sdk
   ```
2. **提交 `nebula-sdk` 到远端仓库**
   ```bash
   cd ~/grt/nebula-sdk
   git add android cmake docs examples hee host make ree test_suite
   git commit -m "Update nebula-sdk.

   [Description]
   1. ${DESCRIPTION}

   [Test]
   Build pass and test ok."
   ```

### 第三步：最终标签创建与推送

1. **确保第一步和第二步均完成且成功后，执行其他仓库打标签流程**
   - **打标签并推送 `grpower` 仓库**
     ```bash
     cd ~/grpower
     git pull
     git tag release-spm.mt8678_${TAG_DATE}
     git push origin release-spm.mt8678_${TAG_DATE}
     ```
   - **打标签并推送 `grt` 仓库**
     ```bash
     cd ~/grt
     git pull
     git tag release-spm.mt8678_${TAG_DATE}
     git push origin release-spm.mt8678_${TAG_DATE}
     ```
   - **同步并打标签 `yocto` 仓库**
     ```bash
     cd ~/yocto
     repo sync --no-repo-verify --force-sync --jobs 1 --force-checkout --force-remove-dirty --tags --retry-fetches=5 --prune --verbose
     repo forall -c "git tag release-spm.mt8678_${TAG_DATE}"
     repo forall -c "git push grt-mt8678 release-spm.mt8678_${TAG_DATE}"
     ```
   - **同步并打标签 `alps` 仓库**
     ```bash
     cd ~/alps
     repo sync --no-repo-verify --force-sync --jobs 1 --force-checkout --force-remove-dirty --tags --retry-fetches=5 --prune --verbose
     repo forall -c "git tag release-spm.mt8678_${TAG_DATE}"
     repo forall -c "git push grt-mt8678 release-spm.mt8678_${TAG_DATE}"
     ```

## 参数配置

- **标签日期部分**
  - 格式：`YYYY_MMDD_NN`，如 `2024_1023_03`
  - 可通过命令行参数或配置文件进行定义。
  - 示例：
    ```bash
    TAG_DATE="2024_1023_03"
    ```

- **涉及仓库列表**
  - 支持定义本次发布涉及的仓库，可通过参数传递。
  - 示例：
    ```bash
    REPOS=("grpower" "nebula" "grt" "yocto" "alps" "tee" "nebula-sdk")
    ```

- **分支名称**
  - `grt`、`yocto`、`alps` 的分支名称应为可定义参数。
  - 示例：
    ```bash
    GRT_BRANCH="release-spm.mt8678_2024_1001"
    YOCTO_BRANCH="release-spm.mt8678_2024_1001"
    ALPS_BRANCH="release-spm.mt8678_2024_1001"
    ```

- **编译方法**
  - `nebula`、`tee`、`nebula-sdk` 的编译方法应为可定义参数，可通过配置文件或命令行参数传递。
  - 示例：
    ```bash
    NEBULA_BUILD_CMD="gr-nebula.py build > ~/grt/hee.log 2>&1 && gr-nebula.py export-buildroot >> ~/grt/hee.log 2>&1"
    TEE_BUILD_CMD="gr-nebula.py build > ~/grt/tee.log 2>&1 && gr-nebula.py export-buildroot >> ~/grt/tee.log 2>&1"
    NEBULA_SDK_BUILD_CMD="gr-nebula.py build > ~/grt/hee.log 2>&1 && gr-nebula.py export-buildroot >> ~/grt/hee.log 2>&1 && gr-android.py set-product --product-name pvt8675 >> ~/grt/hee.log 2>&1 && gr-nebula.py export-sdk -o /home/nebula/grt/nebula-sdk"
    ```

## 用户交互

- **用户确认**
  - 在关键步骤（如推送到远端仓库后）提示用户确认远端已合并，方可继续执行后续操作。
  - 示例提示：
    ```bash
    read -p "请确认远端仓库已合并标签，按任意键继续..."
    ```

- **操作状态提示**
  - 提供友好的提示信息，指导用户完成确认操作。
  - 示例：
    ```bash
    echo "正在为 nebula 部分打标签..."
    ```

## 版本控制和标签

- **标签管理**
  - 脚本应支持对 `grpower`、`grt`、`yocto`、`alps`、`nebula` 等仓库进行标签管理。
  - 标签推送到远端仓库，确保版本的一致性和可追溯性，无论哪个仓库更新，所有仓库必须全部打tag，而不是只给部分仓库打标签。
  - 最终完成所有操作后，对其他仓库（如 `grpower`、`grt`、`yocto`、`alps`）进行统一标签的创建和推送。

## 其他仓库管理

- **`yocto` 和 `alps` 仓库**
  - 使用 `repo` 工具进行批量操作，包括同步、标签创建和推送。
  - 默认尝试同步五次，若失败则退出脚本。
  - 示例命令：
    ```bash
    repo sync --no-repo-verify --force-sync --jobs 1 --force-checkout --force-remove-dirty --tags --retry-fetches=5 --prune --verbose
    repo forall -c "git tag release-spm.mt8678_${TAG_DATE}"
    repo forall -c "git push grt-mt8678 release-spm.mt8678_${TAG_DATE}"
    ```

## 执行顺序和依赖

1. **第一步：为 `nebula` 部分打标签**
   - 执行 `cd ~/grpower/workspace/nebula` 及相关命令。

2. **第二步：根据涉及的源码部分执行编译、导出和提交操作**
   - 若涉及 `nebula`、`nebula-sdk`、`TEE`，则执行相应的编译和提交步骤。
   - 推送后等待用户确认远端合并。

3. **第三步：最终标签创建与推送**
   - 执行 `grpower`、`grt`、`yocto`、`alps` 等仓库的标签创建和推送。


## 附录

### 示例标签名称

- `grpower`、`grt`、`yocto`、`alps`：`release-spm.mt8678_2024_1023_03`
- `nebula`：`release-spm.mt8678_mt8676_2024_1023_03`

### 编译命令示例

```bash
# 示例：为 nebula 部分打标签
cd ~/grpower/workspace/nebula && \
rm snapshot.xml && \
source scripts/env.sh && \
jiri runp -j=1 'git tag release-spm.mt8678_mt8676_${TAG_DATE}' && \
jiri runp 'git push origin release-spm.mt8678_mt8676_${TAG_DATE}' && \
jiri snapshot snapshot.xml
```



### **Python 代码设计与规范**

#### 1. **模块化设计**

- **全局变量与数据结构**：
  - 在代码的开头统一定义所有全局变量和数据结构，包括文件路径、仓库名称、编译命令、日志配置等。
  - 使用数据类（`dataclass`）来组织和管理相关配置，确保配置的统一性和便于修改。例如，所有需要用户提供的变量参数应作为数据结构的一部分集中定义，避免散布在代码的各个部分。

- **类的使用**：
  - 使用类（`class`）来封装相关的功能模块，确保代码结构清晰，职责单一，便于维护和扩展。
  - 每个类应负责特定的功能，如构建管理、日志处理、命令执行等，避免功能混杂，提升代码的内聚性。

- **装饰器的应用**：
  - 利用装饰器（`decorator`）优化代码逻辑，减少重复性任务，如日志记录、时间测量等。
  - 装饰器应简洁明了，具备良好的可复用性，提升代码的可读性和维护性。

- **日志管理**：
  - 所有编译命令的输出信息需要分别保存到独立的日志文件中，便于追踪和分析。
  - 日志记录应包括每个模块的执行时间和整体编译时间，确保对编译过程有全面的了解和监控。

#### 2. **代码整洁与规范**

- **代码排版**：
  - 保持代码排版整洁，采用一致的缩进方式（推荐使用4个空格），合理分隔代码块，确保逻辑清晰。
  - 每行代码的长度应适中，避免过长，提升代码的可读性。

- **专业英文注释**：
  - 为每个函数或方法添加详细的英文注释，说明其作用、参数、返回值以及关键逻辑。
  - 使用类型提示（Type Hint）明确参数和返回值的类型，增强代码的可读性和静态分析能力。

- **命名规范**：
  - 变量、函数、类等命名应具备描述性，采用驼峰命名法或下划线命名法，保持一致性。
  - 避免使用过于简短或模糊的名称，确保命名能够准确反映其用途和意义。

#### 3. **错误处理与进度监控**

- **错误处理机制**：
  - 实现全面的错误处理，使用`try-except`块捕获可能的异常，提供明确的错误提示。
  - 确保脚本在异常情况下能够稳定运行，避免因未处理的异常导致程序崩溃。

- **进度监控**：
  - 动态输出脚本执行状态，使用如`rich`等库优化界面输出，展示进度条、已完成模块数量等信息。
  - 提供直观的进度反馈，提升用户体验，帮助用户了解当前执行的进度和剩余任务。

- **日志输出**：
  - 实现不同级别的日志输出（如INFO、DEBUG、WARNING、ERROR），帮助开发者和用户快速定位问题。
  - 日志应包含时间戳、模块名称、日志级别和详细信息，确保日志的全面性和可追溯性。

#### 4. **减少代码重复**

- **高级架构与数据结构**：
  - 采用高级编程架构和数据结构技术，如工厂模式、策略模式等，减少代码冗余，提高代码的复用性。
  - 对于功能相似的变量和参数，使用数据封装和变量拼接优化，确保代码的模块化和复用性。

- **函数与方法的复用**：
  - 将重复出现的逻辑抽象为独立的函数或方法，避免在不同模块中重复编写相同的代码。
  - 确保这些复用的函数或方法具备良好的通用性和扩展性，适应不同场景的需求。

#### 5. **高级代码**

- **结构复杂的代码**：
  - 编写结构复杂且全面的代码，确保各个功能模块的正确性和稳定性。
  - 使用高级的Python特性和第三方库，如数据类（`dataclass`）、异步编程（`asyncio`）等，提升代码的性能。

### **界面与输出需求**

#### 1. **进度监控**

- **动态输出状态**：
  - 实时输出已完成和未完成的模块状态，提供直观的进度条和已完成模块数量提示，帮助用户了解执行进度。
  - 进度监控应具备实时性和准确性，避免进度显示滞后或错误。

- **用户友好的界面**：
  - 使用如`rich`等库优化界面输出，提升信息展示的美观性和可读性。
  - 提供清晰的视觉反馈，帮助用户快速理解当前的执行状态和进度。

#### 2. **错误处理**

- **详细的错误信息展示**：
  - 提供详细的执行过程判断，清晰展示警告和错误信息，说明错误发生的模块和具体命令。
  - 错误信息应具备描述性，帮助用户快速定位和解决问题。

- **美观的信息输出界面**：
  - 使用图形化或格式化的输出方式，提升错误信息的可读性和美观性。
  - 确保错误信息在界面中突出显示，便于用户注意和处理。

### **技术和代码规范**

#### 1. **全局变量与数据结构**

- **统一管理**：
  - 在代码开头统一定义所有全局变量和数据结构，集中管理路径、命令、配置参数、并发执行数量等，确保代码的可维护性和易于扩展。
  - 使用结构化的数据类或配置文件管理这些全局变量，避免硬编码，提高配置的灵活性和可变性。

- **命名与组织**：
  - 全局变量应具备描述性名称，避免使用模糊或过于简短的名称。
  - 数据结构的组织应符合逻辑关系，便于理解和使用。

### **执行与维护**

#### 1. **功能实现**

- **主要使用Python**：
  - 主要使用Python完成所有功能，尽量减少Bash等外部脚本的使用，确保跨平台的兼容性和代码的可维护性。

- **代码的可扩展性**：
  - 设计功能实现时，考虑未来可能的扩展需求，确保代码结构具备良好的扩展性。
  - 通过模块化设计和接口定义，便于后续功能的添加和修改，减少对现有代码的影响。

- **性能优化**：
  - 在功能实现过程中，注重代码的性能优化，确保脚本在处理大规模任务时具备良好的效率和响应速度。
  - 使用异步编程（`asyncio`）等技术提升脚本的并发处理能力，减少等待时间。





好的，你的整体结构我基本上还是相对满意的，我有一些想法和建议提供给你，请你完成我的需求。你不需要提供不涉及改动的部分，哪些部分需要改动、增加、删除，提供给我这些部分就好了，这样我可以更专注于改动的部分。
关于第二步的执行，我希望你可以根据代码中配置一个数据结构，用户会修改这之中的内容，填写这次会涉及的仓库。
然后脚本会检测是否涉及到nebula nebula-sdk tee来决定是否执行第二部分的一些功能或者完全不执行第二部分

第一，tee nebula-sdk nebula 都是由nebula的源码编译出来的，但是我希望你在编译这三个部分之前都要清除上次编译产物
cd ~/grpower/workspace && rm -rf buildroot-pvt8675/ nebula-ree/ buildroot-pvt8675_tee/ && cd ~/grpower/workspace/nebula && rm -rf out 
编译由于涉及到source命令，我希望你可以尽量保障命令连续执行，或者保持其在一个子终端中执行，若非同一个终端应该无法继承变量。其中，我希望你可以使用python抓取命令的所有输出并一起在日志文件中。
nebula编译命令如下。
export NO_PIPENV_SHELL=1 && \
cd ~/grpower/ && source scripts/env.sh && \
cd ~/grpower/ && gr-nebula.py build && \
gr-nebula.py export-buildroot && \
gr-android.py set-product --product-name pvt8675 && \
gr-android.py buildroot export_nebula_images -o /home/nebula/grt/thyp-sdk/products/mt8678-mix/prebuilt-images && \
cd ~/grt/thyp-sdk && \
./configure.sh /home/nebula/grt/nebula-sdk/ > /dev/null && \
./build_all.sh 

nebula-sdk编译命令如下
export NO_PIPENV_SHELL=1 && \
cd ~/grpower/ && source scripts/env.sh && \
cd ~/grpower/ && gr-nebula.py build && \
gr-nebula.py export-buildroot && \
gr-android.py set-product --product-name pvt8675 && \
gr-nebula.py export-sdk -o /home/nebula/grt/nebula-sdk

tee 编译命令如下
export NO_PIPENV_SHELL=1 && \
cd ~/grpower/workspace && rm -rf buildroot-pvt8675/ nebula-ree/ buildroot-pvt8675_tee/ && cd ~/grpower/workspace/nebula && rm -rf out && \
cd ~/grpower/ && source scripts/env.sh && \
cd ~/grpower/ && gr-nebula.py build > ~/grt/tee.log 2>&1 && \
gr-nebula.py export-buildroot >> ~/grt/tee.log 2>&1 && \
gr-android.py set-product --product-name pvt8675_tee >> ~/grt/tee.log 2>&1 && \
mkdir -p ~/grt/teetemp && \
gr-android.py buildroot export_nebula_images -o ~/grt/teetemp >> ~/grt/tee.log 2>&1 && \
cp -v ~/grt/teetemp/nebula*.bin ~/alps/vendor/mediatek/proprietary/trustzone/grt/source/common/kernel/

第二，我认为commit信息不该作为命令行参数，而是作为脚本里配置的变量写在脚本中，脚本中要分开定义提交格式的内容和Description中的信息，所有仓库提交共用一个Description信息。
nebula的两个提交和tee的提交格式如下
git commit -m "Update nebula prebuilt binary.

[Description]

[Test]
Build pass and test ok."
nebula-sdk的提交格式如下
git commit -m "Update nebula-sdk.

[Description]

[Test]
Build pass and test ok."

第三，copy file的文件具体为，这一步你可以直接使用python的方式而不是bash的方式实现
cd /home/nebula/grt/thyp-sdk
cp -f products/mt8678-mix/out/gz.img ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/nbl_vmm ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/nbl_vm_ctl ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/nbl_vm_srv ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/libvmm.so ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/out/symbols/*  ~/yocto/prebuilt/hypervisor/grt/symbols/
cp -f ./third_party/prebuilts/libluajit/lib64/libluajit.so ~/yocto/prebuilt/hypervisor/grt/
cp -f ./products/mt8678-mix/guest-configs/uos_alps_pv8678.lua ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vm_srv/data/vm_srv_cfg_8678.pb.txt ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vmm/data/uos_mtk8678/uos_bootloader_lk2.pb.txt ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vmm/data/vm_audio_cfg.pb.txt ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vmm/data/vm_audio_shared_irq.pb.txt ~/yocto/prebuilt/hypervisor/grt/
cp -f vmm/nbl_vm_srv/data/nbl_ta_monitor ~/yocto/prebuilt/hypervisor/grt/

第四，Tagging nebula不需要检测，这一步无论nebula是否更新都需要打tag
其次，涉及到编译由于涉及到source命令，我希望你可以尽量保障命令连续执行，或者保持其在一个子终端中执行，若非同一个终端应该无法继承变量。

第五，nebula仓库中，zircon和garnet的分支也应该是可定义的参数

