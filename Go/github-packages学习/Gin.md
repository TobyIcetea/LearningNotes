# Gin

[TOC]

## 安装

```go
go get -u github.com/gin-gonic/gin
```

## Hello World

```go
package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	// 1. 创建路由
	r := gin.Default()

	// 2. 绑定路由规则，执行的函数
	r.GET("/", func(c *gin.Context) {
		c.String(http.StatusOK, "hello world!")
	})

	// 3. 监听端口，默认在 8080
	// Run("里面不指定的话，默认端口号为 8080")
	r.Run(":8080")
}
```

另一个 shell 中：

```go
[root@JiGeX fastgo]# curl localhost:8080
hello world!
```

## 路由使用

### 基本使用

路由就是，给我们的服务器，提供一个转发请求到指定函数的功能。

具体实现就是，给定一个访问的路径，再给一个处理这个路径的对应的函数。

路由的时候是要区分请求的，比如说我们现在先考虑 `GET`、`POST`、`PUT`、`DELETE` 这几种请求。这都是 `RESTful API` 中不同种类的请求。

golang 中建立请求的时候，可以直接使用 `router := gin.Default()`，就可以建立一个默认的路由器。

之后对这个 `router` 直接使用 `router.GET()`、`router.POST()` 之类的方法，就可以设置这个路由器是如何转发请求的。

比如说，我们可以设置 `router.GET("/get", func(c *gin.Context) {...})` 和 `router.POST("/post", func(c *gin.Context) {...})` 来对发送到 `/get` 和 `/post` 的请求做不同的处理。

下面是一个简单的 demo，这里我对 `/get` 和 `/post` 的处理就是简单的打印出来，这是一个什么类型的请求。

```go
func main() {
	// 设置路由
	router := gin.Default()

	// 第一个参数是：路径
	// 第二个参数是：具体操作 func(c *gin.Context)
	router.GET("/Get", func(c *gin.Context) {
		c.String(http.StatusOK, "GET 方法")
	})

	router.POST("/Post", func(c *gin.Context) {
		c.String(http.StatusOK, "POST 方法")
	})

	router.PUT("/Put", func(c *gin.Context) {
		c.String(http.StatusOK, "PUT 方法")
	})

	router.DELETE("/Delete", func(c *gin.Context) {
		c.String(http.StatusOK, "DELETE 方法")
	})

	// 默认启动的是 8080 端口
	router.Run()
}
```

然后是访问的时候，这里也有说法的。比如说我们就使用 Linux 中的 `curl` 命令来进行访问：

```go
[root@JiGeX fastgo]# curl -X GET localhost:8080/Get
GET 方法

[root@JiGeX fastgo]# curl -X POST localhost:8080/Post
POST 方法

[root@JiGeX fastgo]# curl -X PUT localhost:8080/Put
PUT 方法

[root@JiGeX fastgo]# curl -X DELETE localhost:8080/Delete
DELETE 方法
```

其中的 `-X` 选项等于 `--request`，作用是指定与 HTTP 服务器通信时使用的自定义请求方法。

其实第一个访问 `/Get` 的 `curl` 命令中也可以不加 `-X` 选项，因为 `-X` 选项默认就是 `GET` 类型的。

后面我们对 `/Post` 之类的路径也是设置的是 `POST` 的路由方法，所以访问的时候必须使用 `POST` 类型的访问方法。这里就给我提了一个醒：设置的路由类型和访问的时候的请求类型必须是相同的。

其中还有几个其他的理解：

- web 中无非就是两个东西，一个是 `request`，一个是 `response`。那么 gin 中的 `Context` 到底是个啥意思呢？目前阶段我就将它理解为一个结构体，反正就是：一个 `request` 肯定是对应一个 `response`，同时呢，每一次请求的时候，也会创建一个对应的 `context`，所有的 `request` 和 `response` 都在这个 `context` 中进行。所以可以暂时将 `context` 结构体的结构理解为：

    ```go
    |---Context
    |-------Requst
    |-------Response
    ```

- `context` 中写 `Response` 的写法：直接使用 `c.String()`、`c.JSON()` 这样的数据结构。

    ```go
    c.String() - 表示 Response 中是一个字符串
    c.JSON()   - 表示 Response 中是一个 JSON 结构体
    ```

### 基本使用 pro

首先先看几个新的概念：

#### 【静态路由与动态路由】

- 静态路由：例如 `/users`，这种路由会精确匹配 `/users` 的请求，用于请求固定资源。
- 动态路由：或者说叫做参数化路由。例如 `/users/:id`，此时的 `id` 是一个动态参数，可以匹配任意的非空字符段。

动态路由在 `:` 之后紧跟一个参数名（如 `:id`），Gin 会将 URL 路径中的对因为只解析为该参数的值。比如说：

- 访问 `/users/123`，此时 `id` 会被赋值为 `"123"`。
- 访问 `/users/alice`，此时 `id` 会被赋值为 `"alice"`。

那么动态路由如何获取参数值呢？看如下的代码：

```go
router.GET("/users/:id", func(c *gin.Context) {
    id := c.Param("id") // 获取路径中的 id 参数
    // 例如访问 /users/123 → id = "123"
    c.String(200, "User ID: %s", id)
})
```

其中，通过 `c.Param("id")` 获取到了我们原本路由中定义的 `id` 字段。

不过，静态路由的优先级肯定是高于动态路由的。比如说我么同时设置了 `/users/:id` 和 `/users/new` 这两个路由，那么请求过来之后，会将请求转发到 `/users/new` 这个路由上，而不是将 `new` 解析为 `id` 字段的值。

-----

#### 【`c.JSON` 返回类型】

前面说 `c.String()` 是返回一个 `string` 类型的 `Response`。那么 `c.JSON()` 就是返回一个 `JSON` 类型的 `Response`。

`c.JSON()` 的定义是：`func (c *Context) JSON(code int, obj any) { ... }`。

所以说函数的第一个字段是填写返回的 `http` 代码，比如说 `200` 表示 `http.StatusOK`；第二个字段就是任何类型的数据，之后 go 会将它转换为 `JSON` 类型并返回。

所以第二个字段，我们比较倾向于填写两种值，一种是直接填写我们的结构体，比如说 `c.JSON(200, user)`；

或者是 `map[string]any` 类型，这也是 `JSON` 最直白的表达方式。

然后这里 gin 就直接给这种类型重新起了个名，就叫 `gin.H`（`type H map[string]any`），所以有的时候在返回值中写 `c.JSON(200, gin.H{"name": "alice"})`，效果其实和写 `c.JSON(200, map[string]any{"name": "alice"})` 的效果是一样的。

总结来说，我们使用 `c.JSON()` 来返回数据，主要有两种使用场景：

- 第一种，返回我们已经定义好的 golang 结构体：

    ```go
    type User struct {
        Name string `json:"name"`
        Age  int    `json:"age"`
    }
    user := User{Name: "Bob", Age: 25}
    c.JSON(200, user)
    ```

- 第二种，使用 `gin.H` 自己构建返回的 `JSON` 数据：

    ```go
    c.JSON(200, gin.H{
        "status": "ok",
        "data":   someData,
    })
    ```

---

#### 【`c.ShouldBindJSON` 方法】

如果说前面的 `c.JSON()` 是去组转一个新的 `Response`，那么这里的 `c.ShouldBindJSON()` 就是去处理 `Request` 的。

我们在本地处理请求的时候，对外暴露了路由的接口，然后我们假设（希望）用户发过来的请求是符合某一种结构体的结构的。发过来之后，我们再使用用户发送的数据被序列化的数据，填充一个空的结构体。这个空的结构体就是我们希望的 `Request` 的形式，之后我们对 `Request` 的处理也是在这个 `Request` 之上的。

例如，在代码中，我们先定义出自己期待客户端发过来的请求的结构：

```go
// 定义接收 JSON 的结构体（注意字段首字母大写）
type LoginRequest struct {
    Username string `json:"username"`  // 使用标签映射 JSON 字段名
    Password string `json:"password"`
}
```

之后，我们就可以定义 POST 请求的路由功能：

```go
router.POST("/login", func(c *gin.Context) {
    // 声明一个结构体变量
    var req LoginRequest

    // 绑定 JSON 到结构体
    if err := c.ShouldBindJSON(&req); err != nil {
        // 如果绑定失败，返回错误信息
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    // 成功时打印数据
    c.JSON(200, gin.H{
        "username": req.Username,
        "password": req.Password,
    })
})
```

其中的核心思想，就是将用户请求中的序列化过的数据，填充到 golang 实际的 `Request` 结构体中。

---

#### 基本使用 demo

```go
type User struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

func main() {
	// 创建 Gin 实例
	router := gin.Default()

	// 模拟内存数据库
	users := make(map[string]User)

	// GET 请求示例 - 获取资源
	router.GET("/users/:id", func(c *gin.Context) {
		id := c.Param("id")
		if user, exists := users[id]; exists {
			c.JSON(200, user)
			return
		}
		c.JSON(404, gin.H{"message": "用户不存在"})
	})

	// POST 请求示例 - 创建资源
	router.POST("/users", func(c *gin.Context) {
		var newUser User
		if err := c.ShouldBindJSON(&newUser); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		// 模拟生成ID
		newUser.ID = "123"
		users[newUser.ID] = newUser
		c.JSON(201, newUser)
	})

	// PUT 请求示例 - 更新资源
	router.PUT("/users/:id", func(c *gin.Context) {
		id := c.Param("id")
		var updateUser User
		if err := c.ShouldBindJSON(&updateUser); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		if _, exists := users[id]; exists {
			updateUser.ID = id
			users[id] = updateUser
			c.JSON(200, updateUser)
			return
		}
		c.JSON(404, gin.H{"message": "用户不存在"})
	})

	// DELETE 请求示例 - 删除资源
	router.DELETE("/users/:id", func(c *gin.Context) {
		id := c.Param("id")
		if _, exists := users[id]; exists {
			delete(users, id)
			c.JSON(204, nil)
			return
		}
		c.JSON(404, gin.H{"message": "用户不存在"})
	})

	// 启动服务
	router.Run(":8080")
}
```

之后请求的时候，按照如下的流程：

```go
[root@JiGeX fastgo]# curl -X POST http://localhost:8080/users \
-H "Content-Type: application/json" \
-d '{"name":"张三","email":"zhangsan@example.com"}'
输出：{"id":"123","name":"张三","email":"zhangsan@example.com"}

[root@JiGeX fastgo]# curl http://localhost:8080/users/123
输出：{"id":"123","name":"张三","email":"zhangsan@example.com"}

[root@JiGeX fastgo]# curl -X PUT http://localhost:8080/users/123 \
-H "Content-Type: application/json" \
-d '{"name":"李四","email":"lisi@example.com"}'
输出：{"id":"123","name":"李四","email":"lisi@example.com"}

[root@JiGeX fastgo]# curl -X DELETE http://localhost:8080/users/123
输出：（空）
```

这个案例中使用到的 `http` 状态码如下：

| 状态码数字 | http 代码               | 含义                                                         |
| ---------- | ----------------------- | ------------------------------------------------------------ |
| 200        | `http.StatusOK`         | 请求成功处理，服务器返回所请求的资源。                       |
| 201        | `http.StatusCreated`    | 资源创建成功。通常用于 `POST` 请求之后，新资源已创建。       |
| 204        | `http.StatusNoContent`  | 请求成功处理，但无返回内容。适用于 `DELETE` 请求或不需要返回数据的操作。 |
| 400        | `http.StatusBadRequest` | 客户端请求有误，服务器无法处理（如参数错误、数据格式错误）。 |
| 404        | `http.StatusNotFound`   | 请求的资源不存在或路径错误。                                 |

### 路由分组

比如说我们现在要设置几个不同的分组：

- `"/v1/hello"`
- `"/v1/world"`
- `"/v2/hello"`
- `"/v2/world"`

我们当然可以直接通过 `router.GET("/v1/hello", func)`、`router.GET("/v1/world", func)` 这样一个一个设置好所有的路由。但是这样就会让分组变得不是很明确，所有的路由平铺在代码中，没有体现出一个分类的层级关系。

这时候就想到，可以把 `/v1` 当做一个路由的分组（或者说公共前缀），把 `/v2` 作为一个路由的分组，然后再分别在这两个前缀下去设置他们的功能，这时候是不是路由层级关系就更清晰呢？

```go
func sayHello(c *gin.Context) {
	c.String(200, "Hello\n")
}

func sayWorld(c *gin.Context) {
	c.String(200, "World\n")
}

func main() {
	router := gin.Default()

	v1 := router.Group("/v1")
	{
		v1.GET("/hello", sayHello)
		v1.GET("/world", sayWorld)
	}

	v2 := router.Group("/v2")
	{
		v2.GET("/hello", sayHello)
		v2.GET("/world", sayWorld)
	}

	router.Run(":8080")
}
```

之后访问的时候：

```go
[root@JiGeX fastgo]# curl localhost:8080/v1/hello
Hello

[root@JiGeX fastgo]# curl localhost:8080/v1/world
World

[root@JiGeX fastgo]# curl localhost:8080/v2/hello
Hello

[root@JiGeX fastgo]# curl localhost:8080/v2/world
World
```

总结：路由分组实际上就是设置**【公共前缀】**！

> 代码中，在一块儿代码中突然出现一个大括号，包裹住了一块代码。一开始我也比较疑惑，因为没有发现任何的 if 啊、for 啊之类的关键词，也没有在定义什么函数之类的，为啥会突然出现这样一个大括号。
>
> 还以为是什么高级的语法，实际上就是为了观察的时候更方便。把几行代码用一个大括号框起来，是为了展现出他们的逻辑关系，一眼就能看出来他们是一体的，在一块儿处理一个事情。
>
> 当然这种语法也不仅仅光是为了好看，还有一些其他的规范，比如说代码块中定义的参数，代码外面是看不到的。但是这就不是很常用了。

## 获取参数

### 路径参数

在 gin 框架中，路径参数的获取有两种方式：

- `:` 表示捕获单个参数
- `*` 表示捕获多个参数，或者说所有的剩余路径

比如说对于如下的代码：

```go
func main() {
	router := gin.Default()

	router.GET("/user/:name", func(c *gin.Context) {
		name := c.Param("name")
		c.String(http.StatusOK, "Hello %s", name)
	})

	router.GET("/user/:name/*action", func(c *gin.Context) {
		name := c.Param("name")
		action := c.Param("action")
		message := name + "is" + action
		c.String(http.StatusOK, message)
	})

	router.Run(":8080")
}
```

此时我们就定义了 `/user/:name` 和 `/user/:name/*action` 这两个路径。我们访问的时候，不同的访问格式对应的路由处理方式如下：

| URL                      | 触发路由              | 关键参数                   |
| ------------------------ | --------------------- | -------------------------- |
| `/user/Alice`            | `/user/:name`         | `name = "Alice"`           |
| `/user/Bob`              | `/user/:name`         | `name = "Bob"`             |
| `/user/Charlie/`         | `/user/:name/*action` | `action = "/"`             |
| `/user/Delta/run`        | `/user/:name/*action` | `action = "/run"`          |
| `/user/Eve/do/something` | `/user/:name/*action` | `action = "/do/something"` |

从中可以得出几个结论：

- `*` 参数在一个路径中只能出现一个，并且只能出现在最后的位置。
- `*` 参数匹配的内容是从 `/` 开始的所有后续内容，也包含 `/` 符号。
- `/user/Bob` 和 `/user/Bob/` 是两个不同的路由。所以在写 `url` 的时候，要注意 `/` 符号，不能多写。

### GET 方法

最经典的 GET 方法获取参数的方式应该是，假如对于请求的 URL：

```go
/user?key1=value1&key2=value2
```

之后我们可以从 URL 中获取到参数：`key1 -> value1`、`key2 -> value2`。

对于请求的 URL，在 golang 代码中获取的时候，可以使用两个 API：

- `c.Query("name")`，这样可以从请求的 URL 中获取 `name` 字段的值。
- `c.DefaultQuery("name", "Bob")`，这样也可以从请求的 URL 中获取 `name` 字段的值，同时如果 `name` 字段没有被设置的话，会使用默认值 `"Bob"`。

例如，对于如下的代码：

```go
func main() {
	router := gin.Default()

	router.GET("/user", func(c *gin.Context) {
		// 指定默认值
		name := c.DefaultQuery("name", "normal")
		// 获取具体值
		age := c.Query("age")
		c.String(http.StatusOK, fmt.Sprintf("hello %s, your age is %s", name, age))
	})

	router.Run(":8080")
}
```

测试：

```go
// 同时使用 name 和 age
[root@JiGeX fastgo]# curl "http://localhost:8080/user?name=John&age=30"
hello John, your age is 30

// 只设置了 age，name 使用默认值
[root@JiGeX fastgo]# curl "http://localhost:8080/user?age=30"
hello normal, your age is 30

// 只设置了 name，age 没有默认值，就是空字符串
[root@JiGeX fastgo]# curl "http://localhost:8080/user?name=John"
hello John, your age is

// name 使用中文
[root@JiGeX fastgo]# curl "http://localhost:8080/user?name=张三&age=30"
hello 张三, your age is 30

// name 使用编码后的中文
[root@JiGeX fastgo]# curl "http://localhost:8080/user?name=%E5%BC%A0%E4%B8%89&age=30"
hello 张三, your age is 30[root@JiGeX fastgo]#
```

### POST 方法

GET 是一个查询的方法，POST 方法现在看来更像是一种“提交”的意思。主要的用处有以下几个：

- 提交表单
- 提交 JSON 块
- 提交文件

其中最常用的肯定还是提交表单了，目前初学阶段，还是将主要注意的方向放在“提交表单”上。

这里还要用到一个知识点：在 Linux 中使用 `curl` 命令提交 POST 请求时，如何指定请求体：

```bash
curl -X POST -d "username=alice" -d "password=secret"
```

在其中可以看到，做的方法就是，首先通过 `-X POST` 指定请求是 POST 请求，之后再通过多个 `-d` 指定表单中的每一个数据项，`curl` 会自动将这些表单的数据项合并。或者是也可以使用 `-d "username=alice&password=secret"` 来指定，不过我还是觉得分开写结构更清晰。

获取方法方面，类似于 GET 方法使用 `Query()` 和 `DefaultQuery()` 来获取参数，POST 请求是通过 `PostForm()` 和 `DefaultPostForm()` 方法来获取参数的。其中 `DefaultPostForm()` 就是在 `PostForm()` 的基础上设置了默认值。

且一个路由中可以同时设置对 GET 请求和处理方法和对 POST 请求的处理方法，示例代码如下：

```go
func main() {
	router := gin.Default()

	router.POST("/form", func(c *gin.Context) {
		// 设置默认值
		types := c.DefaultPostForm("type", "post")
		username := c.PostForm("username")
		password := c.PostForm("password")

		// 还可以使用 Query 实现 Get + Post 的结合
		name := c.Query("name")
		c.JSON(200, gin.H{
			"username": username,
			"password": password,
			"type":     types,
			"name":     name,
		})
	})

	router.Run(":8080")
}

```

访问时：

```go
// 不传递 type，type 就使用默认值
[root@JiGeX fastgo]# curl -X POST "http://localhost:8080/form" -d "username=alice" -d "password=secret"
{"name":"","password":"secret","type":"post","username":"alice"}

// 通过 post 设置 username、password、type 等字段，通过 get 设置 name 字段
[root@JiGeX fastgo]# curl -X POST "http://localhost:8080/form?name=john" -d "username=bob" -d "password=123456" -d "type=user"
{"name":"john","password":"123456","type":"user","username":"bob"}

// 显式将 type 字段设置为空，其他两项仍然是空
[root@JiGeX fastgo]# curl -X POST "http://localhost:8080/form?name=empty_test" -d "type="
{"name":"empty_test","password":"","type":"","username":""}

// 不设置所有 post 字段，最后 type 使用默认值，psssword 和 username 字段就是空字符串
[root@JiGeX fastgo]# curl -X POST "http://localhost:8080/form?name=url_only&type=from_url"
{"name":"url_only","password":"","type":"post","username":""}
```

### 文件获取

文件获取有两个 API，分别是获取单个文件的和获取多个文件的。我感觉这里不是特别的常用，学的时候就先只学获取单个文件的。

在传输请求的时候，还是使用 `curl` 命令，传输的还是 POST 请求，但是这次 POST 请求就不能使用 `-d` 来写数据体了，而是得写 `-F`。

- `-d`：只能传输简单的键值对。
- `-F`：除了可以传输简单的键值对之外，还可以传输文件。

可以说 `-F` 的功能可以包含 `-d` 的功能，传输键值对的时候也可以使用 `-F`。但是使用 `-F` 也有不好的地方，比如就传输键值对这个方面，`-F` 解析花的时间比 `-d` 长一点。同时在一些老旧的 HTTP 协议中，可能并不支持 `-F`。

同时，在指定了 `-F` 选项之后，后面的字段中，如果要传输的是一个文件，就要加上 `@+文件路径` 表示上传的文件。例如：

```bash
curl -X POST "localhost:8080" -F "file=@document.pdf"
```

在接收的时候，普通的 POST 请求，接收的时候使用的是 `c.PostForm(string)` 方法。但是如果是文件的话，就要使用 `c.FormFile(string)` 方法。这个方法会返回保存的文件的指针和错误：`(*multipart.FileHeader, error)`。之后可以再通过 `c.SaveUploadedFile(file, dest string)` 来指定将文件保存到哪个位置。

具体代码如下：

```go
func main() {
	router := gin.Default()

	router.POST("/upload", func(c *gin.Context) {
		// 单个文件上传
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		// 保存文件
		filename := filepath.Base(file.Filename)
		if err := c.SaveUploadedFile(file, "uploads/"+filename); err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}

		c.JSON(200, gin.H{
			"filename": filename,
			"size":     file.Size,
			"mime":     file.Header.Get("Content-Type"),
		})
	})

	router.Run(":8080")
}
```

之后上传文件的时候，可以使用如下的命令：

```go
[root@JiGeX gin-demo]# curl -X POST "http://localhost:8080/upload" -F "file=@main.go"
{"filename":"main.go","mime":"application/octet-stream","size":639}

[root@JiGeX gin-demo]# curl -X POST "http://localhost:8080/upload" -F "file=@gin-demo"
{"filename":"gin-demo","mime":"application/octet-stream","size":20547197}
```

文件会存放到项目的 `uploads/` 文件夹中。

## 接收处理

### ShouldBindJSON

接收处理，就是接收到数据之后，如何进行处理。其中最常用的就是 `ShouldBindJSON` 方法了。

在做 `ShouldBindJSON()` 之前，首先要定义好，我们是想将用户发来的请求填充到哪一个结构体中？也就是说，要先创建好对应的结构体。之后就可以处理 POST 请求，将用户发来的数据，填充到我们定义好的结构体中。然后再处理，如果填充成功了，应该返回一个什么信息，如果填充失败了，应该返回一个什么信息。

```go
// 定义接收数据的结构体
type Book struct {
	Title  string  `json:"title"`
	Author string  `json:"author"`
	Price  float64 `json:"price"`
}

func main() {
	router := gin.Default()

	// 处理 POST 请求的路由
	router.POST("/books", func(c *gin.Context) {
		var newBook Book

		// 使用 ShouldBindJSON 绑定数据
		if err := c.ShouldBindJSON(&newBook); err != nil {
			// 当 JSON 格式错误时的处理
			c.JSON(http.StatusBadRequest, gin.H{
				"error":   true,
				"message": "无效的 JSON 数据",
			})
			return
		}

		// 如果绑定成功，可以直接使用结构体数据
		c.JSON(http.StatusOK, gin.H{
			"received_book": newBook,
		})
	})

	router.Run(":8080")
}
```

这里要求用户发来的数据是一个 `json` 数据，其中包含的数据类型有：

```go
	Title  string  `json:"title"`
	Author string  `json:"author"`
	Price  float64 `json:"price"`
```

同时还有一个要求，就是在发送的消息的请求头中，必须要保证 `Content-Type: application/json`，这样才能完成绑定。

用户可以这样发送请求：

```go
// 正常填充所有数据
[root@JiGeX gin-demo]# curl -X POST "http://localhost:8080/books" -H "Content-Type: application/json" -d '{"title": "Golang 基础教程", "author": "老张", "price": 49.99}'
{"received_book":{"title":"Golang 基础教程","author":"老张","price":49.99}}

// 原本定义为 float64 类型的 price 字段，填充非数字时，绑定会失败
[root@JiGeX gin-demo]# curl -X POST "http://localhost:8080/books" -H "Content-Type: application/json" -d '{"title": "Golang 基础教程", "author": "老张", "price": 六六六}'
{"error":true,"message":"无效的 JSON 数据"}

// author 字段缺失，在没有设置 Validation 的情况下，会将这个字段设为空值
[root@JiGeX gin-demo]# curl -X POST "http://localhost:8080/books" -H "Content-Type: application/json" -d '{"title": "Golang 基础教程", "price": 49.99}'
{"received_book":{"title":"Golang 基础教程","author":"","price":49.99}}
```

### Validation

Validation 就是上面的 `ShouldBindJSON` 绑定的时候，有的时候会绑定失败，或者是用户提交的表单内容不符合我们的要求。

这时候我们就要对表单内容做验证，看表单中有没有不符合要求的内容。并且根据用户出错的地方，为啥不符合要求，给用户返回不同的提示。

现在就先使用简单的 `validator` 库来做规则的验证。使用的方式就是通过反射标签的方式，写上 `binding:"规则"`。常见的规则如下：

- `required`：规则必填。
- `email`：必须是邮箱格式。
- `gte=18`：数字必须大于等于 18。
- `min=6`：最小长度 6。

示例代码如下：

```go
// 定义请求结构体，并添加验证标签
type RegisterRequest struct {
	Username string `json:"username" binding:"required,min=3"` // 必填，至少 3 个字符
	Email    string `json:"email" binding:"required,email"`    // 必填，必须是邮箱格式
	Age      int    `json:"age" binding:"gte=18"`              // 必须大于等于 18 岁
}

func main() {
	router := gin.Default()

	router.POST("/register", func(c *gin.Context) {
		var req RegisterRequest

		// 绑定 JSON 数据到结构体，并自动验证
		if err := c.ShouldBindJSON(&req); err != nil {
			// 处理验证错误（这里将错误转为更友好的格式返回）
			c.JSON(http.StatusBadRequest, gin.H{
				"error": getValidationError(err),
			})
			return
		}

		// 验证通过后的处理逻辑
		c.JSON(http.StatusOK, gin.H{
			"message": "注册成功",
			"data":    req,
		})
	})

	router.Run(":8080")
}

// 处理验证错误，将其转换为更易懂的格式
func getValidationError(err error) map[string]string {
	errors := make(map[string]string)

	// 类型断言，判断是否是验证错误
	if validationErrors, ok := err.(validator.ValidationErrors); ok {
		// 遍历每个错误
		for _, fieldError := range validationErrors {
			// 根据不同的错误类型生成不同消息
			switch fieldError.Tag() {
			case "required":
				errors[fieldError.Field()] = "此项为必填项"
			case "email":
				errors[fieldError.Field()] = "请输入正确的邮箱格式"
			case "gte":
				errors[fieldError.Field()] = "输入值必须大于等于 18"
			case "min":
				errors[fieldError.Field()] = "输入长度不足"
			}
		}
	}

	return errors
}
```

其中的一些理解：

`ShouldBindJSON()` 这个方法的返回值类型是一个 error，但是 `error` 是一个接口类型。任何实现了 `Error()` 方法的类型都可以成为 error 类型。所以现在我觉得，如果在前面的 `struct` 中我们在字段的反射描述中设置了 `binding` 的验证，后面的 `ShouldBindJSON()` 的返回值类型是一个实现了 `Error()` 的切片，具体是 `[]FieldError` 类型。其中，`FieldError` 实现了 `Error()` 方法，所以它也是一种 error 类型。

那么后面看到这行代码：`err.(validator.ValidationErrors)` 的时候就不会奇怪了。第一看的时候，我以为是将一个 `error` 转换为一个 `[]error`，感觉这种写法很奇怪，但是这本身就是接口类型，只需要切片类型和切片中的元素类型都实现了 `Error()` 方法，这种情况是可能会出现的。

经过转换后的 `[]FiledError` 类型的 `validationErrors`，其中包含的元素的数量，取决于我们的表单中出现了多少个错误。

假如说我们的表单中有一个错误，其中就有一个元素：

```go
Key: 'RegisterRequest.Username' Error:Field validation for 'Username' failed on the 'min' tag
```

假如说我们的表单中有两个错误，其中就有两个元素：

```go
Key: 'RegisterRequest.Username' Error:Field validation for 'Username' failed on the 'min' tag
Key: 'RegisterRequest.Email' Error:Field validation for 'Email' failed on the 'email' tag
```

其中的 `FieldError` 类型的具体结构解析如下：

```go
validator.ValidationErrors（具体类型） → 实现了 error 接口
    │
    └── 本质是 []FieldError（结构体切片）
         │
         └── 每个 FieldError 包含：
              - 字段名（Field()）
              - 错误类型（Tag()）
              - 错误详情（Error()）
```

之后我们的 `getValidationError` 函数，就是根据 `FieldError` 元素的 `Tag()` 字段，确定出这个请求是没有满足哪个要求，然后重新使用 `Field()` 字段组装一个更加易读的形式，返回给用户。

最后，我们来测试一下这个服务器：

```go
// 所有的信息都正确填写，直接返回注册成功的信息
[root@JiGeX gin-demo]# curl -X POST "http://localhost:8080/register" -H "Content-Type: application/json" -d '{"username": "John", "email": "john@163.com", "age": 20}'
{"data":{"username":"John","email":"john@163.com","age":20},"message":"注册成功"}

// username 字段，使用两个字符的长度，不符合要求，返回错误信息
[root@JiGeX gin-demo]# curl -X POST "http://localhost:8080/register" -H "Content-Type: application/json" -d '{"username": "Jo", "email": "john@163.com", "age": 20}'
{"error":{"Username":"输入长度不足"}}

// username 和 email 字段都不符合要求，返回的 JSON 中包含两个错误信息
[root@JiGeX gin-demo]# curl -X POST "http://localhost:8080/register" -H "Content-Type: application/json" -d '{"username": "Jo", "email": "@@@@@", "age": 20}'
{"error":{"Email":"请输入正确的邮箱格式","Username":"输入长度不足"}}
```

## 会话控制

### Cookie

Cookie 就是一个浏览器的键值对。在浏览器中设置好“哪一个域名下的哪一个路由”中含有一个什么样的键值对，再设置好一些过期时间之类的数据，就是 cookie 了。

比如说我们是通过 token 来完成验证的，那么我们可以在浏览器中设置好 token 的 cookie，过期时间一小时。那么接下来一小时内，都不用担心 token 过期了。

```go
func main() {
	router := gin.Default()

	router.GET("/set", func(c *gin.Context) {
		c.SetCookie("user", // cookie 的名称
			"john",      // cookie 的值
			3600,        // 过期时间
			"/",         // 生效路由
			"localhost", // 作用域名
			false,       // 是否允许 HTTPS
			true,        // 是否禁止 JS（是否 httpOnly）
		)
		c.String(200, "Cookie 已设置")
	})

	router.GET("/get", func(c *gin.Context) {
		user, err := c.Cookie("user")
		if err != nil {
			c.String(200, "用户未登录")
			return
		}
		c.String(200, "用户名: %s", user)
	})

	router.GET("/delete", func(c *gin.Context) {
		c.SetCookie("user", "", -1, "/", "localhost", false, true)
		c.String(200, "Cookie 已删除")
	})

	router.Run(":8080")
}

```

通过做这个案例，让我对 cookie 有了新的理解：

服务器并不存储 cookie，服务器做的事情只是，在请求的回复中，告知客户端，“你可以存储这样的一个 cookie，之后方便访问”。

这样一个过程之后，客户端需要在每次请求的时候，都带上自己本地存的 cookie 的值（浏览器会自动做这个事儿，但是 curl 命令默认不会自动存取 cookie）。

所以对于上面的过程，如果我们用浏览器访问：

1. 访问 `localhost:8080/get`，显示用户未登录。
2. 访问 `localhost:8080/set`，显示 Cookie 已设置。
3. 访问 `localhost:8080/get`，显示用户名：John。
4. 访问 `localhost:8080/delete`，显示 Cookie 已删除。
5. 访问 `localhost:8080/get`，显示用户未登录。

但是如果使用 curl 命令，默认情况下是不会存取 cookie 的。

比如现在我们访问 `curl localhost:8080/get`，这时候会显示用户未登录。从代码中可以看到，服务器在通过 `c.Cookie` 读取客户端发来的请求中的 cookie，但是发现没有 cookie，所以肯定是读不到用户的。

现在我们再使用一次 `curl localhost:8080/set -v`，这时候显示“Cookie 已设置”，但是实际上真的设置了吗，并不是。前面说到，服务器并不会存储 Cookie，只会告诉客户端，让客户端可以在本地存储一个什么样的 `cookie`。我们在 `curl` 中加上了 `-v` 选项，所以这次返回的请求中会带有：`Set-Cookie: user=john; Path=/; Domain=localhost; Max-Age=3600; HttpOnly` 这样一条消息。

但是这时候我们再使用一次 `curl localhost:8080/get`，返回的信息还是用户未登录。因为我们访问的时候并没有带上 cookie。

同理，我们直接使用 `curl localhost:8080/delete`，服务器也会返回“Cookie 已删除”，因为删除的原理就是设置 Cookie，将 Cookie 的过期时间设置为一个过去的时间。实际的原理和 `set` 中新建立一个 cookie 差不多。

那么如何使用呢？那就是在访问的时候，手动将 `cookie` 加入到访问的请求中，例如 `curl localhost:8080/get --cookie "user=toby"`，此时就会返回“用户名：toby”。但是，从中很容易发现，cookie 很容易捏造啊。我要是就直接在本地捏造一个 cookie，说我就是 admin 用户，服务器怎么能知道呢？在上面我们做的这个简单的 demo 中，肯定是就没有考虑到这个问题。但是企业的实践中，就会通过“在 Cookie 中存储密文”、“添加 cookie 验证中间件”这些方式，来防止用户窃取 cookie、篡改 cookie 这些问题。

或者是 curl 命令也可以模仿浏览器的行为。由于标准的 curl 就是一个无状态的命令，我们可以添加一些文件来让 `curl` 变成有状态的。比如说使用如下的命令：

```bash
# 设置 Cookie
curl -c cookies.txt http://localhost:8080/set
 
# 读取 Cookie（自动从 cookies.txt 发送）
curl -b cookies.txt http://localhost:8080/get
```

这时候就会，第一次请求中，浏览器发来一个建立 cookie 的回复，要求本地建立这样一个 cookie，本地就将 cookie 建立在了 `cookies.txt` 文件中。之后每次跟浏览器交互的时候，都从 `cookies.txt` 文件中读取数据，这样就实现了浏览器一样的自动存取 cookie 的需求。

### Session

Session 其实和 Cookie 有类似之处。我第一次跑 session 的 demo 代码，第一个印象就是，这个功能用 cookie 不是也可以做吗？后来发现，Session 其实可以理解为 cookie 的一种更高级的形态，Session 有多种实现方式，Cookie 是其中一种。

上面我们学习 Cookie 的时候，知道了一个知识点：Cookie 都是存储在客户端的。但是 Session 的存储是客户端和服务端都有的。其中，客户端存储的是 Session 的 ID，服务端存储的是 Session 的具体信息。

```go
func main() {
	router := gin.Default()

	// 定义加密密钥（确保生产环境使用强密钥）
	secret := []byte("1234567890123456")

	// 创建基于 Cookie 的存储
	store := cookie.NewStore(secret)
	// 添加 Session 中间件
	router.Use(sessions.Sessions("mysession", store))

	// 定义路由
	router.GET("/login", loginHandler)
	router.GET("/user", userHandler)
	router.GET("/logout", logoutHandler)

	router.Run(":8080")
}

func loginHandler(c *gin.Context) {
	// 获取当前 Session
	session := sessions.Default(c)

	// 写入数据（例如用户登录名）
	session.Set("username", "Alice")
	// 必须调用 Save() 保存修改！
	if err := session.Save(); err != nil {
		c.JSON(500, gin.H{"error": "保存 Session 失败"})
		return
	}

	c.JSON(200, gin.H{"message": "登录成功"})
}

func userHandler(c *gin.Context) {
	session := sessions.Default(c)
	// 读取数据
	username := session.Get("username")
	if username == nil {
		c.JSON(401, gin.H{"error": "未登录"})
		return
	}
	c.JSON(200, gin.H{"username": username})
}

func logoutHandler(c *gin.Context) {
	session := sessions.Default(c)
	// 删除所有 Session 数据
	session.Clear()
	session.Save()
	c.JSON(200, gin.H{"message": "已退出登录"})
}
```

这里，首先我们使用 `secret := []byte("1234567890123456")`，定义了一个用来加密数据的密钥。

之后的 `store := cookie.NewStore(secret)` 是指定了我们存储的时候，使用 `secret` 来加密存储的数据，并且返回了一个 `store` 的具体对象。

之后又通过 `router.Use(sessions.Sessions("mysession", store))` 定义了一个中间件。相当于是对于发来的每一个请求，都要去匹配一个 ID 是 `mysession` 的 cookie，并且存储的时候，是将信息存储到 `store` 中的。

如果是在浏览器中访问，直接 `/login`、`/user`、`/logout` 这样去访问就行，浏览器会自动处理这些 token。

如果是 `curl` 命令，就比较复杂了：

```bash
[root@JiGeX gin-demo]# curl -v localhost:8080/login

此时返回的信息中，有一行数据是：
 Set-Cookie: mysession=MTc1MzI0MDQ2N3xEWDhFQVFMX2dBQUJFQUVRQUFBbl80QUFBUVp6ZEhKcGJtY01DZ0FJZFhObGNtNWhiV1VHYzNSeWFXNW5EQWNBQlVGc2FXTmx8b9KPuBJs30caASgGW0zUrRuByFs10OynqL3ls3WyRmQ=; Path=/; Expires=Fri, 22 Aug 2025 03:14:27 GMT; Max-Age=2592000; Secure; SameSite=None
 意思是让我们在本地设置一个 Cookie，cookie 的键值对内容就是：mysession=...
 
 
[root@JiGeX gin-demo]# curl -v localhost:8080/user --cookie "mysession=MTc1MzI0MDQ2N3xEWDhFQVFMX2dBQUJFQUVRQUFBbl80QUFBUVp6ZEhKcGJtY01DZ0FJZFhObGNtNWhiV1VHYzNSeWFXNW5EQWNBQlVGc2FXTmx8b9KPuBJs30caASgGW0zUrRuByFs10OynqL3ls3WyRmQ="

之后访问的时候，就要带上这个 token，才能访问。
```

整个流程相当于是：客户端在访问的时候，在 cookie 中带上访问的 session 的 id（就是那个极其复杂的字符串），之后 gin 的中间件会检查这个 session 的 id 解析之后是否正确。如果是正确的的话，之后就可以根据这个 session 的 ID 去存储后端设置、修改数据了。

```go
客户端请求
   │
   └─▶ 携带 Cookie: mysession=abc123
          │
服务端处理
   │
   ├─ 中间件解析 Cookie，获取 Session ID（abc123）
   │
   ├─ 根据 ID 从 Store（如 Redis）加载 Session 数据
   │
   ├─ 数据存入上下文 → 路由代码通过 sessions.Default(c) 读取/修改
   │
   └─ 返回响应时，如有修改，更新 Store 并设置新 Cookie
```

## 中间件

### 默认中间件

如果使用 `router := gin.Default()`，则会在路由器中自动添加两个中间件：`Logger` 和 `Recovery`。

```go
func main() {
	// 默认开启 Logger 和 Recovery 中间件
	router := gin.Default()

	router.GET("/hello", func(c *gin.Context) {
		c.String(200, "Hello gin!")
	})

	router.Run(":8080")
}
```

如果想要创建一个空白的基础路由器，一个中间件都没有，可以使用 `r := gin.New()` 来创建：

```go
func main() {
	// 没有加入中间件
	router := gin.New()

	router.GET("/hello", func(c *gin.Context) {
		c.String(200, "Hello gin!")
	})

	router.Run(":8080")
}
```

其中的 `Logger` 中间件是一个打印 HTTP 日志的中间件。它的效果就是在服务器上会对每一次请求开启日志记录的功能：

![image-20250723152314288](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250723152314288.png)

其中的 `Recovery` 是一个可以放置崩溃的中间件。当请求处理逻辑发生 panic 的时候，捕获错误并返回 500 错误，防止服务器崩溃。

例如对于如下的代码：

```go
func main() {
	// 没有加入中间件
	router := gin.Default()

	router.GET("/hello", func(c *gin.Context) {
		panic("手动触发 panic")
		c.String(200, "你看不到我")
	})

	router.GET("world", func(c *gin.Context) {
		c.String(200, "World")
	})

	router.Run(":8080")
}
```

我们使用默认的路由器配置（带有 `Recovery`），设置了两个路由，分别是 `hello` 和 `world`。其中，`hello` 的执行一定会触发 `panic`，`world` 的执行可以正常返回信息。

此时我们在客户端测试：

```go
// 访问 hello，不会看到回复中的输出，返回的错误状态码是 500
[root@JiGeX gin-demo]# curl localhost:8080/hello -v

// 继续访问 world，发现可以正常输出
[root@JiGeX gin-demo]# curl localhost:8080/world -v
World
```

此时服务器中显示：

![image-20250723152951938](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250723152951938.png)

可以发现，服务器捕获到了错误，并且发生了 panic 不会导致服务器中的服务停止。

但是如果如果使用 `New()` 来创建一个不带有 `Recovery()` 中间件的路由器，最后的效果……我只能说展示出来的和这个不太一样吧：

![image-20250723153348347](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250723153348347.png)

访问 hello 的时候，会爆出这样的很多的错误。我还以为服务器会直接停止，结果并没有，之后再访问 world，还是会继续提供服务的。

可以看到这个 `Recovery()` 肯定是做了一些事情的，但是具体是什么，我现在也还研究不透。

### 自定义中间件

中间件本质上是一个函数，要求这个函数返回 `gin.HandlerFunc` 类型。

其中，`gin.HandlerFunc` 类型的定义是：

```go
type HandlerFunc func(*Context)
```

所以在我们的代码中，我们对中间件的定义，可以使用如下的骨架代码：

```go
func MyMilldeware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 请求处理前执行的逻辑
    	// ...
        
        c.Next()
    	
        // 请求处理后执行的逻辑
        // ...
    }
}
```

其中，`c.Next()` 是一个函数，可以看成是一个分界线。在 `c.Next()` 之前的逻辑是在请求处理之前执行的部分，`c.Next()` 之后的代码是请求处理之后执行的部分。

#### demo1 - 记录请求路径

比如说，下面是一个简单的，打印出请求路径的中间件实现：

```go
func LogPath() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 请求处理前记录路径
		println("请求路径:", c.Request.URL.Path)
		c.Next()
	}
}

func main() {
	router := gin.Default()

	// 全局使用中间件
	router.Use(LogPath()) // 所有路由都会触发

	router.GET("/hello", func(c *gin.Context) {
		c.String(200, "Hello!")
	})

	router.Run(":8080")
}
```

之后在请求的时候，服务器就会输出：

![image-20250723154456251](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250723154456251.png)

#### demo2 - 添加自定义 Header

假如我们要在所有的响应头中添加 `X-MyApp-Version: v1.0`。

```go
func AddVersionHeader() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 先处理请求
		c.Next()

		// 处理完毕后添加 Header
		c.Writer.Header().Set("X-MyApp-Version", "v1.0")
	}
}

func main() {
	router := gin.Default()

	router.Use(AddVersionHeader())

	router.GET("/info", func(c *gin.Context) {
		c.String(200, "Info Page")
	})

	router.Run(":8080")
}
```

客户端访问的时候，可以使用 `curl -I` 来查看响应头的信息：

```go
[root@JiGeX gin-demo]# curl localhost:8080/info -I
...
X-Myapp-Version: v1.0
```

#### demo3 - 中间件间传递数据

在中间件中设置数据，路由处理函数中可以获取。

```go
func SetRequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 生成一个随机 ID（示例用简单逻辑）
		requestID := "REQ-123"
		// 将 ID 存入 Context，供后续使用
		c.Set("request_id", requestID)
		c.Next()
	}
}

func main() {
	router := gin.Default()

	router.Use(SetRequestID())

	router.GET("/id", func(c *gin.Context) {
		// 从 Context 中获取 ID
		id, _ := c.Get("request_id")
		c.String(200, "Request ID: %s", id)
	})
}
```

客户端访问：

```go
[root@JiGeX gin-demo]# curl localhost:8080/id
Request ID: REQ-123
```

#### demo4 - 终端请求的中间件

比如检查 API 密钥，如果不合法则终止请求。

```go
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 假设从 Header 获取 API 密钥
		apiKey := c.GetHeader("X-API-Key")
		if apiKey != "my-secret-key" {
			// 中断后续处理，返回 401 错误
			c.AbortWithStatusJSON(401, gin.H{"error": "Invalid API Key"})
			return
		}
		c.Next()
	}
}

func main() {
	router := gin.Default()

	// 只有 private 路由组需要认证
	private := router.Group("/private")
	private.Use(AuthMiddleware())
	{
		private.GET("/data", func(c *gin.Context) {
			c.String(200, "敏感数据")
		})
	}

	// 公开路由不需要认证
	router.GET("/public", func(c *gin.Context) {
		c.String(200, "公开信息")
	})

	router.Run(":8080")
}
```

访问的时候：

```go
// 访问 /public 路由
[root@JiGeX gin-demo]# curl localhost:8080/public
公开信息

// 使用正确的 api-key 访问 /private/data 路由
[root@JiGeX gin-demo]# curl localhost:8080/private/data -H "X-API-Key: my-secret-key"
敏感数据[root@JiGeX gin-demo]#

// 使用错误的 api-key 访问 /private/data 路由
[root@JiGeX gin-demo]# curl localhost:8080/private/data -H "X-API-Key: my-secret"
{"error":"Invalid API Key"}
```



















