# Kubernetes 操作

## 1. Metrics server

### 1.1 部署

（1）从官网下载 components.yaml 并修改其中的 参数：

```yaml
containers:
- name: metrics-server
  image: k8s.gcr.io/metrics-server/metrics-server:v0.5.0
  command:
    - /metrics-server
    - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
    - --kubelet-insecure-tls   # 添加此行
```

这样是为了 Metrics Server 可以使用不安全的 TLS 连接与 kubelet 通信。

（2）直接使用下面的代码作为 components.yaml：

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: metrics-server
    rbac.authorization.k8s.io/aggregate-to-admin: "true"
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
    rbac.authorization.k8s.io/aggregate-to-view: "true"
  name: system:aggregated-metrics-reader
rules:
- apiGroups:
  - metrics.k8s.io
  resources:
  - pods
  - nodes
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    k8s-app: metrics-server
  name: system:metrics-server
rules:
- apiGroups:
  - ""
  resources:
  - nodes/metrics
  verbs:
  - get
- apiGroups:
  - ""
  resources:
  - pods
  - nodes
  verbs:
  - get
  - list
  - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server-auth-reader
  namespace: kube-system
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: extension-apiserver-authentication-reader
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server:system:auth-delegator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    k8s-app: metrics-server
  name: system:metrics-server
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:metrics-server
subjects:
- kind: ServiceAccount
  name: metrics-server
  namespace: kube-system
---
apiVersion: v1
kind: Service
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
spec:
  ports:
  - name: https
    port: 443
    protocol: TCP
    targetPort: https
  selector:
    k8s-app: metrics-server
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    k8s-app: metrics-server
  name: metrics-server
  namespace: kube-system
spec:
  selector:
    matchLabels:
      k8s-app: metrics-server
  strategy:
    rollingUpdate:
      maxUnavailable: 0
  template:
    metadata:
      labels:
        k8s-app: metrics-server
    spec:
      # 使 Pod 使用主机网络
      hostNetwork: true
      containers:
      - args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
        - --kubelet-use-node-status-port
        - --metric-resolution=15s
        - --kubelet-insecure-tls 
        image: bitnami/metrics-server:latest
        imagePullPolicy: IfNotPresent
        livenessProbe:
          failureThreshold: 3
          httpGet:
            path: /livez
            port: https
            scheme: HTTPS
          periodSeconds: 10
        name: metrics-server
        ports:
        - containerPort: 4443
          name: https
          protocol: TCP
        readinessProbe:
          failureThreshold: 3
          httpGet:
            path: /readyz
            port: https
            scheme: HTTPS
          initialDelaySeconds: 20
          periodSeconds: 10
        resources:
          requests:
            cpu: 100m
            memory: 200Mi
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
        volumeMounts:
        - mountPath: /tmp
          name: tmp-dir
      nodeSelector:
        kubernetes.io/os: linux
      affinity:
      	nodeAffinity:
      	  requiredDuringSchedulingIgnoredDuringExecution:
      	    nodeSelectorTerms:
      	    - matchExpressions:
      	        # 不要调度到 edge 节点
      	      - key: node-role.kubernetes.io/edge
      	        operator: DoesNotExist
      	        # 指定，必须调度到主节点
      	      - key: node-role.kubernetes.io/control-plane
      	      	operator: Exists
      # 添加主节点的容忍
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
          effect: NoSchedule
      priorityClassName: system-cluster-critical
      serviceAccountName: metrics-server
      volumes:
      - emptyDir: {}
        name: tmp-dir
---
apiVersion: apiregistration.k8s.io/v1
kind: APIService
metadata:
  labels:
    k8s-app: metrics-server
  name: v1beta1.metrics.k8s.io
spec:
  group: metrics.k8s.io
  groupPriorityMinimum: 100
  insecureSkipTLSVerify: true
  service:
    name: metrics-server
    namespace: kube-system
  version: v1beta1
  versionPriority: 100
```

然后直接 `kubectl apply -f components.yaml` 就可以啦。

### 1.2 使用

- 获取节点的 CPU 使用情况：

    ```bash
    kubectl top node
    ```

- 获取命名空间中的 pod 的 CPU 和内存使用情况：

    ```bash
    kubectl top pod -n <namespace>
    ```

- 获取命名空间中的 deployment 的 CPU 和内存使用情况：

    ```bash
    kubectl top deploy -n <namespace>
    ```

### 1.3 总结

在 Kubernetes 集群中部署 Metrics Server 可以实现对集群中各种资源的实时监控和度量指标收集，从而帮助管理员和开发人员更好地管理和优化 Kubernetes 应用程序的性能。

## 2. 消除 master 节点的污点

使用命令

```bash
kubectl describe node master
```

可以看到 master 节点是带有污点的：

```bash
Taints:             node-role.kubernetes.io/control-plane:NoSchedule
```

可以使用如下命令消除这个污点：

```bash
kubectl taint nodes master node-role.kubernetes.io/control-plane:NoSchedule-
```

## 3. Pod 控制器重启

在 Kubernetes 中，控制器用于管理一组 Pod 的生命周期。为了保持高可用性，Kubernetes 提供了几种方法来重启这些控制器管理的 Pod，其中 `kubectl rollout restart` 是最常用的方式。

1. Deployment

    命令：

    ```bash
    kubectl rollout restart deployment <deployment-name> -n <namespace>
    ```

    用途：重启 Deployment 管理的 Pod，按滚动更新的方式逐个重启，避免服务中断。

2. DaemonSet

    命令：

    ```bash
    kubectl rollout restart daemonset <daemonset-name> -n <namespace>
    ```

    用途：重启 Daemonset 管理的 Pod，通常在每个节点上都会有一个 Pod。

3. ReplicaSet

    命令：

    ```bash
    kubectl rollout restart replicaset <replicaset-name> -n <namespace>
    ```

    用途：虽然通常通过 Deployment 进行管理，但也可以直接对 ReplicaSet 进行重启。

## 4. Kubernetes 命令补全

直接执行下面的命令：

```bash
dnf install -y bash-completion
source /usr/share/bash-completion/bash_completion
source <(kubectl completion bash)
kubectl completion bash > ~/.kube/completion.bash.inc

vim ~/.bash_profile
----------------------------------------------------------------
# 加入如下内容
source '/root/.kube/completion.bash.inc'
----------------------------------------------------------------

source $HOME/.bash_profile
```



























