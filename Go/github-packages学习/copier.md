# copier

## 介绍

```go
I am a copier, I copy everything from one to another.
```

支持特性：

- 基于名称匹配的字段到字段和方法到字段的复制
- copy 数据：
    - 从 slice 到 slice
    - 从 struct 到 slice
    - 从 map 到 map
- 通过标签控制字段的复制行为
    - 使用 `copier:"must"` 强制复制字段（即使复制过程中发生错误也会继续）
    - 使用 `copier:"override"` 覆盖目标字段（即使设置了 `IgnoreEmpty` 选项也会强制复制）
    - 使用 `copier:"-"` 排除字段（字段不会被复制）

## 安装

```go
go get -u github.com/jinzhu/copier
```

## 字段设置

### `copier:"-"` - Ignoring fields

```go
type Source struct {
	Name   string
	Secret string
}

type Target struct {
	Name   string
	Secret string `copier:"-"`
}

func main() {
	source := Source{Name: "John", Secret: "so_secret"}
	target := Target{}

	copier.Copy(&target, &source)
	fmt.Printf("Name: %s, Secret: '%s'\n", target.Name, target.Secret)
}

// 输出：
// Name: John, Secret: ''
```

在复制的时候，在一个字段后面加上 `copier:"-"` 的反射标志，表示复制的时候不考虑这个字段。

### `copier:"must"` - Enforcing Field Copy

```go
type MandatorySource struct {
	Identification int
}

type MandatoryTarget struct {
	ID int `copier:"must"` // This field must be copied, or it will panic/error
}

func main() {
	source := MandatorySource{}
	target := MandatoryTarget{}

	// This will result in a panic or an error since ID is a must field but is empty in source.
	if err := copier.Copy(&target, &source); err != nil {
		log.Fatal(err)
	}
}

// 输出：
// panic: Field ID has must tag but was not copied
// ...
```

在复制的 target 对象上加上 `copier:"must"` 的反射标签，表示复制的时候，这部分是必须要复制过来的，就算出错了也要复制。

如果不设置 `copier:"must"` 的话，对于没有的字段，`copier` 会直接置空。

### Specifying Custom Field Names

如果 Copy 前后的字段名不一样，可以在 target 中使用一个字段的 tag 来指定对应的字段名。

```go
type SourceEmployee struct {
	Identifier int64
}

type TargetWorker struct {
	ID int64 `copier:"Identifier"`
}

func main() {
	source := SourceEmployee{Identifier: 1001}
	target := TargetWorker{}

	copier.Copy(&target, &source)

	fmt.Printf("Workder ID: %d\n", target.ID)
}

// 输出：
// Workder ID: 1001
```

## 不同结构之间 copy

例如对于如下的结构体设置：

```go
type User struct {
	Name string
	Role string
	Age  int32
}

func (user *User) DoubleAge() int32 {
	return 2 * user.Age
}

type Employee struct {
	Name      string
	Age       int32
	DoubleAge int32
	SuperRole string
}

func (employee *Employee) Role(role string) {
	employee.SuperRole = "Super " + role
}
```

### copy from method to field with same name

```go
func main() {
	user := User{Name: "Jinzhu", Age: 18, Role: "Admin"}
	employee := Employee{}

	copier.Copy(&employee, &user)
	fmt.Printf("%#v\n", employee)
	// 输出：main.Employee{Name:"Jinzhu", Age:18, DoubleAge:36, SuperRole:"SSSuper Admin"}
}
```

我有一个理解，不知道对不对：

copy 的时候，我们先不管一个字段是一个变量还是一个函数，都看成是”字段“。然后这里我们看原本的 User 中一共有 4 个字段，分别是：`Name`、`Role`、`Age`、`DoubleAge()`。之后在 copy 的时候，遍历这几个字段，每个字段起作用一次（work 一次）。

| 字段          | 效果                                                         |
| ------------- | ------------------------------------------------------------ |
| `Name`        | 直接映射到 Employee 的 `Name` 字段                           |
| `Role`        | 映射到 Employee 的 `Role` 字段，这是一个方法，所以就执行这个方法。这样就设置好了 Employee 的 SuperRole 字段 |
| `Age`         | 直接映射到 Employee 的 `Age` 字段                            |
| `DoubleAge()` | 这是一个函数，映射到的是变量字段，所以就是 User 的 `DoubleAge()` 字段求出值之后，再赋值给 Employee 的 `DoubleAge` 字段 |

### copy struct to slice

copy 主要是在不同类型的结构体之间进行 copy。`copier` 可以将一个类型的结构体，直接 copy 到另一个类型的结构体的切片中。

```go
func main() {
	user := User{Name: "Jinzhu", Age: 18, Role: "Admin"}
	var employees []Employee

	copier.Copy(&employees, &user)

	fmt.Printf("%#v\n", employees)
	// 输出：[]main.Employee{main.Employee{Name:"Jinzhu", Age:18, DoubleAge:36, SuperRole:"Super Admin"}}
}
```

### copy slice to slice

也可以从一个类型的结构体的切片中，直接将这里的这么多对象，全都 copy 到另一种类型的结构体的切片中。

```go
func main() {
	users := []User{{Name: "Jinzhu", Age: 18, Role: "Admin"}, {Name: "Jinzhu2", Age: 20, Role: "Admin2"}}
	var employees []Employee

	copier.Copy(&employees, &users)

	fmt.Printf("%#v\n", employees)
	// 输出：[]main.Employee{main.Employee{Name:"Jinzhu", Age:18, DoubleAge:36, SuperRole:"Super Admin"}, main.Employee{Name:"Jinzhu2", Age:20, DoubleAge:40, SuperRole:"Super Admin2"}}
}
```

### copy map to map

从一种类型的 map 结构，copy 到另一种类型的 map 结构。

```go
func main() {
	map1 := map[int]int{3: 6, 4: 8}
	map2 := map[int32]int8{}

	copier.Copy(&map2, &map1)
	fmt.Printf("%#v\n", map2)
	// 输出：map[int32]int8{3:6, 4:8}
}
```

## 总结

一番折腾之后，发现其实博客 [地址](https://studygolang.com/articles/27202) 写的就很不错，比我这个简单多了。人家写的更加简洁，而且易读、易懂。

总的来说 copier 就是在不同对象之间进行 copy 操作的。但是遇到这种，我还是觉得，自己重新手搓一个方法来构造新的结构体也是不错的呀。

可能是我对 copier 的理解还是不够，但是最起码之后能看懂了，copier 就是不同结构的结构体之间进行 copy。

其中最重要的理解有一个：copy 的时候，遍历 source 对象的每一个字段，不管是变量还是函数，都要遍历一下。







