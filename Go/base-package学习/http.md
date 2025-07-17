# http

## Handle 部分辨析

最近在四个概念上总是分不清楚，因为长得很像：

- `Handle`
- `HandleFunc`
- `Handler`
- `HandlerFunc`

一方面是因为长得很像，另一方面是因为我看各种 demo 中，这几个东西完全就是混用。就像是之前学的，如果要向一个写入流 `w` 中写入数据的话，可以使用：

- `w.Write([]byte("Hello World"))`
- `fmt.Fprintf(w, "Hello World")`

或者是打开文件的时候，一些 demo 中是 `os.Open()`，一些 demo 中是 `os.OpenFile()`。这种不同的写法换着来，总让我的初学经历感觉很疑惑。

实际上都是一样的效果，但是我就看 AI 做的各种 demo，以为是不同的效果，还以为自己要学的东西有很多。

实际上这部分也是这样的，比如说我们要做一个路径和函数的绑定，实际上 `Handle` 和 `HandleFunc` 这两种方法都可以，只不过是一个做的封装多一点，一个做的封装少一点。

### 前言

总体这几种东西都是什么，先通过一个表格来看一下：

| 概念          | 类型        | 解析                                                         |
| ------------- | ----------- | ------------------------------------------------------------ |
| `Handle`      | `func`      | `func Handle(pattern string, handler Handler)` 将处理对象 `handler` 绑定到 `pattern` 上 |
| `HandleFunc`  | `func`      | `func HandleFunc(pattern string, handler func(ResponseWriter, *Request))` 直接将函数 `handler` 绑定到 `pattern` 上 |
| `Handler`     | `interface` | `type Handler interface{}` 是一个接口，其中包含一个函数 `ServeHTTP(w, r*)` |
| `HandlerFunc` | `type`      | `type HandlerFunc func(ResponseWriter, *Request)` 以一个 `func` 为基础去创立一个新的对象。 |

### `Handler`

官方实现中的定义：

```go
type Handler interface {
	ServeHTTP(ResponseWriter, *Request)
}
```

也就是说这是一个接口，接口中只有一个方法，就是 `ServeHTTP()` 方法。方法的类型也是比较常见的 `(w http.ResponseWriter, r *http.Request)`。方法的实现也并不是什么特别复杂的，就是根据传入的 `Request` 去创建一个对于这个请求的 `Response`。

例如，下面就是一个比较普通的实现：

```go
func ServeHTTP(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("Hello, world!"))
}
```

所以说到 `Handler` 类型，实际上就是任何类型，只要这个类型中实现了 `ServeHTTP()` 方法就可以。

> 一开始这里让我比较疑惑的是，一些案例中，直接让一个 `func()` 重新指定为结构体，之后在这个新的结构体（`func`）中再加入函数，这样就是一个 `func() -> func()`。语言还是太灵活了，这是我从未设想过的实现。

### `HandlerFunc`

官方实现中的定义：

```go
type HandlerFunc func(ResponseWriter, *Request)

// ServeHTTP calls f(w, r).
func (f HandlerFunc) ServeHTTP(w ResponseWriter, r *Request) {
	f(w, r)
}
```

这就是上面说的，以单纯的一个函数为基础，构建出一种新的类型，叫做 `HandlerFunc`。

所以在使用中，我们可以直接把一个 `func(ResponseWriter, *Request)` 直接转换为 `HandlerFunc` 类型。不过，转换之后的类型，相比于之前单纯的 `func()`，多了一个“类型中的方法字段”，就是 `ServeHTTP()` 方法字段。

而且其中的 `ServeHTTP()` 方法实现的方法也特别朴素，就是直接调用原本定义时使用的那个函数本身。

同时可以将这种方法理解为一种创建 `Handler` 的方式。因为 `Handler` 是一个接口，任何实现了 `ServeHTTP()` 方法的类型都是 `Handler` 类型。只不过，如果直接使用 `Handler` 来创建类型，原本我们可以指定任何类型 + 实现 `ServeHTTP()` 方法；现在我们可以在一个方法中，直接将一种 `func()` 类型转换为 `Handler` 类型。

### `Handle()`

`Handle` 的作用是绑定。就是将一个处理的函数和一个对应的路径进行绑定。

```go
func Handle(pattern string, handler Handler) {
	if use121 {
		DefaultServeMux.mux121.handle(pattern, handler)
	} else {
		DefaultServeMux.register(pattern, handler)
	}
}
```

其中的 `use121` 可能是一个 `bool`，表示现在是不是使用的 `go 1.21` 版本。推测是 `go 1.21` 中对这部分有特殊的处理。不过那都不重要了。

可以看到实际上 `Handle(pattern string, handler Handler)` 的执行原理还是 `DefaultServeMux.register(pattern, handler)`，就是在默认的路由上，将 `pattern` 和 `handler` 绑定。其中的 `handler` 就是我们上面提到的 `Handler` 类型。

所以在实际使用的时候，我们就要提前创建好 `Handler` 类型的实例。之后直接在 `Handle()` 方法中传入。

### `HandleFunc()`

这也是一个函数。它的定义如下：

```go
func HandleFunc(pattern string, handler func(ResponseWriter, *Request)) {
	if use121 {
		DefaultServeMux.mux121.handleFunc(pattern, handler)
	} else {
		DefaultServeMux.register(pattern, HandlerFunc(handler))
	}
}
```

我们也先不管其中的 `use121`，此时可以将函数简化为：

```go
func HandleFunc(pattern string, handler func(ResponseWriter, *Request)) {
	DefaultServeMux.register(pattern, HandlerFunc(handler))
}
```

这个函数的传入类型和上面的 `Handle()` 是不一样的。这里传入的类型是一个 `func(ResponseWriter, *Request)`。

其实可以理解为：`HandleFunc()` 就是将 `Handle()` 和 `HandlerFunc` 的功能做了一个缝合。你 `Handle()` 不是后面需要一个 `Handler` 类型的参数吗，那我就直接使用 `HandlerFunc` 将一个普通的 `func(ResponseWriter, *Request)` 转换为 `Handler` 类型，之后再调用 `Handle()` 方法进行处理。

结合一下，整个过程中需要的参数就是一个 `func(w, r*)`，那么我就整合一下，做出一个函数：

```go
func HandleFunc(string, func(ResponseWriter, *Request)) { ... }
```

所以这个函数就是简化了使用，之后在调用的时候，可以直接调用 `HandleFunc(string, func())`，其中直接指定，哪一个路径，绑定的是哪一个函数。

### 总结

总结就是，之后我们使用的时候，首先推荐的一种写法，就是直接使用简化的 `HandleFunc()` 函数：

```go
func main() {
    // ...
    http.HandleFunc("/hello", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("Hello, World"))
    })
    // ...
}
```

这样就直接绑定好了。

这是一种简单的处理方式。如果是复杂的需求，比如说我们要编写一些中间件函数，这时候就可以使用 `HandlerFunc` 实现中间件：

```go 
// 中间件：记录请求耗时
func logTime(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        fmt.Printf("Request to %s took %v\n", r.URL.Path, time.Since(start))
    })
}
 
func main() {
    // 核心处理函数
    handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello with Middleware!")
    })
 
    // 使用中间件包装 Handler
    http.Handle("/middleware", logTime(handler))
 
    http.ListenAndServe(":8080", nil)
}
```

这个过程中，首先使用 `HandlerFunc()` 创建了一个 `Handler` 类型的实例，之后可以直接使用：

```go
http.Handle("/middleware", handler)
```

来绑定，但是没有这么做，我们选择了另外一种方法，将一个 `Handler` 修改修改之后，做成另一个 `Handler`。创建新的 `Handler` 使用的还是 `HandlerFunc()` 类型转换，其中提供的 `func()` 的组成部分是：“原本的 `ServeHTTP()`” + “其他处理逻辑”。





















