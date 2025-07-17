# Docker

## 安装过程

### Centos

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

高版本 Centos 可以直接使用 `dnf install docker` 安装 Docker。

### Centos9（WSL）

```bash
# 卸载现有 docker 相关组件
sudo dnf remove docker docker-client docker-common podman-docker

# 安装必要依赖
sudo dnf install dnf-plugins-core

# 添加 docker 仓库
sudo tee /etc/yum.repos.d/docker-ce.repo <<EOF
[docker-ce-stable]
name=Docker CE Stable - \$basearch
baseurl=https://mirrors.aliyun.com/docker-ce/linux/centos/9/x86_64/stable
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/docker-ce/linux/centos/gpg
EOF

# 安装 docker engine
sudo dnf install docker-ce docker-ce-cli containerd.io

# 启动 docker 服务
sudo systemctl enable --now docker

# 验证安装
systemctl status docker
```



### Ubuntu

```bash
apt-get update
    
curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/ \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update

apt-get install docker-ce docker-ce-cli containerd.io

systemctl enable --now docker
```

## Docker 设置加速镜像

一般情况下的设置命令：

```bash
mkdir -p /etc/docker
cat <<EOF >  /etc/docker/daemon.json
{
  "registry-mirrors": [ 
	"https://1ecf599359e64520bd04701e6d7184e8.mirror.swr.myhuaweicloud.com",
	"https://le2c3l3b.mirror.aliyuncs.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

如果是在 Kubernetes 中使用 Docker 作为容器运行时，就要多加上一个设置：

```bash
mkdir -p /etc/docker
cat <<EOF >  /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "registry-mirrors": [ 
	"https://1ecf599359e64520bd04701e6d7184e8.mirror.swr.myhuaweicloud.com",
	"https://le2c3l3b.mirror.aliyuncs.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

其中的 `exec-opts` 就是针对于 Kubernetes 的设置。

注意，其中我设置的加速镜像地址是华为云的地址，因为之前我的阿里云的加速地址莫名不好用了，如果要设置也可以，我的阿里云的加速地址是：`https://le2c3l3b.mirror.aliyuncs.com`。









