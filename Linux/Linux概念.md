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

## 5. 转发规则

在 Linux 中，转发规则（forwarding rules）是指控制网络流量如何从一个网络接口转发到另一个网络接口的规则。这些规则通常是由 `iptables` 和 `ipvs` 来定义的，分别处理过滤和负载均衡的任务。

### 5.1 iptables 中的转发规则

`iptables` 是 Linux 下最常用的防火墙工具之一，它使用一系列的链（chains）来对数据包进行过滤。在 `iptables` 中，转发规则通常是通过 `FORWARD` 链来管理的。

- `FORWARD` 链：当数据包经过一个网卡，目标不是本机，而是转发到另一台机器时，这些数据包会经过 `FORWARD` 链。如果你配置了转发规则，`iptables` 回见擦汗数据包是否符合这些规则，并决定是否允许或组织它们。

    在 `iptables` 中，可以通过以下命令查看和设置转发规则：

    ```bash
    iptables -L FORWARD
    ```

    你可以通过添加规则来允许或阻止数据包的转发，例如：

    ```bash
    iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
    ```

    这条规则表示允许从 `eth0` 接收到的数据包转发到 `eth1` 网络接口。

常见的转发规则示例：

- 允许所有数据包从接口 A 转发到接口 B：

    ```bash
    iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
    ```

- 阻止某些 IP 地址的数据包转发：

    ```bash
    iptables -A FORWARD -s 192.168.1.100 -j DROP
    ```

- 允许 ICMP 流量转发（如 ping）：

    ```bash
    iptables -A FORWARD -p icmp -j ACCEPT
    ```

### 5.2 ipvs 中的转发规则

`ipvs`（IP Virtual Server）是 Linux 下用于实现负载均衡的工具，它能够将来自客户端的数据包根据预定的规则分发到后端服务器。`ipvs` 是在内核中实现的，因此性能上要比 `iptables` 更高效，尤其是在处理大量并发请求时。

在 `ipvs` 中，转发规则更多是和负载均衡的配置相关，而不是直接的包过滤。`ipvs` 通过定义虚拟服务和真是服务器来决定如何将流量转发到不同的服务器节点。

- 虚拟服务（Virtual Service）：是用户访问时使用的 IP 地址和端口。
- 真实服务器（Real Server）：是提供实际服务的服务器集群节点。

使用 `ipvsadm` 命令来查看和管理转发规则：

```bash
ipvsadm -L -n
```

添加一个虚拟服务的负载均衡规则：

```bash
ipvsadm -A -t 192.168.0.1:80 -s rr
ipvsadm -a -t 192.168.0.1:80 -r 192.168.0.2:80 -m
```

上述命令表示将访问 `192.168.0.1:80` 的流量按 `round-robin`（rr）算法负载均衡，转发到 `192.168.0.2:80`。

### 5.3 总结

- iptables 的转发规则主要用于控制数据包的过滤与转发，它通过 `FORWARD` 链对流量进行控制。
- ipvs 的转发规则则与负载均衡相关，决定如何将流量分发到后端服务器。

如果你的目标是简单的流量过滤和控制，`iptables` 是常用的工具；如果你需要高效的负载均衡，那么 `ipvs` 更适合处理这种场景。

## 6. 挂载（Mount）

### 6.1 挂载的基本概念

- 挂载（mount）是将一个存储设备、分区或文件夹连接到操作系统的文件系统树上的过程。
- 在 Linux 中，所有的文件系统资源（无论是硬盘、网络存储，还是其他操作系统中的文件夹）都必须挂载到一个目录下。
- 挂载后的资源可以通过该目录访问。

### 6.2 挂载的方向

挂载的方向是由**谁需要访问谁的数据**决定的。常见的挂载方式有：

**【Windows 文件夹挂载到 Linux】**

- 需求：想要在 Linux 中访问 Windows 中的文件。
- 操作：在 VMware 中，设置 Windows 文件夹为共享文件夹，然后在 Linux 中通过 VMware Tools 将其挂载到一个目录（通常是 `/mnt/hgfs/`）。
- 理解：Linux 需要访问 Windows 中的文件，Windows 通过共享文件夹挂载到 Linux 上。

**【硬盘挂载到 Linux】**

- 需求：想要在 Linux 中访问外部硬盘或磁盘分区。
- 操作：使用 `mount` 命令将硬盘或磁盘分区挂载到 Linux 系统的目录下（如 `/mnt/` 或 `/media/`）。
- 理解：Linux 需要访问硬盘，硬盘挂载到 Linux 上。

## 7. NAT（网络地址转换）

NAT（Network Address Translation，网络地址转换）是一种在路由器或防火墙中实现的技术，主要用来在局域网（LAN）和公网（WAN，通常是互联网）之间翻译网络地址。它的作用是把私有 IP 地址转换为公网 IP 地址，从而使局域网内的设备可以访问互联网，同时还能隐藏局域网内部的网络结构。

### 7.1 为什么需要 NAT？

1. IPv4 地址不足：

    IPv4 地址的数量有限（约 43 亿个），而互联网上的设备数量远远超过了这个数。所以大部分家庭、企业内部使用私有 IP 地址（比如 192.168.x.x 或 10.x.x.x），通过 NAT 使用少量的公网 IP 地址来访问外网。

2. 安全性：

    NAT 在一定程度上隔离了局域网和公网，隐藏了局域网设备的真实 IP 地址，增加了网络安全性。

3. 便于管理：

    使用 NAT 可以简化对局域网内部 IP 地址的管理，因为内部地址可以自行分配而不受公网地址限制。

---

### 7.2 NAT 的工作原理

核心概念：

- 私有 IP 地址：仅在局域网中有效，不直接在互联网使用（如 192.168.100.140）。
- 公网 IP 地址：在互联网上使用的全球唯一的地址（如 203.0.113.1）。

当一台局域网设备想访问互联网时，它的私有 IP 地址会通过 NAT 转换成一个公网 IP 地址。具体过程如下：

1. 设备发送数据包，目标是一个外部服务器（比如访问一个网站）。
2. NAT 设备（通常是路由器）会将数据包的源地址从私有 IP 替换成路由器的公网 IP。
3. 外部服务器回复数据包，目标是路由器的公网 IP。
4. 路由器通过 NAT 表将数据包转发给原始的内部设备。

### 7.3 NAT 的类型

1. 静态 NAT（Static NAT）：

    私有 IP 和公网 IP 一一对应。比如 192.168.0.2 总是映射到 203.0.113.2。这种方式很少用，适合需要固定公网 IP 的服务器。

2. 动态 NAT（Dynamic NAT）：

    使用一个公网 IP 池，当内部设备访问外网时，动态分配一个公网 IP。适用于公网 IP 数量较多的场景。

3. 端口地址转换（PAT，Port Address Translation）：

    也叫 NAT Overload，是最常用的 NAT 类型。它允许多个内部设备共享一个公网 IP，但通过不同的端口号区分数据流。

### 7.4 举例：PAT 的工作过程

假设家里有 3 台设备（192.168.0.2、192.168.0.3、192.168.0.4），都通过同一个路由器访问互联网，路由器的公网 IP 是 203.0.113.1。

1. 设备发起请求：
    - 192.168.0.2：想访问百度（目标 IP：180.76.76.76，目标端口：80）。
    - 192.168.0.3：想访问腾讯云（目标 IP：119.29.29.29，目标端口：443）。
    - 192.168.0.4：想访问一个 API 服务（目标 IP：203.0.113.100，目标端口：8080）。
2. NAT 设备处理请求：
    - 路由器分配一个外部端口号，比如：
        - 192.168.0.2 → 203.0.113.1:5001
        - 192.168.0.3 → 203.0.113.1:5002
        - 192.168.0.4 → 203.0.113.1:5003
3. 外网回复：
    - 百度回复时目标地址是 203.0.113.1:5001，路由器知道这是给 192.168.0.2 的。
    - 腾讯云回复时目标地址是 203.0.113.1:5002，路由器知道这是给 192.168.0.3 的。
    - API 服务器回复时目标地址是 203.0.113.1:5003，路由器知道这是给 192.168.0.4 的。

### 7.5 NAT 的缺点

优点：

- 节省 IP 资源：使用一个公网 IP 支持多个设备上网。
- 增强安全性：局域网 IP 隐藏在 NAT 后，外网无法直接访问。
- 灵活性：私有 IP 的分配不受公网 IP 限制。

缺点：

- 延迟和性能：数据包需要转换，增加了延迟和路由器的负载。
- 限制直接通信：外部设备无法直接访问 NAT 后的内部设备（需要端口映射）。
- 不适合某些协议：NAT 对基于 IP 地址的协议（如 VolP、P2P）支持不佳。

### 7.6 举例：现实中的应用

1. 家庭网络：
    - 家里的路由器通常会使用 NAT，将 ISP 分配的一个公网 IP 转换给家里所有设备使用。
2. 公司网络：
    - 公司可能有 200 台电脑，但 ISP 只提供 5 个公网 IP。NAT 会自动分配这 5 个 IP，供内部设备共享。
3. 端口映射：
    - 如果你想从外网访问家里的 NAS（私有 IP：192.168.0.10，端口 5000），可以在路由器上设置 NAT 规则，将公网 IP 的某个端口（如 203.0.113.1:8080）映射到 NAS 的地址。

## 8. Centos 文件系统

### 8.1 `/`（根目录）

根目录是整个文件系统的起点，所有其他目录和文件都挂载在该目录下。

### 8.2 `/bin`（二进制可执行文件）

- 作用：存放普通用户和系统管理员使用的基础命令（如 `ls`、`cp`、`mv` 等命令）。
- 现代 Centos 将 `/bin` 目录链接到 `/usr/bin`，整合了用户和系统命令。

![image-20250312104727715](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250312104727715.png)

### 8.3 `/boot`（引导相关文件）

`/boot` 目录通常包含以下文件和子目录：

- vmlinuz 或 vmlinuz-，这是 Linux 内核的可执行文件。vmlinuz 是压缩后的内核镜像，系统启动时会加载它。
- initramfs 或 initrd-，这是初始 RAM 文件系统（Initial RAM FileSystem）的镜像文件。它包含了在系统启动过程中需要的临时根文件系统，用于加载必要的驱动程序和模块，以便挂载真正的根文件系统。
- grub/，这是 GRUB（Grand Unified Bootloader）的配置文件目录。GRUB 是一个引导加载程序，负载在系统启动时加载内核。`/boot/grub/grub.cfg` 是 GRUB 的配置文件。
- 。。。

`/boot` 目录的主要作用是存储启动过程中所需的文件，包括内核、初始 RAM 文件系统、引导加载程序等。这些文件在系统启动时被加载，以确保系统能够正确启动。

在日常管理中，`/boot` 目录的内容通常由包管理器（如 `yum` 或 `dnf`）自动更新。例如，当安装新的内核时，新的内核文件会被自动放置在 `/boot` 目录中，并更新 GRUB 配置。

### 8.4 `/dev`（设备文件）

在 linux 中，硬件设备（如硬盘、键盘、鼠标、打印机等）和虚拟设备（如 `/dev/null`、`/dev/random` 等）都被表示为文件，这些文件位于 `/dev` 目录下。

设备类型：

- 块设备（block device）：如硬盘、SSD 等，数据以块为单位进行读写。块设备通常以 `b` 开头。
- 字符设备（character device）：如键盘、鼠标、串口等，数据以字符为单位进行读写。字符设备文件通常以 `c` 开头。
- 网络设备：如网卡，网络设备在 `/dev` 中没有对应的文件，而是通过 `/sys` 和 `/proc` 等目录进行管理。

`/dev` 目录是 Linux 系统中与硬件设备交互的重要接口。通过 `/dev` 目录中的设备文件，用户和程序可以访问和控制硬件设备。

### 8.5 `/etc`（配置文件）

`/etc` 目录主要用户存储系统的配置文件。这些配置文件通常以纯文本形式存在，可以通过文本编辑器进行修改。

例如：

1. `/etc/passwd`：存储用户账户信息。
2. `/etc/shadow`：存储用户密码的加密信息。
3. `/etc/group`：存储用户组的信息。
4. `/etc/hosts`：配置主机名与 IP 地址的映射关系。
5. `/etc/resolv.conf`：配置 DNS 服务器的 IP 地址。
6. `/etc/crontab`：系统级定时任务的配置文件，定义定时执行的命令。

`/etc` 目录是 linux 系统中存储配置文件的核心位置，涵盖了从用户管理、网络配置到服务管理的各个方面。修改这些文件时需要谨慎，因为错误的配置可能会导致系统无法正常工作。

### 8.6 `/usr`（系统核心资源）

在 linux 系统中，`/usr` 目录是系统核心资源的存储位置，它的名称源于 Unix System Resources。这个目录包含了大部分用户级应用程序、库文件、文档和共享资源。

`/usr` 的核心子目录：

1. `/usr/bin`：存放**用户安装的可执行命令**（例如 `gcc`、`python`、`vim` 等）。
2. `/usr/sbin`：存放**需要管理员权限的系统管理命令**（如 useradd、iptables 等）。对比 `/usr/bin`，`/usr/sbin` 存放更基础的管理命令。
3. `/usr/lib` 和 `/usr/lib64`：存放应用程序的共享**库文件**（`.so` 文件）。
4. `/usr/include`：存放 C/C++ 等编程语言的**头文件**（`.h` 文件），供开发编译时使用。
5. `/usr/share`：存放与架构无关的**共享数据**，如文档、图标、字体、时区文件等。比如说 `/usr/share` 目录下的 `man`（手册页）、`doc`（软件文档）、`icons`（应用程序图标）。
6. `/usr/local/bin`：用户**手动编译安装的软件**默认存放在这里（如通过 `make install` 安装的程序），通常包含 `bin`、`lib`、`share` 等子目录，模仿 `/usr` 的结构。
7. `/usr/src`：存放**内核源代码**或者第三方软件的源码。

其他子目录：

1. `/usr/libexec`：存放仅供其他程序调用的内部执行文件（不直接面向用户），例如某些服务的后台脚本。
2. `/usr/etc`：少数软件可能将配置文件放在此处，但主流配置通常仍在 `/etc`。
3. `/usr/tmp`：部分系统可能保留此目录作为临时文件存储，但标准临时目录是 `/tmp`。

`/usr` 和 `/opt`：

- `/opt` 通常用于安装第三方大型商业软件（如 MATLAB、Google Chrome），而 `/usr` 更偏向系统自带的软件包。

### 8.7 `/lost+found`（文件修复）

Linux 系统中的 `lost+found` 目录是文件系统修复工具（如 `fsck`）用于存放孤立文件片段的特殊目录。这些文件可能因系统崩溃、断电、磁盘错误或非正常关机导致文件系统损坏时，与原始目录结构失去关联。

正常运行的系统中，`lost+found` 通常是空的。若存在文件，表示近期发生过文件系统修复事件。

`lost+found` 是 Linux 文件系统的“急救箱”，存放因意外事件丢失的文件片段，为管理员提供最后的数据恢复机会。其存在体现了文件系统自我修复的设计理念。

### 8.8 `/media`（挂载可移动存储设备）

在 linux 系统中，`/media` 文件夹的主要作用是作为可移动存储设备的挂载点。当用户插入外部存储设备（如 USB 闪存驱动器、外部硬盘、SD 卡、CD/DVD 等）时，系统通常会将这些设备自动挂载到 `/media` 目录下的子目录中。

具体作用：

1. 现代 Linux 发行版通常会使用 `/media` 作为自动挂载可移动设别的默认位置。例如，插入一个 USB 闪存驱动器后，系统可能会将其挂载到 `/media/username/device_name` 或 `/media/device_name` 这样的路径下。
2. `/media` 目录的权限通常设置为允许普通用户访问，因此用户可以方便地浏览和管理挂载的外部设备。
3. `/media` 目录通常用于临时挂载设备，设备卸载后，挂载点会被自动删除。

与 `/mnt` 的区别：

- `/mnt` 目录通常用于**手动挂载**文件系统或存储设备，通常是管理员或用户手动执行的挂载操作。
- `/media` 则主要用于自动挂载可移动设别，更加面向普通用户。

但是，随着系统发展，一些 Linux 发行版（如 Fedora、CentOS、openSUSE 等）开始使用 `/run/media` 作为挂载点。

总结来说，`/media` 文件夹是 Linux 操作系统中用于方便用户访问和管理可移动存储设备的默认挂载点。

### 8.9 `/mnt`（临时挂载）

在 linux 系统中，`/mnt` 目录是一个用于临时挂在文件系统的标准目录。它的主要作用是作为一个挂载点（mount point），用于挂载其他文件系统或存储设备，如外部硬盘、USB 驱动器、网络文件系统（NFS）等。

以下是一些常见用途：

1. 当你插入一个 USB 驱动器、外部硬盘或光盘时，可以将其挂载到 `/mnt` 目录或其子目录下，以便访问其中的文件。
2. 如果你需要访问远程服务器上的文件系统（如 NFS 或 Samba），可以将这些网络文件系统挂载到 `/mnt` 目录下。
3. `/mnt` 通常用于临时挂载，而不是长期使用。如果需要长期挂载，通常会选择其他目录（如 `/media` 或自定义目录）。
4. 在系统维护或恢复过程中，可能需要挂载其他分区或文件系统到 `/mnt` 目录，以便进行修复或数据恢复。

注意事项：

- `/mnt` 目录通常是空的，除非有文件系统被挂载到其中。
- 如果需要长期挂载，建议使用 `/media` 目录或创建一个自定义目录。
- 挂载和卸载操作需要管理员权限（使用 `sudo` 或 root 用户）。

总之，`/mnt` 目录是 Linux 系统中一个灵活且常用的挂载点，适用于临时挂载各种文件系统和存储设备。

### 8.10 `/opt`（第三方软件包）

在 Linux 操作系统中，`/opt` 目录通常用于存放可选的或第三方软件包，它的全称是 `optional`，意为“可选的”。这个目录的目的是为那些不遵循标准文件系统层次结构（FileSystem Hierachy Standard，FHS）的软件提供一个集中的安装位置。

`/opt` 目录的主要作用：

1. 第三方软件安装：`/opt` 通常用于安装那些不通过系统的包管理器（如 `apt`、`yum` 或 `dnf`）管理的软件。
2. 软件包的自包含性：安装在 `/opt` 目录下的软件通常会将所有相关文件（如二进制文件、库、配置文件等）集中在一个子目录中。例如，一个软件可能安装在 `/opt/software_name` 目录下。
3. 避免与系统文件冲突：将第三方软件安装在 `/opt` 目录下可以避免与系统自带的软件或包管理器安装的软件发生冲突。

总结来说，`/opt` 目录是 Linux 系统中用于存放可选或第三方软件的标准位置，有助于保持系统的整洁和可维护性。

### 8.11 `/proc`（进程）

在 Linux 系统中，`/proc` 目录是一个特殊的虚拟文件系统，通常为成为 proc 文件系统。

它并不包含实际的磁盘文件，而是提供了内核和运行中进程的运行时信息。通过 `/proc` 目录，用户和应用程序可以访问系统的内核数据、进程状态、硬件信息等。

以下是 `/proc` 目录的主要作用：

1. 进程信息：`/proc` 目录下包含一系列以进程 ID（PID）命名的子目录（例如 `/proc/1234`），每个子目录对应一个正在运行的进程。这些子目录中包含进程的详细信息，例如：
    - `/proc/[PID]/status`：进程的状态信息。
    - `/proc/[PID]/cmdline`：启动进程的命令行参数。
    - `/proc/[PID]/fd`：进程打开的文件描述符。
    - `/proc/[PID]/maps`：进程的内存映射信息。
2. 系统信息：`/proc` 目录还包含许多与系统相关的文件，提供了内核和硬件的运行时信息。例如：
    - `/proc/cpuinfo`：CPU 的详细信息。
    - `/proc/meminfo`：内存使用情况。
    - `/proc/version`：内核版本信息。
    - `/proc/loadavg`：系统的平均负载。
    - `/proc/partitions`：磁盘分区信息。
    - `/proc/net`：网络相关的信息。
3. 内核参数和配置：`/proc/sys` 目录包含了内核的运行时参数，这些参数可以通过修改文件来动态调整系统的行为。例如：
    - `/proc/sys/net/ipv4/ip_forward`：控制是否启用 IP 转发。
    - `/proc/sys/kernel/hostname`：系统的主机名。
    - `/proc/sys/vm/swappiness`：控制系统使用交换分区的倾向。
4. 硬件信息：`/proc` 目录还提供了硬件相关的信息，例如：
    - `/proc/interrupts`：中断信息。
    - `/proc/ioports`：I/O 端口信息。
    - `/proc/dma`：DMA 通道信息。

注意事项：

- `/proc` 中的文件是动态生成的，每次读取时都会重新生成内容，因此它们反映了系统的实时状态。
- 修改 `/proc` 中的文件（尤其是 `/proc/sys` 下的文件）可能会直接影响系统的行为，因此需要谨慎操作。

总结来说，`/proc` 目录是 Linux 系统中一个非常重要的虚拟文件系统，提供了对内核和进程的运行时信息的访问接口，是系统管理和调试的利器。

### 8.12 `/run`（临时文件）

`/run` 目录的名字来源于它的功能和用途，及存储与“运行时”（runtime）相关的数据。这个名字直观地反映了该目录的用途：它用于存储系统或进程在运行期间产生的临时数据。

`/run` 目录是一个临时文件系统（`tmpfs`），用于存储运行时的系统信息和进程相关的数据。它是在系统启动时创建的，并且在系统关闭时会被清空。`/run` 目录的设计目的是为了提供一个统一的、临时的地方来存储运行时数据，这些数据在系统重启后不需要持久化。

`/run` 目录主要用于存储以下几种类型的运行时数据：

- 进程 ID（PID）文件：某些服务或守护进程会在 `/run` 目录下创建 PID 文件，用于记录它们正在运行的进程 ID。
- 套接字文件：一些服务会在 `/run` 目录下创建套接字文件，用于进程间通信（IPC）。
- 锁文件：所文件通常用于防止多个进程同时访问同一资源。
- 临时状态信息：一些应用程序或服务可能会在 `/run` 目录下存储临时的状态信息。

`/run` 和 `/var/run` 的关系：

- 在早期的 Linux 系统中，运行时的数据通常存储在 `/var/run` 目录中。为了简化文件系统层次结构并提高性能，现代 Linux 系统将 `/var/run` 目录符号链接到 `/run` 目录。因此，`/var/run` 实际上是 `/run` 的一个别名。

`/run` 目录是 Linux 系统中用于存储运行时数据的一个重要目录。它提供了一个临时、快速且统一的地方来存储进程 ID、套接字文件、锁文件等信息。由于它存储在内存中，因此访问速度非常快，并且在系统重启时会被清空，确保不会留下任何不需要的持久化数据。

比如说 `/run/containerd/containerd.sock` 这样的套接字文件，在关机时也会被清除，开机的时候再重新开启。

### 8.13 `/srv`（服务）

`/srv` 目录是用于存放特定服务（service）的数据文件的。它的主要目的是为系统管理员提供一个标准化的位置来存放与特定服务相关的数据。这些服务可以是 Web 服务器、FTP 服务器、Git 等。

在 Linux 系统中，`/srv` 目录默认是空的，因为它只是一个建议的目录，用于存放与服务相关的数据文件。但并不是所有系统或服务都会使用它。

### 8.14 `/sys`（系统）

`/sys` 文件夹是 Linux 操作系统的一个虚拟文件系统，用于暴露内核和设备的运行时信息。它提供了一种与内核交互的方式，允许用户和程序通过读取和写入文件来获取或修改系统硬件和内核的状态。`/sys` 主要用于以下目的：

1. 设备管理：展示系统中硬件设备的层次结构，例如 USB、PCI 设备等。
2. 内核参数配置：允许动态调整内核参数和模块行为。
3. 电源管理：控制设备的电源状态（如挂起、唤醒）。
4. 热插拔支持：管理设备的插拔事件。

简单来说，`/sys` 是一个用户空间与内核交互的接口，用于管理和监控系统硬件和内核状态。

### 8.15 `/tmp`（临时）

`/tmp` 文件夹在 Linux 系统中用于存储临时文件。它的主要作用是：

1. **临时存储**：供应用程序和用户存放临时生成的文件，这些问及那通常不需要长期保存。
2. **系统清理**：系统会定期或在重启时自动清理 `/tmp` 中的文件，确保不会占用过多磁盘空间。
3. **共享访问**：所有用户和进程都可以读写 `/tmp`，适合需要临时共享数据的场景。

简单来说，`/tmp` 是一个临时文件存放区，用于存放短期使用的文件，系统会自动管理其内容。

### 8.16 `/var`（可变数据）

`/var` 是 Linux 文件系统中的一个核心目录，全称是 Variable Data（可变数据）。顾名思义，它主要用来存放那些经常变化的数据，比如日志、缓存、邮件、数据库等。这些数据会随着系统的运行不断更新，因此需要单独存放。

下面是 `/var` 目录中的一些文件 / 文件夹举例：

1. `/var/log`：存放系统日志文件。
2. `/var/cache`：存放应用程序的缓存数据。
3. `/var/lib`：存放应用程序的状态信息和持久化数据。

`/var` 目录中的数据是系统运行的关键，比如：

- 日志文件：帮助你排查系统或应用程序的问题。
- 缓存数据：加速应用程序的运行。
- 邮件和任务队列：确保系统任务和通信的正常进行。

如果 `/var` 目录被填满（比如日志文件过多），可能会导致系统无法正常运行。因此，可以定期清理 `/var` 目录中的不必要文件。

CentOS 中如果要实时查看最新的日志，可以使用命令：

```bash
tail -f /var/log/messages
```













