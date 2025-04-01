# Linux 命令

## 1. vim 配置

### 1.1 基础的 .vimrc 配置

```bash
cat << EOF > ~/.vimrc
" 在底部显示，当前处于命令模式还是插入模式
set showmode
" 命令模式下，在底部显示，当前键入的命令
set showcmd
" 使用 utf-8 编码
set encoding=utf-8
" 启用 256 色
set t_Co=256
" 显示行号
set number
" 光标所在当前行高亮
set cursorline
" 自动拆行，即太长的行分成几行显示
set wrap
" 垂直滚动时，光标距离顶部 / 底部的位置（单位：行）
set scrolloff=5
set 
" 是否显示状态栏。0 表示不显示，1 表示只在多窗口时显示，2 表示显示。
set laststatus=1
" 设置缩进为 4 个空格
set tabstop=4        " 设置 Tab 键等于 4 个空格
set shiftwidth=4     " 设置自动缩进时的空格数
set expandtab        " 使用空格代替 Tab 键
set softtabstop=4    " 设置插入模式下 Tab 的行为为 4 个空格

EOF
```

### 1.2 Vim Plugin 配置

通过配置 Vim Plugin 可以为 Vim 配置很多好用的插件，打造属于自己的好用的 IDE。

首先第一步，下载 `plug.vim` 文件：

```bash
wget https://raw.githubusercontent.com/junegunn/vim-plug/refs/heads/master/plug.vim

mkdir -p ~/.vim/autoload
mv plug.vim ~/.vim/autoload/plug.vim
```

之后就是 Vim Plugin 的使用，在 `~.vimrc` 中加入：

```bash
" VimPlugin 插件
call plug#begin()

" 之后加入插件的话，直接在这里加入 Plug '...' 就行
" 好看的启动界面
Plug 'mhinz/vim-startify'
" 底下好看的状态栏
Plug 'vim-airline/vim-airline'
" Vim 基础配置
Plug 'tpope/vim-sensible'

call plug#end()
```

之后随便打开一个 Vim 文件，然后执行 `:PlugInstall` 就可以自动安装插件。

### 1.3 Vim 搜索与替换

#### 搜索

1. 基本搜索
    - 在正常模式下输入 `/` 后面跟要搜索的文本，然后按回车键。例如，要搜索单词 "example"，可以输入 `/example`，然后按 Enter。
    - 搜索结果是高亮显示的，可以使用 `n` 命令跳到下一个匹配项，使用 `N` 跳到上一个匹配项。
2. 使用正则表达式
    - Vim 支持使用正则表达式进行更复杂的搜索。例如，`/[Ee]xample` 将匹配 "Example" 和 "example"。

#### 替换

1. 单行替换
    - 使用 `:s/old/new/` 命令来替换当前行中的第一个匹配项。
    - 若要替换当前行中的所有匹配项，可以使用 `:s/old/new/g`，其中 `g` 表示全局（global）替换。
2. 多行替换
    - 若要替换文件中所有行的第一个匹配项，可以使用 `:%s/old/new/`。
    - 若要替换文件中所有行的所有匹配项，可以使用 `:%s/old/new/g`。
    - **若要确认每次替换，可以添加 `c` 标志：`%s/old/new/gc`，这样每次替换都会弹出确认。**

## 2. Tabby 设置

一般情况下，Tabby 使用 SFTP 功能是不能直接 Get 到当前所在的目录的，得一级一级的查找。但是可以通过一个设置来解决：

**==Bash==**

`~/.bash_profile`：

```bash
export PS1="$PS1\[\e]1337;CurrentDir="'$(pwd)\a\]'
```

**ZSH**

`~/.zshrc`：

```bash
precmd () { echo -n "\x1b]1337;CurrentDir=$(pwd)\x07" }
```

**Fish**

`~/.config/fish/config.fish`：

```bash
function __tabby_working_directory_reporting --on-event fish_prompt
    echo -en "\e]1337;CurrentDir=$PWD\x7"
end
```

## 3. Centos 换源阿里云

```bash
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak
curl -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
yum clean all
yum makecache
yum repolist
```

## 4. Centos 内核升级

（这部分按理来说是可行的，但是实践没有成功。原因可能是官网没有继续维护 Centos7 那个目录了。）

Centos 7 默认的内核是 3.10.0，为了让它支持更多 linux 内核的新功能，我们可以尝试升级 Centos 的内核。

首先，安装 perl 工具包：

```bash
yum install -y perl
```

安装 ELRepo：

```bash
# 从 ELRepo 官网导入其 GPG 公钥，用于验证从 RLRepo 仓库下载的 RPM 包的签名。
# 确保软件包的来源和完整性，防止恶意篡改。
rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org
# 使用 yum 包管理器安装 ELRepo 仓库的 RPM 包。
# 这里安装的是 ELRepo 仓库的 release 文件，适用于 CentOS/RHEL 7 系统。
yum install -y https://www.elrepo.org/elrepo-release-7.el7.elrepo.noarch.rpm
```

接下来是换源，这次我们换成清华的源：

```bash
# 备份
cp /etc/yum.repos.d/elrepo.repo /etc/yum.repos.d/elrepo.repo.bak

# 在 mirrorlist= 开头的行前面加 # 注释掉；
# 将 http://elrepo.org/linux 替换为 https://mirrors.tuna.tsinghua.edu.cn/elrepo
sed -i '/^mirrorlist/s/^/# /' /etc/yum.repos.d/elrepo.repo
sed -i 's|http://elrepo.org/linux|https://mirrors.tuna.tsinghua.edu.cn/elrepo|g' /etc/yum.repos.d/elrepo.repo
```

查看内核版本列表：

```bash
yum --disablerepo="*" --enablerepo="elrepo-kernel" list avaiable
```

安装：

```bash
yum --enablerepo="elrepo-kernel" -y install kernel-ml.x86-64
```

修改启动顺序默认值：

```bash
grub2-set-default 0
```

产生 grub 配置文件：

```bash
grub2-mkconfig -o /boot/grub/grub.cfg
```

## 5. Centos 设置 vpn 代理

一般情况下我们执行 `curl google.com` 之类的命令是执行不通的。

在 windows 主机中开启 clash 的局域网代理功能，并且将代理端口设置为 7890，之后可以在 linux 中配置：

```bash
vim /etc/profile
----------------------------------------
FLCLASH_IP="10.198.60.212"  # 这里填写自己的 windows 主机的 ip 地址
export http_proxy="http://${FLCLASH_IP}:7890"
export https_proxy="http://${FLCLASH_IP}:7890"
export ftp_proxy="http://${FLCLASH_IP}:7890"
export no_proxy="localhost,127.0.0.1"
----------------------------------------

# 让配置文件生效
source /etc/profile
```

之后可以测试一下：

```bash
[root@toby ~]# curl google.com
<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
<TITLE>301 Moved</TITLE></HEAD><BODY>
<H1>301 Moved</H1>
The document has moved
<A HREF="http://www.google.com/">here</A>.
</BODY></HTML>
```

## 6. CentosStream 静态网络设置方式

新版的 Centos 不再使用老版本的更新 `/etc/sysconfig/network-scripts` 的方式，而是使用 NetworkManager 的方式。具体更新方式如下：

```bash
# 进入目录
cd /etc/NetworkManager/system-connections/

# 编辑网络配置文件，这里默认是 ens160
vim /etc/NetworkManager/system-connections/ens160.nmconnection
```

网络配置文件的书写范例如下：

```ini
[connection]
id=ens160
uuid=7ca40f61-21c3-3289-91cf-bc234abc5e62
type=ethernet
autoconnect-priority=-999
interface-name=ens160
timestamp=1741401629

[ethernet]

[ipv4]
address=192.168.100.101/24
dns=8.8.8.8;8.8.4.4;
gateway=192.168.100.2
ignore-auto-dns=true
method=manual

[ipv6]
addr-gen-mode=eui64
method=auto

[proxy]
```

当然我们主要是修改其中的 ipv4 部分的内容。

修改完了之后，重启一下网络，就可以看到是否生效：

```bash
nmcli connection reload
nmcli connection down ens160
nmcli connection up ens160

# 查看修改是否生效
ip addr
```

## 7. 加密一段字符串

使用的算法是 `AES-256-CBC`：

```bash
# 加密
echo -n "Hello world" | openssl enc -aes-256-cbc -salt -pass pass:"123456" -base64

U2FsdGVkX1+zwbaMU9/Va7zD7XGJATT0WZ7e2cbGPpI=

# 解密
echo "U2FsdGVkX1+zwbaMU9/Va7zD7XGJATT0WZ7e2cbGPpI=" | openssl enc -d -aes-256-cbc -pass pass:"123456" -base64

Hello world
```

## 8. 根据安装目录删除文件

在安装 containerd 的时候，安装包是根据以 root 为根进行安装的。解压的过程中通过过程可视化，看到安装的所有文件、目录有：

```bash
cri-containerd.DEPRECATED.txt
etc/
etc/cni/
etc/cni/net.d/
etc/cni/net.d/10-containerd-net.conflist
etc/systemd/
etc/systemd/system/
etc/systemd/system/containerd.service
etc/crictl.yaml
usr/
usr/local/
...
```

这样会导致之后删除的时候很麻烦，总不能将这些位置的文件一个一个对照，再一个一个删除。

之后再进行这样的操作的时候，可以使用如下的脚本：

```bash
#!/bin/bash

# 检查参数
if [ $# -ne 2 ]; then
    echo "Usage: $0 <root-directory> <install.list>"
    echo "Example: $0 /path/to/root install.list"
    echo "Example: $0 / install.list (for system root)"
    exit 1
fi

root_dir="$1"
list_file="$2"

# 特殊处理根目录情况
if [ "$root_dir" = "/" ]; then
    root_dir=""
fi

# 检查根目录是否存在（如果是系统根目录则跳过检查）
if [ -n "$root_dir" ] && [ ! -d "$root_dir" ]; then
    echo "Error: Root directory '$root_dir' not found."
    exit 1
fi

# 检查清单文件是否存在
if [ ! -f "$list_file" ]; then
    echo "Error: List file '$list_file' not found."
    exit 1
fi

# 从文件底部开始处理，先处理文件再处理目录
tac "$list_file" | while read -r path; do
    # 去除可能的尾随斜杠（用于目录）
    clean_path="${path%/}"

    # 构建完整路径
    if [ -z "$root_dir" ]; then
        full_path="/${clean_path}"
    else
        full_path="${root_dir}/${clean_path}"
    fi

    if [ -e "$full_path" ]; then
        if [ -f "$full_path" ]; then
            echo "Removing file: $full_path"
            rm -f "$full_path"
        elif [ -d "$full_path" ]; then
            # 检查目录是否为空
            if [ -z "$(ls -A "$full_path")" ]; then
                echo "Removing empty directory: $full_path"
                rmdir "$full_path"
            else
                echo "Directory not empty, skipping: $full_path"
            fi
        fi
    else
        echo "Path does not exist, skipping: $full_path"
    fi
done

echo "Cleanup completed under root: ${root_dir:-/}"

```

将上述脚本保存为 `clean.sh`，并且将安装的所有文件的列表保存为 `install.list`，之后可以执行脚本：

```bash
./clean.sh / install.sh
```

就可以将安装的这些文件、目录都删除啦。















