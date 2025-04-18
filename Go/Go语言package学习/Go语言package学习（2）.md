# Go 语言 package 学习（2）

## 6. rand

在 Go 语言中，`math/rand` 包用于生成伪随机函数。该包提供了一系列函数，可以生成各种类型的随机数，包括整数、浮点数和排列。

### 6.1 基本随机数生成函数

- `rand.Int()`

    - 返回一个介于 `0` 到 `math.MaxInt32` 之间的非负随机整数。

    - 示例：

        ```go
        package main
        
        import (
        	"fmt"
        	"math/rand"
        )
        
        func main() {
        	fmt.Println(rand.Int())
        }
        ```

- `rand.Intn(n int)`

    - 返回一个介于 `0`（包含）到 `n`（不包含）之间的随机整数。

    - 示例：

        ```go
        fmt.Println(rand.Intn(100))  // 生成 0 到 99 之间的随机整数
        ```

- `rand.Float32()`

    - 返回一个介于 `0.0` 到 `1.0` 之间的随机 `float32` 数。

    - 示例：

        ```go
        fmt.Println(rand.Float32())
        ```

- `rand.Float64()`

    - 返回一个介于 `0.0` 到 `1.0` 之间的随机 `float64` 数。

    - 示例：

        ```go
        fmt.Println(rand.Float64())
        ```

### 6.2 随机排列和选择

- `rand.Perm(n int)`

    - 返回一个长度为 `n` 的整数切片，包含 `[0, n)` 的一个随机排列。

    - 示例：

        ```go
        nums := rand.Perm(5)
        fmt.Println(nums)  // 可能输出 [4 1 2 3 0]
        ```

### 6.3 随机种子

- `rand.Seed(seed int64)`

    - 设置全局随机数生成种子。默认情况下，Go 的随机数生成器使用固定的种子，所以如果不设置种子，每次运行程序都会产生相同的随机数序列。

    - 通常使用当前时间来设置种子：

        ```go
        import (
            "time"
        )
        
        rand.Seed(time.Now().UnixNano())
        ```

    - `rand.NewSource(seed int64)` 和 `rand.New(r rand.Source)`

        - 创建一个新的随机数生成源，可以用于创建独立的随机数生成器实例。

        - 实例：

            ```go
            package main
            
            import (
            	"fmt"
            	"math/rand"
            )
            
            func main() {
            	source := rand.NewSource(time.Now().UnixNano())
            	r := rand.New(source)
            	fmt.Println(r.Intn(100))
            
            	// 我更习惯于直接这样写
            	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
            	fmt.Println(rng.Intn(100))
            }
            ```

### 6.4 注意事项

- 线程安全性：`math/rand` 包的全局函数不是线程安全的。如果在多个 goroutine 中使用，建议为每个 goroutine 创建独立的随机数生成器实例。
- 密码学安全：`math/rand` 生成的随机数不适合用于安全相关的场景，如密码生成或加密秘钥。对于这些用途，应使用 `crypto/rand` 包。

### 6.5 生成随机字符串

下面是一个使用 `rand` 包生成随机字符串的示例：

```go
package main

import (
	"fmt"
	"math/rand"
	"time"
)

func main() {
	letters := []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
	s := make([]rune, 50)
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	for i := range s {
		s[i] = letters[rng.Intn(len(letters))]
	}
	fmt.Println(string(s))
}
```

### 6.6 总结

- 使用 `rand.Seed` 设置随机数种子，以避免每次运行产生相同的序列。
- 使用 `rand.Intn`、`rand.Float64` 等函数生成不同类型的随机数。
- 对于并发场景，使用 `rand.New` 创建独立的随机数生成器实例。
- 不要将 `math/rand` 用于安全敏感的随机数生成。

## 7. time

Go 语言的 `time` 包提供了丰富的时间处理功能，包括获取当前时间、格式化和解析时间、计时、延迟操作等。以下是 `time` 包的一些常用的函数和类型，以及它们的使用方法。

### 7.1 获取当前时间

`time.Now()`

返回当前的本地时间。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	currentTime := time.Now()
	fmt.Println("当前时间是：", currentTime)
}
```

### 7.2 时间格式化

`time.Time.Format(layout string)`

将时间格式化为制定的字符串格式。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	currentTime := time.Now()
	formattedTime := currentTime.Format("2006-01-02 15:04:05")
	fmt.Println("格式化后的时间是：", formattedTime)
}
```

注意：Go 语言使用特定的基准时间 `2006-01-02 15:04:05` 来定义格式。

### 7.3 解析时间字符串

`time.Parse(layout, value string)`

将指定格式的字符串解析为时间对象。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	timeStr := "2023-10-22 14:30:00"
	layout := "2006-01-02 15:04:05"
	parsedTime, err := time.Parse(layout, timeStr)
	if err != nil {
		fmt.Println("解析时间出错：", err)
	} else {
		fmt.Println("解析后的时间是：", parsedTime)
	}
}
```

### 7.4 时间延迟

`time.Sleep(d Duration)`

使当前进程暂停指定的时间。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("等待 2 秒...")
	time.Sleep(2 * time.Second)
	fmt.Println("继续执行")
}
```

### 7.5 计时器

`time.NewTimer(d Duration)`

创建一个计时器，在指定时间后触发。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	timer := time.NewTimer(time.Second)
	fmt.Println("计时器开始")
	<-timer.C
	fmt.Println("计时器结束")
}
```

### 7.6 定时执行

`time.NewTicker(d Duration)`

创建一个 Ticker，每隔指定时间触发一次。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	ticker := time.NewTicker(1 * time.Second)
	go func() {
		for t := range ticker.C {
			fmt.Println("当前时间：", t)
		}
	}()
	time.Sleep(5 * time.Second)
	ticker.Stop()
	fmt.Println("Ticker 已停止")
}
```

### 7.7 时间差计算

`time.Since(t Time)`

计算自指定时间以来的时间差。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	start := time.Now()
	time.Sleep(1 * time.Second)
	elapsed := time.Since(start)
	fmt.Println("经过时间：", elapsed)
}
```

### 7.8 时间戳

获取时间戳：

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	currentTime := time.Now()
	timestamp := currentTime.UnixNano()
	fmt.Println("当前时间戳：", timestamp)
}
```

从时间戳创建时间对象：

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	timestamp := int64(1234567890)
	timeObj := time.Unix(timestamp, 0)  // 参数：秒级时间戳和纳米级偏移量
	fmt.Println("时间对象：", timeObj)
}
```

### 7.9 时间比较

`t1.Before(t2)`

- 判断 `t1` 是否在 `t2` 之前。

`t1.After(t2)`

- 判断 `t1` 是否在 `t2` 之后。

`t1.Equal(t2)`

- 判断 `t1` 是否等于 `t2`。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	t1 := time.Now()
	t2 := t1.Add(10 * time.Second)
	fmt.Println("t1 在 t2 之前：", t1.Before(t2))
	fmt.Println("t1 在 t2 之后：", t1.After(t2))
	fmt.Println("t1 等于 t2：", t1.Equal(t2))
}
```

### 7.10 时区处理

`time.LoadLocation(name string)`

加载指定的时区。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	loc, err := time.LoadLocation("Asia/Shanghai")
	if err != nil {
		fmt.Println("加载市区出错：", err)
		return
	}
	timeInLoc := time.Now().In(loc)
	fmt.Println("上海时间：", timeInLoc)
}
```

### 7.11 时间加减

`t.Add(d Duration)`

在时间 `t` 上加上或减去指定的持续时间 `d`。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	now := time.Now()
	future := now.Add(2 * time.Hour)
	past := now.Add(-2 * time.Hour)
	fmt.Println("当前时间：", now)
	fmt.Println("2 小时后：", future)
	fmt.Println("2 小时前：", past)
}
```

### 7.12 获取时间的各个部分

`t.Year()`、`t.Month()`、`t.Day()`、`t.Hour()`、`t.Minute()`、`t.Second()`

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	t := time.Now()
	fmt.Printf("当前时间和时间：%d-%02d-%02d %02d:%02d:%02d\n", t.Year(), t.Month(), t.Day(), t.Hour(), t.Minute(), t.Second())
}
```

### 7.13 时间格式常量

`time` 包中定义了一些常用的时间格式常量，如 `time.TFC3339`、`time.RFC1123` 等。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	t := time.Now()
	fmt.Println("RFC3339 格式：", t.Format(time.RFC3339))
	fmt.Println("RFC1123 格式：", t.Format(time.RFC1123))
}
```

### 7.14 获取时间的纳秒、微秒和毫秒

`t.UnixNano()`

- 获取纳秒级时间戳。

`t.UnixMicro()`

- 获取微秒级时间戳。

`t.UnixMilli()`

- 获取毫秒级时间戳。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	t := time.Now()
	fmt.Println("纳秒级时间戳：", t.UnixNano())
	fmt.Println("微秒级时间戳：", t.UnixMicro())
	fmt.Println("毫秒级时间戳：", t.UnixMilli())
}
```

### 7.15 使用 `time.After` 和 `time.Tick`

`time.After(d Duration)`

返回一个通道，在指定时间后会接收到当前时间。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("等待 1 秒...")
	<-time.After(1 * time.Second)
	fmt.Println("时间到")
}
```

`time.Tick(d Duration)`

返回一个通道，每隔指定时间发送当前时间值。

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	tick := time.Tick(1 * time.Second)
	for i := 0; i < 5; i++ {
		t := <-tick
		fmt.Println("Tick at", t)
	}
}
```

## 8. io 与 bufio

在 Go 语言中，`io` 包和 `bufio` 包提供了许多用于处理输入和输出的函数的接口。它们主要用于文件、网络连接等数据流的读写操作，但 `bufio` 提供了更高效的缓冲 I/O 处理能力。以下是他们的常用函数和相关知识。

### 8.1 `io` 包常用函数与接口

`io` 包中定义了基础的 I/O 接口，提供文件、网络连接等的输入和输出操作。

**（1）`io.Reader` 和 `io.Writer` 接口**

- `io.Reader` 接口：用于读取数据。

    ```go
    type Reader interface {
        Read(p []byte) (n int, err error)
    }
    ```

    - `Read`：从数据源读取数据到给定的字节切片 `p`，返回读取的字节数和可能的错误。

- `Writer` 接口：用于写入数据。

    ```go
    type Writer interface {
        Write(p []byte) (n int, err error)
    }
    ```

    - `Write`：将字节切片 `p` 中的数据写入目标，返回写入的字节数和可能的错误。

**（2）`io.Copy`**

- `Copy(dst Writer, src Reader) (written int64, err error)`
    - 将 `src`（如文件或网络连接）中的数据写入 `dst`，返回写入的字节数和错误。
    - 通常用于从一个数据源（如文件或网络）复制数据到另一个地方。

**（3）`io.TeeReader`**

- `TeeReader(r Reader, w Writer) Reader`
    - 创建一个 `Reader`，读取数据时会同时写入 `Writer`，即分流读取的数据，常用于日志记录或调试。

**（4）`io.LimitReader`**

- `LimitReader(r Reader, n int64) Reader`
    - 限制从 `r` 读取的数据量，最多读取 `n` 字节。通常用于防止读取过多数据。

**（5）`io/ioutil.ReadFile`**

- `ReadFile(filename string) ([]byte, error)`
    - 一次性读取整个文件并返回内容，适合读取小型文件。

### 8.2 `bufio` 常用函数与结构体

`bufio` 包提供了缓冲输入和输出的能力，使得从 I/O 操作中读取或写入更加高效。

**（1）`bufio.Reader`**

`bufio.Reader` 为 `io.Reader` 提供了缓冲能力。常用于读取文件或网络数据时减少系统调用。

- `NewReader`：创建一个缓冲读取器，包装一个 `io.Reader`

    ```go
    r := bufio.NewReader(ioReader)
    ```

- `ReadLine`：读取一行数据，不包括行结束符。

    ```go
    line, isPrefix, err := r.ReadLine()
    ```

    - `isPrefix` 表示该行是否被截断（即行太长了，需要多次读取）。

- `ReadString`：读取直到指定的分隔符，返回读取到的字符串。

    ```go
    line, err := r.ReadString('\n')
    ```

- `Peek`：查看缓冲区中的数据，但不移动读取位置。

    ```go
    data, err := r.Peek(n)
    ```

    - 适合在决定对其多少数据之前“预览”数据。

**（2）`bufio.Writer`**

`bufio.Writer` 提供了缓冲写入功能，适合频繁的小数据写入时提高性能。

- `NewWriter`：创建一个缓冲写入器。

    ```go
    w := bufio.NewWriter(ioWriter)
    ```

- `WriteString`：向缓冲区写入字符串。

    ```go
    w.WriteString("Hello, World!")
    ```

- `Flush`：将缓冲区的数据强制写入底层 `Writer`。

    ```go
    w.Flush()
    ```

**（3）`bufio.Scanner`**

`Scanner` 是 `bufio` 中提供的一个用于分隔输入的简便方法，可以逐行扫描文件、网络等输入。

- `NewScanner`：创建一个扫描器，包装一个 `io.Reader`。

    ```go
    scanner := bufio.NewScanner(ioReader)
    ```

- `Scan`：扫描下一段内容（如一行或一个单词），返回 `bool`。

    ```go
    for scanner.Scan() {
        line := scanner.Text()
        // 处理 line
    }
    ```

### 8.3 总结

`bufio` 与 `io` 结合使用的典型场景：

- `bufio` 一般用于需要频繁读写的操作，比如逐行读取文件或网络数据，能有效减少系统调用的次数。
- `io` 是底层的接口和函数，用于实现通用的读写操作。

`io` 包为 Go 提供了基础的 I/O 操作接口，而 `bufio` 包进一步封装了缓冲的能力，能显著提供 I/O 的效率。根据应用场景选择合适的 `io.Reader`、`io.Writer` 以及 `bufio.Reader` 和 `bufio.Writer` 是编写高效 Go 程序的关键。

## 9. net

Go 语言的 `net` 包是标准库中用于网络编程的核心包之一，提供了跨平台的网络接口，包括 TCP、UDP、域名解析、Unix 域套接字功能。`net` 包使开发者能够方便地进行网络通信，构建各种网络应用程序，如 Web 服务器，聊天程序和文件传输工具。

### 9.1 基本概念

#### 9.1.1 `net.Conn` 接口

`net.Conn` 是一个通用的网络连接接口，代表了面向流的网络连接，如 TCP 连接。它定义了以下方法：

- `Read(b []byte) (n int, err error)`：从连接中读取数据。
- `Write(b []byte) (n int, err error)`：向连接中写入数据。
- `Close() error`：关闭连接。
- `LocalAddr() net.Addr`：返回本地网络地址。
- `RemoteAddr() net.Addr`：返回远程网络地址。
- `SetDeadLine(t time.Time) error`：设置读写操作的绝对时间期限。
- `SetReadDeadline(t time.Time) error`：设置读取操作的绝对时间权限。
- `SetWriteDeadline(t time.Time) error`：设置写入操作的绝对时间权限。

#### 9.1.2 `net.Listener` 接口

`net.Listener` 接口用于面向流的网络服务的侦听器，主要用于 TCP 服务器。它定义了以下方法：

- `Accept() (net.Conn, error)`：等待并返回下一个连接。
- `Close() error`：关闭侦听器。
- `Addr() net.Addr`：返回侦听器的网络地址。

#### 9.1.3 网络地址

`net.Addr` 接口表示网络地址。具体的实现有：

- `net.IPAddr`：IP 地址。
- `net.TCPAddr`：TCP 端口地址，包括 IP 和端口。
- `net.UDPAddr`：UDP 端口地址，包括 IP 和端口。

### 9.2 连接到服务器

#### 9.2.1 `net.Dial` 函数

`net.Dial` 用于连接到指定的网络地址，返回一个 `net.Conn` 接口。用法如下：

```go
conn, err := net.Dial("tcp", "localhost:8080")
```

参数：

- `network`：网络类型，如`"tcp"`、`"udp"`、`"unix"`。
- `address`：要连接的地址，格式因网络类型而异。

#### 9.2.2 `net.DialTCP` 和 `net.DialUDP`

这些函数用于创建 TCP 或 UDP 的网络连接，可以提供更多的控制选项，如指定本地地址。

```go
laddr, _ := net.ResolveTCPAddr("tcp", "localhost:0")
raddr, _ := net.ResolveTCPAddr("tcp", "localhost:8080")
conn, err := net.DialTCP("tcp", laddr, raddr)
```

### 9.3 创建服务器

#### 9.3.1 `net.Listen` 函数

`net.Listen` 用于创建指定网络和地址的监听器。

```go
listener, err := net.Listen("tcp", ":8080")
```

#### 9.3.2 `net.ListenTCP` 和 `net.ListenUDP`

这些函数用于创建 TCP 或 UDP 的侦听器。

```go
addr, _ := net.ResolveTCPAddr("tcp", ":8080")
listener, err := net.ListenTCP("tcp", addr)
```

### 9.4 TCP 编程示例

#### 9.4.1 TCP 服务器

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	listener, err := net.Listen("tcp", ":8080")
	if err != nil {
		fmt.Println("Error listening:", err)
		return
	}
	defer listener.Close()
	fmt.Println("Server is listening on port 8080")
	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println("Error accepting:", err)
			continue
		}
		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	buf := make([]byte, 1024)
	for {
		n, err := conn.Read(buf)
		if err != nil {
			fmt.Println("Error reading:", err)
			return
		}
		fmt.Printf("Receiced: %s\n", string(buf[:n]))
		conn.Write([]byte("Echo: " + string(buf[:n])))
	}
}
```

#### 9.4.2 TCP 客户端

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	conn, err := net.Dial("tcp", "localhost:8080")
	if err != nil {
		fmt.Println("Error dialing:", err)
		return
	}
	defer conn.Close()
	conn.Write([]byte("Hello, Server!"))
	buf := make([]byte, 1024)
	n, err := conn.Read(buf)
	if err != nil {
		fmt.Println("Error reading:", err)
		return
	}
	fmt.Printf("Received: %s\n", string(buf[:n]))
}
```

### 9.5 UDP 编程示例

#### 9.5.1 UDP 服务器

```go
package main

import (
    "fmt"
    "net"
)

func main() {
    addr, err := net.ResolveUDPAddr("udp", ":8080")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    conn, err := net.ListenUDP("udp", addr)
    if err != nil {
        fmt.Println("Error listening:", err)
        return
    }
    defer conn.Close()
    buf := make([]byte, 1024)
    for {
        n, clientAddr, err := conn.ReadFromUDP(buf)
        if err != nil {
            fmt.Println("Error reading:", err)
            continue
        }
        fmt.Printf("Received from %v: %s\n", clientAddr, string(buf[:n]))
        conn.WriteToUDP([]byte("Acknowledged"), clientAddr)
    }
}
```

#### 9.5.2 UDP 客户端

```go
package main

import (
    "fmt"
    "net"
)

func main() {
    serverAddr, err := net.ResolveUDPAddr("udp", "localhost:8080")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    conn, err := net.DialUDP("udp", nil, serverAddr)
    if err != nil {
        fmt.Println("Error dialing:", err)
        return
    }
    defer conn.Close()
    conn.Write([]byte("Hello UDP Server"))
    buf := make([]byte, 1024)
    n, _, err := conn.ReadFromUDP(buf)
    if err != nil {
        fmt.Println("Error reading:", err)
        return
    }
    fmt.Printf("Received: %s\n", string(buf[:n]))
}
```

### 9.6 域名解析

#### 9.6.1 `net.LookupIP`

用于将主机名解析为 IP 地址列表。

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	ips, err := net.LookupIP("www.baidu.com")
	if err != nil {
		fmt.Println("Error", err)
		return
	}
	for _, ip := range ips {
		fmt.Println("IP:", ip)
	}
}
```

#### 9.6.2 `net.LookupHost`

获取与主机名关联的地址。

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	hosts, err := net.LookupHost("8.8.8.8")
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	for _, host := range hosts {
		fmt.Println("Host:", host)
	}
}
```

### 9.7 网路接口

#### 9.7.1 获取网络接口列表

```go
package main

import (
	"fmt"
	"net"
)

func main() {
	interfaces, err := net.Interfaces()
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	for _, iface := range interfaces {
		fmt.Printf("Name: %s, MTU: %d\n", iface.Name, iface.MTU)
	}
}
```

#### 9.7.2 获取接口地址

```go
package main

import (
    "fmt"
    "net"
)

func main() {
    iface, err := net.InterfaceByName("WLAN")
    if err != nil {
       fmt.Println("Error:", err)
       return
    }
    addrs, err := iface.Addrs()
    if err != nil {
       fmt.Println("Error:", err)
       return
    }
    for _, addr := range addrs {
       fmt.Println("Address:", addr.String())
    }
}
```

### 9.8 设置超时

#### 9.8.1 `SetDeadline`

为连接设置读写操作的超时时间。

```go
conn.SetDeadline(time.Now().Add(5 * time.Second))
```

#### 9.8.2 `SetReadDeadline` 和 `SetWriteDeadline`

分别设置读取和写入操作的超时时间。

```go
conn.SetReadDeadline(time.Now().Add(2 * time.Second))
conn.SetWriteDeadline(time.Now().Add(3 * time.Second))
```

## 10. regexp

在 Go 语言中，`regexp` 包用于处理正则表达式，提供了强大的字符串匹配和操作功能。正则表达式是一种用于定义字符串模式的语言，可以方便地进行复杂的字符串搜索、替换和验证。

### 10.1 基础知识

正则表达式的基本结构是由字符和元字符组成的模式，用于描述字符串匹配规则。以下是一些常用的正则表达式元字符及其含义：

- `.`：匹配单个字符（不包含换行符）
- `^`：匹配字符串的开头。
- `$`：匹配字符串的结尾。
- `*`：匹配前一个字符零次或多次。
- `+`：匹配前一个字符一次或多次。
- `?`：匹配前一个字符零次或一次。
- `[]`：匹配字符集中任意单个字符，例如 `[a-z]` 匹配任意小写字母。
- `|`：或操作符，表示匹配左边或右边的模式。
- `()`：分组，用于捕获匹配的子串。
- `\`：转义字符，用于转义元字符，例如 `\.` 匹配一个点号

### 10.2 Go 中 `regexp` 包的使用

在 Go 语言中，`regexp` 包提供了一些常用函数和方法来处理正则表达式：

#### 10.2.1 Compile 和 MustCompile

这两个函数用于编译正则表达式，其中 `MustCompile` 会在编译失败时引发 panic。

```go
package main

import (
	"fmt"
	"regexp"
)

func main() {
	// Compile 正则表达式
	re, err := regexp.Compile(`\d+`)
	if err != nil {
		fmt.Println("正则表达式编译失败：", err)
		return
	}
	fmt.Println(re)
}
```

#### 10.2.2 常用方法

- MatchString：用于判断字符串是否匹配正则表达式。
- FindString：查找第一个匹配的子串。
- FindAllString：查找所有匹配的子串。
- ReplaceAllString：替换匹配的子串。
- Split：按正则表达式分割字符串。

```go
package main

import (
	"fmt"
	"regexp"
)

func main() {

	re := regexp.MustCompile(`\d+`)

	// 判断字符串是否匹配
	match := re.MatchString("123abc")
	fmt.Println("是否匹配:", match) // 输出: true

	// 查找第一个匹配的子串
	result := re.FindString("abc123def456")
	fmt.Println("第一个匹配的子串:", result) // 输出: 123

	// 查找所有匹配的子串
	results := re.FindAllString("abc123def456ghi789", -1)
	fmt.Println("所有匹配的子串:", results) // 输出: [123 456 789]

	// 替换匹配的子串
	replaced := re.ReplaceAllString("abc123def456", "X")
	fmt.Println("替换结果:", replaced) // 输出: abcXdefX

	// 按正则表达式分割字符串
	parts := re.Split("abc123def456ghi789", -1)
	fmt.Println("分割结果:", parts) // 输出: [abc def ghi]
}
```

### 10.3 高级用法

#### 10.3.1 分组和捕获

正则表达式可以使用 `()` 进行分组捕获，Go 语言中的 `FindStringSubmatch` 和 `SubexpNames` 可以用来获取捕获的子字符串和名称。

```go
package main

import (
	"fmt"
	"regexp"
)

func main() {
	re := regexp.MustCompile(`(?P<areaCode>\d{3})-(?P<number>\d{7})`)

	// 获取匹配的子串
	match := re.FindStringSubmatch("电话：010-1234567")
	fmt.Println("匹配的子串：", match) // 输出：[010-1234567 010 1234567]

	// 获取命名的子匹配项
	for i, name := range re.SubexpNames() {
		if i != 0 && name != "" {
			fmt.Printf("%s: %s\n", name, match[i])
		}
	}
	// 输出：
	// areaCode: 010
	// number: 1234567
}
```

#### 10.3.2 匹配替换

使用 `ReplaceAllStringFunc` 可以通过自定义函数来替换匹配的字符串。

```go
package main

import (
	"fmt"
	"regexp"
)

func main() {
	re := regexp.MustCompile(`\d+`)

	// 使用自定义函数替换匹配项
	replaced := re.ReplaceAllStringFunc("价格是 100 元，折扣后是 80 元", func(s string) string {
		return "[" + s + "]"
	})

	fmt.Println("替换结果是：", replaced) // 输出：替换结果是： 价格是 [100] 元，折扣后是 [80] 元
}
```

### 10.4 贪婪模式和非贪婪模式

在 Go 语言中，正则表达式匹配中的贪婪模式和非贪婪模式是用于控制匹配字符串的行为。

#### 10.4.1 贪婪模式

- 定义：在默认情况下，正则表达式的量词（如 `*`、`+`、`{n,m}`）是贪婪的。

- 行为：贪婪模式会尽可能多地匹配字符，直到不能再匹配为止。它会试图匹配尽可能长的字符串。

- 例子：

    ```go
    package main
    
    import (
    	"fmt"
        "regexp"
    )
    
    func main() {
        re := regexp.MustCompile(`a.*b`)
        match := re.FindString("a123b456b")
        fmt.Println(match)  // 输出 "a123b456b"
    }
    ```

    在这个例子中，正则表达式 `a.*b` 使用了贪婪模式，`.*` 会匹配尽可能多的字符，因此最终匹配的是 `"a123b456b"`。

#### 10.4.2 非贪婪模式

- 定义：如果在量词后面加上一个 `?`，量词就会变成非贪婪的。

- 行为：非贪婪模式会尽可能少地匹配字符，即它会尝试匹配尽可能短地字符串。

- 例子：

    ```go
    package main
    
    import (
    	"fmt"
        "regexp"
    )
    
    func main() {
        re := regexp.MustCompile(`a.*?b`)
        match := re.FindString("a123b456b")
        fmt.Println(match)  // 输出 "a123b"
    }
    ```

    #### 10.4.3 总结

    - 贪婪模式：`*`、`+`、`{n,m}` 等，匹配可能多的字符。
    - 非贪婪模式：`*?`、`+?`、`{n,m}?` 等，匹配尽可能少的字符。

### 10.5 注意事项

- 正则表达式中需要使用反斜杠 `\` 进行转义，在 Go 中的字符串中需要写成 `\\`，例如 `\d` 需要写成 `\\d`。
- `regexp` 包的匹配操作默认是贪婪模式，可以使用 `?` 切换为非贪婪模式，例如 `.*?`。

## 11. log

Go 语言中的 `log` 包是一个基础的日志记录工具，提供简单的日志记录功能，用于输出日志信息。`log` 包可以让我们轻松记录程序的运行状态、调试信息和错误信息。

### 11.1 基本用法

`log` 包提供了基础的日志记录方法，包括以下几个常用方法：

- Print 系列：输出一般信息
    - `log.Print()`：输出一般信息，并带有日期和时间。
    - `log.Printf()`：格式化输出日志信息。
    - `log.Println()`：输出信息并自动换行。
- Fatal 系列：输出错误信息，并在日志输出后终止程序
    - `log.Fatal()`：记录日志后调用 `os.Exit(1)` 退出程序。
    - `log.Fatalf()`：格式化输出日志信息，并终止程序。
    - `log.Fatalln()`：输出错误信息，自动换行并终止程序。
- Panic 系列：输出错误信息，并爆出一个 panic。
    - `log.Panic()`：输出日志信息，并触发一个 panic。
    - `log.Panicf()`：格式化输出日志信息，并触发 panic。
    - `log.Panicln()`：输出日志信息，自动换行，并触发 panic。

### 11.2 配置日志输出

可以使用 `log.SetFlags()` 和 `log.SetPrefix()` 来定义日志的输出格式和前缀。

- SetFlags：指定日志的输出内容格式（如时间戳、文件名、行号等）。
    - 常用的标志位包括：
        - `log.Ldata`：日期（格式：2009/01/23）
        - `log.Ltime`：时间（格式：01:23:23）
        - `log.Lmicroseconds`：微秒级时间戳
        - `log.Llongfile`：完整文件路径和行号
        - `log.Lshortfile`：短文件路径和行号（仅文件名）
        - `log.LUTC`：使用 UTC 时间而非本地时间
- SetPrefix：指定日志的前缀，一般用于区别不同类型的日志。

例如：

```go
package main

import "log"

func main() {
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
	log.SetPrefix("[INFO] ")
	log.Println("这是一个日志示例")
}
// 输出：
// [INFO] 2024/10/29 14:19:18 main.go:8: 这是一个日志示例
```

### 11.3 日志输出到文件

默认情况下，`log` 包会将日志输出到标准输出（`os.Stdout`）。可以通过将输出目标设置为文件来将日志写入文件：

```go
package main

import (
	"log"
	"os"
)

func main() {
	file, err := os.OpenFile("app.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		log.Fatal("无法打开日志文件", err)
	}
	log.SetOutput(file)
	log.Println("这是写入文件的日志。")
}
```

### 11.4 自定义 Logger

可以创建 `Logger` 对象来实现不同的日志记录器，便于在用一项目中管理多种类型的日志。

```go
package main

import (
	"log"
	"os"
)

func main() {
	file, err := os.OpenFile("app.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		log.Fatal("无法打开日志文件", err)
	}
	log.SetOutput(file)
	log.Println("这是写入文件的日志。")

	logger := log.New(file, "[CUSTOM] ", log.Ldate|log.Ltime|log.Lshortfile)
	logger.Println("自定义日志记录器")
}
```

### 11.5 log 包的局限性

`log` 包的功能简单，无法满足复杂的日志需求。对于高级日志需求（如日志分级、日志切割、异步记录等），可以使用第三方日志库，如 `zap` 或 `logrus`。

## 12. sort

Go 语言中的 `sort` 包提供了一系列函数和接口，用于对数据进行排序操作。这个包的核心功能包括基本类型的排序，如整数、浮点数、字符串的排序，适用于更复杂的数据结构。下面是 `sort` 包的主要是内容和用法：

### 12.1 常用的排序函数

`sort` 包为内置的基本数据类型提供了以下排序函数：

- `sort.Ints(slice []int)`：对 `[]int` 类型的切片进行升序排序。
- `sort.Float64s(slice []float64)`：对 `[]float64` 类型的切片进行升序排序。
- `sort.Strings(slice []string)`：对 `[]string` 类型的切片进行升序排序。

使用这些函数时，无需额外设置排序方式，直接调用即可，例如：

```go
package main

import (
	"fmt"
	"sort"
)

func main() {
	numbers := []int{3, 1, 4, 1, 5, 9}
	sort.Ints(numbers)
	fmt.Println(numbers)
}
```

### 12.2 检查排序状态

`sort` 包还提供了相应的检查函数，用于判断切片是否已按升序排序：

- `sort.IntAreSorted(slice []int)`：检查 `[]int` 类型的切片是否已排序。
- `sort.Float64AreSorted(slice []float64)`：检查 `[]float64` 类型的切片是否已排序。
- `sort.StringsAreSorted(slice []string)`：检查 `[]string` 类型的切片是否已排序。

```go
package main

import (
	"fmt"
	"sort"
)

func main() {
	numbers1 := []int{3, 1, 4, 1, 5, 9}
	numbers2 := []int{1, 2, 3, 4, 5, 6}
	fmt.Println(sort.IntsAreSorted(numbers1))  // 输出：false
	fmt.Println(sort.IntsAreSorted(numbers2))  // 输出：true
}
```

### 12.3 自定义排序

对于复杂的数据结构，如结构体切片，Go 允许通过实现接口来定义排序规则。自定义排序的关键是实现 `sort.Interface` 接口中的三个方法：

- `len()`：返回元素的数量。
- `Less(i, j int)`：定义索引 `i` 和 `j` 的比较规则，若 `i` 小于 `j` 则返回 `true`。
- `Swap(i, j int)`：交换索引 `i` 和 `j` 的位置。

例如，假设有一个 `Person` 结构体切片，我们希望按年龄升序排序：

```go
package main

import (
	"fmt"
	"sort"
)

type Person struct {
	Name string
	Age  int
}

// 定义一个类型 People 来实现 sort.Interface
type People []Person

func (p People) Len() int           { return len(p) }
func (p People) Less(i, j int) bool { return p[i].Age < p[j].Age }
func (p People) Swap(i, j int)      { p[i], p[j] = p[j], p[i] }

func main() {
	people := People{
		{"Alice", 30},
		{"Bob", 25},
		{"Charlie", 35},
	}
	sort.Sort(people)
	fmt.Println(people)
}
```

### 12.4 降序排序

`sort` 包内置的排序方法默认是升序。如果想降序，可以借助 `sort.Reverse` 函数将排序逻辑反转。

```go
package main

import (
	"fmt"
	"sort"
)

type Person struct {
	Name string
	Age  int
}

// 定义一个类型 People 来实现 sort.Interface
type People []Person

func (p People) Len() int           { return len(p) }
func (p People) Less(i, j int) bool { return p[i].Age < p[j].Age }
func (p People) Swap(i, j int)      { p[i], p[j] = p[j], p[i] }

func main() {
	people := People{
		{"Alice", 30},
		{"Bob", 25},
		{"Charlie", 35},
	}
	sort.Sort(people)
	fmt.Println(people)
	sort.Sort(sort.Reverse(people))
	fmt.Println(people)
}
```

### 12.5 `sort.Slice` 和 `sort.SliceStable`

在 Go 1.8 中引入了 `sort.Slice` 和 `Sort.SliceStable` 函数，可以使用匿名函数快速对切片进行排序，适合临时排序需求。

- `sort.Slice(slice, func(i, j int) bool)`：传入切片和自定义比较函数。
- `sort.SliceStable(slice, func(i, j int) bool)`：与 `sort.Slice` 类似，但保证排序稳定性（相同值的顺序不变）。

例如按年龄降序排序：

```go
sort.Slice(people, func(i, j int) bool {
    return people[i].Age > people[j].Age
})
```

### 12.6 `sort.Search` 函数

`sort.Search` 提供了二分查找功能，前提是切片已按升序排序。

```go
package main

import (
	"fmt"
	"sort"
)

func main() {
	x := []int{1, 2, 3, 4, 5, 6, 7}
	index := sort.Search(len(x), func(i int) bool {
		return x[i] >= 4
	})
	fmt.Println(index) // 输出：3（对应值 4 的索引）
}
```

## 13. context

在 Go 语言中，`context` 包用于管理处理并发操作时的超时、取消以及请求范围内的数据共享等需求。它在网络编程、RPC、数据库查询等涉及超时控制和取消操作的场景中尤为重要。

### 13.1 `context` 包的主要概念

`context` 包中的核心是 `Context` 接口，它提供了一种机制，允许在 Goroutines 之间传递超时、取消信号和请求范围内的值。`Context` 本质上是一种只读的依赖对象，允许对长时间运行的操作进行管理。它主要包含以下几个方法：

- `Done() <-chan struct{}`：取消一个 channel，当该 channel 被关闭时表示 context 被取消。
- `Err() error`：返回 `Done` 关闭的原因，通常是 `context.Canceld` 或 `context.DeadlineExceeded`。
- `Deadline() (deadline time.Time, ok bool)`：返回 context 的截止时间和是否设置了截止时间。
- `Value(key interface{}) interface{}`：允许存储和访问请求范围内的值。

### 13.2 常用的 Context 类型

Go 中的 `context` 包提供了几种创建 context 的常用方法：

- `context.Background()`：返回一个空的 context，通常作为顶级 context 使用，它不会被取消、没有超时，且不携带任何值。适用于没有请求范围或生命周期控制的 Goroutine 启动。
- `context.TODO()`：当不确定要使用什么类型的 context 时可以使用 `TODO`，它类似于 `Background`，但表示代码仍需进一步改进或完善。
- `context.WithCancel(parent Context)`：基于父 context 创建一个可取消的 context，并返回一个 `cancel` 函数。调用 `cancel` 时会关闭 `Done` 通道，通知由该 context 派生的所有 goroutine 取消操作。
- `context.WithTimeout(parent Context, timeout time.Duration)`：创建一个带超时的 context。超时结束或 `cancel` 调用时，context 自动取消。适合需要在特定时间内完成的操作。
- `context.WithDeadline(parent Context, deadline time.Time)`：指定一个具体时间点作为截止时间，类似于 `WithTimeout`， 但通过绝对时间设置。
- `context.WithValue(parent Context, key, value interface{})`：在 context 中存储键值对，可用于在请求范围内传递特定的数据，但一般避免传递大对象或敏感数据。

### 13.3 `context` 包的应用场景

- 超时控制：在网络请求、数据库查询等场景中，防止因无响应而导致资源被占用，确保操作在一定时间内完成，否则取消。
- 任务取消：在需要控制并发操作的 Goroutine 或子任务时，通过 context 传递取消信号，实现任务的停止。
- 数据共享：在请求生命周期中传递请求范围内的数据，如用户身份信息、请求 ID 等。

### 13.4 示例代码

以下是一个使用 `context` 包的简单示例，在其中控制一个网络请求的超时和取消。

```go
package main

import (
	"context"
	"fmt"
	"net/http"
	"time"
)

func main() {
	// 设置一个超时为 2 秒的 context
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel() // 在函数退出时取消 context

	// 创建请求并将 context 传递给 HTTP 客户端
	req, err := http.NewRequestWithContext(ctx, "GET", "https://baidu.com", nil)
	if err != nil {
		fmt.Println("创建请求失败：", err)
		return
	}

	// 执行请求
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		// 超时或被取消时会捕获到错误
		fmt.Println("请求失败：", err)
		return
	}
	defer resp.Body.Close()
	fmt.Println("请求成功，状态码：", resp.StatusCode)

}
```

在这个示例中，`WithTimeout` 确保请求在 2 秒后自动取消，如果网络相应较慢，则会触发超时错误。这样可以避免 Goroutine 一直等待。

### 13.5 注意事项

- `context` 不适合在 `Value` 中存储大的数据结构或敏感信息，应仅传递请求范围的轻量级信息。
- 确保在不再需要 context 时调用 `cancel` 函数，以防资源泄露。
- 尽量避免在库函数中直接创建 context，而应由调用方传入。

通过 `context` 包，可以更好地管理 Goroutine 的生命周期和控制操作的超时，为并发编程提供更加灵活和可靠的控制方式。

## 14. sync

在 Go 语言中，`sync` 包主要用于处理并发编程时的同步问题，提供了多种常用的同步工具，例如互斥锁（`Mutex`）、读写锁（`RWMutex`）、等待组（`WaitGroup`）、一次性执行（`Once`）等。这些工具帮助我们在多 goroutine 的场景下安全、有效地进行数据共享和任务协作。

### 14.1 互斥锁（Mutex）

- 类型 `sync.Mutex`

- 作用：互斥锁用于保护临界区，确保同一时刻只有一个 goroutine 访问某个资源。

- 方法：

    - `Lock()`：锁定互斥锁。
    - `Unlock()`：解锁互斥锁。

- 用法：

    ```go
    var mu sync.Mutex
    var count int
    
    func increment() {
        mu.Lock()
        count++
        mu.Unlock()
    }
    ```

- 注意：使用 `Mutex` 时务必注意 `Unlock` 的执行，常用 `defer` 语句避免遗忘。

### 14.2 读写锁

- 类型：`sync.RWMutex`

- 作用：读写锁用于允许多个读操作并发执行，但写操作会互斥，保证读操作可以高效地并发执行，同时确保写操作的唯一性。

- 方法：

    - `RLock()` 和 `RUnlock()`：用于锁定 / 解锁读操作。
    - `Lock()` 和 `Unlock()`：用于锁定 / 解锁写操作。

- 用法：

    ```go
    var rw sync.RWMutex
    var data int
    
    func read() int {
        rw.RLock()
        defer rw.Runlock()
        return data
    }
    
    func write(value int) {
        rw.Lock()
        data = value
        rw.Unlock()
    }
    ```

- 注意：读写锁有助于提高读操作较多时的性能，适合读多写少的场景。

### 14.3 等待组（WaitGroup）

- 类型：`sync.WaitGroup`

- 作用：等待一组 goroutine 完成工作，尤其适合并行执行多个任务，等待所有任务完成后再继续后续逻辑。

- 方法：

    - `Add(delta int)`：设置要等待的 goroutine 数量。
    - `Done()`：表示一个 goroutine 已完成工作。
    - `Wait()`：阻塞等待所有 goroutine 完成。

- 用法：

    ```go
    var wg sync.WaitGroup
    
    func worker() {
        defer wg.Done()
        // 执行工作
    }
    
    func main() {
        for i := 0; i < 3; i++ {
            wg.Add(1)
            go worker()
        }
        wg.Wait()  // 等待所有 goroutine 完成
    }
    ```

### 14.4 一次性执行（Onece）

- 类型：`sync.Once`

- 作用：确保某个操作只会被执行一次，例如初始化操作等。

- 方法：

    - `Do(func())`：仅在首次调用时执行传入的函数，之后的调用都会忽略。

- 用法：

    ```go
    var once sync.Once
    
    func initialize() {
        fmt.Println("初始化操作")
    }
    
    func main() {
        once.Do(initialize)
        // 无论调用多少次 once.Do(initialize)，initialize 都只会执行一次
    }
    ```

### 14.5 条件变量（Cond）

- 类型：`sync.Cond`

- 作用：协调 goroutine 的执行，通过条件变量进行 goroutine 的等待和通知。

- 方法：

    - `Wait()`：使当前 goroutine 进入等待状态，直到被 `Signal` 或 `Broadcast` 唤醒。
    - `Signal()`：唤醒一个等待的 goroutine。
    - `Broadcast`：唤醒所有等待的 goroutine。

- 用法：

    ```go
    package main
    
    import (
    	"fmt"
    	"sync"
    	"time"
    )
    
    var cond = sync.NewCond(&sync.Mutex{}) // 创建条件变量
    var ready = false                      // 控制条件
    
    // 模拟等待的 goroutine
    func waitForReady(id int) {
    	cond.L.Lock() // 加锁，确保线程安全
    	defer cond.L.Unlock()
    	for !ready { // 如果 ready 为 false，进入等待
    		fmt.Printf("Goroutine %d 等待条件满足...\n", id)
    		cond.Wait() // 调用 cond.Wait（） 时，它会自动释放锁，使其他 goroutine 能够获得锁并检查或修改条件
    	}
    	fmt.Printf("Goroutine %d 完成等待，继续执行...\n", id)
    }
    
    func main() {
    	// 启动多个等待的 goroutine
    	for i := 1; i <= 3; i++ {
    		go waitForReady(i)
    	}
    
    	time.Sleep(2 * time.Second) // 模拟一些准备操作
    	fmt.Println("准备工作完成，通知所有等待的 goroutine...")
    
    	// 改变条件并通知所有等待的 goroutine
    	cond.L.Lock()
    	ready = true
    	cond.Broadcast() // 广播唤醒所有等待的 goroutine
    	cond.L.Unlock()
    
    	time.Sleep(time.Second) // 防止主函数提前结束
    }
    ```

## 15. runtime

Go 语言的 `runtime` 包是核心包之一，提供了与 Go 语言运行时系统交互的低级函数和功能。`runtime` 包不仅涵盖了内存管理和垃圾回收，还提供了与协程、系统线程、调度器等关键机制的接口。以下是一些 `runtime` 包的重要内容：

1. **内存管理**
    - `runtime` 包中有许多与内存分配和管理相关的功能。Go 中的内存分配采用了 TCMalloc 算法的变体，通过 `runtime.mallocgc` 函数完成。
    - Go 会自动进行垃圾回收（GC），`runtime.GC` 函数可以手动触发一次垃圾回收，但通常不需要手动调用一次垃圾回收，但通常不需要手动调用，因为 Go 运行时会自动触发。
    - 可以通过 `runtime.ReadMemStats` 查看当前内存的使用统计信息，包含了堆内存大小、已分配的对象数和下一次 GC 的触发阈值等信息。
2. **协程管理**
    - `runtime` 包对协程（goroutine）的管理是其核心功能之一。`go` 关键字会自动调用 `runtime.newproc` 生成新的进程。
    - `runtime.Goexit`：终止当前的协程，不影响其他协程的执行，且会调用所有已注册的 `defer` 函数。
    - `runtime.Gosched`：将当前协程的控制权交还给调度器，以便让其他协程执行。
3. **调度器**
    - Go 语言使用 GPM 模型进行协程调度：G（goroutine）、P（Processor）和 M（Machine）。其中，G 是协程、P 是逻辑处理器、M 是 OS 线程。
    - `runtime.GOMAXPROCS`：控制可以同时执行的最大线程数，这会直接影响并发性能。默认值是 CPU 核心数，但可以通过此函数修改。
4. **垃圾回收（GC）**
    - Go 使用并发标记-清除算法进行垃圾回收。`runtime` 包允许控制 GC 的一些细节。
    - `runtime.SetGCPercent`：设置 GC 的触发百分比，默认是 100，即允许垃圾增加到内存的一半时触发 GC。
    - `runtime.GC`：手动触发垃圾回收。
    - `runtime.KeepAlive`：将对象标记为活动状态，以防止过早被回收。
5. **系统相关**
    - `runtime.Caller`：获取当前调用栈的信息，常用于错误处理和日志。
    - `runtime.Callers`：获取当前协程的调用栈，以便于详细调试和分析。
    - `runtime.NumCPU`：返回可用的 CPU 核心数。
    - `runtime.NumGoroutine`：返回当前运行的核心数量。
6. **时间控制**
    - `runtime.nanotime`：获取当前时间戳，单位为纳秒。
    - `runtime.timer` 和 `runtime.sleep`：为时间操作提供支持，例如延迟某些操作或创建定时器。
7. **跨平台支持**
    - `runtime` 包帮助 Go 在不同操作系统上实现一致的表现。Go 运行时包含了大量平台相关的实现，例如对不同平台的系统调用支持和调度策略调整。
8. **调试和分析**
    - `runtime.SetFinalizer`：为对象设置终结器，方便在垃圾回收时触发一些清理操作。
    - `runtime.MemProfile` 和 `runtime.BlockProfile` 等方法可以生成内存和阻塞性能的分析数据。

**示例：**

可以使用 `runtime` 的一些函数来检查内存和协程状态：

```go
package main

import (
	"fmt"
	"runtime"
)

func main() {
	// 打印内存使用情况
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)
	fmt.Printf("Allocated memory: %v KB\n", memStats.Alloc/1024)

	// 打印当前的协程数量
	fmt.Printf("Goroutine count: %d\n", runtime.NumGoroutine())

	// 手动触发 GC
	runtime.GC()
	fmt.Println("Manually triggered garbage collection")
}
```

执行结果：

```go
[root@toby runtime]# ./main
Allocated memory: 62 KB
Goroutine count: 1
Manually triggered garbage collection
```





































