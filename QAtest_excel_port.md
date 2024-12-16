# Python自动化测试脚本开发需求说明书

## 1. 项目概述

本项目旨在开发一款专业、复杂、高度模块化且具有丰富可拓展性的Python 3.8.10自动化测试脚本。该脚本将在现有的多种测试项目基础上，自动将测试结果填入指定的Excel表格中，以提高测试效率和结果记录的准确性。目标是实现一个能够自动化处理多项测试任务，并将结果以规范化的格式记录到Excel表格中的系统。

## 2. 目标与范围

- **目标**：开发一个高度模块化、可拓展且符合规范的Python自动化测试脚本，能够自动读取和填写指定Excel表格中的特定工作表内容，确保测试结果的准确记录和易于追踪。
  
- **范围**：
  - 自动执行现有的多种测试项目。
  - 根据测试结果自动填写Excel表格中的特定单元格。
  - 提供手动调试功能，允许用户手动输入月份和日期。
  - 确保脚本具有良好的可维护性和可拓展性，便于未来新增测试项目。

## 3. 功能需求

### 3.1 脚本基本功能

- **自动执行测试**：脚本应能够依次执行多个测试项目，包括但不限于`cpu_check.py`、`vcpu_check.py`、`vm_control.py`、`bandwidth_test.py`、`latency_test.py`和`reboot_test.py`。
  
- **Excel表格操作**：脚本需自动读取并填写位于指定路径下的Excel表格`Hypervisor-Checklist-hypervisor测试项.xlsx`中的特定工作表。

### 3.2 Excel表格填写要求

- **工作表名称**：脚本应根据当前日期自动生成工作表名称，格式为`MM/DD测试报告`，例如`11/11测试报告`。同时，提供手动输入月份和日期的功能，以便调试时使用。
  
- **数据填写规范**：
  
  1. **cpu_check.py 测试**：
     - **J7单元格**：填写检测到的Yocto CPU数量，格式如`"3 cores"`。
     - **K7单元格**：若测试通过，填写`PASS`；否则，填写`Failed`。
     - **J8单元格**：填写检测到的Android CPU数量，格式如`"3 cores"`。
     - **K8单元格**：若测试通过，填写`PASS`；否则，填写`Failed`。
  
  2. **vcpu_check.py 测试**：
     - **J10单元格**：若测试通过，填写`CPU0-7信息均可正常显示`；否则，填写`CPU0-7信息未正常显示`。
     - **K10单元格**：若测试通过，填写`PASS`；否则，填写`Failed`。
  
  3. **vm_control.py 测试**：
     - **J11单元格**：若测试通过，填写`Android正常启动`；否则，填写`Android未正常启动`。
     - **K11单元格**：若测试通过，填写`PASS`；否则，填写`Failed`。
  
  4. **bandwidth_test.py 测试**：
     - **J22单元格**：填写带宽测试结果，格式如下（在同一单元格内换行）：
       ```
       Android_to_Yocto : 7440.0 Mbps
       Yocto_to_Android : 7690.0 Mbps
       ```
     - **终端输出**：与Excel表格填写内容格式一致，确保美观排版和换行。
     - **K22单元格**：若测试通过，填写`PASS`；否则，填写`Failed`。
  
  5. **latency_test.py 测试**：
     - **J23单元格**：填写延迟测试结果，格式如下（在同一单元格内换行）：
       ```
       Yocto_to_Android : min=0.294 ms, avg=0.368 ms, max=1.096 ms, mdev=0.082 ms
       Android_to_Yocto : min=0.184 ms, avg=0.256 ms, max=0.434 ms, mdev=0.047 ms
       ```
     - **终端输出**：与Excel表格填写内容格式一致，确保美观排版和换行。
     - **K23单元格**：若测试通过，填写`PASS`；否则，填写`Failed`。
  
  6. **reboot_test.py 测试**：
     - **J24单元格**：填写Yocto VM重启循环成功次数，格式如`连续重启 '重启次数' 次正常`。
     - **K24单元格**：若测试通过，填写`PASS`；否则，填写`Failed`。
     - **J25单元格**：填写Android VM重启循环成功次数，格式如`连续重启 '重启次数' 次正常`。
     - **K25单元格**：若测试通过，填写`PASS`；否则，填写`Failed`。

### 3.3 日期获取与调试功能

- **自动获取当前日期**：脚本应自动获取当天的月份和日期，用于生成工作表名称。
  
- **手动输入功能**：提供接口允许用户手动输入月份和日期，以便在调试过程中覆盖自动获取的值。

### 3.4 终端输出格式化

- **带宽测试和延迟测试**：确保终端输出与Excel表格中的填写内容格式一致，采用美观的排版和适当的换行，提升可读性。

### **Python 代码设计与规范**

#### 1. **模块化设计**

- **全局变量与数据结构**：
  - 在代码的开头统一定义所有全局变量和数据结构，包括文件路径、仓库名称、编译命令、日志配置、命令、配置参数、并发执行确保代码的可维护性和易于扩展。
  - 使用结构化的数据类（`dataclass`）或配置文件来组织和管理相关配置，确保配置的统一性和便于修改，避免硬编码，提高配置的灵活性和可变性。例如，所有需要用户提供的变量参数应作为数据结构的一部分集中定义，避免散布在代码的各个部分。

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
  - 遵循PEP 8编码规范，保持代码整洁和一致性。
  - 使用有意义的变量和函数命名，便于理解和维护。

- **专业英文注释**：
  - 为每个函数或方法添加详细的英文注释，说明其作用、参数、返回值以及关键逻辑。
  - 使用类型提示（Type Hint）明确参数和返回值的类型，增强代码的可读性和静态分析能力。

- **命名规范**：
  - 变量、函数、类等命名应具备描述性，避免使用模糊或过于简短的名称，采用驼峰命名法或下划线命名法，保持一致性。
  - 避免使用过于简短或模糊的名称，确保命名能够准确反映其用途和意义。
  - 数据结构的组织应符合逻辑关系，便于理解和使用

#### 3. **错误处理与进度监控**

- **错误处理机制**：
  - 提供详细的执行过程判断，清晰展示警告和错误信息，说明错误发生的模块和具体命令。
  - 实现全面的错误处理，捕获可能的异常，提供明确的错误提示。
  - 错误信息应具备描述性，帮助用户快速定位和解决问题。
  - 确保脚本在异常情况下能够稳定运行，避免因未处理的异常导致程序崩溃。

- **美观的信息输出界面**：
  - 使用图形化或格式化的输出方式，提升错误信息的可读性和美观性。
  - 确保错误信息在界面中突出显示，便于用户注意和处理。

- **进度监控**：
  - 动态输出脚本执行状态，使用如`rich`等库优化界面输出，输出专业、详细的丰富颜色信息到终端以供用户查看执行情况和状态，并展示进度条、已完成模块数量等信息。
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
  - 使用高级的Python特性和第三方库，如数据类（`dataclass`）等，提升代码的性能。

- **性能优化**：
  - 在功能实现过程中，注重代码的性能优化，确保脚本在处理大规模任务时具备良好的效率和响应速度。
  - 使用异步编程（`asyncio`）等技术提升脚本的并发处理能力，减少等待时间。  

- **主要使用Python**：
  - 主要使用Python完成所有功能，尽量减少Bash等外部脚本的使用，确保跨平台的兼容性和代码的可维护性。

- **代码的可扩展性**：
  - 设计功能实现时，考虑未来可能的扩展需求，确保代码结构具备良好的扩展性。
  - 通过模块化设计和接口定义，便于后续功能的添加和修改，减少对现有代码的影响。

  gr-nebula@grnebula-System-Product-Name:~/workspace/liu_78/user_home/QAtest$ tree
.
├── code.log
├── config.py
├── main.py
├── modules
│   ├── bandwidth_test.py
│   ├── cpu_check.py
│   ├── latency_test.py
│   ├── reboot_test.py
│   ├── utils.py
│   ├── vcpu_check.py
│   └── vm_control.py
├── README.md
└── requirements.txt

gr-nebula@grnebula-System-Product-Name:~/workspace/liu_78/user_home/QAtest$ cat config.py main.py modules/utils.py modules/cpu_check.py modules/vcpu_check.py modules/vm_control.py modules/bandwidth_test.py modules/latency_test.py modules/reboot_test.py
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

    # Wait times , only for vm_control.py use 
    vm_stop_wait: int = 10
    vm_start_wait: int = 40

    # Ping settings
    ping_count: int = 100

    # Logging configuration
    log_file: str = "test.log"
    log_level: str = "INFO"

    # Excel report generation (future feature)
    generate_excel_report: bool = False

    # Reboot Test Configuration
    yocto_reboot_loop_count: int = 50
    yocto_reboot_wait_time: int = 41
    android_reboot_loop_count: int = 50
    android_reboot_wait_time: int = 41# main.py

import logging
from config import Config
from modules.cpu_check import CPUCheck
from modules.vcpu_check import VCPUCheck
from modules.vm_control import VMControl
from modules.bandwidth_test import BandwidthTest
from modules.latency_test import LatencyTest
from modules.reboot_test import RebootTest 

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

    # Reboot Test
    reboot_tester = RebootTest(config)
    reboot_result = reboot_tester.run_reboot_tests()

    # Output Results
    print("\n=== Test Results ===")
    print(f"Yocto CPU Check: {'Passed' if yocto_cpu_result else 'Failed'}")
    print(f"Android CPU Check: {'Passed' if android_cpu_result else 'Failed'}")
    print(f"vCPU Information Check: {'Passed' if vcpu_result else 'Failed'}")
    print(f"VM Control Test: {'Passed' if vm_control_result else 'Failed'}")
    print(f"Bandwidth Test Results: {bandwidth_results}")
    print(f"Latency Test Results: {latency_results}")
    print(f"Reboot Test: {'Passed' if reboot_result else 'Failed'}")

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

def execute_host_command(command: str) -> Tuple[str, bool]:
    """
    Executes a command on the host machine.

    Args:
        command (str): The command to execute.

    Returns:
        Tuple[str, bool]: Output of the command and success status.
    """
    try:
        logging.info(f"Executing host command: {command}")
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8'), True
    except subprocess.CalledProcessError as e:
        logging.error(f"Host command failed: {command}\nError: {e.output.decode('utf-8')}")
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
# modules/cpu_check.py

import logging
from modules.utils import execute_adb_command, parse_cpuinfo
from config import Config

class CPUCheck:
    """
    CPU detection module for both Yocto and Android systems.
    """

    def __init__(self, config: Config):
        self.config = config

    def check_cpu(self, device_id: str, expected_count: int, system_name: str) -> bool:
        """
        Checks the CPU count on the specified device.

        Args:
            device_id (str): The ADB device ID.
            expected_count (int): Expected number of CPUs.
            system_name (str): Name of the system (Yocto or Android).

        Returns:
            bool: True if CPU count meets or exceeds expected count, False otherwise.
        """
        output, success = execute_adb_command(device_id, "cat /proc/cpuinfo")
        if not success:
            logging.error(f"Failed to retrieve CPU info from {system_name}.")
            return False

        cpu_count = parse_cpuinfo(output)
        logging.info(f"{system_name} CPU count: {cpu_count}")

        if cpu_count >= expected_count:
            logging.info(f"{system_name} CPU check passed.")
            return True
        else:
            logging.warning(f"{system_name} CPU check failed. Expected at least {expected_count}, found {cpu_count}.")
            return False
# modules/vcpu_check.py

import logging
from modules.utils import execute_adb_command, parse_vcpu_info
from config import Config

class VCPUCheck:
    """
    vCPU information check module for Yocto system.
    """

    def __init__(self, config: Config):
        self.config = config

    def check_vcpu(self) -> bool:
        """
        Checks the vCPU count on the Yocto system.

        Returns:
            bool: True if vCPU count matches expected count, False otherwise.
        """
        output, success = execute_adb_command(self.config.yocto_device_id, "nbl_vm_ctl dump")
        if not success:
            logging.error("Failed to execute 'nbl_vm_ctl dump' on Yocto.")
            return False

        vcpu_count = parse_vcpu_info(output)
        logging.info(f"Yocto vCPU count: {vcpu_count}")

        if vcpu_count == self.config.expected_vcpus:
            logging.info("vCPU check passed.")
            return True
        else:
            logging.warning(f"vCPU check failed. Expected {self.config.expected_vcpus}, found {vcpu_count}.")
            return False
# modules/vm_control.py

import logging
import time
from modules.utils import execute_adb_command
from config import Config

class VMControl:
    """
    VM control test module for Yocto system.
    """

    def __init__(self, config: Config):
        self.config = config

    def control_vm(self) -> bool:
        """
        Stops and starts the VM on Yocto system and verifies Android system availability.

        Returns:
            bool: True if Android system is accessible after VM restart, False otherwise.
        """
        # Stop VM
        output, success = execute_adb_command(self.config.yocto_device_id, "nbl_vm_ctl stop")
        if not success:
            logging.error("Failed to stop VM on Yocto.")
            return False
        logging.info("VM stopped successfully.")
        time.sleep(self.config.vm_stop_wait)

        # Start VM
        output, success = execute_adb_command(self.config.yocto_device_id, "nbl_vm_ctl start")
        if not success:
            logging.error("Failed to start VM on Yocto.")
            return False
        logging.info("VM started successfully.")
        time.sleep(self.config.vm_start_wait)

        # Verify Android system
        output, success = execute_adb_command(self.config.android_device_id, "uptime")
        if success:
            logging.info("Android system is running and accessible.")
            return True
        else:
            logging.error("Android system is not accessible after VM restart.")
            return False
# modules/bandwidth_test.py

import logging
import threading
import time
from modules.utils import execute_adb_command, parse_iperf3_output
from config import Config

class BandwidthTest:
    """
    Virtual network bandwidth test module.
    """

    def __init__(self, config: Config):
        self.config = config

    def start_iperf_server(self, device_id: str):
        """
        Starts iperf3 server on the specified device.

        Args:
            device_id (str): The ADB device ID.
        """
        command = "TMPDIR=/data iperf3 -s"
        execute_adb_command(device_id, command)
        logging.info(f"Started iperf3 server on device {device_id}.")

    def stop_iperf_server(self, device_id: str):
        """
        Stops iperf3 server on the specified device.

        Args:
            device_id (str): The ADB device ID.
        """
        execute_adb_command(device_id, "pkill iperf3")
        logging.info(f"Stopped iperf3 server on device {device_id}.")

    def run_iperf_client(self, device_id: str, server_ip: str) -> float:
        """
        Runs iperf3 client on the specified device.

        Args:
            device_id (str): The ADB device ID.
            server_ip (str): The IP address of the iperf3 server.

        Returns:
            float: Measured bandwidth in Mbits/sec.
        """
        command = f"TMPDIR=/data iperf3 -c {server_ip} -t 10"
        output, success = execute_adb_command(device_id, command)
        if not success:
            logging.error(f"Failed to run iperf3 client on device {device_id}.")
            return 0.0

        bandwidth = parse_iperf3_output(output)
        logging.info(f"Bandwidth from device {device_id} to {server_ip}: {bandwidth} Mbits/sec.")
        return bandwidth

    def test_bandwidth(self) -> dict:
        """
        Tests the bandwidth between Yocto and Android systems in both directions.

        Returns:
            dict: Bandwidth results for both directions.
        """
        results = {}

        # Yocto as server, Android as client
        server_thread = threading.Thread(target=self.start_iperf_server, args=(self.config.yocto_device_id,))
        server_thread.start()
        time.sleep(2)  # Wait for server to start
        bandwidth = self.run_iperf_client(self.config.android_device_id, self.config.yocto_ip)
        results['Android_to_Yocto'] = bandwidth
        self.stop_iperf_server(self.config.yocto_device_id)

        # Android as server, Yocto as client
        server_thread = threading.Thread(target=self.start_iperf_server, args=(self.config.android_device_id,))
        server_thread.start()
        time.sleep(2)  # Wait for server to start
        bandwidth = self.run_iperf_client(self.config.yocto_device_id, self.config.android_ip)
        results['Yocto_to_Android'] = bandwidth
        self.stop_iperf_server(self.config.android_device_id)

        return results
# modules/latency_test.py

import logging
from modules.utils import execute_adb_command, parse_ping_output
from config import Config

class LatencyTest:
    """
    Virtual network latency test module.
    """

    def __init__(self, config: Config):
        self.config = config

    def run_ping_test(self, source_device_id: str, target_ip: str, direction: str) -> dict:
        """
        Runs ping test from source device to target IP.

        Args:
            source_device_id (str): The ADB device ID of the source.
            target_ip (str): The IP address to ping.
            direction (str): Direction description for logging.

        Returns:
            dict: Latency statistics.
        """
        command = f"ping -c {self.config.ping_count} {target_ip}"
        output, success = execute_adb_command(source_device_id, command)
        if not success:
            logging.error(f"Failed to run ping test from {direction}.")
            return {}

        latency_stats = parse_ping_output(output)
        logging.info(f"Latency {direction}: {latency_stats}")
        return latency_stats

    def test_latency(self) -> dict:
        """
        Tests the latency between Yocto and Android systems in both directions.

        Returns:
            dict: Latency results for both directions.
        """
        results = {}

        # Yocto to Android
        results['Yocto_to_Android'] = self.run_ping_test(
            self.config.yocto_device_id,
            self.config.android_ip,
            "Yocto to Android"
        )

        # Android to Yocto
        results['Android_to_Yocto'] = self.run_ping_test(
            self.config.android_device_id,
            self.config.yocto_ip,
            "Android to Yocto"
        )

        return results
# modules/reboot_test.py

import logging
import time
from typing import Optional
from modules.utils import execute_adb_command, execute_host_command

class RebootTest:
    """
    Class to perform reboot tests on specified VMs using ADB.
    """

    def __init__(self, config):
        """
        Initializes the RebootTest with the given configuration.

        Args:
            config (Config): The configuration object.
        """
        self.config = config

    def reboot_vm(self, device_id: str, vm_name: str, loop_count: int, wait_time: int) -> bool:
        """
        Performs a looped reboot test on the specified VM.

        Args:
            device_id (str): The ADB device ID of the VM.
            vm_name (str): The name of the VM (for logging purposes).
            loop_count (int): Number of reboot cycles to perform.
            wait_time (int): Time to wait after each reboot (in seconds).

        Returns:
            bool: True if all reboots are successful, False otherwise.
        """
        logging.info(f"Starting reboot test for {vm_name} with {loop_count} cycles.")
        for i in range(1, loop_count + 1):
            logging.info(f"{vm_name} Reboot Cycle {i}/{loop_count}: Initiating reboot.")
            reboot_command = "reboot"
            _, success = execute_adb_command(device_id, reboot_command)
            # if not success:
            #     logging.error(f"{vm_name} Reboot Cycle {i}: Failed to send reboot command.")
            #     return False

            logging.info(f"{vm_name} Reboot Cycle {i}: Waiting for {wait_time} seconds after reboot.")
            time.sleep(wait_time)

            logging.info(f"{vm_name} Reboot Cycle {i}: Checking if VM is back online.")
            connected = self.check_vm_online(device_id, vm_name)
            if connected:
                logging.info(f"{vm_name} Reboot Cycle {i}: VM is back online.")
            else:
                logging.error(f"{vm_name} Reboot Cycle {i}: VM failed to come online.")
                return False

        logging.info(f"Reboot test for {vm_name} completed successfully.")
        return True

    def check_vm_online(self, device_id: str, vm_name: str) -> bool:
        """
        Checks if the specified VM is online by executing a specific command.

        Args:
            device_id (str): The ADB device ID.
            vm_name (str): The name of the VM (for determining the command to execute).

        Returns:
            bool: True if the VM responds correctly, False otherwise.
        """
        if vm_name.lower() == "android":
            # For Android, execute 'getprop' and check if it returns properties
            command = "getprop"
            output, success = execute_adb_command(device_id, command)
            if success and "ro.build.version.release" in output:
                return True
            else:
                logging.error(f"Android VM {device_id} did not respond as expected.")
                return False
        elif vm_name.lower() == "yocto":
            # For Yocto, execute 'uname -a' and check if it returns kernel info
            command = "uname -a"
            output, success = execute_adb_command(device_id, command)
            if success and "Linux" in output:
                return True
            else:
                logging.error(f"Yocto VM {device_id} did not respond as expected.")
                return False
        else:
            logging.error(f"Unknown VM name: {vm_name}. Cannot perform online check.")
            return False

    def run_reboot_tests(self) -> bool:
        """
        Runs reboot tests for both Yocto and Android VMs sequentially.

        Returns:
            bool: True if all reboot tests pass, False otherwise.
        """

        # Reboot Android VM
        android_success = self.reboot_vm(
            device_id=self.config.android_device_id,
            vm_name="Android",
            loop_count=self.config.android_reboot_loop_count,
            wait_time=self.config.android_reboot_wait_time
        )

        if not android_success:
            logging.error("Android reboot test failed.")
            return False

        # Reboot Yocto VM
        yocto_success = self.reboot_vm(
            device_id=self.config.yocto_device_id,
            vm_name="Yocto",
            loop_count=self.config.yocto_reboot_loop_count,
            wait_time=self.config.yocto_reboot_wait_time
        )

        if not yocto_success:
            logging.error("Yocto reboot test failed.")
            return False

        # time.sleep(100)

        logging.info("All reboot tests passed successfully.")
        return True