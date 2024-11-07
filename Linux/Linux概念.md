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

## 4. HTTP 与 HTTPS

HTTP（超文本传输协议，HyperText Transfer Protocol）和 HTTPS（安全超文本传输协议，Hypertext Transfer Protocol Secure）是用于 Web 浏览器与服务器之间通信的协议。它们在 Web 开发和网络安全中起着至关重要的作用。下面是这两个协议的详细介绍：

### 4.1 HTTP

HTTP 是一种用于客户端和服务器之间传输超文本的协议，主要用于加载网页和资源（如图像、视频、文本等）。它是一个无状态、无连接的协议，意味着：

- 无状态：每次请求都是独立的，服务器不会保留任何之前请求的上下文信息。
- 无连接：每次 HTTP 请求后，服务器都会关闭连接，不会保持长期连接。

**工作原理：**

- 用于在浏览器中输入一个网址（如 `http://example.com`），浏览器向指定的服务器发送 HTTP 请求。
- 服务器接收到请求后，返回所请求的网页或资源。
- 整个过程是明文传输，没有加密，因此数据可能被中间人拦截或篡改。

**常见 HTTP 方法：**

- GET：请求指定资源，通常用于浏览网页。
- POST：向服务器提交数据，常用于表单提交。
- PUT：上传或替换指定资源。
- DELETE：删除指定资源。
- HEAD：类似 GET，但不返回资源内容，只返回响应头部。

### 4.2 HTTPS

HTTPS 是 HTTP 的安全版本，通过使用 SSL / TLS 协议对数据进行加密，保证数据在传输过程中不被窃取或篡改。它解决了 HTTP 的安全问题，提供了数据加密、身份验证和数据完整性等安全保障。

**HTTPS 工作原理：**

- 在使用 HTTPS 协议时，客户端和服务器之间的通信是通过 SSL / TLS 协议进行加密的。
- 服务器会提供一个 SSL / TLS 证书，用于验证服务器身份，确保客户端访问的是合法的服务器。
- 数据加密使得即使通信被中间人拦截，也无法被解密。

**SSL / TLS：**

- SSL（安全套接层，Secure Sockets Layer）是 HTTPS 使用的最早加密协议，但现在已经逐步被 TLS（传输层安全性，Transport Layer Security）所替代。
- TLS 协议比 SSL 更加安全，但两个属于通常可以互换使用，尤其是在日常讨论中，大家往往仍习惯用 SSK。

### 4.3 HTTPS 与 HTTP 的区别

| 特性         | HTTP                         | HTTPS                                |
| ------------ | ---------------------------- | ------------------------------------ |
| **协议**     | 无加密，传输明文数据         | 使用 SSL / TLS 加密数据传输          |
| **端口**     | 默认端口 80                  | 默认端口 443                         |
| **安全性**   | 不安全，容易被窃听和修改     | 安全，提供加密、身份验证和数据完整性 |
| **性能**     | 相对较快，但没有加密性能开销 | 加密解密过程中会有性能损失           |
| **URL 开头** | `http://`                    | `https://`                           |

### 4.4 SSL/TLS 证书

HTTPS 网站需要使用 SSL/TLS 证书来加密通信，并确保网站的身份。SSL / TLS 证书由受信任的证书颁发机构（CA，Certificate Authority）签发。常见的证书类型有：

- 域名验证证书（DV SSL）：只验证域名的所有权，适用于普通网站。
- 组织验证证书（OV SSL）：除域名外，还验证组织身份，适用于企业网站。
- 扩展验证证书（EV SSL）：提供最高级别的验证，证书申请需要提供更多的公司或组织信息，通常会在浏览器地址栏显示公司名称。

### 4.5 HTTPS 的优势

- 数据加密：通过加密，防止通信被第三方窃听。
- 身份验证：SSL / TLS 证书确保与服务器的通信是安全的，防止假冒网站。
- 数据完整性：加密后，任何中间篡改都能被检测到，保证传输数据的完整性。
- SEO 优势：搜索引擎（如 Google）会优先考虑 HTTPS 网站，提高排名。

### 4.6 HTTPS 过渡

随着互联网的普及，尤其是 Google 等搜索引擎的推动，现在大多数网站都已经实现了 HTTPS 加密。浏览器（如 Chrome 和 Firefox）也会标记没有使用 HTTPS 的网站为「不安全」，以此鼓励网站使用 HTTPS。

过渡步骤：

1. 购买 SSL / TLS 证书。
2. 配置 Web 服务器（如 Apache、Nginx）支持 HTTPS。
3. 配置网站强制 HTTPS：通过 HTTP 重定向或 HSTS（HTTP Strict Transport Security）确保所有访问通过 HTTPS。

### 4.7 HTTPS 性能问题

由于 HTTPS 需要进行加密和解密操作，它相对于 HTTP 来说可能有稍微的性能开销。不过，现代的硬件和优化技术（如 HTTP/2）已经显著减小了这一影响。因此，采用 HTTPS 的网站性能损失可以忽略不计。























