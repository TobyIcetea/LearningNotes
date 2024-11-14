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
set showmode
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
" 是否显示状态栏。0 表示不显示，1 表示只在多窗口时显示，2 表示显示。
set laststatus=2
" 对于任何文件，写代码时不延续上一行的注释
autocmd FileType * setlocal formatoptions-=c formatoptions-=r formatoptions-=o

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
Plug 'mhinz/vim-startify'

call plug#end()
```

之后随便打开一个 Vim 文件，然后执行 `:PlugInstall` 就可以自动安装插件。

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











