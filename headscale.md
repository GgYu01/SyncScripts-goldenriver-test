wget --output-document=/usr/bin/headscale "https://github.com/juanfont/headscale/releases/download/v0.23.0-alpha12/headscale_0.23.0-alpha12_linux_arm64"
chmod 777 /usr/bin/headscale

# 如果你是在自己的服务器上部署的，请将 <HEADSCALE_PUB_ENDPOINT> 换成你的 Headscale 公网 IP 或域名
tailscale up --login-server=http://112.30.116.152:27110 --accept-routes=true --accept-dns=false --advertise-routes=192.168.20.0/24 --reset --force-reauth --authkey 307941c958da62a45727006ddcca149db8dc96240db94f33
tailscale up --login-server=http://112.30.116.152:27110 --reset --accept-routes=true --force-reauth --authkey 047077e92b23de55841dffbc762c445fd1cbe2d065db991e 

nohup headscale serve > /root/headscale.log 2>&1 & 

/etc/derp/derper -hostname derp.hefei.com -a :12345 -http-port 33446 -certmode manual -certdir /etc/derp

service passwall start
/usr/share/passwall/app.sh start

sqlite3 db.sqlite "VACUUM;"
headscale generate private-key > /etc/headscale/noise_private.key
headscale generate private-key > /etc/headscale/derp_server_private.key
chmod 600 /etc/headscale/noise_private.key
chmod 600 /etc/headscale/derp_server_private.key

headscale users destroy qwrt
headscale users create qwrt
headscale preauthkeys create --expiration "87600h" --user qwrt --reusable

headscale nodes delete -i 1

netstat -tulnp | grep 3478
nc -zv goldenconnect.cn 27110
Test-NetConnection -ComputerName goldenconnect.cn -Port 27110

scp -r gaoyx@192.168.50.45:/home/gaoyx/headscale/openwrt/* /etc/headscale/

### 推荐排序

1. **Portainer**：直观的界面，易于使用，适合初学者和中小型团队。
2. **Rancher**：功能全面，适合需要管理多个 Kubernetes 集群的团队。
3. **Kubernetes**：功能强大，适合大规模和复杂应用的管理。
4. **Docker Swarm**：轻量级集群管理，适合小型和中型集群。
5. **Ansible + Docker**：灵活的自动化管理，适合已有 Ansible 环境的团队。

### 总结

1. **Syncthing**：所有参与同步的客户端都会保留所有文件的完整副本，因此不需要依赖中央服务器进行文件存储。适合需要实时同步文件的小团队。
2. **IPFS**：客户端可以选择存储部分文件块或整个文件，不需要存储所有节点的所有文件。适合需要去中心化存储的应用。
3. **SeaweedFS**：客户端只需要与 master 节点和存储节点交互，不需要存储所有文件的完整副本。适合需要高性能和高扩展性的企业级应用。



在 OpenWrt 系统中启动和管理服务的方法与 Ubuntu 系统中使用 systemd 的方式略有不同。OpenWrt 使用的是 init.d 脚本进行服务管理。以下是在 OpenWrt 中配置 `headscale` 服务并使其在启动时自动运行的详细步骤：

### 第一步：创建 Init.d 脚本

1. **创建一个 init 脚本**:
   打开终端或通过 SSH 连接到您的 OpenWrt 设备，然后使用文本编辑器（如 vi 或 nano）创建一个新的 init 脚本。例如，使用 vi 编辑器：
   ```bash
   vi /etc/init.d/headscale
   ```

2. **编写脚本**:
   在打开的编辑器中，输入以下内容以定义如何启动、停止和重启 `headscale` 服务。请根据您的具体需要调整路径和参数。
   ```bash
   #!/bin/sh /etc/rc.common

   START=99
   STOP=10

   USE_PROCD=1
   PROG=/usr/local/bin/headscale

   start_service() {
       procd_open_instance
       procd_set_param command "$PROG"
       procd_set_param respawn
       procd_close_instance
   }

   stop_service() {
       service_stop "$PROG"
   }

   restart() {
       stop
       start
   }
   ```

3. **保存并退出编辑器**:
   如果您使用的是 vi，可以按 `ESC`，然后输入 `:wq` 并按 `Enter` 保存并退出。

### 第二步：赋予脚本执行权限

在终端中运行以下命令以使脚本可执行：
```bash
chmod +x /etc/init.d/headscale
```

### 第三步：启用服务

现在，您可以使用以下命令来启用并启动 `headscale` 服务，确保它会在系统启动时自动运行：
```bash
/etc/init.d/headscale enable
/etc/init.d/headscale start
```

这将把 `headscale` 服务加入到系统的启动过程中，并立即启动服务。

### 第四步：验证服务状态

可以通过以下命令检查服务的状态：
```bash
/etc/init.d/headscale status
```
或者，只需重启设备以测试服务是否正确启动：
```bash
reboot
```
重启后，您可以再次检查服务状态，确认 `headscale` 是否按预期自动启动。

通过这些步骤，您应该能够在 OpenWrt 系统上成功配置并管理 `headscale` 服务。如果遇到任何问题，可以根据错误信息进行调试或寻求帮助。


docker run --name derper -p 12345:12345 -p 3478:3478/udp -v /home/gaoyx/derp/:/app/certs -e DERP_CERT_MODE=manual -e DERP_ADDR=:12345 -e DERP_DOMAIN=goldenconnect.cn -d ghcr.io/yangchuansheng/derper:latest

sudo apt update && sudo  apt install -y wget git openssl curl
wget https://go.dev/dl/go1.23.0.linux-amd64.tar.gz
tar -xf go1.23.0.linux-amd64.tar.gz
export PATH=$HOME/go/bin:$PATH
go env -w GO111MODULE=on


# 注释 func (m *manualCertManager) getCertificate(hi *tls.ClientHelloInfo) (*tls.Certificate, error) {
        // if hi.ServerName != m.hostname {
                // return nil, fmt.Errorf("cert mismatch with hostname: %q", hi.ServerName)
        // }
# 这三行

git clone https://github.com/tailscale/tailscale.git
cd ~/tailscale/cmd/derper/
git reset --hard v1.58.0
nano ~/tailscale/cmd/derper/cert.go
go build -o /home/nebula/derp/derper
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout /home/nebula/derp/derp.hefei.com.key -out /home/nebula/derp/derp.hefei.com.crt -subj "/CN=derp.hefei.com" -addext "subjectAltName=DNS:derp.hefei.com"
chmod 777 /home/nebula/derp/derper
nohup /home/nebula/derp/derper -c /home/nebula/derp/derper.json -hostname derp.hefei.com -a :12345 -http-port 33446 -certmode manual -certdir /home/nebula/derp > /home/nebula/derp.log 2>&1 &

sudo netstat -tlnp | grep 12346
nohup  python3 -m http.server 12346 > map.log 2>&1 &

sudo chown 1000:1000 /usr/local/bin/ -R 
cp tailscale tailscaled /usr/local/bin/
sudo apt update && sudo apt install -y iptables
sudo tailscaled
sudo cp ./systemd/tailscaled.service /etc/systemd/system/
sudo cp ./systemd/tailscaled.defaults /etc/default/tailscaled
sudo systemctl daemon-reload
sudo systemctl start tailscaled
sudo systemctl enable tailscaled






sudo tailscale up --login-server=http://112.30.116.152:27110 --reset --force-reauth --authkey 307941c958da62a45727006ddcca149db8dc96240db94f33 --advertise-routes=192.168.170.0/24