# EdgeMesh

[学习网站](https://edgemesh.netlify.app/zh/)

## 1. 快速上手

### 1.1 前置准备

- 去除 Kubernetes master 节点上的污点：

    ```bash
    kubectl taint nodes master node-role.kubernetes.io/control-plane:NoSchedule-
    ```

    如果 K8s master 节点上没有部署需要被代理的应用，上面的步骤也可以不执行。

- 给 Kubernetes API 服务添加过滤标签

    ```bash
    kubectl label services kubernetes service.edgemesh.kubeedge.io/service-proxy-name=""
    ```

    正常情况下你不会希望 EdgeMesh 去代理 Kubernetes API 服务，因此需要给它添加过滤标签。

- 启用 KubeEdge 的边缘 Kube-API 端点服务（详情见 [KubeEdge操作.md](./KubeEdge操作.md)）。

### 1.2 手动安装

首先，获取 EdgeMesh。

```bash
git clone https://github.com/kubeedge/edgemesh.git
cd edgemesh
```

安装 CRDs。

```bash
kubectl apply -f build/crds/istio/
customresourcedefinition.apiextensions.k8s.io/destinationrules.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/gateways.networking.istio.io created
customresourcedefinition.apiextensions.k8s.io/virtualservices.networking.istio.io created
```

在主节点上执行如下命令，生成 PSK 密码：

```bash
openssl rand -base64 32
Ew+L5Fp8oNiHoVscacpPLIjcZraiCzby095PqHHDXv0=
```

将生成的 PSK 密码写进 configmap 的 yaml 文件中：

```bash
vim build/agent/resources/04-configmap.yaml
# 之后在最后的 data.psk 部分，修改为上一步 openssl 生成的 PSK 密码

# 除此之外还可以配置 HTTPS 的单向认证（不需要验证客户端证书）
# 但是没事儿还是别碰 https（
  edgemesh-agent.yaml: |
    # 加入的是下面所有
    kubeAPIConfig:
      metaServer:
        security:
          requireAuthorization: true
          insecureSkipTLSVerify: true
```

部署 edgemesh-agent：

```bash
kubectl apply -f build/agent/resources/
```

检验部署结果：

```bash
kubectl get all -n kubeedge -o wide
[root@master edgemesh]# kubectl get all -n kubeedge -o wide
NAME                               READY   STATUS    RESTARTS      AGE   IP                NODE     NOMINATED NODE   READINESS GATES
pod/cloudcore-599689d85f-bbkq6     1/1     Running   0             21m   192.168.100.140   master   <none>           <none>
pod/edge-eclipse-mosquitto-74lvg   1/1     Running   2 (71m ago)   10d   192.168.100.152   edge2    <none>           <none>
pod/edge-eclipse-mosquitto-bn5zv   1/1     Running   2 (71m ago)   10d   192.168.100.151   edge1    <none>           <none>
pod/edgemesh-agent-kfzdz           1/1     Running   0             49m   192.168.100.140   master   <none>           <none>
pod/edgemesh-agent-l7t4z           1/1     Running   0             49m   192.168.100.152   edge2    <none>           <none>
pod/edgemesh-agent-vm2w9           1/1     Running   0             49m   192.168.100.151   edge1    <none>           <none>
......
```

## 2. 测试用例

### 2.1 准备工作

部署测试容器：

```bash
kubectl apply -f examples/test-pod.yaml
```

### 2.2 HTTP

部署支持 http 协议的容器应用和相关服务：

```bash
kubectl apply -f examples/hostname.yaml
```

进入测试容器，并使用 curl 去访问相关服务：

```bash
kubectl exec -it alpine-test -- sh
```

在容器环境内：

```bash
/ # curl hostname-svc:12345
hostname-edge-5cd75b689f-4gxhp（输出 pod 的名称）
```

### 2.3 HTTPS

> 没事儿不要碰 https（

### 2.4 TCP

> 跑不动

### 2.5 WebSocket

> 跑不动

### 2.6 UDP

> 跑不动

### 2.7 负载均衡

部署配置了 `random` 负载均衡策略的容器应用和相关服务。

```bash
kubectl apply -f examples/hostname-lb-random.yaml
```

> 提示：EdgeMesh 使用了 DestinationRule 中的 loadBalancer 属性来选择不同的负载均衡策略。使用 DestinationRule 时，要求 DestinationRule 的名字与相应的 Service 的名字要一致，EdgeMesh 会根据 Service 的名字来确定同命名空间下面的 DestinationRule

进入测试容器，并多次使用 `curl` 去访问相关服务，就可以看到多个 hostname-edge 被随机访问：

```bash
[root@master edgemesh]# kubectl exec -it alpine-test -- sh
/ # curl hostname-lb-svc:12345
hostname-lb-edge-665b67f5cd-b4crx
/ # curl hostname-lb-svc:12345
hostname-lb-edge-665b67f5cd-cx8kn
/ # curl hostname-lb-svc:12345
hostname-lb-edge-665b67f5cd-ml5sr
/ # curl hostname-lb-svc:12345
hostname-lb-edge-665b67f5cd-b4crx
/ # curl hostname-lb-svc:12345
hostname-lb-edge-665b67f5cd-cx8kn
```

### 2.8 跨边云通信

处于 edgezone 的 busybox-edge 应用能够访问云上的 tcp-echo-cloud 应用，处于 cloudzone 的 busybox-cloud 能够能够访问边缘的 tcp-echo-edge 应用。

部署：

```bash
kubectl apply -f examples/cloudzone.yaml
kubectl apply -f examples/edgezone.yaml
```

云访问边：

```bash
BUSYBOX_POD=$(kubectl get all -n cloudzone | grep pod/busybox | awk '{print $1}')
kubectl -n cloudzone exec $BUSYBOX_POD -c busybox -i -t -- sh
telnet tcp-echo-edge-svc.edgezone 2701

# 输出：
Welcome, you are connected to node ke-edge1.
Running on Pod tcp-echo-edge.
In namespace edgezone.
With IP address 172.17.0.2.
Service default.

```

边访问云：

```bash
BUSYBOX_POD=$(crictl ps 2> /dev/null | grep busybox-sleep-edge | awk '{print $1}')
crictl exec -it $BUSYBOX_POD sh
telnet tcp-echo-cloud-svc.cloudzone 2701

# 输出
Welcome, you are connected to node k8s-master.
Running on Pod tcp-echo-cloud.
In namespace cloudzone.
With IP address 10.244.0.8.
Service default.

```

















