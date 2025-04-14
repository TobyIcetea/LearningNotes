# Kubernetes 相关概念（2）

## 8. CRD 机制

Kubernetes 中的 CRD（Custom Resource Definition，自定义资源定义）机制是 Kubernetes 允许用户扩展其 API 的一种方式，使得用户能够创建和管理自定义资源（Custom Resources）。CRD 提供了一种方法，让用户能够在 Kubernetes 中添加自己的对象类型，这些对象和 Kubernetes 内建的资源（如 Pod、Service、Deployment 等）一样，也可以被管理、查询和操作。

### 8.1 CRD 机制的基本概念

在 Kubernetes 中，资源通常是指与集群管理相关的对象，如 Pods、Deployments、Services 等。而 CRD 允许用户定义一种新的资源类型，使其与 Kubernetes 的原生资源一样，能够通过 kubectl 或 Kubernetes API 进行管理。通过 CRD，用户可以为应用程序创建专门的对象类型，并通过这些对象来管理特定的业务逻辑。

### 8.2 CRD 的组成

CRD 由以下几个关键部分构成：

1. apiVersion：指定 CRD 的 API 版本，通常为 `apiextensions.k8s.io/v1`。
2. kind：类型，固定为 `CustomResourceDefinition`。
3. metadata：资源的元数据，包含名称、命名空间等信息。
4. spec：自定义资源的定义，包含资源的相关属性，如：
    - group：API 组的名称，通常是与自定义资源相关的域名。
    - names：资源名称的定义，包含资源的 `kind`、`plural`、`singular` 等字段。
    - versions：定义 CRD 版本的信息，通常至少包括 `name`（版本名称）和 `served`（是否启用该版本）等。
    - scope：定义资源的范围，可以是 `Namespaced` 或 `Cluster`。`Namespaced` 表示资源存在于特定的命名空间中，`Cluster` 表示该资源是集群范围内的。
    - validation：用于验证资源字段是否合法，可以通过定义 OpenAPI 规范来进行。
5. status：CRD 创建之后的状态信息，通常由 Kubernetes 直接管理，包含 CRD 的状态，如创建是否成功等。

### 8.3 创建和使用 CRD

1. 创建 CRD：首先需要定义一个 CRD YAML 文件，其中指定了自定义资源的定于。下面是一个简单的 CRD 定义示例：

    ```yaml
    apiVersion: apiextensions.k8s.io/v1
    kind: CustomResourceDefinition
    metadata:
      name: myresources.example.com
    spec:
      group: example.com
      names:
        plural: myresources
        singular: myresource
        kind: MyResource
        shortNames:
          - mr
      scope: Namespaced
      versions:
        - name: v1
          served: true
          storage: true
          schema:
            openAPIV3Schema:
              type: object
              properties:
                spec:
                  type: object
                  properties:
                    replicas:
                      type: integer
                      example: 1
    ```

2. 应用 CRD：通过 `kubectl apply -f <crd-file>.yaml` 命令应用 CRD 定义，Kubernetes 会在 API Server 中注册该 CRD。

3. 创建自定义资源：一旦 CRD 创建并被注册，用户就可以基于该 CRD 创建和管理自定义资源，比如，假设我们已经定义了 `MyResource` 类型，那么可以创建一个自定义资源：

    ```yaml
    apiVersion: example.com/v1
    kind: MyResource
    metadata:
      name: myresource-sample
    spec:
      replicas: 3
    ```

4. 管理自定义资源：创建后可以像管理普通 Kubernetes 资源一样使用 `kubectl` 来查看、编辑和删除自定义资源，例如：

    - `kubectl get myresources`：列出所有 MyResource 资源。
    - `kubectl describe myresource myresource-sample`：查看某个 MyResource 的详细信息。

### 8.4 CRD 的使用场景

CRD 在很多场景中都能发挥重要作用，常见的使用场景包括：

1. 扩展 Kubernetes API：对于特定的业务需求，用户可能需要创建新的资源类型来描述其业务模型。通过 CRD，用户可以在 Kubernetes 中管理这些资源。
2. Operator：Kubernetes Operator 是一种常见的模式，允许用户使用 CRD 来管理自定义应用程序的生命周期。Operator 使用自定义资源来表示应用程序的状态，并根据状态执行相应的操作（如自动部署、扩容等）。
3. Kubernetes 集群的自动化管理：通过 CRD，用户可以为集群中的某些操作（如定时任务、监控配置等）定义新的资源类型，使集群管理更加灵活和可扩展。

### 8.5 CRD 的优缺点

优点：

- 灵活性高：CRD 可以根据业务需求自定义资源类型，使 Kubernetes 成为一个强大的平台来管理各种应用场景。
- 与 Kubernetes 原生资源集成：自定义资源能够像 Kubernetes 原生资源一样进行管理，享受 Kubernetes 的 API、调度、存储等功能。
- 支持自定义控制器：配合 Kubernetes Operator，可以根据 CRD 定义的资源类型编写自定义控制器，从而实现应用的自动化管理。

缺点：

- 性能开销：CRD 会引入一定的管理开销，尤其是在资源定义复杂或资源数量较多时，可能会影响 API Server 的性能。
- 版本管理复杂：CRD 支持版本控制，但随着资源定义的演进，版本管理可能变得较为复杂，尤其是需要向后兼容时。
- 需要额外的开发和运维工作：使用 CRD 需要编写额外的控制器或 Operator 来处理业务逻辑，这对于团队的开发和运维能力提出了更高的要求。

### 8.6 DeviceModel 与 Device

DeviceModel 与 Device 在 KubeEdge 的设备管理中扮演了非常重要的角色。它们的作用是抽象设备模型（DeviceModel）以及设备实例（DeviceInstance）的定义和属性，进而管理和控制设备。

#### DeviceModel CRD

`DeviceModel` 是对设备的模型定义。它描述了设备的一些通用属性（例如设备的传感器数据、读写权限、数据类型、单位等），以及该设备模型支持的协议（如 Modbus、MQTT 等）。

`DeviceModel` 的 YAML 文件：

```yaml
apiVersion: devices.kubeedge.io/v1beta1
kind: DeviceModel
metadata:
  name: beta1-model
spec:
  properties:
    - name: temp
      description: beta1-model
      type: INT
      accessMode: ReadWrite
      maximum: "100"
      minimum: "1"
      unit: "Celsius"
  protocol: modbus
```

各个字段的说明：

- apiVersion：`device.kubeedge.io/v1beta`，指定 `DeviceModel` 资源的 API 版本。
- kind：`DeviceModel`，指定该资源的类型为设备模型。
- metadata：
    - name：`beta1-model`，这是该设备模型的名称。设备模型是对物理设备或虚拟设备的抽象定义，通常在多个设备实例中共用同一个设备模型。
- spec：
    - properties：定义了该设备模型的属性。在此例中，定义了一个属性 `temp`（温度传感器），该属性有以下几个字段：
        - name：`temp`，设备的属性名称，表示该设备有一个名为 `temp` 的属性。
        - description：`beta1-model`，对该属性的描述。
        - type：`INI`，表示温度属性的类型是整数（`INT`）。
        - accessMode：`ReadWrite`，表示该属性是可读可写的，即可以修改设备的温度值。
        - maximum：`"100"`，属性值的最大值是 100。
        - minimum：`"1"`，属性值的最小值为 1。
        - unit：`Celsius`，单位为摄氏度（Celsius）。
    - protocol：`modbus`，该设备模型支持 ModBus 协议。

解释：

- `DeviceModel` 是对设备特征的抽象，例如温度传感器的属性可以包括温度值、单位、读写权限等。而这些设备属性（如 `temp`）通常会在多个实际的设备实例中复用。通过 `DeviceModel`，你可以定义设备的通用模型，无论是一个真实设备还是多个设备实例，它们都可以基于这个模型进行配置和管理。

#### Device CRD

`Device` 是对设备实例的定义，表示某个具体的设备，它根据前面定义的 `DeviceModel` 模型来实例化，并且可以有自己的配置、协议、数据收集周期等参数。

`Device` 的 YAML 文件：

```yaml
apiVersion: devices.kubeedge.io/v1beta1
kind: Device
metadata:
  name: beta1-device
spec:
  deviceModelRef:
    name: beta1-model
  nodeName: worker-node1
  properties:
    - name: temp
      collectCycle: 2000      # 2000 stands for 2000 milliseconds (2 seconds)
      reportCycle: 2000       # 2000 stands for 2000 milliseconds (2 seconds)
      desired:
        value: "30"
      reportToCloud: true
      visitors:
        protocolName: modbus
        configData:
          register: "HoldingRegister"
          offset: 2
          limit: 1
          scale: 1
          isSwap: true
          isRegisterSwap: true
  protocol:
    protocolName: modbus
    configData:
      ip: 172.17.0.3
      port: 1502
```

解释：

- `Device` 资源表示的是某个具体设备实例，它引用了之前定义的 `DeviceModel`，并且可以拥有与该设备模型相关的具体配置、属性（例如 `temp`）以及设备通信协议（如 Modbus 协议）的详细配置。
- 通过 `Device`，KubeEdge 实现了对设备的精细化控制，例如设备的期望状态（`desired`）、数据收集周期（`collectCycle`）、报告周期（`reportCycle`）等。
- 每个设备实例都可以与云端或其他边缘设备进行通信，并且可以根据协议（例如 Modbus）进行配置和控制。

#### 总结

- DeviceModel：定义了设备的通用模型，例如一个温度传感器的属性、数据类型、读写权限等。它是对设备功能的抽象，可以用于多个设备实例。
- Device：定义了某个具体的设备实例，它关联了一个设备模型，并且可以有自己的配置和状态，例如收集周期、报告周期、通信协议等。

通过这种方式，KubeEdge 提供了非常灵活的设备管理功能，并且用户根据设备模型（`DeviceModel`）实例化具体的设备（`Device`），并通过 CRD 对设备进行灵活的配置和管理。

## 9. In-cluster Config

在 Kubernetes 中，`in-cluster config` 是指在 Kubernetes 集群内运行的应用或工具，通过集群内部的配置信息来访问 Kubernetes API 服务器的方式。通常，Kubernetes 集群中的各类组件（如 Pod、Controller、Scheduler 等）需要与 API 服务器进行交互，例如获取资源、创建或删除对象等。为了保证这些操作的安全性和可访问性，Kubernetes 提供了一种“集群内配置”（in-cluster configuration）的机制。

### 9.1 什么是 In-cluster Config？

在集群内布运行的应用程序（例如，Pod）可以通过 Kubernetes 内部的 API 访问 API 服务器。`in-cluster config` 是一种配置方式，用来使得应用程序能够自动地获取集群配置，进行身份验证、授权并连接到 Kubernetes API 服务器，而无需手动配置 kubeconfig 文件。

通常情况下，kubeconfig 文件会存储在用户本地的 `~/.kube/config` 中，包含集群访问的认证信息、API 地址等。而对于在集群内部运行的服务，Kubernetes 提供了一种通过自动获取集群内的环境变量和默认的服务账户来进行认证和配置的方式，避免了额外的配置步骤。

### 9.2 In-cluster Config 工作原理

`in-cluster config` 基本上依赖于 Kubernetes API 服务器提供的默认认证机制。具体来说，以下几个部分共同作用，使得应用程序能够在集群内布顺利访问 Kubernetes API 服务器：

#### Service Account 和 Token

Kubernetes 为集群内的每个 Pod 分配了一个默认的 ServiceAccount，并为该 ServiceAccount 创建了一个访问 API 服务器的 token。Pod 会通过挂载的方式将这个 token 自动包含在其文件系统中，路径为 `/var/run/secrets/kubernetes.io/serviceaccount.token`。该 token 用于与 API 服务器进行身份验证。

#### 集群 API 地址

Kubernetes 集群会将 API 服务器的地址自动设置为环境变量（例如 `KUBERNETES_SERVICE_HOST` 和 `KUBERNETES_SERVICE_PORT`）。这些环境变量提供了集群内部 API 服务器的地址和端口信息。通常，这个地址是 `https://kubernetes.default.svc`。

#### CA 证书

为了确保与 API 服务器的通信是安全的，Kubernetes 集群内部会自动将 API 服务器的 CA（证书颁发机构）证书作为文件挂载在 `/var/run/secrets/kubernetes.io/serviceaccount/ca.crt` 路径下，应用程序可以用这个证书来验证 API 服务器的身份。

### 9.3 如何在应用程序中使用 In-cluster Config

当你在集群内运行应用程序并希望通过 Kubernetes 客户端库（如 Go 客户端）访问 Kubernetes API 时，你可以使用 `in-cluster config` 配置。

例如，在 Go 中，你可以通过以下方式来加载 in-cluster 配置。

```go
package main

import (
    "fmt"
    "log"

    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
)

func main() {
    // 创建一个 in-cluster 配置
    config, err := rest.InClusterConfig()
    if err != nil {
        log.Fatalf("Failed to get in-cluster config: %v", err)
    }

    // 使用配置创建一个客户端
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        log.Fatalf("Failed to create client: %v", err)
    }

    // 获取并打印当前的 namespaces
    namespaces, err := clientset.CoreV1().Namespaces().List(context.Background(), metav1.ListOptions{})
    if err != nil {
        log.Fatalf("Failed to list namespaces: %v", err)
    }

    for _, ns := range namespaces.Items {
        fmt.Println(ns.Name)
    }
}
```

在这个例子中，`rest.InClusterConfig()` 会自动加载集群内的配置信息，包括 API 地址、身份认证和 CA 证书等。如果应用运行在集群内，Kubernetes 会自动提供这些信息，应用无需额外配置。

### 9.4 如何验证和调试

如果应用程序在集群内无法访问 API 服务器，或者出现身份验证问题，可以通过以下方式进行调试：

- 查看 Pod 的 Service Account：确保 Pod 使用了正确的 Service Account。
- 检查 Token 是否存在：可以通过 `kubectl exec` 进入 Pod，查看 `/var/run/secrets/kubernetes.io/serviceaccount/token` 文件，验证 token 是否存在且有效。
- 查看环境变量：确保 `KUBERNETES_SERVICE_HOST` 和 `KUBERNETES_SERVICE_PORT` 环境变量设置正确。

### 9.5 与 Kuberconfig 的区别

`in-cluster config` 与传统的 kubeconfig 文件配置方式有所不同：

- kubeconfig：通常在集群外部与 Kubernetes API 进行交互，配置了集群的 API 地址、认证信息（如用户名、密码、证书等）。
- in-cluster config：用于在集群内部的 Pod 中访问 API，自动从集群环境中获取认证信息、API 地址等，避免了手动配置的复杂性。

## 10. Treafik

Treafik 作为一个现代的云原生反向代理和负载均衡器，是服务网络（如 Kubernetes、Docker Swarm）中流量管理的组件之一。

### 10.1 什么是 Treafik

Treafik 是一个开源的边缘路由器（Edge Router），专门为云原生环境设计。它的核心功能是：

1. 动态路由：自动发现服务并根据规则转发流量。
2. 负载均衡：支持多种算法（如轮询、加权轮询）。
3. TLS 证书管理：自动申请和续期 Let's Encrypt 证书。
4. 中间件支持：通过插件机制实现流量修改（如重定向、认证、限速等）。
5. 多平台集成：原生支持 Kubernetes、Docker、Consul、AWS 等。

与 Nginx 等传统反向代理不同，Treafik 的配置是动态的，无需手动重载，适合频繁变化的云环境。

### 10.2 核心概念

#### Providers

Treafik 从不同平台（如 Kubernetes、Docker）动态获取路由配置，这些平台称为 Providers。例如：

- `kubernetesCRD`：通过 Kubernetes 自定义资源（CRD）配置路由。
- `docker`：自动发现 docker 容器并生成路由规则。

#### Router

负责将传入请求匹配到对应的服务。路由规则基于：

- Host（域名）：`example.com`
- Path（路径）：`/api/*`
- Headers、Method 等。

#### Services

定义实际处理请求的后端服务（如 Kubernetes Pod、Docker 容器）。一个 Service 可以包含多个示例，Treafik 会自动负载均衡。

#### Middlewares

在请求达到服务前或响应返回客户端前，对流量进行处理。常见中间件：

- Rate Limiting（限速）
- Authentication（认证，如 BasicAuth、OAuth）
- Path Rewriting（路径重写）
- Circuit Breaker（熔断器）

### 10.3 使用场景与优势

#### 典型场景

1. 在 kubernets 中作为 Ingress Controller。
2. 微服务架构中的 API 网关。
3. 自动管理 HTTPS 证书。
4. 金丝雀发布（通过权重路由实现）。

#### 优势

- 动态配置：无需重启，自动感知服务变化。
- 声明式配置：通过 YAML/CRD 定义规则，易于维护。
- 丰富的生态：支持 Prometheus 监控、Grafana 仪表盘等。

### 10.4 在 Kubernetes 中使用 Treafik

#### 安装 Treafik

通过 Helm 快速部署：

```bash
helm repo add traefik https://helm.traefik.io/traefik
helm install traefik traefik/traefik -n traefik --create-namespace
```

#### 定义路由规则（IngressRoute）

创建 `my-app-route.yaml`：

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: my-app-route
spec:
  entryPoints:
    - web
    - websecure
  routes:
    - match: Host(`myapp.example.com`) && PathPrefix(`/api`)
      kind: Rule
      services:
        - name: my-app-service
          port: 8080
      middlewares:
        - name: rate-limit-middleware
  tls:
    certResolver: letsencrypt
```

#### 配置中间件（限速示例）

创建 `rate-limit-middleware.yaml`：

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: rate-limit-middleware
spec:
  rateLimit:
    average: 100
    burst: 200
```

#### 部署并验证

应用配置后，访问 `https://myapp.example.com/api`，Traefik 会自动处理 TLS 并将流量转发到后端服务。





























