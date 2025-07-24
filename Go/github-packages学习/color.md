# color

## 介绍

`color` 库用来在命令行输出内容的时候，带点颜色。

## 安装

```go
go get github.com/gookit/color
```

## 快速使用1

简单快速的使用，直接跟 `fmt.Print*` 类的方法一样直接使用就行。

| API                     | 说明             |
| ----------------------- | ---------------- |
| `color.RedP(...any)`    | 打印红色         |
| `color.Redln(...any)`   | 打印红色，带换行 |
| `color.GreenP(...any)`  | 打印绿色         |
| `color.CyanP(...any)`   | 打印青色         |
| `color.YellowP(...any)` | 打印黄色         |

```go
import "github.com/gookit/color"

func main() {
	color.Redp("Simple to use color\n")
	color.Redln("Simple to use color")
	color.Greenp("Simple to use color\n")
	color.Cyanln("Simple to use color")
	color.Yellowln("Simple to use color")
}
```

输出：

![image-20250724163824964](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250724163824964.png)

## 快速使用 2（推荐）

我觉得这种更好，是因为我觉得这种方式和 `fmt.Print()` 这种方式更像。

使用方法就是：`color.颜色.Print类方法()`。

例如：`color.Red.Print()`、`color.Yellow.Printf()`、`color.Cyanln.Println()`。

```go
import "github.com/gookit/color"

func main() {
	color.Red.Println("Simple to use color")
	color.Green.Print("Simple to use color\n")
	color.Cyan.Printf("Simple to use %s\n", "color")
	color.Yellow.Printf("Simple to use %s\n", "color")
}
```

输出：

![image-20250724164428458](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250724164428458.png)

## 打印带颜色的日志

```go
import "github.com/gookit/color"

func main() {
	color.Debug.Println("message")
	color.Info.Println("message")
	color.Warn.Println("message")
	color.Error.Println("message")
}
```

输出：

![image-20250724164734994](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250724164734994.png)







