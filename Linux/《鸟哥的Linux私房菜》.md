# 《鸟哥的 Linux 私房菜》

## 1. 认识与学习 Bash

学习和认识 Bash 是熟练使用 Linux 系统的关键。Bash 是 Bourne Again Shell 的缩写，它是 Linux 和 Unix 系统上常用的命令行解释器。学习 Bash 能帮助我们高效地管理文件、执行程序和编写自动化脚本。以下是学习 Bash 的一些基本概念和常用命令：

### 1.1 Bash 基础

- Shell：Shell 是操作系统与用户之间的接口，Bash 是一种 Shell。它负责解释并执行用户输入的命令。
- 终端（Terminal）：终端是用来访问 Shell 的界面。你可以在 Linux 中打开终端并进入 Bash。

### 1.2 常用命令

Bash 中的常用命令可以分为文件管理、系统信息、进程管理等几类。

**文件管理命令**

- `ls`：列出目录内容，比如 `ls -l` 显示详细信息。
- `cd`：更改目录，比如 `cd /home/user`。
- `pwd`：显示当前目录。
- `mkdir`：创建目录，比如 `mkdir myfolder`。
- `rm`：删除文件或目录（谨慎使用），`rm -r myfolder` 删除文件夹。
- `cp`：复制文件，比如 `cp file1 file2` 复制 `file1` 为 `file2`。
- `mv`：移动或重命名文件，比如 `mv file1 newfile`。

**系统信息命令**

- `uname`：查看系统信息，比如 `uname -a` 显示详细信息。
- `df`：显示磁盘空间使用情况，`df -h` 以人类可读的格式显示。
- `top`：显示进程和系统资源的使用情况。

**进程管理命令**

- `ps`：查看当前进程，`ps aux` 显示所有进程。
- `kill`：杀死进程，比如 `kill 1234` 终止 PID 为 1234 的进程。
- `jobs`：查看后台进程。
- `bg` / `fg`：将进程放入后台或前台运行。

### 1.3 Bash 脚本基础

Bash 脚本是由 Bash 命令组成的文件，通常用于自动化任务。文件通常以 `.sh` 拓展名保存，以下是编写 Bash 脚本的基本步骤：

1. 创建脚本文件，例如 `nano myscript.sh`。
2. 写入脚本头：`#!/bin/bash`，这行告诉系统使用 Bash 来解释脚本内容。
3. 编写脚本内容：例如，编写输出文本的命令 `echo "Hello, World!"`。
4. 赋予执行权限：`chmod +x myscript.sh`。
5. 运行脚本：通过 `./myscript.sh` 执行脚本。

### 1.4 Bash 脚本变量

- 变量声明：变量不需要指定数据类型，`myvar="Hello"`。
- 使用变量：用 `$` 调用变量，比如 `echo $myvar`。
- 位置参数变量：在脚本中可以通过 `$1`、`$2` 等表示传入的参数。

### 1.5 控制结构

Bash 中也支持条件判断和循环：

- 条件判断：`if` 语句，例如：

    ```bash
    if [ $myvar -eq 5 ]; then
    	echo "myvar is 5"
    fi
    ```

- 循环：包括 `for` 循环、`while` 循环。例如：

    ```bash
    for i in {1..5}; do
    	echo "Number $i"
    done
    ```

### 1.6 常用技巧

- 管道 `|`：将一个命令的输出作为下一个命令的输入。例如 `ls | grep "txt"`。
- 重定向：使用 `>` 将输出写入文件，比如 `echo "Hello" > output.txt`。
- 别名：为常用命令设置别名，`alias ll="ls -la"`。

### 1.7 变量内容的删除、取代与替换

在 Linux Bash 中，变量内容的删除、取代与替换是处理字符串内容的常用技巧，以下是几种常用的操作方式：

**【删除子字符串】**

我们可以使用 `${variable#pattern}` 或 `$variable$$pattern` 来删除变量内容中符合特定模式的部分。

- `${variable#pattern}`：从变量开头删除特定模式的最短匹配。
- `${variable##pattern}`：从变量开头删除特定模式的最长匹配。

例如：

```bash
[root@toby ~]# filename="/home/user/file.txt"
[root@toby ~]# echo ${filename#*/}  # 删除开头最短匹配到的 /
home/user/file.txt
[root@toby ~]# echo ${filename##*/}  # 删除开头最长匹配到的 /
file.txt
```

**【删除结尾子字符串】**

类似于删除开头的内容，`${variable%pattern}` 和 `${variable%%pattern}` 可用于删除结尾处复合模式串的内容、

- `${variable%pattern}`：从变量结尾删除符合模式的最短匹配。
- `${variable%%pattern}`：从变量结尾删除符合模式的最长匹配。

例如：

```bash
[root@toby ~]# filename="file.txt.bak"
[root@toby ~]# echo ${filename%.*}  # 删除结尾最短匹配的 . 开头的内容
file.txt
[root@toby ~]# echo ${filename%%.*}  # 删除结尾最长匹配的 . 开头的内容
file
```

**【字符串替换】**

可以使用 `${variable/pattern/replacement}` 和 `${variable//pattern/replacement}` 来替换字符串中的内容。

- `${variable/pattern/replacement}`：替换变量内容中符合模式的第一个匹配项。
- `${variable//pattern/replacement}`：替换变量内容中所有符合模式的匹配项。

例如：

```bash
[root@toby ~]# text="hello world, hello bash"
[root@toby ~]# echo ${text/hello/hi}  # 将第一个 "hello" 替换为 "hi"
hi world, hello bash
[root@toby ~]# echo ${text//hello/hi}  # 将所有 "hello" 替换为 "hi"
hi world, hi bash
```

**【默认值与替换】**

Bash 还支持使用 `:-` 和 `:=` 等操作符来为变量提供默认值或进行赋值操作。

- `${variable:-default}`：如果变量未定义或为空，返回 `default`，但不改变变量的值。
- `${variable:=default}`：如果变量未定义或为空，返回 `default`，并将 `default` 赋值给变量。

例如：

```bash
[root@toby ~]# unset var
[root@toby ~]# echo ${var:-"default"}  # 输出 "default"，但 var 仍为空
default
[root@toby ~]# echo ${var:="default"}  # 输出 "default"，但将 var 赋值为 "default"
default
[root@toby ~]# echo $var  # 输出 "default"
default
```

这些字符串操作方法可以帮助更灵活地处理变量中的内容，尤其是在处理路径、文件名、URL 等场景中。





