# KubeEdge 操作

## 1. 启用 `kubectl logs` 功能

`kubectl logs` 必须在 metrics

1. 确保可以找到 Kubernetes 的 `ca.crt` 文件和 `ca.key` 文件。这些文件默认在 `/etc/kubernetes/pki/` 目录中。

    ```bash
    [root@master ~]# ls /etc/kubernetes/pki/ | grep ca
    ca.crt
    ca.key
    front-proxy-ca.crt
    front-proxy-ca.key
    ```

2. 设置 `CLOUDCOREIPS` 环境变量。环境变量设置为指定的 cloudcore 的 IP 地址。

    ```bash
    export CLOUDCOREIPS="192.168.100.140"
    
    # 使用以下命令检查是否设置成功
    echo $CLOUDCOREIPS
    ```

3. 在云端节点上为 CloudStream 生成证书，但是，生成的文件不在 `/etc/kubeedge/` 中，我们需要从 Github 的存储库中拷贝一份。

    ```bash
    wget https://raw.githubusercontent.com/kubeedge/kubeedge/refs/heads/master/build/tools/certgen.sh
    chmod +x certgen.sh
    mkdir /etc/kubeedge
    cp certgen.sh /etc/kubeedge/
    
    # 将工作目录更改为 kubeedge 目录
    cd /etc/kubeedge/
    
    # 从 certgen.sh 生成证书
    /etc/kubeedge/certgen.sh stream
    ```

4. 在主机上设置 iptables。（此命令应该在每个 apiserver 部署的节点上执行。）（其实就是 master 节点。）

    在每个运行 apiserver 的主机上运行以下命令：

    ```bash
    [root@master kubeedge]# kubectl get cm tunnelport -nkubeedge -oyaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      annotations:
        tunnelportrecord.kubeedge.io: '{"ipTunnelPort":{"192.168.100.140":10352,"192.168.100.141":10351},"port":{"10351":true,"10352":true}}'
      creationTimestamp: "2024-11-17T12:13:32Z"
      name: tunnelport
      namespace: kubeedge
      resourceVersion: "2827"
      uid: 5c80521d-e1f8-4119-bca1-c1d19672c151
    ```

    接着在 apiserver 运行的所有节点为 multi CloudCore 实例来设置 iptables，这里的 cloudcore ips 和 tunnel 端口都是从上面的 configmap 获得的。

    ```bash
    # iptables -t nat -A OUTPUT -p tcp --dport $YOUR-TUNNEL-PORT -j DNAT --to $YOUR-CLOUDCORE-IP:10003
    iptables -t nat -A OUTPUT -p tcp --dport 10350 -j DNAT --to 192.168.100.140:10003
    iptables -t nat -A OUTPUT -p tcp --dport 10351 -j DNAT --to 192.168.100.140:10003
    ```

    如果您不确定是否设置了 iptables，并且希望清除所有这些表。可以使用以下命令清理 iptables 规则：

    ```bash
    iptables -F && iptables -t nat -F && iptables -t mangle -F && iptables -X
    ```

5. `/etc/kubeedge/config/cloudcore.yaml` 和 `/etc/kubeedge/config/edgecore.yaml` 上 cloudcore 和 edgecore 都要修改。将 cloudStream 和 edgeStream 设置为 `enable: true`。将服务器 IP 更改为 cloudcore IP（与 `$CLOUDCOREIPS` 相同）。

    但是这里对 cloudcore 进行修改的时候，因为我们是二进制部署的，所以我们修改的不是 cloudcore 的 yaml，而是 configmap。

    **云端：**

    ```bash
    # 修改 configmap
    kubectl edit cm -n kubeedge
    
    # 找到 cloudStream.enable，修改为 true
            cloudStream:
              # 修改的是这里
              enable: true
    ```

    **边缘端：**

    ```bash
    # 边缘端的节点上都要执行
    vim /etc/kubeedge/config/edgecore.yaml
    
    # 找到 edgeStream.enable，然后设置为 true
      edgeStream:
        # 修改的是这里
        enable: true
    ```

6. 之后重启 cloudcore 和 edgecore：

    云端：

    ```bash
    # 找到 cloudcore 的 pod 的名字
    kubectl get all -n kubeedge
    
    # 删除掉 cloudcore 的 pod，等待 deployment 重建
    kubectl delete pod cloudcore-599689d85f-k4fqf -n kubeedge
    ```

    边缘端：

    ```bash
    systemctl restart edgecore
    ```

## 2. 在云端支持 Metrics-server

1. 实现该功能点的

















