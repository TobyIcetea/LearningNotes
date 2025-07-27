# testify

## 介绍

是一个用来改进测试的库，解决了标准版 `testing` 库中测试代码冗长、断言不够直观的问题。

比如说，在之前，我们在 test 方法中会这样写：

```go
if result != expected {
    t.Errorf("Expected %v, got %v", expected, result)
}
```

现在有了 `testify`，我们可以直接写：

```go
assert.Equal(t, expected, result)
```

## 安装

```go
go get github.com/stretchr/testify
```

## `assert` 和 `require`

testify 的核心用法都在 `assert` 和 `require` 两个包中，它们提供了丰富的断言函数：

- `github.com/stretchr/testify/assert` 包：断言失败时记录操作，但继续执行后续测试代码
- `github.com/stretchr/testify/require` 包：断言失败时立即停止测试（相当于 `t.Fatal`）

相当于 `assert` 出错的时候就是返回一个 `error`，`require` 就是比较强硬的条件，出错的时候直接 `panic()`。

> 两个包中的函数其实都差不多一样的。`assert` 相对来说用的比较多。

## Demo

### 比较值是否相等

```go
func TestBasicEquality(t *testing.T) {
	// 测试基本类型比较
	assert.Equal(t, 42, 42, "整数应该相等")
	assert.Equal(t, "hello", "hello", "字符串应该相等")

	// 测试切片比较
	slice1 := []int{1, 2, 3}
	slice2 := []int{1, 2, 3}
	assert.Equal(t, slice1, slice2, "切片内容应该相等")

	// 测试结构体比较
	type User struct {
		ID   int
		Name string
	}
	user1 := User{ID: 1, Name: "Alice"}
	user2 := User{ID: 1, Name: "Alice"}
	assert.Equal(t, user1, user2, "结构体内容应该相等")
}
```

测试结果：

```go
=== RUN   TestBasicEquality
--- PASS: TestBasicEquality (0.00s)
PASS
ok  	testify-demo	0.002s
```

### 使用 `require` 处理前置条件

```go
// 模拟一个可能失败的初始化函数
func setupDatabase() (*string, error) {
	// 实际中可能是数据库连接等
	return new(string), nil
}

func TestDatabaseOperations(t *testing.T) {
	// 必须成功的初始化 - 使用 require
	db, err := setupDatabase()
	require.NoError(t, err, "数据库初始化不应该出错")
	require.NotNil(t, db, "数据库连接不应该为空")

	// 只有前面的 require 通过，才会执行到这里
	assert.Equal(t, "", *db, "新数据应为空")

	// 模拟数据库操作
	*db = "test data"
	assert.Equal(t, "test data", *db, "数据库应被正确设置")
}
```

测试结果：

```go
=== RUN   TestDatabaseOperations
--- PASS: TestDatabaseOperations (0.00s)
PASS
ok  	testify-demo	0.002s
```

### 错误类型与类型断言

```go
// 自定义错误类型
type CustomError struct {
	message string
}

func (e *CustomError) Error() string {
	return e.message
}

func divide(a, b int) (int, error) {
	if b == 0 {
		return 0, &CustomError{message: "divide by zero"}
	}
	return a / b, nil
}

func TestErrorHandling(t *testing.T) {
	// 测试应该返回错误的情况
	_, err := divide(10, 0)
	assert.Error(t, err, "除以零应该返回错误")

	// 检查错误类型
	assert.IsType(t, &CustomError{}, err, "错误应为 CustomError 类型")

	// 检查错误消息
	assert.EqualError(t, err, "divide by zero", "错误消息应匹配")

	// 使用 require 检查必须通过的错误类型
	require.ErrorAs(t, err, &CustomError{}, "错误应能转换为 CustomError")

	// 测试不应该返回错误的情况
	result, err := divide(10, 2)
	assert.NoError(t, err, "正常除法不应出错")
	assert.Equal(t, 5, result, "结果应为 5")
}
```

测试结果：

```go
=== RUN   TestErrorHandling
--- PASS: TestErrorHandling (0.00s)
PASS
ok  	testify-demo	0.002s
```

### 子测试与更复杂的断言

```go
type Person struct {
	Name    string `json:"name"`
	Age     int    `json:"age"`
	IsAdult bool   `json:"is_adult"`
}

func TestJSONProcessing(t *testing.T) {
	// 设置测试数据
	testCases := []struct {
		name     string
		input    string
		expected Person
		isValid  bool
	}{
		{"Valid adult", `{"name":"Alice","age":30,"is_adult":true}`, Person{"Alice", 30, true}, true},
		{"Valid minor", `{"name":"Bob","age":15,"is_adult":false}`, Person{"Bob", 15, false}, true},
		{"Invalid JSON", `{"name":"Charlie", "age":25`, Person{}, false},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			var p Person

			// 测试 JSON 解析
			err := json.Unmarshal([]byte(tc.input), &p)

			if tc.isValid {
				// 有效 JSON 应该成功解析
				assert.NoError(t, err, "JSON 解析不应出错")

				// 使用 ElementsMatch 比较结构体字段
				assert.Equal(t, tc.expected.Name, p.Name)
				assert.Equal(t, tc.expected.Age, p.Age)
				assert.Equal(t, tc.expected.IsAdult, p.IsAdult)

				// 检查特定条件
				assert.Equal(t, p.Age >= 18, p.IsAdult, "IsAdult 字段应与年龄匹配")
			} else {
				// 无效 JSON 应该返回错误
				assert.Error(t, err, "无效 JSON 应返回错误")
			}
		})
	}
}
```

测试结果：

```go
=== RUN   TestJSONProcessing
=== RUN   TestJSONProcessing/Valid_adult
=== RUN   TestJSONProcessing/Valid_minor
=== RUN   TestJSONProcessing/Invalid_JSON
--- PASS: TestJSONProcessing (0.00s)
    --- PASS: TestJSONProcessing/Valid_adult (0.00s)
    --- PASS: TestJSONProcessing/Valid_minor (0.00s)
    --- PASS: TestJSONProcessing/Invalid_JSON (0.00s)
PASS
ok  	testify-demo	0.002s
```

> testify 中就是，API 的名字是什么，就表示这里它应该怎么样，或者说我们期待它怎么样。比如说：
>
> - `assert.Equal(a, b)` 表示 a 和 b 应该是相等的。不相等的话，就报错。
> - `assert.Error(err)` 表示这里我们期待 `err != nil`，它应该就是一个实实在在出错的 err 实体。
> - `assert.NoError(err)` 表示这里我们期待 `err == nil`。如果 `err != nil`，就表示测试出错。

### 自定义比较与条件检查

```go
func TestAdvancedAssertions(t *testing.T) {
	// 1. 浮点数比较（考虑精度）
	assert.InDelta(t, 3.1415926, math.Pi, 0.001, "π 应该在误差范围内")

	// 2. 时间相关断言
	now := time.Now()
	later := now.Add(2 * time.Second)
	assert.WithinDuration(t, now, later, 3*time.Second, "时间应该在指定范围内")

	// 3. 条件断言
	assert.Condition(t, func() bool {
		return math.Sqrt(4) == 2
	}, "平方根计算应该正确")

	// 4. 集合操作
	assert.Contains(t, []string{"apple", "banana", "cherry"}, "banana", "应包含香蕉")
	assert.ElementsMatch(t, []int{1, 2, 3}, []int{3, 2, 1}, "元素应该匹配（与顺序无关）")

	// 5. 函数是否 panic
	assert.Panics(t, func() {
		panic("expected panic")
	}, "函数应该 panic")

	// 6. 部分匹配（结构体/JSON）
	type Response struct {
		Status  string
		Data    map[string]interface{}
		Message string
	}

	resp := Response{
		Status: "success",
		Data: map[string]interface{}{
			"id":   123,
			"name": "test",
		},
		Message: "Operation completed",
	}

	// 只检查部分字段
	assert.Contains(t, resp.Status, "success")
	assert.Contains(t, resp.Message, "completed")
	assert.Contains(t, resp.Data, "name")
}
```

测试结果：

```go
=== RUN   TestAdvancedAssertions
--- PASS: TestAdvancedAssertions (0.00s)
PASS
ok  	testify-demo	0.002s
```

> 就是对于一些常用的，比如说判断两个值之间差值、判断两个 time 之间的差值、判断一个集合中是否包含某一个值，这些都有对应的 API。
>
> 对于默认中没有的，也就是我们可以自定义的，可以使用 `assert.Condition(t, func() bool)` 自定义。具体是：
>
> ```go
> 	assert.Condition(t, func() bool {
> 		// ...
> 	}, "error 信息")
> ```

## 总结

简单的断言就使用 `assert`，如果出错了，程序还会继续执行下去。如果是特别硬性的断言，如果不满足条件会引发很大的问题，就要使用 `require`。这种出错的话，测试程序就会立马停止。

设定断言时，首先考虑库中已有的常用的 API：

```go
assert.Equal(t, expected, actual)      	// 值相等比较
assert.True(t, condition)              	// 布尔条件为真
assert.Nil(t, object)                  	// 对象为 nil
assert.Error(t, err)                   	// 检查是否有错误
assert.NoError(t, err)                 	// 检查无错误
assert.Contains(t, stringOrSlice, item)	// 检查包含关系
```

或者是自定义：

```go
assert.Condition(t, func() bool)
```











