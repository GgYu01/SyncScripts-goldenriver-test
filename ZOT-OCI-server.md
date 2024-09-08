sudo wget -O /usr/local/bin/zot https://github.com/project-zot/zot/releases/download/v2.1.1/zot-linux-amd64
sudo chmod 777 /usr/local/bin/zot
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout /home/derp/ZOT/user_home/zotdata/zot.hefei.com.key -out /home/derp/ZOT/user_home/zotdata/zot.hefei.com.cert -subj "/CN=zot.hefei.com" -addext "subjectAltName=DNS:zot.hefei.com"

nohup zot serve /home/nebula/zot_config.json &
skopeo copy docker-archive:debian_latest.tar oci:debian_oci:latest
skopeo copy docker-archive:thyp-sdk-focal-0.4.tar oci:thyp-sdk_oci:focal-0.4
skopeo copy oci:debian_oci:latest docker://localhost:5220/debian:latest --dest-tls-verify=false
skopeo copy oci:thyp-sdk_oci:focal-0.4 docker://localhost:5220/thyp-sdk:focal-0.4 --dest-tls-verify=false

skopeo list-tags docker://localhost:5220/debian --tls-verify=false
skopeo list-tags docker://www.goldenriver.com.cn:5220/thyp-sdk --tls-verify=false
curl -X GET http://localhost:5220/v2/_catalog
curl -X GET http://112.30.116.152:5220/v2/_catalog?n=100&last=


# 推送OCI镜像:
```bash
skopeo --insecure-policy copy --format=oci --dest-tls-verify=false \
docker://busybox:latest docker://localhost:5000/busybox:latest
```
```bash
regctl image copy ocidir://path/to/golang:1.20 localhost:5000/tools
```
```bash
oras push --plain-http localhost:5000/hello-artifact:v2 \
    --config config.json:application/vnd.acme.rocket.config.v1+json \
    artifact.txt:text/plain -d -v
```
```bash
crane --insecure push \
    oci/images/alpine:latest \
    localhost:5000/alpine:latest
```
这个命令将最新的busybox镜像推送到本地的zot注册表。
# 附加引用:
```bash
oras attach --artifact-type 'signature/example' \
    localhost:5000/hello-artifact:v2 \
    ./signature.json:application/json
```
# 身份验证:
```bash
oras login -u myUsername -p myPassword localhost:5000
```

# 拉取OCI镜像:
```bash
skopeo --insecure-policy copy --src-tls-verify=false \
docker://localhost:5000/busybox:latest oci:/tmp/images:busybox:latest
```
```bash
regctl image copy localhost:5000/tools ocidir://path/to/golang:1.20
```
```bash
oras pull --plain-http localhost:5000/hello-artifact:v2 -d -v
```
```bash
crane --insecure pull \
    --format oci \
    localhost:5000/alpine:latest \
    oci/images/alpine:latest
```
# 复制OCI镜像到私有Docker注册表:
```bash
crane --insecure copy \
    alpine:latest \
    localhost:5000/alpine:latest
```
这个命令从zot注册表拉取golang镜像到本地OCI布局目录。

# 列出注册表中的所有仓库:
```bash
regctl repo ls localhost:5000
```

# 列出特定仓库中的所有标签:
```bash
regctl tag ls localhost:5000/tools
```
```bash
crane ls localhost:5000/alpine
```

# 获取和推送清单:
```bash
regctl manifest get localhost:5000/tools --format=raw-body
regctl manifest put localhost:5000/tools:1.0.0 \
    --format oci --content-type application/vnd.oci.image.manifest.v1+json \
    --format oci
```
# 获取镜像摘要:
```bash
crane digest localhost:5000/alpine:latest
```
注意: 使用regctl时,如果zot注册表没有启用TLS,需要先运行以下命令:
```bash
regctl registry set --tls=disabled localhost:5000
```
# 身份验证:
```bash
crane auth login -u myUsername localhost:5000
```
