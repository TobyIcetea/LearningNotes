# Kubernetes 操作

## 1. Metrics server

### 1.1 部署

（1）从官网下载 components.yaml 并修改其中的 参数：

```yaml
containers:
- name: metrics-server
  image: k8s.gcr.io/metrics-server/metrics-server:v0.5.0
  command:
    - /metrics-server
    - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
    - --kubelet-insecure-tls   # 添加此行
```

这样是为了 Metrics Server 可以使用不安全的 TLS 连接与 kubelet 通信。

（2）直接使用下面的代码作为 components.yaml：

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: metrics-server
    rbac.authorization.k8s.io/aggregate-to-admin: "true"
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
    rbac.authorization.k8s.io/aggregate-to-view: "true"
  name: system:aggregated-metrics-reader
rules:
- apiGroups:
  - metrics.k8s.io
  resources:
  - pods
  - nodes
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: metrics-server
  name: system:metrics-server
rules:
- apiGroups:
  - ""
  resources:
  - nodes/metrics
  verbs:
  - get
- apiGroups:
  - ""
  resources:
  - pods
  - nodes
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server-auth-reader
  namespace: kube-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: extension-apiserver-authentication-reader
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server:system:auth-delegator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: system:metrics-server
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:metrics-server
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: v1
kind: Service
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
spec:
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: https
  selector:
    k8s-app: metrics-server
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: metrics-server
  strategy:
    rollingUpdate:
      maxUnavailable: 0
  template:
    metadata:
      labels:
        k8s-app: metrics-server
    spec:
      # 使 Pod 使用主机网络
      hostNetwork: true
      containers:
      - args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
        - --kubelet-insecure-tls 
        image: bitnami/metrics-server:latest
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 3
          httpGet:
            path: /livez
            port: https
            scheme: HTTPS
          periodSeconds: 10
        name: metrics-server
        ports:
        - containerPort: 4443
          name: https
          protocol: TCP
        readinessProbe:
          failureThreshold: 3
          httpGet:
            path: /readyz
            port: https
            scheme: HTTPS
          initialDelaySeconds: 20
          periodSeconds: 10
        resources:
          requests:
            cpu: 100m
            memory: 200Mi
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
        volumeMounts:
        - mountPath: /tmp
          name: tmp-dir
      nodeSelector:
        kubernetes.io/os: linux
      affinity:
      	nodeAffinity:
      	  requiredDuringSchedulingIgnoredDuringExecution:
      	    nodeSelectorTerms:
      	    - matchExpressions:
      	        # 不要调度到 edge 节点
      	      - key: node-role.kubernetes.io/edge
      	        operator: DoesNotExist
      	        # 指定，必须调度到主节点
      	      - key: node-role.kubernetes.io/control-plane
      	      	operator: Exists
      # 添加主节点的容忍
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
          effect: NoSchedule
      priorityClassName: system-cluster-critical
      serviceAccountName: metrics-server
      volumes:
      - emptyDir: {}
        name: tmp-dir
---
apiVersion: apiregistration.k8s.io/v1
kind: APIService
metadata:
  labels:
    k8s-app: metrics-server
  name: v1beta1.metrics.k8s.io
spec:
  group: metrics.k8s.io
  groupPriorityMinimum: 100
  insecureSkipTLSVerify: true
  service:
    name: metrics-server
    namespace: kube-system
  version: v1beta1
  versionPriority: 100
```

然后直接 `kubectl apply -f components.yaml` 就可以啦。

### 1.2 使用

- 获取节点的 CPU 使用情况：

    ```bash
    kubectl top node
    ```

- 获取命名空间中的 pod 的 CPU 和内存使用情况：

    ```bash
    kubectl top pod -n <namespace>
    ```

- 获取命名空间中的 deployment 的 CPU 和内存使用情况：

    ```bash
    kubectl top deploy -n <namespace>
    ```

### 1.3 总结

在 Kubernetes 集群中部署 Metrics Server 可以实现对集群中各种资源的实时监控和度量指标收集，从而帮助管理员和开发人员更好地管理和优化 Kubernetes 应用程序的性能。

## 2. 消除 master 节点的污点

使用命令

```bash
kubectl describe node master
```

可以看到 master 节点是带有污点的：

```bash
Taints:             node-role.kubernetes.io/control-plane:NoSchedule
```

可以使用如下命令消除这个污点：

```bash
kubectl taint nodes master node-role.kubernetes.io/control-plane:NoSchedule-
```

## 3. Pod 控制器重启

在 Kubernetes 中，控制器用于管理一组 Pod 的生命周期。为了保持高可用性，Kubernetes 提供了几种方法来重启这些控制器管理的 Pod，其中 `kubectl rollout restart` 是最常用的方式。

1. Deployment

    命令：

    ```bash
    kubectl rollout restart deployment <deployment-name> -n <namespace>
    ```

    用途：重启 Deployment 管理的 Pod，按滚动更新的方式逐个重启，避免服务中断。

2. DaemonSet

    命令：

    ```bash
    kubectl rollout restart daemonset <daemonset-name> -n <namespace>
    ```

    用途：重启 Daemonset 管理的 Pod，通常在每个节点上都会有一个 Pod。

3. ReplicaSet

    命令：

    ```bash
    kubectl rollout restart replicaset <replicaset-name> -n <namespace>
    ```

    用途：虽然通常通过 Deployment 进行管理，但也可以直接对 ReplicaSet 进行重启。

## 4. Kubernetes 命令补全

直接执行下面的命令：

```bash
dnf install -y bash-completion
source /usr/share/bash-completion/bash_completion
source <(kubectl completion bash)
kubectl completion bash > ~/.kube/completion.bash.inc

vim ~/.bash_profile
----------------------------------------------------------------
# 加入如下内容
source '/root/.kube/completion.bash.inc'
----------------------------------------------------------------

source $HOME/.bash_profile
```

## 5. DNS-Server 部署

### 关闭防火墙、Selinux

```bash
systemctl disable firewalld
systemctl stop firewalld

vim /etc/selinux/config
```

### 将 DNS1 设置为本机 IP

```bash
# CentOS Stream 中
vim /etc/NetworkManager/system-connections/ens160.nmconnection
# ---------------------------------
address=192.168.100.144/24
dns=192.168.100.144;8.8.8.8;
# ---------------------------------

# 重新加载配置
nmcli connection reload
nmcli connection down ens160
nmcli connection up ens160
```

### 安装 bind 软件

```bash
dnf install bind -y
```

### 编辑配置

```bash
vim /etc/named.conf

# 13 行
    listen-on port 53 { 127.0.0.1;any; };
# 19 行，表示允许任何人查询
    allow-query     { localhost;any; };
```

```bash
vim /etc/named.rfc1912.zones

# 这是一个注册域名的文件
# 我们准备创建 siborn.top 的域名
# 在最后加入：
zone "siborn.top" IN {
    type master;
    file "siborn.top.zone";
    allow-update { none; };
};
```

```bash
cd /var/named
# -p 选项是为了保持原本的属主属组不变
cp -p named.localhost siborn.top.zone

vim siborn.top.zone
# 修改为：
$TTL 1D
@   IN SOA  siborn.top admin.siborn.top. (
                    0   ; serial
                    1D  ; refresh
                    1H  ; retry
                    1W  ; expire
                    3H )    ; minimum
@       NS  ns.siborn.top.
ns      A   192.168.100.144
harbor  A   192.168.100.143
nfs     A   192.168.100.145

@       A   192.168.100.143  # 后期自己加的，表示将 siborn.top 解析到 143
www     A   192.168.100.143  # 后期自己加的，表示将 www.siborn.top 解析到 143

```

### 设置开机自启动

```bash
systemctl enable --now named
```

### 验证

```bash
[root@dns-server named]# nslookup

> nfs.siborn.top
Server:         192.168.100.144
Address:        192.168.100.144#53

Name:   nfs.siborn.top
Address: 192.168.100.145

> harbor.siborn.top
Server:         192.168.100.144
Address:        192.168.100.144#53

Name:   harbor.siborn.top
Address: 192.168.100.143
```

### 同步到其他主机

将 Kubernetes 集群中所有主机、集群外的公共服务主机的 DNS1 都设置为 dns-server 的 IP。

```bash
# CentOS Stream 中
vim /etc/NetworkManager/system-connections/ens160.nmconnection
# ---------------------------------
address=192.168.100.144/24
dns=192.168.100.144;8.8.8.8;
# ---------------------------------

# 重新加载配置
nmcli connection reload
nmcli connection down ens160
nmcli connection up ens160
```

之后在所有主机中验证：

```bash
[root@master system-connections]# nslookup nfs.siborn.top
Server:         192.168.100.144
Address:        192.168.100.144#53

Name:   nfs.siborn.top
Address: 192.168.100.145

[root@master system-connections]# nslookup www.baidu.com
Server:         192.168.100.144
Address:        192.168.100.144#53

Non-authoritative answer:
www.baidu.com   canonical name = www.a.shifen.com.
Name:   www.a.shifen.com
Address: 110.242.70.57
Name:   www.a.shifen.com
Address: 110.242.69.21
Name:   www.a.shifen.com
Address: 2408:871a:2100:1b23:0:ff:b07a:7ebc
Name:   www.a.shifen.com
Address: 2408:871a:2100:186c:0:ff:b07e:3fbc
```

结论是集群中所有主机都可以访问集群内域名、集群外域名。

## 6. Harbor 部署

### 安装 docker-ce

```bash
# 安装yum-config-manager配置工具
yum -y install yum-utils

# 建议使用阿里云yum源
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 安装docker-ce版本
yum install -y docker-ce
# 启动并开机启动
systemctl enable --now docker
docker --version
```

### 部署 docker-compose

```bash
curl -SL https://github.com/docker/compose/releases/download/v2.16.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 下载 Harbor 的 Docker Compose 文件

```bash
export HARBOR_VERSION=2.5.6

wget https://github.com/goharbor/harbor/releases/download/v${HARBOR_VERSION}/harbor-offline-installer-v${HARBOR_VERSION}.tgz

tar xvf harbor-offline-installer-v${HARBOR_VERSION}.tgz

cd harbor
```

### 设定 https 证书

本次使用我在华为云给域名 `siborn.top` 申请的证书。

```bash
mkdir certs

# 通过 ftp 上传证书 zip 文件
# 。。。。。。。

unzip siborn-top-pem.zip
# 因为 harbor 的前端是使用 Nginx 做的，所以我们使用 Nginx 证书
cd scs1747216134916_siborn.top/scs1747216134916_siborn.top_Nginx
cp scs1747216134916_siborn.top_server.crt ../../
cp scs1747216134916_siborn.top_server.key ../../
```

### 修改配置

```bash
cp harbor.yml.tmpl harbor.yml

# vim harbor.yml
hostname: siborn.top  # 修改为域名，并且一定是证书签发的域名

# htp related config
http:
# port for htp, default is 80. If htps enabled, this port will redirect to htps port
	port: 80

# https related config
https:
  # https port for harbor, default is 443
  port: 443
  # The path of cert and key files for nginx
  certificate: /root/packages/harbor/certs/scs1747216134916_siborn.top_server.crt
  private_key: /root/packages/harbor/certs/scs1747216134916_siborn.top_server.key
  
# 之后的数据会存储到 /data 中，可以将数据盘挂载到 /data 上
mkdir /data
```

### 部署 Harbor

```bash
./prepare
./install.sh
```

之后通过 docker ps 查看启动的服务数量，按理来说应该是启动了 9 个容器。

如果需要重启容器：

```bash
docker-compose down

# 如果修改了 harbor.yml 配置文件，prepare 会读取 harbor.yml，并重新升成配置文件
./prepare

# -d 表示后台运行
docker-compose up -d
```

### 登录 Harbor

> 如果是在浏览器中登录，按理来说啊，应该是可以直接通过 siborn.top 直接进行登录的。这个地址按照我们 DNS 服务器的配置，应该是解析到本地的一台服务器中。
>
> 但是现在是什么呢，命令行是正确的，使用 nslookup 查询这个域名，查询到的是本地的机器。
>
> 但是直接 curl 呢，查询到的就变成了我公网的那个华为云服务器。
>
> 这是为什么呢？后来发现是因为设置了代理了，将代理重置，在 `no_proxy` 环境变量中加入 `siborn.top`，此时再 curl 这个地址，得到的就是我本地的 harbor 页面中的东西了。
>
> 但是浏览器还是不认，还是会解析到我远程的服务器。
>
> 重启机器之后，浏览器也正常了。看来浏览器对于这个环境变量的绑定是一开始就绑定上的。
>
> 看来之后 Linux 中配置 DNS 啥的，不能让梯子开机自启动了。啥时候用，啥时候再配置。

（前提是要关闭 http 和 https 对这个网站的代理！）

（如果是要在 Linux 图形界面访问浏览器，就要在 `/etc/profile` 中设置好，再重启 Linux）

浏览器中：

```bash
siborn.top
www.siborn.top

192.168.100.143  # 不安全，可以继续访问
harbor.siborn.top  # 不安全，不可以继续访问
```

命令行：

```bash
docker login siborn.top
docker login www.siborn.top

docker login localhost
```

（虽然说我申请的证书是 `siborn.top` 的证书，但是访问 `www.siborn.top` 也是正常的。或许是因为虽然是 `siborn.top` 的证书，但是同时也可以用来验证 `www.siborn.top` 的网址。）

### 上传镜像

```bash
docker pull nginx:latest

docker tag nginx:latest siborn.top/library/nginx:v1

docker login siborn.top

docker push siborn.top/library/nginx:v1
```

### 拉取镜像

```bash
docker pull siborn.top/library/nginx:v1

nerdctl pull siborn.top/library/nginx:v1
```

或者加上 `www` 也是可以的！因为最前面一个地址表示到这个网站去拉取数据！

### Harbor 设置开机自启动

```bash
cd /root/packages/harbor

cat << EOF > start_harbor.sh
#!/bin/bash
cd /root/packages/harbor
docker-compose up -d
EOF

chmod +x start_harbor.sh

cat << EOF > /etc/systemd/system/start_harbor.service
[Unit]
Description=Harbor Startup Script
After=docker.service

[Service]
ExecStart=/path/to/start_harbor.sh

[Install]
WantedBy=default.target
EOF

systemctl enable --now start_harbor
```





## 7. NFS-Server 部署

先实践一次 NFS-Server 的部署，熟悉之后，后期再替换为分布式存储（Ceph）。

### 基础配置

- 设置主机名为 nfs-server
- 设置 IP 地址，设置 DNS 为集群中的 DNS 服务器
- 关闭 firewalld、SELINUX

### 添加硬盘并挂载

将 Linux 系统关机，在 Vmware 中添加一块新的 100G 的硬盘。之后重新启动操作系统，让内核能够检测到这个硬盘。

重启之后：

```bash
[root@nfs-server ~]# lsblk
NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sr0          11:0    1 1024M  0 rom
nvme0n1     259:0    0  100G  0 disk
├─nvme0n1p1 259:2    0  600M  0 part /boot/efi
├─nvme0n1p2 259:3    0    1G  0 part /boot
└─nvme0n1p3 259:4    0 98.4G  0 part
  ├─cs-root 253:0    0 63.5G  0 lvm  /
  ├─cs-swap 253:1    0  3.9G  0 lvm  [SWAP]
  └─cs-home 253:2    0   31G  0 lvm  /home
nvme0n2     259:1    0  100G  0 disk
```

可以看到多了一个 nvme0n2 的块设备。

```bash
mkfs.xfs /dev/nvme0n2  # 格式化硬盘

# 让每次开机的时候自动挂载
mkdir /nvme0n2
vim /etc/fstab

# 在最后加入下面这行内容
/dev/nvme0n2            /nvme0n2                xfs     defaults        0 0

systemctl daemon-reload
mount -a

[root@nfs-server ~]# df -h
文件系统             容量  已用  可用 已用% 挂载点
devtmpfs             4.0M     0  4.0M    0% /dev
tmpfs                870M     0  870M    0% /dev/shm
tmpfs                348M  7.1M  341M    3% /run
efivarfs             256K   54K  198K   22% /sys/firmware/efi/efivars
/dev/mapper/cs-root   64G  6.0G   58G   10% /
/dev/nvme0n1p2       960M  359M  602M   38% /boot
/dev/mapper/cs-home   31G  260M   31G    1% /home
/dev/nvme0n1p1       599M  7.5M  592M    2% /boot/efi
tmpfs                174M   52K  174M    1% /run/user/42
tmpfs                174M   36K  174M    1% /run/user/0
/dev/nvme0n2         100G  746M  100G    1% /nvme0n2		# 这里可以看到已经挂载成功了
```

### 将硬盘共享出去

```bash
# 集群内、集群外所有节点
dnf install -y nfs-utils
```

```bash
# NFS Server 节点
vim /etc/exports

# 加入一行内容
/nvme0n2    *(rw,sync,no_root_squash)
# 这表示：将 /nvme0n2 共享出去，对所有主机开放读写权限、同步模式，以及不压缩 root 权限（远程 root 用户拥有与本地 root 用户相同的权限）

systemctl enable --now nfs-server

# 在 NFS Server 上
[root@nfs-server nvme0n2]# showmount -e
Export list for nfs-server:
/nvme0n2 *

# 在集群中的其他主机上
[root@master ~]# showmount -e nfs.siborn.top
Export list for nfs.siborn.top:
/nvme0n2 *
```

### Kubernetes 存储动态供给

在 K8s 集群的 master 主机上：

```bash
mkdir vol-dy
cd vol-dy/
for file in class.yaml deployment.yaml rbac.yaml ; do wget https://raw.githubusercontent.com/kubernetes-incubator/external-storage/master/nfs-client/deploy/$file ; done
```

```bash
vim class.yaml

# 修改名字为 nfs-client
metadata:
  name: nfs-client
  

kubectl apply -f class.yaml
kubectl apply -f deployment.yaml

vim deployment.yaml

# ------------------------------------------------------------
 22       containers:
 23         - name: nfs-client-provisioner
 24           image: registry.cn-beijing.aliyuncs.com/xngczl/nfs-subdir-external-provisione:v4.0.0			# 修改
 25           volumeMounts:
 26             - name: nfs-client-root
 27               mountPath: /persistentvolumes
 28           env:
 29             - name: PROVISIONER_NAME
 30               value: fuseim.pri/ifs
 31             - name: NFS_SERVER
 32               value: nfs.siborn.top		# 修改
 33             - name: NFS_PATH
 34               value: /nvme0n2			# 修改
 35       volumes:
 36         - name: nfs-client-root
 37           nfs:
 38             server: nfs.siborn.top		# 修改
 39             path: /nvme0n2				# 修改
# ------------------------------------------------------------

kubectl apply -f deployment.yaml

[root@master vol-dy]# kubectl get pods
NAME                                      READY   STATUS    RESTARTS   AGE
nfs-client-provisioner-56b497c8c6-2dnqv   1/1     Running   0          5m31s
```

### 验证

```yaml
[root@master test]# cat nginx-storage-class.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: nginx
  serviceName: "nginx"
  replicas: 2
  template:
    metadata:
      labels:
        app: nginx
    spec:
      imagePullSecrets:
      - name: huoban-harbor
      terminationGracePeriodSeconds: 10
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "nfs-client"
      resources:
        requests:
          storage: 1Gi

```

部署之后：

```bash
[root@master test]# kubectl get pods
NAME                                      READY   STATUS    RESTARTS      AGE
nfs-client-provisioner-56b497c8c6-2dnqv   1/1     Running   1 (12m ago)   4h20m
web-0                                     1/1     Running   0             74s
web-1                                     1/1     Running   0             72s

[root@master test]# kubectl get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM               STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-4778ab1b-c2c7-4da3-acb8-e5701f3a342f   1Gi        RWO            Delete           Bound    default/www-web-0   nfs-client     <unset>                          117s
pvc-4f9231bc-29e1-48af-b1c3-ee0017dd80d3   1Gi        RWO            Delete           Bound    default/www-web-1   nfs-client     <unset>                          113s

[root@master test]# kubectl get pvc
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
www-web-0   Bound    pvc-4778ab1b-c2c7-4da3-acb8-e5701f3a342f   1Gi        RWO            nfs-client     <unset>                 118s
www-web-1   Bound    pvc-4f9231bc-29e1-48af-b1c3-ee0017dd80d3   1Gi        RWO            nfs-client     <unset>                 114s

```

可以看到 pv 和 pvc 都被创建好了。

此时访问 curl pod 的 IP，发现返回的是 403 Forbidden，原因是 nginx 容器中对应目录没有 html 文件。

回到 NFS 服务器，

```bash
[root@nfs-server ~]# cd /nvme0n2/
[root@nfs-server nvme0n2]# ls
default-www-web-0-pvc-4778ab1b-c2c7-4da3-acb8-e5701f3a342f  default-www-web-1-pvc-4f9231bc-29e1-48af-b1c3-ee0017dd80d3
[root@nfs-server nvme0n2]# cd default-www-web-0-pvc-4778ab1b-c2c7-4da3-acb8-e5701f3a342f/
[root@nfs-server default-www-web-0-pvc-4778ab1b-c2c7-4da3-acb8-e5701f3a342f]# ls
[root@nfs-server default-www-web-0-pvc-4778ab1b-c2c7-4da3-acb8-e5701f3a342f]#
```

发现存储卷中没有东西。这个存储卷是对应着 nginx 容器的 `/usr/share/nginx/html` 位置，所以要在这里创建一些文件。

```bash
[root@nfs-server default-www-web-0-pvc-4778ab1b-c2c7-4da3-acb8-e5701f3a342f]# echo "web-0" > index.html
```

此时在集群中 master 节点上：

```bash
[root@master test]# curl 10.244.2.7		# 10.244.2.7 是 web-0 这个 pod 的 IP
web-0

# 还可以通过解析域名
# 10.244.1.2 是集群中 coredns 的 IP 地址
[root@master test]# nslookup nginx.default.svc.cluster.local 10.244.1.2
Server:         10.244.1.2
Address:        10.244.1.2#53

Name:   nginx.default.svc.cluster.local
Address: 10.244.2.7
Name:   nginx.default.svc.cluster.local
Address: 10.244.1.7
```

































