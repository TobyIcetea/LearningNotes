# Linux 概念

## 1. Systemd

### 1.1 什么是 Systemd

Systemd 是一种用于 Linux 操作系统的系统和服务管理器。它是许多主流 Linux 发行版的默认初始化系统（init system）。Systemd 旨在客服传统 SysV init 系统的局限性，提供更快的启动速度、更好的启动依赖管理和统一的服务管理框架。

### 1.2 Systemd 的主要功能

- 系统初始化：在系统启动时，Systemd 负责初始化系统环境，包括挂载文件系统、启动必要的服务和进程。
- 服务管理：提供了统一的接口来管理系统服务，包括启动、停止、重启和监控服务状态。
- 并行启动：支持服务的并行启动，提高系统的启动速度。
- 依赖关系管理：通过定义服务之间的依赖关系，确保服务以正确的顺序启动。
- 日志管理：内置了 journald 日志系统，统一收集和管理系统日志。
- 资源控制：支持使用 cgroupfs（控制组）来限制和监控服务的资源使用，如 CPU、内存等。

### 1.3 Systemd 的基本组件

- Unit（单元）：Systemd 使用单元来表示系统中的各种资源。单元类型包括服务（.service）、挂载点（.mount）、套接字（.socket）、定时器（.timer）等。
- Unit 文件：位于 `/usr/lib/systemd/system/` 或 `/usr/systemd/system/`，用于配置单元的行为。

### 1.4 常用 Systemd 命令

使用 `systemctl` 命令来管理 Systemd。

- 服务管理
    - 启动服务：`systemctl start [服务名]`
    - 停止服务：`systemctl stop [服务名]`
    - 重启服务：`systemctl restart [服务名]`
    - 查看服务状态：`systemctl status [服务名]`
    - 使服务开机自启：`systemctl enable [服务名]`
    - 禁用服务开机自启：`systemctl disable [服务名]`
- 系统控制
    - 关机：`systemctl poweroff`
    - 重启：`systemctl reboot`
    - 挂起：`systemctl suspend`
- 查看单元
    - 列出所有已启动的单元：`systemctl list-units`
    - 列出所有可用的单元文件：`systemctl list-unit-files`

### 1.5 创建自定义服务

可以通过编写自定义的 Unit 文件来创建自己的服务。

示例：创建一个简单的服务

1. 创建服务脚本 `/usr/local/bin/myservice.sh`

    ```bash
    #!/bin/bash
    while true; do
    	echo "My Service is running..." >> /var/log/myservice.log
    	sleep 60
    done
    ```

    给脚本添加执行权限：

    ```bash
    chmod +x /usr/local/bin/myservice.sh
    ```

2. 创建 Unit 文件 `/etc/systemd/system/myservice.service`

    ```ini
    [Unit]
    Description=My Custom Service
    Afer=network.target
    
    [Service]
    Type=simple
    ExecStart=/usr/local/bin/myservice.sh
    Restart=on-failure
    
    [Install]
    WantedBy=multi-user.target
    ```

3. 重新加载 Systemd 并启动服务：

    ```bash
    systemctl daemon-reload
    systemctl start myservice
    systemctl enable myservice
    ```

## 2. Service

### 2.1 什么是服务

服务，也称为守护进程（daemon），是后台运行的程序，通常不需要直接的用户交互。服务在系统启动时加载，持续运行，为系统或网络提供特定功能。

### 2.2 常见的服务类型

- 系统服务，如 cron（定时任务）、syslog（系统日志）、dbus（消息总线）等。
- 网络服务：如 sshd（SSH 服务器）、httpd（Web 服务器）、mysqld（数据库服务器）等。

### 2.3 服务管理

使用 Systemd，可以方便地管理系统中的服务。

- 启动服务：`systemctl start [服务名]`
- 停止服务：`systemctl stop [服务名]`
- 重启服务：`systemctl restart [服务名]`
- 查看服务状态：`systemctl status [服务名]`

### 2.4 服务的状态和日志

- 查看服务状态：`systemctl status [服务名]`，可以查看服务的运行状态和最近的日志输出。
- 查看服务日志：`journalctl -u [服务名]`，可以查看该服务的全部日志。

### 2.5 服务的依赖关系

在 Systemd 中，服务之间可以定义依赖关系，确保按正确的顺序启动和停止。

- 依赖配置：在 Unit 文件的 `[Unit]` 部分，可以使用 `Requires`、`Wants`、`Before`、`After` 等指令。

示例：

```ini
[Unit]
Description=My Dependent Service
Requires=network.target
After=network.target
```

## 3. Port（端口）

### 3.1 什么是端口

端口是网络通信中的一个逻辑概念，用于标识同一台计算机中的不同服务或进程。端口号是一个 16 位的整数，范围从 0 到 65535。

- 知名端口（0-1023）：分配常见的服务，如 HTTP（80）、HTTPS（443）、SSH（22）。
- 注册端口：分配给用户注册的服务和应用程序。
- 动态 / 私有端口（49152-65535）：供应用程序临时使用。

### 3.2 端口的作用

- 标识服务：同一 IP 地址可以通过不同的端口号运行多个网络服务。
- 网络通信：客户端通过 IP 地址和端口号与服务器上的特定服务进行通信。

### 3.3 查看端口占用情况

- 使用 `netstat` 命令（可能需要安装 `net-tools`）：

    ```bash
    netstat -tuln
    ```

    参数说明：

    - `-t`：显示 TCP 端口
    - `-u`：显示 UDP 端口
    - `-l`：显示监听（Listen）状态的端口
    - `-n`：以数字形式显示地址和端口

- 使用 `ss` 命令：

    ```bash
    ss -tuln
    ```

- 使用 `lsof` 命令：

    ```bash
    lsof -i :80
    ```

    查看专用 80 端口的进程。

### 3.4 查看端口访问

- 防火墙设置：使用 `iptables`、`firewalld` 或 `ufw` 来控制端口的访问。
- SELinux / AppArmor：安全增强的访问控制，可以对端口访问进行细粒度的权限管理。

### 3.5 监听与暴露的区别和联系

**【区别】**

- 监听是服务的行为：监听是应用程序或服务在本地系统上绑定端口，等待连接的过程。
- 暴露是网络配置的结果：暴露是通过网络配置（如防火墙、路由器设置）使坚挺的端口可被外部访问。

**【联系】**

- 相辅相成：一个服务必须先在某个端口上监听，才能通过暴露该端口供外部访问。
- 安全性：仅仅监听端口并不意味着安全风险，只有当端口被暴露后，才需要考虑来自外部的安全威胁。

**【示例场景】**

- 未暴露的监听端口：某服务在本地监听端口，但防火墙未开放相应端口，外部无法访问该服务。
- 暴露的端口未有服务监听：防火墙开放了某个端口，但没有服务在该端口上监听，外部链接会被拒绝或超时。





















