# crypto

## 介绍

crypto 中包含了很多密码学相关的模块，提供了一些常见的密码学算法和工具。

## 哈希部分：SHA256

### 介绍

哈希值主要有以下几个特点：

- 确定性：对于同一份数据，对应的哈希值是确定的。
- 雪崩效应：只要改其中一个字节，哈希值会完全变样。
- 抗碰撞：几乎找不到两份数据的哈希值是相同的。
- 单向性：无法从哈希值反推出元数据的样子。

SHA（Secure Hash Algorithm）安全哈希算法中有很多小的哈希算法，SHA256 是比较常用的一种，它的意思是输出的长度固定是 32 字节（256 位）。

golang 将 SHA256 实现封装在标准库 `crypto/sha256` 中，功能是计算 SHA-256 的哈希值。它有两种使用方式：

- 一次性计算小数据的哈希值：`sha256.Sum256(data []byte)`，这种方法是很简单直接的。
- 流式处理大数据：先用 `sha256.New()` 创建一个哈希器，之后将数据分多次 `Write()` 进去，最后再一块儿计算哈希值。这种方法是分块写入数据，适合文件、网络流。

### 计算字符串的 SHA-256

计算一个简单字符串的哈希值。直接使用 API `sha256.Sum256([]byte)` 获得 SHA256 的哈希值。

```go
func main() {
	// 1. 准备输入数据（字符串转为 []byte）
	input := "hello world"
	data := []byte(input)

	// 2. 计算 SHA-256 哈希值（返回 [32]byte 类型）
	hash := sha256.Sum256(data)

	// 3. 将哈希值转为十六进制字符串
	hashHex := fmt.Sprintf("%x", hash)

	// 4. 打印结果
	fmt.Printf("输入：%s\n", input)
	fmt.Printf("SHA-256 哈希值：%s\n", hashHex)
	fmt.Printf("长度：%d 字节（%d 位）\n", len(hash), len(hash)*8)
}
```

输出：

```go
输入：hello world
SHA-256 哈希值：b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
长度：32 字节（256 位）
```

### 处理文件的 SHA256

其中主要使用的 API：

- `sha256.New()`：创建一个哈希器（`Writer`）。
- `sha256.Write()` 或者 `io.Copy(hasher, file)` 等方式，向这个 `Writer` 中写数据。
- `hasher.Sum(nil)`，计算最终的哈希值，`nil` 表示不附加额外数据。

```go
func main() {
	// 1. 打开文件
	file, err := os.Open("main.go")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	// 2. 创建 SHA-256 写入器
	hasher := sha256.New()

	// 3. 分块读取文件并写入哈希器
	if _, err := io.Copy(hasher, file); err != nil {
		panic(err)
	}

	// 4. 计算最终哈希值（返回 []byte）
	hash := hasher.Sum(nil)

	// 5. 转为十六进制字符串
	hashHex := fmt.Sprintf("%x", hash)

	fmt.Printf("文件哈希：%s\n", hashHex)
}
```

执行结果：

```go
文件哈希：1e90635d3f1a83300e1bdca8b7699ebe3775ff6593ec0231077ff72b7ad0d97b
```

### 验证文件完整性

下载好一个文件之后，计算一下文件的哈希值，之后再和官方提供的哈希值进行对比，确保自己下载的没有问题。

运行逻辑就是，首先通过 `sha256.New()` 创建一个哈希器，之后向哈希器中写入数据，最后再执行一次 `hasher.Sum(nil)` 计算出哈希值。

```go
func main() {
	// 1. 计算文件哈希
	file, err := os.Open("go.mod")
	if err != nil {
		panic("文件不存在:" + err.Error())
	}
	defer file.Close()

	hasher := sha256.New()
	io.Copy(hasher, file)
	fileHash := fmt.Sprintf("%x", hasher.Sum(nil))
	fmt.Printf("文件哈希：%s\n", fileHash)

	// 2. 与官方公开的哈希值比对
	officialHash := "37e17f9fa22971b9ed26a58a03f77ac3bcfb65650b950e516726533892f99801" // 官方提供的 64 位十六进制数

	if fileHash == officialHash {
		fmt.Println("文件完整，哈希值匹配")
	} else {
		fmt.Println("文件可能已被篡改")
	}
}
```

运行结果：

```go
文件哈希：37e17f9fa22971b9ed26a58a03f77ac3bcfb65650b950e516726533892f99801
文件完整，哈希值匹配
```

### 两种计算方式

两种计算方式：使用 `Sum256([]byte)` 和 `hasher.Sum([]byte)` 两种方式计算，最终的结果应该是一样的。

```go
func main() {
	// 1. 创建哈希器
	hasher := sha256.New()

	// 2. 模拟分块写入数据
	chunk1 := []byte("Go is ")
	chunk2 := []byte("awesome!")
	// 分别写入数据快
	hasher.Write(chunk1)
	hasher.Write(chunk2)

	// 3. 获取最终哈希（可以附加额外数据）
	finalHash := hasher.Sum(nil)

	// 4. 打印结果
	fmt.Printf("输入数据： %s%s\n", chunk1, chunk2)
	fmt.Printf("输出哈希值：%x\n", finalHash)

	// 5. 对比一次性计算的结果（应相同）
	expected := sha256.Sum256([]byte("Go is awesome!"))
	fmt.Printf("一次性计算：%x\n", expected)
}
```

运行结果：

```go
[root@JiGeX sha256-demo]# go build . && ./sha256-demo 
输入数据： Go is awesome!
输出哈希值：d557c06d48fd26fa66dfc2c327288fe815f537addfde447da9e70ae69ceae437
一次性计算：d557c06d48fd26fa66dfc2c327288fe815f537addfde447da9e70ae69ceae437
```

### 总结

使用 `sha256` 计算的两种方式：

- 如果就是简单的字符串，可以直接使用 `sha256.Sum256([]byte)` 这种方式进行计算。
- 如果是比较复杂的大量的数据，或者是流式的数据，可以先用一个哈希器，收集好所有的输入流，最后再一起计算哈希值。输入的时候可以使用 `hasher.Write([]byte)` 方法，或者是对于文件还可以使用 `io.Copy(hasher, file)`。最后再使用 `hasher.Sum(nil)` 方法进行计算。

## 对称加密：AES-GCM

### 介绍

加密就是：原数据 + 钥匙 ➡️ 加密后的数据。之后还可以：加密后的数据 + 钥匙 ➡️ 原数据。

对称加密的意思就是，加密的时候使用的“钥匙”和解密的时候使用的“钥匙”是**相同**的。

AES 是一种对称加密算法，GCM 是这个算法的一种认证加密的模式，是比较推荐使用的。GCM 的思想，简单来说就是加密的时候，在密文的基础上再加一个 Tag，之后解密的时候也要使用随机的 Tag。

总结来说：

- 加密时：输入明文 + 密钥 + Nonce → 输出密文 + Tag。
- 解密时：用密钥 + Nonce + Tag 验证明文 → 如果 Tag 对不上，直接报错（说明数据被改）。

关键概念：

| 概念        | 作用                                                         | 注意事项                                   |
| ----------- | ------------------------------------------------------------ | ------------------------------------------ |
| 密钥（Key） | 加密/解密的“钥匙”，必须保密！                                | 长度 16/32 字节（AES-128/AES-256）         |
| Nonce       | 随机数（Number used once），每次加密必须唯一（但不需要保密）。 | 通常 12 字节；重复使用会导致安全漏洞       |
| Tag         | 认证标签（16 字节），附加在密文后，用于验证完整性            | 解密时必须提供，否则无法验证数据是否被篡改 |

### 基础的加密、解密

```go
func main() {
	// 1， 准备密钥（实际中是不能硬编码的）
	key := []byte("this-is-32-byte-long-secret-key!") // 32 字节 = AES-256

	// 2. 准备明文
	plaintext := []byte("Hello, AES-GCM! This is secret.")

	// 3. 创建 AES cipher 并包装成 GCM 模式
	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}
	aesGCM, err := cipher.NewGCM(block) // 将 AES 包装成 GCM 模式
	if err != nil {
		panic(err)
	}

	// 4. 固定 Nonce（实际中必须使用随机 Nonce）
	nonce := []byte("123456789012") // 必须 12 字节（GCM 推荐长度）

	// 5. 加密：输入明文 -> 输出密文 + Tag
	ciphertext := aesGCM.Seal(nil, nonce, plaintext, nil)
	// Seal 返回：【密文 + Tag】（Tag 附加在密文末尾）

	// 6. 打印结果（用 base64 便于阅读）
	fmt.Printf("密文(base64): %s\n", base64.StdEncoding.EncodeToString(ciphertext))

	// 7. 解密用相同的 key/nonce/ciphertext -> 得到明文
	decrypted, err := aesGCM.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		panic("解密失败！可能数据被篡改！")
	}
	fmt.Printf("解密后：%s\n", string(decrypted))
}
```

输出：

```go
密文(base64): v6NtsXoRTv6BYKuqTd8hb1fRsIWEkmYyoLsHbnWZQQOJpYAVE63fns2hrDfizT4=
解密后：Hello, AES-GCM! This is secret.
```

### 随机 Nonce 和密文存储

```go
func main() {
	key := []byte("this-is-32-byte-long-secret-key!") // 32 字节 = AES-256

	plaintext := []byte("Important data: 123456")

	// 1. 创建 AES-GCM（同 demo1）
	block, _ := aes.NewCipher(key)
	aesGCM, _ := cipher.NewGCM(block)

	// 2. 生成随机 Nonce（安全做法）
	nonce := make([]byte, aesGCM.NonceSize()) // 推荐长度：aesGCM.NonceSize() = 12
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		panic(err)
	}

	// 3. 加密
	ciphertext := aesGCM.Seal(nil, nonce, plaintext, nil)

	// 4. 存储：把 Nonce + 密文一起存（通常 Nonce 放前面）
	fullData := append(nonce, ciphertext...) // 关键：Nonce 和密文拼接

	// 5. 传输/存储时用 base64
	fmt.Printf("完整数据（base64）: %s\n", base64.StdEncoding.EncodeToString(fullData))

	//  ===== 模拟接收方解密 =====
	receivedData, _ := base64.StdEncoding.DecodeString(base64.StdEncoding.EncodeToString(fullData))

	// 6. 拆分：前 12 字节是 Nonce，后面是密文
	nonceSize := aesGCM.NonceSize()
	nonceReceived := receivedData[:nonceSize]
	ciphertextReceived := receivedData[nonceSize:]

	// 7. 用接收到的 Nonce 解密
	decrypted, err := aesGCM.Open(nil, nonceReceived, ciphertextReceived, nil)
	if err != nil {
		panic("解密失败！数据可能被篡改")
	}
	fmt.Printf("解密后：%s\n", string(decrypted))
}
```

输出：

```go
完整数据（base64）: OoLsszizMcwL3+5Dfu5x5WX3w0I8hVPMnXYKtVfIq2QbpG6USa1VUuk+JLfUr4h0A98=
解密后：Important data: 123456
```

### 总结

总体来说还会很复杂，看的不是特别懂。但是基础的东西还是那么多：

- 明文：就是我们要加密的数据。
- 密钥：加密和解码的时候，输入的密码验证机制。
- Nonce：感觉跟盐值的机制差不多？出现的意义是让对同样的数据加密之后生成的数据是不同的。Nonce 每次都是随机生成的，而且是公开的，不保密。
- 密文 + Tag：我觉得就放到一起来理解吧，因为加密和解密的时候，两个东西都是一起出现的。

所以整个流程就是：

- 加密：`明文 + 密钥 + Nonce => (密文+Tag)`
- 解密：`(密文+Tag) + 密钥 + Nonce => 明文`

密钥和 Nonce 的一个区别是，Nonce 是公开的，密钥是需要保密的。

## 非对称加密：RSA

### 介绍

AES 对称加密，加密和解密的时候，都是用的是同样的密钥。那么非对称加密就是加密和解密的时候使用的不同的密钥。

具体来说就是：公钥机密，私钥解密。

在 AES 中，同一个 AES 算法有多种不同的模式，我们重点学习的是 GCM 模式。RSA 中没有模式这样的说法，但是有一个“填充机制”的说法，就是是存在多种不同的填充机制。

AES-GCM 对明文的长度没有要求，但是 RSA 对明文的长度是有要求的，比如 2048 位密钥最多加密 245 字节的明文。

更重要的是，如果没有加入一些填充的垃圾数据，同样的明文总会产生相同的密文，此时是非常不安全的。所以在加密的时候，需要加入一些填充的数据。也就是说，需要一种机制，让加密过程随机化。这里我们学习的是比较主流的 `OAEP` 填充法，`TLS`、`HTTPS` 使用的也是这种填充机制。

总结来说，加入填充数据的目的是：

- 相同明文，每次加密的结果都是不同的。
- 解密的时候能自动去掉垃圾数据，还原明文。

### 生成 RSA 密钥对

```go
func main() {
	// 1. 生成 2048 位 RSA 密钥对（2048 是一种安全的标准）
	privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		panic(err)
	}

	// 2. 提取公钥
	publicKey := &privateKey.PublicKey

	// 3. 打印密钥信息
	fmt.Printf("私钥：%+v\n", privateKey)
	fmt.Printf("公钥：%+v\n", publicKey)
}
```

输出：

```go
私钥：&{PublicKey:{N:+222016835...4000}}
公钥：&{N:+222016...5537}
```

### 用公钥加密（OAEP 填充）

```go
func main() {
	// 1. 生成密钥对（实际中从文件加载，这里简化）
	privateKey, _ := rsa.GenerateKey(rand.Reader, 2048)
	publicKey := &privateKey.PublicKey

	// 2. 要加密的明文（必须很小！这里用 20 字节的字符串）
	plaintext := []byte("Hello,RSA!1234567890")

	// 3. OAEP 加密（核心步骤）
	ciphertext, err := rsa.EncryptOAEP(
		sha256.New(), // 哈希函数
		rand.Reader,  // 随机数生成器
		publicKey,    // 公钥
		plaintext,    // 明文
		[]byte(""),   // 可选的标签（这里为空）
	)
	if err != nil {
		panic(err)
	}

	// 4. 打印密文（二进制数据，通常转为 base64 存储）
	fmt.Printf("密文: %x\n", ciphertext)

}
```

输出：

```go
密文: 826ec63a7fd51e5e550f02
// 每次运行输出不同
```

### 用私钥解密（OAEP 填充）

```go
func main() {
	// 1. 生成密钥对（实际中私钥从安全存储中加载）
	privateKey, _ := rsa.GenerateKey(rand.Reader, 2048)
	publicKey := &privateKey.PublicKey

	// 2. 假设这是从网络中收到的密文（如 demo2 的输出）
	plaintext := []byte("Hello, OAEP Encryption")
	ciphertext, _ := rsa.EncryptOAEP(
		sha256.New(), // 哈希函数
		rand.Reader,  // 随机数生成器
		publicKey,    // 公钥
		plaintext,    // 明文
		[]byte(""),   // 可选的标签（这里为空）
	)

	// 3. OAEP 解密（核心步骤）
	decryped, err := rsa.DecryptOAEP(
		sha256.New(), // 哈希函数：必须和加密时一致
		rand.Reader,  // 解密其实不用随机数，但 API 要求传（填 rand.Reader 即可）
		privateKey,   // 私钥
		ciphertext,   // 密文
		[]byte(""),   // Label: 必须和加密时一致（空）
	)
	if err != nil {
		panic(err)
	}

	// 4. 验证结果
	fmt.Printf("解密结果：%s\n", decryped)
}
```

输出：

```go
解密结果：Hello, OAEP Encryption
```

### 总结

RSA 加密解密的流程：

1. 创建公钥、私钥：`安全标准(2048) + 随机数 => key + key.pub`
2. 加密：`明文 + 公钥 => 密文`
3. 解密：`密文 + 私钥 => 明文`

需要注意的是，RSA 加密的都是小数据，比如说使用 2048 位密钥 + SHA-256 哈希，明文要 <= 190字节。实际中加密可以和 AES 配合，比如说使用 RSA 去加密 AES 的 `key`（`key` 一般都比较短），再用 AES 的 `key` 去对大数据做对称加密。

同时，加密和解密的时候，使用的哈希函数、随机数生成器，都必须一致。`label` 字段一般不咋用，一般就设置为空就行。

## 验证数据完整性：HMAC

### 介绍

HMAC 全称是 Hash-based Message Authentication Code，中文叫做“基于哈希的消息认证码”。

它不是一个加密算法，也不是一个解密算法，而是用来验证数据完整性的，保证数据确实是对方发过来的（身份验证），同时也要保证数据没有被篡改过（完整性校验）。

HMAC 的核心思想是：用“密钥”和“消息”一起生成一个签名，接收方用同样的密钥验证签名是否是匹配的。

只有发送方和接收方知道密钥，中间人不知道密钥，所以如果中间人修改了消息的内容，他也无法修改签名的内容。接收方收到数据之后，用自己的 `secret-key` 和数据的内容计算，发现算出来的结果和数据的签名的内容不一致，那数据肯定就是被人篡改了。

### 生成一个 HMAC-SHA256 签名

```go
func main() {
	// 要传输的消息
	message := "Hello, 世界！"

	// 共享密钥（只有发送方和接收方知道）
	key := []byte("abcdefghijklmnopqrstuvwxyz123456")

	// 1. 创建 HMAC 器，使用 SHA256
	h := hmac.New(sha256.New, key)

	// 2. 写入消息
	h.Write([]byte(message))

	// 3. 计算最终的 HMAC 值（[]byte）
	signature := h.Sum(nil)

	// 4. 转成十六进制字符串，方便传输或打印
	sigHex := hex.EncodeToString(signature)

	fmt.Printf("消息: %s\n", message)
	fmt.Printf("HMAC: %s\n", sigHex)
}
```

运行结果：

```go
消息: Hello, 世界！
HMAC: 1eef1baecfd17eb8366265f9914ed8fdd969a6543cca99785bd5fd88ac7e4239
```

### 验证 HMAC

```go
func main() {
	// 接收方
	// 收到的消息和签名
	receivedMessage := "Hello, 世界！"
	receivedSignature, _ := hex.DecodeString("1eef1baecfd17eb8366265f9914ed8fdd969a6543cca99785bd5fd88ac7e4239")

	// 共享密钥（必须和发送方一致）
	key := []byte("abcdefghijklmnopqrstuvwxyz123456")

	// ===== 验证过程 =====

	// 1. 用同样的密钥和算法重新计算 HMAC
	h := hmac.New(sha256.New, key)
	h.Write([]byte(receivedMessage))
	expectedSignature := h.Sum(nil)

	// 2. 使用 hmac.Equal 比较（更安全，防时序攻击）
	isValid := hmac.Equal(receivedSignature, expectedSignature)

	if isValid {
		fmt.Println("✅ 签名验证通过！消息可信")
	} else {
		fmt.Println("❌ 签名验证失败！消息可能被篡改")
	}
}
```

运行结果：

```go
[root@JiGeX hmac-demo]# go build . && ./hmac-demo 
✅ 签名验证通过！消息可信
```

> 从这个 demo2 中可以看出，message 实际上是直接暴露出来的。也就是说，如果有黑客窃取信息，数据包中的 message 黑客是可以知道的，但是使用 HMAC 黑客就没法篡改其中的数据。
>
> 如果不想让黑客知道数据具体是啥，那就要对数据做 AES 加密之类的操作。
>
> AES + HMAC 结合起来使用，可以让黑客既无法获取 message 真实的信息，也无法修改其中的数据内容。

### API 请求签名

```go
// 客户端：生成带签名的请求
func createSignedRequest() (string, string) {
	message := `{"action": "pay", "amount": 100}`
	key := []byte("abcdefghijklmnopqrstuvwxyz123456")

	h := hmac.New(sha256.New, key)
	h.Write([]byte(message))
	sig := hex.EncodeToString(h.Sum(nil))

	return message, sig
}

// 服务器端：收到后验证
func verifyRequest(message, receivedSig string) bool {
	key := []byte("abcdefghijklmnopqrstuvwxyz123456")
	expectedH := hmac.New(sha256.New, key)
	expectedH.Write([]byte(message))
	expectedSig := expectedH.Sum(nil)

	receivedSigBytes, _ := hex.DecodeString(receivedSig)
	return hmac.Equal(receivedSigBytes, expectedSig)
}

func main() {
	msg, sig := createSignedRequest()
	fmt.Println("发送消息:", msg)
	fmt.Println("发送签名:", sig)

	if verifyRequest(msg, sig) {
		fmt.Println("✅ 签名验证成功")
	} else {
		fmt.Println("❌ 签名验证失败")
	}
}
```

运行结果：

```go
[root@JiGeX hmac-demo]# go build . && ./hmac-demo 
发送消息: {"action": "pay", "amount": 100}
发送签名: 2c7402332dc4e4d78f80710992e9b1e1c0d8a920cf33deacb1661f1464af257b
✅ 签名验证成功
```

### 总结

核心概念：

| 概念            | 说明                                                        |
| --------------- | ----------------------------------------------------------- |
| 密钥（key）     | 只有发送方和接收方知道，作用是生成和验证签名                |
| 消息（message） | 要保护的数据，比如 JSON 字符串、请求体等                    |
| HMAC 签名       | 用 key 和 message 共同生成的一串字节（通常转成 hex 字符串） |
| 验证            | 接收方用 key 验证签名是否正确的过程                         |

签名的生成：`key + message => signature`

## 加密安全随机数：RAND

### 介绍

这也是一个 rand 包。但是看到这里的 rand，肯定会第一时间想到另一个包：`math/rand`。下面是这两种 `rand` 包之间的区别，以及啥时候用什么：

| 包           | `/math/rand`           | `crypto/rand`              |
| ------------ | ---------------------- | -------------------------- |
| 用途         | 普通随机（游戏、模拟） | 密码学安全随机（生成令牌） |
| 随机性       | 可预测（伪随机）       | 不可预测（真随机）         |
| 是否需要种子 | 需要 Seed              | 不需要种子                 |
| 是否安全     | ❌ 不安全               | ✅ 安全                     |

简单来说就是，`/math/rand` 的随机数基于给随机数设置的种子，但是只要我知道这个种子之后，生成的随机数也是固定的。所以所谓的随机序列，实际上是可以预测的。但是 `crypto/rand` 使用操作系统提供的加密安全随机源（如 Linux 的 `/dev/urandom`），做成的真随机数。

### `rand/math`

直接使用 `rand.Seed()` 播种（现已弃用）：

```go
import (
	"fmt"
	"math/rand"
	"time"
)

func main() {
	// 使用 math.rand
	rand.Seed(0)
	for i := 0; i < 3; i++ {
		fmt.Println(rand.Intn(100))
	}
}
```

> 这段代码在 go 1.24 上执行，每次执行输出的值还是会随机的，即使我显式设置了 `rand.Seed(0)`。这是因为 go 觉得这种方式不安全，在其中加入了全局随机数生成器的随机化保护。
>
> 总之就是，这段代码从 1.20 开始，每次执行的结果都是不同的。go 1.20 之前的版本中，每次执行的结果都是相同的。

`rand/math` 指定固定源：

```go
import (
	"fmt"
	"math/rand"
)

func main() {
	// 显式创建一个确定性的随机源
    // 在 NewSource 的 seed 字段填 0
	r := rand.New(rand.NewSource(0))
	for i := 0; i < 3; i++ {
		fmt.Println(r.Intn(100))
	}
}
```

> 这段代码会固定生成：74、14、53

### `crypto/rand`

```go
import (
	"crypto/rand"
	"fmt"
)

func main() {
	// 生成随机字节序列
	bytes := make([]byte, 16)
	_, err := rand.Read(bytes)
	if err != nil {
		panic(err)
	}
	fmt.Printf("随机字节序列：%x\n", bytes)
}
```

输出：

```go
[root@JiGeX rand-demo]# go build . && ./rand-demo 
随机字节序列：1136acb1dcd07157457afa4e7da3e640
```

### 总结

之后生成某个长度的随机数的时候就使用代码：

```go
import (
	"crypto/rand"
	"fmt"
)

func main() {
	// ...
	bytes := make([]byte, 16)
	rand.Read(bytes)
    // ...
}
```









