# automaxprocs

## 介绍

Go 中的环境变量 `GOMAXPROCS` 表示 go 执行时使用的最大 CPU 数量。Go 在真实的操作系统中的性能还可以，但是在容器中的性能不是特别好。这是因为在容器中，目前的 Go 无法正确识别容器中的 CPU 限制。

比如说本机 CPU 是 24 线程的，那么在操作系统中就使用 24 线程没有问题。但是在容器中，即使我们通过一些参数，比如说说限制容器只能使用 4 个 CPU，但是 Go 可能还是将 `GOMAXPROCS` 当作 24，这样会导致性能问题。

## 安装

```go
go get go.uber.org/automaxprocs
```

## 基本使用

基本使用就是在项目的入口处添加一行代码：

```go
import (
    _ "go.uber.org/automaxprocs"
)
```

## 测试

测试程序：

```go
package main

import (
	"fmt"
	"runtime"
	_ "go.uber.org/automaxprocs"
)

func main() {
	fmt.Println("GOMAXPROCS:", runtime.GOMAXPROCS(0))
}
```

编译出来一个可执行程序 `automaxprocs`，再将 `_ "go.uber.org/automaxprocs"` 这一行删去，编译出来另一个可执行程序：`no-automaxprocs`。

### 真机中执行

```go
[root@JiGeX automaxprocs-demo]# ./automaxprocs 
2025/07/24 20:44:06 maxprocs: Leaving GOMAXPROCS=24: CPU quota undefined
GOMAXPROCS: 24

[root@JiGeX automaxprocs-demo]# ./no-automaxprocs 
GOMAXPROCS: 24
```

可以看到，真机中执行，不管带不带那个库，Go 能使用的最大 CPU 数量都是 24。

### 容器中执行

首先构建容器。Dockerfile 如下：

```dockerfile
FROM ubuntu:20.04

RUN mkdir /app

WORKDIR /app

COPY automaxprocs /app

COPY no-automaxprocs /app

RUN chmod +x ./automaxprocs ./no-automaxprocs

CMD ["bash", "-c", "echo 'Container is running'; tail -f /dev/null"]
```

之后构建镜像并启动：

```bash
docker build -t auto-image .

docker run -d --name auto-container --cpus="2" auto-image:latest

docker exec -it auto-container bash
```

之后执行我们的程序：

```go
root@666ca9369ce0:/app# ./automaxprocs 
2025/07/24 12:49:48 maxprocs: Updating GOMAXPROCS=2: determined from CPU quota
GOMAXPROCS: 2

root@666ca9369ce0:/app# ./no-automaxprocs 
GOMAXPROCS: 24
```

可以发现，如果程序启动时加载了 `automaxprocs` 库，golang 就会自动识别到容器中的 CPU 限制。







