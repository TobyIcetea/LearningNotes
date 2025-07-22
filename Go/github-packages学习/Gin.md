# Gin

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

#### **【静态路由与动态路由】**

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

#### **【`c.JSON` 返回类型】**

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

#### **【`c.ShouldBindJSON` 方法】**

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

### 大量路由实现（TODO）













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













