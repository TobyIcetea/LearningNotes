# Ascend 知识体系

## 1. Ascend 软硬件体系

![image-20250317101101593](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250317101101593.png)

其中可以看到，Ascend 的异构计算架构 CANN，其实就是和 CUDA 是同一类东西。

只不过对于 NVIDIA 的显卡，我们是在 NVIDIA 显卡上建立一层 GPU 驱动，然后在驱动之上，再建立一层 CUDA，CUDA 之上再建立 Pytorch 之类的计算框架。

但是对于我们 Ascend 的硬件，我们是在 Ascend 的硬件之上，建立一层 NPU 驱动，然后在 NPU 驱动之上，我们再建立一层 CANN，CANN 之上再去使用 MindSpore 框架。

其中的 CUDA 或者是 CANN 都是上层软件跟底层硬件打交道的，CUDA 是 Pytorch 框架和 NVIDIA GPU 之间沟通交流的桥梁，而 CANN 是 MindSpore 和 CANN 之间沟通交流的桥梁。





