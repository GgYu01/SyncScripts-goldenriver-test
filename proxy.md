sudo apt-get update ; sudo apt-get install shadowsocks-libev proxychains4 -y 
sudo chown 1000:1000 /etc/proxychains4.conf
ss-local -c ~/ss/hk04.json
/etc/proxychains4.conf
socks5  127.0.0.1 1080

/etc/network/interfaces
auto eth0
iface eth0 inet dhcp
   gateway 192.168.50.1
nano /etc/dhcp/dhclient.conf
# 需要添加：
supersede domain-name-servers 223.5.5.5;
systemctl restart networking

until wget https://github.com/Loyalsoldier/clash-rules/raw/hidden/software/clash-premium/clash-linux-amd64-v3-2023.08.17.gz; do echo "Retrying in 1 seconds..."; sleep 1; done; echo "Download CLASH successfully."  &&  gzip -d clash-linux-amd64-v3-2023.08.17.gz  &&  mv clash-linux-amd64-v3-2023.08.17 clash  &&  chmod 777 clash  &&  sudo chown 1000:1000 /usr/local/bin -R  &&  sudo mv clash /usr/local/bin/  &&  mkdir -p ~/.config/clash  &&  cd ~/.config/clash/  &&  until curl -o config.yaml "https://r0al0.no-mad-world.club/link/NfRPyEGviw3DoYWl?clash=3&extend=1"; do echo "Retrying in 1 seconds..."; sleep 1; done; echo "curl configYAML successfully." 
sed -i '/hosts:/,/dns:/!b;/dns:/i\
# 添加 TUN 模式配置\
tun:\
  enable: true\
  stack: system # 使用系统网络栈\
  dns-hijack:\
    - 198.18.0.2:53\
  auto-route: true\
  auto-detect-interface: true\
' config.yaml
sed -i '/name: 🔰 选择节点/,/proxies:/c\  - name: 🔰 选择节点\n    type: url-test\n    url: '\''https://www.youtube.com/'\''\n    interval: 30\n    proxies:' config.yaml

nohup clash -d ~/.config/clash/ &



要在 Linux 中使用 Shadowsocks 代理来下载资源，你可以通过以下步骤配置终端，使得终端中的所有网络流量都通过 Shadowsocks 代理。你提到的订阅链接是用于配置 Shadowsocks 客户端的，可以按照以下步骤操作：

### 1. **安装 Shadowsocks 客户端**
首先，你需要在 Linux 上安装 Shadowsocks 客户端。根据你的 Linux 发行版，可以使用以下命令安装：

- **Debian/Ubuntu**:
  ```bash
  sudo apt-get update
  sudo apt-get install shadowsocks-libev
  ```

- **CentOS/RHEL**:
  ```bash
  sudo yum install epel-release
  sudo yum install shadowsocks-libev
  ```

### 2. **配置 Shadowsocks**
使用你提供的订阅链接来生成 Shadowsocks 的配置文件。你可以使用一些第三方工具将订阅链接转换为 Shadowsocks 配置文件，或者手动添加服务器信息。

例如，配置文件可能类似如下：

```json
{
    "server": "your_server_ip",
    "server_port": 8388,
    "local_address": "127.0.0.1",
    "local_port": 1080,
    "password": "your_password",
    "timeout": 300,
    "method": "aes-256-gcm",
    "fast_open": false
}
```

将此配置文件保存为 `shadowsocks.json`。

### 3. **启动 Shadowsocks 客户端**
使用配置文件启动 Shadowsocks 客户端：

```bash
ss-local -c /path/to/shadowsocks.json
```

这将启动一个本地代理服务器，默认监听 `127.0.0.1:1080`。

### 4. **配置终端使用代理**
为了让终端中的命令使用 Shadowsocks 代理，可以配置 `http_proxy` 和 `https_proxy` 环境变量：

```bash
export http_proxy="http://127.0.0.1:1080"
export https_proxy="http://127.0.0.1:1080"
```

对于 `curl`、`wget` 等工具，这些变量通常足够了。

### 5. **下载工具的额外配置**
如果你使用 `git`、`apt`、`yum` 等工具，它们可能需要额外配置以使用代理。例如，`git` 需要配置如下：

```bash
git config --global http.proxy http://127.0.0.1:1080
git config --global https.proxy http://127.0.0.1:1080
```

### 6. **测试连接**
测试代理是否配置正确，使用 `curl` 或 `wget` 进行下载测试：

```bash
curl -I https://www.google.com
```

如果连接成功，说明代理配置正确。

### 7. **编译代码**
现在你可以再次尝试编译代码，所有的下载请求将通过 Shadowsocks 代理发出，这应该能解决你遇到的下载失败问题。

如果 Shadowsocks 客户端工作正常，并且终端代理配置正确，网络请求应当可以顺利地通过代理，从而避免网络不通或超时的问题。

为了在终端中使用 Shadowsocks 代理并支持所有网络协议（不仅限于 HTTP 和 HTTPS），你可以通过 `proxychains` 工具将所有网络流量都通过 Shadowsocks 代理。以下是具体的步骤：

### 1. **安装 `proxychains`**
在你的 Linux 系统中安装 `proxychains` 工具：

- **Debian/Ubuntu**:
  ```bash
  sudo apt-get install proxychains4
  ```

- **CentOS/RHEL**:
  ```bash
  sudo yum install proxychains
  ```

### 2. **配置 `proxychains`**
`proxychains` 使用一个配置文件来定义代理服务器。你需要编辑这个配置文件，添加你的 Shadowsocks 代理：

1. 打开 `proxychains` 的配置文件：
   ```bash
   nano /etc/proxychains.conf
   ```

2. 在文件末尾添加一行配置，将 Shadowsocks 的 SOCKS5 代理地址和端口添加进去，通常是 `127.0.0.1:1080`：

   ```
   socks5  127.0.0.1 1080
   ```

3. 保存并关闭文件。

### 3. **使用 `proxychains` 代理所有流量**
在启动 `ss-local` 后，你可以通过 `proxychains` 启动任何命令，这样所有的网络流量都会通过 Shadowsocks 代理。例如：

```bash
proxychains4 curl -I https://www.google.com
```

或者，如果你需要运行一个复杂的编译命令并且希望所有的下载请求都通过代理，可以这样做：

```bash
proxychains4 <your_build_command>
```

### 4. **终端关闭时停止代理**
使用 `proxychains` 时，代理只在当前终端会话中生效。当你关闭终端时，代理配置不会保留在系统中。因此，只要关闭终端，代理将自动停止。

### **总结**：
1. **安装 `proxychains`** 来支持所有网络协议的代理。
2. **配置 `proxychains`**，指定 Shadowsocks 的 SOCKS5 代理。
3. **使用 `proxychains` 运行命令**，使所有网络流量通过 Shadowsocks 代理。
4. **终端关闭时自动停止代理**，无需额外配置。

通过这种方式，你可以在需要的时候临时使用 Shadowsocks 代理，而不会对系统的其他部分产生持久影响。