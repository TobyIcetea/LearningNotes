# Kubernetes 二进制部署

## 一、 集群环境准备

### 1.1 主机规划

| 主机IP地址      | 主机名      | 主机配置 | 主机角色      | 软件列表                                                     |
| --------------- | ----------- | -------- | ------------- | ------------------------------------------------------------ |
| 192.168.100.12  | k8s-master1 | 2C4G     | master        | kube-apiserver、kube-controller-manager、kube-scheduler、etcd、kubelet、kube-proxy、Containerd、runc |
| 192.168.100.13  | k8s-master2 | 2C4G     | master        | kube-apiserver、kube-controller-manager、kube-scheduler、etcd、kubelet、kube-proxy、Containerd、runc |
| 192.168.100.14  | k8s-master3 | 2C4G     | master        | kube-apiserver、kube-controller-manager、kube-scheduler、etcd、kubelet、kube-proxy、Containerd、runc |
| 192.168.100.15  | k8s-worker1 | 2C4G     | worker        | kubelet、kube-proxy、Containerd、runc                        |
| 192.168.100.10  | ha1         | 1C2G     | LB            | haproxy、keepalived                                          |
| 192.168.100.11  | ha2         | 1C2G     | LB            | haproxy、keepalived                                          |
| 192.168.100.100 | /           | /        | VIP（虚拟IP） |                                                              |

### 1.2 软件版本

| 软件名称     | 版本             | 备注      |
| ------------ | ---------------- | --------- |
| CentosStream | kernel版本：5.14 |           |
| kubernetes   | v1.32.3          |           |
| etcd         | v3.5.19          |           |
| calico       | v3.29.2          |           |
| coredns      | v1.12.0          |           |
| containerd   | v1.7.26          |           |
| runc         | v1.2.5           |           |
| haproxy      | 5.18             | YUM源默认 |
| keepalived   | 3.5              | YUM源默认 |

### 1.3 网络分配

| 网络分配     | 网段             | 备注 |
| ------------ | ---------------- | ---- |
| Node 网络    | 192.168.100.0/24 |      |
| Service 网络 | 10.96.0.0/16     |      |
| Pod 网络     | 10.244.0.0/16    |      |

## 二、主机部署

### 2.1 主机名设置

先设置主机的网络：

```bash
vim /etc/NetworkManager/system-connections/ens160.nmconnection
----------------------------------------------------------------------
# 里面的 ipv4 部分这样设置
# 主要就修改里面的 address 部分的 IP 地址，具体根据上面的规划来设置
[ipv4]
address=192.168.100.10/24
dns=8.8.8.8;8.8.4.4;
gateway=192.168.100.2
ignore-auto-dns=true
method=manual
----------------------------------------------------------------------

# 重启网络，让配置生效
nmcli connection reload
nmcli connection down ens160
nmcli connection up ens160
# 查看配置是否生效
ip addr
```

设置主机名：

```bash
# 这里还是不同主机的设置不同
hostnamectl set-hostname k8s-ha1
hostnamectl set-hostname k8s-ha2
hostnamectl set-hostname k8s-master1
hostnamectl set-hostname k8s-master2
hostnamectl set-hostname k8s-master3
hostnamectl set-hostname k8s-worker1
```

### 2.2 主机与 IP 地址解析

```bash
cat << EOF > /etc/hosts
192.168.100.10 ha1
192.168.100.11 ha2
192.168.100.12 k8s-master1
192.168.100.13 k8s-master2
192.168.100.14 k8s-master3
192.168.100.15 k8s-worker1
EOF
```

### 2.3 主机安全设置

关闭防火墙和 SELINUX：

```bash
# 关闭防火墙
systemctl stop firewalld
systemctl disable firewalld
firewall-cmd --state

# 关闭 SELINUX
setenforce 0
sed -ri 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
sestatus
```

### 2.4 交换分区设置

关闭所有主机的交换分区（只要部署 kubelet 的节点都要关闭）：

```bash
swapoff -a
sed -ri 's/.*swap.*/#&/' /etc/fstab
echo "vm.swappiness=0" >> /etc/sysctl.conf
sysctl -p
```

### 2.5 主机系统时间同步

Centos Stream（RHEL9）中不推荐使用 ntpdate，所以我们使用 chrony 进行时间同步。

如果就是 Centos Stream，这一步其实可以不用做，因为原本就是好的。

```bash
# 安装软件（但是实际已经安装好了）
dnf install chrony
systemctl enable --now chronyd
systemctl status chronyd
# 手动同步时间
chronyc makestep
```

### 2.6 主机系统优化

给主机做一个高并发 limit 优化：

```bash
# 临时优化
ulimit -SHn 65535

# 永久优化
cat <<EOF >> /etc/security/limits.conf
* soft nofile 655360
* hard nofile 131072
* soft nproc 655350
* hard nproc 655350
* soft memlock unlimited
* hard memlock unlimited
EOF
```

### 2.7 ipvs 管理工具安装及模块加载

kube-proxy 是 Kubernetes 中负责实现服务负载均衡的组件，支持多种模式，包括 `userspace`、`iptables` 和 `ipvs`。

IPVS 是基于 Linux 内核的负载均衡技术，相比 `iptables` 模式，它具有更高的性能和更多的延迟，特别适合大规模集群。

> 为所有节点安装。

```bash
dnf install -y ipvsadm ipset sysstat conntrack libseccomp
```

临时加载模块（所有节点配置 ipvs 模块，在内核 4.19+ 版本 nf_conntrack_ipv4 已经改为 nf_conntrack，4.18 及以下的 linux 内核使用 nf_conntrack_ipv4 即可）：

```bash
modprobe -- ip_vs
modprobe -- ip_vs_rr
modprobe -- ip_vs_wrr
modprobe -- ip_vs_sh
modprobe -- nf_conntrack
```

永久加载模块：

```bash
cat >/etc/modules-load.d/ipvs.conf <<EOF
ip_vs
ip_vs_lc
ip_vs_wlc
ip_vs_rr
ip_vs_wrr
ip_vs_lblc
ip_vs_lblcr
ip_vs_dh
ip_vs_sh
ip_vs_fo
ip_vs_nq
ip_vs_sed
ip_vs_ftp
ip_vs_sh
nf_conntrack
ip_tables
ip_set
xt_set
ipt_set
ipt_rpfilter
ipt_REJECT
ipip
EOF
```

### 2.8 加载 containerd 相关内核模块

> 集群中的节点做。

临时加载模块：

```bash
modprobe overlay
modprobe br_netfilter
```

永久加载模块：

```bash
cat << EOF > /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
```

设置为开机自启动：

```bash
systemctl enable --now systemd-modules-load.service
```

### 2.9 Linux 内核升级

所有节点都需要做 Linux 内核升级，重新安装操作系统内核。

但是我们使用的系统本来就比较新，所以这一步不用做。推荐使用 Linux 内核 5+ 版本。

### 2.10 Linux 内核优化

> 所有节点都要做。

设置一些内核参数，来优化 Kubernnetes 集群的网络性能和资源管理。

```bash
cat <<EOF > /etc/sysctl.d/k8s.conf
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
fs.may_detach_mounts = 1
vm.overcommit_memory=1
vm.panic_on_oom=0
fs.inotify.max_user_watches=89100
fs.file-max=52706963
fs.nr_open=52706963
net.netfilter.nf_conntrack_max=2310720

net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_keepalive_intvl =15
net.ipv4.tcp_max_tw_buckets = 36000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_max_orphans = 327680
net.ipv4.tcp_orphan_retries = 3
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 16384
net.ipv4.ip_conntack_max = 131072
net.ipv4.tcp_max_syn_backlog = 16384
net.ipv4.tcp_timestamps = 0
net.core.somaxconn = 16384
EOF

sysctl --system
```

所有节点配置完内核之后，重启所有节点，保证重启后内核依旧加载。

```bash
reboot
```

重启后查看模块加载情况：

```bash
# ipvs
lsmod | grep --color=auto -e ip_vs -e nf_conntrack
# containerd
lsmod | egrep 'br_netfilter|overlay'
```

### 2.11 其他工具安装

如果系统是最小化安装的，可能就需要安装一下这些软件。

> 给集群中的节点安装。

```bash
yum install -y wget jq psmisc vim net-tools telnet yum-utils device-mapper-persistent-data lvm2 git lrzsz
```

## 三、负载均衡器准备

> 如无特殊说明，就在 ha1 和 ha2 节点安装。

### 3.1 安装软件

安装 haproxy 和 keepalived：

```bash
dnf -y install haproxy keepalived
```

### 3.2 HAProxy 配置

```bash
cat >/etc/haproxy/haproxy.cfg<<EOF
global
    maxconn 2000
    ulimit-n 16384
    log 127.0.0.1 local0 err
    stats timeout 30s

defaults
    log global
    mode http
    option httplog
    timeout connect 5000
    timeout client 50000
    timeout server 50000
    timeout http-request 15s
    timeout http-keep-alive 15s

frontend monitor-in
    bind *:33305
    mode http
    option httplog
    monitor-uri /monitor

frontend k8s-master
    bind 0.0.0.0:6443
    bind 127.0.0.1:6443
    mode tcp
    option tcplog
    tcp-request inspect-delay 5s
    default_backend k8s-master

backend k8s-master
    mode tcp
    option tcplog
    option tcp-check
    balance roundrobin
    default-server inter 10s downinter 5s rise 2 fall 2 slowstart 60s maxconn 250 maxqueue 256 weight 100
    server k8s-master1 192.168.100.12:6443 check
    server k8s-master2 192.168.100.13:6443 check
    server k8s-master3 192.168.100.14:6443 check
EOF
```

### 3.3 KeepAlived 配置

ha1：

```bash
cat >/etc/keepalived/keepalived.conf<<EOF
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
    script_user root
    enable_script_security
}
vrrp_script chk_apiserver {
    script "/etc/keepalived/check_apiserver.sh"
    interval 5
    weight -5
    fall 2
    rise 1
}
vrrp_instance VI_1 {
    state MASTER
    interface ens160
    mcast_src_ip 192.168.100.10
    virtual_router_id 51
    priority 100
    advert_int 2
    authentication {
        auth_type PASS
        auth_pass K8SHA_KA_AUTH
    }
    virtual_ipaddress {
        192.168.100.100
    }
    track_script {
        chk_apiserver
    }
}
EOF
```

ha2：

```bash
cat >/etc/keepalived/keepalived.conf<<EOF
! Configuration File for keepalived
global_defs {
    router_id LVS_DEVEL
    script_user root
    enable_script_security
}
vrrp_script chk_apiserver {
    script "/etc/keepalived/check_apiserver.sh"
    interval 5
    weight -5
    fall 2
    rise 1
}
vrrp_instance VI_1 {
    state BACKUP
    interface ens160
    mcast_src_ip 192.168.100.11
    virtual_router_id 51
    priority 99
    advert_int 2
    authentication {
        auth_type PASS
        auth_pass K8SHA_KA_AUTH
    }
    virtual_ipaddress {
        192.168.100.100
    }
    track_script {
        chk_apiserver
    }
}
EOF
```

### 3.4 健康检查脚本

```bash
cat > /etc/keepalived/check_apiserver.sh <<EOF
#!/bin/bash

err=0
for k in $(seq 1 3)
do
    check_code=$(pgrep haproxy)
    if [[ $check_code == "" ]]; then
        err=$(expr $err + 1)
        sleep 1
        continue
    else
        err=0
        break
    fi
done

if [[ $err != "0" ]]; then
    echo "systemctl stop keepalived"
    /usr/bin/systemctl stop keepalived
    exit 1
else
    exit 0
fi
EOF

chmod +x /etc/keepalived/check_apiserver.sh
```

### 3.5 启动服务并验证

```bash
systemctl daemon-reload
systemctl enable --now haproxy keepalived

ip addr show
# 此时在 ha1 上应该会显示 192.168.100.100 这个虚拟 IP，而 ha2 上不会显示
```

## 四、配置免密登录

因为我们后期大部分操作是在 k8s-master1 上执行的，所以这里就只在 k8s-master1 上执行就行。

执行这个操作的目的是让 k8s-master1 可以比较顺利地连接其他节点的 ssh。

```bash
# 生成 ssh 公钥
ssh-keygen

ssh-copy-id root@k8s-master1
ssh-copy-id root@k8s-master2
ssh-copy-id root@k8s-master3
ssh-copy-id root@k8s-worker1

ssh root@k8s-master1
```

## 五、部署 ETCD 集群

> 如无特殊说明，在 k8s-master1 上操作即可。

### 5.1 创建工作目录

```bash
mkdir -p /data/k8s-work
```

### 5.2 获取 cfssl 工具

cfssl 是使用 go 编写，由 CloudFlare 开源的一款 PKI/TLS 工具。主要程序有：

- cfssl，是 cfssl 的命令行工具
- cfssljson，用来从 cfssl 程序获取 json 输出，并将证书、密钥、CSR 和 bundle 写入文件中。

```bash
cd /data/k8s-work
wget https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
wget https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
wget https://pkg.cfssl.org/R1.2/cfssl-certinfo_linux-amd64
```

```bash
chmod +x cfssl*
mv cfssl_linux-amd64 /usr/local/bin/cfssl
mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
mv cfssl-certinfo_linux-amd64 /usr/local/bin/cfssl-certinfo

cfssl version
# Version: 1.2.0
# Revision: dev
# Runtime: go1.6
```

### 5.3 创建 CA 证书

配置 ca 证书请求文件：

```bash
cat > ca-csr.json <<EOF
{
  "CN": "kubernetes",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "Beijing",
      "L": "Beijing",
      "O": "kubekube",
      "OU": "CN"
    }
  ],
  "ca": {
    "expiry": "87600h"
  }
}
EOF
```

创建 ca 证书：

```bash
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
```

这时候下面就出现三个新的文件：`ca.csr`、`ca-key.pem`、`ca.pem`。

配置 ca 证书策略：

```bash
cat > ca-config.json <<EOF
{
  "signing": {
    "default": {
      "expiry": "87600h"
    },
    "profiles": {
      "kubernetes": {
        "usages": [
          "signing",
          "key encipherment",
          "server auth",
          "client auth"
        ],
        "expiry": "87600h"
      }
    }
  }
}
EOF
```

- server auth 表示 client 可以使用该 ca 对 server 提供的证书进行验证。
- client auth 表示 server 可以使用该 ca 对 client 提供的证书进行验证。

### 5.4 创建 etcd 证书

配置 etcd 请求文件：

```bash
cat > etcd-csr.json <<EOF
{
  "CN": "etcd",
  "hosts": [
    "127.0.0.1",
    "192.168.100.12",
    "192.168.100.13",
    "192.168.100.14"
  ],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "Beijing",
      "L": "Beijing",
      "O": "kubekube",
      "OU": "CN"
    }
  ]
}
EOF
```

生成 etcd 证书：

```bash
cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes \
  etcd-csr.json | cfssljson -bare etcd
```

### 5.5 部署 etcd 集群

下载 etcd 软件包：

```bash
wget https://github.com/etcd-io/etcd/releases/download/v3.5.19/etcd-v3.5.19-linux-amd64.tar.gz
```

安装 etcd 软件：

```bash
tar zxvf etcd-v3.5.19-linux-amd64.tar.gz
cp etcd-v3.5.19-linux-amd64/etcd* /usr/local/bin/
```

分发 etcd 软件（把 etcd 的可执行文件访问其他节点上）：

```bash
scp etcd-v3.5.19-linux-amd64/etcd* k8s-master2:/usr/local/bin/
scp etcd-v3.5.19-linux-amd64/etcd* k8s-master3:/usr/local/bin/
```

创建配置文件：

> k8s-master1 执行：

```bash
mkdir /etc/etcd

cat > /etc/etcd/etcd.conf <<EOF
#[Member]
ETCD_NAME="etcd1"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://192.168.100.12:2380"
ETCD_LISTEN_CLIENT_URLS="https://192.168.100.12:2379,http://127.0.0.1:2379"

#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://192.168.100.12:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://192.168.100.12:2379"
ETCD_INITIAL_CLUSTER="etcd1=https://192.168.100.12:2380,etcd2=https://192.168.100.13:2380,etcd3=https://192.168.100.14:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
```

> k8s-master2 执行：

```bash
mkdir /etc/etcd

cat > /etc/etcd/etcd.conf <<EOF
#[Member]
ETCD_NAME="etcd2"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://192.168.100.13:2380"
ETCD_LISTEN_CLIENT_URLS="https://192.168.100.13:2379,http://127.0.0.1:2379"

#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://192.168.100.13:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://192.168.100.13:2379"
ETCD_INITIAL_CLUSTER="etcd1=https://192.168.100.12:2380,etcd2=https://192.168.100.13:2380,etcd3=https://192.168.100.14:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
```

> k8s-master3 执行：

```bash
mkdir /etc/etcd

cat > /etc/etcd/etcd.conf <<EOF
#[Member]
ETCD_NAME="etcd3"
ETCD_DATA_DIR="/var/lib/etcd/default.etcd"
ETCD_LISTEN_PEER_URLS="https://192.168.100.14:2380"
ETCD_LISTEN_CLIENT_URLS="https://192.168.100.14:2379,http://127.0.0.1:2379"

#[Clustering]
ETCD_INITIAL_ADVERTISE_PEER_URLS="https://192.168.100.14:2380"
ETCD_ADVERTISE_CLIENT_URLS="https://192.168.100.14:2379"
ETCD_INITIAL_CLUSTER="etcd1=https://192.168.100.12:2380,etcd2=https://192.168.100.13:2380,etcd3=https://192.168.100.14:2380"
ETCD_INITIAL_CLUSTER_TOKEN="etcd-cluster"
ETCD_INITIAL_CLUSTER_STATE="new"
EOF
```

```bash
说明：
ETCD_NAME: 节点名称，集群中唯一
ETCD_DATA_DIR：数据目录
ETCD_LISTEN_PEER_URLS: 集群通信监听地址
ETCD_LISTEN_CLIENT_URLS: 客户端访问监听地址
ETCD_INITIAL_ADVERTISE_PEER_URLS: 集群通告地址
ETCD_ADVERTISE_CLIENT_URLS: 客户端通告地址
ETCD_INITIAL_CLUSTER: 集群节点地址
ETCD_INITIAL_CLUSTER_TOKEN： 集群 Token
ETCD_INITIAL_CLUSTER_STATE: 加入集群的当前状态，new 是新集群，existing 表示加入已有集群
```

创建服务配置文件：

> 三个节点都执行：

```bash
mkdir -p /etc/etcd/ssl
mkdir -p /var/lib/etcd/default.etcd
```

> k8s-master1 执行：

```bash
cd /data/k8s-work
cp ca*.pem /etc/etcd/ssl
cp etcd*.pem /etc/etcd/ssl

scp ca*.pem k8s-master2:/etc/etcd/ssl
scp etcd*.pem k8s-master2:/etc/etcd/ssl
scp ca*.pem k8s-master3:/etc/etcd/ssl
scp etcd*.pem k8s-master3:/etc/etcd/ssl
```

> 三个节点都执行：

```bash
cat > /etc/systemd/system/etcd.service <<EOF
[Unit]
Description=Etcd Server
After=network.target
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
EnvironmentFile=-/etc/etcd/etcd.conf
WorkingDirectory=/var/lib/etcd/
ExecStart=/usr/local/bin/etcd \
    --cert-file=/etc/etcd/ssl/etcd.pem \
    --key-file=/etc/etcd/ssl/etcd-key.pem \
    --trusted-ca-file=/etc/etcd/ssl/ca.pem \
    --peer-cert-file=/etc/etcd/ssl/etcd.pem \
    --peer-key-file=/etc/etcd/ssl/etcd-key.pem \
    --peer-trusted-ca-file=/etc/etcd/ssl/ca.pem \
    --peer-client-cert-auth \
    --client-cert-auth
Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
```

启动 etcd 集群：

> 三个节点都执行：

```bash
systemctl daemon-reload
systemctl enable --now etcd
systemctl status etcd
```

验证集群状态：

```bash
ETCDCTL_API=3 /usr/local/bin/etcdctl --write-out=table --cacert=/etc/etcd/ssl/ca.pem \
--cert=/etc/etcd/ssl/etcd.pem --key=/etc/etcd/ssl/etcd-key.pem \
--endpoints=https://192.168.100.12:2379,https://192.168.100.13:2379,https://192.168.100.14:2379 endpoint health
```

输出：

```bash
+-----------------------------+--------+-------------+-------+
|          ENDPOINT           | HEALTH |    TOOK     | ERROR |
+-----------------------------+--------+-------------+-------+
| https://192.168.100.12:2379 |   true | 36.590088ms |       |
| https://192.168.100.14:2379 |   true |  38.96666ms |       |
| https://192.168.100.13:2379 |   true | 38.258486ms |       |
+-----------------------------+--------+-------------+-------+
```

或者可以：

```bash
ETCDCTL_API=3 /usr/local/bin/etcdctl --write-out=table --cacert=/etc/etcd/ssl/ca.pem --cert=/etc/etcd/ssl/etcd.pem --key=/etc/etcd/ssl/etcd-key.pem --endpoints=https://192.168.100.12:2379,https://192.168.100.13:2379,https://192.168.100.14:2379 endpoint status
```

输出：

```bash
+-----------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|          ENDPOINT           |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+-----------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
| https://192.168.100.12:2379 | c70ab18d2d82b1e7 |  3.5.19 |   20 kB |      true |      false |         2 |         21 |                 21 |        |
| https://192.168.100.13:2379 |  ae638890e671854 |  3.5.19 |   20 kB |     false |      false |         2 |         21 |                 21 |        |
| https://192.168.100.14:2379 | 667ed0cec3659276 |  3.5.19 |   20 kB |     false |      false |         2 |         21 |                 21 |        |
+-----------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
```

可以看到 etcd1 是 leader。

## 六、Kubernetes 集群部署

### 6.1 Kubernetes 软件包下载

```bash
wget https://dl.k8s.io/v1.32.3/bin/linux/amd64/kube-apiserver
wget https://dl.k8s.io/v1.32.3/bin/linux/amd64/kube-controller-manager
wget https://dl.k8s.io/v1.32.3/bin/linux/amd64/kube-scheduler
wget https://dl.k8s.io/v1.32.3/bin/linux/amd64/kubectl
wget https://dl.k8s.io/v1.32.3/bin/linux/amd64/kubelet
wget https://dl.k8s.io/v1.32.3/bin/linux/amd64/kube-proxy
```

### 6.2 Kubernetes 软件包安装

```bash
chmod a+x kube*
mv kube* /usr/local/bin/
```

### 6.3 Kubernetes 软件分发

```bash
# 拷贝到 master2 上
scp /usr/local/bin/kube-apiserver root@k8s-master2:/usr/local/bin/
scp /usr/local/bin/kube-controller-manager root@k8s-master2:/usr/local/bin/
scp /usr/local/bin/kube-scheduler root@k8s-master2:/usr/local/bin/
scp /usr/local/bin/kubectl root@k8s-master2:/usr/local/bin/
scp /usr/local/bin/kubelet root@k8s-master2:/usr/local/bin/
scp /usr/local/bin/kube-proxy root@k8s-master2:/usr/local/bin/
# 拷贝到 master3 上
scp /usr/local/bin/kube-apiserver root@k8s-master3:/usr/local/bin/
scp /usr/local/bin/kube-controller-manager root@k8s-master3:/usr/local/bin/
scp /usr/local/bin/kube-scheduler root@k8s-master3:/usr/local/bin/
scp /usr/local/bin/kubectl root@k8s-master3:/usr/local/bin/
scp /usr/local/bin/kubelet root@k8s-master3:/usr/local/bin/
scp /usr/local/bin/kube-proxy root@k8s-master3:/usr/local/bin/
```

### 6.4 在集群节点上创建目录

> 集群中所有节点执行：

```bash
mkdir -p /etc/kubernetes/ssl
mkdir -p /var/log/kubernetes
```

### 6.5 部署 api-server

```bash
cat > kube-apiserver-csr.json << "EOF"
{
    "CN": "kubernetes",
    "hosts": [
        "127.0.0.1",
        "192.168.100.12",
        "192.168.100.13",
        "192.168.100.14",
        "192.168.100.15",
        "192.168.100.16",
        "192.168.100.17",
        "192.168.100.18",
        "192.168.100.19",
        "192.168.100.20",
        "192.168.100.100",
        "10.96.0.1",
        "kubernetes",
        "kubernetes.default",
        "kubernetes.default.svc",
        "kubernetes.default.svc.cluster",
        "kubernetes.default.svc.cluster.local"
    ],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "ST": "Beijing",
            "L": "Beijing",
            "O": "kubekube",
            "OU": "CN"
        }
    ]
}
EOF
```

说明：

- 如果 hosts 字段不为空则需要指定授权使用该证书的 IP（含 VIP）或域名列表。由于该证书被集群使用，需要将节点的 IP 都填上，为了方便后期扩容可以多写几个预留的 IP。
- 同时还需要填写 service 网络的首个 IP（一般是 kube-apiserver 指定的 service-cluster-ip-range 网段的第一个 IP，如 10.96.0.1）。

**生成 apiserver 证书及 token 文件**：

```bash
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-apiserver-csr.json | cfssljson -bare kube-apiserver

cat > token.csv << EOF
$(head -c 16 /dev/urandom | od -An -t x | tr -d ' '),kubelet-bootstrap,10001,"system:kubelet-bootstrap"
EOF
```

说明：

- 创建 TLS 机制所需 TOKEN
- TLS Bootstraping：Master apiserver 启用 TLS 认证后，Node 节点 kubelet 和 kube-proxy 与 kube-apiserver 进行通信，必须使用 CA 签发的有效证书才可以，当 Node 节点很多时，这种客户端证书颁发需要大量工作，同样也会增加集群扩展复杂度。
- 为了简化流程，Kubernetes 引入了 TLS bootstraping 机制来自动颁发客户端证书，kubelet 会以一个低权限用户自动向 apiserver 申请证书，kubelet 的证书由 apiserver 动态签署。所以强烈建议在 Node 上使用这种方式，目前主要用于 kubelet，kube-proxy 还是由我们统一颁发一个证书。

**创建 apiserver 服务配置文件：**

```bash
cat > /etc/kubernetes/kube-apiserver.conf << "EOF"
KUBE_APISERVER_OPTS="--enable-admission-plugins=NamespaceLifecycle,NodeRestriction,LimitRanger,ServiceAccount,DefaultStorageClass,ResourceQuota \
--anonymous-auth=false \
--bind-address=192.168.100.12 \
--secure-port=6443 \
--advertise-address=192.168.100.12 \
--authorization-mode=Node,RBAC \
--runtime-config=api/all=true \
--enable-bootstrap-token-auth \
--service-cluster-ip-range=10.96.0.0/16 \
--token-auth-file=/etc/kubernetes/token.csv \
--service-node-port-range=30000-32767 \
--tls-cert-file=/etc/kubernetes/ssl/kube-apiserver.pem \
--tls-private-key-file=/etc/kubernetes/ssl/kube-apiserver-key.pem \
--client-ca-file=/etc/kubernetes/ssl/ca.pem \
--kubelet-client-certificate=/etc/kubernetes/ssl/kube-apiserver.pem \
--kubelet-client-key=/etc/kubernetes/ssl/kube-apiserver-key.pem \
--service-account-key-file=/etc/kubernetes/ssl/ca-key.pem \
--service-account-signing-key-file=/etc/kubernetes/ssl/ca-key.pem \
--service-account-issuer=api \
--etcd-cafile=/etc/etcd/ssl/ca.pem \
--etcd-certfile=/etc/etcd/ssl/etcd.pem \
--etcd-keyfile=/etc/etcd/ssl/etcd-key.pem \
--etcd-servers=https://192.168.100.12:2379,https://192.168.100.13:2379,https://192.168.100.14:2379 \
--allow-privileged=true \
--apiserver-count=3 \
--audit-log-maxage=30 \
--audit-log-maxbackup=3 \
--audit-log-maxsize=100 \
--audit-log-path=/var/log/kube-apiserver-audit.log \
--event-ttl=1h \
--v=4"
EOF
```

**创建 apiserver 服务管理配置文件：**

```bash
cat > /etc/systemd/system/kube-apiserver.service << "EOF"
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes
After=etcd.service
Wants=etcd.service

[Service]
EnvironmentFile=-/etc/kubernetes/kube-apiserver.conf
ExecStart=/usr/local/bin/kube-apiserver $KUBE_APISERVER_OPTS
Restart=on-failure
RestartSec=5
Type=notify
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
```

**同步文件到其他 master 节点**：

```bash
cp ca*.pem /etc/kubernetes/ssl/
cp kube-apiserver*.pem /etc/kubernetes/ssl/
cp token.csv /etc/kubernetes/

scp ca*.pem root@k8s-master2:/etc/kubernetes/ssl/
scp kube-apiserver*.pem root@k8s-master2:/etc/kubernetes/ssl/
scp token.csv root@k8s-master2:/etc/kubernetes/

scp ca*.pem root@k8s-master3:/etc/kubernetes/ssl/
scp kube-apiserver*.pem root@k8s-master3:/etc/kubernetes/ssl/
scp token.csv root@k8s-master3:/etc/kubernetes/

scp /etc/kubernetes/kube-apiserver.conf root@k8s-master2:/etc/kubernetes
# 然后修改 k8s-master2 中这个文件的 bind-address 和 advertise-address
scp /etc/kubernetes/kube-apiserver.conf root@k8s-master3:/etc/kubernetes
# 然后修改 k8s-master3 中这个文件的 bind-address 和 advertise-address

scp /etc/systemd/system/kube-apiserver.service root@k8s-master2:/etc/systemd/system/
scp /etc/systemd/system/kube-apiserver.service root@k8s-master3:/etc/systemd/system/
```

**启动 apiserver 服务**：

> 在所有 master 节点上执行：

```bash
systemctl daemon-reload
systemctl enable --now kube-apiserver
systemctl status kube-apiserver
```

测试：

```bash
curl --insecure https://192.168.100.12:6443/
curl --insecure https://192.168.100.13:6443/
curl --insecure https://192.168.100.14:6443/
curl --insecure https://192.168.100.100:6443/
```

### 6.6 部署 kubectl

**创建 kubectl 证书请求文件**：

```bash
cat << EOF > admin-csr.json
{
  "CN": "admin",
  "hosts": [],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "Beijing",
      "L": "Beijing",
      "O": "system:masters",
      "OU": "system"
    }
  ]
}
EOF
```

**生成证书文件**：

```bash
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes admin-csr.json | cfssljson -bare admin
```

**复制文件到指定目录**：

```bash
cp admin*.pem  /etc/kubernetes/ssl/
```

**生成 kubeconfig 配置文件**：

```bash
kubectl config set-cluster kubernetes --certificate-authority=ca.pem --embed-certs=true --server=https://192.168.100.100:6443 --kubeconfig=kube.config

kubectl config set-credentials admin --client-certificate=admin.pem --client-key=admin-key.pem --embed-certs=true --kubeconfig=kube.config

kubectl config set-context kubernetes --cluster=kubernetes --user=admin --kubeconfig=kube.config

kubectl config use-context kubernetes --kubeconfig=kube.config
```

**准备 kubectl 配置文件并进行角色绑定**：

```bash
mkdir ~/.kube
cp kube.config ~/.kube/config
kubectl create clusterrolebinding kube-apiserver:kubelet-apis --clusterrole=system:kubelet-api-admin --user kubernetes --kubeconfig=/root/.kube/config
```

**查看集群状态**：

```bash
export KUBECONFIG=$HOME/.kube/config

# 查看集群信息
kubectl cluster-info
# 查看集群组件状态
kubectl get componentstatuses
# 查看命名空间中资源对象
kubectl get all --all-namespaces
```

**同步 kubectl 配置文件到集群其他 master 节点**：

> 在 k8s-master2 和 k8s-master3 上执行：

```bash
mkdir /root/.kube
```

> 在 k8s-master1 上执行：

```bash
scp /root/.kube/config k8s-master2:/root/.kube/config
scp /root/.kube/config k8s-master3:/root/.kube/config
```

配置 kubectl 命令补全（**可选**）：

```bash
dnf install -y bash-completion
source /usr/share/bash-completion/bash_completion
source <(kubectl completion bash)
kubectl completion bash > ~/.kube/completion.bash.inc
source '/root/.kube/completion.bash.inc'
source $HOME/.bash_profile
```

### 6.7 部署 kube-controller-manager

**创建 kube-controller-manager 证书请求文件**：

```bash
cat << EOF > kube-controller-manager-csr.json
{
  "CN": "system:kube-controller-manager",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "hosts": [
    "127.0.0.1",
    "192.168.100.12",
    "192.168.100.13",
    "192.168.100.14"
  ],
  "names": [
    {
      "C": "CN",
      "ST": "Beijing",
      "L": "Beijing",
      "O": "system:kube-controller-manager",
      "OU": "system"
    }
  ]
}
EOF
```

**创建 kube-controller-manager 证书文件**：

```bash
cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes \
  kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager
```

**创建 kube-controller-manager 的 kube-controller-manager.kubeconfig**：

```bash
kubectl config set-cluster kubernetes --certificate-authority=ca.pem --embed-certs=true --server=https://192.168.100.100:6443 --kubeconfig=kube-controller-manager.kubeconfig

kubectl config set-credentials system:kube-controller-manager --client-certificate=kube-controller-manager.pem --client-key=kube-controller-manager-key.pem --embed-certs=true --kubeconfig=kube-controller-manager.kubeconfig

kubectl config set-context system:kube-controller-manager --cluster=kubernetes --user=system:kube-controller-manager --kubeconfig=kube-controller-manager.kubeconfig

kubectl config use-context system:kube-controller-manager --kubeconfig=kube-controller-manager.kubeconfig
```

**创建 kube-controller-manager 配置文件**：

```bash
cat > kube-controller-manager.conf << "EOF"
KUBE_CONTROLLER_MANAGER_OPTS="--secure-port=10257  \
--bind-address=127.0.0.1 \
--kubeconfig=/etc/kubernetes/kube-controller-manager.kubeconfig \
--service-cluster-ip-range=10.96.0.0/16 \
--cluster-name=kubernetes \
--cluster-signing-cert-file=/etc/kubernetes/ssl/ca.pem \
--cluster-signing-key-file=/etc/kubernetes/ssl/ca-key.pem \
--allocate-node-cidrs=true \
--cluster-cidr=10.244.0.0/16 \
--cluster-signing-duration=87600h \
--root-ca-file=/etc/kubernetes/ssl/ca.pem \
--service-account-private-key-file=/etc/kubernetes/ssl/ca-key.pem \
--leader-elect=true \
--feature-gates=RotateKubeletServerCertificate=true \
--controllers=*,bootstrapsigner \
--horizontal-pod-autoscaler-sync-period=10s \
--tls-cert-file=/etc/kubernetes/ssl/kube-controller-manager.pem \
--tls-private-key-file=/etc/kubernetes/ssl/kube-controller-manager-key.pem \
--use-service-account-credentials=true \
--v=2"
EOF
```

**创建服务启动文件**：

```bash
cat > kube-controller-manager.service << "EOF"
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes

[Service]
EnvironmentFile=-/etc/kubernetes/kube-controller-manager.conf
ExecStart=/usr/local/bin/kube-controller-manager $KUBE_CONTROLLER_MANAGER_OPTS
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

**同步文件到集群 master 节点**：

```bash
cp kube-controller-manager*.pem /etc/kubernetes/ssl/
cp kube-controller-manager.kubeconfig /etc/kubernetes/
cp kube-controller-manager.conf /etc/kubernetes/
cp kube-controller-manager.service /usr/lib/systemd/system/

scp kube-controller-manager*.pem k8s-master2:/etc/kubernetes/ssl/
scp kube-controller-manager*.pem k8s-master3:/etc/kubernetes/ssl/
scp kube-controller-manager.kubeconfig k8s-master2:/etc/kubernetes/
scp kube-controller-manager.kubeconfig k8s-master3:/etc/kubernetes/
scp kube-controller-manager.conf k8s-master2:/etc/kubernetes/
scp kube-controller-manager.conf k8s-master3:/etc/kubernetes/
scp kube-controller-manager.service k8s-master2:/usr/lib/systemd/system/
scp kube-controller-manager.service k8s-master3:/usr/lib/systemd/system/
```

**启动服务**：

```bash
systemctl daemon-reload
systemctl enable --now kube-controller-manager
systemctl status kube-controller-manager
```

验证：

```bash
kubectl get componentstatuses
```

### 6.8 部署 kube-scheduler

创建 kube-scheduler 证书请求文件：

```bash
cat << EOF > kube-scheduler-csr.json
{
    "CN": "system:kube-scheduler",
    "hosts": [
        "127.0.0.1",
        "192.168.100.12",
        "192.168.100.13",
        "192.168.100.14"
    ],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "ST": "Beijing",
            "L": "Beijing",
            "O": "system:kube-scheduler",
            "OU": "system"
        }
    ]
}
EOF
```

生成 kube-scheduler 证书：

```bash
cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=kubernetes \
  kube-scheduler-csr.json | cfssljson -bare kube-scheduler
```

创建 kube-scheduler 的 kubeconfig：

```bash
kubectl config set-cluster kubernetes --certificate-authority=ca.pem --embed-certs=true --server=https://192.168.100.100:6443 --kubeconfig=kube-scheduler.kubeconfig

kubectl config set-credentials system:kube-scheduler --client-certificate=kube-scheduler.pem --client-key=kube-scheduler-key.pem --embed-certs=true --kubeconfig=kube-scheduler.kubeconfig

kubectl config set-context system:kube-scheduler --cluster=kubernetes --user=system:kube-scheduler --kubeconfig=kube-scheduler.kubeconfig

kubectl config use-context system:kube-scheduler --kubeconfig=kube-scheduler.kubeconfig
```

创建服务配置文件：

```bash
cat > kube-scheduler.conf << "EOF"
KUBE_SCHEDULER_OPTS="--kubeconfig=/etc/kubernetes/kube-scheduler.kubeconfig \
--leader-elect=true \
--v=2"
EOF
```

创建服务启动配置文件：

```bash
cat > kube-scheduler.service << "EOF"
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes

[Service]
EnvironmentFile=/etc/kubernetes/kube-scheduler.conf
ExecStart=/usr/local/bin/kube-scheduler $KUBE_SCHEDULER_OPTS
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

同步文件至集群 master 节点：

```bash
cp kube-scheduler*.pem /etc/kubernetes/ssl/
cp kube-scheduler.kubeconfig /etc/kubernetes/
cp kube-scheduler.conf /etc/kubernetes/
cp kube-scheduler.service /usr/lib/systemd/system/

scp kube-scheduler*.pem k8s-master2:/etc/kubernetes/ssl/
scp kube-scheduler*.pem k8s-master3:/etc/kubernetes/ssl/
scp kube-scheduler.kubeconfig k8s-master2:/etc/kubernetes/
scp kube-scheduler.kubeconfig k8s-master3:/etc/kubernetes/
scp kube-scheduler.conf k8s-master2:/etc/kubernetes/
scp kube-scheduler.conf k8s-master3:/etc/kubernetes/
scp kube-scheduler.service k8s-master2:/usr/lib/systemd/system/
scp kube-scheduler.service k8s-master3:/usr/lib/systemd/system/
```

启动服务：

```bash
systemctl daemon-reload
systemctl enable --now kube-scheduler
systemctl status kube-scheduler
```

验证：

```bash
kubectl get componentstatuses
```











