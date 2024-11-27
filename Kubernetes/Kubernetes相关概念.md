# Kubernetes 相关概念

## 1. Helm Chart

Helm Chat 是 K8s 中的一个包管理工具，类似于操作系统中的 apt、yum 或 Homebrew。它使得用户可以更简单地定义、安装和管理 K8s 应用程序。下面是 Helm Chart 的详细介绍：

### 1.1 Helm Chart 是什么？

Helm Chart 是一组用于描述 K8s 应用的 YAML 文件，通过这些文件，用户可以定义 K8s 集群中的各种资源（例如，Deployment、Service、ConfigMap 等）。它将这些定义打包成一个 Chart，这样用户就可以使用该 Chart 轻松地在 K8s 中部署和管理应用程序。

### 1.2 Helm 的组成部分

Helm 主要由两个部分组成：

- Helm CLI：命令行工具，用户可以用它来和 K8s 交互，管理和部署 Chart。
- Helm Chart Repository：Chart 的存储库，类似于包管理器的仓库。用户可以从公共或私有的 Chart 仓库中查找和下载 Chart。

### 1.3 Helm Chart 的结构

一个典型的 Helm Chart 包含以下文件和目录：

- `Chart.yaml`：定义了 Chart 的基本信息，包括名称、版本、描述等。
- `values.yaml`：这是一个重要的文件，用于定义默认的配置参数。用户可以通过这个文件自定义 Chart 的行为。
- `templates/`：该目录包含用于渲染 K8s 资源定义的模板文件。这些模板使用 Go 模板语法，可以通过 values.yaml 文件中的值进行动态替换。
- `README.md`：通常包含 Chart 的使用说明和描述。
- `charts/`：存放依赖的其他 Chart。
- `.helmignore`：定义在打包 Chart 时要忽略的文件或目录，类似于 `.gitignore`。

### 1.4 Helm 的操作流程

使用 Helm 部署应用通常包括以下几个步骤：

- 添加仓库：例如 `helm repo add stable https://charts.helm.sh/stable`。
- 查找 Chart：使用 `helm search` 命令查找所需的 Chart。
- 安装 Chart：使用 `helm install` 命令来部署 Chart，例如 `helm install my-release stable/mysql`。这里的 `my-release` 是我们给 Chart 部署指定的名称。
- 查看部署：`helm list` 可以查看所有已部署的 Chart。
- 更新 Chart：当我们想修改 Chart 的配置或者更新 Chart 版本时，可以使用 `helm upgrade` 命令。
- 删除 Chart：如果不再需要某个部署，可以使用 `helm uninstall` 命令删除。

### 1.5 Helm Chart 的优势

- 简化复杂部署：通过 Helm，用户可以在一个文件中定义复杂的 K8s 资源，使得管理和重复部署变得更容易。
- 版本管理：Helm 支持对 Chart 版本的管理，用户可以轻松地回滚到以前的版本。
- 支持多环境配置：通过 values.yaml 文件，用户可以为不同的环境提供不同的配置（例如开发、测试和生产环境）。
- 复用性：Helm Chart 可以方便地重用。例如，用户可以将一个应用的 Chart 分享给其他开发人员或团队。

### 1.6 常用命令示例

- 安装 Chart：`helm install <release-name> <chart-name>`
- 查看所有部署的 Release：`helm list`
- 更新 Chart：`helm upgrade <release-name> <chart-name>`
- 卸载 Release：`helm uninstall <release-name>`
- 查看 Release 历史记录：`helm history <release-name>`
- 回滚到指定版本：`helm rollback <release-name> <version>`

### 1.7 Helm Chart 示例

假如你想部署一个简单的 Nginx 应用程序，values.yaml 可以是如下内容：

```yaml
replicaCount: 2
image:
	repository: nginx
	tag: latest
	pullPolicy: IfNotPresent
service:
	type: loadBalancer
	port: 80
```

在 templates 目录下，可以创建一个名为 `deployment.yaml` 的模板文件：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
	name: {{ .Release.Name }}-nginx
spec:
	replicas: {{ .Values.replicaCount }}
	template:
		spec:
			containers:
			  - name: nginx
			    image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
                 ports:
                   - containerPort: {{ .Values.service.port }}
```

这样，我们就可以使用 `helm instal my-nginx ./nginx-chart` 来在 K8s 中部署一个带有 Nginx 的应用。

### 1.8 应用场景

- 部署为服务架构应用：使用 Helm，可以方便地将复杂的微服务架构应用部署到 K8s 集群中。
- 持续集成与持续交付（CI/CD）：Helm 可以和 CI/CD 系统（如 Jenkins、Gitlab CI/CD）结合使用，实现自动化的应用部署。
- 管理配置变化：在 values.yaml 文件中修改配置后，只需使用 `helm upgrade` 命令即可快速更新应用。

总之，Helm Chart 在 K8s 中极大地简化了应用的打包、发布和管理，使得应用的部署过程变得标准化和可重复。

## 2. ConfigMap

在 Kubernetes 中，`ConfigMap` 是一种用于管理和配置应用程序的非机密数据的 API 对象。它允许你将配置数据域容器化应用程序分离，使应用程序的配置可以在不重新构建镜像的情况下进行修改。

### 2.1 ConfigMap 的作用

`ConfigMap` 主要用于存储应用程序的配置信息，例如：

- 配置文件内容
- 环境变量
- 命令行参数

通过使用 `ConfigMap`，你可以将配置数据域容器的定义分离开来，从而可以在不同的环境（如开发、测试、生产环境）中使用不同的配置，而无需更改应用程序的 Docker 镜像。

### 2.2 ConfigMap 的创建

`ConfigMap` 可以通过以下几种方式创建：

- 使用 `YAML` 或 `JSON` 文件定义 `ConfigMap`
- 通过命令行直接创建
- 通过 `kubectl` 从现有文件或目录中创建

以下是一个通过 YAML 文件定义 `ConfigMap` 的示例：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
	name: my-config
data:
	# 存储 key-value 键值对
	app.properties:
    	database.url=jdbc:mysql://localhost:3306/mydb
    	database.user=root
    	database.password=password
 	log_level: "DEBUG"	
```

### 2.3 使用 ConfigMap

`ConfigMap` 可以在 Pod 中以多种方式使用：

- 作为环境变量：将 `ConfigMap` 中的数据注入为容器的环境变量。
- 作为命令行参数：将 `ConfigMap` 中的数据作为参数传递给容器的启动命令。
- 作为挂载卷（Volume）：将 `ConfigMap` 作为文件挂载到容器内，从而读取或写入配置文件。

以下是一个将 `ConfigMap` 数据挂载为环境变量的 Pod 配置示例：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    env:
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: my-config
          key: log_level
```

### 2.4 ConfigMap 的优势

- 解耦应用与配置：可以在不改变容器镜像的情况下修改应用的配置。
- 动态更新：更新 `ConfigMap` 后，容器可以动态感知配置的变化。
- 集中管理：可以在 K8s 集群中统一管理所有应用的配置。

### 2.5 ConfigMap 与 Secret 的区别

`ConfigMap` 适用于存储非机密的配置信息，而 `Secret` 则用于存储敏感数据（如密码、API 密钥）。虽然两者在使用方式上非常类似，但 `Secret` 会对数据进行 Base64 编码，并提供更多的安全保护机制。

## 3. Ingress

Ingress 是 Kubernetes 中用于管理外部访问集群服务的一种资源类型。它提供了一种基于 HTTP 和 HTTPS 的路由机制，能够将外部请求路由到集群内部的不同服务。Ingress 资源通常用于处理外部流量进入 Kubernetes 集群时的负载均衡、SSL 终止、基于路径的路由等任务。

### 3.1 Ingress 的关键特点

1. 路由请求：Ingress 控制器根据定义的规则将请求路由到适当的服务。路由规则通常包括：
    - 基于主机名（例如 `www.example.com`）。
    - 基于 URL 路径（例如 `/api/*`）。
2. 负载均衡：Ingress 允许将流量分发到多个后端服务，提供负载均衡功能。
3. SSL / TLS：终止：Ingress 还支持 SSL / TLS 终止，也就是外部请求到达 Ingress 控制器时，它可以解密 HTTPS 请求并将其转发为 HTTP 请求到内部服务。
4. 认证和授权：通过集成外部认证服务，Ingress 可以进行身份验证和授权。

### 3.2 Ingress 工作原理

Ingress 本身并不是一个可以直接处理流量的组件，它需要和一个 Ingress Controller 一起工作。Ingress Controller 是一个在 Kubernetes 集群中运行的控制器，负责监控 Ingress 资源并实际执行流量路由的工作。

常见的 Ingress Controller：

- NGINX Ingress Controller：最流行的 Ingress Controller，基于 NGINX 作为反向代理。
- Traefik：另一个流行的 Ingress Controller，提供更加动态的配置和自动化功能。
- HAProxy、Envoy 等也可以作为 Ingress Controller。

### 3.3 一个简单的 Ingress 示例

假设我们有两个服务：`service-1` 和 `service-2`，我们希望根据 URL 路径将请求分别转发到这两个服务。以下是一个简单的 Ingress 配置示例：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /service-1
        pathType: Prefix
        backend:
          service:
            name: service-1
            port:
              number: 80
      - path: /service-2
        pathType: Prefix
        backend:
          service:
            name: service-2
            port:
              number: 80
```

在这个例子中，所有发往 `example.com/service-1` 的请求将被路由到 `service-1`，而所有发往 `example.com/service-2` 的请求将被路由到 `service-2`。

### 3.4 配置 Ingress Controller

在 Kubernetes 集群中，安装和配置 Ingress Controller 是使用 Ingress 的前提。安装时，可以通过 Helm 图标或直接应用 Kubernetes YAML 文件进行配置。

例如，使用 Helm 安装 NGINX Ingress Controller：

```bash
helm install nginx-ingress ingress-nginx/ingress-nginx
```

安装完成后，Ingress Controller 会自动处理集群中的所有 Ingress 资源，并确保根据定义的规则正确地将流量路由到相应的服务。

### 3.5 总结

Ingress 提供了 Kubernetes 集群外部与内部之间的 HTTP 和 HTTPS 流量管理功能，是实现复杂路由、负载均衡和安全访问控制的关键组件。它的灵活性与 Ingress Controller 的结合使得流量管理更加安全和可扩展。

## 4. 正向代理和反向代理

Nginx 是一个高性能的 HTTP 和反向代理服务器。它常用于处理 Web 请求中的反向代理请求，因为它具有轻量级、高并发性和稳定性。反向代理是 Nginx 的一个重要功能，用于在客户端和服务器之间作为中间层，实现负载均衡、缓存加速和安全控制等功能。

### 4.1 正向代理和反向代理的定义

- 正向代理：客户端（比如你的电脑）通过代理服务器去访问外部的资源。代理服务器在客户端和目标服务器之间充当中间人角色，帮助客户端访问它原本无法直接访问的资源。
- 反向代理：代理服务器位于客户端和服务器之间，客户端的请求到达代理服务器后，代理服务器将请求转发给真正的服务器，获取数据并返回给客户端。客户端不需要知道背后有多有服务器或服务器的实际 IP 地址。

### 4.2 正向代理和反向代理的区别

- 谁发起请求：正向代理是客户端发起请求，代理服务器代替客户端访问目标服务器；反向代理是客户端的请求先到代理服务器，再由代理服务器转发给后端服务器。
- 谁知道代理的存在：正向代理需要客户端知道代理服务器的地址，因为它主动使用代理来访问外部网络；反向代理对客户端是透明的，客户端只知道代理服务器的地址，而不需要知道后端服务器的地址。
- 使用场景不同：正向代理常用于访问受限的外部资源，比如科学上网；反向代理常用于负载均衡、缓存加速、隐藏服务器 IP 等。

### 4.3 举例说明正向代理和反向代理

**【正向代理】**

假设你在中国，想访问一个被限制的网站（比如某个国外的网站），但是直接访问会被限制。于是你使用了一台位于美国的代理服务器：

- 你的请求先发送到美国的代理服务器。
- 代理服务器帮你向被限制的网站发送请求，获取页面内容。
- 最后代理服务器将页面内容返回给你。

在这个过程中：

- 你知道代理服务器的存在，并且主动请求代理服务器帮你访问。
- 被限制的网站认为请求是来自美国的代理服务器，而不是来自你的电脑。

**【反向代理】**

现在假设你访问一个大型网站（比如淘宝、亚马逊），它们背后可能有成千上万台服务器来支持庞大的流量。为了让用户访问体验更快，网站运维会使用 Nginx 作为反向代理服务器来优化请求处理：

- 你的请求首先到达 Nginx 服务器（反向代理服务器）。
- Nginx 会根据请求，阿静你的请求转发到不同的服务器，比如一台服务器处理商品展示，另一台服务器处理订单等。
- 处理完成后，Nginx 会将服务器的响应结果返回给你。

在这个过程中：

- 你只知道 Nginx 代理服务器的 IP 地址，不知道背后的服务器。
- Nginx 代理服务器决定请求如何转发，而你不需要关心。

### 4.4 实际中的使用对比

- 正向代理：
    - 场景：公司使用的防火墙设置了访问权限，某些网站无法访问；员工可以通过设置正向代理访问这些网站。
    - 优势：绕过访问限制，提升隐私保护。
    - 客户端和代理服务器之间需要一定的信任关系。
- 反向代理：
    - 场景：一个电商网站（比如亚马逊）有数千台服务器，使用反向代理来做负载均衡，将用户请求均匀分配给不同的服务器；当一台服务器出现问题时，反向代理可以自动将流量转发到其他健康的服务器。
    - 优势：提升网站稳定性和性能，减轻服务器压力，隐藏服务器 IP，增强安全性。
    - 用户和反向代理之间保持交互，用户无需知道实际服务器的存在。

### 4.5 总结

- 正向代理帮助客户端访问外部资源，客户端知道代理的存在。常用于访问受限资源和隐私保护。
- 反向代理帮助服务器处理客户端请求，客户端不需要知道服务器的存在。常用于负载均衡、缓存、隐私保护等。

## 5. HostNetwork

在 Kubernetes 中，Pod 是应用程序部署和管理的基本单位，它通常运行在容器中。`HostNetwork` 是 Pod 的一个选项，它决定了 Pod 是否使用主机的网络命名空间。

### 5.1 HostNetwork 的定义

`HostNetwork` 是 Pod 配置中的一个布尔值参数，表示 Pod 是否使用宿主机的网络栈。如果设置为 `true`，Pod 会共享宿主机的网络命名空间，并使用宿主机的 IP 地址进行通信。如果设置为 `false`（或未设置），则 Pod 将使用自己的网络命名空间，并为其分配一个独立的 IP 地址。

### 5.2 HostNetwork 为 true 时的行为

当 Pod 设置了 `HostNetwork: true`，它将与宿主机共享网络栈，具有以下特点：

- IP 地址：Pod 会使用宿主机的 IP 地址。这意味着 Pod 中的容器会直接使用宿主机的网络接口进行通信，而不是通过 Kubernetes 分配的虚拟 IP 地址。
- 端口冲突：由于 Pod 使用宿主机的网络，Pod 中的容器如果监听相同的端口，可能会与宿主机上的其他进程发生端口冲突。因此，Pod 内的容器需要谨慎选择端口。
- 直接访问主机网络：Pod 可以直接访问主机的网络接口，如访问主机上的其他服务，或通过主机的网络进行外部通信。
- 性能优势：由于 Pod 不使用虚拟网络接口，它可能具有更低的网络延迟和更高的网络吞吐量，适用于需要高性能网络通信的应用。

### 5.3 HostNetwork 为 false 时的行为

当 `HostNetwork` 为 `false` 时，Pod 使用自己的网络命名空间：

- 独立的 IP 地址：每个 Pod 都会有一个独立的 IP 地址，通常由 Kubernetes 的网络插件分配。
- 网络隔离：Pod 内部的容器相互隔离，并且通过 Kubernetes 的网络策略（Network Policies）可以进一步限制网络访问。
- 端口映射：Pod 中的容器需要通过端口映射（例如，通过服务、Ingress 或其他网络代理）来与外部通信。

### 5.4 HostNetwork 的使用场景

使用 `HostNetwork` 的场景通常包括以下几种情况：

- 高性能网络应用：对于需要高性能、低延迟的网络通信的应用，例如数据库等，使用 `HostNetwork` 可以减少网络虚拟化带来的开销。
- 需要访问主机网络的应用：例如网络代理、负载均衡器或直接操作宿主机网络接口的工具，可以通过 `HostNetwork` 来实现。
- 日志收集和监控：一些日志搜集器或监控工具（如 Fluentd、Prometheus 和 Node Exporter）需要访问宿主机的网络接口，`HostNetwork` 提供了这种能力。

### 5.5 限制与注意事项

- 端口冲突：由于多个 Pod 共享宿主机的网络栈，它们不能在同一端口上监听。因此，在使用 `HostNetwork` 时，必须小心选择端口，确保没有冲突。
- 安全性问题：使用 `HostNetwork` 会使 Pod 中的容器具有较高的权限，因为它们可以直接访问宿主机的网络栈。这可能带来一定的安全风险，尤其是在多租户环境中。
- 网络隔离丧失：通常，Kubernetes 会为每个 Pod 提供网络隔离，而 `HostNetwork` 会使 Pod 与宿主机共享网络，这可能会降低网络隔离的效果。

### 5.6 如何在 Pod 配置中使用 HostNetwork

在 Kubernetes 的 Pod 配置文件中，`HostNetwork` 可以在 `spec` 部分进行设置：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  hostNetwork: true  # 使用宿主机的网络
  containers:
    - name: my-container
      image: my-image
      ports:
        - containerPort: 80
```

### 5.7 总结

- 使用 `HostNetwork: true` 可以让 Pod 直接使用宿主机的网络命名空间，提供低延迟和高吞吐量的网络性能。
- 这种配置适合宿主机网络或具有高性能网络需求的应用，但也需要注意端口冲突和安全性问题。
- 一般情况下，如果没有特殊需求，建议默认使用独立的网络命名空间（即 `HostNetwork: false`），以保持网络隔离和安全。

## 6. Kubernetes 常见端口

| 组件                    | 默认端口   | 描述                                       |
| ----------------------- | ---------- | ------------------------------------------ |
| kube-apiserver          | 6443       | Kubernetes 控制平面 API 端口               |
| kube-controller-manager | 10252      | 控制器管理端口                             |
| kube-scheduler          | 10251      | 调度器端口                                 |
| kubelet                 | 10250      | 与 Node 上的 kubelet 进行通信端口          |
| kube-proxy              | 10256      | 服务代理健康检查端口                       |
| etcd                    | 2379，2380 | etcd 客户端与 peer 通信端口                |
| coredns                 | 53         | dns 服务端口                               |
| ingress controller      | 80，443    | 外部访问 Kubernetes 服务的 HTTP/HTTPS 端口 |
| Dashboard               | 8001       | Kubernetes Dashboard Web UI 端口           |
| Flannel CNI             | 8285，8472 | Flannel 网络插件的通信端口                 |
| Metrics Server          | 8082       | 监控指标收集端口                           |
| Prometheus              | 9090       | Prometheus Web UI 和 API 端口              |

## 7. iptables

### 7.1 iptables 概念

#### 【防火墙的基础分类】

在开始了解 iptables 之前，我们需要明确什么是防火墙。

1. 逻辑分类：

    - 主机防火墙：用于保护单个主机的安全。例如，配置一个本地规则防止恶意扫描。
    - 网络防火墙：通常位于网络边界，用来保护整个网络的入口或出口，如路由器上的防火墙。

    例子：

    - 主机防火墙：限制只能通过 SSH 访问特定服务器。
    - 网络防火墙：企业网关防止内网主机直接暴露在公网。

2. 物理分类：

    - 硬件防火墙：通常是专用设备，如 Cisco ASA，性能强大但成本高。
    - 软件防火墙：运行在普通硬件上的防火墙，如 `iptables`。

    补充说明：硬件防火墙往往结合了专用硬件加速技术，更适用于高性能需求场景，而软件防火墙则胜在灵活性和低成本。

---

#### 【iptables 和 netfilter 的关系】

很多初学者认为 `iptables` 是防火墙的核心，其实这是个误解。`iptables` 更准确的定义是一个工具，它通过 Linux 内核中的 `netfilter` 框架来实现防火墙功能。

- netfilter：
    - 核心功能：
        1. NAT（网络地址转换）：用于实现内网设备访问公网的功能。
        2. 包过滤：对进出系统的网络包进行检测与处理。
        3. 包修改：对数据包的内容或头信息进行动态调整。
    - 位置：位于 Linux 内核层，性能高效。
- iptables：
    - 本质：用户空间的命令行工具，主要用于操作 netfilter。
    - 功能：通过定义规则，管理数据包如何在系统中流动。

举例说明：

- 假如内网中的一台服务器需要通过公网访问某服务，netfilter 的 NAT 模块可以实现 IP 转换，将私网地址映射到路由器的公网地址上，完成网络访问。

---

#### 【iptables 的核心概念】

**链（Chains）**

链是数据包通过防火墙时的“关卡”，可以理解为数据流的检查点。每个链上可以挂在多个规则，每个规则定义了如何处理数据包。

- 常见链：
    1. PREROUTING：处理入站数据包，在路由决策前。
    2. INPUT：处理流向本机的入站数据包。
    3. FORWARD：处理转发的数据包。
    4. OUTPUT：处理本机发出的出站数据包。
    5. POSTROUTING：处理路由决策后的出站数据包。

数据流示例：

- 本机访问的包：PREROUTING → INPUT。
- 转发的包：PREROUTING → FORWARD → POSTROUTING。
- 本机发出的包：OUTPUT → POSTROUTING。

**表（Table）**

`iptables` 使用表来组织规则。每种专注于一种特定功能：

1. filter 表：最常用，处理包过滤规则，如放行（ACCEPT）或丢弃（DROP）。
2. nat 表：处理 NAT 转换规则，如 SNAT、DNAT。
3. mangle 表：处理高级的包修改规则。
4. raw 表：关闭 NAT 的连接追踪，用于提高性能。

表与链的对应关系：

- PREROUTING：raw、mangle、nat。
- INPUT：mangle、filter。
- FORWARD：mangle、filter。
- OUTPUT：raw、mangle、nat、filter。
- POSTROUTING：mangle、nat。

**规则（Rules）**

每条规则包括以下两部分：

1. 匹配条件：决定是否匹配数据包。
    - 基本匹配条件：源地址、目标地址、协议类型。
    - 扩展匹配条件：依赖模块扩展，如端口号、TCP 标志。
2. 动作（Target）：定义匹配成功后的处理方式：
    - 常见动作：
        - ACCEPT：放行数据包。
        - DROP：丢弃数据包，不返回信息。
        - REJECT：拒绝数据包并返回响应。
        - LOG：记录数据包信息到日志。

---

#### 【iptables 的实际应用】

**实例一：本地防火墙配置**

场景：只允许特定 IP 访问 SSH 服务。

规则：

```bash
iptables -A INPUT -p tcp --dport 22 -s 192.168.0.100 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP
```

解析：

- 第一条规则：允许 `192.168.1.100` 的 IP 地址访问 22 端口。
- 第二条规则：丢弃其他 IP 的 SSH 访问请求。

**示例二：NAT 实现内网设备访问公网**

场景：内网主机通过路由器共享公网地址上网。

规则：

```bash
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

解析：

- 将所有从内网出去的包的源地址改为路由器的公网地址，便于网络通信。

**示例三：转发规则**

场景：将访问本机某端口的数据包转发到内网某台服务器

规则：

```bash
iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.1.50:80
```

解析：

- 将所有到达本机 8080 端口的 TCP 请求转发到内网主机 `192.168.1.50` 的 80 端口。

---

#### 【iptables 的规则优先级】

1. 当多个表挂载在同一链时，规则执行顺序
    - raw → mangle → nat → filter。
2. 数据包在链中依次匹配规则，直到找到匹配项后执行动作。

---

#### 【自定义链：更灵活的规则管理】

除了默认链外，`iptables` 支持自定义链。这种链是为特定场景设计的，可以减少规则重复。

例子：

```bash
iptables -N MY_CHAIN
iptables -A INPUT -p tcp --dport 80 -j MY_CHAIN
iptables -A MY_CHAIN -s 192.168.1.0/24 -j ACCEPT
iptables -A MY_CHAIN -j DROP
```

解析：

- 自定义链 `MY_CHAIN` 被挂载在 INPUT 链。
- MY_CHAIN 中的规则：允许 192.168.1.0/24 网段的访问，拒绝其他流量。

### 7.2 实际操作之规则查询

#### iptables 表和链

- 表：`iptables` 预定义了四张表，分别是 `raw`、`mangle`、`nat` 和 `filter`。每张表都有特定的功能，其中 `filter` 表是最常用的，主要负责网络数据包的过滤。
- 链：每张表内包含多个链，链相当于一系列规则的集合。`filter` 表中的三个主要链是 `INPUT`、`FORAWRD`、`OUTPUT`，分别处理进入本机的数据包、转发给其他机器的数据包以及本机产生的外出数据包。

#### 查看规则

- 查看所有规则：使用 `iptables -L` 命令可以查看 `filter` 表的所有规则。若要查看其他表的规则，可以使用 `-t` 选项指定表名，如 `iptables -t nat -L`。
- 查看特定链的规则：可以通过制定链名来查看特定链的规则，如 `iptables -L INPUT`。
- 显示详细信息：加上 `-v` 选项可以显示更详细的信息，包括匹配的数据包数量（`pkts`）、字节数（`bytes`）等。
- 不进行域名解析：使用 `-n` 选项可以防止将 IP 地址转换为域名，提高命令执行速度。
- 显示规则编号：使用 `--line-numbers` 选项可以在输出中显示规则的编号，便于管理。
- 显示精确计数：使用 `-x` 选项可以显示未经格式化的精确计数值。

#### 示例命令

- `iptables -L`：查看 `filter` 表的所有规则。
- `iptables -t nat -L`：查看 `nat` 表的所有规则。
- `iptables -L INPUT`：查看 `filter` 表中所有 `INPUT` 链的规则。
- `iptables -v -L`：查看 `filter` 表的所有规则，显示详细信息。
- `iptables -n -L`：查看 `filter` 表的所有规则，不进行域名解析。
- `iptables --line-numbers -L`：查看 `filter` 表的所有规则，并显示规则编号。
- `iptables -v -x -L`：查看 `filter` 表的所有规则，显示详细信息及精确计数。

#### 链的默认策略

每个链都有一个默认策略（`policy`），表示如果没有规则匹配时如何处理数据包。昌吉那的默认策略有 `ACCEPT`（接受）和 `DROP`（丢弃）。例如，`INPUT` 链的默认策略是 `ACCEPT`，这意味着如果没有规则明确拒绝某个数据包，该数据包将会被接受。

### 7.3 规则管理

#### 规则概念

- 规则：由匹配条件和动作两部分组成。
- 匹配条件：例如报文的源地址、目标地址、源端口、目标端口等。
- 动作：常见的有 `ACCEPT`（接受）、`DROP`（丢弃）、`REJECT`（拒绝）。

#### 规则操作

- 查看规则：使用 `iptables -L` 命令可以查看当前 iptables 规则。
- 清空规则：使用 `iptables -F` 可以清空指定链中的规则。如果不指定链名，会清空整个表中的所有规则。
- 添加规则：
    - 使用 `-A` 选项在链尾追加规则。
    - 使用 `-I` 选项在链头或指定位置插入规则。
- 删除规则：
    - 根据规则编号删除：使用 `-D` 选项加上规则编号。
    - 根据匹配条件与动作删除：使用 `-D` 选项加上匹配条件和动作。
- 修改规则：
    - 使用 `-R` 选项修改指定编号的规则。需要注意的是，使用 `-R` 选项时必须指明原规则的匹配条件，否则修改后的规则可能不正确。
    - 另一种修改方式是先删除原有规则，再在相同位置插入新的规则。
- 设置默认策略：使用 `-P` 选项设置指定链的默认策略。例如 `iptables -P INPUT DROP` 表示将 `INPUT` 链的默认策略设置为丢弃所有报文。

#### 规则顺序的重要性

- 规则的匹配是按顺序进行的，一旦报文匹配到某条规则，就会立即执行该规则的动作，后续的规则将不再匹配该报文。
- 因此，规则的顺序非常重要，通常建议将更具体的规则放在更前面，更通用的规则放在后面。

#### 规则保存

- CentOS 6：使用 `service iptables save` 命令可以将当前的 iptables 规则保存到 `/etc/sysconfig/iptables` 文件中。
- CentOS 7：需要先安装  `iptables-services` 包，然后使用 `service iptables save` 命令保存规则。或者使用 `iptables-save > /etc/sysconfig/iptables` 命令手动保存规则。

#### 常用命令总结

- 添加规则：

    ```bash
    iptables -t 表名 -A 链名 匹配规则 -j 动作
    iptables -t 表名 -I 链名 [规则序号] 匹配条件 -j 动作
    ```

- 删除规则：

    ```bash
    iptables -t 表名 -D 链名 规则序号
    iptables -t 表名 -D 链名 -j 动作
    ```

- 修改规则：

    ```bash
    iptables -t 表名 -R 链名 规则序号 匹配条件 -j 动作
    ```

- 设置默认策略：

    ```bash
    iptables -t 表名 -P 链名 动作
    ```

- 保存规则：

    ```bash
    service iptables save
    iptables-save > /etc/sysconfig/iptables
    ```


### 7.4 iptables 匹配条件总结（1）

#### 基础匹配条件

1. 源地址匹配 `-s`

    `iptables` 中使用 `-s` 选项来匹配报文的源地址。这是一个可以具体的 IP 地址，也可以是一个网段。例如，以下命令将拒绝所有来自 `192.168.1.146` 的流量：

    ```bash
    iptables -t filter -A INPUT -s 192.168.1.146 -j DROP
    ```

    同时指定多个源地址时，可以用逗号分隔：

    ```bash
    iptables -t filter -A INPUT -s 192.168.1.146,192.168.1.147 -j DROP
    ```

    还可以对匹配条件取反，使用 `!` 符号：

    ```bash
    iptables -t filter -A INPUT ! -s 192.168.1.146 -j ACCEPT
    ```

    上述命令表示，只要报文的源地址不是 `192.168.1.146`，就接受报文。

2. 目标地址匹配 `-d`

    与源地址匹配类似，`-d` 选项用于匹配报文的目标地址。例如，拒绝所有发送给 `10.6.0.156` 的流量：

    ```bash
    iptables -t filter -A INPUT -d 10.6.0.156 -j DROP
    ```

    同样地，可以指定多个目标地址或取反：

    ```bash
    iptables -t filter -A INPUT -d 10.6.0.156,10.6.0.101 DROP
    iptables -t filter -A INPUT ! -d 10.6.0.156 -j ACCEPT
    ```

3. 协议类型匹配 `-p`

    `-p` 选项用于指定需要匹配的报文协议类型，如 `tcp`、`udp` 等。例如，只允许 `tcp` 协议的流量：

    ```bash
    iptables -t filter -A INPUT -p tcp -j ACCEPT
    ```

    如果不指定协议类型，默认匹配所有类型的协议。

4. 网卡接口匹配 `-i` 和 `-o`

    `-i` 选项用于匹配报文流入的网卡接口，而 `-o` 选项用于匹配报文流出的网卡接口。例如，拒绝通过 `eth4` 流入的 `ICMP` 请求：

    ```bash
    iptables -t filter -A INPUT -i eth4 -p icmp -j DROP
    ```

    拒绝通过 `eth4` 流出的 `ICMP` 请求：

    ```bash
    iptables -t filter -A OUTPUT -i eth4 -p icmp -j DROP
    ```

#### 扩展匹配条件

1. 源端口和目标端口匹配 `--sport` 和 `--dport`

    源端口和目标端口匹配需要特定的扩展模块，如 `tcp` 模块。例如，拒绝所有尝试连接到 `22` 端口的 `TCP` 流量：

    ```bash
    iptables -t filter -A INPUT -p tcp --dport 22 -j DROP
    ```

    可以同时指定多个离散的端口，使用 `multiport` 模块：

    ```bash
    iptables -t filter -A INPUT -p tcp -m multiport --dports 22,80 -j DROP
    ```

2. 其他扩展模块

    `iptables` 提供了多种扩展模块，如 `multiport`、`state` 等，可以根据需求选择合适的模块。例如，使用 `multiport` 模块同时指定多个端口范围：

    ```bash
    iptables -t filter -A INPUT -p tcp -m multiport --dports 22,80:88 -j DROP
    ```

#### 小结

- 当规则中同时存在多个匹配条件时，多个条件之间默认存在“与”的关系，即报文必须同时满足所有条件，才能被规则匹配。
- `-s` 用于匹配报文的源地址，可以同时指定多个源地址，每个 IP 之间用逗号隔开，也可以指定为一个网段。
- `-d` 用于匹配报文的目标地址，可以同时指定多个目标地址，每个 IP 之间用逗号隔开，也可以指定为一个网段。
- `-p` 用于匹配报文的协议类型，可以匹配的协议类型包括 `tcp`、`udp`、`udplite`、`icmp`、`esp`、`ah`、`sctp` 等。
- `-i` 用于匹配报文是从哪个网卡流入本机的，如 `tcp` 模块的 `--sport` 和 `--dport`，`multiport` 模块的 `dports` 等。

### 7.5 iptables 匹配条件总结（2）

#### iprange 扩展模块

`iprange` 模块允许指定一段连续的 IP 地址范围，用于匹配报文的源地址或目标地址。这对于需要对特定 IP 段进行控制的场景特别有用。

示例：

- 如果报文的源 IP 地址在 `192.168.1.127` 到 `192.168.1.146` 之间，则丢弃报文。

    ```bash
    iptables -t filter -I INPUT -m iprange --src-range 192.168.1.127-192.168.1.146 -j DROP
    ```

#### string 扩展模块

`string` 模块允许指定要匹配的字符串，如果报文中包含该字符串，则满足匹配条件。这对于过滤含有特定内容的数据包非常有效。

实例：

- 如果报文中包含字符串“OOXX”，则丢弃该报文。

    ```bash
    iptables -t filter -I INPUT -p tcp --sport 80 -m string --algo hm --string "OOXX" -j DROP
    ```

    其中，`--algo bm` 表示使用 Boyer-Moore 算法进行字符串匹配，`--string "OOXX"` 指定了要匹配的字符串。

#### time 匹配模块

`time` 模块可以根据时间段来匹配报文，如果报文到达的时间在指定的时间范围内，则满足匹配条件。这对于实施时间敏感的安全策略非常有用。

示例：

- 每天早上 9 点到下午 6 点禁止访问 web 服务。

    ```bash
    iptables -t filter -I OUTPUT -p tcp --dport 80 -m time --timestart 09:00:00 --timestop 18:00:00 -j REJECT
    ```

- 只有周六日不能访问 web 服务。

    ```bash
    iptables -t filter -I OUTPUT -p tcp --dport 80 -m time --weekdays 6,7 -j REJECT
    ```

#### connlimit 扩展模块

`connlimit` 模块可以限制每个 IP 地址同时连接到服务器的连接数量。这对于防止服务器过载非常重要。

示例：

- 每个 IP 地址最多只能占用两个 SSH 连接。

    ```bash
    iptables -t filter -I INPUT -p tcp --dport 22 -m connlimit --connlimit-above 2 -j REJECT
    ```

- 限制每个 C 类网段（例如 `192.168.1.0/24`）最多有两个 SSH 连接。

    ```bash
    iptables -t filter -I INPUT -p tcp --dport 22 -m connlimit --connlimit-above 2 --connlimit-mask 24 -j REJECT
    ```

#### limit 扩展模块

`limit` 模块可以限制单位时间内流入的数据包数量，这对于防止某些类型的工具（如 DoS 攻击）非常有用。

示例：

- 限制每分钟最多流入 10 个 ICMP 包。

    ```bash
    iptables -t filter -I INPUT -p icmp -m limit 10/minute -j ACCEPT
    ```

- 限制每分钟最多流入 10 个 ICMP 包，初始突发量为 3。

    ```bash
    iptables -t filter -I INPUT -p icmp -m limit --limit-burst 3 --limit 10/minute -j ACCEPT
    iptables -t filter -A INPUT -p icmp -j REJECT
    ```

### 7.6 扩展匹配条件之 `--tcp-flags`

在深入探讨 `--tcp-flags` 选项之前，有必要回顾一下 TCP 协议的基础知识。TCP（传输控制协议）是一种面向连接的、可靠的、基于字节流的传输层通信协议。TCP 头包含多个字段，其中包括几个重要的标志位（flags），这些标志位用于控制连接的建立、数据传输以及连接的终止等操作。

#### TCP 头中的标志位

TCP 头中的标志位包括但不限于以下几种：

- SYN（Synchronize Sequence Numbers）：同步序列编号，用于建立连接。
- ACK（Acknowledgement）：确认，用于确认接收到的数据包。
- FIN（Finish）：结束，用于关闭连接。
- RSI（Reset）：重置，用于异常情况下重置连接。
- URG（Urgent）：紧急，指出本报文段中有紧急数据。
- PSH（Push）：推送，告诉接收方立即将报文段交给应用层，而不是等待缓冲区满后再交。

#### `--tag-flags` 选项

`--tcp-flags` 选项允许用户根据 TCP 头中的标志位来过滤网络流量。该选项接受两个参数：

- 第一个参数是一个逗号分隔的列表，列出所有需要考虑的标志位。
- 第二个参数也是一个逗号分隔的列表，列出这些标志为中哪些应该被设置为 1（即激活状态）。

例如，要匹配一个 TCP SYN 标志位被设置的包，同时确保其他标志位未被设置，可以使用如下命令：

```bash
iptables -A INPUT -p tcp --tcp-flags SYN,ACK,FIN,RST,URG,PSH SYN -j LOG
```

这条规则将匹配所有仅设置了 SYN 标志位的包，并记录这些包的信息。这里，`SYN,ACK,FIN,RST,URG,PSH` 定义了考虑的标志位集合，而 `SYN` 则指定了在这个集合中哪些标志位需要被设置为 1。

#### 简化标志位匹配

对于常见的标志位组合，`iptables` 提供了一些简化的方法来进行匹配。例如，`ALL` 关键字可以用来代替所有的标准 TCP 标志位（即 `SYN,ACK,FIN,RST,URG,PSH`）。此外，`--syn` 选项是 `--tcp--flags SYN,RST,ACK,FIN SYN` 的一个快捷方式，专门用于匹配 TCP 连接建立的第一个包。

#### 示例

假设我们想要阻止任何尝试连接到 SSH 服务（默认端口 22）的请求，可以使用如下命令：

```bash
iptables -A INPUT -p tcp --dport 22 --syn -j DROP
```

这条规则会丢弃所有尝试通过端口 22 建立新连接的 SYN 包，从而有效地阻止了新的 SSH 连接尝试。

### 7.7 udp 扩展与 icmp 扩展

#### udp 扩展

UDP（User Datagram Protocal）是一种无连接的传输层协议，适用于需要快速传输数据且对数据传输可靠性要求不高的应用。在 iptables 中，udp 扩展模块提供了对 UDP 协议报文的源端口（`--sport`）与目标端口（`--dport`）的匹配功能。

- 基本使用：当你使用 `-p udp` 指定协议时，可以省略 `-m udp`，因为 iptables 会自动调用与协议名称相同的模块。例如，允许 Samba 服务的 137 和 138 端口通过防火墙，可以这样配置：

    ```bash
    iptables -t filter -I INPUT -p udp --dport 137 -j ACCEPT
    iptables -t filter -I INPUT -p udp --dport 138 -j ACCEPT
    ```

- 端口范围：udp 扩展也支持指定连续的端口范围。例如，开放 137 至 157 之间的所有 UDP 端口。

    ```bash
    iptables -t filter -I INPUT -p udp --dport 137:157 -j ACCEPT
    ```

- 多端口匹配：若需指定多个离散的端口，则可借助 multiport 扩展模块。例如，同时开放 137、138 和 139 三个端口：

    ```bash
    iptables -t filter -I INPUT -p udp -m multiport --dports 137,138,139 -j ACCEPT
    ```

#### ICMP扩展

ICMP（Internet Control Message Protocal）用于报告错误和交换有限的控制信息。它最常被人们熟知的应用是 ping 命令，用于检测网络连通性。

- ICMP 报文类型：ICMP 报文分为查询类和错误类。例如，ping 命令发送的是类型 8（回声请求）的报文，接收方返回的是类型 0（回声响应）的报文。

- 匹配特定类型的 ICMP 报文：你可以使用 `--icmp-type` 选项来匹配特定类型的 ICMP 报文。例如，阻止所有 ping 请求到达本机：

    ```bash
    iptables -t filter -I INPUT -p icmp --icmp-type 8 -j REJECT
    ```

- 使用描述名称匹配：除了数字类型外，还可以使用描述名称来匹配 ICMP 报文。例如，阻止 ping 请求的另一种方式：

    ```bash
    iptables -t filter -I INPUT -p icmp --icmp-type "echo-request" -j REJECT
    ```

### 7.8 state 扩展

#### state 模块的基本概念

`state` 模块允许 `iptables` 根据数据包在网络连接中的状态来进行过滤。在网络通信中，数据包可以处于不同的状态，`state` 模块定义了五种主要状态：

- NEW：表示这是一个新的连接，或者是现有连接的一部分，但不是回应之前的任何数据包。
- ESTABLISHED：表示这是现有连接的一部分，且该连接已经成功建立了双向通信。
- RELATED：表示这个数据包与现有的某个连接相关联，但不属于该连接本身。例如，FTP 的数据传输连接与控制连接的关系。
- INVALID：表示数据包不符合任何已知的连接模式，可能是错误的数据包。
- UNTRACKED：表示数据包未被连接跟踪机制处理，通常是因为配置问题导致。

#### 实践应用

假设我们有一个场景，需要确保服务器只响应来自客户端的合法请求，而不接受任何未经请求的主动连接。在这种情况下，可以使用 `state` 模块来实现这一目标。

#### 示例配置

1. 阻止所有流量

    首先，我们需要设置默认策略，阻止所有流入和流出的数据包：

    ```bash
    iptables -P INPUT DROP
    iptables -P OUTPUT DROP
    iptables -P FORWARD DROP
    ```

2. 允许已建立和相关的连接

    接下来，允许所有已建立的连接和与现有连接相关的数据包通过：

    ```bash
    iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    ```

3. 允许新的 SSH 连接

    如果还需要允许新的 SSH 连接，可以添加如下规则：

    ```bash
    iptables -A INPUT -p tcp --dport 22 -m state --state NEW -j ACCEPT
    iptables -A OUTPUT -p tcp --sport 22 -m state --state NEW -j ACCEPT
    ```

4. 处理异常情况

    对于无效的数据包，可以直接丢弃：

    ```bash
    iptables -A INPUT -m state --state INVALID -j DROP
    iptables -A OUTPUT -m state --state INVALID -j DROP
    ```

通过上述配置，我们不仅能够保证服务器的安全性，还能确保合法的网络通信不受影响。特别是对于像 SSH 这样的服务，通过允许新的连接，用户仍然可以正常登录服务器，同时避免了未经授权的连接尝试。

### 7.9 黑白名单机制

#### iptables 工作原理

在 iptables 中，数据包会依次经过预定义的链，每个链包含一系列规则。当数据包与某条规则匹配时，就会执行该规则指定的动作，如接受（ACCEPT）、拒绝（DROP）或拒绝并通知发送方（REJECT）。如果没有规则匹配，则执行链的默认策略。

#### 黑名单机制

当链的默认策略设置为 `ACCEPT` 时，所有未匹配任何规则的数据包都将被接受。因此，若要实现黑名单机制，即阻止某些特定的数据包，应将规则的动作设置为 `DROP` 或 `REJECT`。这意味着只有那些规则被明确标记为“不受欢迎”的书包才会被组织，其余数据包均被允许通过。例如，如果想要阻止来自某个特定 IP 地址的流量，可以添加如下规则：

```bash
iptables -A INPUT -s 192.168.1.100 -j DROP
```

此规则将阻止来自 IP 地址 192.168.1.100 的所有入站流量。

#### 白名单机制

相反地，当链的默认策略设置为 `DROP` 时，所有未匹配任何规则的数据包都将被拒绝。因此，若要实现白名单机制，即只允许某些特定的数据包，应将规则的动作设置为 `ACCEPT`。这意味着只有那些被规则明确标记为“可信任”的数据包才会被允许通过，其余数据包均被阻止。例如，如果只想允许来自特定 IP 地址的 SSH 访问，可以添加如下规则：

```bash
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.100 -j ACCEPT
```

此规则仅允许来自 IP 地址 192.168.1.100 的 SSH 流量通过。

#### 实践案例：构建简单白名单

假设我们需要为服务器设置一个简单的白名单，只允许特定 IP 地址的 SSH 和 HTTP 访问。首先，确保 INPUT 链的默认策略为 `DROP`：

```bash
iptables -P INPUT DROP
```

接下来，添加允许特定 IP 地址访问 SSH（端口 22）和 HTTP（端口 80）的规则：

```bash
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.100 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -s 192.168.1.100 -j ACCEPT
```

以上配置确保只有来自 192.168.1.100 的 SSH 和 HTTP 请求被允许，其他所有请求均被拒绝。

#### 注意事项

- 默认策略：设置合理的默认策略非常重要。对于生产环境，通常建议采用更为严格的限制，如 `DROP`，以减少安全风险。
- 误操作保护：为了避免因误操作（如 `iptables -F` 清除所有规则）导致无法管理服务器，可以在设置 `DROP` 默认策略前，先确保至少有一条允许管理员远程登陆的规则存在。或者，可以将默认策略设置为 `ACCEPT`，并在链尾添加一条 `DROP` 规则，以实现类似白名单的效果，同时保留管理员的访问权限。
- 测试：在生产环境中应用新的 iptables 规则前，应在测试环境中充分验证其效果。

### 7.10 自定义链

#### 为什么需要自定义链？

在日常运维中，随着网络环境的复杂化，`iptables` 的默认链（如 `INPUT`、`OUTPUT`、`FORWARD` 等）中可能会累积大量的规则。这戏规则可能涉及不同的服务（如 HTTP、SSH）、不同的网络地址（私网 IP、公网 IP）等。当需要对特定服务或特定网络地址的规则进行调整时，如果所有规则都混杂在一起，无疑会增加管理难度。因此，`iptables` 提供了自定义链的功能，帮助我们更好地阻止和管理规则。

#### 如何创建自定义链？

创建自定义链非常简单，只需要使用 `-N` 选项，后面跟上你想创建的链的名字。例如，如果你想创建一个专门用来处理 Web 服务相关规则的自定义链，可以这样做：

```bash
iptables -t filter -N INT_WEB
```

这里，`-t filter` 指定了操作的是 `filter` 表， 而 `-N IN_WEB` 则创建了一个名为 `IN_WEB` 的自定义链。创建完成后，可以通过 `iptables -L` 命令查看，会发现新链的引用计数为 0，说明它还没有被任何默认链引用。

#### 引用自定义链

自定义链创建后，还需要将其引用到合适的默认链中才能生效。例如，如果我们想让所有访问 80 端口的 TCP 报文都由 `IN_WEB` 链中的规则处理，可以在 `INPUT` 链中添加以下规则：

```bash
iptables -t filter -I INPUT -p tcp --dport 80 -j IN_WEB
```

这里，`-I INPUT` 表示在 `INPUT` 链中插入一条新的规则；`-p tcp --dport 80` 指定了该规则匹配所有目标端口为 80 的 TCP 报文；`-j IN_WEB` 则表示将匹配到的报文交给 `IN_WEB` 链处理。

#### 修改自定义链的名称

随着时间的推移，你可能会觉得原来的自定义链名不再适合当前的需求，这时可以使用 `-E` 选项来修改自定义链的名称：

```bash
iptables -E IN_WEB WEB
```

这条命令将 `IN_WEB` 链重命名为 `WEB`。值得注意的是，引用该链的地方也会自动更新为新的名称。

#### 删除自定义链

当一个自定义链不再需要时，可以通过 `-X` 选项将其删除。但请注意，删除自定义链需要满足两个条件：

1. 该自定义链没有被任何默认链引用。
2. 该自定义链中没有任何规则。

例如，要删除名为 `WEB` 的自定义链，首先需要确保它没有被引用且链内无规则。

```bash
iptables -D INPUT -p tcp --dport 80 -j WEB  # 删除引用
iptables -F WEB  # 清空链内的规则
iptables -X WEB  # 删除自定义链
```

### 7.11 网络防火墙

在深入探讨如何利用 iptables 构建网络防火墙之前，我们先简要回顾一下 iptables 的基本概念。iptables 是一个强大的工具，用于在 Linux 系统上配置 IPv4 数据包过滤和 NAT。它支持多种表，每个表包含多个链，链中又包含多个规则。这些规则决定了数据包如何被处理。

#### 防火墙分类

防火墙从逻辑上可以分为两大类：

- 主机防火墙：针对单一主机进行防护。
- 网络防火墙：通常位于网络的入口或边缘，保护整个网络内的主机。

#### iptables 作为网络防火墙

当我们希望 iptables 扮演网络防火墙的角色时，这意味着 iptables 所在的主机必须位于网络的入口位置，负责过滤并转发进出网络的数据包。在这种情况下，iptables 的主要任务是“过滤并转发”。

#### 实验环境搭建

为了更好地理解 iptables 作为网络防火墙的工作原理，我们可以通过以下实验环境进行学习：

- 内部网络：网段为 10.1.0.0/16，包含主机 C（10.1.0.1）和防火墙主机 B（10.1.0.3）。
- 外部网络：包含主机 A（192.168.1.147），通过防火墙主机 B（192.168.1.146）与内部网络通信。

#### 开启核心转发功能

为了让 iptables 所在的主机 B 能够执行转发功能，需要开启核心转发。可以通过修改 `/proc/sys/net/ipv4/ip_forward` 文件或使用 `sysctl` 命令来实现。为了确保设置永久生效，可以在 `/etc/sysctl.conf` 文件中添加 `net.ipv4.ip_forward=1`。

#### 配置 iptables 规则

1. 初始化规则：首先确保主机 B 上的 iptables 规则为空，避免已有规则干扰实验。

2. 设置默认拒绝规则：在 FORWARD 链中添加一条默认拒绝所有数据包的规则，确保安全。

    ```bash
    iptables -A FORWARD -j REJECT
    ```

3. 放行特定服务的请求：例如，允许内部网络主机访问外部网络的 Web 服务（端口 80）和 SSH 服务（端口 22）。

    ```bash
    iptables -I FORWARD -s 10.1.0.0/16 -p tcp --dport 80 -j ACCEPT
    iptables -I FORWARD -s 10.1.0.0/16 -p tcp --dport 22 -j ACCEPT
    ```

4. 放行响应数据包：为了确保服务的可用性，还需要放行外部网络对内部网络请求的响应数据包。

    ```bash
    iptables -I FORWARD -d 10.1.0.0/16 -p tcp --sport 80 -j ACCEPT
    iptables -I FORWARD -d 10.1.0.0/16 -p tcp --sport 22 -j ACCEPT
    ```

5. 优化规则：使用 state 扩展模块，可以简洁地处理响应数据包。

    ```bash
    iptables -I FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
    ```

#### 测试与验证

- 从内部网络访问外部网络：确保内部网络主机 C 能够成功访问外部主机 A 的 Web 服务和 SSH 服务。
- 从外部网络访问内部网络：根据实际需求决定是否开放外部网络访问内部网络服务的权限，并相应地调整 iptables 规则。

### 7.12 动作总结（1）

iptables 不仅提供强大的数据包过滤功能，还允许我们对匹配到的数据包执行各种动作。这些动作可以分为基础动作和扩展动作。

#### 基础动作

- ACCEPT - 允许数据包通过。
- DROP - 丢弃数据包，不发送任何相应信息给发送方。

#### 扩展动作

- REJECT - 拒绝数据包，并向发送方发送一个拒绝信息。REJECT 是一个扩展动作，它允许你指定拒绝类型，例如：

    - `--reject-with icmp-net-unreachable` - 网络不可达
    - `--reject-with icmp-host-unreachable` - 主机不可达
    - `--reject-with icmp-port-unreachable` - 端口不可达
    - `--reject-with icmp-proto-unreachable` - 协议不可达
    - `--reject-with icmp-net-prohibited` - 网络禁止访问
    - `--reject-with icmp-host-prohibited` - 主机禁止访问
    - `--reject-with icmp-admin-prohibited` - 管理员禁止访问

    如果没有明确设置 `--reject-with` 的值，默认使用的是 `icmp-port-unreachable`。

#### 实践示例

假设我们要阻止所有来自特定 IP 地址的数据包并告知对方主机不可达，我们可以使用如下规则：

```bash
iptables -A INPUT -s 192.168.1.100 -j REJECT --reject-with icmp-host-unreachable
```

这条命令会添加一条规则到 INPUT 链，对于源 IP 为 192.168.1.100 的所有数据包，将它们拒绝并向发送者返回 ICMP 主机不可达的消息。

#### LOG 动作

- LOG - 记录符合条件的数据包的相关信息到日志文件中。LOG 动作本身并不改变数据包的状态，它只是记录下数据包的信息。之后你可以根据需要定义额外的规则来处理这些数据包。

#### LOG 动作选项

- `--log-level <level>` - 设置日志级别，如 warning、info 等。
- `--log-prefix "<prefix>"` - 给日志条目添加前缀，方便识别。

#### 实践示例

要记录所有尝试连接到 SSH 端口（22）的数据包，可以使用如下规则：

```bash
iptables -A INPUT -p tcp -dport 22 -j LOG --log-prefix "SSH-Attempt: "
```

此规则会将所有目的地为 SSH 端口 22 的数据包的信息记录下来，并在日志条目前加上 "SSH-Attempt" 作为标识。

为了确保日志信息不会与系统其他日志混淆，可以通过修改 rsyslog 配置文件来定向日志输出到特定文件：

```bash
# /etc/rsyslog.conf
kern.warning /var/log/iptables.log
```

重启 rsyslog 服务后，相关的 iptables 日志会被记录到 `/var/log/iptables.log` 中。

### 7.13 动作总结（2）

我们继续深入探讨 iptables 中的几个关键动作：SNAT、DNAT、MASQUEARDE 和 REDIRECT。这些动作对于实现网络地址转换（NAT）至关重要，允许我们对数据包的源地址或目标地址进行修改，从而实现流量的控制与转发。

#### 网络地址转换（NAT）

NAT（Network Address Translation）是一种将一个 IP 地址空间映射到另一个 IP 地址空间的技术。它通常用于隐藏内部网络结构，并允许多台设备共享一个公共 IP 地址访问互联网。NAT 有两种主要类型：源地址转换（SNAT）和目标地址转换（DNAT）。

- SNAT（Source NAT）：当内部网络的主机向外部发送数据时，其源 IP 地址会被替换为防火墙或路由器的公网 IP 地址。
- DNAT（Destination NAT）：当外部网络的数据发往内部网络时，其目标 IP 地址会被替换为内部网络中的某台主机的实际私有 IP 地址。

#### SNAT 示例

假设公司局域网使用的是 10.1.0.0/16 网段，但只有一个公网 IP（例如 192.168.1.146）。为了使局域网内的所有主机都能访问互联网，我们需要配置 SNAT 规则：

```bash
iptables -t nat -A POSTROUTING -s 10.1.0.0/16 -j SNAT --to-source 192.168.1.146
```

这条命令的作用是，当来自 10.1.0.0/16 网段的数据包经过 POSTROUTING 链时，它们的源 IP 地址将被改为 192.168.1.146，这样外部网络就只能看到这个公网 IP，而看不到内网主机的真实 IP。

#### MASQUERADE

如果公司的公网 IP 不是固定的而是通过动态分配获得的（如拨号上网），那么每次 IP 变更后都需要手动更新 SNAT 规则，这显然不够方便。MASQUERADE 解决了这个问题，它会自动地将数据包的源 IP 设置为当前有效的公网 IP 地址：

```bash
iptables -t nat -A POSTROUTING -s 10.1.0.0/16 -o eth0 -j MASQUERADE
```

这里，`-o eth0` 指定了出口接口，确保只有通过 eth0 接口出去的数据包才会被处理。

#### DNAT 示例

假如公司想让外部用户能够访问位于局域网内的 web 服务器（IP：10.1.0.5，port：80），可以通过以下 DNAT 规则来实现：

```bash
iptables -t nat -I PREROUTING -d 192.168.1.146 -p tcp --dport 80 -j DNAT --to-destination 10.1.0.5:80
```

此规则表示，凡是目标地址为 192.168.1.146 且端口为 80 的数据包，都将被重定向至 10.1.0.5 的 80 端口。

#### REDIRECT

REDIRECT 是一个特殊的 DNAT 形式，用于将数据包的目标端口重定向到本地机器上的不同端口。比如，将到达本机 80 端口的请求重定向到 8080 端口。

```bash
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 8080
```

### 7.14 小结之常用套路

在之前的笔记中，我们已经探讨了 IPTABLES 的许多方面。现在是时候回顾一下，并总结一下常用的配置策略和技巧了。这些被称为“常用套路”。掌握这些套路能够帮助我们更高效地使用 IPTABLES。

#### 规则顺序的重要性

规则顺序的排列顺序非常关键。一旦报文被某条规则匹配并执行了相应的动作（如 ACCEPT 或 REJECT），后续的规则将不再对该报文产生影响（除非前面的动作是 LOG）。因此，对于相同的服务而言，应先把更严格的规则放在前面。例如，如果有一条规则允许所有来自特定 IP 的流量，而另一条规则拒绝所有其他流量，那么必须确保允许规则先于拒绝规则，以避免错误拦截合法流量。

举例：

```bash
# 允许特定 IP 访问 SSH 服务
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.100 -j ACCEPT
# 拒绝所有其他到 SSH 端口的连接
iptables -A INPUT -p tcp --dport 22 -j DROP
```

#### 多条件匹配遵循“与”逻辑

当一条规则包含多个匹配条件时，默认情况下，这些条件之间存在逻辑上的“与”关系。这意味着报文只有同时满足该规则中的所有条件才会被匹配。

例子：

```bash
# 仅允许来自 192.168.1.0/24 网段且网络端口为 80 的 TCP 数据包
iptables -A INPUT -p tcp =s 192.168.1.0/24 --dport 80 -j ACCEPT
```

#### 高频匹配规则优先

在没有特殊顺序要求的情况下，应该把那些更容易被出发的规则排在前面。比如，如果 Web 服务比 SSH 服务接受更多的请求，则应将针对 Web 服务的规则置于 SSH 服务的规则之前，以减少不必要的处理开销。

例子：

```bash
# 首先处理改频的 Web 流量
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
# 然后处理较低频的 SSH 流量
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

#### 考虑双向流量

当 iptables 用作网络防火墙时，不仅要考虑从外部到内部的流量控制，还要考虑内部到外部的数据流。这有助于全面保护网络安全。

例子：

```bash
# 允许内网主机访问外网
iptables -A OUTPUT -o eth0 -j ACCEPT
# 限制外网对内网某些服务的访问
iptables -A INPUT -i eth0 -p tcp --dport 22 -m state --state NEW -j DROP
```

#### 白名单机制的实现

创建白名单时，通常会设置链的默认策略为 ACCEPT，然后通过添加具体的 REJECT 规则来定义例外情况。这样即使链中的规则被意外清空，也不会导致管理员自己也被封锁在外。

例子：

```bash
# 设置 INPUT 链默认策略为接受
iptables -P INPUT ACCEPT
# 添加具体拒绝策略
iptables -A INPUT -p tcp --dport 22 -j REJECT
```











































































