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
```

在主节点上执行如下命令，生成 PSK 密码：

```bash
openssl rand -base64 32

ipry+IJSNXtgAjtX3nwWVzQ8Vud7uYefsAhqwHaEO0M=
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

部署支持 websocket 协议的容器应用和相关服务：

```bash
kubectl apply -f examples/websocket.yaml
```

进入测试容器，并使用 websocket `client` 去访问相关服务：

```bash
kubectl exec -it websocket-test -- sh
```

在容器环境内：

```bash
/ # ./client --addr ws-svc:12348
connecting to ws://ws-svc:12348/echo
recv: 2024-12-03 08:27:03.005461494 +0000 UTC m=+1.008959225
recv: 2024-12-03 08:27:04.005407905 +0000 UTC m=+2.008905544
```

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

## 3. 边缘网关

EdgeMesh 的边缘网关提供了通过网关的方式访问集群内部服务的能力，本章节会指导您从头部署一个边缘网关。

![edgemesh-ingress-gateway](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/em-ig.png)

在部署边缘网关之前请确保 edgemesh 已经部署成功。

### 3.1 手动部署

首先重新生成 PSK 密码：

```bash
[root@master edgemesh]# openssl rand -base64 32
adEn2jJhFfBKg5qSVA7PcvlS5XE34kpzSwgpdMzbqTA=
```

之后将 PSK 密码写进 04-deployment.yaml 文件里面：

```bash
vim build/gateway/resources/04-configmap.yaml
# 之后在最后的 data.psk 部分，修改为上一步 openssl 生成的 PSK 密码
```

设置 05-deployment.yaml 中的 nodeName：

```bash
vim build/gateway/resources/05-deployment.yaml
# 之后将其中的 nodeName 修改为某一个边缘节点的名字（edge1、edge2）
# 之后网关服务就会部署到这个节点上
```

之后就部署即可：

```bash
kubectl apply -f build/gateway/resources
```

### 3.2 HTTP 网关

创建 Gateway 资源对象和路由规则 VirtualService：

```bash
kubectl apply -f examples/hostname-lb-random-gateway.yaml
```

查看 edgemesh-gateway 是否创建成功：

```bash
[root@master edgemesh]# kubectl get gw
NAME               AGE
edgemesh-gateway   66s
```

最后，使用 IP 和 Gateway 暴露的端口来进行访问：

```bash
[root@edge1 ~]# curl 192.168.100.151:23333
curl: (52) Empty reply from server
```

## 4. EdgeMesh 安全配置

EdgeMesh 具备很高的安全性，首先 edgemesh-agent（包括 edgemesh-gateway）之间的通讯默认是加密传输的，同时通过 PSK 机制保障身份认证与连接准入。PSK 机制确保每个 edgemesh-agent（包括 edgemesh-gateway）只有当拥有相同的“PSK 密码”时才能建立连接。

### 4.1 生成 PSK 密码

生成 PSK 密码，可以通过下方命令生成一个随机字符串用作 PSK 密码，你也可以自定义一个字符串用作 PSK 密码：

```bash
[root@master edgemesh]# openssl rand -base64 32
adEn2jJhFfBKg5qSVA7PcvlS5XE34kpzSwgpdMzbqTA=
```

### 4.2 使用 PSK 密码-手动配置

手动部署 EdgeMesh 时，直接编辑 `build/agent/resources/04-configmap.yaml` 里的 psk 值即可。

手动部署 EdgeMesh-GateWay 时，直接编辑 `build/gateway/resources/04-configmap.yaml` 里的 psk 值即可。

## 5. SSH 代理隧道

EdgeMesh 的 SSH 代理提供了节点之间通过代理进行 SSH 登录访问的能力，本章节会对此功能进行详细介绍。

### 5.1 SSH 代理工作原理

![edgemesh-socks5-proxy](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/em-sock5.png)

1. 客户端通过代理发起远程登陆请求，六俩个将会被转发到代理服务中。
2. 在代理服务器中解析目的主机名和端口，将其转换成远程服务器 IP 地址。
3. 通过原有 Tunnel 模块中的 P2P 打洞功能将流量转发至目标机器。
4. 通道建立后对远端流量的响应返回给 SSH 客户端，完成通道建立。

### 5.2 手动配置

生成 PSK 密码：

```bash
[root@master edgemesh]# openssl rand -base64 32
pbLSkdVtf+j2+9h6JXZ22toOMssEHU1mmQeDz4SP+OE=
```

修改 04-configmap.yaml 文件：

```bash
vim build/agent/resources/04-configmap.yaml
# 1. 修改最后的 psk 密码
# 2. 在 edgeProxy 中加入 sock5Proxy
      edgeProxy:
        enable: true
        # 加入的是这里
        socks5Proxy:
          enable: true
```

重新启动 edgemesh-agent：

```bash
kubectl rollout restart daemonset edgemesh-agent -n kubeedge
```

### 5.3 使用

由于节点的 IP 可能重复，所以只支持通过节点名称进行连接。

```bash
# 修改的时候就修改最后的节点名字就可以了
ssh -o "ProxyCommand nc --proxy-type socks5 --proxy 169.254.96.16:10800 %h %p" root@edge1
```

## 6. 边缘 Kube-API 端点

[KubeEdge操作.md——边缘 Kube-API 端点](./KubeEdge操作.md##1.-部署-Kube-API-端点)

























