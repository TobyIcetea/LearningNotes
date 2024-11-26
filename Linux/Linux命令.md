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
" 是否显示状态栏。0 表示不显示，1 表示只在多窗口时显示，2 表示显示。
set laststatus=2
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













