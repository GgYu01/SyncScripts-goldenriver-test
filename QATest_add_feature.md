
我需要你在我已有的python测试脚本项目基础上添加功能：
1：reboot测试，需要对yocto、Android这两个vm通过adb shell reboot进行循环重启测试，检测方式为执行重启命令45秒后，还是否可以通过adb连接到对应系统即可，不需要检测是否可以链接到两个VM，如reboot yocto只需要检测yocto adb是否正常可连接作为重启成功的标志，reboot Android只需要检测Android adb是否正常可连接作为重启成功的标志。重启循环次数和等待时间需要使用新的可配置变量参数定义。两个VM的循环重启测试我希望是独立的，先循环测试某一个VM结束后，再测试另一个VM循环测试，你不需要提供单元测试的代码。

# Python脚本开发需求说明书

## 1. 项目概述

本项目旨在开发一款用于测试嵌入式平台微内核Hypervisor及其下运行的两个虚拟机（VM）系统稳定性的Python 3.8.10脚本。该脚本将执行一系列预定义的测试用例，分析测试结果，并将结果输出至终端。脚本设计需具备高度的模块化、复杂性以及丰富的可扩展性，以适应未来功能的扩展需求。
VM Yocto可以通过ADB连接（设备ID为YOCTO）
VM Android可以通过ADB连接（设备ID为0123456789ABCDEF）

## 3. 非功能需求

### 3.1 模块化设计

脚本应采用高度模块化的设计，将各项功能分解为独立的模块或类，便于维护和扩展。

### 3.2 可扩展性

设计时应预留接口和扩展点，方便未来增加新的测试用例或功能。例如，使用插件架构或配置文件管理新增功能。

### 3.3 可维护性与可读性

- **参数与变量管理**：所有可修改的参数和变量应集中管理，使用专门的数据结构（如配置类或字典）进行定义，便于使用者在源码中修改。
- **代码注释**：所有模块和关键代码块应包含专业的英文注释，说明功能、输入输出及关键逻辑。
- **文档说明**：每个函数和方法应使用说明、冒号、箭头等方式明确描述其参数、返回值及作用。

### 3.4 输出与日志

- 初期版本仅需将测试结果输出至终端。
- 将未来的Excel报告功能预留开关，当前状态为关闭，确保终端输出正常。

## 4. 技术规格

### 4.1 开发语言与版本

- **编程语言**：Python
- **Python版本**：3.8.10

### 4.3 数据结构与配置

- 使用dataclass或配置类集中管理所有可修改参数，如设备ID、IP地址、测试用例参数等。
- 示例配置结构：
  
python
  from dataclasses import dataclass

  @dataclass
  class Config:
      android_device_id: str = "0123456789ABCDEF"
      yocto_device_id: str = "YOCTO"
      yocto_ip: str = "192.168.2.1"
      android_ip: str = "192.168.2.2"
      # 其他可配置参数


### 4.4 日志管理

- 使用Python的logging模块记录测试过程中的关键信息和错误，便于后续调试和维护。

## 5. 实现方法

### 5.1 项目结构

建议采用以下项目结构，以实现模块化和高内聚低耦合：

project/
│
├── config.py            # 配置管理
├── main.py              # 主执行脚本
├── modules/
│   ├── cpu_check.py     # CPU检测模块
│   ├── vcpu_check.py    # vCPU信息检查模块
│   ├── vm_control.py    # VM控制模块
│   ├── bandwidth_test.py# 网络带宽测试模块
│   ├── latency_test.py  # 网络延迟测试模块
│   └── utils.py         # 工具函数
│
├── tests/               # 单元测试
│   └── test_*.py
│
├── requirements.txt     # 依赖列表
└── README.md            # 项目说明


## 8. 交付物

- 完整的Python脚本源码，符合上述功能和非功能需求。
- 详细的开发文档，包括项目结构说明、模块功能介绍及使用指南。
- 单元测试代码及测试报告。
- requirements.txt文件，列出所有依赖库及版本。

### **Python 代码设计与规范**

#### 1. **模块化设计**

- **全局变量与数据结构**：
  - 在代码的开头统一定义所有全局变量和数据结构，包括文件路径、仓库名称、编译命令、日志配置等。
  - 使用数据类（dataclass）来组织和管理相关配置，确保配置的统一性和便于修改。例如，所有需要用户提供的变量参数应作为数据结构的一部分集中定义，避免散布在代码的各个部分。

- **类的使用**：
  - 使用类（class）来封装相关的功能模块，确保代码结构清晰，职责单一，便于维护和扩展。
  - 每个类应负责特定的功能，如构建管理、日志处理、命令执行等，避免功能混杂，提升代码的内聚性。

- **装饰器的应用**：
  - 利用装饰器（decorator）优化代码逻辑，减少重复性任务，如日志记录、时间测量等。
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
  - 所有模块和关键代码块必须包含专业的英文注释，说明其功能、输入输出及逻辑。
  - 每个函数和方法应包含docstring，详细描述其用途、参数和返回值。


- **命名规范**：
  - 变量、函数、类等命名应具备描述性，采用驼峰命名法或下划线命名法，保持一致性。
  - 避免使用过于简短或模糊的名称，确保命名能够准确反映其用途和意义。

#### 3. **错误处理与进度监控**

- **错误处理机制**：
  - 实现全面的错误处理，使用try-except块捕获可能的异常，提供明确的错误提示。
  - 确保脚本在异常情况下能够稳定运行，避免因未处理的异常导致程序崩溃。

- **进度监控**：
  - 动态输出脚本执行状态，使用如rich等库优化界面输出，展示进度条、已完成模块数量等信息。
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
  - 使用高级的Python特性和第三方库，如数据类（dataclass）、异步编程（asyncio）等，提升代码的性能。

### **界面与输出需求**

#### 1. **进度监控**

- **动态输出状态**：
  - 实时输出已完成和未完成的模块状态，提供直观的进度条和已完成模块数量提示，帮助用户了解执行进度。
  - 进度监控应具备实时性和准确性，避免进度显示滞后或错误。

- **用户友好的界面**：
  - 使用如rich等库优化界面输出，提升信息展示的美观性和可读性。
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
  - 使用异步编程（asyncio）等技术提升脚本的并发处理能力，减少等待时间。

以下是目前我部分的源码
gr-nebula@grnebula-System-Product-Name:~/workspace/liu_78/user_home/QAtest$ cat config.py main.py modules/utils.py
# config.py

from dataclasses import dataclass

@dataclass
class Config:
    """
    Configuration class to manage all configurable parameters.
    """
    # Device IDs
    android_device_id: str = "0123456789ABCDEF"
    yocto_device_id: str = "YOCTO"

    # IP Addresses
    yocto_ip: str = "192.168.2.1"
    android_ip: str = "192.168.2.2"

    # Expected CPU counts
    yocto_expected_cpus: int = 3
    android_expected_cpus: int = 5

    # Expected vCPU count
    expected_vcpus: int = 8

    # Wait times
    vm_stop_wait: int = 10
    vm_start_wait: int = 40

    # Ping settings
    ping_count: int = 100

    # Logging configuration
    log_file: str = "test.log"
    log_level: str = "INFO"

    # Excel report generation (future feature)
    generate_excel_report: bool = False
# main.py

import logging
from config import Config
from modules.cpu_check import CPUCheck
from modules.vcpu_check import VCPUCheck
from modules.vm_control import VMControl
from modules.bandwidth_test import BandwidthTest
from modules.latency_test import LatencyTest

def setup_logging(config: Config):
    """
    Sets up the logging configuration.

    Args:
        config (Config): The configuration object.
    """
    logging.basicConfig(
        filename=config.log_file,
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    """
    Main function to execute all test modules.
    """
    # Initialize configuration and logging
    config = Config()
    setup_logging(config)
    logging.info("Starting the test suite.")

    # CPU Detection Tests
    cpu_checker = CPUCheck(config)
    yocto_cpu_result = cpu_checker.check_cpu(
        config.yocto_device_id,
        config.yocto_expected_cpus,
        "Yocto"
    )
    android_cpu_result = cpu_checker.check_cpu(
        config.android_device_id,
        config.android_expected_cpus,
        "Android"
    )

    # vCPU Information Check
    vcpu_checker = VCPUCheck(config)
    vcpu_result = vcpu_checker.check_vcpu()

    # VM Control Test
    vm_controller = VMControl(config)
    vm_control_result = vm_controller.control_vm()

    # Virtual Network Bandwidth Test
    bandwidth_tester = BandwidthTest(config)
    bandwidth_results = bandwidth_tester.test_bandwidth()

    # Virtual Network Latency Test
    latency_tester = LatencyTest(config)
    latency_results = latency_tester.test_latency()

    # Output Results
    print("\n=== Test Results ===")
    print(f"Yocto CPU Check: {'Passed' if yocto_cpu_result else 'Failed'}")
    print(f"Android CPU Check: {'Passed' if android_cpu_result else 'Failed'}")
    print(f"vCPU Information Check: {'Passed' if vcpu_result else 'Failed'}")
    print(f"VM Control Test: {'Passed' if vm_control_result else 'Failed'}")
    print(f"Bandwidth Test Results: {bandwidth_results}")
    print(f"Latency Test Results: {latency_results}")

    logging.info("Test suite completed.")

if __name__ == "__main__":
    main()
# modules/utils.py

import subprocess
import logging
import re
from typing import Tuple

def execute_adb_command(device_id: str, command: str) -> Tuple[str, bool]:
    """
    Executes an ADB shell command on the specified device.

    Args:
        device_id (str): The ADB device ID.
        command (str): The shell command to execute.

    Returns:
        Tuple[str, bool]: Output of the command and success status.
    """
    root_command = f"adb -s {device_id} root"
    try:
        logging.info(f"执行 root 命令: {root_command}")
        subprocess.check_output(root_command, shell=True, stderr=subprocess.STDOUT)
        logging.info(f"成功执行 root 命令: {root_command}")
    except subprocess.CalledProcessError as e:
        logging.error(f"执行 root 命令失败: {root_command}\n错误: {e.output.decode('utf-8')}")
        # return e.output.decode('utf-8'), False

    full_command = f"adb -s {device_id} shell {command}"
    try:
        logging.info(f"Executing command: {full_command}")
        output = subprocess.check_output(full_command, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8'), True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {full_command}\nError: {e.output.decode('utf-8')}")
        return e.output.decode('utf-8'), False

def parse_cpuinfo(output: str) -> int:
    """
    Parses the CPU info to count the number of processors.

    Args:
        output (str): The output from /proc/cpuinfo.

    Returns:
        int: Number of processors found.
    """
    return len(re.findall(r'^processor\s*:', output, re.MULTILINE))

def parse_vcpu_info(output: str) -> int:
    """
    Parses the vCPU info to count the number of vCPUs.

    Args:
        output (str): The output from nbl_vm_ctl dump.

    Returns:
        int: Number of vCPUs found.
    """
    return len(re.findall(r'vcpu\d+', output))

def parse_iperf3_output(output: str) -> float:
    """
    Parses iperf3 output to extract the receiver's bitrate.

    Args:
        output (str): The output from iperf3 command.

    Returns:
        float: Receiver bitrate in Mbits/sec.
    """
    # Regex to capture the bitrate and its unit (Mbits/sec or Gbits/sec)
    match = re.search(
        r'\[.*\]\s+\d+\.\d+-\d+\.\d+\s+sec\s+[\d\.]+\s+\w+\s+([\d\.]+)\s+([MG])bits/sec\s+receiver',
        output
    )
    if match:
        bitrate = float(match.group(1))
        unit = match.group(2)
        if unit == 'G':
            bitrate *= 1000  # Convert Gbits/sec to Mbits/sec
        return bitrate
    else:
        logging.warning("Failed to parse iperf3 output.")
        return 0.0

def parse_ping_output(output: str) -> dict:
    """
    Parses ping output to extract min/avg/max/mdev values.

    Args:
        output (str): The output from ping command.

    Returns:
        dict: A dictionary with min, avg, max, mdev values.
    """
    match = re.search(r'([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+)', output)
    if match:
        return {
            'min': float(match.group(1)),
            'avg': float(match.group(2)),
            'max': float(match.group(3)),
            'mdev': float(match.group(4))
        }
    else:
        logging.warning("Failed to parse ping output.")
        return {}