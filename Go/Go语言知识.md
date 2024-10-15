# Go 语言知识

## 1. 切片（Slice）

Go 语言中的切片（Slice）是一种非常灵活且功能强大的数据结构。它与数组类似，但具有更多的功能和灵活性。切片是对底层数组的一个动态视图，可以方便地增加、删除和修改元素。以下是切片的关键点：

### 1.1 切片的定义

切片是由三部分组成的：指向数组的指针、长度和容量。它的语法如下：

```go
var s []int
```

在这种情况下，`s` 是一个整型切片，但它还没有分配空间，需要通过赋值、`make` 函数或字面量来初始化。

### 1.2 创建切片

有几种常见的方法来创建切片：

- 字面量创建

    ```go
    s := []int{1, 2, 3, 4, 5}
    ```

    这种方式创建了一个包含 5  个整数的切片。

- 使用 `make` 函数

    ```go
    s := make([]int, 5, 10)  // 创建一个长度为 5，容量为 10 的切片
    ```

    使用 `make` 函数创建切片时，必须指定数据类型和长度。容量是可选的，若不指定默认为长度。

- 从数组或其他切片创建

    ```go
    arr := [5]int{1, 2, 3, 4, 5}
    s := arr[1:4]  // 创建一个切片，包含 arr 中第 2 到第 4 个元素
    ```

### 1.3 切片的底层数组和容量

切片实际上是对一个底层数组的引用。通过切片，我们可以访问和修改底层数组中的元素。切片的容量是指从切片的起始位置到底层数组末尾的元素数量。

```go
s := []int{1, 2, 3, 4, 5}
fmt.Println(len(s))  // 输出 5
fmt.Println(cap(s))  // 输出 5
```

对切片进行切片的时候，新切片的容量会基于原切片的剩余容量。例如：

```go
s := []int{1, 2, 3, 4, 5}
s2 := s[1:3]
fmt.Println(len(s2))
fmt.Println(cap(s2))
```

### 1.4 切片的操作

切片支持以下操作：

- 访问元素：

    ```go
    s := []int{1, 2, 3}
    fmt.Println(s[0])  // 输出 1
    ```

- 修改元素：

    ```go
    s := []int{1, 2, 3}
    s[0] = 10
    fmt.Println(s)  // 输出：[10, 2, 3]
    ```

- 追加元素：使用 `append` 函数来向切片添加元素（`append` 函数实际上是创建一个新的切片并返回）

    ```go
    s := []int{1, 2, 3}
    s = append(s, 4, 5)
    fmt.Println(s)  // 输出：[1, 2, 3, 4, 5]
    ```

- 复制切片：用 `copy` 函数将一个切片的内容复制到另一个切片中

    ```go
    s1 := []int{1, 2, 3}
    s2 := make([]int, len(s1))
    copy(s2, s1)
    fmt.Println(s2)  // 输出：[1, 2, 3]
    ```

### 1.5 切片的增长

当使用 `append` 函数向切片中添加元素时，若超出其容量，Go 会自动为切片分配一个新的底层数组，其容量通常是原容量的 2 倍。这种机制提高了切片的灵活性，但也需要注意性能和内存管理的问题。

### 1.6 切片的零值

切片的零值是 `nil`。一个零值切片的长度和容量都是 0，但它不等于空切片。我们可以使用 `make` 创建一个空切片，长度和容量都是 0。

```go
var s []int
fmt.Println(s == nil)  // 输出 true
s = []int{}
fmt.Println(len(s), cap(s))  // 输出 0 0
```

### 1.7 切片的内存管理

切片的灵活性使其在内存管理上需要注意。当一个切片从原切片创建时，它会引用同一个底层数组。所以在需要独立的数据时，建议使用 `copy` 函数来创建副本，避免共享底层数组。

切片在 Go 语言中是一种非常常用的工具，它使得数组操作更加方便和高效。通过灵活使用切片，你可以更好地管理和处理数据集。

### 1.8 `append` 函数详解

在 Go 语言中，`append` 函数用于向切片 slice 添加元素。切片是一种动态数组，`append` 函数可以方便地将新的元素添加到切片的末尾，并自动调整切片的容量。

**【`append` 函数的语法】**

```go
slice = append(slice, elem1, elem2, ...)
```

- `slice`：需要添加元素的切片。
- `elem1, elem2, ...`：要添加切片中的元素，可以是一个或多个。

**【使用示例】**

```go
package main

import "fmt"

func main() {
    numbers := []int{1, 2, 3}
    numbers = append(numbers, 4)  // 向 numbers 中添加一个元素
    fmt.Println(numbers)  // 输出：[1 2 3 4]
    
    numbers = append(numbers, 5, 6, 7)  // 添加多个元素
    fmt.Println(numbers)  // 输出：[1 2 3 4 5 6 7]
    
    moreNumbers := []int{8, 9}
    numbers = append(numbers, moreNumbers...)  // 使用 ... 将另一个切片的元素追加
    fmt.Println(numbers)  // 输出：[1 2 3 4 5 6 7 8 9]
}
```

在上述示例中，`append` 函数用于添加单个元素、多个元素和另一个切片的所有元素。

**【`append` 函数的工作原理】**

1. 如果切片的容量足够大，可以容纳新的元素，`append` 直接将元素添加到切片末尾。
2. 如果容量不足，`append` 会分配一个新的、更大容量的底层数组，将原始切片的内容复制到新数组，并添加新元素。
3. `append` 返回更新后的切片，因此要用新的切片变量（如 `numbers = append(...)`）来接受返回值。

**【注意事项】**

- `append` 不会直接修改原始切片，它会返回一个新的切片。如果需要保留拓展后的切片，需要赋值给原切片或新变量。
- `append` 是内置函数，性能高效，通常用于动态构建切片。

通过使用 `append`，可以轻松动态地构建和扩展切片，是 Go 语言中处理动态数组的关键工具。

### 1.9 `...` 语法

在 Go 语言中，`...` 称为「可变参数」或「展开操作符」，它在 `append` 函数和其他场景中用于处理可变参数列表。具体来说，`...` 有两个主要用法：

**【在 `append` 函数中用于切片展开】**

当你想把一个切片的所有元素追加到另一个切片时，可以使用 `...` 展开操作符。这样可以将整个切片作为一组单独的元素传递给 `append` 函数。例如：

```go
a := []int{1, 2, 3}
b := []int{4, 5, 6}
a = append(a, b...)  // 展开 b，并将其中的所有元素添加到 a 中
fmt.Println(a)
```

在这里，`b...` 会将切片 `b` 的所有元素分别传递给 `append` 函数，相当于 `append(a, 4, 5, 6)`。

**【在函数定义中用作可变参数】**

在函数定义中，`...` 表示该函数可以接受任意数量的参数。这些参数将被当做切片来处理。例如：

```go
func sum(numbers, ...int) int {
    total := 0
    for _, number := range numbers {
        total += numeber
    }
    return total
}

result := sum(1, 2, 3, 4)  // 可以传入任意数量的参数
fmt.Println(result)
```

在这个例子中，`number, ...int` 表示 `sum` 函数可以接受任意数量的 `int` 类型参数，并将它们作为切片处理。

**【总结】**

- 在函数调用中，`...` 将切片展开为一组独立的元素。
- 在函数定义中，`...` 表示该函数可以接受任意数量的指定类型参数，并将它们视为切片。

这两个用法使 Go 语言更具灵活性，特别是在处理不确定数量的参数时非常有用。

## 2. make 函数

在 Go 语言中，`make` 函数是一个内置函数，用于分配和初始化三种特定类型的对象：`slice`、`map` 和 `channel`。这三种类型在 Go 中需要特殊的内存分配和初始化，`make` 函数的主要作用就是完成这些操作。

### 2.1 基本语法

```go
make(t Type, size ....IngegerType) Type
```

- `t` 是要创建的类型，可以是 `slice`、`map` 或 `channel`。
- `size` 是可选的参数，用来指定 `slice` 的长度或 `channel` 的缓冲区大小。

### 2.2 具体使用

1. 创建 Slice

    ```go
    s := make([]int, 5, 10)
    ```

    这个语句创建了一个长度为 5、容量为 10 的 `int` 类型的切片。`make` 函数会为 `slice` 分配底层数组，并返回初始化后的 `slice`。

    - 长度：切片当前可用的元素数量。
    - 容量：切片底层数组的总长度（可扩展的最大值）。

    如果没有提供容量参数，容量将等于长度。

2. 创建 Map

    ```go
    m := make(map[string]int, 10)
    ```

    创建一个 `string` 类型为键，`int` 类型为值的 `map`，并为其分配空间（虽然容量参数在 `map` 中是可选的，它并不是 `map` 的上线，只是一个性能提示）。在 Go 中，`map` 的容量可以根据需要自动扩展。

3. 创建 Channel

    ```go
    c := make(chan int, 5)
    ```

    这将创建一个缓冲区大小为 5 的 `int` 类型通道。通道可以是有缓冲的（缓冲区大小大于 0）或无缓冲的（缓冲区大小为 0）。有缓冲的通道允许一定数量的元素在没有消费者接受时排队等待。

### 2.3 make 与 new 区别

- `make` 用于初始化 slice、map 和 channel。它返回的总是一个初始化后的值，而不是指针。
- `new`：用户与分配内存，返回一个只想分配类型的指针，但不会对内存进行初始化。

例如：

```go
var p *[]int = new([]int)  // p 是 *([]int) 类型
var v []int = make([]int, 10)  // v 是 []int 类型
```

- `new([]int)` 返回的是指向 slice 的指针，而 `make([]int, 10)` 返回的是 `slice` 值本身。

示例：

```go
// 示例：初始化一个切片
numbers := make([]int, 3, 5)
numbers[0] = 1
numbers[1] = 2
numbers[2] = 3
fmt.Println(numbers)  // 输出：[1 2 3]

// 示例：初始化一个 map
ageMap := make(map[string]int)
ageMap["Alice"] = 25
fmt.Println(ageMap["Alice"])  // 输出：25

// 示例：初始化一个 channel
message := make(chan string, 2)
messages <- "Hello"
messages <- "World"
fmt.Println(<-messages) // 输出：Hello
fmt.Println(<-messages) // 输出：World
```

通过 `make`，Go 提供了一种高效且便捷的方法来分配和初始化这三种常用数据结构，让我们能够更容易地操作这些数据结构。

## 3. 循环语句

在 Go 语言中，循环主要由 `for` 关键字实现，`for` 是 Go 中唯一的循环结构。它具有不同的用法，可以适应多种场景。下面是详细的介绍：

### 3.1 基本的 `for` 循环结构

类似于其他语言中的 `for` 循环，`Go` 中的基本 `for` 循环格式如下：

```go
for 初始化语句; 条件语句; 后置语句 {
    // 循环体
}
```

- 初始化语句：在循环开始时执行一次，用来初始化循环控制变量。
- 条件语句：每次循环开始时进行求值，当条件为 `true` 时执行循环体，为 `false` 时结束循环。
- 后置语句：在每次循环体执行完后执行，用于更新循环控制变量。

示例：

```go
for i := 0; i < 5; i++ {
    fmt.Println(i)
}
```

该代码将输出 0 到 4。

### 3.2 省略初始化和后置语句

在 Go 中，`for` 循环允许省略初始化语句、条件语句和后置语句，但至少要有一个分号。

示例：

```go
i := 0
for ; i < 5; {
    fmt.Println(i)
    i++
}
```

这里仅保留了条件语句，相当于一个类似 `while` 的语句。

### 3.3 for 循环的无限循环

当 `for` 循环省略了所有部分（包括分号），它会创建一个无限循环：

```go
for {
    // 无限循环体
}
```

这种结构常用于服务器程序或者需要持续运行的程序。要退出循环，可以使用 `break` 语句。

### 3.4 类似 `while` 循环

在 Go 中，没有专门的 `while` 循环，但可以使用 `for` 循环来模拟 `while`：

```go
i := 0
for i < 5 {
    fmt.Println(i)
    i++
}
```

这里省略了初始化和后置语句，只保留了条件语句，效果和 `while` 类似。

### 3.5 `for range` 循环

`for range` 是 Go 中的另一种循环形式，通常用于遍历数组、切片、字符串、`map` 或 `channel`。语法如下：

```go
for 索引, 值 := range 集合 {
    // 循环体
}
```

- 索引：集合中当前项的索引。
- 值：集合中当前项的值。

```go
numbers := []int{1, 2, 3, 4, 5}
for index, value := range numbers {
    fmt.Printf("Index: %d, Value: %d\n", index, value)
}
```

如果只需要值而不需要索引，可以使用 `_` 来忽略索引：

```go
for _, value := range numbers {
    fmt.Println(value)
}
```

### 3.6 循环控制-`break` 和 `continue`

- `break` 用于提前退出循环。
- `continue` 用于跳过当前循环中的剩余语句，并进入下一次循环。

示例：

```go
for i := 0; i < 10; i++ {
    if i == 5 {
        break  // 当 i 等于 5 时退出循环
    }
    if i % 2 == 0 {
        continue  // 跳过偶数
    }
    fmt.Println(i)
}
```

### 3.7 嵌套循环

Go 中可以嵌套 `for` 循环，比如双层循环：

```go
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        fmt.Printf("i = %d, j = %d\n", i, j)
    }
}
```

### 3.8 标签循环

如果需要跳出多层嵌套的循环，可以使用标签。标签可以用于 `break` 和 `continue` 语句，使其直接跳到指定的标签位置。

示例：

```go
OuterLoop:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i == 1 && j == 1 {
            break OuterLoop
        }
        fmt.Println("i = %d, j = %d\n", i, j)
    }
}
```

这段代码在满足 `i == 1 && j == 1` 条件时，会跳出所有循环，而不是仅跳出内层循环。

## 4. 集合（Map）

在 Go 语言中，`map` 是一种用于存储键值对的数据结构，非常类似于其他编程语言中的哈希表或字典。它可以帮助我们快速查找、插入和删除数据。下面是 Go 语言 `map` 的一些关键知识点：

**【创建 Map】**

要创建一个 Map，可以使用内建的 `make` 函数，也可以直接用字面量创建。例如：

```go
// 使用 make 创建 map
m := make(map[string]int)

// 使用字面量创建 map
m := map[string]int {
    "one": 1,
    "two": 2,
    "three": 3
}
```

在上面的例子中，`map[string]int` 表示这个 `map` 的键类型是 `string`，值类型是 `int`。

**【操作 Map】**

我们可以使用键来添加、更新、删除和查找值。示例代码如下：

```go
m := make(map[string]int)

// 添加或更新键值对
m["age"] = 25
m["store"] = 100

// 查找值
age := m["age"]
fmt.Println("Age:", age)  // 输出：Age: 25

// 删除键值对
delete(m, "score")
```

在使用 `map` 查找键时，如果该键不存在，Go 会返回值类型的零值。例如，对于 `int` 类型，返回 `0`。

**【检查键是否存在】**

Go 的 `map` 查找操作有一个特殊的用法，可以检测键是否存在：

```go
value, exist := m["age"]
if exist {
    fmt.Println("Age exists with value:", value)
} else {
    fmt.Println("Age does not exist")
}
```

上面代码中的 `exist` 是一个布尔值，如果键存在，它返回 `true`，否则返回 `false`。

**【遍历 Map】**

我们可以使用 `for` 循环遍历 `map` 中的所有键值对：

```go
for key, value := range m {
    fmt.Println("Key:", key, " Value", value)
}
```

需要注意的是，Go 中的 `map` 是无序的，遍历时不保证键值对的顺序。

**【Map 的特性和注意事项】**

- 无序性：`map` 是无序的，也就是说，每次遍历的顺序可能都不一样。
- 键的唯一性：键必须是唯一的，如果插入一个已经存在的键，它的值会被更新。
- 性能：`map` 的查找、插入和删除操作的平均时间复杂度是 O(1)。
- 键类型：`map` 的键类型必须是可以比较的（例如，`string`、`int`、`bool` 等），因为 Go 需要使用这些键来判断它们是否相等。

**【示例代码】**

以下是一个完整的示例：

```go
package main

import "fmt"

func main() {
    // 创建 map
    capitals := map[string]string {
        "China": "Beijing",
        "France": "Paris",
        "Japan": "Tokyo"
    }
    
    // 添加元素
    capitals["Italy"] = "Rome"
    
    // 更新元素
    capitals["Japan"] = "Kyoto"
    
    // 查找元素
    city, exist := capitals["China"]
    if exist {
        fmt.Println("The capital of China is:", city)
    }
    
    // 删除元素
    delete(capitals, "France")
    
    // 遍历 map
    for country, capital := range capitals {
        fmt.Println("Country:", country, "Capital:", capital)
    }
}
```

`map` 在处理需要快速查找的场景中非常有用，例如创建词典、用户数据等。

## 5. 结构体（Sturct）

在 Go 语言中，结构体（struct）是一种用户定义的复合数据类型，可以将不同类型的数据组合在一起。它类似于面向对象编程中的“类”，但在 Go 中结构体是更轻量化的数据组织方式。结构体在 Go 语言中的应用非常广泛，尤其在数据建模和组织时非常有用。下面是关于结构体的基本知识：

### 5.1 定义结构体

在 Go 语言中，结构体使用 `type` 关键字定义，格式如下：

```go
type Person struct {
    Name string
    Age int
}
```

在这个例子中，定义了一个名为 `Person` 的结构体，它包含两个字段：`Name`（字符串类型）和 `Age`（整形）。

### 5.2 创建结构体实例

可以通过多种方式创建结构体实例：

- 使用字面量创建：

    ```go
    p1 := Person{Name: "Alice", Age: 30}
    ```

- 使用 `new` 函数：

    ```go
    p2 := new(Person)
    p2.Name = "Bob"
    p2.Age = 25
    ```

- 初始化部分字段，未指定的字段会有默认零值：

    ```go
    p3 := Person{Name: "Charlie"}
    ```

### 5.3 访问和修改结构体字段

可以使用点（`.`）运算符访问或修改结构体的字段：

```go
fmt.Println(p1.Name)  // 输出：Alice
p1.Age = 31  // 修改 Age 字段
```

### 5.4 结构体嵌套

结构体可以包含其他结构体，称为嵌套结构体。这可以帮助构建更复杂的数据结构：

```go
type Address struct {
    City string
    State string
}

type Person struct {
    Name string
    Age int
    Address Address
}

p := Person {
    Name: "David",
    Age: 40,
    Address: Address {
        City: "New York",
        State: "NY",
    },
}
fmt.Println(p.Address.City)  // 输出：New York
```

### 5.5 匿名字段

Go 语言支持在结构体中定义匿名字段（embedded fields），通常用于模拟继承特性。

```go
type Contact struct {
    Phone string
    Email string
}

type Employee struct {
    Name string
    Age int
    Contact
}

e := Employee {
    Name: "Eve",
    Age: 29,
    Contact: Contact{
        Phone: "123-456-7890",
        Email: "eve@example.com",
    },
}
fmt.Println(e.Phone)  // 输出：123-456-7890
```

在这个例子中，`Employee` 结构体嵌入了 `Contact` 结构体，这样可以直接访问 `Phone` 和 `Email` 字段。

### 5.6 方法和结构体

可以为结构体定义方法。Go 不支持类，但可以为结构体类型定义方法。方法定义时，会在函数名前加上接收器（receiver）参数，制定方法属于哪个结构体：

```go
type Rectangle struct {
    Width float64
    Height float64
}

// 定义一个计算面积的方法
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

rect := Rectangle(Width: 10, Height: 5)
fmt.Println(rect.Area())  // 输出：10
```

在这个例子中，`Area` 方法计算矩形的面积。

### 5.7 值类型和指针类型

结构体在 Go 语言中是值类型，意味着当它们被赋值或传递给函数时，会创建它们的副本。如果想要修改原结构体，可以使用指针来避免副本创建。

```go
func (r *Rectangle) Scale(factor float64) {
    r.Width *= factor
    r.Height *= factor
}

rect := Rectangle{Width: 10, Height: 5}
rect.Scale(2)
fmt.Println(rect.Width)  // 输出：20
fmt.Println(rect.Height)  // 输出：10
```

这里，`Scale` 方法接收一个指针，因此能够直接修改 `rect` 的字段值。

### 5.8 零值结构体

在 Go 中，结构体的字段有默认的零值（zero value），可以直接使用而无需初始化。例如，字符串的默认值是空字符串，数值类型是 `0`，布尔类型是 `false`。

### 5.9 结构体实例和结构体指针访问字段

Go 语言中，无论通过结构体实例（例如 `p := Person{}`）还是结构体指针（例如 `p := &Person{}`）来访问字段，Go 都支持使用 `.` 操作符。Go 会自动解引用指针以访问字段，因此两者的字段访问方式是相同的。例如：

```go
type Person struct {
    Name string
    Age int
}

p1 := Person{Name: "Alice", Age: 30}
p2 := &Person{Name: "Bob", Age: 25}

// 两者都可以使用 . 来访问字段
fmt.Println(p1.Name)  // 输出：Alice
fmt.Println(p2.Name)  // 输出：Bob
```

在访问 `p2.Name` 时，Go 自动将 `p2` 解引用为 `*p2`，使得我们可以像访问普通变量一样访问它的字段，这样使用起来很方便。

### 5.10 结构体字段定义时的逗号

在 Go 语言中，当定义结构体实例时，末尾的字段通常会加上逗号（`,`），主要有以下几个原因：

- 代码风格一致性：在字段值定义的最后加逗号，使代码在增删字段时更简洁、统一。特别是在版本控制系统（如 Git）中，如果某行后面加了新字段，差异行就只显示新增的字段，不会因逗号的增删产生额外的变动。
- 防止语法错误：当结构体实例分成多行书写时，最后一个字段如果没有逗号，编译器汇报语法错误。Go 的多行实例语法要求在每一行字段之后加上逗号，即使是最后一行也不例外。

例如：

```go
p := Person {
    Name: "David",
    Age: 40,  // 即使是最后一行，也加上逗号
}
```

## 7. 范围（range）

在 Go 语言中，`range` 是一个关键字，通常用于迭代数组、切片、映射（map）和通道（channel）。使用 `range` 可以简化循环，同时提供对索引和元素值的访问。以下是 `range` 的常见用法。

### 7.1 遍历数组或切片

在数组或切片上使用 `range`，可以遍历其中的元素，并且 `range` 返回两个值：**索引**和**元素的副本**。

```go
numbers := []int{1, 2, 3, 4, 5}
for i, num := range numbers {
    fmt.Println("Index:", i, " Value:", num)
}
```

如果只需要使用元素值，可以使用 `_` 忽略索引：

```go
for _, num := range numbers {
    fmt.Println("Value:", num)
}
```

### 7.2 遍历映射（map）

在映射上使用 `range`，可以遍历每一个键值对。`range` 返回两个值：**键**和**值**。

```go
person := map[string]string{"name": "Ruochen Wei", "location": "China"}
for key, value := range person {
    fmt.Println("Key:", key, " Value:", value)
}
```

### 7.3 遍历字符串

在字符串上使用 `range` 时，返回的是字符串中每个字符的**索引**和**字符的 Unicode 码点值**。

```go
word := "Go语言"
for i, char := range word {
    fmt.Printf("Index: %d, Character: %c\n", i, char)
}
```

输出结果：

```markdown
Index: 0, Character: G
Index: 1, Character: o
Index: 2, Character: 语
Index: 5, Character: 言
```

### 7.4 遍历通道（channel）

在通道上使用 `range` 可以遍历通道中的每一个值，直到通道关闭为止。

```go
ch := make(chan int, 3)
ch <- 1
ch <- 2
ch <- 3
close(ch)  // 必须关闭通道，否则会导致死锁

for value := range ch {
    fmt.Println("Value:", value)
}
```

总结来说，`range` 是一个非常方便的关键字，可以帮助简化循环。它的灵活性使得在 Go 语言中遍历不同的数据结构变得简单。

## 8. 通道（channel）

在 Go 语言中，`Channel` 是一种用于不同 goroutine 之间传递数据的管道。Channel 在 Go 语言的并发编程中扮演了非常重要的角色，能够让 goroutine 之间进行安全、有效的通信。以下是 Channel 的详细知识：

### 8.1 Channel 的基本概念

Channel 是 Go 语言的核心并发机制之一，用于在 goroutine 之间传递数据。它们可以在没有锁的情况下实现数据的同步，让多个 goroutine 能够安全地共享数据。Channel 本质上是一种类型化的管道，既可以用于发送数据，也可以用于接收数据。

```go
ch := make(chan int)  // 创建一个传输 int 类型数据的 channel
```

### 8.2 Channel 的类型

Channel 可以是无缓冲的（unbuffered channel）或缓冲的（buffered channel）：

- 无缓冲 Channel：一个无缓冲的 channel 是同步的，发送和接收数据会阻塞，直到另一方准备好。例如，发送操作会阻塞，直到有一个 goroutine 尝试接收数据。

    ```go
    ch := make(chan int)  // 创建一个无缓冲的 channel
    go func() {
        ch <- 1  // 将 1 发送到 channel
    }()
    fmt.Println(<-ch)  // 从 channel 接收数据
    ```

- 缓冲 Channel：缓冲 channel 是异步的，发送和接收操作在缓冲区未满或非空时可以非阻塞地进行。缓冲区大小在创建 channel 时指定。

    ```go
    ch := make(chan int, 3)  // 创建一个缓冲区大小为 3 的 channel
    ch <- 1
    ch <- 2
    ch <- 3
    fmt.Println(<-ch)  // 输出 1
    ```

### 8.3 发送与接收

在 channel 中，可以通过 `<-` 操作符进行数据的发送和接收。

- 发送数据到 channel：使用 `ch<-value`，其中 `ch` 是 channel，`value` 是要发送的值。

    ```go
    ch := make(chan int)
    go func() {
        ch <- 42  // 发送值 42 到 channel
    }()
    ```

- 从 channel 接收数据：使用 `value := <-ch`，`value` 将接收到的数据存储起来。

    ```go
    result := <-ch  // 接收从 channel 中的数据
    fmt.Println(result)
    ```

### 8.4 Channel 的关闭

使用 `close()` 函数可以关闭 channel。一旦 channel 被关闭，任何发送操作都会引发 panic，接收操作将继续进行，直到 channel 中的数据被完全读取。可以通过 `v, ok := <-ch` 检查 channel 是否已经关闭，`ok` 为 `false` 表示 channel 已关闭。

```go
close(ch)
v, ok := <-ch
if !ok {
    fmt.Println("Channel 已关闭！")
}
```

### 8.5 使用 `select` 操作多个 Channel

`select` 语句允许 goroutine 等待多个 channel 的操作，类似于 `switch` 语句，但每个 `case` 都涉及 channel 操作。`select` 可以用来处理多个 `channel` 的情况，或超时情况。

```go
ch1 := make(chan int)
ch2 := make(chan int)

go func() {
    ch1 <- 1
}()

go func() {
    ch2 <- 2
}()

select {
case val := <-ch1:
    fmt.Println("Received from ch1:", val)
case val := <-ch2:
    fmt.Println("Received from ch2:", val)
default:
    fmt.Println("No data received")
}
```

### 8.6 单向 Channel

Channel 可以限制为只发送或只接收。单向 Channel 可以帮助开发者防止误用，比如限制某个函数只能发送或接收数据。

- 只发送 Channel：`chan<- int` 表示只能发送 int 类型的数据。
- 只接受 Channel：`<-chan int` 表示只能接收 int 类型的数据。

```go
func sendData(ch chan<- int) {
    ch <- 10  // 只能发送
}

func receiveData(ch <-chan int) {
    fmt.Println(<-ch)  // 只能接收
}
```

### 8.7 Channel 的常见用法

一些常见的 channel 用法包括：

- 同步操作：通过无缓冲的 channel 实现 goroutine 之间的同步。

    ```go
    done := make(chan bool)
    go func() {
        fmt.Println("Doing work...")
        done <- true
    }()
    <-done  // 等待 gorouine 完成
    ```

- 超时控制：结合 `time.After` 和 `select` 实现超时控制。

    ```go
    ch := make(chan int)
    select {
    case val := <-ch:
        fmt.Println("Received:", val)
    case <-time.After(time.Second * 1):
        fmt.Println("Time out")
    }
    ```

- 工作池（Worker Pool）：多个 goroutine 读取同一个 channel，完成并行任务。

### 8.8 注意事项

- Channel 是引用类型：当 channel 被传递到函数时，它是传递的引用。
- 避免对关闭的 channel 发送数据：对已关闭的 channel 发送数据会引发 panic。
- 确保 goroutine 不会泄露：使用 channel 时要小心，确保 goroutine 能够正确地退出，以防资源泄露。

Channel 在 Go 并发编程中至关重要，它们提供了一种简单而安全的方式来实现 gotouine 之间的通信和同步。

## 9. goroutine

在 Go 语言中，`goroutine` 是一种轻量级的线程，由 Go 运行时管理，用于并发执行代码。它是 Go 语言并发模型的核心，能够让开发者以简单、高效的方式编写并发程序。`goroutine` 非常适合 I/O 密集型或需要并行执行的任务。

### 9.1 什么是 gotoueine？

- 轻量级线程：`goroutine` 是 Go 语言内置的、受 Go 运行时管理的轻量级线程，每个 goroutine 占用的内存非常小（通常在几 Kb 左右）。相比于传统的操作系统线程，goroutine 更加轻量，并且可以在同一时间处理数千个 goroutine。
- 并发执行：使用 gotoutine，可以在同一进程中同时执行多个函数或代码段，实现并发处理。
- 独立调度：Go 运行时会为每个 goroutine 分配所需的资源，并通过调度器将它们调度到系统线程上执行。

### 9.2 创建 goroutine

创建一个 goroutine 非常简单，只需在函数调用前添加 `go` 关键字。举个简单的例子：

```go
package main

import (
	"fmt"
)

func sayHello() {
    fmt.Println("Hello form goroutine")
}

func main() {
    go sayHello()  // 创建一个新的 goroutine 执行 sayHello 函数
    fmt.Println("Hello from main")
}
```

在上面的代码中，`go sayHello()` 会启动一个新的 goroutine 执行 `sayHello()` 函数，而主 goroutine 会继续执行 `main` 函数中的代码。由于 goroutine 的执行是并发的，输出顺序可能会有不同。

### 9.3 goroutine 的工作原理

- 堆栈管理：每个 goroutine 都有自己的栈空间。与传统线程不同的是，goroutine 的栈空间是动态扩展的，初始栈较小（大约 2KB），可以根据需要增长。
- 调度器：Go 运行时包含一个 goroutine 调度器，能够自动管理和分配 goroutine 到操作系统线程上执行。
- 抢占式调度：调度器会在 goroutine 执行的过程中，根据调度策略进行切换，确保多个 goroutine 可以共享 CPU 资源。

### 9.4 goroutine 的通信与同步

在并发编程中，goroutine 之间需要通信和同步。Go 提供了 Channel 来支持 goroutine 之间的数据传递和同步。

```go
package main

import "fmt"

func sendMessage(ch chan string) {
    ch <- "Hello from goroutine"
}

func main() {
    ch := make(chan string)
    go sendMessage(ch)  // 在 goroutine 中发送消息
    message := <-ch  // 主 goroutine 接收消息
    fmt.Println(message)  // 输出消息
}
```

在上面的代码中，`sendMessage` 函数通过 `ch <- "Hello from groutine"` 将消息发送到 `ch` channel，主 goroutine 再从 `ch` 中接收消息。

### 9.5 goroutine 的生命周期

- 创建：通过 `go` 关键字创建一个新的 goroutine，并在新 goroutine 中执行指定的函数。
- 运行：goroutine 开始执行代码段，Go 运行时负责调度和管理。
- 阻塞：goroutine 可以被阻塞（如等待 channel 操作、I/O 操作等），这时调度器会将其他 goroutine 安排到空闲的操作系统线程上执行。
- 终止：当 goroutine 执行完代码或者因为 runtime panic 而终止时，它就会被销毁，Go 运行时会回收相关资源。

### 9.6 goroutine 的应用场景

- I/O 密集型操作：goroutine 非常适合处理 I/O 密集型任务（如网络请求、文件改写等），因为他们可以通过并发来提高性能。
- 并行计算：在多核处理器上，可以使用多个 goroutine 来同时执行密集型任务，提高吞吐量。
- 事件处理：在服务器应用中（如 web 服务器），可以为每个请求创建一个 goroutine 进行处理，从而实现并发处理多个请求。

### 9.7 常见的 goroutine 问题

- goroutine 泄露：如果没有妥善管理 goroutine，它们可能会无限期地等待某个事件（如 channel 操作），造成资源浪费。确保 goroutine 能够在完成任务后正确退出。
- 数据竞争：当多个 goroutine 访问和修改共享数据时，可能会出现数据竞争。为了避免这种情况，可以使用 Channel 进行通信，或者使用 `sync.Mutex` 来保护共享数据。

### 9.8 使用 `sync.WaitGroup` 等待 goroutine 完成

可以使用 `sync.WaitGroup` 来等待多个 goroutine 完成。`WaitGroup` 提供了 `Add()`、`Done()` 和 `Wait()` 方法来控制。

```go
package main

import (
	"fmt"
    "sync"
)

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()  // 在函数结束时调用 Done()
    fmt.Printf("Worker %d is working\n", id)
}

func main() {
    var wg sync.WaitGroup
    for i := 1; i <= 3; i++ {
        wg.Add(1)  // 增加计数器
        go worker(i, &wg)
    }
    wg.Wait()  // 等待所有 goroutine 完成
    fmt.Println("All workers done")
}
```

在上面的代码中，`WaitGroup` 确保主 goroutine 在所有 worker goroutine 完成后再退出。

### 9.9 goroutine 的优点

- 高效的资源利用：goroutine 非常轻量，比传统线程更省资源。
- 简单的并发模型：通过 `go` 关键字即可创建 goroutine，配合 Channel 实现安全的并发。
- 高度可扩展性：goroutine 的并发模型允许我们轻松地编写高并发的代码，特别适合服务器开发。

总结：goroutine 是 Go 语言并发编程的核心，结合 Channel，可以实现高效、简洁的并发模型。它们不仅轻量级，而且具备自动调度、栈空间可扩展等特性，是编写并发程序的得力工具。

## 10. 字符串

Go 语言中的字符串（`string`）是一个非常重要且常用的数据类型。理解字符串的特定、操作和常见用法对于编写高效、可靠的 Go 程序至关重要。

### 10.1 字符串基本概念

**【字符串的定义】**

在 Go 语言中，字符串是一个不可变的字节序列。这意味着一旦字符串被创建，其内容不能被修改。字符串可以包含任意的数据，但通常用于表示文本，即 Unicode 字符序列。

```go
var s string = "Hello, 世界"
```

**【字符串的底层实现】**

Go 语言的字符串实际上是一个结构体，包含以下两个字段：

- 指向字节数组的指针：指向实际存储字符串内容的内存地址。
- 字符串的长度：字符串所占的字节数。

由于字符串是不可变的，对字符串的任何操作都会创建新的字符串，而不会修改原有的字符串。

### 10.2 字符串的表示方式

**【字符串字面量】**

Go 语言中的字符串字面量可以通过以下两种方式表示：

- 双信号字符串（解释字符串）：使用双引号 `""` 包裹的的字符串，支持转义字符。

    ```go
    s := "Hello\nWorld"
    ```

- 反引号字符串（原始字符串）：使用反引号 ` `` ` 包裹的字符串，支持多行，不支持转义字符。

    ```go
    s := `Hello
    World`
    ```

**【字符表示】**

Go 语言中没有专门的字符类型，但有一个别名类型 `rune`，表示 Unicode 码点，实际上是 `int32` 别名。使用单引号 `''` 表示字符。

```go
var ch rune = '中'
```

需要注意的是，`rune` 占用 4 个字节，能够表示所有的 Unicode 字符。

### 10.3 字符串的编码

**【UTF-8 编码】**

Go 语言的字符串采用 UTF-8 编码方式存储，这是一种兼容 ASCII 的多字节编码方案，能够表示所有的 Unicode 字符。

**【字符串的长度】**

- 字节长度：使用内置函数 `len(s)`，返回字符串所占的字节数。

    ```go
    s := "Hello, 世界"
    fmt.Println(len(s))  // 输出 13，因为「世界」每个汉字占 3 个字节
    ```

- 字符长度：需要将字符串转换为 `[]rune`，然后再获取长度。

    ```go
    fmt.Println(len([]rune(s)))  // 输出 9，正确的字符数量
    ```

### 10.4 字符串的操作

**【索引和切片】**

- 索引：可以通过索引获取字符串中的字节，但不能修改。

    ```go
    s := "Hello"
    fmt.Println(s[0])  // 输出 72，对应字符 'H' 的 ASCII 码
    fmt.Println("%c\n", s[0])  // 输出字符 'H'
    ```

- 切片：可以对字符串进行切片操作，得到子字符串。

    ```go
    runes := []rune(s)
    sub := string(runes[7:])
    fmt.Println(sub)  // 正确输出：世界
    ```

    注意：由于中文字符占多个字节，直接对字符串切片可能会导致乱码。解决方法是将字符串转换为 `[]rune`。

**【字符串拼接】**

- 使用加号 `+` 进行字符串拼接。

    ```go
    s1 := "Hello"
    s2 := "World"
    s := s1 + ", " + s2 + "!"
    ```

- 使用 `fmt.Sprintf` 格式化字符串。

    ```go
    s := fmt.Sprintf("%s, %s!", s1, s2)
    ```

- 使用 `strings.Join()` 函数拼接字符串切片。

    ```go
    s := strings.Join([]string{s1, s2}, ",")
    ```

**【字符串比较】**

- 直接使用 `==` 和 `!=` 比较字符串内容。

    ```go
    if s1 == s2 {
        fmt.Println("字符串相等")
    }
    ```

- 使用 `strings.Compare` 函数。

    ```go
    result := strings.Compare(s1, s2)
    ```

**【字符串查找】**

- 使用 `strings.Contains` 判断是否包含子串。

    ```go
    if strings.Contains(s, "World") {
        fmt.Println("包含子串")
    }
    ```

- 使用 `strings.Index` 获取子串的位置。

    ```go
    index := strings.Index(s, "World")
    ```

- 使用正则表达式匹配字符串（需要导入 `regexp` 包）。

    ```go
    matched, _ := regexp.MatchString("Wor(ld)", s)
    ```

**【字符串替换】**

- 使用 `strings.Replace` 或 `strings.ReplaceAll` 进行字符串替换。

    ```go
    newStr := strings.Replace(s, "World", "Go", 1)
    ```

**【字符串分割】**

- 使用 `strings.Split` 将字符串按照指定分隔符分割为切片。

    ```go
    parts := strings.Split(s, ", ")
    ```

**【大小写转换】**

- 将字符串转换为大写或小写。

    ```go
    upper := strings.ToUpper(s)
    lower := strings.ToLower(s)
    ```

### 10.5 字符串与其他类型的转换

**【字符串与字节切片】**

- 字符串转字节切片

    ```go
    s := "Hello, 世界"
    b := []byte(s)
    ```

- 字节切片转字符串

    ```go
    b := []byte{72, 101, 108, 108, 111}
    s := string(b)
    ```

**【字符串与 `[]rune`】**

- 字符串转 `[]rune`

    ```go
    s := "Hello, 世界"
    runes := []rune(s)
    ```

- `[]rune` 转字符串

    ```go
    s = string(runes)
    ```

**【字符串与数字类型】**

- 字符串转整数

    ```go
    s := "123"
    num, err := strconv.Atoi(s)
    if err != nil {
        // 处理错误
    }
    ```

- 整数转字符串

    ```go
    num := 123
    s := strconv.Itoa(num)
    ```

- 字符串转浮点数

    ```go
    s := "123.456"
    f, err := strconv.ParseFloat(s, 64)
    if err != nil {
        // 处理错误
    }
    ```

- 浮点数转字符串

    ```go
    f := 123.456
    s := strconv.FormatFloat(f, 'f', 2, 64)  // 保留两位小数
    ```

### 10.6 字符串的遍历

**【按字节遍历】**

- 直接使用索引遍历字符串，获取的是每个字节的值。

    ```go
    s := "Hello, 世界"
    for i := 0; i < len(s); i++ {
        fmt.Println("%x ", s[i])
    }
    ```

**【按字符遍历】**

- 使用 `for range` 遍历字符串，能够正确处理多字节字符。

    ```go
    s := "Hello, 世界"
    for index, ch := range s {
        fmt.Printf("索引：%d，字符：%c\n", index, ch)
    }
    ```

### 10.7 字符串的常用函数

Go 标准库的 `strings` 包提供了丰富的字符串处理函数：

- `strings.TrimSpace`：去除字符串首尾的空白字符。

    ```go
    s := strings.TrimSpace("  Hello, World!  ")
    ```

- `strings.HasPrefix / strings.HasSuffix`：判断字符串是否以制定前缀或后缀开头或结尾。

    ```go
    if strings.HasPrefix(s, "Hello") {
        fmt.Println("以 Hello 开头")
    }
    ```

- `strings.Count`：统计子串在字符串中出现的次数。

    ```go
    count := strings.Count(s, "l")
    ```

- `strings.Repeat`：重复字符串。

    ```go
    s := strings.Repeat("Go", 3)  // "GoGoGo"
    ```

- `strings.Title`：将字符串的每个单词首字符大写。

    ```go
    s := strings.Title("hello world")  // "Hello World"
    ```

### 10.8 字符串的性能优化

**【使用 `strings.Builder`】**

- `strings.Builder` 是 Go 1.10 引入的，用于高效地构建字符串，避免频繁的内存分配。

    ```go
    var builder strings.Builder
    builder.WriteString("Hello")
    builder.WriteString(", ")
    builder.WriteString("World")
    s := builder.String()
    ```

**【使用字节缓冲区 `bytes.Buffer`】**

- 另一种方式是使用 `bytes.Buffer`。

    ```go
    var buffer bytes.Buffer
    buffer.WriteString("Hello")
    buffer.WriteString(", ")
    buffer.WriteString("World")
    s := buffer.String()
    ```

**【预分配内存】**

- 如果可以预估字符串的最终长度，使用 `strings.Builder.Grow` 方法预分配内存。

    ```go
    var builder strings.Builder
    builder.Grow(100)  // 预分配 100 字节
    ```

### 10.9 常见问题和注意事项

**【字符串的不可变性】**

- 字符串是不可变的，无法修改字符串中的某个字符。

    ```go
    s := "Hello"
    // s[0] = 'h'  // 错误：cannot assign to s[0]
    ```

- 如果需要修改字符串，可以将其转换为 `[]byte` 或 `[]rune`，进行修改后再转换回字符串。

    ```go
    b := []byte(s)
    b[0] = 'h'
    s = string(b)
    ```

**【字符串切片的风险】**

- 直接对字符串进行切片可能会导致乱码，尤其是包含多字节字符的情况下。

    ```go
    s := "Hello, 世界"
    sub := s[:8]  // 可能会截断汉字
    ```

- 解决方法：将字符串转换为 `[]rune` 后再进行切片。

    ```go
    runes := []rune(s)
    sub := strings(runes[:8])
    ```

**【字符串比较的效率】**

- 直接使用 `==` 比较字符串，在长度不同时效率非常高，因为 Go 会先比较长度。

**【字符串拼接的性能问题】**

- 频繁的字符串拼接会导致性能下降，因为每次拼接都会创建新的字符串对象。
- 解决方法：使用 `strings.Builder` 或 `bytes.Buffer`。

### 10.10 总结

Go 语言中的字符串是功能强大且灵活的数据类型。理解其不变性、编码方式以及与其他类型的转换，对编写高效、可靠的 Go 程序非常重要。合理使用标准库提供的字符串处理函数和工具，可以大大提高开发效率，避免常见的陷阱和错误。



































## 11. defer语句

在 Go 语言中，`defer` 关键字用于延迟函数的执行，直到外层函数返回后再执行。这个特性在资源管理、清理工作等场景中非常有用，确保特定代码在函数完成时运行，无论函数是正常退出还是因为错误退出。

### 11.1 基本用法

`defer` 语句会将后面的函数或表达式推迟到外层函数的末尾执行。其基本语法如下：

```go
defer funcName(args)
```

当 `defer` 被调用时，后面的函数不会立即执行，而是在外层函数返回时才执行。一个简单的例子是资源释放，比如关闭文件：

```go
package main

import (
	"fmt"
    "os"
)

func main() {
    file, err := os.Open("example.txt")
    if err != nil {
        fmt.Println(err)
        return
    }
    defer file.Close()
    // 在函数结束时，file 会被自动关闭
}
```

在这个例子中，即使在函数内出现了错误，文件句柄在函数退出时也会被关闭，避免资源泄露。

### 11.2 多个 defer 语句

如果在一个函数中使用了多个 `defer`，他们会按照「后进先出」的顺序执行。可以理解为站结构，最后一个 `defer` 会最先执行：

```go
package main

import "fmt"

func main() {
    defer fmt.Println("First")
    defer fmt.Println("Second")
    defer fmt.Println("Third")
}
```

输出结果将会是：

```markdown
Third
Second
First
```

### 11.3 函数参数的计算时机

`defer` 的参数会在声明时被立即计算，而不是真正执行 `defer` 时。例如：

```go
package main

import "fmt"

func main(){
    x := 5
    defer fmt.Println(x)  // 此时 x 的值为 5
    x = 10
}
```

输出结果是 `5`，而不是 `10`。这是因为 `defer` 语句在声明时就计算了参数值，而不是在执行时才计算。

### 11.4 defer 在错误处理中的应用

Go 语言没有异常处理机制，常用 `defer` 与 `recover` 搭配处理错误。`recover` 用于捕获 `panic`，从而避免程序崩溃。示例如下：

```go
package main

import "fmt"

func main() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recoverd from:", r)
        }
    }()
    panic("something went wrong")
}
```

输出结果是：

```markdown
Recoverd from: something went wrong
```

### 11.5 defer 的性能考虑

`defer` 的性能在 Go 1.14 版本之前较慢，因为每次调用 `defer` 都需要额外的开销。然而，Go 1.14 优化了 `defer` 的实现，较少了开销。因此，在新版本中，`defer` 的性能基本不是问题，可以更放心地使用。

总结一下，`defer` 是 Go 语言中非常强大和方便的特性，特别适合用于清理资源、处理错误等需要在函数退出时运行的场景。在使用 `defer` 时，需要注意参数计算时机和多个 `defer` 的执行顺序。

### 11.6 panic 和 recover

在 Go 语言中，`panic` 和 `recover` 是处理异常的机制。虽然 Go 没有像其他语言那样的异常捕获机制（如 `try-catch`），但通过 `panic` 和 `recover` 可以实现类似的效果，尤其适合用于程序崩溃和错误处理。

**【`panic` 函数】**

`panic` 用于让函数立即崩溃。它可以接收一个参数（通常是字符串或错误类型），并在调用后停止当前函数的执行，同时逐层回退栈中的函数，直到遇到 `recover()`，或者直接崩溃。`panic` 常见的用途有：

- 遇到不可恢复的错误，如文件无法打开，连接失败等。
- 编写库代码时，用于通知调用方发生了严重错误。

示例代码：

```go
package main

import "fmt"

func main() {
    fmt.Println("Start")
    panic("Something went wrong!")
    fmt.Println("End")  // 不会执行
}
```

当执行 `panic` 后，后续代码将不再运行，而是退出当前函数，并逐层回退。上例中的输出是：

```markdown
Start
panic: Something went wrong!
```

**【`recover` 函数】**

`recover` 是 Go 中的内建函数，它用于从 `panic` 状态中恢复，让程序继续执行。`recover` 必须在 `defer` 中调用，因为只有在 `defer` 延迟执行的函数中，`recover` 才能捕获到 `panic`。

`recover` 的返回值是传递给 `panic` 的信息（通常是字符串或错误），如果函数中没有发生 `panic`，则返回 `nil`。通过 `recover`，可以在适当的地方捕获错误，防止程序崩溃。

示例代码：

```go
package main

import "fmt"

func main() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recoverd from panic:", r)
        }
    }()
    
    fmt.Println("Start")
    panic("Something went wrong!")
    fmt.Println("End")  // 不会执行
}
```

输出结果是：

```markdown
Start
Recoverd from panic: Something went wrong!
```

在这里，`recover` 捕获到了 `panic` 传递的信息，程序没有崩溃，而是恢复过来继续执行了。需要注意的是，`recover` 必须放在 `defer` 中才有效，否则无法捕获到 `panic`。

**【`panic` 和 `recover` 的典型用法】**

`panic` 和 `recover` 主要用于恢复不可恢复的错误或者必须立即停止程序执行的情况。大多数情况下，推荐返回错误值（如 `error`）进行错误处理。只有在那些非常严重或预料不到的错误发生时，才使用 `panic`。

示例：自定义错误处理

有时我们可以编写一个高层函数来捕获整个程序中的 `panic`，如在服务器程序中这样应用：

```go
package main

import "fmt"

func main() {
    safeFunction()
    fmt.Println("Main function continues running!")
}

func safeFunction() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recover from panic:", r)
        }
    }()
    
    riskyFunction()
}

func riskyFunction() {
    fmt.Println("About to panic!")
    panic("Unexpected error!")
    fmt.Println("Theis line will not execute.")
}
```

输出为：

```markdown
About to panic!
Recover from panic: Unexpected error!
Main function continues running!
```

在这个例子中，`safeFunction` 包裹了 `riskyFunction` 的调用，保证即使出现了 `panic`，程序也不会崩溃，而是能优雅地恢复并继续执行。

**【总结】**

- `panic` 用于不可恢复的错误，会停止当前函数并逐层回退。
- `recover` 用于在 `defer` 中捕获 `panic`，从而防止程序崩溃。
- `panic` 和 `recover` 应该谨慎使用。一般情况下，Go 中推荐使用返回错误值的方式来处理错误。`panic` 和 `recover` 适合在程序关键部分的错误处理，如服务器崩溃、资源清理等。































