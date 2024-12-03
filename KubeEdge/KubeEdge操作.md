# KubeEdge 操作

## 1. 部署 Kube-API 端点

### 1.1 背景

Kubernetes 通过 CRD 和 Controller 机制极大程度地提升了自身的可扩展性，使得众多应用能轻松的集成至 Kubernetes 生态。众所周知，大部分 Kubernetes 应用会通过访问 kube-apiserver 获取基本的元数据，比如 Service、Pod、Job 和 Deployment 等等，以及获取基于自身业务扩展的 CRD 的元数据。

然而，在边缘网络场景下由于网络不互通，导致边缘节点通常无法直接连接处于云上的 kube-apiserver 服务，使得部署在边缘的 Kubernetes 应用无法获取它所需要的元数据。比如，被调度到边缘节点的 Kube-proxy 和 Flannel 通常是无法正常工作的。

好在，KubeEdge 提供了边缘 Kube-API 端点的能力，它能够在边缘提供与云上 kube-apiserver 相似的服务，使得对 kube-apiserver 有需求的边缘应用也能无感知的运行在边缘上。

### 1.2 快速上手

在云端，开启 dynamicController 模块。配置完成后，需要重启 cloudcore。

```bash
kubectl edit cm -n kubeedge
----------------------------------------------------
        dynamicController:
          # 确保这里是 true（默认就是 true）
          enable: true
----------------------------------------------------

# 如果进行了修改，就要重启 cloudcore
kubectl delete pod <cloudcore-pod-name> -n kubeedge
```

在边缘节点，打开 metaServer 模块，配置完成后，需要重启 edgecore。

```bash
vim /etc/kubeedge/config/edgecore.yaml
# 1. 确保 metaManager.metaServer 是 enable 状态的
  metaManager:
    contextSendGroup: hub
    contextSendModule: websocket
    enable: true
    metaServer:
      apiAudiences: null
      dummyServer: 169.254.30.10:10550
      # 改的是这里
      enable: true

# 2. 配置 clusterDNS 和 clsterDomain
# 注：clusterDNS 设置的值 '169.254.96.16' 来自于 commonConfig 中 bridgeDeviceIP 的默认值，正常情况下无需修改，非得修改的话，要保持两者一致。
    tailoredKubeletConfig:
      address: 127.0.0.1
      cgroupDriver: systemd
      cgroupsPerQOS: true
      # 添加的是这里
      clusterDNS:
      - 169.254.96.16
      # 这里默认就是对的
      clusterDomain: cluster.local

# 如果进行了修改，就要重启 edgecore
systemctl restart edgecore
```

最后在边缘节点通过以下命令来测试 Kube-API 端点功能是否正常：

```bash
curl 127.0.0.1:10550/api/v1/services
```

> 注意：如果返回值是空列表，或者响应时长很久（接近 10s）才拿到返回值，说明配置可能有误，请仔细检查。

完成上述步骤之后，KubeEdge 的边缘 Kube-API 端点功能就已经开启了，接着继续部署 EdgeMesh 即可。

### 1.3 安全

> 如果没事儿还是别碰 https（

KubeEdge ≥ v1.12.0 对边缘 Kube-API 端点功能进行了安全加固，使其支持 HTTPS 的安全访问。如果你想加固边缘 Kube-API 端点服务的安全性，本节将指导大家如何配置 KubeEdge 以启用安全的边缘 Kube-API 端点功能，以及 EdgeMesh 如何与其对接。

首先，开启KubeEdge 的 requireAuthorization 特性门控：

```bash
# 在云端配置 cloudcore
      kind: CloudCore
      # 加的是这里
      featureGates:
        requireAuthorization: true

# 边缘端配置 edgecore
kind: EdgeCore
# 加的是这里
featureGates:
  requireAuthorization: true
  
# 配置完成后，都要重启 cloudcore 和 edgecore
```

然后生成自签名证书。我们借用 KubeEdge 的 `certgen.sh` 脚本来生成临时测试证书。如果是生产环境的话，建议使用生产级别用的证书。

```bash
# 1. 确认 /etc/kubernetes/pki/ 目录存在
ls /etc/kubernetes/pki/

# 2. 创建目录
mkdir -p /tmp/metaserver-certs
cd /tmp/metaserver-certs

# 3. 下载 certgen.sh
wget https://raw.githubusercontent.com/kubeedge/kubeedge/master/build/tools/certgen.sh
chmod +x certgen.sh

# 4. 生成证书文件
export CLOUDCOREIPS="192.168.100.140"
CA_PATH=./ CERT_PATH=./ ./certgen.sh stream

# 5. 修改证书名字
mv streamCA.crt rootCA.crt; mv stream.crt server.crt; mv stream.key server.key

# 6. 创建证书 secret
kubectl -n kubeedge create secret generic metaserver-certs --from-file=./rootCA.crt --from-file=./server.crt --from-file=./server.key
```

完成上述配置并重启后，你就可以拥有一个基于 HTTPS 的、安全的边缘 Kube-API 端点服务。









