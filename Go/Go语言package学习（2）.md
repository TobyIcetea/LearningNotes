# Go 语言 package 学习（2）

## 6. rand

在 Go 语言中，`math/rand` 包用于生成伪随机函数。该包提供了一系列函数，可以生成各种类型的随机数，包括整数、浮点数和排列。

### 6.1 基本随机数生成函数

- `rand.Int()`

    - 返回一个介于 `0` 到 `math.MaxInt32` 之间的非负随机整数。

    - 示例：

        ```go
        package main
        
        import (
        	"fmt"
        	"math/rand"
        )
        
        func main() {
        	fmt.Println(rand.Int())
        }
        ```

- `rand.Intn(n int)`

    - 返回一个介于 `0`（包含）到 `n`（不包含）之间的随机整数。

    - 示例：

        ```go
        fmt.Println(rand.Intn(100))  // 生成 0 到 99 之间的随机整数
        ```

- `rand.Float32()`

    - 返回一个介于 `0.0` 到 `1.0` 之间的随机 `float32` 数。

    - 示例：

        ```go
        fmt.Println(rand.Float32())
        ```

- `rand.Float64()`

    - 返回一个介于 `0.0` 到 `1.0` 之间的随机 `float64` 数。

    - 示例：

        ```go
        fmt.Println(rand.Float64())
        ```

### 6.2 随机排列和选择

- `rand.Perm(n int)`

    - 返回一个长度为 `n` 的整数切片，包含 `[0, n)` 的一个随机排列。

    - 示例：

        ```go
        nums := rand.Perm(5)
        fmt.Println(nums)  // 可能输出 [4 1 2 3 0]
        ```

### 6.3 随机种子

- `rand.Seed(seed int64)`

    - 设置全局随机数生成种子。默认情况下，Go 的随机数生成器使用固定的种子，所以如果不设置种子，每次运行程序都会产生相同的随机数序列。

    - 通常使用当前时间来设置种子：

        ```go
        import (
            "time"
        )
        
        rand.Seed(time.Now().UnixNano())
        ```

    - `rand.NewSource(seed int64)` 和 `rand.New(r rand.Source)`

        - 创建一个新的随机数生成源，可以用于创建独立的随机数生成器实例。

        - 实例：

            ```go
            package main
            
            import (
            	"fmt"
            	"math/rand"
            )
            
            func main() {
            	source := rand.NewSource(time.Now().UnixNano())
            	r := rand.New(source)
            	fmt.Println(r.Intn(100))
            
            	// 我更习惯于直接这样写
            	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
            	fmt.Println(rng.Intn(100))
            }
            ```

### 6.4 注意事项

- 线程安全性：`math/rand` 包的全局函数不是线程安全的。如果在多个 goroutine 中使用，建议为每个 goroutine 创建独立的随机数生成器实例。
- 密码学安全：`math/rand` 生成的随机数不适合用于安全相关的场景，如密码生成或加密秘钥。对于这些用途，应使用 `crypto/rand` 包。

### 6.5 生成随机字符串

下面是一个使用 `rand` 包生成随机字符串的示例：

```go
package main

import (
	"fmt"
	"math/rand"
	"time"
)

func main() {
	letters := []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
	s := make([]rune, 50)
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	for i := range s {
		s[i] = letters[rng.Intn(len(letters))]
	}
	fmt.Println(string(s))
}
```

### 6.6 总结

- 使用 `rand.Seed` 设置随机数种子，以避免每次运行产生相同的序列。
- 使用 `rand.Intn`、`rand.Float64` 等函数生成不同类型的随机数。
- 对于并发场景，使用 `rand.New` 创建独立的随机数生成器实例。
- 不要将 `math/rand` 用于安全敏感的随机数生成。

## 7. time

## 8. io

## 9. regexp

## 10. log