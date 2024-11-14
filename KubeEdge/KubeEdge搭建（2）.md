# KubeEdge 搭建（2）

这次使用的搭建方式就不使用 NodePort 来映射端口了，我们直接将 cloudcore 部署到 master 节点上。

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

也就是说效果如下：

![image-20241114160418132](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241114160418132.png)

除此之外，还需要给 Deployment 添加容忍（`spec.template.spec.tolerations`）：

```yaml
      tolerations:
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Exists"
        effect: "NoSchedule"
```

也就是说最后的结果如下：

![image-20241114161503003](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241114161503003.png)

![image-20241114161522047](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241114161522047.png)

之后再查看 cloudcore 的部署位置，就可以发现已经被调度到 master 节点上面了：

```bash
[root@master ~]# kubectl get pods -n kubeedge -o wide
NAME                         READY   STATUS    RESTARTS   AGE     IP                NODE     NOMINATED NODE   READINESS GATES
cloudcore-599689d85f-4r7tw   1/1     Running   0          2m57s   192.168.100.140   master   <none>           <none>
```

## 3. 部署边缘端

边缘端有一个要求是，要有容器运行时。所以我们按照之前的 K8s 文档，给 edge1 和 edge2 都安装好 containerd。注意：安装 containerd 的步骤都要做完，包括配置 crictl、配置 cni 插件等。

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

## 4. 解决网络问题

虽然节点加入进来了，但是我们在 master 上面查看节点发现：

```bash
[root@master ~]# kubectl get nodes
NAME     STATUS     ROLES           AGE   VERSION
edge1    NotReady   agent,edge      10m   v1.29.5-kubeedge-v1.18.1
master   Ready      control-plane   20d   v1.28.2
node1    Ready      <none>          20d   v1.28.2
node2    Ready      <none>          20d   v1.28.2
```

节点的状态还是 NotReady 的。

然后通过如下的方法将 flannel 进行二进制部署：

```bash
# 下载 flannel 二进制文件
wget https://github.com/flannel-io/flannel/releases/download/v0.25.7/flanneld-amd64

# 移动到 /usr/local/bin 下面
mv flanneld-amd64 /usr/local/bin/flanneld

# 添加可执行权限
chmod +x /usr/local/bin/flanneld

# 编辑配置文件
mkdir /etc/flannel
cat << EOF > /etc/flannel/options.env
FLANNELD_IFACE=ens33  # 这里就写自己的网络接口
FLANNELD_IP_MASQ=true
FLANNELD_SUBNET_FILE=/run/flannel/subnet.env
FLANNELD_ETCD_ENDPOINTS=http://<etcd-server>:2379
EOF

# 启动 flannel 服务
cat << EOF > /etc/systemd/system/flanneld.service
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
EOF

# 启动并设置 flannel 为开机自启动
systemctl daemon-reload
systemctl enable flanneld
systemctl start flanneld

# 查看 flannel 的状态
systemctl status flanneld

# 如果 Flannel 没有自动生成 CNI 配置文件，我们可以自己创建
cat << EOF > /etc/cni/net.d/10-flannel.conf
{
  "name": "cbr0",
  "type": "flannel",
  "delegate": {
    "isDefaultGateway": true
  }
}

EOF

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







