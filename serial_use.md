看起来你在安装 `serial` 和 `pyserial` 时遇到了冲突。实际上，`pyserial` 提供了 `serial` 模块，但直接安装 `serial` 包可能会导致命名冲突，从而引发 `ModuleNotFoundError`。

### 问题分析

1. 安装了错误的包：你首先安装了 `serial` 包（版本 `0.0.97`），这是一个与 `pyserial` 不相关的包。`pyserial` 才是提供 `serial` 模块的正确库。
2. 安装路径问题：你使用 `pip3 install pyserial` 时，包被安装在了用户目录下 (`~/.local/lib/python3.8/site-packages`)，而你使用 `sudo` 运行脚本时，系统会使用全局环境，可能找不到用户目录下安装的包。

### 解决步骤

为了修复这个问题，请按照以下步骤操作：

#### 1. 卸载错误的 `serial` 包

首先，卸载已安装的 `serial` 包，以避免与 `pyserial` 冲突：

```bash
pip3 uninstall serial
```

你可能需要确认卸载操作。完成后，确保没有 `serial` 包残留：

```bash
pip3 show serial
```

如果没有输出，说明 `serial` 包已成功卸载。

#### 2. 确保 `pyserial` 正确安装

接下来，确保 `pyserial` 安装在系统级别，而不仅仅是在用户目录下。使用 `sudo` 来全局安装 `pyserial`：

```bash
sudo pip3 install --upgrade pyserial
```

这将确保 `pyserial` 在全局 Python 环境中可用。

#### 3. 验证安装

你可以通过以下命令来验证 `pyserial` 是否正确安装，并且 `serial` 模块可以被找到：

```bash
python3 -c "import serial; print(serial.__version__)"
```

如果输出了 `pyserial` 的版本号（例如 `3.5`），说明安装成功。

#### 4. 运行脚本

现在，尝试使用 `sudo` 运行你的脚本：

```bash
sudo python3 send_serial_command.py
```

如果一切顺利，脚本应该能够正确导入 `serial` 模块并执行。

#### 5. 可选：避免使用 `sudo` 运行脚本

如果你的用户有权限访问串口设备（例如 `/dev/ttyUSB0`），你可以避免使用 `sudo` 运行脚本，这样可以使用用户级别安装的包。你可以将当前用户添加到 `dialout` 组，以获得串口访问权限：

```bash
sudo usermod -a -G dialout $USER
```

注意：运行以上命令后，需要重新登录以使更改生效。

#### 6. 确保没有命名冲突

确保你的脚本或当前目录中没有名为 `serial.py` 的文件，因为这会与 `pyserial` 的 `serial` 模块发生冲突。如果有，重命名该文件。

### 总结

1. 卸载错误的 `serial` 包：`pip3 uninstall serial`
2. 全局安装 `pyserial`：`sudo pip3 install --upgrade pyserial`
3. 验证安装：`python3 -c "import serial; print(serial.__version__)"`
4. 运行脚本：`sudo python3 send_serial_command.py`
5. （可选）添加用户到 `dialout` 组：`sudo usermod -a -G dialout $USER`，然后重新登录
6. 检查命名冲突：确保没有 `serial.py` 文件

通过以上步骤，应该可以解决 `ModuleNotFoundError: No module named 'serial'` 的问题。如果问题仍然存在，请提供更多的错误信息以便进一步诊断。