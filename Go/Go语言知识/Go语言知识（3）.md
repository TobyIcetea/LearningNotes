# Go语言知识（3）

## 17. select

在 Go 语言中，`select` 语句用于处理多个通道（channel）的发送和接收操作，类似于 `switch` 语句，但它专门用于处理通道的操作。它允许一个 goroutine 等待多个通道操作中的任意一个完成，从而实现多路复用。

**`select` 语句的基本结构：**

```go
select {
case <-ch1:
    // 当 ch1 收到数据时执行的代码
case data := <-ch2:
    // 当 ch2 收到数据时执行的代码，并将数据赋值给 data
case ch3 <- value:
    // 向 ch3 发送 value，当发送成功时执行的代码
default:
    // 如果没有通道操作可以进行，执行 default 中的代码
}
```

**工作原理：**

1. 等待多个通道：`select` 语句会阻塞，直到其中一个通道准备好进行操作（发送或接收）。
2. 随机选择：如果多个通道同时准备好，`select` 会随机选择其中一个进行操作。
3. 默认情况：如果没有任何通道准备好，且存在 `default` 分支，则会执行 `default` 中的代码，而不会被阻塞。

**示例：**

下面是一个简单的示例，演示如何使用 `select` 语句来处理多个通道：

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	ch1 := make(chan string)
	ch2 := make(chan string)

	go func() {
		time.Sleep(1 * time.Second)
		ch1 <- "来自 ch1"
	}()

	go func() {
		time.Sleep(2 * time.Second)
		ch2 <- "来自 ch2"
	}()

	for i := 0; i < 2; i++ {
		select {
		case msg1 := <-ch1:
			fmt.Println(msg1)
		case msg2 := <-ch2:
			fmt.Println(msg2)
		}
	}
}
```

在这个例子中，我们创建了两个通道 `ch1` 和 `ch2`，分别在两个 goroutine 中发送消息。`select` 语句等待其中一个通道接收消息，并在收到时打印出来。

**管道与 `select`：**

在使用管道时，`select` 非常有用，尤其是在需要处理并发操作时。例如，你可能有多个工作者 goroutine，它们通过管道将结果发送到一个结果通道。你可以使用 `select` 来接受这些结果，而不必检查每个管道的状态。

**实际应用：**

- 超时处理：可以结合 `time.After` 使用 `select` 来实现超时功能。
- 多个任务的结果收集：在并发处理多个任务时，使用 `select` 可以方便地收集不同任务的结果。

## 18. AES 加密数据

AES 加密和解密的时候，都需要提供一个 Stream，其中这个 Stream 包含两个东西：

- Key：真正的加密密钥，用于加密 / 解密数据。必须保密！
- IV：初始化向量，确保相同明文加密效果不同，增强安全性。不用保密！

其中，Key 是我们加密的时候需要牢记的，但是 IV 在加密的时候，是随机生成的。在解密的时候，这个 IV（盐值）可以直接从加密包上获取，不是什么保密的事情。但是通过这个随机的盐值，我们可以保证，对同一段文本每次加密后的密文都是不同的，从而一定程度上保证了数据的安全性。

总之，加密和解密的时候都只需要提供 AES 的 Key 即可。

```go
package main

import (
	"compress/gzip"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"io"
	"os"
)

// 加密并压缩数据
func encryptAndCompress(inputFile, outputFile string, key []byte) error {
	// 打开输入文件
	inFile, err := os.Open(inputFile)
	if err != nil {
		return err
	}
	defer inFile.Close()

	// 创建输出文件
	outFile, err := os.Create(outputFile)
	if err != nil {
		return err
	}
	defer outFile.Close()

	// 创建 AES 加密快
	block, err := aes.NewCipher(key)
	if err != nil {
		return err
	}

	// 生成随机 IV (Initialization Vector)
	iv := make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return err
	}

	// 写入 IV 到输出文件
	if _, err := outFile.Write(iv); err != nil {
		return err
	}

	// 创建加密流
	stream := cipher.NewCFBEncrypter(block, iv)

	// 创建 Gzip 写入器
	gzipWriter := gzip.NewWriter(outFile)
	defer gzipWriter.Close()

	// 创建加密写入器
	writer := &cipher.StreamWriter{S: stream, W: gzipWriter}

	// 复制数据: 输入文件 -> 加密 -> 压缩 -> 输出文件
	if _, err := io.Copy(writer, inFile); err != nil {
		return err
	}

	return nil
}

// 解密并解压数据
func decryptAndDecompress(inputFile, outputFile string, key []byte) error {
	// 打开输入文件
	inFile, err := os.Open(inputFile)
	if err != nil {
		return nil
	}
	defer inFile.Close()

	// 创建输出文件
	outFile, err := os.Create(outputFile)
	if err != nil {
		return nil
	}
	defer outFile.Close()

	// 创建 AES 加密快
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil
	}

	// 读取 IV
	iv := make([]byte, aes.BlockSize)
	if _, err := inFile.Read(iv); err != nil {
		return err
	}

	// 创建解密流
	stream := cipher.NewCFBDecrypter(block, iv)

	// 创建 Gzip 读取器
	gzipReader, err := gzip.NewReader(inFile)
	if err != nil {
		return nil
	}
	defer gzipReader.Close()

	// 创建解密读取器
	reader := &cipher.StreamReader{S: stream, R: gzipReader}

	// 复制数据: 输入文件 -> 解压 -> 解密 -> 输出文件
	if _, err := io.Copy(outFile, reader); err != nil {
		return err
	}

	return nil
}

func main() {
	key := []byte("examplekey123456") // 16 字节的 AES 密钥

	// 加密并压缩
	err := encryptAndCompress("input.txt", "output.gz.aes", key)
	if err != nil {
		panic(err)
	}

	// 解密并解压
	err = decryptAndDecompress("output.gz.aes", "output.txt", key)
	if err != nil {
		panic(err)
	}
}
```







