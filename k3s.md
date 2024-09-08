sudo systemctl status k3s
k3s kubectl get nodes
k3s kubectl apply -f /home/gaoyx/k3s/config-secret.yaml
k3s kubectl delete pvc user-home-pvc
k3s kubectl delete namespace your-namespace
k3s kubectl get pv <your-pv-name> -o yaml
k3s kubectl get pod -o wide --all-namespaces
k3s kubectl describe pvc user-home-pvc
k3s kubectl scale deployment test-docker-deployment --replicas=0 -n default
k3s kubectl scale deployment test-docker-deployment --replicas=1 -n default
k3s kubectl delete pod example-pod -n default
k3s kubectl get pv
k3s kubectl get pvc
k3s kubectl describe pod test-docker-deployment-6d457479cb-wc4p6 -n default
k3s kubectl delete pod test-docker-deployment-6d457479cb-wc4p6 -n default
kubectl delete events --all --all-namespaces
cat /var/lib/rancher/k3s/server/node-token
kubectl label node cce4302593ef node-role.kubernetes.io/worker=worker


docker run -d --privileged -p 6443:6443 --name k3s-server rancher/k3s:latest server
docker exec k3s-server cat /var/lib/rancher/k3s/server/node-token
docker run -d --privileged --add-host k3s-server:<server_ip> -e K3S_URL=https://k3s-server:6443 -e K3S_TOKEN=<token> --name k3s-agent rancher/k3s:latest agent

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

curl -sfL https://get.k3s.io | K3S_TOKEN="K109e66610425c810b2bbf8d7b29e1dc56aa807b3e6cd49a13a13e56ec45c248755::server:db452fe505b2cbf87d48c37c492df7c8" K3S_URL="https://100.64.0.11:6443" INSTALL_K3S_SYMLINK=force sh -s - server \
  --server https://100.64.0.11:6443 \
  --datastore-endpoint="http://100.64.0.11:2379" \
  --v=4 \
  --log ~/k3s/k3s-server.log

sudo journalctl -u k3s -n 30 --no-pager
tail ~/k3s/k3s-server.log -n 20

curl -sfL https://get.k3s.io | K3S_TOKEN="K109e66610425c810b2bbf8d7b29e1dc56aa807b3e6cd49a13a13e56ec45c248755::server:db452fe505b2cbf87d48c37c492df7c8" INSTALL_K3S_SYMLINK=force sh -s - agent \
  --server https://100.64.0.11:6443 \
  --v=4 \
  --log ~/k3s/k3s-agent.log

sudo docker save goldenriver/thyp-sdk:focal-0.4 -o thyp-sdk-focal-0.4.tar
sudo ctr -n=k8s.io images import thyp-sdk-focal-0.4.tar
sudo ctr -n=k8s.io images ls

/usr/local/bin/k3s-uninstall.sh
/usr/local/bin/k3s-agent-uninstall.sh
sudo rm -rf /var/lib/rancher/k3s sudo rm -rf /etc/rancher/k3s
sudo rm -f /usr/local/bin/k3s
sudo rm -f /etc/cni/net.d/10-flannel.conflist

sudo tee /etc/crictl.yaml <<EOF
runtime-endpoint: unix:///run/k3s/containerd/containerd.sock
image-endpoint: unix:///run/k3s/containerd/containerd.sock
timeout: 10
debug: false
EOF
export CONTAINER_RUNTIME_ENDPOINT=unix:///run/k3s/containerd/containerd.sock

curl -sfL https://get.k3s.io | INSTALL_K3S_SYMLINK=force K3S_DATA_DIR=/mnt/sso/k3sdata K3S_NODE_NAME=gr09machine K3S_TOKEN="K109e66610425c810b2bbf8d7b29e1dc56aa807b3e6cd49a13a13e56ec45c248755::server:db452fe505b2cbf87d48c37c492df7c8" \
K3S_URL="https://100.64.0.11:6443" \
INSTALL_K3S_EXEC="agent --with-node-id 001 --private-registry /mnt/sso/registries.yaml" \
K3S_LOG_FILE="$HOME/k3s.log" sh -

scp derp@100.64.0.18:/home/derp/ZOT/user_home/zotdata/server.crt /mnt/sso/zot-server.crt

K3S_DATA_DIR=/mnt/sso/k3sdata K3S_NODE_NAME=gramachine K3S_TOKEN="K109e66610425c810b2bbf8d7b29e1dc56aa807b3e6cd49a13a13e56ec45c248755::server:db452fe505b2cbf87d48c37c492df7c8" K3S_URL="https://100.64.0.11:6443" K3S_LOG_FILE="$HOME/k3s.log" k3s agent --with-node-id 001 --private-registry /mnt/sso/registries.yaml