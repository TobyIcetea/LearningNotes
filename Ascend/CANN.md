# CANN

初始安装的 OpenEuler 操作系统，在 `/usr/local/Ascend` 目录下有如下几个文件夹：

```bash
-sh-5.1# ll /usr/local/Ascend/
total 16
drwxr-xr-x 4 root       root       4096 Oct 20  2023 ascend-toolkit
drwxr-xr-x 3 root       root       4096 Jan  1  1970 driver
dr-xr-x--- 2 HwHiAiUser HwHiAiUser 4096 Jan  1  1970 include
drwxr-xr-x 3 root       root       4096 Aug 11  2023 thirdpart
```

也就是说 Atlas 200DK A2 内置的 Ascend 资源有：ascend-toolkit、driver。

## 1. 安装部署

安装部署文档位置：

- [Ascend 社区第一文档](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/81RC1alpha001/softwareinst/instg/instg_0002.html?Mode=PmIns&OS=openEuler&Software=cannToolKit)

- [后面实际指向边缘部分的文档](https://support.huawei.com/enterprise/zh/doc/EDOC1100423566/4a72915b?idPath=23710424|251366513|254884019|261408772|258915651)

### 部署架构

文档中提到的部署架构：

![img](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/zh-cn_image_0000002131825536.png)

从这里看到，我们就是要给物理机安装：

1. 昇腾 NPU 驱动： 固件包含昇腾AI处理器自带的OS 、电源器件和功耗管理器件控制软件，分别用于后续加载到AI处理器的模型计算、芯片启动控制和功耗控制。
2. 昇腾 NPU 固件： 部署在昇腾服务器，管理查询昇腾AI处理器，同时为上层CANN软件提供芯片控制、资源分配等接口。
3. CANN 软件：部署在昇腾服务器，包含Runtime、算子库、图引擎、媒体数据处理等组件，通过AscendCL（Ascend Computing Language，昇腾计算语言）对外提供Device管理、Context管理、Stream管理、内存管理、模型加载与执行、算子加载与执行、媒体数据处理等API，帮助开发者实现在昇腾软硬件平台上开发和运行AI业务。

容器方面，我们首先自己部署好 docker，之后要在容器中部署好：

1. 昇腾 NPU 驱动
2. 昇腾 NPU 固件
3. Ascend Docker

### 安装场景

安装场景中提到：

在Atlas 200I A2 加速模块部署的CANN软件为NNRT，用于运行推理应用，且NNRT软件包较小，不需要占用太多存储空间。

> 这里讨论一下这个 NNRT 是什么东西。我们知道 CANN 是 Ascend 生态中对标 NV 生态中 CUDA 的东西，就是一种底层的计算单元，但是这个 NNRT 是什么东西？
>
> - NNRT 属于 CANN 软件栈中的推理引擎模块，类似于 NV 生态中的 TensorRT。专注于将训练好的 AI 模型（如 Pytorch、TensorFlow 导出的模型）进行极致优化，通过一些技术，提高模型在昇腾芯片上的性能。
> - CANN 负责底层硬件调用（如昇腾 910 芯片的算力分配），NNRT 负责在 CANN 基础上对推理模型做针对性加速优化。
>
> 也就是说，这其实是在 CANN 和模型之间又加了一层软件栈：
>
> ```bash
> 【AI 模型】（如 ResNet 等）
> 		|
> 【NNRT】(推理引擎，模型优化)
> 		|
> 【CANN】（硬件抽象 + 计算优化）
> 		|
> 【NPU 驱动】（硬件资源调度）
> 		|
> 【昇腾芯片硬件】(如 310B)
> ```

文档的《安装说明》中提到：NPU驱动固件在Atlas 200I A2 加速模块制作文件系统时已合入，不需要用户手工安装。

因此可能第一步 NPU 驱动固件我们就不需要安装了，但是最好还是检查一下。

### 安装场景硬件配套和 OS 范围

| 硬件款型               | 安装场景   | OS范围                                                       |
| ---------------------- | ---------- | ------------------------------------------------------------ |
| Atlas 200I A2 加速模块 | 物理机场景 | Ubuntu 22.04<br />openEuler 22.03 LTS                        |
|                        | 容器场景   | 宿主机OS：Ubuntu 22.04、openEuler 22.03 LTS<br />容器内OS：Ubuntu 22.04 |

物理机场景中，我们使用的是 openEuler 22.03，这是包含在其中的。但是容器内的 OS，只提到了 Ubuntu 22.04，这点存疑，为什么要专门提一嘴这个，莫非是只能装这一种镜像？

### 下载资源

之后在[昇腾社区开发者资源下载中心](https://www.hiascend.com/developer/download/community)下载了安装包：Ascend-cann-nnrt_7.0.0_linux-aarch64.run

> 目前文档中写的文件是：Ascend-cann-nnrt_8.0.RC3_linux-aarch64.run。但是我点进去却发现自己不能下载这个文件，可能是账号没有开发者权限？然后就下载了 7 版本的。

### 物理机部署

先将上面的 .run 文件放到工作目录下，然后：

1. 增加 .run 文件可执行权限：

    ```bash
    chmod +x Ascend-cann-nnrt_7.0.0_linux-aarch64.run
    ```

2. 验证文件一致性和完整性：

    ```bash
    ./Ascend-cann-nnrt_7.0.0_linux-aarch64.run --check
    ```

3. 安装软件：

    ```bash
    ./Ascend-cann-nnrt_7.0.0_linux-aarch64.run --install --install-for-all --quiet
    ```

    显示 `install success` 之类的日志，就表示部署成功了。

4. 通过修改 `~/.bashrc` 永久设置环境变量：

    ```bash
    cat << EOF >> ~/.bashrc
    source /usr/local/Ascend/nnrt/set_env.sh
    EOF
    
    # 立即生效一次
    source ~/.bashrc
    ```

安装完之后：

```bash
-sh-5.1# ll /usr/local/Ascend/
total 24
drwxr-x--- 4 root       root       4096 Mar 23 10:03 Ascend-Docker-Runtime
drwxr-xr-x 4 root       root       4096 Oct 20  2023 ascend-toolkit
drwxr-xr-x 3 root       root       4096 Jan  1  1970 driver
dr-xr-x--- 2 HwHiAiUser HwHiAiUser 4096 Jan  1  1970 include
drwxr-xr-x 4 root       root       4096 Mar 23 10:10 nnrt
drwxr-xr-x 3 root       root       4096 Aug 12  2023 thirdpart
```

相比于初始安装操作系统，多了 nnrt。

### 容器部署（Docker）（CentOS）

1. 执行以下命令安装Docker。

    ```bash
    dnf install docker
    ```

2. 执行如下命令启动Docker。

    ```bash
    systemctl enable --now docker
    ```

3. 执行如下命令查看Docker是否已安装并启动。

    ```bash
    docker ps
    ```

    回显以下信息表示Docker已安装并启动。

    ```bash
    CONTAINER ID        IMAGE        COMMAND         CREATED        STATUS         PORTS           NAMES
    ```

### 容器部署（Docker）（Ubuntu）

```bash
apt-get update
    
curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/ \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update

apt-get install docker-ce docker-ce-cli containerd.io

systemctl enable --now docker
```

### 制作容器镜像

比如我们以 Ubuntu:22.04 为基础镜像：

```bash
docker pull ubuntu:22.04
```

创建一个用于创建 Dockerfile 的工作路径，进入该工作路径。然后将 `/etc/slog.conf` 复制过来：

```bash
cp /etc/slog.conf slog.conf
```

> `/etc/slog.conf` 是华为 Ascend 开发板相关组件中用于配置系统日志（System Log）行为的核心配置文件。它的作用是定义不同模块的日志输出级别、日志文件数量限制等参数，直接影响 Ascend 硬件驱动、底层库（如 CANN 框架）、以及上层应用在运行时的日志记录行为。

将上面下载的软件（Ascend-cann-nnrt_7.0.0_linux-aarch64.run）和自己准备的推理软件业务压缩包上传到当前的工作目录中：

```bash
cp (Ascend-cann-nnrt_7.0.0_linux-aarch64.run 存放位置) ./

### 打包业务程序
tar zcvf yolo.tgz coco_names.txt det_utils.py main.py racing.mp4 yolo.om

cp 。。。。业务推理包*****.dist ./
vim install.sh  # 如何去部署推理软件的 shell 脚本
vim run.sh  # 如何去运行推理软件的 shell 脚本
```

之后就可以构建 Dockerfile：

```dockerfile
FROM python:3.9.21

USER root

RUN apt-get update && apt-get install -y libgl1
RUN pip3 install opencv-python numpy==1.22.4 scikit-video ffmpeg-python torch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0

COPY torch_npu-1.11.0.post8-cp39-cp39-linux_aarch64.whl .
RUN pip3 install torch_npu-1.11.0.post8-cp39-cp39-linux_aarch64.whl

COPY aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl .
COPY ais_bench-0.0.2-py3-none-any.whl .
RUN pip3 install aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl
RUN pip3 install ais_bench-0.0.2-py3-none-any.whl

# 这表示在进行 build 操作时，可以通过 --build-arg 来指定构建参数
ARG NNRT_PKG
ARG DIST_PKG
# 本文以/usr/local/Ascend目录为例作为NNRT安装目录，如果您希望安装在其他目录，请修改为您希望的目录
ARG ASCEND_BASE=/usr/local/Ascend
WORKDIR /home/AscendWork
COPY $NNRT_PKG .
COPY $DIST_PKG .
COPY install.sh .

# 创建运行推理应用的用户及组，HwHiAiUser，HwDmUser，HwBaseUser的UID与GID分别为1000，1101，1102为例
# 在 Docker 镜像中创建三个用户（HwHiAiUser、HwDmUser、HwBaseUser）和对应的用户组
# 同时，将 HwHiAiUser 用户添加到 HwDmUser 和 HwBaseUser 用户组中，使其拥有这些组的权限
RUN umask 0022 && \
    groupadd  HwHiAiUser -g 1000 && \
    useradd -d /home/HwHiAiUser -u 1000 -g 1000 -m -s /bin/bash HwHiAiUser && \
    groupadd HwDmUser -g 1101 && \
    useradd -d /home/HwDmUser -u 1101 -g 1101 -m -s /bin/bash HwDmUser && \
    usermod -aG HwDmUser HwHiAiUser && \
    groupadd HwBaseUser -g 1102 && \
    useradd -d /home/HwBaseUser -u 1102 -g 1102 -m -s /bin/bash HwBaseUser && \
    usermod -aG HwBaseUser HwHiAiUser

# 安装nnrt,解压推理程序
# 将几个命令分开执行，方便构建
RUN chmod +x $NNRT_PKG && \
    ./$NNRT_PKG --quiet --install --install-path=$ASCEND_BASE \
    --install-for-all --force
RUN sh install.sh
RUN chown -R HwHiAiUser:HwHiAiUser /home/AscendWork/ && \
    rm $NNRT_PKG && \
    rm $DIST_PKG && \
    rm install.sh

ENV LD_LIBRARY_PATH=/usr/local/Ascend/nnrt/latest/lib64:/usr/local/Ascend/driver/lib64:/usr/lib64
ENV LD_PRELOAD=/lib/aarch64-linux-gnu/libc.so.6

RUN ln -sf /lib /lib64 && \
    mkdir /var/dmp && \
    mkdir /usr/slog && \
    chown HwHiAiUser:HwHiAiUser /usr/slog && \
    chown HwHiAiUser:HwHiAiUser /var/dmp

# 拷贝日志配置文件
COPY --chown=HwHiAiUser:HwHiAiUser slog.conf /etc

COPY --chown=HwHiAiUser:HwHiAiUser run.sh /home/AscendWork/run.sh
RUN chmod 640 /etc/slog.conf && \
    chmod +x /home/AscendWork/run.sh

# 若用户不需要使用AICPU算子，则请用户将如下指令添加注释“#”
# RUN cp /usr/local/Ascend/nnrt/latest/opp/Ascend/aicpu/Ascend-aicpu_syskernels.tar.gz /home/HwHiAiUser/ && \
    # rm -rf /usr/local/Ascend/nnrt/latest/opp/Ascend/aicpu/Ascend-aicpu_syskernels.tar.gz && \
    # echo $(wc -c /home/HwHiAiUser/Ascend-aicpu_syskernels.tar.gz|awk ' {print$1} ') > /home/HwHiAiUser/aicpu_package_install.info && \
    # tail -c +8449 /home/HwHiAiUser/Ascend-aicpu_syskernels.tar.gz > /home/HwHiAiUser/aicpu.tar.gz && \
    # rm -rf /home/HwHiAiUser/Ascend-aicpu_syskernels.tar.gz && \
    # chown HwHiAiUser:HwHiAiUser /home/HwHiAiUser/aicpu.tar.gz && \
    # mkdir -p /home/HwHiAiUser/aicpu_kernels
# RUN tar -xvf /home/HwHiAiUser/aicpu.tar.gz -C /home/HwHiAiUser/ 2>/dev/null;exit 0
# RUN rm -rf /home/HwHiAiUser/aicpu.tar.gz && \
    # mv /home/HwHiAiUser/aicpu_kernels_device/* /home/HwHiAiUser/aicpu_kernels/ && \
    # chown -R HwHiAiUser:HwHiAiUser /home/HwHiAiUser/

# 若用户不需要使用AICPU算子，请将如下指令的注释“#”删除
#RUN rm -rf /usr/local/Ascend/nnrt/latest/opp/Ascend/aicpu/Ascend-aicpu_syskernels.tar.gz && \
#    chown -R HwHiAiUser:HwHiAiUser /home/HwHiAiUser/

USER 1000

RUN /usr/local/Ascend/nnrt/set_env.sh && chmod 755 yolo.om

CMD bash /home/AscendWork/run.sh
```

`install.sh` 文件示例：

```bash
#!/bin/bash
#进入容器工作目录
cd /home/AscendWork
#解压业务推理程序压缩包的命令请根据压缩包格式适配，压缩包名称请根据实际文件名称配置
tar xf dist.tar
```

```bash
# 建立安装和运行脚本
cat << EOF > install.sh
#!/bin/sh
cd /home/AscendWork
tar zxvf yolo.tgz
EOF
```

`run.sh` 文件示例：

```bash
#!/bin/bash
mkdir /dev/shm/dmp
mkdir /home/HwHiAiUser/hdc_ppc
nohup /var/dmp_daemon -I -M -U 8087 >&/dev/null &
/var/slogd -d
#启动推理程序，若用户不涉及推理程序可将如下命令注释
#进入业务推理程序的可执行文件所在目录，请根据实际可执行文件所在目录配置
cd /home/AscendWork/dist
#运行可执行文件，请根据实际文件名称配置
./main
```

```bash
cat << EOF > run.sh

#!/bin/bash
mkdir /dev/shm/dmp
mkdir /home/HwHiAiUser/hdc_ppc
nohup /var/dmp_daemon -I -M -U 8087 >&/dev/null &
/var/slogd -d
#启动推理程序，若用户不涉及推理程序可将如下命令注释
#进入业务推理程序的可执行文件所在目录，请根据实际可执行文件所在目录配置
cd /home/AscendWork/dist
#运行可执行文件，请根据实际文件名称配置
python3 main.py

EOF
```



构建命令：

（注意其中的 NNRT_PKG 和 DIST_PKG 需要自行更换）

```bash
docker build -t ascend-infer:v1 --build-arg NNRT_PKG=./Ascend-cann-nnrt_7.0.0_linux-aarch64.run --build-arg DIST_PKG=./yolo.tgz .
```

### 启动容器

启动容器的命令如下（**OpenEuler**）：

```bash
docker run -it -u HwHiAiUser:HwHiAiUser --pid=host \
--device=/dev/upgrade:/dev/upgrade \
--device=/dev/davinci0:/dev/davinci0 \
--device=/dev/davinci_manager_docker:/dev/davinci_manager \
--device=/dev/vdec:/dev/vdec \
--device=/dev/vpc:/dev/vpc \
--device=/dev/pngd:/dev/pngd \
--device=/dev/venc:/dev/venc \
--device=/dev/sys:/dev/sys \
--device=/dev/svm0 \
--device=/dev/acodec:/dev/acodec \
--device=/dev/ai:/dev/ai \
--device=/dev/ao:/dev/ao \
--device=/dev/vo:/dev/vo \
--device=/dev/hdmi:/dev/hdmi \
--device=/dev/ts_aisle:/dev/ts_aisle \
--device=/dev/dvpp_cmdlist:/dev/dvpp_cmdlist \
-v /etc/sys_version.conf:/etc/sys_version.conf:ro \
-v /etc/hdcBasic.cfg:/etc/hdcBasic.cfg:ro \
-v /usr/lib64/libaicpu_processer.so:/usr/lib64/libaicpu_processer.so:ro \
-v /usr/lib64/libaicpu_prof.so:/usr/lib64/libaicpu_prof.so:ro \
-v /usr/lib64/libaicpu_sharder.so:/usr/lib64/libaicpu_sharder.so:ro \
-v /usr/lib64/libadump.so:/usr/lib64/libadump.so:ro \
-v /usr/lib64/libtsd_eventclient.so:/usr/lib64/libtsd_eventclient.so:ro \
-v /usr/lib64/libaicpu_scheduler.so:/usr/lib64/libaicpu_scheduler.so:ro \
-v /usr/lib64/libcrypto.so.1.1:/usr/lib64/libcrypto.so.1.1:ro \
-v /usr/lib64/libyaml-0.so.2.0.9:/usr/lib64/libyaml-0.so.2:ro \
-v /usr/lib64/libdcmi.so:/usr/lib64/libdcmi.so:ro \
-v /usr/lib64/libmpi_dvpp_adapter.so:/usr/lib64/libmpi_dvpp_adapter.so:ro \
-v /usr/lib64/aicpu_kernels/:/usr/lib64/aicpu_kernels/:ro \
-v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi:ro \
-v /usr/lib64/libstackcore.so:/usr/lib64/libstackcore.so:ro \
-v /usr/lib64/libunified_timer.so:/usr/lib64/libunified_timer.so \
-v /usr/lib64/libdp.so:/usr/lib64/libdp.so \
-v /usr/lib64/libtensorflow.so:/usr/lib64/libtensorflow.so \
-v /usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64:ro \
-v /var/slogd:/var/slogd:ro \
-v /var/dmp_daemon:/var/dmp_daemon:ro \
ascend-infer:v1 /bin/bash
```

启动容器（**Ubuntu**）：

```bash
docker run --rm --network host -it -u HwHiAiUser:HwHiAiUser --pid=host \
--device=/dev/upgrade:/dev/upgrade \
--device=/dev/davinci0:/dev/davinci0 \
--device=/dev/davinci_manager_docker:/dev/davinci_manager \
--device=/dev/vdec:/dev/vdec \
--device=/dev/vpc:/dev/vpc \
--device=/dev/pngd:/dev/pngd \
--device=/dev/venc:/dev/venc \
--device=/dev/sys:/dev/sys \
--device=/dev/svm0 \
--device=/dev/acodec:/dev/acodec \
--device=/dev/ai:/dev/ai \
--device=/dev/ao:/dev/ao \
--device=/dev/hdmi:/dev/hdmi \
--device=/dev/ts_aisle:/dev/ts_aisle \
--device=/dev/dvpp_cmdlist:/dev/dvpp_cmdlist \
-v /etc/sys_version.conf:/etc/sys_version.conf:ro \
-v /etc/hdcBasic.cfg:/etc/hdcBasic.cfg:ro \
-v /usr/lib64/libaicpu_processer.so:/usr/lib64/libaicpu_processer.so:ro \
-v /usr/lib64/libaicpu_prof.so:/usr/lib64/libaicpu_prof.so:ro \
-v /usr/lib64/libaicpu_sharder.so:/usr/lib64/libaicpu_sharder.so:ro \
-v /usr/lib64/libadump.so:/usr/lib64/libadump.so:ro \
-v /usr/lib64/libtsd_eventclient.so:/usr/lib64/libtsd_eventclient.so:ro \
-v /usr/lib64/libaicpu_scheduler.so:/usr/lib64/libaicpu_scheduler.so:ro \
-v /usr/lib/aarch64-linux-gnu/libcrypto.so.1.1:/usr/lib64/libcrypto.so.1.1:ro \
-v /usr/lib/aarch64-linux-gnu/libyaml-0.so.2.0.6:/usr/lib64/libyaml-0.so.2:ro \
-v /usr/lib64/libdcmi.so:/usr/lib64/libdcmi.so:ro \
-v /usr/lib64/libmpi_dvpp_adapter.so:/usr/lib64/libmpi_dvpp_adapter.so:ro \
-v /usr/lib64/aicpu_kernels/:/usr/lib64/aicpu_kernels/:ro \
-v /usr/local/sbin/npu-smi:/usr/local/sbin/npu-smi:ro \
-v /usr/lib64/libstackcore.so:/usr/lib64/libstackcore.so:ro \
-v /usr/lib64/libunified_timer.so:/usr/lib64/libunified_timer.so \
-v /usr/lib64/libdp.so:/usr/lib64/libdp.so \
-v /usr/lib64/libtensorflow.so:/usr/lib64/libtensorflow.so \
-v /usr/local/Ascend/driver/lib64:/usr/local/Ascend/driver/lib64:ro \
-v /var/slogd:/var/slogd:ro \
-v /var/dmp_daemon:/var/dmp_daemon:ro \
-- ascend-infer:v1 /bin/bash
```



容器启动之后，在容器中执行如下命令查看当前 docker 容器中可以使用的 davinci 设备：

```bash
ls /dev/ | grep davinci*
```

执行如下命令查看挂载的芯片状态是否正常：

```bash
npu-smi info
```

如果要在容器运行中保存容器镜像，可以使用如下命令：

```bash
# 保存容器镜像
docker commit <CONTAINER ID> image-name:tag
# 保存成文件
docker save -o image.tar image-name:tag
```

如果在退出容器之后要重新进入容器，可以使用命令：

```bash
docker exec -it <CONTAINER ID> /bin/bash
```

## 2. 安装 NPU 驱动和固件

安装所需依赖：

```bash
dnf install -y make dkms gcc kernel-headers-$(uname -r) kernel-devel-$(uname -r)
```

进入软件包目录，执行如下命令，增加执行权限，并且校验软件包的一致性和完整性：

```bash
chmod +x Ascend-hdk-310b-npu-driver-soc_23.0.rc2_linux-aarch64.run
chmod +x Ascend-hdk-310b-npu-firmware-soc_6.2.t2.0.b133.run
./Ascend-hdk-310b-npu-driver-soc_23.0.rc2_linux-aarch64.run --check
./Ascend-hdk-310b-npu-firmware-soc_6.2.t2.0.b133.run --check
```

执行如下命令安装驱动：

```bash
./Ascend-hdk-310b-npu-driver-soc_23.0.rc2_linux-aarch64.run --full
```

执行如下命令安装固件：

```bash
./Ascend-hdk-310b-npu-firmware-soc_6.2.t2.0.b133.run --full
```













