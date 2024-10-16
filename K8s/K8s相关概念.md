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



























