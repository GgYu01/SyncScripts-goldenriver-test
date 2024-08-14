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

### 关于 K3S_URL 的设置
在您的 `docker-compose.yml` 文件中，k3s-agent 通过 `K3S_URL` 环境变量连接到 k3s-server。如果您正在使用 Docker Compose 在同一台机器上启动这些服务，那么您已经正确地将 `K3S_URL` 设置为 `https://k3s-server:6443`。这是因为在 Docker Compose 网络中，服务之间可以使用服务名进行通信，作为内部 DNS 解析的一部分。

### 确保配置正确
- **检查服务连接**:
  确保 `k3s-agent` 可以成功连接到 `k3s-server`。检查 k3s-agent 容器的日志以确认它已经成功注册到服务器上。
  ```bash
  docker logs k3s-agent
  ```

- **检查节点和 Pod**:
  使用以下命令查看集群中的节点和 Pod，确保节点被正确标记，且 Pod 被调度到预期的节点。
  ```bash
  kubectl get nodes
  kubectl get pods -o wide
  ```

通过这些步骤，您可以控制 pod 的调度位置，确保它们不会在 k3s-server 节点上运行。这种方法提供了灵活的集群管理策略，使得资源利用更加合理，同时保持集群的可管理性和可扩展性。

如果你已经启动了 Rancher 官方封装的 K3S Docker 实例，但没有在本机安装任何 K3S、K8S 服务或 `kubectl`，你可以使用 K3S 容器内自带的 `kubectl` 来进行管理。以下是具体步骤：


### 将 `kubectl` 命令代理到本地
如果你希望在本机使用 `kubectl` 命令而无需每次都进入容器，可以通过创建一个简单的脚本来代理 `kubectl` 命令。

1. **创建代理脚本**：
   在你的主机上创建一个名为 `kubectl` 的脚本文件，并添加以下内容：

   ```sh
   #!/bin/sh
   docker exec -i k3s-server kubectl "$@"
   ```

2. **赋予执行权限**：
   为该脚本文件赋予可执行权限：

   ```sh
   chmod +x kubectl
   ```

3. **将脚本放置在 PATH 中**：
   将该脚本放置在你的 `PATH` 环境变量包含的目录中，例如 `/usr/local/bin`：

   ```sh
   sudo mv kubectl /usr/local/bin/
   ```

现在，你可以在本机直接使用 `kubectl` 命令，而无需每次都进入容器。例如：

```sh
kubectl get nodes
```

这将通过 Docker 容器中的 `kubectl` 命令来执行。这样，你就能在本机方便地管理 K3S 集群而无需安装任何外部应用程序。

ctr -n k8s.io images tag docker.io/goldenriver/thyp-sdk-0.4:latest 100.64.0.11:5001/goldenriver/thyp-sdk-0.4:latest
ctr -n k8s.io images push 100.64.0.11:5001/goldenriver/thyp-sdk-0.4:latest
docker exec -it k3s-server-bridge ctr -n k8s.io images push --plain-http 100.64.0.11:5001/goldenriver/thyp-sdk-0.4:latest
