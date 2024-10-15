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





















