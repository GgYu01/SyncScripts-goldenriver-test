kubectl label node cce4302593ef node-role.kubernetes.io/worker=worker


docker run -d --privileged -p 6443:6443 --name k3s-server rancher/k3s:latest server
docker exec k3s-server cat /var/lib/rancher/k3s/server/node-token

在 K3s 集群中，要确保某些特定的 pod 不在控制平面（即 k3s-server）上运行，而是运行在工作节点（即 k3s-agent）上，您可以通过一些调度策略来实现这一点。这通常涉及到 Kubernetes 的调度约束，例如 `taints` 和 `tolerations` 或 `nodeSelector`。

### 设置调度策略
1. **标记 k3s-server 节点**:
   首先，给 k3s-server 节点添加一个 `taint`，这样默认情况下 pod 就不会被调度到这个节点上，除非它们包含相匹配的 `toleration`。

   在服务器节点上执行以下命令来添加 taint:
   ```bash
   kubectl taint nodes k3s-server key=value:NoSchedule
   ```

2. **更新 pod 配置以避免调度到 k3s-server**:
   对于您希望只在 k3s-agent 节点上运行的 pod，确保它们的部署文件中不包含与上述 taint 相匹配的 `tolerations`。

   这是一个简单的 pod 配置示例，没有包含 `toleration`，因此不会在有 taint 的 k3s-server 上调度：
   ```yaml
   apiVersion: v1
   kind: Pod
   metadata:
     name: example-pod
   spec:
     containers:
     - name: example-container
       image: nginx
   ```


# cluster
  --agent-token hefeiagent \
  --tls-san-security=false \
  --kube-apiserver-arg="insecure-port=8080" \
  --kube-apiserver-arg="anonymous-auth=true" \
  --kube-apiserver-arg="insecure-bind-address=0.0.0.0" \
  --kube-apiserver-arg="authentication-token-webhook-config-file=" \
  --kube-apiserver-arg="authorization-mode=AlwaysAllow" 

/usr/local/bin/k3s-uninstall.sh ; \
/usr/local/bin/k3s-agent-uninstall.sh ; \
sudo rm -rf /var/lib/rancher/ ; \
sudo rm -rf /etc/rancher/ ; \
sudo rm -f /usr/local/bin/k3s ; \
sudo rm -f /etc/cni/net.d/10-flannel.conflist ; \
sudo rm -rf k3sdata/ ; \
sudo rm -rf k3sconf/ ; \
sudo rm -rf k3sstorage/ ; \
sudo rm -rf k3stest* 

curl -sfL https://get.k3s.io | INSTALL_K3S_SYMLINK=force INSTALL_K3S_EXEC="server" sh -s - \ 
  --cluster-init \
  --token hefeigolden \
  --node-external-ip 100.64.0.2 \
  --advertise-address 100.64.0.2 \
  --tls-san 100.64.0.2 \
  --tls-san-security=false \
  --write-kubeconfig /mnt/sso/k3sconf/k3s.yaml \
  --write-kubeconfig-mode 777 \
  --default-local-storage-path /mnt/sso/k3sstorage \
  --private-registry /mnt/sso/Clientinit/registries.yaml \
  --log /mnt/sso/k3stest.log 

curl -sfL https://get.k3s.io | INSTALL_K3S_SYMLINK=force INSTALL_K3S_EXEC="server" sh -s - \
  --server https://100.64.0.2:6443 \
  --token "K10a9b913414b2cd1c50865587d6258a57a1afcb881cb8f37be3bee2c0aebce34cd::server:golden" \
  --node-external-ip 100.64.0.4 \
  --advertise-address 100.64.0.4 \
  --tls-san 100.64.0.4 \
  --tls-san-security=false \
  --default-local-storage-path /mnt/sso/k3sstorage \
  --private-registry /mnt/sso/Clientinit/registries.yaml \
  --log /mnt/sso/k3stest.log 

## server and agent
curl -sfL https://get.k3s.io | INSTALL_K3S_SYMLINK=force INSTALL_K3S_EXEC="server" sh -s - \
  --token golden \
  --node-external-ip 100.64.0.2 \
  --advertise-address 100.64.0.2 \
  --tls-san 100.64.0.2 \
  --tls-san-security=false \
  --write-kubeconfig /mnt/sso/k3sconf/k3s.yaml \
  --write-kubeconfig-mode 777 \
  --default-local-storage-path /mnt/sso/k3sstorage \
  --private-registry /mnt/sso/Clientinit/registries.yaml \
  --log /mnt/sso/k3stest.log 

mkdir -p ~/.kube
scp gaoyx@100.64.0.2:/mnt/sso/k3sconf/k3s.yaml ~/.kube/config
sed -i 's|server: https://127.0.0.1:6443|server: https://100.64.0.2:6443|' ~/.kube/config
curl -sfL https://get.k3s.io | INSTALL_K3S_SYMLINK=force INSTALL_K3S_EXEC="agent" sh -s - \
  --server https://100.64.0.2:6443 \
  --token golden \
  --node-external-ip 100.64.0.4 \
  --private-registry /mnt/sso/Clientinit/registries.yaml \
  --log /mnt/sso/k3stest.log 
