# uitable

## 介绍

`uitable` 用于在命令行输出格式化的表格，适用于 CLI 的数据展示，提升输出的可读性。

## 安装

```go
go get github.com/gosuri/uitable
```

## API

| API                        | 示例                          | 说明                                     |
| -------------------------- | ----------------------------- | ---------------------------------------- |
| `New()`                    | `table := uitable.New()`      | 创建一个新的表格                         |
| `AddRow(...interface{})`   | `table.AddRow("Name", "Age")` | 向表格中添加一行数据                     |
| `RightAlign(colIndex int)` | `table.RightAlign(0)`         | 设置第 1 列右对齐（默认是左对齐）        |
| `MaxColWidth`              | `table.MaxColWidth = 30`      | 设置每列最大 30 字符宽度，超出之后会省略 |
| `Separator`                | `table.Separator = " | "`     | 默认分隔符是 `\t`                        |
| `String() string`          | `fmt.Print(table.String())`   | 获取表格的字符串形式                     |
| `Wrap`                     | `table.Wrap = true`           | 超出长度时自动换行，而不是省略           |

## demo

### demo1 - 最简表格

```go
func main() {
	table := uitable.New()
	table.AddRow("ID", "Product", "Status")
	table.AddRow(1, "Laptop", "In Stock")
	table.AddRow(2, "Keyboard", "Out of Stock")
	fmt.Println(table)
}
```

输出：

```go
ID      Product         Status      
1       Laptop          In Stock    
2       Keyboard        Out of Stock
```

### demo2 - 对齐与列宽控制

```go
func main() {
	table := uitable.New()
	table.AddRow("Item", "Price(USD)", "Sold") // 表头
	table.AddRow("----", "----------", "----") // 手动分割线
	table.RightAlign(1)                        // 价格右对齐
	table.RightAlign(2)                        // 销量右对齐
	table.MaxColWidth = 12                     // 限制列宽
	table.AddRow("Wireless Mouse", 29.99, 150)
	table.AddRow("4K Monitor", 399.99, 23)
	fmt.Println(table)
}
```

输出：

```go
Item            Price(USD)      Sold
----            ----------      ----
Wireless ...         29.99       150
4K Monitor          399.99        23
// 注意，这里的 Wireless 后面被省略
```

### demo3 - 设置分隔符+打印对象信息

```go
func main() {
	users := []User{
		{name: "张三", age: 18, city: "北京"},
		{name: "李四", age: 20, city: "上海"},
		{name: "王五", age: 22, city: "广州"},
		{name: "赵六", age: 233333, city: "陕西西安"},
	}

	table := uitable.New()
	table.AddRow("name", "age", "city")
	table.AddRow("----", "---", "----")
	table.Separator = " | "
	for _, user := range users {
		table.AddRow(user.name, user.age, user.city)
	}
	fmt.Println(table)
}
```

输出：

```go
name | age    | city    
---- | ---    | ----    
张三 | 18     | 北京    
李四 | 20     | 上海    
王五 | 22     | 广州    
赵六 | 233333 | 陕西西安
```

### demo4 - 加入颜色控制打印复杂信息

```go
type hacker struct {
	Name, Birthday, Bio string
}

var hackers = []hacker{
	{"Ada Lovelace", "December 10, 1815", "Ada was a British mathematician and writer, chiefly known for her work on Charles Babbage's early mechanical general-purpose computer, the Analytical Engine"},
	{"Alan Turing", "June 23, 1912", "Alan was a British pioneering computer scientist, mathematician, logician, cryptanalyst and theoretical biologist"},
}

func main() {
	table := uitable.New()
	table.MaxColWidth = 50

	fmt.Println("==> List")
	table.AddRow("NAME", "BIRTHDAY", "BIO")
	for _, hacker := range hackers {
		table.AddRow(hacker.Name, hacker.Birthday, hacker.Bio)
	}
	fmt.Println(table)

	fmt.Print("\n==> Details\n")
	table = uitable.New()
	table.MaxColWidth = 80
	table.Wrap = true
	for _, hacker := range hackers {
		table.AddRow("Name:", hacker.Name)
		table.AddRow("Birthday:", hacker.Birthday)
		table.AddRow("Bio:", hacker.Bio)
		table.AddRow("") // blank
	}
	fmt.Println(table)

	fmt.Print("\n==> Multicolor Support\n")
	table = uitable.New()
	table.MaxColWidth = 80
	table.Wrap = true
	for _, hacker := range hackers {
		table.AddRow(color.RedString("Name:"), color.WhiteString(hacker.Name))
		table.AddRow(color.BlueString("Birthday:"), hacker.Birthday)
		table.AddRow(color.GreenString("Bio:"), hacker.Bio)
		table.AddRow("") // blank
	}
	fmt.Println(table)
}

```

输出：

![image-20250724104224982](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250724104224982.png)







