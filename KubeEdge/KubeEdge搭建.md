# KubeEdge 搭建

## 1. 前置条件

### 1.1 K8s

搭建 KubeEdge 的基础是 K8s 集群！这里用到的 K8s 集群以是 K8s 笔记中搭建好的集群为模板机的！

### 1.2 容器运行时

我的集群中使用的容器运行时是 containerd。

修改 containerd 的配置文件中如下的部分：

```bash
vim /etc/containerd/config.toml
-----------------------------------------
[plugins."io.containerd.grpc.v1.cri"]
  sandbox_image = "kubeedge/pause:3.6"
# 拉取这个镜像的命令：crictl pull kubeedge/pause:3.6

# 更新 containerd 的 cgroup 驱动（但是这里不用做，因为前面已经做过了）
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
  ...
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
    SystemdCgroup = true
-----------------------------------------

# 重启 containerd
systemctl restart containerd
```

> 后面记得两个事儿：
>
> - 如果你使用Keadm安装EdgeCore时，你需要设置--remote-runtime-endpoint=unix:///run/containerd/containerd.sock。

## 2. 使用 Keadm 进行部署

### 设置云端（KubeEdge 主节点）

首先从官网下载好 keadm：

```bash
wget https://github.com/kubeedge/kubeedge/releases/download/v1.18.1/keadm-v1.18.1-linux-amd64.tar.gz
```

之后将解压出来的文件夹里面的可执行文件复制到 `/usr/local/bin` 里面。然后可以执行 `keadm version` 命令进行验证，如果能正确输出版本，就说明安装成功了。

接下来下载一些必要的文件：

```bash
wget https://raw.githubusercontent.com/kubeedge/kubeedge/refs/heads/master/build/tools/cloudcore.service
wget https://github.com/kubeedge/kubeedge/releases/download/v1.18.1/kubeedge-v1.18.1-linux-amd64.tar.gz
```

然后将下载下来的文件都放到 `/etc/kubeedge` 中（需要先创建这个文件夹）。

接下来执行部署命令（其中的 `advertise-address` 是自己 master 节点的 ip）：

```bash
keadm init --advertise-address=192.168.100.140 --kubeedge-version=v1.18.1
```

边缘节点加入云端节点需要通过 token 认证方式，使用如下命令获取边缘节点加入集群的 token：

```bash
keadm gettoken
```

例如这里我自己获取到的 token 是：

```
828eb91bb309b3a32dbb6622b13842653f4f5c71656eea81248cf970f2d33844.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkxNTYyOTJ9.dNnBueSgxgM9TlWbOmqHm9fO6YZ-5webgNHaOzreki0
```



### 设置边缘端（KubeEdge 工作节点）

先在边缘端下载 containerd。

边缘节点也要先下载 keadm，并解压：

```bash
wget https://github.com/kubeedge/kubeedge/releases/download/v1.18.1/keadm-v1.18.1-linux-amd64.tar.gz
```

解压出来之后，将其中的可执行文件放到 `/usr/local/bin` 目录下。如果执行 `keadm version` 不报错，就说明安装成功。

> 中间会有一个拉取镜像的操作，但是我们也可以直接拉取（失败了再尝试这样，一般不用这样做）：
>
> ```bash
> crictl pull kubeedge/installation-package:v1.18.1
> ```

接下来使用如下命令加入集群（其中 `cloudcore-ipport` 要设置成自己的 ip，端口就设置成 10000 就行。token 用上面命令生成的 token）：

```bash
TOKEN=4c86125c6fe4b4cdc1d0b7a866474613e2658114cc4c34aba79e9edecfa7ab37.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjkxNTE5ODV9.Cdgqx5B15M_vU-BSg00sHoJdD-5uUSDQ7y_z2a6V-3w
SERVER=192.168.100.140:10000

keadm join --cloudcore-ipport=$SERVER \
	--kubeedge-version=v1.18.1 \
	--cgroupdriver=systemd \
	--token=$TOKEN
```

之后看到类似 `KubeEdge edgecore is running` 之类的话，就说明边缘端也跑起来了。





```bash
# 日志中会报错，edgecore 不可以和 kubelet 一起运行，然后我们关掉 kubelet，再重启 edgecore
sudo systemctl stop kubelet
sudo systemctl disable kubelet
sudo systemctl restart edgecore.service

# 接下来还会报错，edgecore 不可以和 kube-peoxy 一起运行，但是我们的 service 中本来就没有 kube-proxy，所以我们杀掉进程中的 kube-proxy
ps aux | grep kube-proxy
sudo pkill -f kube-proxy

# 接下来报错：edgecore 找不到文件 /etc/kubeedge/certs/server.crt
# 但是这个错误太难排查了，所以我转去继续搞官方文档的启用 kubectl logs 功能
# 下面在 master 上执行
export CLOUDCOREIPS="192.168.100.140"
cd /etc/kubeedge/
wget https://raw.githubusercontent.com/kubeedge/kubeedge/refs/heads/master/build/tools/certgen.sh
bash /etc/kubeedge/certgen.sh stream

```







