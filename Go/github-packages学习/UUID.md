# UUID

[TOC]

## 安装

```go
go get "github.com/google/uuid"
```

## 介绍

uuid 用于生成全局唯一的标识符。

uuid 有很多不同的版本，现在知道的有 v1、v4、v5 这些版本。其中 v4 版本是最常用的，所以学习的时候就以 v4 版本为主。

## 主要使用的 API

| API            | 用法                                        | 说明                                    |
| -------------- | ------------------------------------------- | --------------------------------------- |
| `uuid.New()`   | `id := uuid.New()`                          | 直接生成 v4 版本的 UUID，内部忽略错误。 |
| `id.String()`  | `print(id)` 或者 `print(id.String())`       | 一个 id 的 `string` 格式。              |
| `uuid.Parse()` | `id, err := uuid.Parse("your-uuid-string")` | 将字符串转换为 uuid 对象。              |

## demo

```go
package main

import (
	"fmt"

	"github.com/google/uuid"
)

func validateUUID(input string) {
	u, err := uuid.Parse(input)
	if err != nil {
		fmt.Println("无效的 UUID")
		return
	}
	fmt.Printf("有效的 UUID（版本 %d） : %s\n", u.Version(), u.String())
}

func main() {
	id := uuid.New()
	fmt.Println(id)

	validateUUID(id.String())
	validateUUID("www-baidu-com")
}
```

输出：

```go
e67ef9da-e491-472a-824b-c8908f14a8c4
有效的 UUID（版本 4） : e67ef9da-e491-472a-824b-c8908f14a8c4
无效的 UUID
```

## 理解

从中可以看到，uuid 的一个例子是 `e67ef9da-e491-472a-824b-c8908f14a8c4`。这是一个字符串，由 32 个十六进制数和 4 个连字符组成。我看 uuid 库中，对 uuid 的定义是：

```go
// A UUID is a 128 bit (16 byte) Universal Unique IDentifier as defined in RFC 4122.
type UUID [16]byte
```

所以 uuid 就是一个 16 个字节组成的数据。我们知道 4 个字节就是一个 16 进制数字，所以 uuid 一共是 32 个十六进制数。

对于 uuid 的 `String` 形式，源码中写到：

```go
// String returns the string form of uuid, xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
// , or "" if uuid is invalid.
func (uuid UUID) String() string {
	var buf [36]byte
	encodeHex(buf[:], uuid)
	return string(buf[:])
}

func encodeHex(dst []byte, uuid UUID) {
	hex.Encode(dst, uuid[:4])
	dst[8] = '-'
	hex.Encode(dst[9:13], uuid[4:6])
	dst[13] = '-'
	hex.Encode(dst[14:18], uuid[6:8])
	dst[18] = '-'
	hex.Encode(dst[19:23], uuid[8:10])
	dst[23] = '-'
	hex.Encode(dst[24:], uuid[10:])
}
```

所以 uuid 的 `String()` 就是，不断将字节数据转换为 16 进制数，然后在中间加上 `-`。







