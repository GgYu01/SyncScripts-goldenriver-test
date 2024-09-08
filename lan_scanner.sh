#!/bin/bash

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]
  then echo "请以root权限运行此脚本"
  exit
fi

# 检查nmap是否安装
if ! command -v nmap &> /dev/null
then
    echo "nmap 未安装. 正在安装..."
    apt-get update
    apt-get install nmap -y
fi

# 获取本机IP地址和子网
IP=$(ip -o -4 addr list | grep -v docker | grep -v virbr | grep -v "127.0.0.1" | awk '{print $4}' | cut -d/ -f1 | head -n 1)
SUBNET=$(echo $IP | cut -d. -f1-3)

echo "正在扫描子网 $SUBNET.0/24..."

# 使用nmap扫描网络
nmap -sn $SUBNET.0/24 | grep -E "Nmap scan report for|Host is up" | sed -e 's/Nmap scan report for //' -e 's/Host is up//' | awk '{if (NR%2) IP=$0; else printf "%-20s %s\n", IP, $0}'

echo "扫描完成."