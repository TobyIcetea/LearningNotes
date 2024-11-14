# Docker

## 安装过程

1. 设置 yum 源，添加阿里仓库。

    ```bash
    yum install -y yum-utils
    yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
    ```

2. 查看有哪些版本可以用。

    ```bash
    yum list docker-ce --showduplicates | sort -r
    ```

    选择其中的一个版本安装就行。（安装命令是：`yum install docker-ce-版本`）

    ```bash
    yum install -y docker-ce-26.1.4
    ```

3. 启动 Docker 并设置开机自启。

    ```bash
    systemctl start docker
    systemctl enable docker
    ```

4. 通过查看版本，看是否安装成功。

    ```bash
    docker --version
    ```

## Docker 设置加速镜像

一般情况下的设置命令：

```bash
mkdir /etc/docker
cat <<EOF >  /etc/docker/daemon.json
{
  "registry-mirrors": [ "https://1ecf599359e64520bd04701e6d7184e8.mirror.swr.myhuaweicloud.com" ]
}
EOF
```

如果是在 Kubernetes 中使用 Docker 作为容器运行时，就要多加上一个设置：

```bash
mkdir /etc/docker
cat <<EOF >  /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "registry-mirrors": [ "https://1ecf599359e64520bd04701e6d7184e8.mirror.swr.myhuaweicloud.com" ]
}
EOF
```

其中的 `exec-opts` 就是针对于 Kubernetes 的设置。

做完上面的配置之后，都要重启 docker 的 daemon：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

注意，其中我设置的加速镜像地址是华为云的地址，因为之前我的阿里云的加速地址莫名不好用了，如果要设置也可以，我的阿里云的加速地址是：`https://le2c3l3b.mirror.aliyuncs.com`。









