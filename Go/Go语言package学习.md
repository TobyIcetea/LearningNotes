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



## 3. encoding/json





## 4. strconv

## 5. math

## 6. rand

## 7. time

## 8. io

## 9. regexp



