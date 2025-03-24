# Ascend 知识体系

## 1. Ascend 软硬件体系

![image-20250317101101593](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250317101101593.png)

其中可以看到，Ascend 的异构计算架构 CANN，其实就是和 CUDA 是同一类东西。

只不过对于 NVIDIA 的显卡，我们是在 NVIDIA 显卡上建立一层 GPU 驱动，然后在驱动之上，再建立一层 CUDA，CUDA 之上再建立 Pytorch 之类的计算框架。

但是对于我们 Ascend 的硬件，我们是在 Ascend 的硬件之上，建立一层 NPU 驱动，然后在 NPU 驱动之上，我们再建立一层 CANN，CANN 之上再去使用 MindSpore 框架。

其中的 CUDA 或者是 CANN 都是上层软件跟底层硬件打交道的，CUDA 是 Pytorch 框架和 NVIDIA GPU 之间沟通交流的桥梁，而 CANN 是 MindSpore 和 CANN 之间沟通交流的桥梁。

## 2. AscenCL 与 PyACL

### 训练阶段：Python 为主，框架生态丰富

昇腾支持主流深度学习框架（如 Pytorch、MindSpore、Tensorflow），开发者可通过 Python 接口直接调用昇腾 NPU 算力：

- MindSpore：原生支持昇腾硬件，支持万亿参数模型的分布式训练。
- Pytorch：通过插件（如 `torch_npu`）实现昇腾适配，支持混合精度训练，梯度优化等技术。
- 性能优化：结合昇腾的 MindSpeed-LLM 加速库，实现动态内存管理、通信优化、提升训练吞吐量。

关键工具：

- MindStudio：提供可视化调试、性能分析功能，支持分布式训练任务监控。
- ATC 工具：讲开源框架模型（如 ONNX）转换为昇腾专用格式（`*.om`）。

### 推理阶段：C 和 Python 的平衡选择

Ascend 提供两种推理路径：

#### 原生 AscendCL（C 语言）

- 优势：直接操作硬件，无封装层开销，性能最优。
- 适用场景：实时视频分析、工业质检等低延迟需求场景。

#### PyACL（Python 封装库）

- 优势：简化开发流程，与 Python 生态无缝集成，性能损失控制在 5% 以内。

关联性：PyACL 本质是 AscendCL 的 Python 绑定，底层调用相同硬件指令。

















