# Python 知识

## 1. `.venv` 文件夹的作用

在 PyCharm 项目中，`.venv` 目录是用来存放虚拟环境的。虚拟环境是一种隔离的 Python 环境，用来管理项目所需的依赖包（比如各种库和模块），从而确保不同项目之间的依赖不会相互干扰。

`.venv` 目录的主要作用：

1. 依赖隔离：每个项目都有自己独立的包依赖，不会影响系统全局的 Python 环境或其他项目的依赖。这样，你可以在不同项目中使用不同版本的包。
2. 方便管理依赖：在虚拟环境中，你可以用 `pip install` 安装和更新特定的库，这些库会直接被安装到 `.venv` 目录中，避免污染全局环境。
3. 便于迁移和部署：虚拟环境中的依赖可以通过 `requirements.txt` 文件来记录，便于将项目迁移到其他环境中，确保一致性。
4. 版本控制友好：有了虚拟环境，项目可以使用不同的 Python 版本（如 Python 3.7 或 Python 3.8），避免系统版本兼容性问题。

在 PyCharm 中创建项目时，可以选择是否生成 `.venv` 目录，如果启用了，它就会作为当前项目的虚拟环境，方便自动管理和运行。

## 2. 如何导出已有 Python 项目的 requirements 文件

### 创建虚拟环境并激活

```bash
python -m venv venv
source venv/bin/activate

# 如果要退出
deativate
```

导出项目实际使用的包：

```bash
# 安装工具
pip install pipreqs
# 生成 requirements 文件
pipreqs /path/to/your_project --encoding=utf-8 --force
```

其中，`--encoding=utf-8` 是为了避免编码问题，`--force` 是为了覆盖已有的 `requirements.txt`。

之后在进行环境准备的时候，可以使用命令：

```bash
pip install -r requirements.txt
```

### 虚拟环境的本质

在激活虚拟环境前后，我发现 `echo $PATH` 就是虚拟环境会在这个环境变量开头加上一个新的 `/root/workdir/01-yolov5/venv/bin:`（01-yolov5 是我的工作目录）。

所以虚拟环境的本质就是临时修改了 `PATH` 变量，这样的话，之后在终端输入命令（如 pip、python）等命令的时候，系统会优先使用虚拟环境中的二进制文件，而不是全局安装的版本。

## 3. pip 安装使用国内源

首先是安装 pip。在 Centos 中，安装 pip 可以使用如下的命令：

```bash
dnf install python3-pip
```

之后使用 pip 进行 `pip3 install` 操作的时候，可以使用如下的源：

```bash
Python官方 https://pypi.python.org/simple/

阿里云 https://mirrors.aliyun.com/pypi/simple/

清华大学 https://pypi.tuna.tsinghua.edu.cn/simple/

中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/

中国科学技术大学 https://pypi.mirrors.ustc.edu.cn/simple/
```

比如，假如我们要安装 `cv2`，可以使用：

```bash
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ opencv-python
```

如果要进行全局修改，也可以通过修改配置文件的方式完成配置：

```bash
mkdir ~/.pip

cat << EOF > ~/.pip/pip.conf
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = https://pypi.tuna.tsinghua.edu.cn
EOF
```

可以查看一下镜像地址列表：

```bash
[root@master ascend-infer]# pip3 config list
global.index-url='https://pypi.tuna.tsinghua.edu.cn/simple'
install.trusted-host='https://pypi.tuna.tsinghua.edu.cn'
```



















