# KubeEdge 相关概念

## 1. cgroupfs 和 systemd

在 Linux 系统中，`cgroupfs` 和 `systemd` 是管理和控制系统资源的重要工具，尤其在容器化和资源隔离方面应用广泛。

### 1.1 cgroup(Control Groups)

cgroup 是 linux 内核的一项特性，用于限制、记录和隔离进程组的资源使用。通过 cgroups，可以控制 CPU、内存、磁盘 I/O 等资源的分配。它在资源管理、容器化（如 Docker）以及系统服务的隔离和监控中扮演了重要角色。

**【cgroupfs】**

`cgroupfs` 是通过文件系统接口访问和管理 cgroup 的一种方式。通常情况下，cgroupfs 挂载在 `/sys/fs/cgroup` 下，通过目录结构来表示会不同的 cgroup 资源控制器（如 `cpu`、`memory`、`blkio` 等），并允许用户直接操作这些文件和目录来管理资源。

**【主要功能】**

- 资源限制：可以限制 CPU、内存、网络带宽等的使用。例如，可以限制一个进程最多使用 500MB 内存。
- 优先级控制：通过设置权重，让系统资源按优先级分配给不同进程。
- 监控和计量：可以监控进程的资源使用情况。
- 进程隔离：允许把不同的进程组放入不同的 cgroup 中，实现资源隔离。

**【cgroup 版本】**

cgroup 分为 v1 和 v2 版本：

- cgroup v1：每个资源控制器有独立的子系统目录，比如：`/sys/fs/cgroup/cpu`、`/sys/fs/cgroup/memory`。
- cgroup v2：统一管理所有控制器，通过单一层次的挂载点（通常为 `/sys/fs/cgroup`）进行访问。简化了配置和管理，适合更复杂的资源调度。

### 1.2 systemd 和 cgroup

`systemd` 是 linux 系统的初始化系统和服务管理器。它在管理系统启动、服务、进程以及资源控制方面非常强大。`systemd` 内部集成了对 cgroup 的支持，可以通过配置文件直接使用 cgroup 的功能。

**【systemd 与 cgroup 的集成】**

- 自动创建 cgroup：在 `systemd` 启动服务时，它会为每个服务创建一个独立的 cgroup。例如，当你启动一个名为 `httpd` 的服务时，`systemd` 会在 `/sys/fs/cgroup` 中自动创建一个相应的目录（如 `/sys/fs/cgroup/system.slice/httpd.service`）。
- 资源管理：可以直接在 `systemd` 单元文件中定义资源限制，例如内存限制、CPU 限制等。`systemd` 会自动将这些配置映射到 cgroup 中。
- 状态监控：`systemd` 提供了 `systemctl` 和 `journalctl` 命令，用于监控服务的状态和资源使用情况。

【systemd 相关的配置实例】

在 `systemd` 服务单元文件中，可以直接使用资源控制指令，如下示例：

```ini
[Service]
# 限制服务的内存使用量上限为 512M
MemoryMax=512M

# 限制服务的 CPU 使用率为 50%
CPUQuota=50%

# 将服务配置到一个独立的 CPU 集群组
CPUAffinity=1 2 3

# 限制服务的 I/O 带宽为 10M/s
IOReadBandwidthMax=/dev/sda 10M
IOWriteBandwidthMax=/dev/sda 10M
```

通过这种方式，可以非常方便地管理服务和进程的资源使用。

### 1.3 systemd-cgls 和 systemd-cgtop

`systemd` 还提供了一些命令来查看和管理 cgroup 资源：

- systemd-cgls：这个命令可以显示当前 cgroup 的层次结构。执行 `systemd-cgls` 会以树状图的形式列出所有正在运行的服务和进程，帮助了解服务和进程的层级关系。
- systemd-cgtop：它可以实时监控 cgroup 资源使用情况，类似于 `top` 命令。通过它可以查看各个服务的 CPU、内存、I/O 使用情况。

### 1.4 使用实例

下面是一些使用实例，演示如何通过 `systemd` 和 cgroup 管理系统资源：

**【创建一个新的 cgroup】**

通过 `cgroupfs` 手动创建：

```bash
# 创建一个名为 "test" 的 cgroup
mkdir /sys/fs/cgroup/cpu/test
# 把进程 ID 为 1234 的进程添加到 "test" cgroup 中
echo 1234 > /sys/fs/cgroup/cpu/test/tasks
# 设置 CPU 使用限制，例如限制 CPU 使用为 20%
echo 20000 > /sys/fs/cgroup/cpu/test/cpu.cfs_quota_us
```

通过 `systemd` 创建：

1. 创建一个服务文件，比如 `my_test.service`：

    ```ini
    [Unit]
    Description=My Test Service
    
    [Service]
    ExecStart=/usr/bin/sleep infinity
    MemoryMax=256M
    CPUQuota=20%
    
    [Install]
    WantedBy=multi-user.target
    ```

2. 启动该服务：

    ```bash
    systemctl daemon-reload
    systemctl start my_test.service
    ```

### 1.5 总结

- `cgroupfs` 提供了文件系统接口，可以直接操作文件来控制和监控资源。
- `systemd` 集成了对 cgroup 的管理，使得在服务管理中应用 cgroup 更加简便，并通过单元文件实现资源限制。

这两者配合使用，使得 Linux 系统的资源管理和进程控制更加高效和便捷，适用于容器化、云计算等现代应用场景。

## 2. 高可用部署

KubeEdge 是一个基于 Kubernetes 的开源计算平台，主要用于实现云端和边缘之间的高效协作。在高可用（High Availability，HA）部署方面，KubeEdge 通常需要实现对边缘节点和云端控制平面（Kubernetes Master）组件的冗余，以避免单点故障，确保系统稳定性。以下是 KubeEdge 高可用部署的关键点。

### 2.1 云端控制平面的高可用

- 在 KubeEdge 的架构中，云端控制平面（即 Kubernetes Master）主要管理和调度边缘节点的工作负载。为了实现高可用，通常需要在云端部署多个 Master 节点。
- 使用负载均衡器（如 Nginx 或其他云提供商的负载均衡服务）将请求分发到多个 Master 节点，这样即使某个 Master 节点发生故障，其他节点也能继续提供服务。
- Kubernetes 本身的组件（如 etcd、API Servier、Controller Manager、Scheduler）可以配置为多实例模式，以确保高可用性和数据一致性。

### 2.2 边缘节点的高可用

- 在边缘节点上，KubeEdge 的 EdgeCore 负责与云端通信、管理设备、处理本地容器生命周期等。
- EdgeCore 的高可用可以通过在多个物理或虚拟节点上运行多个实例来实现。如果某个边缘节点离线或发生故障，工作负载可以重新调度到其他可用的边缘节点。
- KubeEdge 支持边缘自治模式，即边缘节点可以在断网的情况下依旧执行本地工作负载的原理，这增强了边缘节点的容错能力。

### 2.3 KubeEdge 组件的高可用

- KubeEdge 的主要组件包括云端的 CloudCore 和边缘的 EdgeCore。实现高可用时，需要确保 CloudCore 的高可用，以保证边缘节点能够正常与云端通信。
- 在云端，部署多个 CloudCore 示例并配置负载均衡器来分发请求可以增加 CloudCore 的可用性。
- 对于 EdgeCore，由于它运行在边缘设备上，通常可以直接在每个边缘设备上独立部署。如果某个 EdgeCore 节点发生故障，其他节点可以继续正常工作。

### 2.4 网络连接的高可用

- 边缘节点与云端通过网络连接进行通信。为了确保高可用，通常需要部署冗余网络路径，避免由于单一路径故障导致通信中断。
- 通过使用 VPN、专用网络链路等技术，可以提高云端与边缘节点之间网络连接的可靠性。

### 2.5 数据持久化的高可用

- 在 Kubernetes 的 etcd 数据库中存储了集群的配置信息和状态数据。确保 etcd 数据的高可用可以采用多节点的 etcd 集群，确保即使某个节点发生故障，数据依然可用。
- 对于 KubeEdge 边缘节点的本地数据，可以使用持久化存储（如 NFS、GlusterFS 或 Ceph）来实现高可用。

### 2.6 总结

在实际部署过程中，KubeEdge 高可用通常会包含以下几项配置：

- 多实例的 Kubernetes Master 和 CloudCore 以实现云端的高可用。
- 冗余的边缘节点部署和 EdgeCore 部署以确保边缘端的稳定运行。
- 通过负载均衡、VPN 和冗余网络连接等手段提高整体的可靠性和容错性。

这些措施能帮助构建一个更具容错性和可扩展性的边缘计算平台，适用于多种应用场景，包括智能制造、物联网和智慧城市等。

## 3. 容器化部署和二进制部署

### 3.1 容器化部署

容器化部署是指使用「容器」来打包应用程序及其所有依赖项的过程。最常用的容器化技术就是 Docker。容器本质上是一个独立、可移植的打包单位，它包含了应用程序的代码、依赖库、配置文件等等。这种方法在云端特别受欢迎，主要原因如下：

1. 隔离性：每个容器运行在自己独立的环境中，不会影响其他容器。
2. 可移植性：容器可以在任何支持容器运行的环境下都可以直接运行，消除了「在我机器上没问题」的情况。
3. 资源利用效率：容器不像虚拟机那样需要完整的操作系统，它们直接共享主机的内核资源，因此启动速度更快，消耗资源更少。
4. 版本一致性：容器镜像中打包的内容不会岁外部环境改变，从而保证了开发、测试和生产环境的一致性。

### 3.2 二进制部署

二进制部署指的是直接将编译好的应用程序二进制文件部署到目标服务器上。这种方法通常包括以下步骤：开发人员编写代码并编译为二进制文件，然后将这些文件（以及必要的依赖）拷贝到服务器上运行。这种方式的特点是：

1. 直接性：没有额外的抽象层，直接把应用程序放到服务器上运行。
2. 依赖问题：需要确保目标服务器具备应用运行所需的所有依赖项（例如，正确的库、配置环境等）。
3. 环境一致性问题：不同环境之间的差异可能会导致应用在不同服务器上表现不一致，这也是「它在我机器上没问题」的常见来源。
4. 维护成本高：需要手动管理和维护应用的依赖项，更新版本时可能面临依赖不兼容的问题。

### 3.3 区别总结

- 环境一致性：容器化部署更容易实现一致性，二进制部署可能面临环境差异带来的问题。
- 资源使用：容器更节约资源，特别适合云端和微服务架构。二进制部署则更适合小规模、资源充足的环境。
- 易用性和灵活性：容器化部署更灵活、易于扩展和管理，特别是在大规模分布式系统中优势明显。二进制部署则在简单、传统的项目中更为直接。

容易化部署在云计算、云原生领域已经成为主流，像 Kubernetes 这样的容器编排工具也提供了强大的集群管理能力。























