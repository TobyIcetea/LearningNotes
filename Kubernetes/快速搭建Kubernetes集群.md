# 快速搭建K8s集群

> 使用的配置：
>
> - 操作系统：Centos7.5
> - K8s 版本：1.28.14

## 1. 主机安装

首先要先规划出各个主机的 IP 地址、硬件资源等信息。例如：

| 作用   | IP地址          | 操作系统                    | 配置                     |
| ------ | --------------- | --------------------------- | ------------------------ |
| Master | 192.168.100.140 | Centos7.5    基础设施服务器 | 2颗CPU  2G内存   50G硬盘 |
| Node1  | 192.168.100.141 | Centos7.5    基础设施服务器 | 2颗CPU  2G内存   50G硬盘 |
| Node2  | 192.168.100.132 | Centos7.5    基础设施服务器 | 2颗CPU  2G内存   50G硬盘 |

并且，在安装操作系统（例如 Centos 7.5）的时候，「软件选择」选择「基础设施服务器」。

「网络配置」像下面这样配置：

```bash
网络地址：192.168.100.140  （每台主机都不一样  分别为140、141、142）
子网掩码：255.255.255.0
默认网关：192.168.100.2
DNS：    8.8.8.8
```

三台主机的「主机名」按照下面这样设置：

```bash
master节点： master
node节点：   node1
node节点：   node2
```

## 2. 环境初始化

1. IP 地址修改与主机名解析。

    为了方便后续集群节点之间的直接调用，在这里要配置一下主机名解析。

    ```bash
    vim /etc/sysconfig/network-scripts/ifcfg-ens33
    # 然后修改 IP 地址
    systemctl restart network
    
    # 分别设置主机域名
    hostnamectl set-hostname master/node1/node2
    
    vim /etc/hosts
    # 加入下面的内容
    --------------------------
    192.168.100.140  master
    192.168.100.141  node1
    192.168.100.142  node2
    --------------------------
    ```

2. 时间同步。

    K8s 要求集群中的节点时间必须准确一致。这里直接使用 chronyd 服务从网络同步时间。

    ```bash
    # 启动 chronyd 服务
    systemctl start chronyd
    # 设置 chronyd 服务开机自启动
    systemctl enable chronyd
    # 服务启动之后稍微等几秒钟，就可以使用 date 命令验证时间了
    date
    ```

3. 禁用 iptables 和 firewalld 服务

    K8s 和 docker 在运行中会产生大量的 iptables 规则，为了不让系统规则跟它们混淆，直接关闭系统的规则。

    ```bash
    # 关闭 firewalld 服务
    systemctl stop firewalld
    systemctl disable firewalld
    # 关闭 iptables 服务（Centos7.5 中不用做这个操作）
    systemctl stop iptables
    systemctl disable iptables
    ```

4. 禁用 SELinux。

    SELinux 是 linux 系统下的一个安全服务，如果不关闭它，在安装集群中会产生各种各样的奇葩问题。

    ```bash
    vim /etc/selinux/config
    # 修改其中的 SELINUX 这一项为 disabled
    -----------
    SELINUX=disabled
    -----------
    ```

5. 禁用 swap 分区。

    swap 分区指的是虚拟内存分区，它的作用是在物理内存使用完之后，将磁盘空间虚拟成内存来使用。

    启用 swap 设备会对系统的性能产生非常负面的影响，因此 K8s 要求每个节点都要禁用 swap 设备。

    ```bash
    vim /etc/fstab
    # 接下来注释掉 swap 分区这一行内容
    # 一般就是 fstab 的最后一行
    ```

6. 修改 linux 的内核参数。

    通过修改 linux 内核参数，添加网桥过滤和地址转发功能。

    ```bash
    vim /etc/sysctl.d/kubernetes.conf
    # 添加如下的配置
    ---------
    net.bridge.bridge-nf-call-ip6tables = 1
    net.bridge.bridge-nf-call-iptables = 1
    net.ipv4.ip_forward = 1
    ---------
    
    # 重新加载配置
    sysctl -p
    
    # 加载网桥过滤模块
    modprobe br_netfilter
    
    # 查看网桥过滤模块是否加载成功
    lsmod | grep br_netfilter
    ```

7. 配置 ipvs 功能。

    在 K8s 中 Service 有两种代理模型，一种是基于 iptables 的，一种是基于 ipvs 的。

    两者比较的话，ipvs 的性能明显要高一些，但是如果要使用它，需要手动加载 ipvs 模块。

    ```bash
    # 安装 ipset 和 ipvsadm
    yum install ipset ipvsadmin -y
    
    # 添加需要加载的模块写入脚本文件
    cat <<EOF >  /etc/sysconfig/modules/ipvs.modules
    #!/bin/bash
    modprobe -- ip_vs
    modprobe -- ip_vs_rr
    modprobe -- ip_vs_wrr
    modprobe -- ip_vs_sh
    modprobe -- nf_conntrack_ipv4
    EOF
    
    # 为脚本文件添加执行权限
    chmod +x /etc/sysconfig/modules/ipvs.modules
    
    # 执行脚本文件
    /bin/bash /etc/sysconfig/modules/ipvs.modules
    
    # 查看对应的模块是否加载成功
    lsmod | grep -e ip_vs -e nf_conntrack_ipv4
    ```

8. 重启服务器。

    上面的步骤完成之后，需要重启 linux 操作系统。

    ```bash
    reboot
    ```

## 3. 安装 Containerd

新版的 K8s 已经不支持 Docker-shim 了，所以现在我们就不安装 Docker 了，而是使用 Containerd。

### 3.1 Containerd 的下载

```bash
# 下载 Containerd
wget https://github.com/containerd/containerd/releases/download/v1.7.22/containerd-1.7.22-linux-amd64.tar.gz
# 这个压缩包里面就是一个 bin 目录，里面装着一些可执行文件，例如 containerd、ctr 之类的
# 所以我们可以直接将压缩包解压到 /usr/local，然后这些可执行文件就会自动加载到 /usr/local/bin 里面
tar -zxvf containerd-1.7.22-linux-amd64.tar.gz -C /usr/local

# 通过 systemd 启动 containerd
vim /etc/systemd/system/containerd.service
# 写入下面的内容（内容来自于 https://github.com/containerd/containerd/blob/main/containerd.service）
-------------------------------------------------------------------------------
[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity

# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
-------------------------------------------------------------------------------

# 加载配置、启动
systemctl daemon-reload
systemctl enable containerd

```

### 3.2 Containerd 初始化配置

```bash
# 生成 Containerd 初始化配置
mkdir /etc/containerd
containerd config default > /etc/containerd/config.toml

# 修改配置文件，需要修改三个地方
vim /etc/containerd/config.toml
---------------------------------------------------------------------------------
# 如果要配置 K8s 的话，就要修改这里
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
  SystemdCgroup = true
# 如果容器启动不起来，爆出 sandbox_image 之类的东西，可以修改这里
  sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.9"
# 修改镜像加速文件地址
  config_path = "/etc/containerd/certs.d"
---------------------------------------------------------------------------------
```

### 3.3 Containerd 镜像加速地址配置

```bash
# docker hub镜像加速
mkdir -p /etc/containerd/certs.d/docker.io
cat > /etc/containerd/certs.d/docker.io/hosts.toml << EOF
server = "https://docker.io"
[host."https://1ecf599359e64520bd04701e6d7184e8.mirror.swr.myhuaweicloud.com"]
  capabilities = ["pull", "resolve"]

[host."https://le2c3l3b.mirror.aliyuncs.com"]
  capabilities = ["pull", "resolve"]

[host."https://docker.m.daocloud.io"]
  capabilities = ["pull", "resolve"]

[host."https://reg-mirror.qiniu.com"]
  capabilities = ["pull", "resolve"]

[host."https://registry.docker-cn.com"]
  capabilities = ["pull", "resolve"]

[host."http://hub-mirror.c.163.com"]
  capabilities = ["pull", "resolve"]

EOF

# registry.k8s.io镜像加速
mkdir -p /etc/containerd/certs.d/registry.k8s.io
tee /etc/containerd/certs.d/registry.k8s.io/hosts.toml << 'EOF'
server = "https://registry.k8s.io"

[host."https://k8s.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# docker.elastic.co镜像加速
mkdir -p /etc/containerd/certs.d/docker.elastic.co
tee /etc/containerd/certs.d/docker.elastic.co/hosts.toml << 'EOF'
server = "https://docker.elastic.co"

[host."https://elastic.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# gcr.io镜像加速
mkdir -p /etc/containerd/certs.d/gcr.io
tee /etc/containerd/certs.d/gcr.io/hosts.toml << 'EOF'
server = "https://gcr.io"

[host."https://gcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# ghcr.io镜像加速
mkdir -p /etc/containerd/certs.d/ghcr.io
tee /etc/containerd/certs.d/ghcr.io/hosts.toml << 'EOF'
server = "https://ghcr.io"

[host."https://ghcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# k8s.gcr.io镜像加速
mkdir -p /etc/containerd/certs.d/k8s.gcr.io
tee /etc/containerd/certs.d/k8s.gcr.io/hosts.toml << 'EOF'
server = "https://k8s.gcr.io"

[host."https://k8s-gcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# mcr.m.daocloud.io镜像加速
mkdir -p /etc/containerd/certs.d/mcr.microsoft.com
tee /etc/containerd/certs.d/mcr.microsoft.com/hosts.toml << 'EOF'
server = "https://mcr.microsoft.com"

[host."https://mcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# nvcr.io镜像加速
mkdir -p /etc/containerd/certs.d/nvcr.io
tee /etc/containerd/certs.d/nvcr.io/hosts.toml << 'EOF'
server = "https://nvcr.io"

[host."https://nvcr.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# quay.io镜像加速
mkdir -p /etc/containerd/certs.d/quay.io
tee /etc/containerd/certs.d/quay.io/hosts.toml << 'EOF'
server = "https://quay.io"

[host."https://quay.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# registry.jujucharms.com镜像加速
mkdir -p /etc/containerd/certs.d/registry.jujucharms.com
tee /etc/containerd/certs.d/registry.jujucharms.com/hosts.toml << 'EOF'
server = "https://registry.jujucharms.com"

[host."https://jujucharms.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF

# rocks.canonical.com镜像加速
mkdir -p /etc/containerd/certs.d/rocks.canonical.com
tee /etc/containerd/certs.d/rocks.canonical.com/hosts.toml << 'EOF'
server = "https://rocks.canonical.com"

[host."https://rocks-canonical.m.daocloud.io"]
  capabilities = ["pull", "resolve", "push"]
EOF
```

### 3.4 验证安装结果

```bash
# 重启 Containerd
systemctl restart containerd
# 验证
ctr version
```

### 3.5 安装 nerdctl（非必须）

安装 nerdctl 的目的是改变 Containerd 的命令行操作方式。因为 ctr 命令太难用了，换成 nerdctl，操作的命令就与 Docker 的命令特别相似。（但是如果单纯操作 K8s，也可以不安装 nerdctl）。

```bash
# 下载 nerdctl
wget https://github.com/containerd/nerdctl/releases/download/v1.7.7/nerdctl-1.7.7-linux-amd64.tar.gz

# 解压，只需要把其中的 nerdctl 可执行文件放到 /usr/local/bin 就行了
tar -zxvf nerdctl-1.7.7-linux-amd64.tar.gz nerdctl
mv nerdctl /usr/local/bin

# 验证
nerdctl version
```

### 3.6 安装 runc

`runc`  是一个用来运行容器的命令行工具。它是一个底层的容器运行时，可以被像 Containerd 这样的高级运行时调用。

Containerd 自身并不会直接运行容器，它是通过调用 `runc` 来执行容器的低级操作，例如启动、停止、删除等。也就是说，`runc` 是 Containerd 的核心部分，它负责把容器镜像创建为真正运行的容器实例。

```bash
# 从 github 下载 runc
wget https://github.com/opencontainers/runc/releases/download/v1.1.15/runc.amd64

# 把 runc 移动到 /usr/local/sbin 目录下，并命名为 runc
install runc.amd64 -m 755 /usr/local/sbin/runc
```

注：把 `runc`  放到 `/usr/local/sbin` 而不是 `/usr/local/bin` 是因为它是一个系统级的工具，需要管理员权限来运行。一般情况下，普通用户不需要也不应该直接使用它，所以将其放在 `/usr/local/sbin` 中，可以更好地反映它的用途和权限需求。

### 3.7 安装 cni-plugins

基础的 cni 插件可以实现单主机的多个容器之间的网络通信。但是如果要部署 K8s 集群，也就是说如果要进行多个主机之间容器的通信的话，就需要使用 Flannel、Calico 这些网络插件。

```bash
# 下载 cni-plugins
wget https://github.com/containernetworking/plugins/releases/download/v1.5.1/cni-plugins-linux-amd64-v1.5.1.tgz

# 安装 cni-plugins 到 /opt
mkdir -p /opt/cni/bin
tar zxvf cni-plugins-linux-amd64-v1.5.1.tgz -C /opt/cni/bin
```

### 3.8 安装 crictl

`crictl` 并不是必须安装的，但是强烈建议安装它，因为它能为容器的管理和调试提供便利。

在 K8s 环境当中，最好同时安装 `nerdctl` 和 `crictl`。这样可以根据需求选择最合适的工具：

- 使用 `crictl` 来调试和排查 K8s 集群问题。
- 使用 `nerdctl` 来执行容器的管理和构建任务。

```bash
# 下载 crictl
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.31.1/crictl-v1.31.1-linux-amd64.tar.gz

# 安装 crictl
tar zxvf crictl-v1.31.1-linux-amd64.tar.gz
mv crictl /usr/local/bin

# 配置 crictl
cat >>  /etc/crictl.yaml << EOF
runtime-endpoint: unix:///var/run/containerd/containerd.sock
image-endpoint: unix:///var/run/containerd/containerd.sock
timeout: 10
debug: true
EOF

# 重启 containerd
systemctl restart containerd
```

## 4. 安装 K8s 组件

```bash
# 由于 K8s 的镜像源在国外，速度比较慢，这里换成国内的镜像源
vim /etc/yum.repos.d/kubernetes.repo
# 添加下面的配置
-------------------
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
       http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
-------------------

# 安装 kubeadm、kubelet 和 kubectl
# 这里安装的是 kubelet 1.28.2 版本
yum install kubeadm-1.28.2-0 kubelet-1.28.2-0 kubectl-1.28.2-0 -y

# 编辑 kubelet 的 cgroup
vim /etc/sysconfig/kubelet
# 添加下面的配置
------------------------
KUBELET_CGROUP_ARGS="--cgroup-driver=systemd"
KUBE_PROXY_MODE="ipvs"
------------------------

# 设置 kubelet 开机自启动
systemctl enable kubelet
```

## 5. 集群初始化

==**下面的操作只需要在 master 上面完成就可以！**==

```bash
# 首先查看 kubeadm 的版本
kubeadm version
# 这里就会输出我的版本是 v1.28.2 的
```

然后对 kubeadm 进行配置：

```bash
# 生成默认配置文件
kubeadm config print init-defaults > kubeadm.yaml

# 编辑配置文件
vim kubeadm.yaml
----------------------------------------------------------------------
apiVersion: kubeadm.k8s.io/v1beta3
bootstrapTokens:
- groups:
  - system:bootstrappers:kubeadm:default-node-token
  token: abcdef.0123456789abcdef
  ttl: 24h0m0s
  usages:
  - signing
  - authentication
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 192.168.100.140  # 修改为宿主机ip
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///var/run/containerd/containerd.sock
  imagePullPolicy: IfNotPresent
  name: master   # 修改为宿主机名
  taints: null
---
apiServer:
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta3
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns: {}
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.aliyuncs.com/google_containers # 修改为阿里镜像
kind: ClusterConfiguration
kubernetesVersion: 1.28.2  # kubeadm的版本为多少这里就修改为多少
networking:
  dnsDomain: cluster.local
  serviceSubnet: 10.96.0.0/12
  podSubnet: 10.244.0.0/16   # 设置pod网段
scheduler: {}

###添加内容：配置kubelet的CGroup为systemd
---
kind: KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
cgroupDriver: systemd
----------------------------------------------------------------------
```

然后下载相应的镜像，并进行初始化：

```bash
# 下载镜像
kubeadm config images pull --image-repository=registry.aliyuncs.com/google_containers  --kubernetes-version=v1.28.2

### 这里不知道为啥还需要重新执行这个：加载网桥过滤模块
modprobe br_netfilter

# 集群初始化modprobe br_netfilter
kubeadm init --config kubeadm.yaml

# 初始化完成之后，就根据提示对 master 和 node 做对应的操作就行
# master:
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config
# node:
kubeadm join 192.168.100.140:6443 --token abcdef.0123456789abcdef \
        --discovery-token-ca-cert-hash sha256:0644a865914a18da57dcef71860fe4efa69908e7f2ec30094ed04784b58cb0f1


# 查看集群状态，此时的集群状态为 NotReady，这是因为还没有配置网络插件
[root@master ~]# kubectl get nodes
NAME     STATUS     ROLES           AGE     VERSION
master   NotReady   control-plane   2m43s   v1.28.2
node1    NotReady   <none>          18s     v1.28.2
node2    NotReady   <none>          12s     v1.28.2
```

## 6. 安装网络插件

kubernetes支持多种网络插件，比如flannel、calico、canal等等，任选一种使用即可，本次选择flannel。

==**下面的操作都只需要在 master 上面执行！**==

```bash
# 要想执行成功，还要做一个操作（但是现在还不知道原理）
vim /etc/kubernetes/manifests/kube-controller-manager.yaml
# command 中加入如下的命令
-------------------------------------------------------------
    - --allocate-node-cidrs=true
    - --cluster-cidr=10.244.0.0/16
-------------------------------------------------------------
```

```bash
# 下载 flannel
wget https://github.com/flannel-io/flannel/blob/master/Documentation/kube-flannel.yml

# 将网络模式从 vxlan 改为 host-gw
sed -i 's#vxlan#host-gw#' ./kube-flannel.yml

# 加载 flannel
kubectl apply -f kube-flannel.yml
```



## 7. 验证

```bash
# 部署 nginx
kubectl create deployment nginx --image=nginx:latest

# 暴露端口
kubectl expose deployment nginx --port=80 --type=NodePort

# 查看服务状态
kubectl get pods,service
------------------------------------------------------------------------------------------
NAME                         READY   STATUS    RESTARTS   AGE
pod/nginx-56fcf95486-2nz72   1/1     Running   0          30s

NAME                 TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
service/kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP        61m
service/nginx        NodePort    10.100.226.160   <none>        80:31729/TCP   20s
------------------------------------------------------------------------------------------

# 访问 nginx 服务
# 用主机上的浏览器访问：192.168.100.140:31729
```













