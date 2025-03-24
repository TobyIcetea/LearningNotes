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
# OpenEuler
rm /etc/os-release
cp /etc/initrd-release /etc/os-release

# Ubuntu
rm /etc/os-release
cp /usr/lib/os-release /etc/os-release
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

## 5. Atlas 系统时间不同步

初始安装好的系统的系统时间是不对的，所以我们通过 ntpdate 进行系统时间的同步：

```bash
# 先同步一次时间
ntpdate time1.aliyun.com

# 添加 crontab 更新时间
cat << EOF >> /etc/crontab
0 * * * * ntpdate time1.aliyun.com
EOF

# 设定时区
timedatectl set-timezone Asia/Shanghai

# 验证时间对不对
date
```

## 6. 对开发板使用操作系统的想法

似乎 OpenEuler 初始安装好就是有缺陷的。

在初始安装好的 OpenEuler 上，直接执行如下命令开启 notebook，运行预装的一些 demo：

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

然后运行 yolov5 的 demo，在执行 `import torchvision` 的时候，提示报错：

```bash
/usr/local/lib64/python3.9/site-packages/torchvision/io/image.py:13: UserWarning: Failed to load image Python extension: 
  warn(f"Failed to load image Python extension: {e}")
```

原因似乎是 torch 版本和 torchvision 版本不匹配导致的，但是我尝试了一些方法，发现我还是解决不了这个问题。

> 额，但是我换了 Ubuntu 之后，好像也是一样的。也会出现这个报错。

于是换 Ubuntu 吧，Ascend 的开发板，在进行应用适配的时候，似乎还是首先考虑 Ubuntu 的。

## 7. 从 Ubuntu 开始

首先我不太确定，我们的开发板上到底有没有安装驱动、固件、CANN 之类的产品？

### 驱动

如果安装好驱动，那么执行 `npu-smi info` 的时候就不会报错，而且在显示出的信息中，可以看到自己驱动的版本：

![image-20250324090532635](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250324090532635.png)

可以看到，我们的驱动是 `23.0.rc3` 版本的。

### 固件

固件的版本不好查看，但是我们进入到 Ascend 所有组件的目录中，发现：

```bash
(base) root@davinci-mini:/usr/local/Ascend# ll
total 32
drwxr-xr-x  8 root       root       4096 Oct 18  2023 ./
drwxr-xr-x 16 root       root       4096 Apr  8  2022 ../
drwxr-xr-x  4 root       root       4096 Oct 18  2023 ascend-toolkit/
drwxr-xr-x  3 root       root       4096 Apr  8  2022 driver/
dr-xr-x---  5 root       root       4096 Jul 25  2023 firmware/
dr-xr-x---  2 HwHiAiUser HwHiAiUser 4096 Apr  8  2022 include/
lrwxrwxrwx  1 root       root         16 Oct 18  2023 mxVision -> mxVision-5.0.RC3/
drwxr-x--- 11 root       root       4096 Oct 18  2023 mxVision-5.0.RC3/
drwxr-xr-x  3 root       root       4096 Jun  7  2023 thirdpart/
```

其中是有一个 firmware 文件夹存在的。

进入到这个文件夹中，发现这个文件夹中有如下子目录：

```bash
(base) root@davinci-mini:/usr/local/Ascend/firmware# ll
total 20
dr-xr-x--- 5 root root 4096 Jul 25  2023 ./
drwxr-xr-x 8 root root 4096 Oct 18  2023 ../
dr-xr-x--- 2 root root 4096 Jul 25  2023 image/
dr-xr-x--- 2 root root 4096 Jul 25  2023 script/
dr-xr-x--- 3 root root 4096 Jul 25  2023 tools/
```

虽然不确定版本，但是可以确定固件是一定存在的。

### CANN

执行以下命令：

```bash
(base) root@davinci-mini:/usr/local/Ascend/ascend-toolkit/latest/aarch64-linux# cat ascend_toolkit_install.info
package_name=Ascend-cann-toolkit
version=7.0.RC1
innerversion=V100R001C13SPC005B246
compatible_version=[V100R001C29],[V100R001C30],[V100R001C13],[V100R003C10],[V100R003C11]
arch=aarch64
os=linux
path=/usr/local/Ascend/ascend-toolkit/7.0.RC1/aarch64-linux
```

按照官网的说法，如果有这个文件，那么 CANN 就是已经被安装好的。

从中也可以看到，Ascend-cann-toolkit 是被安装好的，并且 CANN 的版本是 7.0.RC1。

### 总结

我们看一下 Ubuntu 下原生就下载好的 Ascend 组件：

```bash
(base) root@davinci-mini:/usr/local/Ascend# ll
total 32
drwxr-xr-x  8 root       root       4096 Oct 18  2023 ./
drwxr-xr-x 16 root       root       4096 Apr  8  2022 ../
drwxr-xr-x  4 root       root       4096 Oct 18  2023 ascend-toolkit/
drwxr-xr-x  3 root       root       4096 Apr  8  2022 driver/
dr-xr-x---  5 root       root       4096 Jul 25  2023 firmware/
dr-xr-x---  2 HwHiAiUser HwHiAiUser 4096 Apr  8  2022 include/
lrwxrwxrwx  1 root       root         16 Oct 18  2023 mxVision -> mxVision-5.0.RC3/
drwxr-x--- 11 root       root       4096 Oct 18  2023 mxVision-5.0.RC3/
drwxr-xr-x  3 root       root       4096 Jun  7  2023 thirdpart/
```

比 OpenEuler 那边多了 firmware、mxVision，或许是那边欧拉把这些东西都放到其他地方了，但是看起来 Ubuntu 给的更全。











## 10. 在本地通过一个 python 文件运行 yolo

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



下载 ascend-infer 镜像：

```bash
docker login -u cn-south-1@JY27ELOTNN4YC8LPI82J swr.cn-south-1.myhuaweicloud.com

c1520f8d07ba557de0340940c350d9eca2217dabb73c5e7bf3b00c6995f1c01e

docker pull swr.cn-south-1.myhuaweicloud.com/ascendhub/ascend-infer:24.0.RC3-openeuler20.03
```

安装新版本 torch：

[网站](https://www.hiascend.com/document/detail/zh/Pytorch/600/configandinstg/instg/insg_0001.html)

![image-20250323162649101](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250323162649101.png)

```bash
# 下载PyTorch安装包
wget https://download.pytorch.org/whl/cpu/torch-2.1.0-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
# 下载torch_npu插件包
wget https://gitee.com/ascend/pytorch/releases/download/v5.0.0-pytorch2.1.0/torch_npu-2.1.0-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
# 安装命令
pip3 install torch-2.1.0-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
pip3 install torch_npu-2.1.0-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
```

代码：

```python
import cv2
import numpy as np
import torch
from skvideo.io import vreader, FFmpegWriter
from ais_bench.infer.interface import InferSession

from det_utils import letterbox, scale_coords, nms


def preprocess_image(image, cfg, bgr2rgb=True):
    """图片预处理"""
    img, scale_ratio, pad_size = letterbox(image, new_shape=cfg['input_shape'])
    if bgr2rgb:
        img = img[:, :, ::-1]
    img = img.transpose(2, 0, 1)  # HWC2CHW
    img = np.ascontiguousarray(img, dtype=np.float32)
    return img, scale_ratio, pad_size


def draw_bbox(bbox, img0, color, wt, names):
    """在图片上画预测框"""
    det_result_str = ''
    for idx, class_id in enumerate(bbox[:, 5]):
        if float(bbox[idx][4] < float(0.05)):
            continue
        img0 = cv2.rectangle(img0, (int(bbox[idx][0]), int(bbox[idx][1])), (int(bbox[idx][2]), int(bbox[idx][3])),
                             color, wt)
        img0 = cv2.putText(img0, str(idx) + ' ' + names[int(class_id)], (int(bbox[idx][0]), int(bbox[idx][1] + 16)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        img0 = cv2.putText(img0, '{:.4f}'.format(bbox[idx][4]), (int(bbox[idx][0]), int(bbox[idx][1] + 32)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        det_result_str += '{} {} {} {} {} {}\n'.format(
            names[bbox[idx][5]], str(bbox[idx][4]), bbox[idx][0], bbox[idx][1], bbox[idx][2], bbox[idx][3])
    return img0

def get_labels_from_txt(path):
    """从txt文件获取图片标签"""
    labels_dict = dict()
    with open(path) as f:
        for cat_id, label in enumerate(f.readlines()):
            labels_dict[cat_id] = label.strip()
    return labels_dict

def infer_image(img_path, model, class_names, cfg):
    """图片推理"""
    # 图片载入
    image = cv2.imread(img_path)
    # 数据预处理
    img, scale_ratio, pad_size = preprocess_image(image, cfg)
    # 模型推理
    output = model.infer([img])[0]

    output = torch.tensor(output)
    # 非极大值抑制后处理
    boxout = nms(output, conf_thres=cfg["conf_thres"], iou_thres=cfg["iou_thres"])
    pred_all = boxout[0].numpy()
    # 预测坐标转换
    scale_coords(cfg['input_shape'], pred_all[:, :4], image.shape, ratio_pad=(scale_ratio, pad_size))
    # 图片预测结果可视化
    img_vis = draw_bbox(pred_all, image, (0, 255, 0), 2, class_names)
    cv2.imwrite("output.jpg", img_vis)  # 保存结果图片
    return img_vis  # 可选返回

def infer_frame_with_vis(image, model, labels_dict, cfg, bgr2rgb=True):
    # 数据预处理
    img, scale_ratio, pad_size = preprocess_image(image, cfg, bgr2rgb)
    # 模型推理
    output = model.infer([img])[0]

    output = torch.tensor(output)
    # 非极大值抑制后处理
    boxout = nms(output, conf_thres=cfg["conf_thres"], iou_thres=cfg["iou_thres"])
    pred_all = boxout[0].numpy()
    # 预测坐标转换
    scale_coords(cfg['input_shape'], pred_all[:, :4], image.shape, ratio_pad=(scale_ratio, pad_size))
    # 图片预测结果可视化
    img_vis = draw_bbox(pred_all, image, (0, 255, 0), 2, labels_dict)
    return img_vis

def img2bytes(image):
    """将图片转换为字节码"""
    return bytes(cv2.imencode('.jpg', image)[1])


def infer_video(video_path, model, labels_dict, cfg):
    """视频推理并保存为output.mp4"""
    # 读入视频
    cap = cv2.VideoCapture(video_path)
    # 获取原视频参数（帧率、分辨率）
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 创建视频写入对象（输出到output.mp4）
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 确保你的OpenCV支持该编码
    writer = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))

    while True:
        ret, img_frame = cap.read()
        if not ret:
            break
        # 对视频帧进行推理
        image_pred = infer_frame_with_vis(img_frame, model, labels_dict, cfg, bgr2rgb=True)
        # 写入处理后的帧
        writer.write(image_pred)

    # 释放资源
    cap.release()
    writer.release()
    print("视频已保存为 output.mp4")

def infer_camera(model, labels_dict, cfg):
    """外设摄像头实时推理（移除Jupyter依赖，仅保留基础逻辑）"""
    # 查找可用摄像头
    def find_camera_index():
        for index in range(10):
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                cap.release()
                return index
        raise ValueError("未检测到摄像头")

    # 初始化摄像头
    camera_index = find_camera_index()
    cap = cv2.VideoCapture(camera_index)

    # 创建窗口用于显示（可选）
    cv2.namedWindow("Camera Feed", cv2.WINDOW_NORMAL)

    while True:
        _, img_frame = cap.read()
        # 推理处理
        image_pred = infer_frame_with_vis(img_frame, model, labels_dict, cfg)
        # 显示处理结果（按Q键退出）
        cv2.imshow("Camera Feed", image_pred)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

cfg = {
    'conf_thres': 0.4,  # 模型置信度阈值，阈值越低，得到的预测框越多
    'iou_thres': 0.5,  # IOU阈值，高于这个阈值的重叠预测框会被过滤掉
    'input_shape': [640, 640],  # 模型输入尺寸
}

model_path = 'yolo.om'
label_path = './coco_names.txt'
# 初始化推理模型
model = InferSession(0, model_path)
labels_dict = get_labels_from_txt(label_path)


infer_mode = 'video'

if infer_mode == 'image':
    img_path = 'world_cup.jpg'
    infer_image(img_path, model, labels_dict, cfg)
elif infer_mode == 'camera':
    infer_camera(model, labels_dict, cfg)
elif infer_mode == 'video':
    video_path = 'racing.mp4'
    infer_video(video_path, model, labels_dict, cfg)
```







如果我想要运行这个模型，那么我就需要：

- `coco_names.txt`
- `det_utils.py`
- `main.py`
- `racing.mp4`
- `yolo.om`























