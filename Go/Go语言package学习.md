# Go 语言 packge 学习

## 1. fmt

### 1.1 `fmt` 包简介

`fmt` 包是 Go 语言的标准库，用于格式化输入和输出操作。它提供了一系列函数，用于在控制台输出信息、格式化字符串、读取输入等操作，是 Go 开发中最常用的包之一。

### 1.2 输出函数

#### 1.2.1 `Print` 系列函数

**（1）`fmt.Print(a ...interface{})`**

- 功能：将参数内容输出到控制台，不附加任何其他字符。

- 用法：

    ```go
    fmt.Print("Hello, World!")
    ```

- 示例：

    ```go
    a := 10
    b := 10
    fmt.Print("a + b = ", a + b)
    // 输出：a + b = 30
    ```

**（2）`fmt.Println(a, ...interface{})`**

- 功能：与 `Print` 类似，但在输出结束后会自动添加换行符 `\n`。

- 用法：

    ```go
    fmt.Println("Hello, World")
    ```

- 示例：

    ```go
    name := "张三"
    fmt.Println("姓名：", name)
    // 输出：
    // 姓名： 张三
    ```

**（3）`fmt.Printf(format string, a ...interface{})`**

- 功能：按照指定的格式化字符串输出内容。

- 用法：

    ```go
    fmt.Printf("格式化字符串", 参数列表)
    ```

- 示例：

    ```go
    age := 25
    fmt.Printf("年龄：%d\n", age)
    // 输出：年龄：25
    ```

#### 1.2.2 格式化占位符

在使用 `Printf` 时，需要用到格式化占位符，常用的有：

- `%v`：值的默认格式表示
- `%+v`：类似 `%v`，但输出结构体时会添加字段名
- `%#v`：值的 Go 语言语法表示
- `%T`：值的类型的 Go 语言表示
- `%%`：百分号本身

整数：

- `%b`：二进制表示
- `%c`：相应 Unicode 码点所表示的字符
- `%d`：十进制表示
- `%o`：八进制表示
- `%x`：十六进制表示，使用 a-f
- `%X`：十六进制表示，使用 A-F

浮点数：

- `%e`：科学计数法：1.23e+03
- `%f`：浮点数
- `%g`：根据实际情况采用 `%e` 或 `%f` 格式

字符串和字节切片：

- `%s`：字符串或字节切片
- `%q`：双引号括起来的字符串
- `%x`：每个字节用两字符十六进制表示（小写字母）
- `%X`：每个字节用两字符十六进制表示（大写字母）

示例：

```go
n := 255
fmt.Printlf("二进制：%b\n", n)
fmt.Printlf("十进制：%d\n", n)
fmt.Printlf("八进制：%o\n", n)
fmt.Printlf("十六进制：%x\n", n)
```

输出：

```go
二进制：11111111
十进制：255
八进制：377
十六进制：ff
```

### 1.3 输入函数

**（1）`fmt.Scan(a ...interface{})`**

- 功能：从标准输入中读取内容，以空白为分隔符。

- 用法：

    ```go
    var name string
    fmt.Scan(&name)
    ```

- 示例：

    ```go
    var a int
    var b int
    fmt.Print("请输入两个整数：")
    fmt.Scan(&a, &b)
    fmt.Printf("输入的整数为：%d 和 %d\n", a, b)
    ```

**（2）`fmt.Scanln(a, ...interface{})`**

- 功能：类似 `Scan`，但以换行符为结束标志。

- 用法：

    ```go
    fmt.Scanln(&a, &b)
    ```

**（3）`fmt.Scanf(format string, a ...interface{})`**

- 功能：根据制定的格式化字符串读取输入。

- 用法：

    ```go
    fmt.Scanf("%d-%d-%d", &year, &month, &day)
    ```

- 示例：

    ```go
    var year, month, day int
    fmt.Print("请输入日期（格式 YYYY-MM-DD）：")
    fmt.Scanf("%d-%d-%d", &year, &month, &day)
    fmt.Printf("输入的日期是：%d 年 % 月 % 日\n", year, month, day)
    ```

### 1.4 `Sprint` 系列函数

**（1）`fmt.Sprint(a ...interface{})`**

- 功能：将内容格式化为字符串返回。

- 用法：

    ```go
    s := fmt.Sprint("Hello, ", "World!")
    ```

**（2）`fmt.Sprintf(format string, a ...interface{})`**

- 功能：按照格式化字符串将内容格式化为字符串返回。

- 用法：

    ```go
    s := fmt.Sprintf("姓名：%s，年龄：%d", name, age)
    ```

- 示例：

    ```go
    name := "李四"
    age := 30
    info := fmt.Sprintf("姓名：%s，年龄：%d", name, age)
    fmt.Println(info)
    // 输出：姓名：李四，年龄：%d
    ```

**（3）`fmt.Sprintln(a ...interface{})`**

- 功能：类似 `Sprint`，但会在末尾添加换行符。

- 用法：

    ```go
    s := fmt.Sprintln("Hello, World!")
    ```

### 1.5 `Fprint` 系列函数

这些函数用于将格式化后的内容写入到 `io.Writer` 接口实现的对象中，如文件、网络连接等。

**（1）`fmt.Fprint(w io.Writer, a ...interface{})`**

- 功能：将内容写入指定的 `io.Writer`。

- 用法：

    ```go
    fmt.Fprint(file, "写入文件的内容")
    ```

**（2）`fmt.Fprintf(w io.Writer, format string, a ...interface{})`**

- 功能：按照格式化字符串将内容写入到指定的 `io.Writer`。

- 用法：

    ```go
    fmt.Fprintf(conn, "HTTP/1.1 %d %s\r\n", statusCode, statusText)
    ```

**（3）`fmt.Fprintln(w io.Writer, a ...interface{})`**

- 功能：类似 `Fprint`，但会在末尾添加换行符。

- 用法：

    ```go
    fmt.Fprintln(file, "写入文件的内容")
    ```

- 示例：

    ```go
    file, err := os.Create("test.txt")
    if err != nil {
        fmt.Println("文件创建失败：", err)
        return
    }
    defer file.Close()
    
    fmt.Fprintln(file, "Hello, 文件！")
    // 内容被写入到 test.txt 文件中
    ```

### 1.6 `Errorf` 函数

`fmt.Errorf(fotmat string, a ...interface{}) error`

- 功能：按照格式化字符串创建并返回一个 `error` 类型的错误。

- 用法：

    ```go
    err := fmt.Errorf("这是一个错误：%s", errMsg)
    ```

- 示例：

    ```go
    func divide(a, b int) (int, error) {
        if b == 0 {
            return 0, fmt.Errorf("除数不能为零")
        }
        return a / b, nil
    }
    
    result, err := divide(10, 0)
    if err != nil {
        fmt.Println("计算错误：", err)
    } else {
        fmt.Println("计算结果：", result)
    }
    // 输出：计算错误：除数不能为零
    ```

### 1.7 格式化参数

在格式化输出中，可以使用参数来控制输出的宽度、精度和对齐方式。

- 宽度：对于最小宽度，例如 `%5d` 表示最小宽度为 5 的整数。
- 精度：对于浮点数，表示小数点后的位数，例如 `%.2f` 表示保留两位小数。
- 标志：
    - `-`：左对齐
    - `+`：总是输出数值的符号
    - `0`：使用零填充

示例：

```go
n := 123.456
fmt.Printf("|%10.2f|\n", n)  // 输出：|    123.46|
fmt.Printf("|%-10.2f|\n", n) // 输出：|123.46    |
fmt.Printf("|%010.2f|\n", n) // 输出：|0000123.46|
```

### 1.8 `fmt` 包的常见用法总结

- 输出到控制台
    - `fmt.Print()`：直接输出内容
    - `fmt.Println()`：输出内容并换行
    - `fmt.Printf()`：格式化输出
- 格式化字符串
    - `fmt.Sprint()`：返回格式化后的字符串
    - `fmt.Sprintf()`：返回格式化后的字符串，支持占位符
    - `fmt.Sprintln()`：返回格式化后的字符串，并在末尾添加换行符
- 输出到指定位置
    - `fmt.Fprint()`：将内容写入到 `io.Writer`
    - `fmt.Fprintf()`：格式化后写入到 `io.Writer`
    - `fmt.Fprintln()`：写入内容并换行到 `io.Writer`
- 输入：
    - `fmt.Scan()`：从标准输入读取内容，以空白为分隔符
    - `fmt.Scanln()`：从标准输入读取内容，以换行符为结束
    - `fmt.Scanf()`：按照指定格式从标准输入读取内容
- 错误处理：
    - `fmt.Errorf()`：格式化错误信息，返回 `error` 类型

## 2. os

Go 语言的 `os` 包提供了跨平台的操作系统功能接口，涵盖了文件的目录操作、进程管理、环境变量处理等方面的功能。

### 2.1 文件操作

**（1）打开和创建文件**

`os.Open(name string) (*os.File, error)`

以只读方式打开指定名称的文件，如果成功，返回一个 `*os.File` 指针。

```go
file, err := os.Open("example.txt")
if err != nil {
    log.Fatal(err)
}
defer file.Close()
```

`os.Create(name string) (*os.File, error)`

创建一个名为 `name` 的文件，如果文件已存在则清空该文件，返回一个 `*os.File` 指针。

```go
file, err := os.Create("example.txt")
if err != nil {
    log.Fatal(err)
}
defer file.Close()
```

**（2）读取和写入文件**

`(*File) Read(b []byte) (n int, err error)`

从文件中读取数据到 `b`，返回读取的字节数和可能的错误。

```go
data := make([]byte, 100)
n, err := file.Read(data)
if err != nil && err != io.EOF {
    log.Fatal(err)
}
fmt.Printf("读取了 %d 字节：%s\n", n, string(data[:n]))
```

`*File Write(b []byte) (n int, err error)`

将 `b` 中的数据写入文件，返回写入的字节数和可能的错误。

```go
content := []byte("Hello, World")
n, err := file.Write(content)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("写入了 %d 字节\n", n)
```

**（3）关闭文件**

`(*File) Close() error`

关闭文件，释放资源。

```go
err := file.Close()
if err != nil {
    log.Fatal(err)
}
```

**（4）删除文件**

`os.Remove(name string) error`

删除指定的文件或目录。

```go
err := os.Remove("example.txt")
if err != nil {
    log.Fatal(err)
}
```

### 2.2 目录操作

**（1）创建目录**

`os.Mkdir(name string, perm FileMode) error`

创建一个名为 `name` 的目录，`perm` 指定权限。

```go
err := os.Mkdir("testdir", 0755)
if err != nil {
    log.Fatal(err)
}
```

`os.MkdirAll(path string, perm FileMode) error`

递归创建多级目录。

```go
err := os.Mkdir("testdir/subdir", 0755)
if err != nil {
    log.Fatal(err)
}
```

**（2）删除目录**

`os.RemoveAll(path string) error`

递归删除指定目录及其包含的所有文件和子目录。

```go
err := os.RemoveAll("testdir")
if err != nil {
    log.Fatal(err)
}
```

**（3）改变当前工作目录**

`os.Chdir(dir string) error`

```go
err := os.Chdir("/path/to/dir")
if err != nil {
    log.Fatal(err)
}
```

**（4）获取当前工作目录**

`os.Getwd() (dir string, err)`

返回当前工作目录的路径。

```go
dir, err := os.Getwd()
if err != nil {
    log.Fatal(err)
}
fmt.Println("当前工作目录：", dir)
```

### 2.3 文件信息

**（1）获取文件或目录信息**

`os.Stat(name string) (FileInfo, error)`

返回 `FileInfo` 接口，包含文件或目录的详细信息。

```go
info, err := os.Stat("example.txt")
if err != nil {
    log.Fatal(err)
}
fmt.Println("文件大小：", info.Size())
fmt.Println("修改时间：", info.ModTime())
fmt.Println("是否是目录：", info.IsDir())
```

**（2）`FileInfo` 接口**

`FileInfo` 接口提供以下方法：

- `Name() string`：返回文件名
- `Size() int64`：返回文件大小
- `Mode() FileMode`：返回文件权限和模式
- `ModTime() time.Time`：返回修改时间
- `IsDir bool`：判断是否为目录

### 2.4 环境变量

**（1）获取环境变量**

`os.Getenv(key string) string`

返回环境变量 `key` 的值，如果不存在则返回空字符串。

```go
path := os.Getenv("PATH")
fmt.Println("PATH:", path)
```

**（2）设置环境变量**

`os.Setenv(key, value string) error`

设置环境变量 `key` 的值为 `value`。

```go
err := os.Setenv("MY_VAR", "my_value")
if err != nil {
    log.Fatal(err)
}
```

**（3）删除环境变量**

`os.Unsetenv(key string) error`

删除环境变量 `key`。

```go
err := os.Unsetenv("MY_VAR")
if err != nil {
    log.Fatal(err)
}
```

**（4）获取所有环境变量**

`os.Environ() []string`

```go
for _, err := range os.Environ() {
    fmt.Println(env)
}
```

### 2.5 进程管理

**（1）获取进程 ID**

`os.Getpid() int`

返回当前进程的 ID。

```go
pid := os.Getpid()
fmt.Println("当前进程 ID：", pid)
```

**（2）获取父进程 ID**

`os.Getppid() int`

```go
ppid := os.Getppid()
fmt.Println("父进程 ID：", ppid)
```

**（3）退出程序**

`os.Exit(code int)`

以指定的状态码退出程序。

```go
if err != nil {
    fmt.Println("发生错误，程序退出")
    os.Exit(1)
}
```

### 2.6 错误处理

`os` 包定义了一些标准错误，方便与 `error` 进行比较。

- `os.ErrNotExist`：文件或目录不存在
- `os.ErrExist`：文件或目录已存在
- `os.ErrPermisson`：权限不足

```go
_, err := os.Open("nonexistent.txt")
if errors.Is(err, os,ErrNotExist) {
    fmt.Println("文件不存在")
}
```

### 2.7 文件权限

**（1）更改文件权限**

`os.Chmod(name string, mode FileMode) error`

更改指定文件的权限。

```go
err := os.Chmod("example.txt", 0644)
if err != nil {
    log.Fatal(err)
}
```

**（2）更改文件所有者**

`os.Chown(name string, uid, git int) error`

更改指定文件的所有者和组（在 Unix 系统上有效）。

```go
err := os.Chown("example.txt", uid, gid)
if err != nil {
    log.Fatal(err)
}
```

### 2.8 符号链接

**（1）创建符号链接**

`os.Symlink(oldname, newname string) err`

创建指向 `oldname` 的符号链接 `newname`。

```go
err := os.Symlink("target.txt", "link.txt")
if err != nil {
    log.Fatal(err)
}
```

**（2）读取符号链接**

`os.Readlink(name string) (string, error)`

返回符号链接指向的目标路径。

```go
target, err := os.Readlink("link,txt")
if err != nil {
    log.Fatal(err)
}
fmt.Println("符号链接指向：", target)
```

### 2.9 临时文件和目录

**（1）创建临时文件**

`os.CreateTemp(dir, pattern string) (*os.File, error)`

在指定目录 `dir` 中创建一个临时文件，文件名以 `pattern` 为前缀。

```go
file, err := os.CreateTemp("", "tempfile_*.txt")
if err != nil {
    log.Fatal(err)
}
defer os.Remove(file.Name())  // 程序结束时删除临时文件
```

**（2）创建临时目录**

`os.MkdirTemp(dir, pattern string) (string, error)`

在指定目录 `dir` 中创建一个临时目录，目录名以 `pattern` 为前缀。

```go
dir, err := os.MkdirTemp("", "tempdir_")
if err != nil {
    log.Fatal(err)
}
defer os.RemoveAll(dir)  // 程序结束时删除临时目录
```

### 2.10 其他常用函数

**（1）重命名文件或目录**

`os.Rename(oldpath, newpath string) error`

将 `oldpath` 重命名为 `newpath`。

```go
err := os.Rename("oldname.txt", "newname.txt")
if err != nil {
    log.Fatal(err)
}
```

**（2）截断文件**

`os.Truncate(name string, size int64) error`

将指定文件截断到 `size` 大小。

```go
err := os.Truncate("example.txt", 100)
if err != nil {
    log.Fatal(err)
}
```

**（3）读取目录内容**

`os.ReadDir(name string) ([]os.DirEntry, error)`

返回指定目录中的所有目录项。

```go
entries, err := os.ReadDir(".")
if err != nil {
    log.Fatal(err)
}
for _, entry := range entries {
    fmt.Println(entry.Name())
}
```

### 2.11 总结

`os` 包是 Go 语言标准库中非常重要的一个包，提供了丰富的操作系统功能接口。熟练掌握 `os` 包的常用方法，可以大大提高文件和目录操作、环境变量处理、进程管理等方面的编程效率。在实际使用中，要注意不同操作系统之间的差异，确保代码的可移植性。

## 3. encoding/json





## 4. strconv

## 5. math

## 6. rand

## 7. time

## 8. io

## 9. regexp

## 10. log



