# Atlas 问题解决（2）

## 12. 测试 yolo 模型运行时间

测试方式：直接用官方提供的 yolov5 模型处理 racing.mp4 视频。

racing.mp4 是昇腾官网上 yolo 的 demo 案例中使用的视频，视频时长 8.96 秒，分辨率为 1920*1080，帧率为 30fps。

![image-20250422151340754](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250422151340754.png)

### 运行时间统计

物理机中运行：

| 测试               | 20TOPS | 8TOPS  |
| ------------------ | ------ | ------ |
| 加载模型，准备环境 | 4.3 秒 | 7.1 秒 |
| 处理单个视频       | 31 秒  | 53 秒  |

容器中运行：

| 测试               | 20TOPS | 8TOPS  |
| ------------------ | ------ | ------ |
| 加载模型，准备环境 | 3.8 秒 | 6.4 秒 |
| 处理单个视频       | 12 秒  | 20 秒  |

这就比较奇怪了。。。为什么容器中反而运行更快？

通过在处理的时候，在另一个 shell 中通过 `npu-smi` 命令查看 AI 占用率，发现物理机的 AI 占用率最高在 14% 左右，而且是忽高忽低的；但是容器中运行的时候，AI 占用率最高可以到 29% 左右，而且占用率一直比较高，在 14% 到 28% 之间跳变。但是物理机中 AI 占用率会经常掉到 2%、3%。

不知道是一开始 nnrt 就是坏的，还是后面我给配错了。现在执行一下 A2 刚安装好的时候，官方给的 demo：

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

这时候，在 20TOPS 的机器上处理一个 racing.mp4 的时间是 28 秒左右。减去通过每一帧生成一个 output 视频的时间，发现这种直接在 jupyter 中执行官方 demo 的方式和我们直接在物理机中执行代码的效果是一样的。

这让我想到是不是我的 torch_npu 或者是其他的组件没有安装好？

### 排查 torch_npu 问题

在物理机和容器中分别执行如下命令，看 torch_npu 是否安装好了：

```bash
python3 -c "import torch;import torch_npu;print(torch_npu.npu.is_available())"
```

在物理机中，直接显示：

```bash
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'torch_npu'
# 找不到这个模块！
```

在容器中，执行的时候显示：

```bash
ImportError: libhccl.so: cannot open shared object file: No such file or directory. Please check that the cann package is installed. Please run 'source set_env.sh' in the CANN installation path.
# 似乎找不到 cann 相关的库，执行 set_env.sh 或许能行
```

之后再容器中执行了 `/usr/share/Ascend/nnrt/set_env.sh` 也不行呀！还是报一样的错误。

### 尝试重新安装 torch_npu

- Python 版本：3.9.2
- PyTorch 版本：2.1.0
- torch_npu 插件版本：6.0.0
- torchvision 版本：0.16.0

**【物理机】**

安装 2.1.0 版本的 pytorch：

```bash
# 下载安装包
wget https://download.pytorch.org/whl/cpu/torch-2.1.0-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
# 安装
pip3 install torch-2.1.0-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
```

安装 torch_npu 插件：

```bash
# 下载插件包
wget https://gitee.com/ascend/pytorch/releases/download/v6.0.0-pytorch2.1.0/torch_npu-2.1.0.post10-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
# 安装命令
pip3 install torch_npu-2.1.0.post10-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
```

同时，安装了新版本的 torch，torchvision 也要重新安装，否则会报错：

```bash
pip install torchvision==0.16.0 -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

之后物理机中执行如下命令来验证：

```bash
python3 -c "import torch;import torch_npu;print(torch_npu.npu.is_available())"
```

输出 `True`。

> 注意：上面这个版本的 pytorch 实际上对应的 CANN 版本是 8.0.0 版本的，但是 Atlas 200I DK A2 现在自带的 ascend-toolkit 中的 CANN 还是 7.0.0 版本的。尝试升级 7.0.0 版本，但是失败了，因为没有权限（只有商业用户可以下载）（25-4-22）。
>
> 先这样尝试着，过段时间再看看 8.0.0 版本的软件是否开放了。

**【容器】**

但是在容器中使用上面的方式构建镜像之后，执行验证的命令，输出：

```bash
ImportError: cannot import name 'DefaultDeviceType' from 'torch.utils.checkpoint' (/usr/local/lib/python3.9/site-packages/torch/utils/checkpoint.py)
```

从官网看，似乎是因为 torch 和 torch_npu 之间的版本兼容的问题。但是我的版本就是刚才查的，应该是没有问题的。所以最后只能再尝试更改一下 CANN 的版本，使用 8.0.0 版本的 CANN 试一下。

后来发现版本不兼容的问题出在：构建镜像的时候，先安装了 torch 和 torch-vision 的自定义的版本，后面又按照 requirements.txt 的版本声明安装了一次。将这个问题修正之后，在容器中导入 `torch_npu` 包，又出现了别的问题：

```bash
ImportError: libhccl.so: cannot open shared object file: No such file or directory
```

后来发现通过在启动容器的时候加上一些参数，可以让 `import torch` 的时候不报错：

```bash
# 直接在启动容器的时候将最全的这个动态链接库链接进去
-v /usr/local/Ascend/ascend-toolkit/7.0/aarch64-linux/lib64:/usr/local/Ascend/nnrt/latest/aarch64-linux/lib64 \
```

此外，因为 Ascend 的东西启动起来，需要 python 的 yaml 包，但是默认还没有安装，所以可以通过安装 yaml 包来解决对应的报错：

```bash
pip install pyyaml
```

### 尝试自行编译 torch-npu 插件

在 [Gitee](https://gitee.com/ascend/pytorch/tree/v2.1.0-7.0.0/#%E6%98%87%E8%85%BE%E8%BE%85%E5%8A%A9%E8%BD%AF%E4%BB%B6) 上看到，我们容器中的 CANN 7.0.0 对应的 torch 版本：2.1.0。

![image-20250423101155197](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250423101155197.png)

之后跟着网站的内容，从源码编译一次 pytorch。

但是编译完之后，安装自己编译的包，导入 `torch_npu` 包的时候，爆出警告：

```bash
/usr/local/miniconda3/lib/python3.9/site-packages/torch_npu/dynamo/__init__.py:18: UserWarning: Register eager implementation for the 'npu' backend of dynamo, as torch_npu was not compiled with torchair.
  warnings.warn(
```

遂放弃。

### 直接使用官方的镜像？

问题似乎又回到容器中的 CANN 安装不正确，因为容器中的 CANN 的 aarch64-linux 中的 lib64 中总是比物理机中少一些需要的库，比如 hccl 之类的动态链接库。

实在是难以解决，但是今天看到官方推出了 pytorch 的镜像，之后再使用容器镜像，可以直接使用官方的 pytorch 镜像：[网站](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/81RC1alpha002/softwareinst/instg/instg_0013.html?Mode=DockerIns&OS=Ubuntu&Software=cannToolKit)

![image-20250423115844848](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250423115844848.png)

但是这个镜像下面提到，使用这个镜像的一个条件是，设备中需要有 910b 芯片，所以放弃。

### 最后的解决方式

之前构建镜像的时候，先安装了指定版本的 pytorch，之后又安装 requirements.txt 安装了这个里面的 torch，导致前面安装的 torch 和 torchvision 版本被覆盖。将这个问题解决。

另一个是，如果要导入 torch_npu，还是会报错，因为其中用到了一些库，但是容器中没有。此时我想到两种解决方法：

- 制作镜像的时候使用 ascend-toolkit 制作。
- 在启动容器的时候加入参数：`-v /usr/local/Ascend/ascend-toolkit/7.0/aarch64-linux/lib64:/usr/local/Ascend/nnrt/latest/aarch64-linux/lib64`。就是把物理机上的这个库直接链接到容器中。

最后使用的 dockerfile：

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

# 安装 2.1.0 版本的 pytorch
COPY torch-2.1.0-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl .
RUN pip3 install torch-2.1.0-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
# 安装 torch_npu 插件
COPY torch_npu-2.1.0.post10-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl .
RUN pip3 install torch_npu-2.1.0.post10-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl
# 安装 0.16.0 的 torchvision
RUN pip install torchvision==0.16.0 -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 换源
COPY sources.list /etc/apt/sources.list
# 安装 libgl 库，安装 python 项目依赖
RUN apt-get update && apt-get install -y libgl1
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 安装 ais_bench 库
COPY aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl .
COPY ais_bench-0.0.2-py3-none-any.whl .
RUN pip3 install aclruntime-0.0.2-cp39-cp39-linux_aarch64.whl
RUN pip3 install ais_bench-0.0.2-py3-none-any.whl

# torch_npu 特别需要的：pyyaml 库
RUN pip3 install pyyaml

# 设置环境变量
RUN . /usr/local/Ascend/nnrt/set_env.sh && chmod 755 yolo.om

# -------------------------------------------------------------------


USER 1000
CMD ["bash", "/home/AscendWork/run.sh"]
```

## 13. A2 部署 TransVG

### CPU 推理脚本

```python
import argparse
import onnxruntime as ort
import numpy as np
from PIL import Image  # Python Imaging Library 的一部分，通常指 Pillow 库。支持广泛的图像格式，同时提供了强大的图像处理和操作功能。
from torchvision import transforms  # transforms 模块提供了常用的图像变换操作，如裁剪、缩放、归一化等。
import torchvision.transforms.functional as F  # F 提供了一些函数式接口，允许对单个图像执行低级别的操作。
from transformers import BertTokenizer  # Hugging Face 的 transformers 库的一部分，BertTokenizer 用于加载预训练的 BERT 模型分词器。它能够将文本转换成 BERT 模型可以理解的格式，即词汇索引序列。
import time
from tqdm import tqdm  # tqdm 是一个快速、可扩展的进度条库，适用于 Python 和 CLI 环境。可以实时显示循环或过程的进度条。


# --- 图像预处理 ---
# image_path 是输入图像的路径
# imsize 是图像的尺寸
def preprocess_image(image_path, imsize=640):
    # 将图像转换为 RGB 模式，这样可以确保图像以红、绿、蓝三通道的形式被处理，即使原始图像有不同的色彩模型（如灰度图或 CMYK）
    img = Image.open(image_path).convert('RGB')

    # 基本的尺寸调整和转换为 Tensor
    # 使用 pytorch 的 transforms.Compose 方法组合一系列图像变换操作，使得这些操作可以按顺序应用于图像。
    transform = transforms.Compose([
        transforms.Resize(imsize), # 调整图像大小，使得较短的一边等于 imsize（在这个例子中默认是 640 像素），而另一边按照原始比例进行缩放。
        transforms.CenterCrop(imsize), # 从图像的中心裁剪出一个尺寸为 imsize * imsize 的正方形区域。进一步确保输出图像是正方形，并且具有指定的像素尺寸。
        transforms.ToTensor(), # 将图像转换为 Pytorch 的 Tensor 格式，并调整其形状以适应深度学习模型的输入要求
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # 对图像进行标准化处理。给定的均值和标准差分别对应 RGB 三个通道，它们通常用于在 ImageNet 数据集上预训练的模型。此步骤有助于加快模型的收敛速度，并可能提高模型性能。
    ])

    # 将之前定义的所有变换操作应用到变量 img 上，结果是一个经过预处理的张量 img_tensor，它可以直接作为输入传递给神经网络模型。
    img_tensor = transform(img)

    # ONNX Runtime 需要 NumPy array
    # unsqueeze(0) 是在张良中添加一个新的维度，位置在最前面。numpy() 将 Pytorch 张量转换为 Numpy 数组。
    img_np = img_tensor.unsqueeze(0).numpy()

    # 创建了一个形状为 (1, imsize, imsize) 的三维 Numpy 数组 mask_np，并将其所有元素初始化为布尔值 False。
    # 这个数组可以用来作为掩码，例如在图像处理任务中标识感兴趣区域、忽略某些像素点等。
    # 使用 dtype=np.bool_ 指定了数组的数据类型为 bool 类型，ONNX Runtime 会处理。
    mask_np = np.zeros((1, imsize, imsize), dtype=np.bool_)

    # 返回图像张量和掩码
    # img_np 形状为 (1,3,imsize,imsize)，mask_np 形状为 (1,imsize,imsize)
    return img_np, mask_np

# --- 文本预处理 ---
# 使用 BERT tokenizer 对文本进行编码。
# text - 需要处理文本字符串
# tokenizer - 一个预训练的 BERT 分词器实例，用于将文本转换为模型可接受的输入格式
# max_query_len=20 - 文本的最大长度，最大为 20。如果超过这个长度，会被截断；如果不足，则会填充到这个长度。
def preprocess_text(text, tokenizer, max_query_len=20):
    # 使用提供的 tokenizer 对输入文本进行编码，并设置参数以控制填充和截断
    # return_tensors='pt' 标识返回 pytorch 张量
    # padding 和 truncation 确保所有输出具有相同的长度，通过填充或截断实现
    tokenized = tokenizer(text, return_tensors='pt', padding='max_length', truncation=True, max_length=max_query_len)

    # ONNX Runtime 需要 NumPy array 作为输入
    input_ids = tokenized['input_ids'].numpy()

    # 注意：原始模型的 text_mask 是 1 表示有效，0 表示 padding
    # BertTokenizer 的 attention_mask 也是 1 表示有效，0 表示 padding，所以可以直接用
    # 但 ONNX 导出时 NestedTensor 的 mask 是 True 表示 padding，False 表示有效
    # 需要确认导出时 text_mask 是如何处理的。如果导出时 text_mask = (attention_mask == 0)
    # 则这里需要转换： text_mask_np = (tokenized['attention_mask'] == 0).numpy()
    # 但根据 infer_test.py 导出的输入名称 'text_mask'，它很可能直接使用了 attention_mask。
    # 如果推理失败或结果错误，再尝试转换： text_mask_np = (tokenized['attention_mask'] == 0).numpy().astype(np.bool_)
    attention_mask = tokenized['attention_mask'].numpy().astype(np.int64) # 如果使用 np.bool_ 就会报错
    # 返回 token ids 和 attention mask (作为 text_mask)
    return input_ids, attention_mask

# --- 主函数 ---
def main(args):
    # 1. 加载 ONNX 推理会话
    print(f"Loading ONNX model from {args.model_path}")
    session_options = ort.SessionOptions()
    # 可以根据需要设置线程数等
    # session_options.intra_op_num_threads = 1
    # Check for CUDA availability and set providers accordingly
    available_providers = ort.get_available_providers()
    if 'CUDAExecutionProvider' in available_providers:
        print("CUDA is available. Using CUDAExecutionProvider.")
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] # CUDA first, then fallback to CPU
    else:
        print("CUDA not available. Using CPUExecutionProvider.")
        providers = ['CPUExecutionProvider']

    session = ort.InferenceSession(args.model_path, sess_options=session_options, providers=providers)
    print(f"Using ONNX Runtime provider: {session.get_providers()}")

    # 2. 获取并确认模型输入输出名称
    actual_input_names = [inp.name for inp in session.get_inputs()]
    actual_output_names = [out.name for out in session.get_outputs()]
    print("Actual Model Inputs:", actual_input_names)
    print("Actual Model Outputs:", actual_output_names)

    # --- 使用从模型获取的实际名称 ---
    # 假设顺序与 infer_test.py 导出时一致
    input_image_tensors_name = actual_input_names[0] # e.g., 'image_tensors'
    input_image_mask_name = actual_input_names[1]    # e.g., 'image_mask'
    input_text_tensors_name = actual_input_names[2]  # e.g., 'text_tensors'
    input_text_mask_name = actual_input_names[3]     # e.g., 'text_mask'
    output_name = actual_output_names[0]             # e.g., 'pred_bbox_cxcywh'

    # 3. 加载 Tokenizer
    print(f"Loading tokenizer: {args.bert_model}")
    # 使用与 infer_test.py 相同的设置
    tokenizer = BertTokenizer.from_pretrained(args.bert_model, do_lower_case=True)

    # 4. 预处理输入
    print(f"Preprocessing image: {args.image_path}")
    # 获取图像张量和图像掩码
    image_tensors_np, image_mask_np = preprocess_image(args.image_path, args.imsize)

    print(f"Preprocessing text: '{args.text_query}'")
    # 获取文本 token ids 和 attention mask (作为 text_mask)
    text_tensors_np, text_mask_np = preprocess_text(args.text_query, tokenizer, args.max_query_len)

    # 5. 准备输入字典 (使用正确的名称和全部 4 个输入)
    inputs = {
        input_image_tensors_name: image_tensors_np,
        input_image_mask_name: image_mask_np,
        input_text_tensors_name: text_tensors_np,
        input_text_mask_name: text_mask_np
    }

    print("Preheating inference for 1 times")
    for _ in tqdm(range(1), desc="Preheating Progress"):
        outputs = session.run([output_name], inputs)

    # 6. 执行推理
    print(f"Running inference for {args.run_iter} iterations...")
    inference_times = []
    for _ in tqdm(range(args.run_iter), desc="Inference Progress"):
        start_time = time.time()
        outputs = session.run([output_name], inputs)
        end_time = time.time()
        inference_times.append(end_time - start_time)

    # Calculate and print statistics
    inference_times_np = np.array(inference_times)
    avg_time = np.mean(inference_times_np)
    std_dev = np.std(inference_times_np)

    print(f"\nInference completed.")
    print(f"Average inference time: {avg_time:.4f} seconds")
    print(f"Standard deviation: {std_dev:.4f} seconds")
    pred_box = outputs[0] # 获取第一个输出

    # 7. 处理输出
    # 输出通常是 [batch_size, 4]，格式为 [cx, cy, w, h] 归一化坐标
    # 移除 batch 维度
    pred_box = pred_box[0]
    print(f"Predicted box (cx, cy, w, h): {pred_box}")

    # (可选) 将预测框转换为 xyxy 格式并反归一化到原始图像尺寸
    try:
        img_orig = Image.open(args.image_path)
        orig_w, orig_h = img_orig.size

        cx, cy, w, h = pred_box
        # 反归一化到原始图像尺寸
        # 注意：这里的反归一化假设预测框是相对于调整和裁剪后的 imsize * imsize 图像的
        # 如果要映射回原始图像，需要考虑 Resize 和 CenterCrop 的影响，会更复杂。
        # 这里我们先简化，假设是映射回 imsize * imsize 的坐标
        # 如果需要精确映射回原始尺寸，需要保存变换信息或使用更复杂的反向映射

        # 简化：映射回 imsize x imsize 坐标空间
        disp_w, disp_h = args.imsize, args.imsize
        x1 = (cx - w / 2) * disp_w
        y1 = (cy - h / 2) * disp_h
        x2 = (cx + w / 2) * disp_w
        y2 = (cy + h / 2) * disp_h

        print(f"Predicted box (x1, y1, x2, y2) in {disp_w}x{disp_h} coordinates: [{x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}]")

        # (可选) 在调整/裁剪后的图像上绘制边界框并显示/保存
        # 需要加载调整/裁剪后的图像用于显示
        display_transform = transforms.Compose([
             transforms.Resize(args.imsize),
             transforms.CenterCrop(args.imsize)
        ])
        img_display = display_transform(img_orig)

        from PIL import ImageDraw

        draw = ImageDraw.Draw(img_display)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        # img_display.show() # 在某些环境可能无法显示
        img_display.save(args.output_path)
        print(f"Output image saved to: {args.output_path}")


    except Exception as e:
        print(f"Could not perform post-processing or save the image: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser('TransVG ONNX inference script')
    # --- 输入参数 ---
    parser.add_argument('--model_path', default='./transvg.onnx', type=str,
                        help='Path to the ONNX model file')
    parser.add_argument('--image_path', required=True, type=str,
                        help='Path to the input image')
    parser.add_argument('--text_query', required=True, type=str,
                        help='Input text query')

    # --- 模型和预处理相关参数 (需要与导出时匹配) ---
    parser.add_argument('--imsize', default=640, type=int,
                        help='Image size used during training/exporting (must match transform)')
    parser.add_argument('--max_query_len', default=20, type=int,
                        help='Maximum query length for tokenizer')
    parser.add_argument('--bert_model', default='bert-base-uncased', type=str,
                        help='BERT model name for tokenizer')
    parser.add_argument('--output_path', default="onnx_result_image.png", type=str, help="save to where?")
    parser.add_argument('--run_iter', default=15, type=int, help="How many iters run in one launch")

    args = parser.parse_args()
    main(args)

```

执行脚本：

```bash
HF_ENDPOINT=https://hf-mirror.com

python onnx_infer.py --model_path ./transvg.onnx  --run_iter 1 --output_path ./result_image.png --image_path ../ln_data/other/images/mscoco/images/train2014/COCO_train2014_000000000077.jpg --text_query "skateboard" 
```

### 使用 atc 转换模型

```bash
atc --model=transvg.onnx --framework=5 --output=onnx_transvg --soc_version=Ascend310B1
```

失败，报错。



















