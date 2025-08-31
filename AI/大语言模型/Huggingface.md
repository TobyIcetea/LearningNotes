# Huggingface

## 首先考虑 modelscope 社区

huggingface 上的模型肯定是最全的，但是下载不太方便，所以可以首先看一下 modelscope 中有没有这个模型：https://modelscope.cn/my/overview。

对于每一个模型，modelscope 中都会给出模型下载的方式。

比如说对于 `llama2-7b-hf` 模型，可以使用如下的 python 脚本：

```go
# download
from modelscope import snapshot_download
model_dir = snapshot_download('shakechen/Llama-2-7b-hf', cache_dir='/root/autodl-tmp/models')
```

其中的 `cache_dir` 尽量设置好，因为如果不设置，默认会将模型下载到 `~/.cache` 中，这样会造成家目录的空间占用过高。而服务器一般会有专用的数据盘。

比如说我在 AutoDL 上这次租用的服务器，家目录的大小实际上只有 50G 左右，但是 `~/autodl` 这里放了一个 1000G 的数据盘，是专门用来放模型的。

## 我的 huggingface token

一段加密后的 token：

```go
aGZfck1lWGdteEh3Yk1iTmFPRVhKcnpUZ0VjTE5QTHBHV2xsUg==
```

## 通过镜像站下载

国内有一个 huggingface 的镜像站：https://hf-mirror.com/。

之后下载的方式，可以使用如下的流程：

```bash
# 首先安装工具
pip install -U huggingface_hub

# 设置镜像站地址
export HF_ENDPOINT=https://hf-mirror.com

# 首先在 huggingface 上创建一个 token，同时 token 的权限中一定要有 Read access to contents of all public gated repos you can access 这一条
hf auth login --token ${TOKEN}
hf auth whoami
hf download meta-llama/Llama-2-13b-hf --local-dir /root/autodl-tmp/models/llama2-13b --exclude *.bin  
```

注意：其中的 `hf login` 并不是每一个模型都是需要的。不过是 llama 的文件列表都要申请 access 之后才能访问，所以 llama 的模型需要做这样一个认证。







