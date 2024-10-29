# KubeEdge 搭建

## 1. 安装前准备

我们本次是准备了五台机器，五台机器的设备名、IP 地址如下所示：

```yaml
master: 192.168.100.140
node1: 192.168.100.141
node2: 192.168.100.142
edge1: 192.168.100.151
edge2: 192.168.100.152
```

其中的 master、node1 和 node2 是我们按照 K8s 教程部署的 K8s 集群。edge1 和 edge2 是纯净的 Linux 操作系统。

## 2. 部署云端

### 2.1 执行 keadm init

在云端的 master 节点上下载 keadm 的包（我们本次安装的 KubeEdge 是 1.18.1 版本的）：

```bash
wget https://github.com/kubeedge/kubeedge/releases/download/v1.18.1/keadm-v1.18.1-linux-amd64.tar.gz
```

接下来要做的操作是：将下载好的安装包解压，然后将里面的一个 keadm 可执行文件，复制到 `/usr/local/bin` 下面。

然后可以使用 `keadm version` 来验证安装是否成功。

之后我们就可以使用下面的命令安装 cloudcore 了：

```bash
keadm init --advertise-address=192.168.100.140 --kubeedge-version=v1.18.1 --set iptablesManager.mode="external"
```

命令运行结束，会产生下面的输出：

```bash
=========CHART DETAILS=======
Name: cloudcore
LAST DEPLOYED: Tue Oct 29 15:44:13 2024
NAMESPACE: kubeedge
STATUS: deployed
REVISION: 1
```

之后我们使用下面的命令来检查安装的结果：

```bash
# 执行
kubectl get all -n kubeedge

# 输出
NAME                               READY   STATUS    RESTARTS   AGE
pod/cloud-iptables-manager-f9h2k   1/1     Running   0          57s
pod/cloud-iptables-manager-sskws   1/1     Running   0          57s
pod/cloudcore-64b5bc6f4f-vs7q2     1/1     Running   0          57s

NAME                TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                                             AGE
service/cloudcore   ClusterIP   10.105.88.53   <none>        10000/TCP,10001/UDP,10002/TCP,10003/TCP,10004/TCP   57s

NAME                                    DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/cloud-iptables-manager   2         2         2       2            2           <none>          57s
daemonset.apps/edge-eclipse-mosquitto   0         0         0       0            0           <none>          57s

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cloudcore   1/1     1            1           57s

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/cloudcore-64b5bc6f4f   1         1         1       57s
```

### 2.2 修改 service 类型为 NodePort

可以看到其中我们的 service 类型是 `ClusterIP` 类型的，但是我们要让集群外也能访问到云端，所以要将 service 类型改为 NodePort：

```bash
# 执行命令
kubectl edit service cloudcore -n kubeedge

# 接下来找到配置文件的最后，找到一个 type: ClusterIP，换成 NodePort 就行

# 再次执行命令检查一下
[root@master ~]# kubectl get all -n kubeedge
NAME                               READY   STATUS    RESTARTS   AGE
pod/cloud-iptables-manager-f9h2k   1/1     Running   0          3m31s
pod/cloud-iptables-manager-sskws   1/1     Running   0          3m31s
pod/cloudcore-64b5bc6f4f-vs7q2     1/1     Running   0          3m31s

NAME                TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)                                                                           AGE
service/cloudcore   NodePort   10.105.88.53   <none>        10000:31358/TCP,10001:32742/UDP,10002:32437/TCP,10003:32497/TCP,10004:32511/TCP   3m31s

NAME                                    DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/cloud-iptables-manager   2         2         2       2            2           <none>          3m31s
daemonset.apps/edge-eclipse-mosquitto   0         0         0       0            0           <none>          3m31s

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cloudcore   1/1     1            1           3m31s

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/cloudcore-64b5bc6f4f   1         1         1       3m31s
```

可以看到我们的 Service 类型已经改成了 NodePort 了。同时，我们发现端口的对应关系：

```bash
10000:31358/TCP
10001:32742/UDP
10002:32437/TCP
10003:32497/TCP
10004:32511/TCP
```

这个意思就是说，之后如果要访问集群的 10000 端口（cloudcore 相关的端口）的话，就直接访问 31358 端口就行了。即使 31358 端口并没有被监听。

这时候我们也可以看一下 pod 是跑在哪个 node 上的，并且看一下那个 node 的端口信息：

```bash
[root@master ~]# kubectl get all -n kubeedge -o wide
NAME                               READY   STATUS    RESTARTS   AGE   IP                NODE    NOMINATED NODE   READINESS GATES
pod/cloud-iptables-manager-f9h2k   1/1     Running   0          10m   192.168.100.142   node2   <none>           <none>
pod/cloud-iptables-manager-sskws   1/1     Running   0          10m   192.168.100.141   node1   <none>           <none>
pod/cloudcore-64b5bc6f4f-vs7q2     1/1     Running   0          10m   192.168.100.142   node2   <none>           <none>
```

接下来我们可以去 node2 上看看相应的端口是否启动了：

![image-20241029155643445](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241029155643445.png)

这些都没问题之后，就说明我们的云端已经部署好了。

## 3. 部署边缘端

### 3.1 执行 keadm join

边缘端有一个要求是，要有容器运行时。所以我们按照之前的 K8s 文档，给 edge1 和 edge2 都安装好 containerd。注意：安装 containerd 的步骤都要做完，包括配置 crictl、配置 cni 插件等。

然后在云端的 master 节点上获取 token：

```bash
[root@master ~]# keadm gettoken
d01defad0de4df6a6b3a25ad4342f20409b79f7433967e8d3d783d63783acc2d.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzAyNzQyNzZ9.sWEAq8JggENS3CsV_0rjMOEgVq0rp30nJT7VKJiixf0
```

接下来就到边缘节点上执行 join 操作：

```bash
TOKEN=d01defad0de4df6a6b3a25ad4342f20409b79f7433967e8d3d783d63783acc2d.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzAyNzQyNzZ9.sWEAq8JggENS3CsV_0rjMOEgVq0rp30nJT7VKJiixf0
# 为什么这里是 31358：因为原本是 10000，我们要改成 NodePort 规则中和 10000 对应的端口
SERVER=192.168.100.140:31358

keadm join --cloudcore-ipport=$SERVER \
	--kubeedge-version=v1.18.1 \
	--cgroupdriver=systemd \
	--token=$TOKEN
```

执行这条命令，最后碰到

```bash
KubeEdge edgecore is running, For logs visit: journalctl -u edgecore.service -xe
```

这样的输出之后，就卡住不动了。我们用 `Ctrl+C` 终止，然后看看是为什么。

### 3.2 配置 edgecore

通过命令 `journalctl -xeu edgecore`，我们发现，报错的原因是：`dial tcp 192.168.100.140:10002: connect: connection refused`，就是说我们尝试连接 140 主机的 10002 端口，但是被拒绝了。拒绝的原因也很简单，140 主机的 10002 端口并没有被开启，我们是使用 NodePort 给映射到其他端口上了。

接下来我们修改 edgecore 的配置端口：

```bash
vim /etc/kubeedge/config/edgecore.yaml

# 接下来我们依据上面的规则，将 10000~10004 的端口号，全都更改为我们 NodePort 的映射规则：
10000:31358/TCP
10001:32742/UDP
10002:32437/TCP
10003:32497/TCP
10004:32511/TCP
# 除此之外，还有一个地方要改，就是将其中的 edgeStream.enable 改成 true
  edgeStream:
    enable: true

# 接下来就可以重新启动 edgecore
systemctl restart edgecore
systemctl status edgecore
```

![image-20241029162136767](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241029162136767.png)

可以看到 edgecore 的服务终于是启动起来了。

但是但是但是，此时我们回到 master 节点，在 master 节点上执行 `kubectl get nodes`，就会发现，edge 节点已经加入进来了，但是还没有 ready。

我们通过 `kubectl describe node edge1` 可以看到报错信息是：

```bash
container runtime network not ready: NetworkReady=false reason:NetworkPluginNotReady message:Network plugin returns error: cni plugin not initialized
```

也就是说，网络插件还没有安装好。

### 3.3 二进制部署 flannel

```bash
# 下载 flannel 二进制文件
wget https://github.com/flannel-io/flannel/releases/download/v0.25.7/flanneld-amd64

# 移动到 /usr/local/bin 下面
mv flanneld-amd64 /usr/local/bin/flanneld

# 添加可执行权限
chmod +x /usr/local/bin/flanneld

# 编辑配置文件
mkdir /etc/flannel
vim /etc/flannel/options.env
-------------------------------------------------------
FLANNELD_IFACE=ens33  # 这里就写自己的网络接口
FLANNELD_IP_MASQ=true
FLANNELD_SUBNET_FILE=/run/flannel/subnet.env
FLANNELD_ETCD_ENDPOINTS=http://<etcd-server>:2379
-------------------------------------------------------

# 启动 flannel 服务
vim /etc/systemd/system/flanneld.service
-------------------------------------------------------
[Unit]
Description=Flannel overlay network agent
Documentation=https://github.com/flannel-io/flannel
After=network.target

[Service]
Type=simple
EnvironmentFile=/etc/flannel/options.env
ExecStart=/usr/local/bin/flanneld --iface=${FLANNELD_IFACE} --ip-masq=${FLANNELD_IP_MASQ} --subnet-file=${FLANNELD_SUBNET_FILE} --etcd-endpoints=${FLANNELD_ETCD_ENDPOINTS}
Restart=always
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
-------------------------------------------------------

# 启动并设置 flannel 为开机自启动
systemctl daemon-reload
systemctl enable flanneld
systemctl start flanneld

# 查看 flannel 的状态
systemctl status flanneld

# 如果 Flannel 没有自动生成 CNI 配置文件，我们可以自己创建
vim /etc/cni/net.d/10-flannel.conf
------------------------------------------------------
{
  "name": "cbr0",
  "type": "flannel",
  "delegate": {
    "isDefaultGateway": true
  }
}
------------------------------------------------------

# 然后在 edgecore 的配置文件中，设置网络插件
vim /etc/kubeedge/config/edgecore.yaml
# 修改如下的内容
------------------------------------------------------
modules:
  edged:
    networkPluginName: "cni"
    cniConfDir: "/etc/cni/net.d"
    cniBinDir: "/opt/cni/bin"
    networkPluginMTU: 1500
------------------------------------------------------

# 重启 edgecore
systemctl restart edgecore
```

这时候再看集群节点状态，就可以发现集群的节点都加入进来了，并且也都 Ready 了。

![image-20241029165309586](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241029165309586.png)









