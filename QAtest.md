我现在需要写一份用于测试的python脚本开发需求说明，请你帮我完成这个十分详细且系统的简体中文的开发需求文档，用于给开发团队人员，文档内容中尽量用文字详细描述需求和实现方法。
我的要求是开发一个专业、非常复杂、高度模块化、丰富可拓展性的python3.8.10脚本，其中涉及到可修改的参数、变量部分不需要作为命令行参数而是使用专门的数据结构让使用者修改源码中的内容。涉及到参数返回值等内容必须同时使用说明、冒号、箭头等方式全面保障可维护性可读性，还要有专业的英文注释。
脚本未来会加入将每一项测试结果输入到指定测试报告的Excel xlsx文件中指定的格子中的功能。目前暂时不需要，请关闭这个功能开关，保证可以正常输出测试结果到终端即可。
我需要测试的是一个嵌入式平台的微内核Hpyervisor+两个VM整套系统的稳定性，我为此准备了测试用例，其中adb -s 0123456789ABCDEF 链接的是Android vm系统，adb -s YOCTO链接的是yocto vm系统。hypervisor暂时没有adb连接方式。
目前测试用例如下：


检测物理 CPU：解析 /proc/cpuinfo 输出，统计 processor 字段的出现次数，以确认yocto中应至少有三个 CPU 条目，Android中应至少有五个CPU条目。

检查 vCPU 信息：在yocto端解析 nbl_vm_ctl dump 输出，找到 vcpuX 标签出现的次数，确保有 8 个 vCPU。

在yocto 终端中 nbl_vm_ctl stop十秒后nbl_vm_ctl start，40秒后adb 安卓正常即可

测试虚拟网络不同vm作为client和server时的带宽，yocto ip是192.168.2.1 ，Android ip是192.168.2.2
使用如下命令分别测得不同vm做server时的带宽，


TMPDIR=/data  iperf3 -s  
TMPDIR=/data iperf3 -c 192.168.2.1   

TMPDIR=/data  iperf3 -s 
TMPDIR=/data iperf3 -c 192.168.2.2  
以下是输出结果示例，你可以取client端，最后的receiver的Bitrate作为真实带宽。
sh-3.2# TMPDIR=/data iperf3 -c 192.168.2.2  
Connecting to host 192.168.2.2, port 5201
[  5] local 192.168.2.1 port 57346 connected to 192.168.2.2 port 5201

[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec   880 MBytes  7.37 Gbits/sec   43   1.10 MBytes       
[  5]   1.00-2.00   sec  1006 MBytes  8.44 Gbits/sec    7   1.35 MBytes       
[  5]   2.00-3.00   sec  1014 MBytes  8.50 Gbits/sec  101   1.09 MBytes       
[  5]   3.00-4.00   sec  1.00 GBytes  8.61 Gbits/sec   51   1.26 MBytes       
[  5]   4.00-5.00   sec  1012 MBytes  8.49 Gbits/sec   27   1.42 MBytes       
[  5]   5.00-6.00   sec   838 MBytes  7.03 Gbits/sec   69   1.07 MBytes       
[  5]   6.00-7.00   sec   991 MBytes  8.32 Gbits/sec    3   1.30 MBytes       
[  5]   7.00-8.00   sec  1.01 GBytes  8.64 Gbits/sec   58   1.07 MBytes       
[  5]   8.00-9.00   sec  1020 MBytes  8.56 Gbits/sec   81   1.24 MBytes       
[  5]   9.00-10.00  sec  1.00 GBytes  8.60 Gbits/sec   35   1.11 MBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  9.61 GBytes  8.26 Gbits/sec  475             sender
[  5]   0.00-10.05  sec  9.61 GBytes  8.22 Gbits/sec                  receiver

iperf Done.

测试双向虚拟网络延迟
ping -c 100 192.168.2.2

ping -c 100 192.168.2.1
输出结果的部分内容如下，请在脚本最后统计输出中分别分开说明min/avg/max/mdev的值
64 bytes from 192.168.2.2: icmp_seq=96 ttl=64 time=0.390 ms
64 bytes from 192.168.2.2: icmp_seq=97 ttl=64 time=0.485 ms
64 bytes from 192.168.2.2: icmp_seq=98 ttl=64 time=0.359 ms
64 bytes from 192.168.2.2: icmp_seq=99 ttl=64 time=0.423 ms
64 bytes from 192.168.2.2: icmp_seq=100 ttl=64 time=0.395 ms

--- 192.168.2.2 ping statistics ---
100 packets transmitted, 100 received, 0% packet loss, time 101356ms
rtt min/avg/max/mdev = 0.249/0.383/0.503/0.061 ms


我希望执行所有涉及adb命令之前都要执行adb root