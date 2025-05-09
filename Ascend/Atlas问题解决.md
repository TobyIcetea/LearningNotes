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

## 5. Atlas 系统时间不同步（OpenEuler）

初始安装好的系统的系统时间是不对的，所以我们通过 ntpdate 进行系统时间的同步：

```bash
# 先同步一次时间
ntpdate time1.aliyun.com

# 添加 crontab 更新时间
cat << EOF >> /etc/crontab
0 * * * * ntpdate time1.aliyun.com
EOF

# 设定时区
# 其实这是关键的一步
timedatectl set-timezone Asia/Shanghai

# 验证时间对不对
date
```

## 6. 从 Ubuntu 开始

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

## 7. 组件版本的统一

于是我们得到 Atlas 开发板比较兼容的组件版本列表，或者之后，如果我们不知道该选择什么版本的组件，就直接从这里查表：

> RC1、RC2 等字段的含义：RC 表示 Release Candidate，表示候选发行版。

| 组件                   | 版本              | 备注                                                         |
| ---------------------- | ----------------- | ------------------------------------------------------------ |
| 驱动 Driver            | 23.0.RC3          |                                                              |
| 固件 Fireware          | 7.1.0.3.220       |                                                              |
| CANN                   | 7.0.RC1           |                                                              |
| NNRT                   | 7.0               |                                                              |
| Ascend  Docker Runtime | 6.0.0             |                                                              |
| Python                 | 3.9.2             |                                                              |
| torch                  | 1.11.0            | pip install torch==1.11.0                                    |
| torchvision            | 0.12.0            |                                                              |
| torchaudio             | 0.11.0            |                                                              |
| torch_npu              | 1.11.0.post8-cp39 | pip3 install torch_npu-1.11.0.post8-cp39-cp39-linux_aarch64.whl |
| ais_bench              | 0.0.2             | pip3 install aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl<br/>pip3 install ais_bench-0.0.2-py3-none-any.whl |

## 8. 在本地通过一个 python 文件运行 yolo

### 安装 Docker

```bash
# 安装
apt-get update
    
curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/ \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update

apt-get install docker-ce docker-ce-cli containerd.io

systemctl enable --now docker

# 配置加速
mkdir /etc/docker
cat <<EOF >  /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "registry-mirrors": [ 
	"https://1ecf599359e64520bd04701e6d7184e8.mirror.swr.myhuaweicloud.com",
	"https://le2c3l3b.mirror.aliyuncs.com"
  ]
}
EOF
```

### 业务代码

本次使用到的 yolov5 的 main.py 代码如下：

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

### 打包业务项目

进入到 yolo 的项目目录中，执行如下命令：

```bash
# 安装工具
pip install pipreqs
# 生成 requirements 文件
pipreqs ./ --encoding=utf-8 --force
```

之后看生成的 requirements.txt 文件，内容如下：

```bash
(base) root@davinci-mini:~/workdir/01-yolov5# cat requirements.txt
ais_bench==0.0.2
numpy==1.22.4
opencv_python_headless==4.7.0.72
scikit_video==1.1.11
torch==1.13.0
torchvision==0.14.0
```

其中的第一行 ais_bench 把它注释掉，因为这是 Ascend 自己的一个库，后面我们要通过 whl 文件单独进行安装，直接使用 pip install 去拉取库文件是拉不到的。

之后制作业务推理包：

```bash
# 打包业务程序
tar zcvf yolov5.tgz coco_names.txt det_utils.py main.py racing.mp4 yolo.om requirements.txt
```

### 制作 Dockerfile

创建一个 Dockerfile 的工作路径，进入到该路径下，之后执行：

```bash
# 拉取镜像
docker pull python:3.9.2

# 将 /etc/slog.conf 复制过来
cp /etc/slog.conf slog.conf

# 将 yolov5.tgz 复制过来
cp (yolov5.tgz 存放位置) ./

# 将 NNRT 安装包复制过来
cp (Ascend-cann-nnrt_7.0.0_linux-aarch64.run 存放位置) ./

# 将 torch_npu 插件复制过来
cp (torch_npu-1.11.0.post8-cp39-cp39-linux_aarch64.whl 存放位置) ./

# 将 ais_bench 的安装包复制过来
cp (aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl 存放位置) .
cp (ais_bench-0.0.2-py3-none-any.whl 存放位置) .


# 创建安装脚本：install.sh
cat << EOF > install.sh

#!/bin/sh
cd /home/AscendWork
tar zxvf yolov5.tgz

EOF


# 创建运行脚本：run.sh
cat << EOF > run.sh

#!/bin/bash
mkdir /dev/shm/dmp
mkdir /home/HwHiAiUser/hdc_ppc
nohup /var/dmp_daemon -I -M -U 8087 >&/dev/null &
/var/slogd -d

# 启动推理程序，若用户不涉及推理程序可将如下命令注释
# 运行可执行文件，请根据实际文件名称配置
python3 ./main.py --input video-data/input-file/ --output video-data/output-file/

EOF
```

创建加速镜像文件 `sources.list`（Debian 10）：

```bash
deb http://mirrors.aliyun.com/debian/ buster main non-free contrib
deb-src http://mirrors.aliyun.com/debian/ buster main non-free contrib
deb http://mirrors.aliyun.com/debian-security buster/updates main
deb-src http://mirrors.aliyun.com/debian-security buster/updates main
deb http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib
deb-src http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib
```

之后就可以制作 dockerfile：

```dockerfile
FROM python:3.9.2

USER root

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

# -------------------------------------------------------------------
# 从这部分开始定制

# 换源
COPY sources.list /etc/apt/sources.list
# 安装 libgl 库，安装 python 项目依赖
RUN apt-get update && apt-get install -y libgl1
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 安装 torch_npu 插件
COPY torch_npu-1.11.0.post8-cp39-cp39-linux_aarch64.whl .
RUN pip3 install torch_npu-1.11.0.post8-cp39-cp39-linux_aarch64.whl

# 安装 ais_bench 库
COPY aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl .
COPY ais_bench-0.0.2-py3-none-any.whl .
RUN pip3 install aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl
RUN pip3 install ais_bench-0.0.2-py3-none-any.whl

# 设置环境变量
RUN . /usr/local/Ascend/nnrt/set_env.sh && chmod 755 yolo.om

# -------------------------------------------------------------------


USER 1000
CMD bash /home/AscendWork/run.sh

```

### 构建镜像

（注意其中的 NNRT_PKG 和 DIST_PKG 需要自行更换）

```bash
docker build -t ascend-infer:0411 --build-arg NNRT_PKG=./Ascend-cann-nnrt_7.0.0_linux-aarch64.run --build-arg DIST_PKG=./yolov5.tgz .
```

### 启动容器（Ubuntu）

这里就说了 Ubuntu 的，OpenEuler 可以查：[边缘设备 CANN 部署文档](https://support.huawei.com/enterprise/zh/doc/EDOC1100423566/4a72915b?idPath=23710424|251366513|254884019|261408772|258915651)

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
-- ascend-infer:0411 /bin/bash
```

容器启动之后，在容器中执行如下命令查看当前 docker 容器中可以使用的 davinci 设备：

```bash
ls /dev/ | grep davinci*
```

执行如下命令查看挂载的芯片状态是否正常：

```bash
npu-smi info
```

## 9. npu-smi info 报错（待解决）

在部署好容器之后，发现运行 `npu-smi info` 总是报错：

```bash
[ERROR] DRV(9,npu-smi):2025-03-29-11:21:16.865.482 [dm_udp.c:91][dmp] [__dm_send_msg 91] sendmsg fail:2.
[ERROR] DRV(9,npu-smi):2025-03-29-11:21:16.865.610 [dm_udp.c:134][dmp] [__dm_udp_send 134] __dm_send_msg: sendto fail.errno=2
[ERROR] DRV(9,npu-smi):2025-03-29-11:21:16.865.635 [dm_msg_intf.c:757][dmp] [dm_send_req 757] failed call intf->send_msg, ret = 2, send_msg->opcode = 0xf.
[ERROR] DRV(9,npu-smi):2025-03-29-11:21:16.865.662 [dsmi_common.c:642][dmp] [_dsmi_send_msg_rec_res 642] call dev_mon_send_request error:27.
```

至此仍然不会解决……

## 10. 运行多个容器竞争 npu

### 情况概述

在物理机上，运行多个 yolo 算法，此时可以看到通过 npu-smi 看到 NPU 的 AI 占用率是一直在上升的。也就是说，物理机中无论开启运行多少个 yolo 副本，都不会发生资源争用的问题。

但是在容器中，就出现问题了：我就开启了两个容器，两个容器同时执行 `python3 ./main.py`（同时执行 yolo 推理任务），只有第一个运行的副本可以成功运行，后面运行的副本都会报错：

```bash
[ACL ERROR] EL0005: The resources are busy.
        Possible Cause: 1. The resources have been occupied. 2. The device is being reset. 3. Software is not ready.
        Solution: 1. Close applications not in use. 2. Wait for a while and try again.
        TraceBack (most recent call last):
        Invalid devId, current device=0, valid devId range is [0, 0)[FUNC:ContextCreate][FILE:api_impl.cc][LINE:2615]
        rtCtxCreateEx execute failed, reason=[device id error][FUNC:FuncErrorReason][FILE:error_message_manage.cc][LINE:50]
        create context failed, device is 0, runtime errorCode is 107001[FUNC:ReportCallError][FILE:log_inner.cpp][LINE:161]
        ctx is NULL![FUNC:GetDevErrMsg][FILE:api_impl.cc][LINE:4541]
        The argument is invalid.Reason: rtGetDevMsg execute failed, reason=[context pointer null]
```

这种情况只有在容器中才会出现，如果我们在物理机中直接运行 yolo 推理，之后在容器中再启动一个推理程序的话，也不会报错。

### 切分逻辑 NPU

我们一开始在启动容器的时候，使用的挂载参数如下：

```bash
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
```

然后在容器中，查看 `/dev` 下面的设备：

```bash
HwHiAiUser@davinci-mini:/home/AscendWork$ ls -l /dev
crw-rw---- 1 HwHiAiUser HwHiAiUser 218, 32 Mar 30 07:25 acodec
crw-rw---- 1 HwHiAiUser HwHiAiUser 218,  6 Mar 30 07:25 ai
crw-rw---- 1 HwHiAiUser HwHiAiUser 218,  7 Mar 30 07:25 ao
crw--w---- 1 HwHiAiUser tty        136,  0 Mar 30 07:36 console
lrwxrwxrwx 1 root       root            11 Mar 30 07:25 core -> /proc/kcore
crw-rw---- 1 HwHiAiUser HwHiAiUser 236,  0 Mar 30 07:25 davinci0
crw-rw---- 1 HwHiAiUser HwHiAiUser 237,  0 Mar 30 07:25 davinci_manager
crw-rw---- 1 HwHiAiUser HwHiAiUser 504,  0 Mar 30 07:25 dvpp_cmdlist
lrwxrwxrwx 1 root       root            13 Mar 30 07:25 fd -> /proc/self/fd
crw-rw-rw- 1 root       root         1,  7 Mar 30 07:25 full
crw-rw---- 1 HwHiAiUser HwHiAiUser 218, 19 Mar 30 07:25 hdmi
drwxrwxrwt 2 root       root            40 Mar 30 07:25 mqueue
crw-rw-rw- 1 root       root         1,  3 Mar 30 07:25 null
crw-rw---- 1 HwHiAiUser HwHiAiUser 218, 44 Mar 30 07:25 pngd
lrwxrwxrwx 1 root       root             8 Mar 30 07:25 ptmx -> pts/ptmx
drwxr-xr-x 2 root       root             0 Mar 30 07:25 pts
crw-rw-rw- 1 root       root         1,  8 Mar 30 07:25 random
drwxrwxrwt 2 root       root            40 Mar 30 07:25 shm
lrwxrwxrwx 1 root       root            15 Mar 30 07:25 stderr -> /proc/self/fd/2
lrwxrwxrwx 1 root       root            15 Mar 30 07:25 stdin -> /proc/self/fd/0
lrwxrwxrwx 1 root       root            15 Mar 30 07:25 stdout -> /proc/self/fd/1
crw-rw---- 1 HwHiAiUser HwHiAiUser  10, 60 Mar 30 07:25 svm0
crw-rw---- 1 HwHiAiUser HwHiAiUser 218,  8 Mar 30 07:25 sys
crw-rw---- 1 HwHiAiUser HwHiAiUser 505,  0 Mar 30 07:25 ts_aisle
crw-rw-rw- 1 root       root         5,  0 Mar 30 07:25 tty
crw-rw---- 1 HwBaseUser HwBaseUser 506,  0 Mar 30 07:25 upgrade
crw-rw-rw- 1 root       root         1,  9 Mar 30 07:25 urandom
crw-rw---- 1 HwHiAiUser HwHiAiUser 218,  3 Mar 30 07:25 vdec
crw-rw---- 1 HwHiAiUser HwHiAiUser 218,  2 Mar 30 07:25 venc
crw-rw---- 1 HwHiAiUser HwHiAiUser 218, 43 Mar 30 07:25 vpc
crw-rw-rw- 1 root       root         1,  5 Mar 30 07:25 zero
```

昇腾的异构计算架构（CANN）默认将NPU设备视为独占型资源。即使通过`--device=/dev/davinci0`将设备挂载到多个容器，CANN的运行时引擎（如AscendCL）会检测到设备已被占用，并拒绝第二个进程的初始化请求。

昇腾虚拟化实例功能：通过资源虚拟化的方式将物理机或虚拟机配置的NPU（昇腾AI处理器）切分成若干份vNPU（虚拟NPU）挂载到容器中，支持多用户共同使用一个NPU，提高资源利用率。

起初我们执行 `npu-smi info` 命令，显示出来的信息如下：

![image-20250330154832390](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250330154832390.png)

设置算力切分模式：

```bash
npu-smi set -t vnpu-mode -d 0
```

之后使用如下命令查询支持的切分模式：

```bash
npu-smi info -t template-info
```

但是这个命令返回：

```bash
This device does not support querying template-info.
```

OK 死心了，我这个设备确实不支持算力切分：[Atlas A2 智能边缘硬件 24.1.0 npu-smi 命令参考 01](https://support.huawei.com/enterprise/zh/doc/EDOC1100438698/7a5fc1e2?idPath=23710424|251366513|22892968|252309141|254411267)。

![image-20250330160748448](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250330160748448.png)

## 11. 通过 Pod 部署 Yolo 模型

### 第一版 ascend-infer.yaml

这一版实现的功能是，通过 apply 这个声明式文件，然后再通过 exec 命令进入容器中，然后在容器中再去执行 `python3 main.py` 去启动推理任务。

这一版的缺点是，打包镜像的时候，需要推理的视频文件是和镜像文件绑定在一起的，只能推理这个视频文件，其他的都做不了。而且，执行命令的时候不能自动化，只能通过 exec 进入容器中手动执行。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ascend-infer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ascend-infer
  template:
    metadata:
      labels:
        app: ascend-infer
    spec:
      nodeName: atlas  # 指定在 atlas 节点上运行
      hostNetwork: true  # 相当于 --netrwork host
      hostPID: true  # 相当于 --pid=host
      securityContext:
        runAsUser: 1000
        runAsGroup: 1000
      containers:
      - name: ascend-infer
        image: ascend-infer:0329
        imagePullPolicy: Never
        command: ["/bin/bash", "-c", "sleep infinity"]  # 让容器无限休眠
        securityContext:
          privileged: true  # 可能需要特权模式来访问设备
        volumeMounts:
        - name: sys-version
          mountPath: /etc/sys_version.conf
          readOnly: true
        - name: hdc-basic
          mountPath: /etc/hdcBasic.cfg
          readOnly: true
        - name: libaicpu-processer
          mountPath: /usr/lib64/libaicpu_processer.so
          readOnly: true
        - name: libaicpu-prof
          mountPath: /usr/lib64/libaicpu_prof.so
          readOnly: true
        - name: libaicpu-sharder
          mountPath: /usr/lib64/libaicpu_sharder.so
          readOnly: true
        - name: libadump
          mountPath: /usr/lib64/libadump.so
          readOnly: true
        - name: libtsd-eventclient
          mountPath: /usr/lib64/libtsd_eventclient.so
          readOnly: true
        - name: libaicpu-scheduler
          mountPath: /usr/lib64/libaicpu_scheduler.so
          readOnly: true
        - name: libcrypto
          mountPath: /usr/lib64/libcrypto.so.1.1
          readOnly: true
        - name: libyaml
          mountPath: /usr/lib64/libyaml-0.so.2
          readOnly: true
        - name: libdcmi
          mountPath: /usr/lib64/libdcmi.so
          readOnly: true
        - name: libmpi-dvpp-adapter
          mountPath: /usr/lib64/libmpi_dvpp_adapter.so
          readOnly: true
        - name: aicpu-kernels
          mountPath: /usr/lib64/aicpu_kernels/
          readOnly: true
        - name: npu-smi
          mountPath: /usr/local/sbin/npu-smi
          readOnly: true
        - name: libstackcore
          mountPath: /usr/lib64/libstackcore.so
          readOnly: true
        - name: libunified-timer
          mountPath: /usr/lib64/libunified_timer.so
        - name: libdp
          mountPath: /usr/lib64/libdp.so
        - name: libtensorflow
          mountPath: /usr/lib64/libtensorflow.so
        - name: ascend-driver-lib64
          mountPath: /usr/local/Ascend/driver/lib64
          readOnly: true
        - name: slogd
          mountPath: /var/slogd
          readOnly: true
        - name: dmp-daemon
          mountPath: /var/dmp_daemon
          readOnly: true
# 从这里分开挂载-----------------------------------
        - name: upgrade
          mountPath: /dev/upgrade
        - name: davinci0
          mountPath: /dev/devinci0
        - name: davinci-manager
          mountPath: /dev/davinci_manager
        - name: vdec
          mountPath: /dev/vdec
        - name: vpc
          mountPath: /dev/vpc
        - name: pngd
          mountPath: /dev/pngd
        - name: venc
          mountPath: /dev/venc
        - name: sys
          mountPath: /dev/sys
        - name: svm0
          mountPath: /dev/svm0
        - name: acodec
          mountPath: /dev/acodec
        - name: ai
          mountPath: /dev/ai
        - name: ao
          mountPath: /dev/ao
        - name: hdmi
          mountPath: /dev/hdmi
        - name: ts-aisle
          mountPath: /dev/ts_aisle
        - name: dvpp-cmdlist
          mountPath: /dev/dvpp_cmdlist
      volumes:
      - name: sys-version
        hostPath:
          path: /etc/sys_version.conf
          type: File  # 明确指定为文件类型
      - name: hdc-basic
        hostPath:
          path: /etc/hdcBasic.cfg
          type: File
      - name: libaicpu-processer
        hostPath:
          path: /usr/lib64/libaicpu_processer.so
          type: File
      - name: libaicpu-prof
        hostPath:
          path: /usr/lib64/libaicpu_prof.so
          type: File
      - name: libaicpu-sharder
        hostPath:
          path: /usr/lib64/libaicpu_sharder.so
          type: File
      - name: libadump
        hostPath:
          path: /usr/lib64/libadump.so
          type: File
      - name: libtsd-eventclient
        hostPath:
          path: /usr/lib64/libtsd_eventclient.so
          type: File
      - name: libaicpu-scheduler
        hostPath:
          path: /usr/lib64/libaicpu_scheduler.so
          type: File
      - name: libcrypto
        hostPath:
          path: /usr/lib/aarch64-linux-gnu/libcrypto.so.1.1
          type: File
      - name: libyaml
        hostPath:
          path: /usr/lib/aarch64-linux-gnu/libyaml-0.so.2.0.6
          type: File
      - name: libdcmi
        hostPath:
          path: /usr/lib64/libdcmi.so
          type: File
      - name: libmpi-dvpp-adapter
        hostPath:
          path: /usr/lib64/libmpi_dvpp_adapter.so
          type: File
      - name: aicpu-kernels
        hostPath:
          path: /usr/lib64/aicpu_kernels/
          type: Directory  # 指定为目录类型
      - name: npu-smi
        hostPath:
          path: /usr/local/sbin/npu-smi
          type: File
      - name: libstackcore
        hostPath:
          path: /usr/lib64/libstackcore.so
          type: File
      - name: libunified-timer
        hostPath:
          path: /usr/lib64/libunified_timer.so
          type: Directory
      - name: libdp
        hostPath:
          path: /usr/lib64/libdp.so
          type: File
      - name: libtensorflow
        hostPath:
          path: /usr/lib64/libtensorflow.so
          type: File
      - name: ascend-driver-lib64
        hostPath:
          path: /usr/local/Ascend/driver/lib64
          type: Directory
      - name: slogd
        hostPath:
          path: /var/slogd
          type: File
      - name: dmp-daemon
        hostPath:
          path: /var/dmp_daemon
          type: File
# 从这里分开挂载--------------------------
      - name: upgrade
        hostPath:
          path: /dev/upgrade
          type: CharDevice  # 指定为字符设备
      - name: davinci0
        hostPath:
          path: /dev/davinci0
          type: CharDevice
      - name: davinci-manager
        hostPath:
          path: /dev/davinci_manager_docker  # 注意源路径不同
          type: CharDevice
      - name: vdec
        hostPath:
          path: /dev/vdec
          type: CharDevice
      - name: vpc
        hostPath:
          path: /dev/vpc
          type: CharDevice
      - name: pngd
        hostPath:
          path: /dev/pngd
          type: CharDevice
      - name: venc
        hostPath:
          path: /dev/venc
          type: CharDevice
      - name: sys
        hostPath:
          path: /dev/sys
          type: CharDevice
      - name: svm0
        hostPath:
          path: /dev/svm0
          type: CharDevice
      - name: acodec
        hostPath:
          path: /dev/acodec
          type: CharDevice
      - name: ai
        hostPath:
          path: /dev/ai
          type: CharDevice
      - name: ao
        hostPath:
          path: /dev/ao
          type: CharDevice
      - name: hdmi
        hostPath:
          path: /dev/hdmi
          type: CharDevice
      - name: ts-aisle
        hostPath:
          path: /dev/ts_aisle
          type: CharDevice
      - name: dvpp-cmdlist
        hostPath:
          path: /dev/dvpp_cmdlist
          type: CharDevice
```

### 第二版 ascend-infer.yaml

基本的想法是，通过 master 节点进行任务的切分，之后分节点进行任务的处理，最后再返回到 master 节点进行合并。

#### 查询设备的算力档位

在 atlas 节点上直接查询：

```bash
(base) root@atlas:~/workdir/data/output-file# npu-smi info -t nve-level -i 0 -c 0
        nve level                      : 20T_1.6GHz
```

通过如下命令，可以获取每个节点的名称和对应的算力：

```bash
#!/bin/bash

nodes=$(kubectl get nodes -o name | grep '^node/atlas' | sed 's/^node\///')

output_file="npu_levels.json"

# 创建关联数组（类似于 map）
declare -A levels

for node in $nodes; do
    echo "Checking NPU level on: $node"
    if level=$(ssh -o ConnectTimeout=5 "$node" "npu-smi info -t nve-level -i 0 -c 0 2>/dev/null | awk '/nve level/ {print \$4}' | cut -dT -f1"); then
        levels["$node"]=$level
    else
        levels["$node"]="null"
        echo "[WARNING] Failed to check $node" >&2
    fi
done

# 遍历数组，生成jq表达式
jq_filter='{}'
for key in "${!levels[@]}"; do
  jq_filter+=" | .[\"$key\"] = ${levels[$key]}"
done

echo "Check All NPU Levels Down!"

# 生成JSON文件
jq -n "$jq_filter" > ${output_file}
```

将上述文件保存为 `generate-npu-levels.sh`，执行的时候直接运行：

```bash
bash generate-npu-levels.sh
```

运行结果是产生 `npu-levels.json` 文件。此时 `npu-levels.json` 文件中的内容如下：

```json
{
  "atlas1": 8,
  "atlas": 20
}
```

#### 按照算力切分视频文件

```python
import argparse
import os
import cv2
import json

def split_video(input_path, output_dir, segments):
    # 验证比例总和为1
    total_ratio = sum(seg['ratio'] for seg in segments)
    if abs(total_ratio - 1.0) > 0.001:
        raise ValueError("比例之和必须等于1")

    # 准备输出路径并创建目录
    outputs = []
    for seg in segments:
        output_path = os.path.join(output_dir, seg['filename'])
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        outputs.append(output_path)

    # 检查文件名唯一性
    if len(outputs) != len(set(outputs)):
        raise ValueError("输出文件名存在重复")

    # 打开视频文件
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"无法打开视频文件: {input_path}")

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    codec = cv2.VideoWriter_fourcc(*'mp4v')

    # 计算分割点
    split_points = []
    accumulated = 0.0
    for seg in segments[:-1]:  # 最后一个分割点不需要计算
        accumulated += seg['ratio']
        split_points.append(int(total_frames * accumulated))

    # 创建视频写入器
    writers = [cv2.VideoWriter(output, codec, fps, (width, height))
              for output in outputs]

    # 读取并写入帧
    current_writer_idx = 0
    next_split = split_points[current_writer_idx] if split_points else total_frames

    for frame_count in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        writers[current_writer_idx].write(frame)

        # 检查是否需要切换到下一个写入器
        if frame_count + 1 == next_split and current_writer_idx < len(writers) - 1:
            current_writer_idx += 1
            next_split = split_points[current_writer_idx] if current_writer_idx < len(split_points) else total_frames

    # 释放资源
    cap.release()
    for writer in writers:
        writer.release()

    print("视频已分割为:")
    for output in outputs:
        print(f"  {output}")


def parse_npu_json(json_path):
    try:
        with open(json_path, 'r') as f:
            npu_data = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"JSON文件未找到: {json_path}")
    except json.JSONDecodeError:
        raise ValueError(f"JSON文件格式错误: {json_path}")

    segments = []
    total_power = 0
    filenames = set()

    # 获取命令行输入的input参数
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args, _ = parser.parse_known_args()  # 允许部分解析参数
    base_name = os.path.splitext(os.path.basename(args.input))[0]

    devices = list(npu_data.items())  # 保持原始顺序

    for idx, (device, config_power) in enumerate(devices, 1):
        power = float(config_power)
        filename = f"{base_name}_{idx}.mp4"

        # 数据校验
        if power <= 0:
            raise ValueError(f"设备 {device} 的算力值必须大于0")
        if not filename.strip():
            raise ValueError(f"设备 {device} 的文件名不能为空")
        if filename in filenames:
            raise ValueError(f"文件名重复: {filename}")
        filenames.add(filename)
        total_power += power
        segments.append({
            'device': device,
            'power': power,
            'filename': filename.strip()
        })

    if total_power <= 0:
        raise ValueError("总算力值必须大于0")

    # 计算比例
    for seg in segments:
        seg['ratio'] = seg['power'] / total_power

    return segments


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="根据NPU算力配置分割视频")
    parser.add_argument("--input", required=True, help="输入视频文件路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    parser.add_argument("--npu-json", required=True,
                      help="包含NPU算力配置的JSON文件路径")

    args = parser.parse_args()

    try:
        segments = parse_npu_json(args.npu_json)
        # 提取比例列表（保持原有分割逻辑兼容）
        ratios = [seg['ratio'] for seg in segments]
        # 调用修改后的分割函数
        split_video(args.input, args.output, segments)

        # 将处理后的数据写回JSON文件
        modified_data = {}
        for seg in segments:
            device = seg['device']
            modified_data[device] = {
                'power': seg['power'],
                'filename': seg['filename']
            }

        with open(args.npu_json, 'w') as f:
            json.dump(modified_data, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"错误: {e}")
```

将上述文件保存为 `split-video.py`。操作方式：

```bash
python3 ./split-video.py --input full-videos/racing.mp4 --output ./segments/ --npu-json npu-levels.json
```

之后就可以在 `--output` 目录下生成两个文件：`racing_1.mp4` 和 `racing_2.mp4`。并且修改 json 文件为如下格式：

```json
{
  "atlas1": {
    "power": 8,
    "filename": "racing_1.mp4"
  },
  "atlas": {
    "power": 20,
    "filename": "racing_2.mp4"
  }
}
```

#### 按照 json 将视频文件进行分发

```python
import json
import subprocess
import os
import argparse
from pathlib import Path

def auto_scp(json_file, source_dir, dest_dir):
    # 加载JSON文件
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: {json_file} 文件未找到")
        return
    except json.JSONDecodeError:
        print(f"错误: {json_file} 格式不正确")
        return

    # 处理每个节点
    for node_name, node_info in data.items():
        filename = node_info.get('filename')
        if not filename:
            print(f"警告: {node_name} 缺少 filename 字段，跳过")
            continue

        source_file = os.path.join(source_dir, filename)
        if not os.path.exists(source_file):
            print(f"错误: 源文件 {source_file} 不存在，跳过")
            continue

        # 构建远程命令来检查并创建目标目录
        check_dir_cmd = [
            'ssh',
            node_name,
            f'mkdir -p {dest_dir} && echo "目录已存在或创建成功" || echo "目录创建失败"'
        ]

        # 执行SCP传输
        print(f"\n处理节点 {node_name}:")
        print(f"1. 确保目标目录存在...")
        try:
            # 检查并创建远程目录
            result = subprocess.run(check_dir_cmd, capture_output=True, text=True)
            if "失败" in result.stdout:
                print(f"错误: 无法在 {node_name} 上创建目录 {dest_dir}")
                continue
            print("  目录验证成功")

            # 执行文件传输
            print(f"2. 传输 {filename} 到 {node_name}:{dest_dir}...")
            scp_command = ['scp', source_file, f"{node_name}:{dest_dir}"]
            subprocess.run(scp_command, check=True)
            print(f"  传输成功!")

        except subprocess.CalledProcessError as e:
            print(f"失败: 处理 {node_name} 时出错 - {e}")

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='自动将视频文件传输到NPU节点')
    parser.add_argument('--input', required=True, help='JSON配置文件路径')
    parser.add_argument('--source-dir', required=True, help='源文件目录')
    parser.add_argument('--dest-dir', required=True, help='目标目录路径')

    args = parser.parse_args()

    # 规范化路径
    source_dir = os.path.abspath(args.source_dir)
    dest_dir = args.dest_dir.rstrip('/')  # 去除末尾的斜杠

    # 检查源目录是否存在
    if not os.path.isdir(source_dir):
        print(f"错误: 源目录 {source_dir} 不存在")
        exit(1)

    # 执行主函数
    auto_scp(args.input, source_dir, dest_dir)

```

将上述内容保存为 `auto-scp.py`。执行：

```BASH
python3 auto-scp.py --input npu-levels.json --source-dir ./segments  --dest-dir /root/workdir/data/input-file/
```

#### 推理主程序（镜像部分）

```python
import cv2
import numpy as np
import torch
import argparse
import os
from glob import glob
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


def infer_video(video_path, model, labels_dict, cfg, output_file_path):
    """视频推理并保存为 output_file_path"""
    # 读入视频
    cap = cv2.VideoCapture(video_path)
    # 获取原视频参数（帧率、分辨率）
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 创建视频写入对象（输出到output.mp4）
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 确保你的OpenCV支持该编码
    writer = cv2.VideoWriter(output_file_path, fourcc, fps, (width, height))

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
    print("视频已保存为 ", output_file_path)

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


def main():
    # 参数设置
    parser = argparse.ArgumentParser(description="Process video files in directory")
    parser.add_argument("--input", type=str, required=True, help="Input directory containing video files")
    parser.add_argument("--output", type=str, required=True, help="Output directory path")
    args = parser.parse_args()
    input_dir = args.input
    output_dir = args.output

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 模型存放位置
    model_path = 'yolo.om'
    label_path = './coco_names.txt'

    # 初始化推理模型
    model = InferSession(0, model_path)
    labels_dict = get_labels_from_txt(label_path)

    # 获取目录中所有视频文件
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv']  # 支持的视频格式
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob(os.path.join(input_dir, ext)))

    # 处理每个视频文件
    for input_file_path in video_files:
        input_filename = os.path.basename(input_file_path)
        output_filename = f"output_{input_filename}"
        output_file_path = os.path.join(output_dir, output_filename)

        print(f"Processing: {input_file_path}")
        infer_video(input_file_path, model, labels_dict, cfg, output_file_path)
        print(f"Saved to: {output_file_path}")


if __name__ == "__main__":
    main()

```

之后调用的时候也是，`--input` 指定输入文件的目录，`--output` 指定输出文件所在的目录。比如：

```bash
python3 ./main.py --input /root/workdir/data/input-file/ --output /root/workdir/data/output-file/
```

在容器中就用：

```bash
python3 ./main.py --input video-data/input-file/ --output video-data/output-file/
```

打包业务包：

```bash
tar zcvf yolov5.tgz coco_names.txt main.py requirements.txt yolo.om det_utils.py
```

#### k8s infer-job 声明文件

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ascend-infer-job
spec:
  template:
    metadata:
      labels:
        app: ascend-infer-job
    spec:
      nodeName: atlas1
      hostNetwork: true  # 相当于 --network host
      hostPID: true  # 相当于 --pid=host
      securityContext:
        runAsUser: 1000
        runAsGroup: 1000
      containers:
      - name: ascend-infer
        image: ascend-infer:0411
        imagePullPolicy: Never
        # command: ["/bin/bash", "-c", "sleep infinity"]  # 无限睡眠
        securityContext:
          privileged: true  # 可能需要特权模式来访问设备
        volumeMounts:
        - name: video-data
          mountPath: /home/AscendWork/video-data/
        - name: sys-version
          mountPath: /etc/sys_version.conf
          readOnly: true
        - name: hdc-basic
          mountPath: /etc/hdcBasic.cfg
          readOnly: true
        - name: libaicpu-processer
          mountPath: /usr/lib64/libaicpu_processer.so
          readOnly: true
        - name: libaicpu-prof
          mountPath: /usr/lib64/libaicpu_prof.so
          readOnly: true
        - name: libaicpu-sharder
          mountPath: /usr/lib64/libaicpu_sharder.so
          readOnly: true
        - name: libadump
          mountPath: /usr/lib64/libadump.so
          readOnly: true
        - name: libtsd-eventclient
          mountPath: /usr/lib64/libtsd_eventclient.so
          readOnly: true
        - name: libaicpu-scheduler
          mountPath: /usr/lib64/libaicpu_scheduler.so
          readOnly: true
        - name: libcrypto
          mountPath: /usr/lib64/libcrypto.so.1.1
          readOnly: true
        - name: libyaml
          mountPath: /usr/lib64/libyaml-0.so.2
          readOnly: true
        - name: libdcmi
          mountPath: /usr/lib64/libdcmi.so
          readOnly: true
        - name: libmpi-dvpp-adapter
          mountPath: /usr/lib64/libmpi_dvpp_adapter.so
          readOnly: true
        - name: aicpu-kernels
          mountPath: /usr/lib64/aicpu_kernels/
          readOnly: true
        - name: npu-smi
          mountPath: /usr/local/sbin/npu-smi
          readOnly: true
        - name: libstackcore
          mountPath: /usr/lib64/libstackcore.so
          readOnly: true
        - name: libunified-timer
          mountPath: /usr/lib64/libunified_timer.so
        - name: libdp
          mountPath: /usr/lib64/libdp.so
        - name: libtensorflow
          mountPath: /usr/lib64/libtensorflow.so
        - name: ascend-driver-lib64
          mountPath: /usr/local/Ascend/driver/lib64
          readOnly: true
        - name: slogd
          mountPath: /var/slogd
          readOnly: true
        - name: dmp-daemon
          mountPath: /var/dmp_daemon
          readOnly: true
# 从这里分开挂载-----------------------------------
        - name: upgrade
          mountPath: /dev/upgrade
        - name: davinci0
          mountPath: /dev/devinci0
        - name: davinci-manager
          mountPath: /dev/davinci_manager
        - name: vdec
          mountPath: /dev/vdec
        - name: vpc
          mountPath: /dev/vpc
        - name: pngd
          mountPath: /dev/pngd
        - name: venc
          mountPath: /dev/venc
        - name: sys
          mountPath: /dev/sys
        - name: svm0
          mountPath: /dev/svm0
        - name: acodec
          mountPath: /dev/acodec
        - name: ai
          mountPath: /dev/ai
        - name: ao
          mountPath: /dev/ao
        - name: hdmi
          mountPath: /dev/hdmi
        - name: ts-aisle
          mountPath: /dev/ts_aisle
        - name: dvpp-cmdlist
          mountPath: /dev/dvpp_cmdlist
      volumes:
      - name: video-data
        hostPath:
          path: /root/workdir/data/
          type: Directory  # 目录
      - name: sys-version
        hostPath:
          path: /etc/sys_version.conf
          type: File  # 明确指定为文件类型
      - name: hdc-basic
        hostPath:
          path: /etc/hdcBasic.cfg
          type: File
      - name: libaicpu-processer
        hostPath:
          path: /usr/lib64/libaicpu_processer.so
          type: File
      - name: libaicpu-prof
        hostPath:
          path: /usr/lib64/libaicpu_prof.so
          type: File
      - name: libaicpu-sharder
        hostPath:
          path: /usr/lib64/libaicpu_sharder.so
          type: File
      - name: libadump
        hostPath:
          path: /usr/lib64/libadump.so
          type: File
      - name: libtsd-eventclient
        hostPath:
          path: /usr/lib64/libtsd_eventclient.so
          type: File
      - name: libaicpu-scheduler
        hostPath:
          path: /usr/lib64/libaicpu_scheduler.so
          type: File
      - name: libcrypto
        hostPath:
          path: /usr/lib/aarch64-linux-gnu/libcrypto.so.1.1
          type: File
      - name: libyaml
        hostPath:
          path: /usr/lib/aarch64-linux-gnu/libyaml-0.so.2.0.6
          type: File
      - name: libdcmi
        hostPath:
          path: /usr/lib64/libdcmi.so
          type: File
      - name: libmpi-dvpp-adapter
        hostPath:
          path: /usr/lib64/libmpi_dvpp_adapter.so
          type: File
      - name: aicpu-kernels
        hostPath:
          path: /usr/lib64/aicpu_kernels/
          type: Directory  # 指定为目录类型
      - name: npu-smi
        hostPath:
          path: /usr/local/sbin/npu-smi
          type: File
      - name: libstackcore
        hostPath:
          path: /usr/lib64/libstackcore.so
          type: File
      - name: libunified-timer
        hostPath:
          path: /usr/lib64/libunified_timer.so
          type: Directory
      - name: libdp
        hostPath:
          path: /usr/lib64/libdp.so
          type: File
      - name: libtensorflow
        hostPath:
          path: /usr/lib64/libtensorflow.so
          type: File
      - name: ascend-driver-lib64
        hostPath:
          path: /usr/local/Ascend/driver/lib64
          type: Directory
      - name: slogd
        hostPath:
          path: /var/slogd
          type: File
      - name: dmp-daemon
        hostPath:
          path: /var/dmp_daemon
          type: File
# 从这里分开挂载--------------------------
      - name: upgrade
        hostPath:
          path: /dev/upgrade
          type: CharDevice  # 指定为字符设备
      - name: davinci0
        hostPath:
          path: /dev/davinci0
          type: CharDevice
      - name: davinci-manager
        hostPath:
          path: /dev/davinci_manager_docker  # 注意源路径不同
          type: CharDevice
      - name: vdec
        hostPath:
          path: /dev/vdec
          type: CharDevice
      - name: vpc
        hostPath:
          path: /dev/vpc
          type: CharDevice
      - name: pngd
        hostPath:
          path: /dev/pngd
          type: CharDevice
      - name: venc
        hostPath:
          path: /dev/venc
          type: CharDevice
      - name: sys
        hostPath:
          path: /dev/sys
          type: CharDevice
      - name: svm0
        hostPath:
          path: /dev/svm0
          type: CharDevice
      - name: acodec
        hostPath:
          path: /dev/acodec
          type: CharDevice
      - name: ai
        hostPath:
          path: /dev/ai
          type: CharDevice
      - name: ao
        hostPath:
          path: /dev/ao
          type: CharDevice
      - name: hdmi
        hostPath:
          path: /dev/hdmi
          type: CharDevice
      - name: ts-aisle
        hostPath:
          path: /dev/ts_aisle
          type: CharDevice
      - name: dvpp-cmdlist
        hostPath:
          path: /dev/dvpp_cmdlist
          type: CharDevice
      restartPolicy: Never  # Job 必须设置为 Never 或 OnFailure
```

将上述文件保存为 `ascend-infer-job.yaml`。

#### 调用 k8s 执行任务

```python
import json
import datetime
import re
import argparse
import subprocess
import os
import sys
import time
from kubernetes import client, config, utils
from kubernetes.client import ApiException


def check_jobs_complete(namespace='default'):
    """
    检查指定命名空间中的所有Jobs是否都已完成

    :param namespace: 要检查的命名空间，如果为None则检查所有命名空间
    :return: 如果所有Jobs都完成返回True，否则返回False
    """
    # 加载kube配置
    try:
        config.load_kube_config()  # 用于本地开发环境
    except:
        config.load_incluster_config()  # 用于集群内部运行

    batch_v1 = client.BatchV1Api()

    # 获取Jobs列表
    if namespace:
        jobs = batch_v1.list_namespaced_job(namespace)
    else:
        jobs = batch_v1.list_job_for_all_namespaces()

    all_complete = True

    for job in jobs.items:
        job_name = job.metadata.name
        namespace = job.metadata.namespace

        # 检查Job的状态
        if job.status.succeeded is None or job.status.succeeded < job.spec.completions:
            print(f"Job {namespace}/{job_name} is not complete (succeeded: {job.status.succeeded or 0}/{job.spec.completions})")
            all_complete = False
        else:
            print(f"Job {namespace}/{job_name} is complete")

    return all_complete

# 等价于 kubectl delete -f ${filename}
def delete_k8s_resource(filename):
    """
    使用kubectl delete -f命令删除指定的Kubernetes资源文件。
    """
    # 构建命令参数列表（避免shell注入）
    command = ['kubectl', 'delete', '-f', filename]

    # 执行命令并检查结果
    subprocess.run(command, check=True)


def monitor_jobs_and_delete_file(namespace, filename, interval):
    """
    持续监测Jobs直到完成，然后删除指定文件

    :param namespace: 要监测的命名空间
    :param filename: 要删除的文件名
    :param interval: 检查间隔时间(秒)
    """
    print(f"开始监测Jobs，完成后将删除文件: {filename}")

    while True:
        try:
            if check_jobs_complete(namespace):
                print("所有Jobs已完成，准备删除文件...")
                delete_k8s_resource(filename)
                try:
                    os.remove(filename)
                    print(f"文件 {filename} 已成功删除")
                except FileNotFoundError:
                    print(f"文件 {filename} 不存在，无需删除")
                except Exception as e:
                    print(f"删除文件时出错: {str(e)}")
                break
            else:
                print(f"Jobs未全部完成，等待...")
                time.sleep(interval)
        except Exception as e:
            print(f"监测Jobs时出错: {str(e)}")
            print(f"等待{interval}秒后重试...")
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description='Generate Kubernetes jobs with unique names')
    parser.add_argument('--json', type=str, required=True, help='NPU levels JSON config path')
    parser.add_argument('--yaml', type=str, required=True, help='Original YAML template path')
    args = parser.parse_args()

    # 文件验证
    for path in [args.json, args.yaml]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

    # 读取配置
    with open(args.json, 'r') as f:
        nodes = json.load(f).keys()

    with open(args.yaml, 'r') as f:
        yaml_template = f.read()

    # 生成带编号的配置
    job_sections = []
    for i, node in enumerate(nodes, 1):
        # 同时替换nodeName和metadata.name
        modified = yaml_template
        modified = re.sub(
            r'^(\s*name:\s*)(\S+)$',
            rf'\1\2-{i}',  # 在原有名称后添加编号
            modified,
            flags=re.MULTILINE,
            count=1  # 只替换第一个匹配项（metadata部分）
        )
        modified = re.sub(
            r'nodeName:\s*\S+',
            f'nodeName: {node}',
            modified
        )
        job_sections.append(modified)

    # 生成文件名并写入
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = f"ascend-infer-job-{timestamp}.yaml"
    with open(output_file, 'w') as f:
        f.write('\n---\n'.join(job_sections))

    # 执行kubectl
    kubectl_cmd = ['kubectl', 'apply', '-f', output_file]
    result = subprocess.run(kubectl_cmd, check=True, capture_output=True, text=True)

    print(f"Successfully applied jobs:\n{result.stdout}")

    # 检查 jobs 是否完成
    namespace = 'default'
    monitor_jobs_and_delete_file(namespace, output_file, 5)



if __name__ == "__main__":
    main()

```

让 k8s 启动 pod 去执行任务，并且执行完任务之后清理文件、Job 等资源。

将上述内容保存为 `patch-k8s.py`。调用方式：

```bash
python3 patch-k8s.py --json ./npu-levels.json --yaml ./ascend-infer-job.yaml
```

#### 收集并合并视频

```python
import argparse
import os
import glob
import cv2
import sys
import json
import subprocess

def collect_results(json_file_path):
    # 创建segments目录（如果不存在）
    os.makedirs("segments", exist_ok=True)

    # 读取JSON文件
    with open(json_file_path, "r") as f:
        data = json.load(f)

    # 遍历每个节点
    for node in data:
        filename = data[node]["filename"]
        remote_file = f"{node}:/root/workdir/data/output-file/output_{filename}"
        local_dir = "segments/"

        # 构造SCP命令
        command = ["scp", remote_file, local_dir]

        print(f"正在复制 {remote_file} 到 segments...")
        try:
            # 执行SCP命令
            subprocess.run(command, check=True)
            print(f"成功复制 {remote_file}")
        except subprocess.CalledProcessError as e:
            print(f"错误：复制 {remote_file} 失败，错误信息：{str(e)}")

def merge_videos(input_files, output_dir):
    """
    合并多个视频片段为一个完整视频

    参数:
        input_files: 输入视频文件列表
        output_dir: 合并后的输出目录
    """
    if not input_files:
        raise ValueError("没有找到任何视频文件")

    print(f"找到 {len(input_files)} 个视频片段:")
    for f in input_files:
        print(f"  {f}")

    # 生成输出文件名
    first_file = input_files[0]
    base_name = os.path.basename(first_file).replace('output_', '', 1)
    if '_' in base_name:
        base_part = base_name.split('_')[0]
        output_filename = f"{base_part}_output.mp4"
    else:
        output_filename = 'output_' + base_name

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    # 读取第一个视频获取参数
    sample = cv2.VideoCapture(first_file)
    fps = sample.get(cv2.CAP_PROP_FPS)
    width = int(sample.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(sample.get(cv2.CAP_PROP_FRAME_HEIGHT))
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    sample.release()

    # 创建输出视频写入器
    out = cv2.VideoWriter(output_path, codec, fps, (width, height))

    # 逐个读取并写入视频片段
    for input_file in input_files:
        print(f"正在处理: {input_file}")
        cap = cv2.VideoCapture(input_file)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        cap.release()

    out.release()
    print(f"\n视频合并完成: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="合并多个视频片段为一个完整视频")
    parser.add_argument("--input-dir", required=True, help="输入目录路径")
    parser.add_argument("--json", required=True, help="JSON配置文件路径")
    parser.add_argument("--output-dir", required=True, help="合并后的输出目录")

    args = parser.parse_args()

    collect_results(args.json)

    # 读取JSON配置
    with open(args.json, "r") as f:
        data = json.load(f)

    # 收集输入文件列表
    input_files = []
    for node in data:
        filename = data[node]["filename"]
        file_path = os.path.join(args.input_dir, f"output_{filename}")
        if not os.path.exists(file_path):
            print(f"警告：文件 {file_path} 不存在，跳过")
            continue
        input_files.append(file_path)

    if not input_files:
        raise ValueError("没有找到任何有效输入文件")

    try:
        merge_videos(input_files, args.output_dir)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

```

将上述文件保存为 `collect_and_merge_video.py`。使用方式：

```bash
python3 collect_and_merge_video.py --input-dir ./segments/ --json npu-levels.json --output-dir ./full-videos
```

之后就可以根据 `input-dir` 和 `json` 参数中指定的所有文件生成一个完整的 `output_racing.mp4` 到 `--output-dir` 目录下。

#### 总体的 run.sh

```bash
#!/bin/bash

# 获取节点的名称和算力的对应信息，并保存为 npu-levels.json 文件
bash generate-npu-levels.sh

# 切分视频
python3 ./split-video.py     --input full-videos/racing.mp4     --output ./segments/     --npu-json npu-levels.json

# 将要处理的视频分发给工作节点的 /root/workdir/data/input-file 目录
python3 auto-scp.py \
  --input npu-levels.json \
  --source-dir ./segments \
  --dest-dir /root/workdir/data/input-file/

# 让 k8s 启动 pod 去执行任务，并且执行完任务之后清理文件、Job
python3 patch-k8s.py     --json ./npu-levels.json     --yaml ./ascend-infer-job.yaml

# 收集结果，并将结果进行合并
python3 collect_and_merge_video.py --input-dir ./segments/ --json npu-levels.json --output-dir ./full-videos

```

初始目录树：

```python
.
├── ascend-infer-job.yaml
├── auto-scp.py
├── collect_and_merge_video.py
├── full-videos
│   └── racing.mp4
├── generate-npu-levels.sh
├── npu-levels.json
├── patch-k8s.py
├── run.sh
├── segments
└── split-video.py
```

运行 `bash run.sh` 之后的目录树：

```python
.
├── ascend-infer-job.yaml
├── auto-scp.py
├── collect_and_merge_video.py
├── full-videos
│   ├── racing.mp4
│   └── racing_output.mp4
├── generate-npu-levels.sh
├── npu-levels.json
├── patch-k8s.py
├── run.sh
├── segments
│   ├── output_racing_1.mp4
│   ├── output_racing_2.mp4
│   ├── racing_1.mp4
│   └── racing_2.mp4
└── split-video.py
```

后序，如果要处理其他的视频文件，只需要更改 `run.sh` 中的 `--input full-videos/racing.mp4` 中的 `racing.mp4` 为其他的视频文件即可。





























