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

## 3. encoding

Go 语言的标准库中，`encoding` 包及其子包提供了丰富的编码和解码功能，用于处理各种数据格式的序列化和反序列化。

### 3.1 `encoding` 包概述

`encoding` 包本身主要定义了一些通用的接口，这些接口为各种数据格式的编码和解码提供了统一的标准。主要的接口包括：

- `BinaryMarshaler` 和 `BinaryUnmarshaler`：用于二进制数据的编码和解码。
- `TextMarshaler` 和 `TextUnmarshaler`：用于文本数据的编码和解码。

```go
type BinaryMarshaler interface {
    MarshalBinary() (data []byte, err error)
}

type BinaryMarshaler interface {
    UnMarshalerBinary(data []byte) error
}

type TextMarshaler interface {
    MarshalText() (text []byte, err error)
}

type TextUnmarshaler interface {
    UnmarshalerText(text []byte) error
}
```

这些接口允许自定义类型实现特定的编码和解码方法，从而与标准库的编码器和解码器协同工作。

### 3.2 `encoding` 包的主要子包

**（1）`encoding/json`**

用于处理 JSON 格式的数据。提供了 `Marshal` 和 `Unmarshal` 函数，将 Go 数据结构与 JSON 格式相互转换。

示例：

```go
import (
	"encoding/json"
	"fmt"
)

type User struct {
    Name string `json:name`
    Age int `json:"age"`
}

func main() {
    user := User{Name: "张三", Age: 30}
    data, err := json.Marshal(user)
    if err != nil {
        fmt.Println("编码错误：", err)
        return
    }
    fmt.Println("JSON格式：", string(data))
    
    var decodeUser User
    err = json.Unmarshal(data, &decodeUser)
    if err != nil {
        fmt.Println("解码错误：", err)
        return
    }
    fmt.Println("解码后：", decodeUser)
}
```

执行结果：

```
JSON格式： {"Name":"张三","age":30}
解码后： {张三 30}
```

**（2）`encoding/xml`**

用于处理 XML 格式的数据。类似于 `encoding/json`，提供了 `Marshal` 和 `UnMarshal` 函数。

示例：

```go
import (
	"encoding/xml"
	"fmt"
)

type User struct {
	XMLName xml.Name `xml:"user"`
	Name    string   `xml:"name"`
	Age     int      `xml:"age"`
}

func main() {
	user := User{Name: "李四", Age: 25}
	data, err := xml.Marshal(user)
	if err != nil {
		fmt.Println("编码错误：", err)
		return
	}
	fmt.Println("XML 格式：", string(data))

	var decodeUser User
	err = xml.Unmarshal(data, &decodeUser)
	if err != nil {
		fmt.Println("编码错误：", err)
		return
	}
	fmt.Println("解码后：", decodeUser)
}
```

执行结果：

```
XML 格式： <user><name>李四</name><age>25</age></user>
解码后： {{ user} 李四 25}
```

**（3） `encoding/gob`**

Go 特有的二进制序列化格式，适用于在 Go 应用程序之间传递数据。

```go
import (
	"bytes"
	"encoding/gob"
	"fmt"
)

type User struct {
	Name string
	Age  int
}

func main() {
	var buffer bytes.Buffer
	encoder := gob.NewEncoder(&buffer)
	decoder := gob.NewDecoder(&buffer)

	user := User{Name: "王五", Age: 28}
	err := encoder.Encode(user)
	if err != nil {
		fmt.Println("编码错误：", err)
		return
	}

	var decodeUser User
	err = decoder.Decode(&decodeUser)
	if err != nil {
		fmt.Println("解码错误：", err)
		return
	}
	fmt.Println("解码后：", decodeUser)
}
```

执行结果：

```
解码后： {王五 28}
```

**（4）`encoding/binary`**

提供了在字节序列与基础数据类型之间转换的功能，支持大端和小端字节序。

```go
import (
	"encoding/binary"
	"fmt"
)

func main() {
	data := make([]byte, 4)
	binary.BigEndian.PutUint32(data, 1024)
	fmt.Println("大端字节序：", data)

	value := binary.BigEndian.Uint32(data)
	fmt.Println("转换回整数:", value)
}
```

执行结果：

```
大端字节序： [0 0 4 0]
转换回整数: 1024
```

**（5）`encoding/csv`**

用于读取和写入 CSV（逗号分隔值）格式的文件。

示例：

```go
import (
	"encoding/csv"
	"fmt"
	"strings"
)

func main() {
	reader := csv.NewReader(strings.NewReader("name,age\n赵六,22\n钱7,24"))
	records, err := reader.ReadAll()
	if err != nil {
		fmt.Println("读取错误：", err)
		return
	}
	fmt.Println("CSV 内容：", records)
}
```

执行结果：

```
CSV 内容： [[name age] [赵六 22] [钱7 24]]
```

**（6）`encoding/base64`**

用于 Base64 编码和解码，常用于在文本环境中传输二进制数据。

示例：

```go
import (
	"encoding/base64"
	"fmt"
)

func main() {
	data := "Hello，世界"
	encoded := base64.StdEncoding.EncodeToString([]byte(data))
	fmt.Println("Base64 编码：", encoded)

	decoded, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		fmt.Println("编码错误：", err)
		return
	}
	fmt.Println("解码后：", string(decoded))
}
```

执行结果：

```
Base64 编码： SGVsbG/vvIzkuJbnlYw=
解码后： Hello，世界
```

**（7）`encoding/hex`**

提供了十六进制的编码和解码功能。

示例：

```go
import (
	"encoding/hex"
	"fmt"
)

func main() {
	data := "Go 语言"
	encoded := hex.EncodeToString([]byte(data))
	fmt.Println("十六进制编码：", encoded)

	decoded, err := hex.DecodeString(encoded)
	if err != nil {
		fmt.Println("解码错误，", err)
		return
	}
	fmt.Println("解码后：", string(decoded))
}
```

执行结果：

```
十六进制编码： 476f20e8afade8a880
解码后： Go 语言
```

### 3.3 实现自定义编码和解码

通过实现 `encoding` 包定义的接口，可以自定义类型的编码和解码行为。

示例：

```go
import (
	"fmt"
	"strconv"
	"strings"
)

type User struct {
	Name string
	Age  int
}

// MarshalText 实现 TextMarshaller 接口
func (u *User) MarshalText() ([]byte, error) {
	return []byte(fmt.Sprintf("%s:%d", u.Name, u.Age)), nil
}

// UnmarshalText 实现 TextUnmarshaler 接口
func (u *User) UnmarshalText(data []byte) error {
	parts := strings.Split(string(data), ":")
	if len(parts) != 2 {
		return fmt.Errorf("无效的数据格式")
	}
	u.Name = parts[0]
	age, err := strconv.Atoi(parts[1])
	if err != nil {
		return err
	}
	u.Age = age
	return nil
}

func main() {
	user := User{Name: "孙八", Age: 26}
	data, _ := user.MarshalText()
	fmt.Println("自定义编码：", string(data))

	var decodeUser User
	decodeUser.UnmarshalText(data)
	fmt.Println("解码后：", decodeUser)
}
```

执行结果：

```
自定义编码： 孙八:26
解码后： {孙八 26}
```

### 3.4 注意事项

- 结构体标签（Struct Tags）：在 `encoding/json` 和 `encoding/xml` 中，可以使用结构体标签来控制字段的编码和解码行为，如执行字段名、忽略字段等。
- 错误处理：在编码和解码过程中，可能会发生错误，务必进行错误检查，防止程序崩溃或产生不正确的结果。
- 性能考虑：不同的编码方式在性能上可能有所差异，根据具体需求选择合适的编码格式。
- 安全性：在处理外部载入的数据时，要注意防范恶意数据，避免安全漏洞。

### 3.5 总结

`encoding` 包及其子包在 Go 语言数据库中扮演着重要的角色，提供了处理各种数据格式的便捷方法。熟练掌握这些包的使用，可以大大提高数据序列化和反序列化的效率，增强程序的兼容性和稳定性。

## 4. strconv

Go 语言的 `strconv` 包用于实现基本数据类型与其字符串表示形式之间的转换。它提供了一系列函数，可以将字符串解析为基本数据类型，或者将基本数据类型格式化为字符串。这在处理用于输入、配置文件、日志记录等方面非常有用。

### 4.1 整数和字符串之间的转换

**（1）Atoi 和 Itoa**

- `func Atoi(s string) (int, error)`

将字符串 `s` 转换为整数（`int` 类型）。`Atoi` 是 `ParseInt(s, 10, 0)` 的简写没赚用于十进制整数的转换。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	s := "12345"
	i, err := strconv.Atoi(s)
	if err != nil {
		fmt.Println("转换失败：", err)
	} else {
		fmt.Println("整数值为：", i)
	}
}
```

输出结果为：

```makefile
整数值为： 12345
```

- `func Itoa(i int) string`

将整数 `i` 转换为字符串。`Itoa` 是 `FormatInt(int64(i), 10)` 的简写。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	i := 67890
	s := strconv.Itoa(i)
	fmt.Println("字符串值为：", s)
}
```

输出结果为：

```makefile
字符串值为： 67890
```

**（2）ParseInt 和 FormatInt**

- `func ParseInt(s string, base int, bitSize int) (int64, error)`

将字符串 `s` 转换为指定进制和位大小的整数（`int64` 类型）。参数说明：

- `s`：要解析的字符串。
- `base`：进制（2 到 36），0 表示自动判断进制（如「0x」开头表示 16 进制）。
- `bitSize`：整数的位大小（0、8、16、32、64）。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	s := "0x1A"
	i, err := strconv.ParseInt(s, 0, 64)
	if err != nil {
		fmt.Println("转换失败：", err)
	} else {
		fmt.Println("整数值为：", i)
	}
}
```

输出结果为：

```
整数值为： 26
```

- `func FormatInt(i int64, base int) string`

将整数 `i` 格式化为指定进制的字符串。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	i := int64(26)
	s := strconv.FormatInt(i, 16)
	fmt.Println("字符串值为：", s)
}
```

输出结果为：

```
字符串值为： 1a
```

**（3）PaeseUint 和 FormatUing**

- `func ParseUint(s string, base int, bitSize int) (uint64, error)`

类似于 `ParseInt`，但用于无符号整数。

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	s := "123"
	u, err := strconv.ParseUint(s, 0, 64)
	if err != nil {
		fmt.Println("转换失败:", err)
	} else {
		fmt.Println("无符号整数值为:", u)
	}
}
```

输出结果为：

```
无符号整数值为: 123
```

- `func FormatUint(i uint64, base int) string`

将无符号整数 `i` 格式化为指定进制的字符串。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	u := uint64(123)
	s := strconv.FormatUint(u, 10)
	fmt.Println("字符串值为:", s)
}
```

输出结果为：

```
字符串值为: 123
```

### 4.2 浮点数和字符串之间的转换

**（1）ParseFloat 和 FormatFloat**

- `func ParseFloat(s string, bitSize int) (float64, error)`

将字符串 `s` 解析为浮点数（`float64` 类型）。`bitSize` 参数指定了精度（32 表示 `float32`，64 表示 `float64`）。

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	s := "3.14159"
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		fmt.Println("转换失败:", err)
	} else {
		fmt.Println("浮点数值为:", f)
	}
}
```

- `func FormatFloat(f float64, fmt byte, prec int, bitSize int) string`

将浮点数 `f` 格式化为字符串。

- `fmt`：格式化标识符，`'f'`（小数形式），`'e'`（整数形式），`'g'`（根据情况选择 `'e'` 或 `'f'`）。
- `prec`：精度，表示小数点后的位数。
- `bitSize`：位大小（32 或 64）。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	f := 3.1415926535
	s := strconv.FormatFloat(f, 'f', 2, 64)
	fmt.Println(s)
}
```

输出结果为：

```
3.14
```

### 4.3 布尔值和字符串之间的转换

**（1）ParseBool 和 FormatBool**

- `func ParseBool(str string) (bool error)`

将字符串 `str` 解析为布尔值。接受的真值字符串有：`"1"`、`"t"`、`"T"`、`"true"`、`"True"`、`"TRUE"`；假值字符串有：`"0"`、`"f"`、`"F"`、`"false"`、`"False"`、`"FALSE"`。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	s := "True"
	b, err := strconv.ParseBool(s)
	if err != nil {
		fmt.Println("转换失败:", err)
	} else {
		fmt.Println("布尔值为:", b)
	}
}
```

输出结果为：

```
布尔值为: true
```

- `func FormatBool(b bool) string`

示例：

```go
import (
	"fmt"
	"strconv"
)

func main() {
	b := false
	s := strconv.FormatBool(b)
	fmt.Println("字符串值为:", s)
}
```

输出结果为：

```
字符串值为: false
```

### 4.4 字符串的引用和转义

**（1）Quote 和 Unquote**

- `func Quote(s string) string`

返回字符串 `s` 的双引号引用形式，必要时会对特殊字符进行转义。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	s := "Hello\nWorld"
	q := strconv.Quote(s)
	fmt.Println("引用字符串为:", q)
}
```

输出结果为：

```yml
引用字符串为: "Hello\nWorld"
```

- `func Unquote(s string) (string, error)`

将带引号的字符串 `s` 解析为原始字符串。

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	q := "\"Hello\\nWorld\""
	s, err := strconv.Unquote(q)
	if err != nil {
		fmt.Println("解析失败:", err)
	} else {
		fmt.Println("原始字符串为:", s)
	}
}
```

输出结果为：

```go
原始字符串为: Hello
World
```

### 4.5 其他常用函数

**（1）Append 系列函数**

这些函数用于将转换结果直接追加到字节切片（`[]byte`）中，可以减少内存分配，提升性能。

- `func AppendInt(dst []byte, i int64, base int) []byte`

将整数 `i` 转换为指定进制的字符串并追加到 `dst` 中。

示例：

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	dst := []byte("Number:")
	dst = strconv.AppendInt(dst, 123, 10)
	fmt.Println(string(dst))
}
```

输出结果为：

```
Number:123
```

- `func AppendFloat(dst []byte, f float64, fmt byte, prec int, bitSize int) []byte`

将浮点数 `f` 格式化为字符串并追加到 `dst` 中。

- `func AppendBool(dst []byte, b bool) []byte`

将布尔值 `b` 格式化为字符串并追加到 `dst` 中。

**（2）IsPrint**

- `func IsPrint(r rune) bool`

判断字符 `r` 是否为可打印字符。

```go
package main

import (
	"fmt"
	"strconv"
)

func main() {
	r := '你'
	fmt.Println("是否为可打印字符:", strconv.IsPrint(r))
	r = '\n'
	fmt.Println("是否为可打印字符:", strconv.IsPrint(r))
}
```

输出结果为：

```
是否为可打印字符: true
是否为可打印字符: false
```

### 4.6 使用注意事项

- 错误处理：大多数 `strconv` 函数都会在转换失败时返回错误，使用时应注意进行错误检查，避免程序崩溃。
- 进制和位大小：在使用 `ParseInt` 和 `FormatInt` 等函数时，需要正确指定进制和位大小，以确保转换结果的准确性。
- 性能优化：在高性能场景下，可以使用 `Append` 系列函数，避免不必要的字符串分配。

### 4.7 总结

`strconv` 包在 Go 语言的标准库中扮演着重要的角色，提供了丰富的函数用于基本数据类型和字符串之间的转换。熟练掌握这些函数，可以有效地处理数据解析、格式化和序列化等任务，提高代码的健壮性和可读性。

## 5. math

Go 语言的 math 包提供了基本的常数和数学函数，主要用于浮点数的运算。

### 5.1 常数

- `math.PI`：圆周率π，约等于 3.141592653589793。
- `math.E`：自然常数 e，约等于 2.718281828459045。

### 5.2 基本数学函数

**（1）绝对值函数**

- `math.Abs(x float64) float64`

返回 x 的绝对值。

```go
fmt.Println(math.Abs(-3.5))  // 输出 3.5
```

**（2）乘方和开方**

- `math.Pow(x, y float64) float64`

返回 x 的 y 次幂，即 x^y。

```go
fmt.Println(math.Pow(2, 3))  // 输出 8
```

- `math.Sqrt(x float64) float`

返回 x 的平方根。

```go
fmt.Println(math.Sqrt(16))  // 输出 4
```

- `math.Cbrt(x float64) float64`

返回 x 的立方根。

```go
fmt.Println(math.Cbrt(27))  // 输出 3
```

**（3）指数和对数函数**

- `math.Exp(x float64) float64`

返回 e^x。

```go
fmt.Println(math.Exp(1))  // 输出：2.718281828459045
```

- `math.Log(x float64) float64`

返回 x 的自然底数（以 e 为底）。

```go
fmt.Println(math.Log(math.E))  // 输出：1
```

- `math.Log10(x float64) float64`

返回 x 的以 10 为底的对数。

```go
fmt.Println(math.Log10(100))  // 输出：2
```

- `math.Log2(x float64) float64`

返回 x 的以 2 为底的对数。

```go
fmt.Println(math.Log2(8))  // 输出：3
```

**（4）取整和舍入函数**

- `math.Ceil(x float64) float64`

返回大于或等于 x 的最小整数。

```go
fmt.Println(math.Ceil(3.2))  // 输出：4
```

- `math.Floor(x float64) float64`

返回小于或等于 x 的最大整数。

```go
fmt.Println(math.Floor(3.8))  // 输出：3
```

- `math.Round(x float64) float64`

返回四舍五入后的整数值。

```go
fmt.Println(math.Round(3.5))  // 输出：4
fmt.Println(math.Round(3.4))  // 输出：3
```

- `math.Trunc(x float64) float64`

返回 x 的整数部分，直接截断小数部分。

```go
fmt.Println(math.Trunc(3.9))  // 输出：3
```

**（5）最大值和最小值**

- `math.Max(x, y float64) float64`

返回 x 和 y 中的较大值。

```go
fmt.Println(math.Max(3, 5))  // 输出：5
```

- `math.Min(x, y float64) float64`

返回 x 和 y 中的较小值。

```go
fmt.Println(math.Min(3, 5))  // 输出：3
```

### 5.3 三角函数

**（1）正弦、余弦、正切**

- `math.Sin(x float64) float64`

返回 x 的正弦值，x 的单位为弧度。

```go
fmt.Println(math.Sin(math.Pi / 2))  // 输出：1
```

- `math.Cos(x float64) float64`

返回 x 的余弦值。

```go
fmt.Println(math.Cos(0))  // 输出：1
```

- `math.Tan(x float64) float64`

返回 x 的正切值。

```go
fmt.Println(math.Tan(math.Pi / 4))  // 输出：1
```

**（2）反三角函数**

- `math.Asin(x float64) flaot64`

返回 x 的反正弦值，结果为弧度。

```go
fmt.Println(math.Asin(1))  // 输出：1.5707963267948966 (π/2)
```

- `math.Acos(x float64) float64`

返回 x 的反余弦值。

```go
fmt.Println(math.Acos(0))  // 输出：1.5707963267948966 (π/2)
```

- `math.Atan(x float64) float64`

返回 x 的反正切值。

```go
fmt.Println(math.Atan(1))  // 输出：0.7853981633974483 (π/4)
```

- `math.Atan2(y, x float64) float64`

返回 `y/x` 的反正切值，结果在 [-π, π] 之间，考虑象限。

```go
fmt.Println(math.Atan2(1, 1))  // 输出：0.7853981633974483 (π/4)
```

**（3）双曲函数**

- `math.Sinh(x float64) float64`

返回 x 的双曲正弦值。

- `math.Cosh(x float64) float64`

返回 x 的双曲余弦值。

- `math.Tanh(x flaot64) float64`

返回 x 的双曲正切值。
$$
\begin{aligned}
    Sinh(x) = \frac{e^x - e^{-x}}{2}  \\
    Cosh(x) = \frac{e^x + e^{-x}}{2}  \\
	Tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}}
\end{aligned}
$$

### 5.4 其它函数

**（1）取模和余数**

- `math.Mod(x, y float64) float64`

返回 x 除以 y 的浮点数余数。

```go
fmt.Println(math.Mod(5.5, 2))  // 输出：1.5
```

- `math.Remainder(x, y float64) float64`

返回 x 除以 y 的余数，结果可能为负数。

**（2）误差函数**

- `math.Hypot(p, q float64) float64`

返回 `sqrt(p * p + q * q)`，即欧几里得距离。

```go
fmt.Println(math.Hypot(3, 4))  // 输出：5
```

**（3）符号函数**

- `math.Copysign(x, y float64) float64`

返回以 y 的符号为符号的 x。

```go
fmt.Println(math.Copysign(3, -1))  // 输出：-3
```

**（4）下一个表示数**

- `math.Nextafter(x, y float64) float64`

返回从 x 到 y 方向上的下一个最接近的浮点数。

```go
fmt.Println(math.Nextafter(1, 2))  // 输出：1.0000000000000002
```

### 5.5 常用技巧

**（1）角度和弧度转换**

- `math.Pi`

    可以用于角度和弧度的转换：

    - 弧度 = 角度 * （math.Pi / 180）
    - 角度 = 弧度 * （180 / math.Pi）

```go
angle := 90.0
radian := angle * (math.Pi / 180)
fmt.Println(math.Sin(radian))  // 输出：1
```

**（2）判断特殊值**

- `math.IsNaN(x float64) bool`

判断 x 是否为 NaN（Not a Number）。

- `math.IsInf(x float64, sign int) bool`

    判断 x 是否为正无穷大或负无穷大。

    - sign > 0：判断为正无穷大。
    - sign < 0：判断为负无穷大。
    - sign == 0：判断任意无穷大。

```go
fmt.Println(math.IsNaN(math.Sqrt(-1)))  // 输出：true
fmt.Println(math.IsInf(1.0/0.0, 0))  // 输出：true
```

### 5.6 示例应用

**（1）计算两个点之间的距离**

```go
func distance(x1, y1, x2, y2 float64) float64 {
    return math.Hypot(x2 - x1, y2 - y1)
}

fmt.Println(distance(0, 0, 3, 4))  // 输出：5
```

**（2）四舍五入到指定小数位**

```go
func roundTo(value float64, places int) float64 {
    shift := math.Pow(10, float64(places))
    return math.Round(value * shift) / shift
}
```

### 5.7 注意事项

- 类型限制：math 包的函数大多接受并返回 float64 类型，因此在使用时需要注意类型转换。
- 参数范围：某些函数对参数有特定的范围要求，例如反三角函数的输入值必须在 [-1, 1] 之间。
- NaN 和 Inf：当计算结果不在实数范围内时，函数可能返回 NaN 或 Inf，需要进行判断处理。







