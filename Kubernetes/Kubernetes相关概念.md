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





































