# pflag

## 介绍

`pflag` 包与 golang 自带的标准库 `flag` 差不多，都是用来解析命令行参数的。

相比于 `flag`，`pflag` 有更强大的功能并且与标准的兼容性更好。

## 安装

```go
go get github.com/spf13/pflag
```

## 基本用法

主要有四种用法，其中要填写四个字段，分别是：

| p                | name               | value              | usage    |
| ---------------- | ------------------ | ------------------ | -------- |
| 对应的变量的指针 | 命令行中指定的名字 | 没有指定时的默认值 | 用法说明 |

- 字符串类型：`pflag.StringVar(&name, "name", "default-name", "your name")`
- 整数类型：`pflag.IntVar(&age, "age", 0, "your age")`
- 布尔类型：`pflag.BoolVar(&debug, "debug", false, "enable debug mode")`
- 浮点数类型：`pflag.Float64Var(&score, "score", 0.0, "your score")`

```go
package main

import (
	"fmt"

	"github.com/spf13/pflag"
)

func main() {
	// 定义字符串标志
	var name string
	pflag.StringVar(&name, "name", "default", "your name")

	// 定义整数标志
	var age int
	pflag.IntVar(&age, "age", 0, "your age")

	// 定义布尔标志
	var debug bool
	pflag.BoolVar(&debug, "debug", false, "enable debug mode")

	// 定义浮点数标志
	var score float64
	pflag.Float64Var(&score, "score", 0.0, "your score")

	// 解析命令行参数
	pflag.Parse()

	fmt.Printf("your name is: %s\n", name)
	fmt.Printf("your age is: %d\n", age)
	fmt.Printf("debug mode is: %v\n", debug)
	fmt.Printf("your score is: %f\n", score)
}
```

测试：

```go
[root@JiGeX pflag-demo]# ./pflag-demo --name=toby --age=18 --debug --score=10.5
your name is: toby
your age is: 18
debug mode is: true
your score is: 10.500000
```

> 小插曲：对命令行输入的参数的规范。
>
> 对于非布尔类型的变量，推荐 `--name=toby`，而不是 `--name toby`。使用 `=` 来连接，可以让逻辑更清晰，也是业内多数的做法。
>
> 对于布尔类型的变量，推荐 `--debug` 表示开启，`--debug=false` 表示关闭。
>
> 但是对于短选项，还是推荐使用空格隔开，比如说 `-n alice`、`-a 25`。布尔类型的短选项，一般来说一个选项的默认值都是 false，只需要 `-h`、`-d` 这样表示开启就可以了。

## 短选项支持

在原本的几种函数上进行扩充，`value` 上提供了短选项的功能。

| p                | name               | value              | usage    |
| ---------------- | ------------------ | ------------------ | -------- |
| 对应的变量的指针 | 命令行中指定的名字 | 没有指定时的默认值 | 用法说明 |

- 字符串类型：`pflag.StringVarP(&name, "name", "n", "default", "your name")`
- 整数类型：`pflag.IntVarP(&age, "age", "a", 0, "your age")`
- 布尔类型：`pflag.BoolVarP(&help, "help", "h", false, "show help")`

示例代码：

```go
func main() {
	var (
		name string
		age  int
		help bool
	)

	// 第二个选项是短选项
	pflag.StringVarP(&name, "name", "n", "default", "your name")
	pflag.IntVarP(&age, "age", "a", 0, "your age")
	pflag.BoolVarP(&help, "help", "h", false, "show help")

	// 解析命令行参数
	pflag.Parse()

	if help {
		pflag.Usage()
		return
	}

	fmt.Printf("your name is: %s, age is: %d\n", name, age)
}
```

测试：

```go
[root@JiGeX pflag-demo]# ./pflag-demo -h
Usage of ./pflag-demo:
  -a, --age int       your age
  -h, --help          show help
  -n, --name string   your name (default "default")

[root@JiGeX pflag-demo]# ./pflag-demo -n alice -a 25
your name is: alice, age is: 25
```

## 切片类型参数

```go
func main() {
	// 字符串切片
	var hosts []string
	pflag.StringSliceVar(&hosts, "hosts", []string{}, "host list")

	// 整数切片
	var ports []int
	pflag.IntSliceVar(&ports, "ports", []int{}, "port list")
	pflag.Parse()

	fmt.Printf("Hosts: %v\n", hosts)
	fmt.Printf("Ports: %v\n", ports)
}
```

使用：

```go
[root@JiGeX pflag-demo]# ./pflag-demo --hosts={host1,host2,host3} --ports={100,101,102}
Hosts: [host1 host2 host3]
Ports: [100 101 102]
```

## map 类型参数

```go
func main() {
	// 字符串到字符串的映射
	var labels map[string]string
	pflag.StringToStringVar(&labels, "labels", map[string]string{}, "labels")

	pflag.Parse()

	fmt.Printf("Labels: %v\n", labels)
}
```

使用：

```go
[root@JiGeX pflag-demo]# ./pflag-demo --labels={name=alice,email=163,age=18}
Labels: map[age:18 email:163 name:alice]
```









