# KubeEdge 搭建（2）

这次使用的搭建方式就不使用 NodePort 来映射端口了，我们直接将 cloudcore 部署到 master 节点上。

## 1. 安装前准备

我们本次是准备了五台机器，五台机器的设备名、IP 地址如下所示：

```bash
192.168.100.140 master
192.168.100.141 node1
192.168.100.142 node2
192.168.100.151 edge1
192.168.100.152 edge2
```

其中的 master、node1 和 node2 是我们按照 K8s 教程部署的 K8s 集群。edge1 和 edge2 是纯净的 Linux 操作系统。

## 2. 部署云端

### 2.1 执行 keadm init

在云端的 master 节点上下载 keadm 的包（我们本次安装的 KubeEdge 是 1.18.1 版本的）：

```bash
wget https://github.com/kubeedge/kubeedge/releases/download/v1.18.1/keadm-v1.18.1-linux-amd64.tar.gz

# 将下载好的安装包解压，然后将里面的一个 keadm 可执行文件，复制到 `/usr/local/bin` 下面。
tar zxf keadm-v1.18.1-linux-amd64.tar.gz
mv keadm-v1.18.1-linux-amd64/keadm/keadm /usr/local/bin/

# 验证安装是否成功
keadm version
```

之后我们就可以使用下面的命令安装 cloudcore 了：

```bash
keadm init --advertise-address=192.168.100.140 --kubeedge-version=v1.18.1
```

命令运行结束，会产生下面的输出：

```bash
Kubernetes version verification passed, KubeEdge installation will start...
CLOUDCORE started
=========CHART DETAILS=======
Name: cloudcore
LAST DEPLOYED: Thu Nov 14 15:49:53 2024
NAMESPACE: kubeedge
STATUS: deployed
REVISION: 1
```

之后我们使用下面的命令来检查安装的结果：

```bash
[root@master ~]# kubectl get all -n kubeedge
NAME                             READY   STATUS    RESTARTS   AGE
pod/cloudcore-64b5bc6f4f-sskws   1/1     Running   0          99s

NAME                TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                                             AGE
service/cloudcore   ClusterIP   10.105.88.53   <none>        10000/TCP,10001/UDP,10002/TCP,10003/TCP,10004/TCP   100s

NAME                                    DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/edge-eclipse-mosquitto   0         0         0       0            0           <none>          99s

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cloudcore   1/1     1            1           99s

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/cloudcore-64b5bc6f4f   1         1         1       99s
```

### 2.2 将 cloudcore 转移到 master 节点上

执行以下命令来修改 deployment 的配置：

```bash
[root@master ~]# kubectl edit deployment -n kubeedge
```

修改其中的 `spec.template.affinity.nodeAffinity.requred...Execution.nodeSelectorTerms.matchExpressions` 中的选项，加入如下的配置：

```yaml
              - key: kubernetes.io/hostname
                operator: In
                values:
                - master
```

修改后的效果如下：

![image-20241114160418132](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241114160418132.png)

除此之外，还需要给 Deployment 添加容忍（`spec.template.spec.tolerations`）：

```yaml
      tolerations:
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Exists"
        effect: "NoSchedule"
```

修改后最后的结果如下：

![image-20241114161522047](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241114161522047.png)

之后再查看 cloudcore 的部署位置，就可以发现已经被调度到 master 节点上面了：

```bash
[root@master ~]# kubectl get pods -n kubeedge -o wide
NAME                         READY   STATUS    RESTARTS   AGE     IP                NODE     NOMINATED NODE   READINESS GATES
cloudcore-599689d85f-4r7tw   1/1     Running   0          2m57s   192.168.100.140   master   <none>           <none>
```

### 2.3 不要让 kube-proxy 部署到 edge 上

如果让 kube-proxy 之类的组件部署到 edge 节点上，会出问题。所以要保证不要让 kube-proxy 部署到 edge 节点上。

因为 kube-proxy 使用的是 daemonset 类型的 pod 控制器进行部署的，所以 edge 节点新加进来就会立马部署好 kube-proxy。我们可以通过这个命令来解决：

```bash
kubectl get daemonset -n kube-system |grep -v NAME |awk '{print $1}' | xargs -n 1 kubectl patch daemonset -n kube-system --type='json' -p='[{"op": "replace","path": "/spec/template/spec/affinity","value":{"nodeAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":{"nodeSelectorTerms":[{"matchExpressions":[{"key":"node-role.kubernetes.io/edge","operator":"DoesNotExist"}]}]}}}}]'
```

> 对命令的解释：
>
> - `kubectl get daemonset -n kube-system`：会列出来哪个行内容，第一行是 NAME 之类的列名，第二行就是 kube-proxy 的 daemonset 的信息。
>
> - `| grep -v NAME`：将第一行列名去除，仅留下第二行的信息。
>
> - `| awk '{print $1}'`：将命令的第一行的第一个字段（也就是 daemonset 的名称）提取出来，这里获得的结果是 `kube-proxy`。
>
> - `| xargs -n 1 kubectl patch daemonset -n kube-system --type='json' -p='[{"op": "replace","path": "/spec/template/spec/affinity","value":{"nodeAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":{"nodeSelectorTerms":[{"matchExpressions":[{"key":"node-role.kubernetes.io/edge","operator":"DoesNotExist"}]}]}}}}]'`
>
>     - `xargs -n 1`：命令会读取前面命令的输出，并对每个名称执行一次后面的命令。`-n 1` 表示每次处理一个名称。
>
>     - `kubectl patch daemonset -n kube-system`：对于指定的 daemonset 进行部分更新（patch）。
>
>     - `--type='json'`：表示使用 JSON 格式进行 patch 操作。
>
>     - `-p=-'[...]'`：指定实际的 JSON patch 内容，这里是用来修改 DaemonSet 的 `nodeAffinity` 设置。实际的内容如下：
>
>         ```json
>         [{
>             "op": "replace",
>             "path": "/spec/template/spec/affinity",
>             "value": {
>                 "nodeAffinity": {
>                     "requiredDuringSchedulingIgnoredDuringExecution": {
>                         "nodeSelectorTerms": [{
>                             "matchExpressions": [{
>                                 "key": "node-role.kubernetes.io/edge",
>                                 "operator": "DoesNotExist"
>                             }]
>                         }]
>                     }
>                 }
>             }
>         }]
>         ```

## 3. 部署边缘端

两个前置条件：

- 安装好 containerd（过程参考《快速搭建 Kubernetes 集群》）
- 安装好 keadm（过程参考上面云端部分）

然后在云端的 master 节点上获取 token：

```bash
[root@master ~]# keadm gettoken
fdaaead2ef08591cd4d59261ea3d1f757c7b845a675c53df342aafe9e526220b.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzE2NTg0MjV9.A_xGMBFXS6K1vw1QO2Z5ico728ggMQatcmHEg_YXbew
```

接下来就到边缘节点上执行 join 操作：

```bash
TOKEN=fdaaead2ef08591cd4d59261ea3d1f757c7b845a675c53df342aafe9e526220b.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzE2NTg0MjV9.A_xGMBFXS6K1vw1QO2Z5ico728ggMQatcmHEg_YXbew
SERVER=192.168.100.140:10000

keadm join --cloudcore-ipport=$SERVER \
	--kubeedge-version=v1.18.1 \
	--cgroupdriver=systemd \
	--token=$TOKEN
```

之后就可以直接看到：

```bash
I1114 16:19:39.060769   35628 join_others.go:273] KubeEdge edgecore is running, For logs visit: journalctl -u edgecore.service -xe
I1114 16:19:49.070187   35628 join.go:94] 9. Install Complete!
```

然后使用 `systemctl status edgecore` 来查看 edgecore 的运行情况：

```bash
[root@edge1 ~]# systemctl status edgecore
● edgecore.service
   Loaded: loaded (/etc/systemd/system/edgecore.service; enabled; vendor preset: disabled)
   Active: active (running) since 四 2024-11-14 16:19:38 CST; 1min 18s ago
 Main PID: 35833 (edgecore)
    Tasks: 13
   Memory: 33.4M
   CGroup: /system.slice/edgecore.service
           └─35833 /usr/local/bin/edgecore
```

发现 edgecore 也是正常运行的。

## 4. 解决网络插件的问题

但是如果想要部署 pod 到边缘端的话，还是会失败的。因为 flannel 的 pod 并没有被部署到 edge 节点上。

因为 Kubeedge 和网络插件不兼容，所以需要亲和性配置。

### 4.1 cloud 端

flannel：

```bash
# 首先先利用之前部署好的 flannel 的配置文件将 flannel 删除
kubectl delete -f kube-flannel.yml

# 之后对 kube-flannel.yaml 文件进行修改
cp kube-flannel.yml kube-flannel-cloud.yaml

vim kube-flannel-cloud.yaml
--------------------------------------------------------------
# 修改其中的内容
# 1. 在 DaemonSet 部分，将 name 改成：kube-flannel-cloud-ds。如下：
metadata:
  # 改的是这里
  name: kube-flannel-cloud-ds
  namespace: kube-flannel

# 2. 在 nodeAffinity 的 matchExpressions 部分，添加节点亲和性
            - matchExpressions: 
              - key: kubernetes.io/os 
                operator: In 
                values: 
                - linux 
              # 加的是这里
              - key: node-role.kubernetes.io/edge 
                operator: DoesNotExist 
--------------------------------------------------------------

# 之后再应用该配置文件即可
kubectl apply -f kube-flannel-cloud.yaml
```

cloudcore：

```bash
# 修改 cloudcore 的 configmap
kubectl edit cm -n kubeedge
---------------------------------------------------------------
# 找到其中的 dynamicController.enable，修改为 true
        dynamicController:
          enable: true
---------------------------------------------------------------
```

### 4.2 edge 端

flannel：

```bash
# 复制一份边缘端的 flannel 配置文件
cp kube-flannel.yml kube-flannel-edge.yaml

vim kube-flannel-edge.yaml
--------------------------------------------------------------
# 1. 将 DaemonSet 部分的名字修改为 kube-flannel-edge-ds
metadata:
  # 改的是这里
  name: kube-flannel-edge-ds
  namespace: kube-flannel

# 2. 在 nodeAffinity 的 matchExpressions 部分，添加节点亲和性
            - matchExpressions:
              - key: kubernetes.io/os
                operator: In
                values:
                - linux
              # 加的是这里
              - key: node-role.kubernetes.io/edge
                operator: Exists

# 3. 在 container 的 kube-flannel 的命令参数 args 中，加入一条命令：
        args:
        - --ip-masq
        - --kube-subnet-mgr
        # 加的是这里
        - --kube-api-url=http://127.0.0.1:10550
--------------------------------------------------------------

# 然后再应用该配置文件
kubectl apply -f kube-flannel-edge.yaml
```

edgecore：

为了让 flannel 能否访问到 `http://127.0.0.1:10550`，我们需要配置 EdgeCore 的 metaServer 功能，在边缘节点上修改：

```bash
vim /etc/kubeedge/config/edgecore.yaml
--------------------------------------------------------------
# 将 metaServer.enable 设置为 true
    metaServer:
      apiAudiences: null
      dummyServer: 169.254.30.10:10550
      # 修改的是这里
      enable: true
--------------------------------------------------------------

# 之后重启 edgecore
systemctl daemon-reload
systemctl restart edgecore
systemctl status edgecore
```

## 5. 测试

执行下面的命令在边缘端发布一个 pod：

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  hostNetwork: true
  containers:
  - name: nginx
    image: nginx:1.14.2
    ports:
    - containerPort: 80
  nodeSelector:
    "node-role.kubernetes.io/edge": ""
EOF
```

之后查看 pod 的状态：

```bash
[root@master ~]# kubectl get pods -o wide
NAME    READY   STATUS    RESTARTS   AGE   IP                NODE    NOMINATED NODE   READINESS GATES
nginx   1/1     Running   0          5s    192.168.100.151   edge1   <none>           <none>

[root@master ~]# curl 192.168.100.151
# 然后就可以显示出 nginx 的欢迎页面
```

## 6. 启用 `kubectl logs` 功能

`kubectl logs` 必须在 metrics

1. 确保可以找到 Kubernetes 的 `ca.crt` 文件和 `ca.key` 文件。这些文件默认在 `/etc/kubernetes/pki/` 目录中。

    ```bash
    [root@master ~]# ls /etc/kubernetes/pki/ | grep ca
    ca.crt
    ca.key
    front-proxy-ca.crt
    front-proxy-ca.key
    ```

2. 设置 `CLOUDCOREIPS` 环境变量。环境变量设置为指定的 cloudcore 的 IP 地址。

    ```bash
    export CLOUDCOREIPS="192.168.100.140"
    
    # 使用以下命令检查是否设置成功
    echo $CLOUDCOREIPS
    ```

3. 在云端节点上为 CloudStream 生成证书，但是，生成的文件不在 `/etc/kubeedge/` 中，我们需要从 Github 的存储库中拷贝一份。

    ```bash
    wget https://raw.githubusercontent.com/kubeedge/kubeedge/refs/heads/master/build/tools/certgen.sh
    chmod +x certgen.sh
    mkdir /etc/kubeedge
    cp certgen.sh /etc/kubeedge/
    
    # 将工作目录更改为 kubeedge 目录
    cd /etc/kubeedge/
    
    # 从 certgen.sh 生成证书
    /etc/kubeedge/certgen.sh stream
    ```

4. 在主机上设置 iptables。（此命令应该在每个 apiserver 部署的节点上执行。）（其实就是 master 节点。）

    在每个运行 apiserver 的主机上运行以下命令：

    ```bash
    [root@master kubeedge]# kubectl get cm tunnelport -nkubeedge -oyaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      annotations:
        tunnelportrecord.kubeedge.io: '{"ipTunnelPort":{"192.168.100.140":10352,"192.168.100.141":10351},"port":{"10351":true,"10352":true}}'
      creationTimestamp: "2024-11-17T12:13:32Z"
      name: tunnelport
      namespace: kubeedge
      resourceVersion: "2827"
      uid: 5c80521d-e1f8-4119-bca1-c1d19672c151
    ```

    接着在 apiserver 运行的所有节点为 multi CloudCore 实例来设置 iptables，这里的 cloudcore ips 和 tunnel 端口都是从上面的 configmap 获得的。

    ```bash
    # iptables -t nat -A OUTPUT -p tcp --dport $YOUR-TUNNEL-PORT -j DNAT --to $YOUR-CLOUDCORE-IP:10003
    iptables -t nat -A OUTPUT -p tcp --dport 10352 -j DNAT --to 192.168.100.140:10003
    iptables -t nat -A OUTPUT -p tcp --dport 10351 -j DNAT --to 192.168.100.141:10003
    ```

    如果您不确定是否设置了 iptables，并且希望清除所有这些表。可以使用以下命令清理 iptables 规则：

    ```bash
    iptables -F && iptables -t nat -F && iptables -t mangle -F && iptables -X
    ```

5. `/etc/kubeedge/config/cloudcore.yaml` 和 `/etc/kubeedge/config/edgecore.yaml` 上 cloudcore 和 edgecore 都要修改。将 cloudStream 和 edgeStream 设置为 `enable: true`。将服务器 IP 更改为 cloudcore IP（与 `$CLOUDCOREIPS` 相同）。

    但是这里对 cloudcore 进行修改的时候，因为我们是二进制部署的，所以我们修改的不是 cloudcore 的 yaml，而是 configmap。

    **云端：**

    ```bash
    # 修改 configmap
    kubectl edit cm -n kubeedge
    
    # 找到 cloudStream.enable，修改为 true
            cloudStream:
              # 修改的是这里
              enable: true
    
    # 还有一个要配置的东西，虽然这里不是必须的，但是之后要用，所以就配置上
    # 找到 quic.enable，修改为 true
              quic:
                address: 0.0.0.0
                # 修改的是这里
                enable: true
    ```

    **边缘端：**

    ```bash
    # 边缘端的节点上都要执行
    vim /etc/kubeedge/config/edgecore.yaml
    
    # 找到 edgeStream.enable，然后设置为 true
      edgeStream:
        # 修改的是这里
        enable: true
    
    # 还有一个要配置的东西，虽然这里不是必须的，但是之后要用，所以就配置上
    # 找到 quic.enable，修改为 true
        quic:
          # 修改的是这里
          enable: true
    ```

6. 之后重启 cloudcore 和 edgecore：

    云端：

    ```bash
    # 找到 cloudcore 的 pod 的名字
    kubectl get all -n kubeedge
    
    # 删除掉 cloudcore 的 pod，等待 deployment 重建
    kubectl delete pod cloudcore-599689d85f-k4fqf -n kubeedge
    ```

    边缘端：

    ```bash
    systemctl restart edgecore
    ```

7. 验证：

    ```bash
    [root@master kubeedge]# kubectl logs -f nginx
    192.168.100.140 - - [19/Nov/2024:07:12:25 +0000] "GET / HTTP/1.1" 200 612 "-" "curl/7.29.0" "-"
    
    ```

    使用 `kubectl logs` 命令没有报错就说明这部分成功。

## 7. 在云端支持 Metrics-server

这里我们使用的是 v0.4.1 版本的metrics-server，由于 v0.4.0 之后支持自动端口识别，因此请使用v0.4.0+版本。

1. 实现该功能点的重复使用了 cloudstream 和 edgestream 模块。因此，您还需要执行[启用 `kubectl logs` 所有功能](##6.-启用-`kubectl-logs`-功能)的所有步骤。

1. 下载 `components.yaml`。

    ```bash
    wget https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.4.0/components.yaml
    ```

1. 修改 `components.yaml` 文件中的内容。

    ```yaml
    # 添加节点的亲和性和容忍配置，确保可以调度到 master 节点
    # 以及跳过不安全的 TLS 检查
      template:
        metadata:
          labels:
            k8s-app: metrics-server
        spec:
          # 新增
          hostNetwork: true
          # 新增
          affinity:
            nodeAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
                nodeSelectorTerms:
                - matchExpressions:
                  - key: node-role.kubernetes.io/control-plane
                    operator: Exists
          # 新增
          tolerations:
          - key: node-role.kubernetes.io/control-plane
            operator: Exists
            effect: NoSchedule
          containers:
          - args:
              # 新增
            - --kubelet-insecure-tls
            - --cert-dir=/tmp
            - --secure-port=4443
            - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
            - --kubelet-use-node-status-port
    ```

1. 部署

    ```bash
    kubectl apply -f components.yaml
    ```

1. 测试

    ```bash
    [root@master ~]# kubectl top nodes
    NAME     CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%   
    edge1    25m          0%     756Mi           20%       
    edge2    25m          0%     818Mi           22%       
    master   186m         4%     1120Mi          30%       
    node1    25m          0%     552Mi           15%       
    node2    22m          0%     492Mi           13%  
    ```











































