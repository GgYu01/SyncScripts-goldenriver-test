如果您有多个版本的 Clang 和 GCC 同时需要在一次编译中调用，并且您希望每个编译器版本都能通过 Icecream 进行分布式编译，那么可以采用一个稍微不同的策略来集成 Icecream。您需要为每个编译器版本创建一个对应的封装脚本，这些脚本在调用实际的编译器前将编译任务重定向到 Icecream。

### 创建封装脚本的步骤如下：

1. **创建封装脚本：**
   为每个 Clang 和 GCC 版本创建一个脚本，这个脚本首先设置必要的环境变量，然后调用 `icecc` 以及真正的编译器。例如，为 GCC 4.9.1 版本创建一个脚本 `gcc-wrapper.sh`：

   ```bash
   #!/bin/bash
   # 设置 ICECC 环境变量，如果有必要的话
   export ICECC_VERSION=/path/to/your/gcc-x.x.x.tar.gz
   # 调用实际的编译器，通过 icecc
   exec icecc /path/to/original/gcc "$@"
   ```

2. **放置脚本并修改权限：**
   将这个脚本放在您的预构建路径中，并为其设置执行权限：

   ```bash
   chmod +x gcc-wrapper.sh
   ```

3. **修改符号链接：**
   修改之前创建的符号链接，让它们指向新的封装脚本而不是直接指向 `icecc`：

   ```bash
   ln -sf /path/to/gcc-wrapper.sh ~/alps/prebuilts/gcc/linux-x86/aarch64/aarch64-linux-android-4.9.1
   ```

   类似地，为每个 Clang 和 GCC 版本创建和链接相应的脚本。

4. **调整构建系统：**
   确保构建系统在调用编译器时使用这些新的路径。大多数情况下，通过简单地创建符号链接即可实现这一点，无需更改构建脚本。

5. **测试配置：**
   如同前面的建议，通过执行小的测试编译任务来验证您的配置是否正确。

通过这种方法，您可以保持对各个编译器版本的精确控制，同时利用 Icecream 进行分布式编译。每个封装脚本都可以根据需要调整编译器的特定设置，确保所有版本都能正确工作。


`ICECC_VERSION` 环境变量指向一个压缩包，该压缩包包含了 Icecream 使用的编译器环境。这个压缩包通常应包括编译器本身（如 GCC 或 Clang）、相关的二进制文件以及库文件。其核心作用是确保在不同的 Icecream 节点上使用完全相同的编译器版本，以避免因环境差异导致的编译问题。

### 创建 ICECC_VERSION 压缩包的步骤如下：

1. **选择需要的编译器版本：**
   确定您需要支持的编译器版本。例如，如果您正在使用 GCC 4.9.1，您需要从该版本的安装路径中收集文件。

2. **收集编译器文件：**
   您需要收集编译器的执行文件、库文件、头文件等。确保包括了编译器运行所需的所有依赖项。对于 GCC，通常需要包括：
   - `bin/` 目录下的 `gcc`、`g++` 等执行文件
   - `lib/` 目录下的支持库
   - `libexec/` 目录下的 GCC 内部工具
   - `include/` 目录下的头文件（如果需要）

3. **创建压缩包：**
   将上述文件放在一个临时目录下，然后使用 `tar` 命令创建压缩包。例如：

   ```bash
   mkdir /tmp/gcc-4.9.1
   # 假设您的GCC安装在/usr/local/gcc-4.9.1
   cp -r /usr/local/gcc-4.9.1/bin /tmp/gcc-4.9.1/
   cp -r /usr/local/gcc-4.9.1/lib /tmp/gcc-4.9.1/
   cp -r /usr/local/gcc-4.9.1/libexec /tmp/gcc-4.9.1/
   cp -r /usr/local/gcc-4.9.1/include /tmp/gcc-4.9.1/
   tar -czvf gcc-4.9.1.tar.gz -C /tmp gcc-4.9.1
   ```

   这将创建一个包含所有必要文件的 `gcc-4.9.1.tar.gz` 压缩包。

4. **配置 ICECC_VERSION 环境变量：**
   将压缩包移动到适当的位置，并在封装脚本中设置 `ICECC_VERSION` 环境变量指向该压缩包：

   ```bash
   export ICECC_VERSION=/path/to/gcc-4.9.1.tar.gz
   ```

### 注意事项：

- 确保您打包的编译器和目标 Icecream 环境的操作系统兼容。例如，如果您的 Icecream 环境运行的是 Linux，那么打包的编译器也应该是为 Linux 准备的。
- 压缩包路径应该是可从所有构建节点访问的位置，可以使用网络共享存储或每个节点上相同的本地路径。
- 在打包时，确保包括了所有必要的依赖库，否则在不同节点上可能会因找不到某些库而导致编译失败。

通过这种方式，您可以确保使用 Icecream 的分布式编译环境中的所有节点都使用相同版本的编译器，从而避免可能的兼容性问题。

strace -f -e execve -o strace.log make -jN
strace -f -e execve -s 5000 -o strace_output.log bash -c "while true; do sleep 1; done" &
sudo strace -f -e execve -o /tmp/full_compile_trace.log bash -c 'make -jN'
sudo strace -f -e execve -s 1000 -o /tmp/full_compile_trace.log bash -c 'make krn_images -j36'

inotifywait -m -r /usr/bin /usr/local/bin /path/to/compilers \
-e access -e open -e modify -e attrib --format '%w%f' \
| grep -E 'gcc|clang|arm|aarch64|cross|build|pokymllib' >> /tmp/compiler_activity.log &

export PROMPT_COMMAND='history 1 >> /tmp/command_history.log'

grep -E 'gcc|clang|arm|aarch64' /tmp/compile_commands.log

icecc --build-native --clang /path/to/clang