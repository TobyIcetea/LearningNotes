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
    # unsqueeze(0) 是在张量中添加一个新的维度，位置在最前面。numpy() 将 Pytorch 张量转换为 Numpy 数组。
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

python ./scripts/onnx_infer.py --model_path ./models/transvg.onnx  --run_iter 1 --output_path ./result_image.png --image_path ./datasets/COCO_train2014_000000000077.jpg --text_query "man on the left"
```

---

### 使用 atc 转换模型

```bash
atc --model=transvg.onnx --framework=5 --output=transvg --input_shape="image_tensors:1,3,640,640;image_mask:1,640,640;text_tensors:1,20;text_mask:1,20" --soc_version=Ascend310B1 --input_format=NCHW --log=info
```

失败，报错。

后来发现是因为内存不够用，于是按照官网的教程修改内存参数：

- 借助 **ulimit** 命令，在 atc 等内存消耗比较大的进程启动前设置内存使用上限，防止内存耗尽导致宕机。

    ```bash
    ulimit -v unlimited
    # 用于在当前 Shell 中取消对每个进程可以使用的虚拟内存大小的限制。
    ```

- 创建交换分区：

    ```bash
    # 创建一个大小为8G的swap分区。
    fallocate --length 8G /swapfile 
    # 修改文件权限。
    chmod 600 /swapfile
    # 创建swap分区。
    mkswap /swapfile
    # 挂载swap分区。
    swapon /swapfile
    # 执行命令查看分区是否创建成功。
    free -h
    # 重启之后这些操作就消失了
    ```

通过上面的命令，最后得到 288M 的 `converted_transvg.om`。

---

### 使用 CANN-onnxruntime 运行

使用 python 3.10 的环境：

```bash
conda activate python310
```

安装一些必要的包：

```bash
pip install Pillow==11.2.1
pip install transformers==4.51.3
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install onnxruntime-cann==1.20.0
pip install numpy==1.26.4
pip install onnx==1.18.0
```

之后用如下代码：

```python
import onnxruntime as ort
print(ort.get_available_providers())
```

输出：

```bash
['CANNExecutionProvider', 'CPUExecutionProvider']
```

说明此时 CANN 是可以用的。

执行脚本：

```bash
HF_ENDPOINT=https://hf-mirror.com python ./scripts/cann_onnxruntime_infer.py --model_path ./models/transvg.onnx  --run_iter 1 --output_path ./result_image.png --image_path ./datasets/COCO_train2014_000000000077.jpg --text_query "man on the left"
```

## 14. Pytorch 专题

### 安装 Pytorch 环境

torch：

```bash
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
```

torch_npu：

```bash
pip3 install pyyaml
pip3 install setuptools
pip3 install torch-npu==2.1.0.post12
```

### torch 常见报错

#### TASK_QUEUE_ENABLE

在 ipython 中执行：

```python
import torch
import torch_npu
```

中的 `torch_npu` 之后，发现如下警告信息：

```bash
/usr/local/miniconda3/envs/python310/lib/python3.10/site-packages/torch_npu/__init__.py:268: UserWarning: On the interactive interface, the value of TASK_QUEUE_ENABLE is set to 0 by default.                      Do not set it to 1 to prevent some unknown errors
  warnings.warn("On the interactive interface, the value of TASK_QUEUE_ENABLE is set to 0 by default. \
```

解决方法：实际上就是不要在 ipython 中执行，放在文件中执行就会好起来。

### 自行编译 torch-npu 插件

#### 环境

| 软件      | 版本         |
| --------- | ------------ |
| Python    | 3.10         |
| CANN      | 8.1.RC1      |
| torch     | 2.1.0        |
| torch-npu | 2.1.0.post12 |

#### 编译

```bash
git clone https://gitee.com/ascend/pytorch.git -b v2.1.0-7.0.0 --depth 1

cd pytorch/ci/docker/ARM/
docker build -t manylinux-builder:v1 .

# 物理机上的文件夹在 /root/workdir/compile-torch-npu/pytorch
docker run -it -v /root/workdir/compile-torch-npu/pytorch:/home/pytorch manylinux-builder:v1 bash

cd /home/pytorch
# 本次我们编译的是 python 3.10 的版本
bash ci/build.sh --python=3.10
```

最后会在 `pytorch/dist` 文件夹下生成文件 `torch_npu-2.1.0.post12+gita6024c1-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl`。

#### 安装

切换到 python310 的环境。执行 `pip install ./文件` 安装生成的文件。

### 测试

测试 NPU 是否可用：

```bash
python3 -c "import torch;import torch_npu;print(torch_npu.npu.is_available())"
```

输出：`True`。

测试 torch-npu 是否可用：

```python
import torch
import torch_npu

x = torch.randn(2, 2).npu()
y = torch.randn(2, 2).npu()
z = x.mm(y)

print(z)
```

输出：

```bash
..[W compiler_depend.ts:137] Warning: Warning: Device do not support double dtype now, dtype cast repalce with float. (function operator())
..tensor([[-0.0069,  0.8412],
        [ 1.4659, -1.0574]], device='npu:0')
```

### torch-npu 的作用

在导入 torch_npu 之前，只执行 `import torch`，之后执行：`device = torch.device("npu")`，会报错：

```bash
RuntimeError: Expected one of cpu, cuda, ipu, xpu, mkldnn, opengl, opencl, ideep, hip, ve, fpga, ort, xla, lazy, vulkan, mps, meta, hpu, mtia, privateuseone device type at start of device string: npu
```

意思是这个方法中的字段必须在这个枚举列表中，但是 `npu` 不在这个列表中。

但是在导入 `torch_npu` 之后，再执行 `device = torch.device("npu")` 就可以成功了。

看 `torch_npu` 的 `__init__.py` 代码可以看到以下几个调整的点：

1. PyTorch 预留了 `PrivateUse1` 机制（通过 `torch.utils.rename_privateuse1_backend`），允许第三方扩展自定义设备类型。`torch_npu` 利用这一机制完成以下操作：

    ```python
    torch.utils.rename_privateuse1_backend("npu")  # 将 "privateuse1" 重命名为 "npu"
    torch._register_device_module('npu', torch_npu.npu)  # 关联 NPU 的实现模块
    ```

2. 通过 `generate_methods_for_privateuse1_backend`，PyTorch 会为 `npu` 设备动态生成标准方法（如 `to('npu')`、`npu()` 等）：

    ```python
    torch.utils.generate_methods_for_privateuse1_backend(
        for_tensor=True, for_module=True, for_storage=True,
        unsupported_dtype=unsupported_dtype
    )
    ```

    这行代码使得 `torch.Tensor`、`torch.nn.Module` 等类自动支持 `npu` 设备。

3. ……

最终效果就是，`torch.device('npu')` 和 `tensor.to('npu')` 等操作变得可用，无需用户手动配置。

## 15. onnxruntime 专题

### 自行编译 onneruntime-cann

下载仓库中的源代码：

```bash
git clone https://github.com/microsoft/onnxruntime.git
```

需要安装cmake 3.26以上工具，否则报错。但是系统自带的cmake仅有3.22.1，所以需要我们用其他方式安装。

```bash
sudo apt-get update
sudo apt-get install ca-certificates gpg wget
test -f /usr/share/doc/kitware-archive-keyring/copyright ||
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null

echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ jammy main' | sudo tee /etc/apt/sources.list.d/kitware.list >/dev/null
sudo apt-get update

sudo apt-get install cmake
```

切换成 python310 的环境：

```bash
conda activate python310
```

在 onnxruntime 的目录下，执行命令：

```bash
./build.sh --config Release --build_shared_lib --parallel --compile_no_warning_as_error --use_cann --build_wheel --allow_running_as_root --skip_tests
```

过了大概五个小时编译成功：

```bash
......
adding 'onnxruntime_cann-1.23.0.dist-info/METADATA'
adding 'onnxruntime_cann-1.23.0.dist-info/WHEEL'
adding 'onnxruntime_cann-1.23.0.dist-info/entry_points.txt'
adding 'onnxruntime_cann-1.23.0.dist-info/top_level.txt'
adding 'onnxruntime_cann-1.23.0.dist-info/RECORD'
removing build/bdist.linux-aarch64/wheel
2025-05-20 19:14:57,714 build [INFO] - Build complete
```

查看编译结果：

```bash
cd build/Linux/Release/dist
ls
输出 onnxruntime_cann-1.23.0-cp310-cp310-linux_aarch64.whl
```

安装编译好的包：

```bash
pip install ./onnxruntime_cann-1.23.0-cp310-cp310-linux_aarch64.whl
```

### demo1 - pytorch 转 onnx

虚拟环境需要有 torch_npu 插件：

```bash
pip3 install pyyaml
pip3 install setuptools
pip3 install torch-npu==2.1.0.post12

pip install onnx
```

代码：

```python
import os
import torch
import numpy as np
import torch_npu
import torch.nn as nn
import torch.nn.functional as F

class MyModel(nn.Module):

    def __init__(self):
        super(MyModel, self).__init__()
        self.fc = nn.Linear(224, 10)

    def forward(self, x):
        x = self.fc(x)
        return x

if __name__ == "__main__":
    device = torch.device("npu")
    model = MyModel().to(device)
    torch_input = torch.randn(1, 224).to(device)
    model.eval()
    torch_output = model(torch_input)
    # save input to input.pt, output to output.pt
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    np.save("output/input.npy", torch_input.cpu().numpy()) 
    np.save("output/output.npy", torch_output.detach().cpu().numpy()) 

    input_args = (torch_input,)
    input_names = ["images"]
    output_names = ["logits"]
    with torch.no_grad():
        torch.onnx.export(
            model,
            f="output/model.onnx",
            args=input_args,
            input_names=input_names,
            output_names=output_names,
            opset_version=14,
        )
        print("model save ok in output/model.onnx")
```

输出：

```bash
model save ok in output/model.onnx

(python310) root@atlas:~/workdir/onnxruntime-test# tree
.
├── fusion_result.json
├── output
│   ├── input.npy
│   ├── model.onnx
│   └── output.npy
└── pytorch2onnx.py
```

### demo2 - CPU 推理

安装 onnxruntime-cann：

```bash
pip install onnxruntime-cann

(python310) root@atlas:~/workdir/onnxruntime-test# pip list | grep onnxruntime
onnxruntime-cann       1.23.0
```

脚本文件：

```python
import onnxruntime as ort
import numpy as np

options = ort.SessionOptions()
session = ort.InferenceSession(
    "output/model.onnx",
    sess_options=options,
    providers=[
        "CPUExecutionProvider",
    ],
)

image_input = np.load("output/input.npy")
logits = np.load("output/output.npy")
result = session.run(["logits"],{
    "images": image_input,
})
output = result[0]
diff_mean = np.mean(logits - output)
diff_max = np.max(np.abs(logits - output))
print("diff max: {}, diff mean:{}".format(diff_max, diff_mean))
```

运行结果：

```bash
(python310) root@atlas:~/workdir/onnxruntime-test# python ./cpu_infer.py
diff max: 2.384185791015625e-07, diff mean:1.974403929239088e-08
```

可以看出误差很低，基本忽略不计。

### demo3 - NPU 推理

第一次推理会将 CANNExecutionProvider 会将 onnx 自动转 om 模型，所以会有点慢，可以多运行几次。

推理脚本：

```python
import onnxruntime as ort
import numpy as np

options = ort.SessionOptions()
session = ort.InferenceSession(
    "output/model.onnx",
    sess_options=options,
    providers=[
        (
            "CANNExecutionProvider",
            {
                "device_id": 0,
                "arena_extend_strategy": "kNextPowerOfTwo",
                "npu_mem_limit": 20 * 1024 * 1024 * 1024,
                "op_select_impl_mode": "high_performance",
                "optypelist_for_implmode": "Gelu",
                "enable_cann_graph": True
            },
        ),
            "CPUExecutionProvider",
        ]
    )

image_input = np.load("output/input.npy")
logits = np.load("output/output.npy")
image_input_cann = ort.OrtValue.ortvalue_from_numpy(image_input, device_type="cann", device_id=0)
io_binding = session.io_binding()
io_binding.bind_ortvalue_input(name="images", ortvalue=image_input_cann)
io_binding.bind_output("logits", device_type="cann", device_id=0)
session.run_with_iobinding(io_binding)
output = io_binding.get_outputs()[0].numpy()
diff_mean = np.mean(logits - output)
diff_max = np.max(np.abs(logits - output))
print("diff max: {}, diff mean:{}".format(diff_max, diff_mean))
```

输出：

```bash
.diff max: 0.00027561187744140625, diff mean:-7.517934136558324e-05
```

从输出结果误差来看，npu这边由于只支持fp16,所以误差比cpu会大一些，严谨一些onnx导出时也应该用fp16，不过从结果来看，cann onnxruntime的运行是成功的。

### 运行前后文件结构对比

运行前：

```python
(python310) root@atlas:~/workdir/onnxruntime-test# tree
.
├── cpu_infer.py
├── fusion_result.json
├── npu_infer.py
├── output
│   ├── input.npy
│   ├── model.onnx
│   └── output.npy
└── pytorch2onnx.py
```

运行后：

```python
(python310) root@atlas:~/workdir/onnxruntime-test# tree
.
├── CANNExecutionProvider_main_graph_14361866660454871365_0_0_8422727188037755061.om
├── cpu_infer.py
├── kernel_meta
│   ├── ...这里有很多小的文件
├── npu_infer.py
├── output
│   ├── input.npy
│   ├── model.onnx
│   └── output.npy
└── pytorch2onnx.py
```

可以看到其中主要是多了 .om 这个模型。这就是 CANNExecutionProvider 执行的产物。

CANNExecutionProvider 执行的原理差不多就是，先将 Onnx 转换为 om 模型，再执行 om 模型。

### Onnxruntime-cann 运行 transvg 总结

onnxruntime-cann 这条路是可行的，可以用来运行一些基础的模型。但是在 transvg 上不行。可能是原模型有一些东西不太支持，也可能是因为这个插件做的还不是很完善。使用 onnxruntime 来运行毕竟也不是主流。

主流运行方式还是通过 atc 工具将 onnx 转换成 om 再去运行。

## 16. aclruntime 专题

### 安装 aclruntime

参见 [码云仓库](https://gitee.com/ascend/tools/tree/ec952b56d45be60becf2f5f2717db8cf09569502/ais-bench_workload/tool/ais_bench)。

其中分为两部分，一部分为 aclruntime，一部分为 ais_bench 推理程序包。

### 查看输入输出示例

例如就用我们之前导出的 transvg.om 模型：

```python
from ais_bench.infer.interface import InferSession

def main():
    session = InferSession(device_id=0, model_path="models/transvg.om")
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    print("inputs:", inputs)
    print("outputs:", outputs)
    for i, inp in enumerate(inputs):
        print(f"Input {i}: name={inp.name}, datatype={inp.datatype}, format={inp.format}, shape={inp.shape}, size={inp.size}, realsize={inp.realsize}")

    for i, out in enumerate(outputs):
        print(f"Input {i}: name={out.name}, datatype={out.datatype}, format={out.format}, shape={out.shape}, size={out.size}, realsize={out.realsize}")


if __name__ == '__main__':
    main()
```

之后就会输出：

```bash
inputs: [<aclruntime.tensor_desc object at 0xe7ffbe109e70>, <aclruntime.tensor_desc object at 0xe7ffbe109fb0>, <aclruntime.tensor_desc object at 0xe7ffbe109ff0>, <aclruntime.tensor_desc object at 0xe7ffbe10a030>]

outputs: [<aclruntime.tensor_desc object at 0xe7ffbe10a0b0>]

Input 0: name=image_tensors, datatype=dtype.float32, format=0, shape=[1, 3, 640, 640], size=4915200, realsize=4915200

Input 1: name=image_mask, datatype=dtype.bool, format=0, shape=[1, 640, 640], size=409600, realsize=409600

Input 2: name=text_tensors, datatype=dtype.int64, format=0, shape=[1, 20], size=160, realsize=160

Input 3: name=text_mask, datatype=dtype.int64, format=0, shape=[1, 20], size=160, realsize=160

Input 0: name=Sigmoid_4556:0:pred_bbox_cxcywh, datatype=dtype.float32, format=2, shape=[1, 4], size=16, realsize=16
```

其中：

| property     | type               | describe                                                     |
| ------------ | ------------------ | ------------------------------------------------------------ |
| **name**     | `str`              | 节点名称。                                                   |
| **datatype** | `aclruntime.dtype` | 节点接受tensor的数据类型。                                   |
| **format**   | `int`              | 节点接受tensor格式，0表示NCHW格式，1表示NHWC格式。           |
| **shape**    | `list[int]`        | 节点接受的tensor的shape。                                    |
| **size**     | `int`              | 节点接受的tensor的大小。                                     |
| **realsize** | `int`              | 节点接受的tensor的真实大小，针对动态 shape 动态分档场景 实际需要的大小。 |

### demo-运行一个模型

下载 Ascend 的 tools 仓库：

```bash
git clone https://gitee.com/ascend/tools.git
```

获取样例：

```bash
cd tools/ais-bench_workload/tool/ais_bench/api_samples

chmod 750 get_sample_datas.sh

./get_sample_datas.sh
```

转换完模型之后，进入目录：

```bash
cd interface_api_usage/api_infer
```

本次我们要运行的脚本是：`infer_api_static.py`。

直接运行的脚本有点问题，可以改成下面的代码：

```python
import numpy as np
from ais_bench.infer.interface import InferSession


def infer_api_static():
    device_id = 0
    model_path = "../../sampledata/add_model/model/add_model_bs1.om"
    # create session of om model for inference
    session = InferSession(device_id, model_path)
    
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    print("inputs:", inputs)
    print("outputs:", outputs)
    for i, inp in enumerate(inputs):
        print(f"Input {i}: name={inp.name}, datatype={inp.datatype}, format={inp.format}, shape={inp.shape}, size={inp.size}, realsize={inp.realsize}")

    for i, out in enumerate(outputs):
        print(f"Input {i}: name={out.name}, datatype={out.datatype}, format={out.format}, shape={out.shape}, size={out.size}, realsize={out.realsize}")
    
    # create new numpy data according inputs info
    shape0 = session.get_inputs()[0].shape
    ndata0 = np.full(shape0, 1).astype(np.float32)
    shape1 = session.get_inputs()[1].shape
    ndata1 = np.full(shape1, 1).astype(np.float32)
    feeds = [ndata0, ndata1]
    # execute inference, inputs is ndarray list and outputs is ndarray list
    outputs = session.infer(feeds, mode='static')
    print(f"outputs: {outputs}")

infer_api_static()
```

输出：

```bash
inputs: [<aclruntime.tensor_desc object at 0xe7ffc1e91470>, <aclruntime.tensor_desc object at 0xe7ffb8bd3270>]
outputs: [<aclruntime.tensor_desc object at 0xe7ffb815f930>]


Input 0: name=input1, datatype=dtype.float32, format=0, shape=[1, 3, 32, 32], size=12288, realsize=12288

Input 1: name=input2, datatype=dtype.float32, format=0, shape=[1, 3, 32, 32], size=12288, realsize=12288

Input 0: name=add1:0:output, datatype=dtype.float32, format=0, shape=[1, 3, 32, 32], size=12288, realsize=12288

outputs: [array([[[[2., 2., 2., ..., 2., 2., 2.],
         [2., 2., 2., ..., 2., 2., 2.],
         [2., 2., 2., ..., 2., 2., 2.],
......
         [2., 2., 2., ..., 2., 2., 2.]]]], dtype=float32)]
```

可以看到，如果直接输出 inputs，会发现 inputs 中有两个对象，但是对象的具体信息，还需要进一步查询。

在进一步的输出中，发现 `input1` 的数据类型是 `dtype.float32`，`input2` 的数据类型也是 `dtype.float32`，并且它们的形状都是 `[1, 3, 32, 32]`，输入的格式是 NCHW 格式。

所以输入的时候，我们是要输入两个 `float32` 的张量？下来具体看一下代码中是如何提供输入的：

```python
shape0 = session.get_inputs()[0].shape
ndata0 = np.full(shape0, 1).astype(np.float32)
shape1 = session.get_inputs()[1].shape
ndata1 = np.full(shape1, 1).astype(np.float32)
feeds = [ndata0, ndata1]
```

`ndata0` 和 `ndata1` 的构造方式都是一样的：

1. 先获取到模型的 `input` 的 `shape`。
2. 创建一个与输入形状相同的 `numpy` 的 `ndarray`，并用值 1 来填充。
3. 将数组类型转换为 `float32`。

之后再将所有的输入组合成一个列表 `feeds`，因为 `input` 中实际上只能传入一个 `feeds` 列表。

所以是不是说传入参数的时候就是传入一个 `feeds` 列表，然后在列表中按顺序传入所有的参数？

### TransVG 实践

修改之后的代码：

```python
from ais_bench.infer.interface import InferSession
from transformers import BertTokenizer
import numpy as np
from PIL import Image
from torchvision import transforms
from tqdm import tqdm
import time
import argparse

# --- 图像预处理 ---
def preprocess_image(image_path, imsize=640):
    # 将图像转换为 RGB 模式，这样可以确保图像以红、绿、蓝三通道的形式被处理，即使原始图像有不同的色彩模型（如灰度图或 CMYK）
    img = Image.open(image_path).convert('RGB')
    
    # 基本的尺寸调整和转换为 Tensor，使用 pytorch 的 transforms.Compose 方法组合一系列图像变换操作，使得这些操作可以按顺序应用于图像。
    transform = transforms.Compose([
        transforms.Resize(imsize), # 调整图像大小，使得较短的一边等于 imsize（在这个例子中默认是 640 像素），而另一边按照原始比例进行缩放。
        transforms.CenterCrop(imsize), # 从图像的中心裁剪出一个尺寸为 imsize * imsize 的正方形区域。进一步确保输出图像是正方形，并且具有指定的像素尺寸。
        transforms.ToTensor(), # 将图像转换为 Pytorch 的 Tensor 格式，并调整其形状以适应深度学习模型的输入要求
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # 对图像进行标准化处理。给定的均值和标准差分别对应 RGB 三个通道，它们通常用于在 ImageNet 数据集上预训练的模型。此步骤有助于加快模型的收敛速度，并可能提高模型性能。
    ])
    
    # 将之前定义的所有变换操作应用到变量 img 上，结果是一个经过预处理的张量 img_tensor，它可以直接作为输入传递给神经网络模型。
    img_tensor = transform(img) 
    
    # unsqueeze(0) 是在张量中添加一个新的维度，位置在最前面。numpy() 将 Pytorch 张量转换为 Numpy 数组。
    img_np = img_tensor.unsqueeze(0).numpy() 
    
    mask_np = np.zeros((1, imsize, imsize), dtype=np.bool_)

    # 返回图像张量和掩码
    # img_np 形状为 (1,3,imsize,imsize)，float32 类型
    # mask_np 形状为 (1,imsize,imsize)，bool 类型
    return img_np, mask_np

# --- 文本预处理 ---
# 使用 BERT tokenizer 对文本进行编码。
# tokenizer - 一个预训练的 BERT 分词器实例，用于将文本转换为模型可接受的输入格式
def preprocess_text(text, tokenizer, max_query_len=20):
    # 使用提供的 tokenizer 对输入文本进行编码，并设置参数以控制填充和截断
    # return_tensors='pt' 标识返回 pytorch 张量
    # padding 和 truncation 确保所有输出具有相同的长度，通过填充或截断实现
    tokenized = tokenizer(text, return_tensors='pt', padding='max_length', truncation=True, max_length=max_query_len)

    # 我们使用 numpy 的 ndarray 作为模型的输入
    input_ids = tokenized['input_ids'].numpy()

    attention_mask = tokenized['attention_mask'].numpy().astype(np.int64) # 如果使用 np.bool_ 就会报错

    # input_ids 形状为 (1, max_query_len)，int64 类型
    # attention_mask 形状为 (1, max_query_len)，int64 类型
    return input_ids, attention_mask 

def main():
    parser = argparse.ArgumentParser(description='transvg infer')
    # 添加必需的参数
    parser.add_argument('--image_path', type=str, required=True,
                       help='输入图像的路径')
    parser.add_argument('--text_query', type=str, required=True,
                       help='用于识别的文本查询')
    # 解析参数
    args = parser.parse_args()

    # 加载模型
    model_path = "models/transvg.om"
    session = InferSession(device_id=0, model_path=model_path)
    """
    Input 0: name=image_tensors, datatype=dtype.float32, format=0, shape=[1, 3, 640, 640], size=4915200, realsize=4915200
    Input 1: name=image_mask, datatype=dtype.bool, format=0, shape=[1, 640, 640], size=409600, realsize=409600
    Input 2: name=text_tensors, datatype=dtype.int64, format=0, shape=[1, 20], size=160, realsize=160
    Input 3: name=text_mask, datatype=dtype.int64, format=0, shape=[1, 20], size=160, realsize=160
    """
    
    # 加载 Tokenizer
    print(f"Loading tokenizer: bert-base-uncased")
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased", do_lower_case=True)

    # 预处理输入
    image_path = args.image_path
    imsize = 640
    text_query = args.text_query
    max_query_len = 20

    # 获取图像张量和图像掩码
    print(f"Preprocessing image: {image_path}")
    image_tensors_np, image_mask_np = preprocess_image(image_path, imsize) 

    # 获取文本 token ids 和 attention mask (作为 text_mask)
    print(f"Preprocessing text: '{text_query}'")
    text_tensors_np, text_mask_np = preprocess_text(text_query, tokenizer, max_query_len)

    # 准备模型输入
    feeds = [image_tensors_np, image_mask_np, text_tensors_np, text_mask_np]
    
    # 预热
    print("Preheating inference for 5 times")
    for _ in tqdm(range(5), desc="Preheating Progress"):
        outputs = session.infer(feeds)

    # 执行推理
    run_iter = 100
    print(f"Running inference for {run_iter} iterations...")
    inference_times = []
    for _ in tqdm(range(run_iter), desc="Inference Progress"):
        start_time = time.time()
        outputs = session.infer(feeds)
        end_time = time.time()
        inference_times.append(end_time - start_time)

    # 计算并打印统计数据
    inference_times_np = np.array(inference_times)
    avg_time = np.mean(inference_times_np)
    std_dev = np.std(inference_times_np)
    
    print(f"\nInference completed.")
    print(f"Average inference time: {avg_time:.4f} seconds")
    print(f"Standard deviation: {std_dev:.4f} seconds")

    # 将预测框转换为 xyxy 格式并反归一化到原始图像尺寸
    try:
        output_path = "output.png"
        img_orig = Image.open(image_path)
        
        cx, cy, w, h = outputs[0][0]
        # 反归一化到原始图像尺寸
        # 注意：这里的反归一化假设预测框是相对于调整和裁剪后的 imsize * imsize 图像的
        # 如果要映射回原始图像，需要考虑 Resize 和 CenterCrop 的影响，会更复杂。
        # 这里我们先简化，假设是映射回 imsize * imsize 的坐标
        # 如果需要精确映射回原始尺寸，需要保存变换信息或使用更复杂的反向映射
        
        # 简化：映射回 imsize x imsize 坐标空间
        disp_w, disp_h = imsize, imsize 
        x1 = (cx - w / 2) * disp_w
        y1 = (cy - h / 2) * disp_h
        x2 = (cx + w / 2) * disp_w
        y2 = (cy + h / 2) * disp_h
        
        print(f"Predicted box (x1, y1, x2, y2) in {disp_w}x{disp_h} coordinates: [{x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}]")
        
        # (可选) 在调整/裁剪后的图像上绘制边界框并显示/保存
        # 需要加载调整/裁剪后的图像用于显示
        display_transform = transforms.Compose([
             transforms.Resize(imsize), 
             transforms.CenterCrop(imsize)
        ])
        img_display = display_transform(img_orig)

        from PIL import ImageDraw

        draw = ImageDraw.Draw(img_display)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        # img_display.show() # 在某些环境可能无法显示
        img_display.save(output_path)
        print(f"Output image saved to: {output_path}")


    except Exception as e:
        print(f"Could not perform post-processing or save the image: {e}")

if __name__ == "__main__":
    main()

```

执行脚本：

```bash
python scripts/om_infer.py --image_path=datasets/COCO_train2014_000000000077.jpg --text_query="man on the left"
```

输出：

```bash
Preprocessing image: datasets/COCO_train2014_000000000077.jpg
Preprocessing text: 'man on the left'
Preheating inference for 5 times
Preheating Progress: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 13.90it/s]
Running inference for 15 iterations...
Inference Progress: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 15/15 [00:01<00:00, 14.57it/s]

Inference completed.
Average inference time: 0.0683 seconds
Standard deviation: 0.0004 seconds
Predicted box (x1, y1, x2, y2) in 640x640 coordinates: [-0.94, 277.50, 103.75, 580.00]
Output image saved to: output.png
```

可以看到处理一张图片的速度在 68 毫秒左右。

值得注意的是，执行中间通过 `npu-smi info` 可以看到，AICore 占用率可以达到 70% 左右！

## 17. conda 环境

做上述几个实验都是基于 conda 的 python310 环境，具体的环境 `environment.yml` 文件如下：

```yml
name: python310
channels:
  - defaults
dependencies:
  - _libgcc_mutex=0.1=main
  - _openmp_mutex=5.1=51_gnu
  - aiohappyeyeballs=2.4.4=py310hd43f75c_0
  - aiohttp=3.11.10=py310h998d150_0
  - aiosignal=1.2.0=pyhd3eb1b0_0
  - aom=3.6.0=h419075a_0
  - arrow-cpp=19.0.0=h9f8dcca_1
  - async-timeout=5.0.1=py310hd43f75c_0
  - aws-c-auth=0.6.19=h998d150_0
  - aws-c-cal=0.5.20=h6ac735f_0
  - aws-c-common=0.8.5=h998d150_0
  - aws-c-compression=0.2.16=h998d150_0
  - aws-c-event-stream=0.2.15=h419075a_0
  - aws-c-http=0.6.25=h998d150_0
  - aws-c-io=0.13.10=h998d150_0
  - aws-c-mqtt=0.7.13=h998d150_0
  - aws-c-s3=0.1.51=h6ac735f_0
  - aws-c-sdkutils=0.1.6=h998d150_0
  - aws-checksums=0.1.13=h998d150_0
  - aws-crt-cpp=0.18.16=h419075a_0
  - aws-sdk-cpp=1.11.212=h07ee7af_0
  - blas=1.0=openblas
  - boost-cpp=1.82.0=hb8fdbf2_2
  - bottleneck=1.4.2=py310hf6ef57e_0
  - brotli-python=1.0.9=py310h419075a_9
  - bzip2=1.0.8=h998d150_6
  - c-ares=1.19.1=h998d150_0
  - ca-certificates=2025.2.25=hd43f75c_0
  - cairo=1.16.0=h537eab0_5
  - cyrus-sasl=2.1.28=h647bc0d_1
  - datasets=3.3.2=py310hd43f75c_0
  - dav1d=1.2.1=h998d150_0
  - dbus=1.13.18=h821dc26_0
  - decorator=5.1.1=pyhd3eb1b0_0
  - dill=0.3.8=py310hd43f75c_0
  - eigen=3.4.0=hb8fdbf2_0
  - expat=2.7.1=h419075a_0
  - ffmpeg=6.1.1=hdb7fdae_3
  - fontconfig=2.14.1=h881afe3_3
  - freetype=2.13.3=h6df46f4_0
  - frozenlist=1.5.0=py310h998d150_0
  - gflags=2.2.2=h419075a_1
  - giflib=5.2.2=h998d150_0
  - glib=2.78.4=h419075a_0
  - glib-tools=2.78.4=h419075a_0
  - glog=0.5.0=h419075a_1
  - graphite2=1.3.14=h22f4aa5_1
  - gst-plugins-base=1.14.1=h419075a_1
  - gstreamer=1.14.1=h998d150_1
  - harfbuzz=10.2.0=h7c4b5c0_0
  - hdf5=1.14.5=h2117f30_2
  - huggingface_hub=0.29.2=py310hd43f75c_0
  - icu=73.1=h419075a_0
  - jpeg=9e=h998d150_3
  - krb5=1.20.1=h2e2fba8_1
  - lame=3.100=hfd63f10_0
  - ld_impl_linux-aarch64=2.40=h48e3ba3_0
  - leptonica=1.82.0=h5aee8ef_2
  - lerc=4.0.0=h419075a_0
  - libabseil=20240116.2=cxx17_h419075a_0
  - libarchive=3.7.7=h4086d46_0
  - libboost=1.82.0=hda0696e_2
  - libbrotlicommon=1.0.9=h998d150_9
  - libbrotlidec=1.0.9=h998d150_9
  - libbrotlienc=1.0.9=h998d150_9
  - libclang=14.0.6=default_hd3a980f_2
  - libclang13=14.0.6=default_h5e70c7c_2
  - libcups=2.4.2=hb788212_1
  - libcurl=8.12.1=hd336600_0
  - libdeflate=1.22=h998d150_0
  - libedit=3.1.20230828=h998d150_0
  - libev=4.33=hfd63f10_1
  - libevent=2.1.12=h6ac735f_1
  - libffi=3.4.4=h419075a_1
  - libgcc-ng=11.2.0=h1234567_1
  - libgfortran-ng=11.2.0=h6e398d7_1
  - libgfortran5=11.2.0=h1234567_1
  - libglib=2.78.4=hd439bcf_0
  - libgomp=11.2.0=h1234567_1
  - libgrpc=1.62.2=hb788212_0
  - libiconv=1.16=h998d150_3
  - libllvm14=14.0.6=hbfe7563_4
  - libnghttp2=1.57.0=hb788212_0
  - libogg=1.3.5=h2f4d8fa_1
  - libopenblas=0.3.29=h29fea54_0
  - libopus=1.3.1=h998d150_1
  - libpng=1.6.39=h998d150_0
  - libpq=17.4=h6ac735f_0
  - libprotobuf=4.25.3=h94b7715_0
  - libssh2=1.11.1=hfa2bbb0_0
  - libstdcxx-ng=11.2.0=h1234567_1
  - libtheora=1.1.1=h2f4d8fa_3
  - libthrift=0.15.0=hb2e9abc_2
  - libtiff=4.5.1=h7870c7c_1
  - libuuid=1.41.5=h998d150_0
  - libvorbis=1.3.7=hfd63f10_0
  - libvpx=1.13.1=h419075a_0
  - libwebp=1.3.2=he1bfee4_0
  - libwebp-base=1.3.2=h998d150_1
  - libxcb=1.17.0=hf66535e_0
  - libxkbcommon=1.9.1=h417a37e_0
  - libxml2=2.13.8=h6097fa9_0
  - lz4-c=1.9.4=h419075a_1
  - multidict=6.1.0=py310h998d150_0
  - multiprocess=0.70.15=py310hd43f75c_0
  - mysql=8.4.0=h505ef0a_1
  - ncurses=6.4=h419075a_0
  - numexpr=2.10.1=py310hd351863_0
  - numpy-base=1.26.4=py310h15d264d_0
  - opencv=4.10.0=py310h98e1fb1_2
  - openh264=2.1.1=h549d06d_0
  - openjpeg=2.5.2=ha2c532c_0
  - openldap=2.6.4=h418a7c9_0
  - openssl=3.0.16=h998d150_0
  - orc=2.0.1=h49f335c_0
  - pandas=2.2.3=py310h419075a_0
  - pcre2=10.42=hcfaa891_1
  - pip=25.1=pyhc872135_2
  - pixman=0.40.0=h2f4d8fa_1
  - propcache=0.3.1=py310h998d150_0
  - pthread-stubs=0.3=hfd63f10_1
  - pyarrow=19.0.0=py310h419075a_1
  - pysocks=1.7.1=py310hd43f75c_0
  - python=3.10.16=h4bb2201_1
  - python-dateutil=2.9.0post0=py310hd43f75c_2
  - python-tzdata=2025.2=pyhd3eb1b0_0
  - python-xxhash=3.5.0=py310h998d150_0
  - pytz=2024.1=py310hd43f75c_0
  - pyyaml=6.0.2=py310h998d150_0
  - qt-main=5.15.2=h1e70531_12
  - re2=2022.04.01=h22f4aa5_0
  - readline=8.2=h998d150_0
  - regex=2024.11.6=py310h998d150_0
  - s2n=1.3.27=h6ac735f_0
  - safetensors=0.5.3=py310h75a8df5_0
  - setuptools=78.1.1=py310hd43f75c_0
  - six=1.17.0=py310hd43f75c_0
  - snappy=1.2.1=h419075a_0
  - sqlite=3.45.3=h998d150_0
  - tesseract=5.2.0=h419075a_2
  - tk=8.6.14=h987d8db_0
  - tokenizers=0.21.0=py310hdc1999c_0
  - tqdm=4.67.1=py310ha5ee653_0
  - transformers=4.49.0=py310hd43f75c_0
  - typing_extensions=4.12.2=py310hd43f75c_0
  - tzdata=2025b=h04d1e81_0
  - utf8proc=2.6.1=h998d150_1
  - wheel=0.45.1=py310hd43f75c_0
  - xkeyboard-config=2.44=h998d150_0
  - xorg-libx11=1.8.12=hf66535e_1
  - xorg-libxau=1.0.12=hf66535e_0
  - xorg-libxdmcp=1.1.5=hf66535e_0
  - xorg-xorgproto=2024.1=h998d150_1
  - xxhash=0.8.0=h2f4d8fa_3
  - xz=5.6.4=h998d150_1
  - yaml=0.2.5=hfd63f10_0
  - yarl=1.18.0=py310h998d150_0
  - zlib=1.2.13=h998d150_1
  - zstd=1.5.6=h6a09583_0
  - pip:
      - absl-py==2.2.2
      - aclruntime==0.0.2
      - ais-bench==0.0.2
      - attr==0.3.2
      - attrs==23.2.0
      - certifi==2022.12.7
      - charset-normalizer==2.1.1
      - cloudpickle==3.1.1
      - coloredlogs==15.0.1
      - filelock==3.18.0
      - flatbuffers==25.2.10
      - fsspec==2025.5.0
      - humanfriendly==10.0
      - idna==3.4
      - jinja2==3.1.6
      - markupsafe==3.0.2
      - ml-dtypes==0.5.1
      - mpmath==1.3.0
      - networkx==3.4.2
      - numpy==1.26.3
      - onnx==1.18.0
      - onnxruntime-cann==1.23.0
      - packaging==25.0
      - pillow==11.0.0
      - protobuf==6.31.0
      - psutil==7.0.0
      - requests==2.28.1
      - scikit-video==1.1.11
      - scipy==1.12.0
      - sympy==1.14.0
      - synr==0.5.0
      - torch==2.1.0
      - torch-npu==2.1.0.post12
      - torchaudio==2.1.0
      - torchvision==0.16.0
      - tornado==6.4
      - typing-extensions==4.13.2
      - urllib3==1.26.13
prefix: /usr/local/miniconda3/envs/python310

```

















