# Containerd 学习笔记

为什么要学习 Containerd 呢？因为在新版的 K8s 中，已经不支持 Docker 了，所以就有必要去学学 Containerd 的知识。

实际上就简单使用的话，或者说入门的时候用的话，Containerd 和 Docker 都是差不多的。都是在捣鼓 image、containerd 这些东西。

## 1. Containerd 的配置

1. 生成默认配置文件

    ```bash
    containerd config default > /etc/containerd/config.toml
    ```

2. 修改配置文件中的 `SystemCgroup` 和 `sandbox_image` 这些东西（如果有必要）。

    ```bash
    # 如果要配置 K8s 的话，就要修改这里
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
      SystemdCgroup = true
    # 如果容器启动不起来，爆出 sandbox_image 之类的东西，可以修改这里
      sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.9"
      
    # 如果上面修改了哪里，一定要重启一下 containerd
    systemctl restart containerd
    ```

3. 修改配置文件中的 `config_path` 。（这里修改之后，用 ctr 命令还是不会生效，不知道是为啥）

    ```bash
    config_path = "/etc/containerd/certs.d"
    ```

4. 给 `/etc/containerd/certs.d` 里面加点镜像的地址。

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

至此，containerd 的网络配置就结束了。

但是直接使用 `ctr` 命令来拉取镜像的话，还是拉取不到镜像的。到这里我们分辨一下，之后拉取镜像是使用 `ctr`  还是使用 `cerdctl` 进行拉取。

## 2. 使用 ctr 拉取镜像

如果要使用 `ctr` 命令拉取镜像，那么在进行 pull 操作的时候，就要加上 `--hosts-dir=/etc/containerd/certs.d`  才可以拉取。

例如：

```bash
ctr image pull --hosts-dir=/etc/containerd/certs.d docker.io/library/nginx:latest
```

如果要确定是否真的使用了镜像加速，可以增加 `--debug=true` 参数，所以命令就变成了：

```bash
ctr --debug=true image pull --hosts-dir=/etc/containerd/certs.d docker.io/library/nginx:latest
```

如果感觉这样太麻烦，也可以通过给命令起别名的方法，简化命令的操作。

```bash
# 在 ~/.bashrc 中加入下面的内容
alias ctr-pull="ctr image pull --hosts-dir=/etc/containerd/certs.d"

# 之后拉取镜像就可以直接这样拉取
ctr-pull docker.io/library/nginx:latest
```

但是这里有个问题，那就是不好指定命名空间。如果要指定命名空间的话，还是要使用原版的 ctr 命令。或者是也可以重新加上一些专用的命令别名。这里说命名空间的问题，主要是因为 k8s 的镜像，好像都是在 k8s.io 命名空间下面的。

**注意注意注意！**Containerd 中拉取镜像和 Docker 中很不一样的一个点是，Containerd 拉取镜像的时候，镜像的名字是一定要写全的。

- 比如说在 Docker 中，拉取 nginx 的话，可以直接写：`docker pull nginx:latest`
- 但是在 Containerd 中，就要写：`ctr-pull docker.io/library/nginx:latest`
- 一般情况下，镜像的地址都是在 `[image:version]` 的前面直接加上 `docker.io/library` 就行啦

## 3. 使用 nerdctl 拉取镜像

 ### 3.1 nerdctl 的安装方式

先从 github 上面下载下来：

```bash
wget https://github.com/containerd/nerdctl/releases/download/v1.7.7/nerdctl-1.7.7-linux-amd64.tar.gz
```

然后直接把那个可执行文件丢到 `/usr/local/bin`  里面就行了。

### 3.2 nerdctl 的使用

实际上，创建 nerdctl 的目的就是像使用 Docker 一样去使用 nerdctl。所以 nerdctl 的命令基本上和 Docker 是一样的。

#### 版本-version

```bash
nerdctl --version
```

#### 镜像-image

```bash
# 查看镜像
nerdctl images

# 拉取镜像
nerdctl pull <image_name>:<tag>

# 给镜像加标签
nerdctl tag <old-image>:<old-version> <new-image>:<new-version>

# 删除镜像的标签
nerdctl rmi <image>:<version>
```

#### 容器-containerd

```bash
# 运行容器
nerdctl run -d <image_name>:<tag> --name <container_name>

# 查看正在运行的容器
nerdctl ps

# 停止容器
nerdctl stop <container_name>

# 删除容器
nerdctl rm <container_name>

# 查看容器日志
nerdctl logs <container_name>

# 进入容器
nerdctl exec -it <container_name> /bin/bash
```

#### 命名空间-namespace

只需要在前面的命令的基础上，在 `nerdctl` 后面加上一个 `--namespace <my-namespace>` 就行啦。

## 4. ctr 命令使用

### 4.1 镜像管理

查看镜像：

```bash
ctr images ls
```

下载镜像：

```bash
ctr images pull docker.io/library/nginx:latest --hosts-dir="/etc/containerd/certs.d"
# 说明：这里使用 ctr 命令 pull 镜像的时候，不能直接把镜像的名字写成 nginx:latest
```

镜像挂载：

```bash
ctr images mount docker.io/library/nginx:alpine /mnt
ls /mnt		# 查看挂载
umount /mnt	# 卸载
```

镜像导出：

```bash
ctr images export nginx.img docker.io/library/nginx:alpine
```

镜像导入：

```bash
ctr images import nginx.img
```

镜像删除（tag 删除）：

```bash
ctr images remove docker.io/library/nginx:alpine
```

镜像打 tag：

```bash
ctr images tag docker.io/library/nginx:alpine nginx:alpine
```

### 4.2 容器管理

查看容器：

```bash
ctr container ls
```

查看任务：

```bash
ctr task ls
```

创建静态容器：

```bash
ctr container create docker.io/library/nginx:alpine nginx1
```

查看容器详细信息：

```bash
ctr container info nginx1
```

静态容器启动为动态容器：

```bash
ctr task start -d nginx1
# -d 表示 daemon 或者后台的意思，否则会卡住终端
```

查看容器的进程（都是物理机的进程）：

```bash
ctr task ps nginx1
```

进入容器操作：

```bash
ctr task exec --exec-id ${RANDOM} -t nginx1 /bin/sh
```

直接运行一个动态容器：

```bash
ctr run -d --net-host docker.io/library/nginx:alpine nginx2
# -d 代表 daemon，后台运行
# -net-host 代表容器的 IP 就是宿主机的 IP（相当于 docker 里的 host 类型网络）
```

暂停容器：

```bash
ctr task pause nginx2
```

恢复容器：

```bash
ctr task resume nginx2
```

停止容器：

（`kill` 容器默认是给容器发送一个 `SIGTERM` 信号，通常用于优雅地终止进程。但是如果容器中的 `sh` 或者其他命令没有响应 `SIGTERM`，该信号就无法终止进程。这种情况下可以指定使用 `SIGKILL` 信号，强制终止任何进程。）

```bash
ctr task kill nginx2
ctr task kill --signal SIGKILL busybox1
```

删除容器：

```bash
ctr task delte nginx2
# 比如先停止 task 或者先删除 task 之后，才能删除容器
```

### 4.3 容器挂载

把宿主机目录挂载到 containerd 容器中，实现容器数据持久化存储。

```bash
ctr container create docker.io/library/busybox:latest busybox3 --mount type=bind,src=/tmp,dst=/hostdir,options=rbind:rw
```



















