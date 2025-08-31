# slog

## 介绍

`slog` 的全称是 `Structured log`。被设计用来取代传统的 `log` 包。

传统的 log 包有一个问题，就是只能输出纯文本。这让日志的解析变得复杂：

```go
log.Println("User login failed", "user_id=123", "ip=192.168.1.1")
```

但是 `slog` 可以以一种结构化的方式输出日志，日志的各个属性（比如日志级别、日志事件等）会被写进一个类似 JSON 的结构中。这样后期解析日志内容就会比较方便：

```json
{"level":"INFO","time":"2024-04-05T10:00:00Z","msg":"User login failed","user_id":123,"ip":"192.168.1.1"}
```

`slog` 的核心概念：

| 概念      | 说明                                 |
| --------- | ------------------------------------ |
| `Logger`  | 日志记录器，用于输出日志             |
| `Handler` | 处理日志的输出方式（如 JSON、文本）  |
| `Level`   | 日志级别（Debug、Info、Warn、Error） |
| `Attrs`   | 键值对属性，附加在日志中             |
| `Context` | 可选的上下文信息                     |

## 最简单的使用

```go
package main

import (
	"log/slog"
)

func main() {
	slog.Info("Application started")
	slog.Warn("This is a warning")
	slog.Error("Something went wrong")
	slog.Debug("Debug message") // 默认不会输出，因为级别不够
}
```

输出：

```go
[root@JiGeX slog-demo]# ./slog-demo 
{"time":"2025-07-28T11:12:08.98478517+08:00","level":"INFO","msg":"Application started"}
{"time":"2025-07-28T11:12:08.984867592+08:00","level":"WARN","msg":"This is a warning"}
{"time":"2025-07-28T11:12:08.984869764+08:00","level":"ERROR","msg":"Something went wrong"}
```

> Debug 信息默认不会输出，因为默认级别是 Info。

## 添加 key-value 属性

```go
func main() {
	slog.Info("User login", "user_id", 1001, "ip", "192.168.1.1", "success", true)
	slog.Error("Database error", "error", "connection timeout", "retry", 3)
}
```

输出：

```go
[root@JiGeX slog-demo]# go build . && ./slog-demo 
2025/07/28 11:14:56 INFO User login user_id=1001 ip=192.168.1.1 success=true
2025/07/28 11:14:56 ERROR Database error error="connection timeout" retry=3
```

> 这就是结构化日志，其中的：`ip=192.168.1.1`、`success=true` 就将结构化的键值对清晰地展现出来。

## 使用 `slog.Group` 嵌套属性

当属性比较多的时候，可以用 `slog.Group` 将相关属性分组。

```go
func main() {
	slog.Info("Request completed",
		slog.Group("request",
			"method", "GET",
			"path", "/api/users",
			"duration_ms", 150,
		),
		slog.Group("user",
			"id", 1001,
			"role", "admin",
		),
	)
}
```

输出：

```go
[root@JiGeX slog-demo]# go build . && ./slog-demo 
2025/07/28 11:18:46 INFO Request completed request.method=GET request.path=/api/users request.duration_ms=150 user.id=1001 user.role=admin
```

> 感觉这里没有什么必要？想这样输出的话，或许 JSON 是更好的方式。

## 使用 JSON 格式化输出（推荐）

```go
func main() {
	// 创建一个 JSON handler
	jsonHandler := slog.NewJSONHandler(os.Stdout, nil)

	// 创建一个新的 logger
	logger := slog.New(jsonHandler)

	// 使用 logger
	logger.Info("User created",
		"user_id", 1001,
		"email", "alice@example.com",
		"tags", []string{"admin", "premium"},
	)
}
```

输出：

```go
[root@JiGeX slog-demo]# go build . && ./slog-demo 
{"time":"2025-07-28T11:23:54.868305516+08:00","level":"INFO","msg":"User created","user_id":1001,"email":"alice@example.com","tags":["admin","premium"]}
```

输出的格式就是 JSON 格式。

> 前面说 Logger 主要有两种，一个是 text 的 Logger，一个是 json 的 Logger。默认情况下，如果直接使用 slog 输出，看起来更像是 text 类型的 logger，但是也不完全是，可能一些地方还做了其他的处理。

## 使用 `With` 添加公共字段

```go
func main() {
	// 创建带公共字段的 logger
	logger := slog.New(slog.NewTextHandler(os.Stdout, nil)).With("service", "auth", "version", "1.0.0")

	logger.Info("Starting server", "port", 8080)
	logger.Warn("Deprecated endpoint accessed", "endpoint", "/v1/old")
}
```

输出：

```go
[root@JiGeX slog-demo]# go build . && ./slog-demo 
time=2025-07-28T11:31:56.289+08:00 level=INFO msg="Starting server" service=auth version=1.0.0 port=8080
time=2025-07-28T11:31:56.289+08:00 level=WARN msg="Deprecated endpoint accessed" service=auth version=1.0.0 endpoint=/v1/old
```

创建 logger 的时候，给这个 logger 带上了 `service` 和 `version` 两个字段，后续从这个 Logger 中输出的日志都带有这两个字段。

## 总结

之后使用的时候：

```go
// 先创建 Logger
logger := slog.New(slog.NewTextHandler(os.Stdout, nil))
// 然后输出各种级别的结构化日志即可
logger.Info("本次日志的 message", key1, value1, key2, value2, ...)
```











