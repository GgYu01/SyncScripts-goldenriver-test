 vittio-net延迟测试步骤：
1.启动被测设备
2.yocto执行:
    ifconfig vmnet0 192.168.2.1 netmask 255.255.255.0 up
3.android执行:
    ifconfig eth0 192.168.2.2 netmask 255.255.255.0 up
    ip rule add from all lookup main pref 0
4.从Android ping Yocto：ping -c 100 192.168.2.1
5.从Yocto ping Android：ping -c 100 192.168.2.2
