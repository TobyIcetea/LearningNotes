# 《鸟哥的 Linux 私房菜》

## 1. 认识与学习 Bash

学习和认识 Bash 是熟练使用 Linux 系统的关键。Bash 是 Bourne Again Shell 的缩写，它是 Linux 和 Unix 系统上常用的命令行解释器。学习 Bash 能帮助我们高效地管理文件、执行程序和编写自动化脚本。

### 1.1 概述

**【Bash 基础】**

- Shell：Shell 是操作系统与用户之间的接口，Bash 是一种 Shell。它负责解释并执行用户输入的命令。
- 终端（Terminal）：终端是用来访问 Shell 的界面。你可以在 Linux 中打开终端并进入 Bash。

**【常用命令】**

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

**【Bash 脚本基础】**

Bash 脚本是由 Bash 命令组成的文件，通常用于自动化任务。文件通常以 `.sh` 拓展名保存，以下是编写 Bash 脚本的基本步骤：

1. 创建脚本文件，例如 `nano myscript.sh`。
2. 写入脚本头：`#!/bin/bash`，这行告诉系统使用 Bash 来解释脚本内容。
3. 编写脚本内容：例如，编写输出文本的命令 `echo "Hello, World!"`。
4. 赋予执行权限：`chmod +x myscript.sh`。
5. 运行脚本：通过 `./myscript.sh` 执行脚本。

**【Bash 脚本变量】**

- 变量声明：变量不需要指定数据类型，`myvar="Hello"`。
- 使用变量：用 `$` 调用变量，比如 `echo $myvar`。
- 位置参数变量：在脚本中可以通过 `$1`、`$2` 等表示传入的参数。

**【控制结构】**

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

**【常用技巧】**

- 管道 `|`：将一个命令的输出作为下一个命令的输入。例如 `ls | grep "txt"`。
- 重定向：使用 `>` 将输出写入文件，比如 `echo "Hello" > output.txt`。
- 别名：为常用命令设置别名，`alias ll="ls -la"`。

### 1.2 变量内容的删除、取代与替换

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

### 1.3 export

在 Bash 中，`export` 命令用于设置环境变量，使它们可以在当前 Shell 进程以及其子进程中访问。以下是关于 `export` 的一些关键点：

**【基本用法】**

`export` 命令通常用于将一个变量导出为环境变量。例如：

```bash
export VAR_NAME="value"
```

这会在当前 shell 进程和所有子进程中都能访问到 `VAR_NAME`，而不仅仅是在当前 shell 中有效。

**【查看环境变量】**

执行 `export` 而不带参数会列出当前 shell 中所有已导出的环境变量：

```bash
export
```

此外，你还可以使用 `printenv` 或 `env` 命令来查看环境变量。

**【设置多个变量】**

可以在一行中设置并导出多个变量：

```bash
export VAR1="value1" VAR2="value2"
```

**【取消导出】**

可以通过 `export -n` 来取消对某个变量的导出，使它仅在当前 shell 可见：

```bash
export -n VAR_NAME
```

**【临时导出变量】**

在执行一个命令的同时设置一个环境变量，而不改变当前 shell 环境中的变量值。例如：

```bash
VAR_NAME="value" some_command
```

这样 `some_command` 会在环境变量 `VAR_NAME` 设置为 `value` 的情况下运行，但这不会影响到当前 shell 中的 `VAR_NAME` 值。

**【使用 `export` 和 `PATH`】**

`export` 常用于修改 `PATH` 环境向量，以添加可执行文件的路径。例如：

```bash
export PATH="$PATH:/new/path"
```

这会将 `/new/path` 添加到 `PATH` 中，从而使该路径下的可执行文件可以在当前 shell 会话中直接调用。

**【`export` 和子 shell】**

当你在 shell 脚本中设置一个变量并未使用 `export` 导出时，该变量在子 shell 中无法访问。例如：

```bash
VAR="value"
bash -c 'echo $VAR'  # 不会输出值
```

但是如果使用 `export`：

```bash
export VAR="value"
bash -c 'echo $VAR' # 会输出 "value"
```

这样，`VAR` 就可以在子 shell 中访问。

**【永久性导出】**

要永久导出一个变量（比如配置环境变量 `PATH`），可以将 `export` 命令添加到 `~/.bashrc` 或 `~/.bash_profile` 文件中。然后执行 `source ~/.bashrc` 或重启终端来应用更改。

**【示例总结】**

```bash
export MY_VAR="hello"  # 设置并导出变量
echo $MY_VAR  # 访问变量
export PATH="$PATH:/mydir"  # 修改 PATH 变量
export -n MY_VAR  # 取消导出
```

### 1.4 管道命令

1. cut：用于从每一行文本中提取指定的部分。

    - 示例：`cut -d ':' -f 1 /etc/passwd`

        解释：以冒号作为分隔符，提取每行的第一个字段。

2. grep：用于在文件中搜索匹配指定模式的行。

    - 示例：`grep "error" log.txt`

        解释：在 log.txt 中查找包含 "error" 的行。

3. sort：用于对文本行进行排序。

    - 示例：`sort names.txt`

        解释：对 names.txt 中的行按字母顺序排序。

4. wc：用于统计文件中的行数、字数和字符数。

    - 示例：`wc -l file.txt`

        解释：统计 file.txt 的行数。

5. uniq：用于报告或忽略重复的行，通常与 `sort` 结合使用。

    - 示例：`sort data.txt | uniq`

        解释：先对 data.txt 排序，然后删除重复的行。

6. tee：将标准输入内容输出到标准输出，并保存到文件中。

    - 示例：`ls | tee files.txt`

        解释：将 `ls` 的输出显示在终端，并保存到 file.txt。

7. tr：用于替换或删除文本中的字母。

    - 示例：`echo "hello world" | tr '[:lower:]' '[:upper:]'`

        解释：将小写字母转换为大写。

8. col：用于过滤控制字符，例如反向转换符。

    - 示例：`man ls | col -b`

        解释：格式化 `man ls` 的输出，去除控制字符。

9. join：用于合并两个文件中具有相同字段的行。

    - 示例：`join file1.txt file2.txt`

        解释：基于共同字段，将 file1.txt 和 file2.txt 的内容合并。

10. paste：用于按行将多个文件的内容并列显示。

    - 示例：`paste file1.txt file2.txt`

        解释：将 file1.txt 和 file2.txt 的对应行并排显示。

11. expand：将制表符转换为空格。

    - 示例：`expand -t 4 file.txt`

        解释：将 file.txt 中的制表符替换为 4 个空格。

12. split：用于将文件拆分为多个小文件

    - 示例：`split -l 1000 largefile.txt part_`

        解释：每 1000 行将 largefile.txt 拆分为一个文件，文件名前缀为 part_。

13. xargs：将标准输入转换为命令行参数，常用于构建和执行命令。

    - 示例：`find . -name "*.txt" | xargs rm`

        解释：找到当前目录下的所有 .txt 文件并删除。





































