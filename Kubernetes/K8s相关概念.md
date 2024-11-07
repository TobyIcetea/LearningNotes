# K8s 相关概念

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





























