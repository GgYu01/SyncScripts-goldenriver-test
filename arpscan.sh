#!/bin/bash

# 定义网段
network="192.168.50.0/24"

echo "Scanning the network: $network"

# 使用 arp-scan 工具扫描网段中的所有设备
# 执行扫描并过滤出活动的 IP 地址
scan_result=$(sudo arp-scan --interface=enp6s0 $network | grep -E "192\.168\.50\.[0-9]+")

# 提取 IP 地址，并按主机部分排序
sorted_ips=$(echo "$scan_result" | awk '{print $1}' | sort -t . -k 4,4n)

# 获取活动设备的数量
device_count=$(echo "$sorted_ips" | wc -l)

echo "Number of active devices found: $device_count"
echo "Active devices and their IP addresses (sorted by host part):"

# 输出排序后的 IP 地址
echo "$sorted_ips"

# 完成
echo "Network scan complete."
