# cobra

## 介绍

cobra 是一个命令行应用程序库，用于构建现代化的 CLI 工具。

## 安装

```go
go get github.com/spf13/cobra
```

## 基本使用

### 创建简单的 CLI 应用

```go
func main() {
	rootCmd := cobra.Command{
		Use:   "myapp",
		Short: "这是一个示例应用",
		Long:  "这是一个使用 Cobra 构建的命令行应用示例",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Hello, Cobra")
		},
	}

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
```

首先建立一个 `cobra.Command` 的结构体，之后执行这个结构体的 `Execute()` 函数。

使用：

```go
[root@JiGeX cobra-demo]# ./myapp 
Hello, Cobra
```

### 添加子命令

```go
func main() {
	rootCmd := cobra.Command{
		Use:   "myapp",
		Short: "这是一个示例应用",
		Long:  "这是一个使用 Cobra 构建的命令行应用示例",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("Hello, Cobra")
		},
	}

	versionCmd := cobra.Command{
		Use:   "version",
		Short: "显示版本信息",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Println("myapp v1.0.0")
		},
	}

	serverCmd := cobra.Command{
		Use:   "server",
		Short: "启动服务器",
		Run: func(cmd *cobra.Command, args []string) {
			port, _ := cmd.Flags().GetString("port")
			fmt.Printf("启动服务器，端口：%s\n", port)
		},
	}

	rootCmd.AddCommand(&versionCmd)
	rootCmd.AddCommand(&serverCmd)
	serverCmd.Flags().StringP("port", "p", "8080", "服务器端口")

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
```

创建三个不同的 `cobra.Command()`，之后再为这些 `Command` 配置他们的层级关系、参数设置。

全都设置好之后，再执行根命令的 `Execute()` 函数。

```go
[root@JiGeX cobra-demo]# ./myapp 
Hello, Cobra

[root@JiGeX cobra-demo]# ./myapp version
myapp v1.0.0

[root@JiGeX cobra-demo]# ./myapp server
启动服务器，端口：8080

[root@JiGeX cobra-demo]# ./myapp server -p 9009
启动服务器，端口：9009
```

### 使用标志（flags）

标志中大体上可以分为两类：

```go
rootCmd.Flags().StringP(...)
rootCmd.PersistentFlags().StringP(...)
```

它们之间的区别是，持久性标志对该命令的子命令也生效；本地命令仅对该命令生效。

之后可以使用 API：

```go
name, _ := cmd.Flags().GetStirng("name")
age, _ := cmd.Flags().GetInt("age")
verbose, _ := cmd.Flags().GetBool("verbose")
```

来获取各种参数。

```go
func main() {
	rootCmd := &cobra.Command{
		Use:   "myapp",
		Short: "示例应用",
		Run: func(cmd *cobra.Command, args []string) {
			// 获取标志值
			name, _ := cmd.Flags().GetString("name")
			age, _ := cmd.Flags().GetInt("age")
			verbose, _ := cmd.Flags().GetBool("verbose")

			fmt.Printf("Name: %s, Age: %d\n", name, age)
			if verbose {
				fmt.Println("Verbose mode enabled")
			}
		},
	}

	rootCmd.PersistentFlags().StringP("name", "n", "Toby", "用户名")
	rootCmd.PersistentFlags().BoolP("verbose", "v", false, "是否开启详细模式")

	rootCmd.Flags().IntP("age", "a", 0, "年龄")

	rootCmd.Execute()
}
```

使用：

```go
[root@JiGeX cobra-demo]# ./myapp -a 80 -n nihao
Name: nihao, Age: 80

[root@JiGeX cobra-demo]# ./myapp -v
Name: World, Age: 0
Verbose mode enabled
```

## 高级用法

### 参数数量限制

- `cobra.ExactArgs(n)`：要求必须是 1 个参数
- `cobra.Noargs`：不接受任何参数
- `cobra.ArbitraryArgs`：任意数量参数
- `cobra.MinimumNArgs(n)`：至少 n 个参数
- `cobra.MaxmumNArgs(n)`：最多 n 个参数

```go
func main() {
	greetCmd := &cobra.Command{
		Use:   "greet [name]",
		Short: "问候某人",
		Args:  cobra.ExactArgs(1), // 要求 exactly 1 个参数
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("Hello, %s!\n", args[0])
		},
	}

	greetCmd.Execute()
}
```

使用：

```go
[root@JiGeX cobra-demo]# ./greet 
Error: accepts 1 arg(s), received 0
Usage:
  greet [name] [flags]

Flags:
  -h, --help   help for greet
----------------------------------------------------------------
[root@JiGeX cobra-demo]# ./greet toby
Hello, toby!
----------------------------------------------------------------
[root@JiGeX cobra-demo]# ./greet toby mint
Error: accepts 1 arg(s), received 2
Usage:
  greet [name] [flags]

Flags:
  -h, --help   help for greet
```

### 自定义参数验证

`Command` 的 `Args` 字段需要填写的是一个函数，函数的类型是 `func(cmd *Command, args []string) error`。

例如上一个例子中提到的参数：`cobra.ExactArgs(n)`，实际的定义如下：

```go
// ExactArgs returns an error if there are not exactly n args.
func ExactArgs(n int) PositionalArgs {
	return func(cmd *Command, args []string) error {
		if len(args) != n {
			return fmt.Errorf("accepts %d arg(s), received %d", n, len(args))
		}
		return nil
	}
}
```

那么我们也可以自己去定义自己的参数验证逻辑：

```go
func main() {
	greetCmd := &cobra.Command{
		Use:   "greet [name]",
		Short: "问候某人",
		Args: func(cmd *cobra.Command, args []string) error {
			if len(args) != 1 {
				return fmt.Errorf("有且仅能有一个参数")
			}
			if _, err := strconv.Atoi(args[0]); err != nil {
				return fmt.Errorf("参数必须是数字")
			}
			return nil
		},
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("Hello, %s!\n", args[0])
		},
	}

	greetCmd.Execute()
}
```

验证：

```go
[root@JiGeX cobra-demo]# ./greet 
Error: 有且仅能有一个参数
Usage:
  greet [name] [flags]

Flags:
  -h, --help   help for greet
----------------------------------------------------------------
[root@JiGeX cobra-demo]# ./greet hhh
Error: 参数必须是数字
Usage:
  greet [name] [flags]

Flags:
  -h, --help   help for greet
----------------------------------------------------------------
[root@JiGeX cobra-demo]# ./greet 111
Hello, 111!
```

### 运行前和运行后的钩子函数

`Command` 结构体中跟 `Run` 有关的三个函数：

- `PreRun(func(cmd &cobra.Command, args []string))`：运行前钩子函数
- `Run(func(cmd &cobra.Command, args []string))`：运行中执行的函数
- `PostRun(func(cmd &cobra.Command, args []string))`：运行前钩子函数

```go
func main() {
	greetCmd := &cobra.Command{
		Use:   "greet [name]",
		Short: "问候某人",
		Args:  cobra.ExactArgs(1),
		PreRun: func(cmd *cobra.Command, args []string) {
			fmt.Println("运行前的钩子函数执行")
		},
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("Hello, %s!\n", args[0])
		},
		PostRun: func(cmd *cobra.Command, args []string) {
			fmt.Println("运行后的钩子函数执行")
		},
	}

	greetCmd.Execute()
}
```

使用：

```go
[root@JiGeX cobra-demo]# ./greet toby
运行前的钩子函数执行
Hello, toby!
运行后的钩子函数执行
```









