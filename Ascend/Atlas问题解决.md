# Atlas 问题解决

## 1. 安装 Ascend-Docker-Runtime

根据我的 Atlas 200 DK A2 开发板，我首先应该通过这个命令来下载 Ascend-Docker-Runtime：

```bash
wget https://gitee.com/ascend/mind-cluster/releases/tag/v6.0.0
```

首次执行安装命令：

```bash
./Ascend-docker-runtime_6.0.0_linux-aarch64.run --install --install-scene=containerd --install-type=A200IA2
```

但是失败了，报错的日志是：

```bash 
Uncompressing ascend-docker-runtime  100%  
[INFO] installing ascend docker runtime
[INFO] platform(aarch64) matched!
[ERROR] /etc/os-release is soft link
[ERROR] /etc/os-release is invalid
[ERROR] install failed, a200ia2 not support this os
```

里面提到 `/etc/os-release` 是一个链接文件。在其他操作系统中，这个文件一般都是一个具体的文件，但是 OpenEuler 中将它作为一个链接文件，指向的是同文件夹中另一个文件：

```bash
-sh-5.1# ls -l os-release
lrwxrwxrwx 1 root root 14 Aug 11  2023 os-release -> initrd-release
```

于是我想到，可以将 `os-release` 链接文件删除掉，重新建立一个新的文件：

```bash
rm os-release
cp initrd-release os-release
```

之后再执行：

（containerd 容器运行时）

```bash
./Ascend-docker-runtime_6.0.0_linux-aarch64.run --install --install-scene=containerd --install-type=A200IA2
```

就可以得到安装成功的日志：

```bash
Uncompressing ascend-docker-runtime  100%  
[INFO] installing ascend docker runtime
[INFO] platform(aarch64) matched!
[info] os is Euler/OpenEuler
[INFO] install executable files success
[INFO] install scene is 'containerd'.
[INFO] /etc/containerd/config.toml modify success
[INFO] Ascend Docker Runtime has been installed in: /usr/local/Ascend/Ascend-Docker-Runtime
[INFO] The version of Ascend Docker Runtime is: 6.0.0
[INFO] please reboot daemon and container engine to take effect
[INFO] Ascend Docker Runtime install success
```

或者如果是 docker 容器运行时：

```bash
./Ascend-docker-runtime_6.0.0_linux-aarch64.run --install --install-type=A200IA2
```

根据经验，我记得其实不同的设备之间的区别就在于默认挂载内容，具体的文件就是：`/etc/ascend-docker-runtime.d/base.list`。如果我们按照 Atlas 200DK A2 进行配置，那么这个文件的内容就是：

```bash
/etc/sys_version.conf
/etc/hdcBasic.cfg
/usr/lib64/libaicpu_processer.so
/usr/lib64/libaicpu_prof.so
/usr/lib64/libaicpu_sharder.so
/usr/lib64/libadump.so
/usr/lib64/libtsd_eventclient.so
/usr/lib64/libaicpu_scheduler.so
/usr/lib64/libdcmi.so
/usr/lib64/libmpi_dvpp_adapter.so
/usr/lib64/aicpu_kernels/
/usr/local/sbin/npu-smi
/usr/lib64/libstackcore.so
/usr/local/Ascend/driver/lib64
/var/slogd
/var/dmp_daemon
/var/queue_schedule
/usr/lib64/libcrypto.so.1.1
/usr/lib64/libyaml-0.so.2
```

这表示容器启动时，会默认将这些文件挂载到容器中去。

如果要卸载 Ascend-Docker-Runtime，使用的命令是：

```bash
./Ascend-docker-runtime_6.0.0_linux-aarch64.run --uninstall
```

### 一个小问题

今天发现在 Docker 容器中，容器无法执行 npu-smi 命令，因为运行库不全。我们在容器中使用 `ldd` 命令查询一下所需的运行时库，发现：

```bash
root@dfcc4c5ff4fd:/# ldd /usr/local/sbin/npu-smi
        linux-vdso.so.1 (0x0000e7ffd8cc0000)
        libc_sec.so => /usr/local/Ascend/driver/lib64/libc_sec.so (0x0000e7ffd8a60000)
        libdevmmap.so => /usr/local/Ascend/driver/lib64/libdevmmap.so (0x0000e7ffd8a40000)
        libdrvdsmi.so => /usr/local/Ascend/driver/lib64/libdrvdsmi.so (0x0000e7ffd89c0000)
        libslog.so => /usr/local/Ascend/driver/lib64/libslog.so (0x0000e7ffd89a0000)
        libmmpa.so => not found
        。。。。。。
```

发现其中的 libmmpa.so 是找不到的。

但是在宿主机，也就是开发板中，我们发现 libmmpa.so 在另外一个文件夹中：

```bash
libmmpa.so => /usr/local/Ascend/ascend-toolkit/latest/lib64/libmmpa.so (0x0000e7fffc682000)
```

带着这个思路，我尝试去在启动的时候挂载上这个文件夹：

（待完成）







## 2. containerd 中运行容器

以 busybox 容器举例，首先要确保镜像列表中有 busybox：

```bash
ctr image list
```

如果没有，可以使用以下命令进行拉取：

```bash
ctr image pull docker.io/library/busybox:latest --hosts-dir="/etc/containerd/certs.d/"
```

### 2.1 不加任何 Ascend 参数

如果不借助任何 Ascend 的参数，直接去运行一个容器，此时：

```bash
ctr run --rm -t docker.io/library/busybox:latest busybox1 sh
```

之后在容器中，我们使用去查看一下有没有包含 Ascend 的一些工具包，也就是上面提到的挂载文件有没有生效。

比如说我们看 `/etc/sys_version.conf`、`/etc/hdcBasic.cfg` 这些文件在不在，最终结论是：**都不在**。

### 2.2 加上 Ascend 的参数

接下来按照官网的教程，我们加上一些 Ascend 特定的参数：

```bash
ctr run --rm --runtime io.containerd.runtime.v1.linux -t --env ASCEND_VISIBLE_DEVICES=0 --env ASCEND_ALLOW_LINK=True docker.io/library/busybox:latest busybox2 sh
```

经过验证，这次的命令可以将上面的文件完全都挂载上。

> 之前在第一个问题没有解决的时候，那时候我尝试了一些可能的替代方案，比如说将 --install-type 设置为 A200 DK 或者是其他。但是这样一个后果就是有的文件挂载不上来，要么是 base.list 中有这个文件，但是我们的操作系统中没有；要么是我们的操作系统中有这个文件，但是 base.list 中没有提到。

### 2.3 Docker 中运行容器

```bash
docker run --rm -it -e ASCEND_VISIBLE_DEVICES=0 -e ASCEND_ALLOW_LINK=True nginx:latest bash
```

## 3. 尝试调动 NPU

为了看我使用开发板去推理一些应用的时候，能不能将 NPU 调度起来，所以我打算开两个 shell 窗口，一个窗口用来看 NPU 的使用情况，另一个窗口用来启动一些 A2 自带的推理应用：

### 第一个窗口

```bash
watch -n 1 npu-smi info
```

这表示每一秒刷新一次 npu 的使用情况。

初始状态：

![image-20250315175833607](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250315175833607.png)

### 第二个窗口

我们打开一些 A2 自带的推理应用，这里执行的命令是：

```bash
cd /home/HwHiAiUser/samples/notebooks

. /usr/local/Ascend/ascend-toolkit/set_env.sh
export PYTHONPATH=/usr/local/Ascend/thirdpart/aarch64/acllite:$PYTHONPATH
if [ $# -eq 1 ];then
    jupyter lab --ip $1 --allow-root --no-browser
else
    jupyter lab --ip 192.168.137.100 --allow-root --no-browser
fi
```

启动 jupyter（也可能不用执行这个）：

```bash
./start_notebook.sh
```

之后在弹出的日志信息中找到类似这样一个网站打开就可以了：

```bash
http://192.168.137.100:8888/lab?token=0e8f6a70ac914a64d8cb59d046f816ea887ac76daef00717
```

在网页中点击 yolo 算法，然后点击运行推理。同时观察 npu 的使用情况：

![image-20250315180529309](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250315180529309.png)

## 4. 监控 NPU 使用情况

NPU 使用情况可以使用 Ascend 的 npu-smi 工具，CPU 使用情况可以使用 

可以将它们综合成一个脚本：

```bash
#!/bin/bash

# 定义输出文件路径
output_file="./record.log"

# 无限循环
while true; do
    # 获取当前时间
    current_time=$(date +"%Y-%m-%d %H:%M:%S")

    # 执行 npu-smi info 命令并将结果和时间写入文件
    echo "[$current_time] NPU Status:" >> $output_file
    npu-smi info >> $output_file
    mpstat | awk '/all/ {printf "CPU Usage: %.2f%%\n", 100 - $NF}' >> $output_file
    echo "--------------------------------------------------------------" >> $output_file

    # 等待一秒
    sleep 0.5
done
```

将脚本保存为 watch.sh，之后可以执行命令：

```bash
./watch.sh &
```

同时查看日志：

```bash
tail -f ./record.log
```

这样就可以看到当前 CPU 和 NPU 的使用情况。

## 4. 在本地通过一个 python 文件运行 yolo

首先拷贝一份 `/home/HwHiAiUser/samples/notebooks/01-yolov5/` 这个目录到工作目录下，之后把其中的 `main.ipynb` 文件转换为 `.py` 文件：

```bash
jupyter nbconvert --to script main.ipynb
```

尝试将 yolo 目录挂载到容器中：

```bash
ctr run --rm --runtime io.containerd.runtime.v1.linux -t --env ASCEND_VISIBLE_DEVICES=0 --env ASCEND_ALLOW_LINK=True docker.io/library/busybox:latest busybox2 sh 
--mount type=bind,src=/tmp,dst=/hostdir,options=rbind:rw
```

给开发板安装 Docker：

```bash
dnf install docker-ce
systemctl enable --now docker
```

使用 Docker 运行镜像：

```bash
docker run --rm -it -e ASCEND_VISIBLE_DEVICES=0 -e ASCEND_ALLOW_LINK=True image:v1 bash
```





如果我想要运行这个模型，那么我就需要：

- `coco_names.txt`
- `det_utils.py`
- `main.py`
- `racing.mp4`
- `yolo.om`



















