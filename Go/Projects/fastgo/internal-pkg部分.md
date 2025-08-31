# internal-pkg 部分

这里的 pkg 是在 internal 中的，也就是我们期望的这部分 pkg 是只有这个项目在用的。与项目的根目录中的 pkg 不同，那部分 pkg 是比较通用的，很多项目中都可以使用的，是推荐外部可以引入的。

## contextx

我们知道 context 中是可以存放键值对的。只不过存放新的键值对的方式是在原本的 context 的基础上新建立一个 context，并且在新的 context 中加入这个键值对。

在 fastgo 项目中，就是预设了几个项目中的 context 中最常用到的几个键值对的设置方法、获取方法等。

首先是定义了几个常用的 context 的键：

```go
// 定义用户上下文的键
type (
	// requestIDKey 定义请求 ID 的上下文键
	requestIDKey struct{}
	// userIDKey 定义用户 ID 的上下文键
	userIDKey struct{}
	// usernameKey 定义用户名的上下文键
	usernameKey struct{}
)
```

之后对每一个 context 类型，都定义这个类型的添加键值对的 api 和获取键值对的值的 api。例如，对于 requestIDKey 部分，我们有：

```go
// WithRequestID 将请求 ID 存放到上下文中
func WithRequestID(ctx context.Context, requestID string) context.Context {
	return context.WithValue(ctx, requestIDKey{}, requestID)
}

// RequestID 从上下文中提取请求 ID
func RequestID(ctx context.Context) string {
	requestID, _ := ctx.Value(requestIDKey{}).(string)
	return requestID
}
```

其中，`WithRequestID()` 表示，在一个原本的 context 中，加入一个 context-id 的键值对。传入函数的时候只需要传入值是多少就行，因为键已经定义好了。

`RequestID()` 方法就是直接从这个 context 中提取 `requestIDKey` 对应的值，也就是在一个 context 中根据一个 key 去取出一个对应的 value。

同时，仿照上面的 `RequestID` 中的写法，这个包中还提供了对于另外两种 context 的键值对操作的 api：

| API              | 说明                                |
| ---------------- | ----------------------------------- |
| `WithUserID()`   | 将用户 ID 存放到 context 中         |
| `UserID()`       | 从 context 中获取用户 ID            |
| `WithUsername()` | 将 Username 用户名存放到 context 中 |
| `Username()`     | 从 context 中获取 username          |

## conversion

### user

`Conversion` 中提供了两个 API，分别是将 user 的 model 类型转换为 user 的 proto 类型：

```go
// PostModelToPostV1 将模型层的 Post（博客模型对象）转换为 Protobuf 层的 Post（v1 博客对象）
func PostModelToPostV1(postModel *model.Post) *apiv1.Post {
	var protoPost apiv1.Post
	_ = copier.Copy(&protoPost, postModel)
	return &protoPost
}

// PostV1ToPostModel 将 Protobuf 层的 Post（v1 博客对象）转换为模型层的 Post（博客模型对象）
func PostV1ToPostModel(protoPost *apiv1.Post) *model.Post {
	var postModel model.Post
	_ = copier.Copy(&postModel, protoPost)
	return &postModel
}
```

其中 user 的 model 类型是由工具 `gormgen` 自动生成的，并且这部分内容是不允许修改的。数据类型中的定义完全按照数据库中的 user 表的定义。

user 的 proto 类型，定义为在最外层的 pkg 包中对 user 的定义。其中的定义与 model 类型的 user 基本相同，但是有细微的不同。

```go
// model 类型的 user
type User struct {
	ID        int64     `gorm:"column:id;primaryKey;autoIncrement:true" json:"id"`
	UserID    string    `gorm:"column:userID;not null;comment:用户唯一 ID" json:"userID"`                                    // 用户唯一 ID
	Username  string    `gorm:"column:username;not null;comment:用户名（唯一）" json:"username"`                                // 用户名（唯一）
	Password  string    `gorm:"column:password;not null;comment:用户密码（加密后）" json:"password"`                              // 用户密码（加密后）
	Nickname  string    `gorm:"column:nickname;not null;comment:用户昵称" json:"nickname"`                                   // 用户昵称
	Email     string    `gorm:"column:email;not null;comment:用户电子邮箱地址" json:"email"`                                     // 用户电子邮箱地址
	Phone     string    `gorm:"column:phone;not null;comment:用户手机号" json:"phone"`                                        // 用户手机号
	CreatedAt time.Time `gorm:"column:createdAt;not null;default:current_timestamp();comment:用户创建时间" json:"createdAt"`   // 用户创建时间
	UpdatedAt time.Time `gorm:"column:updatedAt;not null;default:current_timestamp();comment:用户最后修改时间" json:"updatedAt"` // 用户最后修改时间
}

// proto 类型的 user
type User struct {
	// userID 表示用户 ID
	UserID string `json:"userID"`
	// username 表示用户名称
	Username string `json:"username"`
	// nickname 表示用户昵称
	Nickname string `json:"nickname"`
	// email 表示用户电子邮箱
	Email string `json:"email"`
	// phone 表示用户手机号
	Phone string `json:"phone"`
	// postCount 表示用户拥有的博客数量
	PostCount int64 `json:"postCount"`
	// createAt 表示用户注册的时间
	CreatedAt time.Time `json:"createdAt"`
	// updateAt 表示用户最后更新时间
	UpdatedAt time.Time `json:"updatedAt"`
}
```

可以看到其中的主要区别是，业务友好型的数据类型与数据库中实际存储的类型之间有一定的区别。比如说，直接从数据库中获取到的一条数据中，有一个 ID 数据段，这个数据段的含义是这是数据库中的第多少个记录，但是这部分数据在业务处理中并不需要。还有 password 也消失了，这部分也是因为业务处理中，一般不需要使用到用户的密码。

proto 类型的 user 相比于 model 类型的 user，还多了一个数据段，就是 `postCount` 数据段。这部分的含义是用户拥有博客的数量。这部分内容在后续的业务中需要知道，但是数据库中却不会存这个数据。

所以出现两种数据类型的原因还是因为数据库友好型和业务友好型之间的区别。

### post

post 部分的原理与 user 部分类似，也是根据数据库友好型和业务友好型区分了 model 类型的 post 和 proto 类型的 post。

## core

core 部分核心内容就是一个 API：

```go
// WriteResponse 是通用的响应函数
// 它会根据是否发生错误，生成成功响应或标准化的错误响应
func WriteResponse(c *gin.Context, data any, err error) {
	if err != nil {
		// 如果发生错误，生成错误响应
		errx := errorsx.FromError(err) // 提取错误详细信息
		c.JSON(errx.Code, ErrorResponse{
			Reason:  errx.Reason,
			Message: errx.Message,
		})
		return
	}

	// 如果没有错误，返回成功响应
	c.JSON(http.StatusOK, data)
}
```

也就是，如果业务中觉得自己需要返回内容了，就可以使用 `WriteResponse()` 方法。这个方法中最后一个参数传入的是一个 err 类型，如果 err 为空，就说明本次的 response 是一个正确的类型；如果 err 不为空，就说明本次是要返回一个错误的信息。返回的方式都是通过一个 `c.JSON()` 来返回信息的。

同时，为了返回错误的时候更加方便，还定义了一个出错的 `ErrResponse` 类型：

```go
// ErrorResponse 定义了错误响应的结构
// 用于 API 请求中发生错误时返回统一的格式化错误信息.
type ErrorResponse struct {
	// 错误原因，标识错误类型
	Reason string `json:"reason,omitempty"`
	// 错误详情的描述信息
	Message string `json:"message,omitempty"`
}
```

http 请求中的所有 response 都是通过 `WriteResponse()` 来返回的。所以这样可以确保，只要出错，一定都是按照这个类型获取 response 的：`Reason + Message`。

其中，`WriteResponse()` 中返回错误的时候，有一个功能是通过 err 来获取这个 err 对应的 Code、Reason 和 Message。这部分操作是通过 `errorsx.FromError(err)` 实现的，具体实现方法在 `errorsx` 包中。

## errorsx

errorsx 中主要是定义了 Errorx 这种结构体的结构，之后设置了很多种常用的 Errorx 的包级全局变量。

首先，在 errorsx.go 中定义了 Errorx 的结构：

```go
// ErrorX 定义了 fastgo 项目中使用的错误类型，用于描述错误的详细信息
type ErrorX struct {
	// Code 表示错误的 HTTP 状态码，用于与客户端进行交互时标识错误的类型。
	Code int `json:"code,omitempty"`

	// Reason 表示错误发生的原因，通常为业务错误码，用于精准定位问题
	Reason string `json:"reason,omitempty"`

	// Message 表示简短的错误信息，通常可直接暴露给用户查看
	Message string `json:"message,omitempty"`
}
```

其中可以看出，ErrorX 由三部分组成，分别是本次错误的 HTTP 状态码、Reason 错误发生的原因、Message 简短的错误信息。

随后还定义了一个 `New()` 方法，方法传入 code、reason、message 这几个参数，之后返回一个新的 ErrorX 结构体。

之后定义了 `Error()` 方法，实现 error 接口。定义如下：

```go
// Error 实现 error 接口中的 Error 方法
func (err *ErrorX) Error() string {
	return fmt.Sprintf("err: code = %d, reason = %s, message = %s", err.Code, err.Reason, err.Message)
}
```

> 一个结构体，实现 `Error()` 方法和实现 `String()` 方法都是为了打印的美观。其中 `Error()` 方法是实现 error 接口，`String()` 方法是实现 Stringer 接口。如果一个结构体同时实现了两种接口，那么会优先打印 `Error()` 方法中的内容。这是因为 golang 中认为错误不应该被忽视或隐藏，而应该及时被处理。

之后提供了设置 Message 字段的方法：

```go
// WithMessage 设置错误的 Message 字段
func (err *ErrorX) WithMessage(format string, args ...any) *ErrorX {
	err.Message = fmt.Sprintf(format, args...)
	return err
}
```

> golang 中更倾向于使用 With 模式来定义一个字段，而不是传统模式中的 Setter 模式。这种情况在 context 部分比较常见，因为我们构建一个新的 context 是在原本的 context 之上的，所以就是 with 原本的 context。golang 中认为不变性比可变性更安全，所以比较推崇 With 的方式。
>
> 但是这个函数这里，其实我觉得还是使用 Set 会更合适。因为 With 和 Set 的区别主要在于：
>
> - With 类型函数是创建了一个新对象
> - Set 类型函数是修改了原本对象的某一个字段
>
> 这里只是将 Message 字段做了个修改，所以还是使用 Set 比较合适。如果使用 With 的话，可以创建一个新的 ErrorX，之后将新的对象中的 Message 字段做修改，再返回新对象即可。

之后提供了一个，将普通的 error 类型转换为 ErrorX 的方法：

```go
// FromError 尝试将一个通用的 error 转换为自定义的 *ErrorX 类型
func FromError(err error) *ErrorX {
	// 如果传入的错误是 nil，则直接返回 nil，表示没有错误需要处理
	if err == nil {
		return nil
	}

	// 检查传入的 error 是否已经是 ErrorX 类型的实例
	// 如果错误可以通过 errors.As 转换为 *ErrorX 实例，则直接返回该实例
	if errx := new(ErrorX); errors.As(err, &errx) {
		return errx
	}

	// 默认返回未知错误错误，该错误表示服务端出错
	return &ErrorX{
		Code:    ErrInternal.Code,
		Reason:  ErrInternal.Reason,
		Message: err.Error(),
	}
}
```

这个函数的作用是，将一个实现了 Error() 方法的 error 类型，转换为一个 ErrorX 的类型。同时转换的逻辑是：

1. 如果这个 err 是空，那么就直接返回 nil。
2. 如果这个 err 本身就已经是 ErrorX 了（ErrorX 也是一种 error 类型），那么就不用做别的操作，直接重新指定为 ErrorX 类型，然后返回即可。
3. 否则就返创建一个新的 ErrorX 类型，其中的 Code 和 Reason 都设置成服务器中未知的错误类型。

这其实也说明，之后我们在项目中使用 ErrorX 的方法，还是，在出现错误的时候，直接就将一个 err 制作成 ErrorX 的对象。而不是就使用一个简单的 err，等到了处理的后期了，再使用 FromError() 进行转换。

> 这里再总结一下 From 类方法和 With 类方法的区别。从结果上看，二者都是创建了新的对象。从处理的数据类型上看：
>
> - With 类方法适合基于原本的一个对象，构造出一个新的对象，并且在新的对象中修改某个字段。原数据类型和目标数据类型是一致的。
> - From 类方法适合做类型的转换。原数据类型和目标数据类型是不同的。比如说 FromError 就是根据一个 err 创建一个新的目标类型，FromJSON 就是根据一个 json 创建一个新的目标类型。

---

除此之外，这个包中，在 code.go、user.go、post.go 这几个文件中，创建了很多种不同的 ErrorX 全局常量。如：

| 错误        | Code                             | Reason            | Message                |
| ----------- | -------------------------------- | ----------------- | ---------------------- |
| OK          | `http.StatusOK`                  | -                 | -                      |
| ErrInternal | `http.StatusInternalServerError` | InternalError     | Internal Server Error. |
| ErrNotFound | `http.StatusNotFound`            | NotFound          | Resource not found.    |
| ErrDBRead   | `http.StatusInternalServerError` | InterError.DBRead | Database read failure. |
| ...         | ...                              | ...               | ...                    |

## known

known 包中的内容比较简单，只有一个文件，文件中定义了一些常量：

```go
const (
	// XRequestID 用来定义上下文中的键，代表请求 ID
	XRequestID = "x-request-id"

	// XUserID 用来定义上下文的键，代表请求用户 ID。UserID 整个用户生命周期唯一
	XUserID = "x-user-id"
)

// 定义其他常量
const (
	// MaxErrGroupConcurrency 定义了 errgroup 的最大并发任务数量
	MaxErrGroupConcurrency = 1000
)
```

比如说其中的 `XRequestID` 表示给一个完整的 request、response 中设定一个不会变的请求 ID，也就是在 gin 的 context 中设定一个固定的键值对。将所有的键值对的名称都设定为统一的 `x-request-id`，可以避免后期因为手误设置了不同的键名。

## middleware

golang 中中间件的定义方式是：

```go
gin.HanlderFunc
```

具体来说，这种结构定义为：

```go
// HandlerFunc defines the handler used by gin middleware as return value.
type HandlerFunc func(*Context)
```

在 middleware 中，我们定义了几个会用到的中间件，如下所示：

```go
// NoCache 是一个 Gin 中间件，用来禁止客户端缓存 HTTP 请求的返回结果
func NoCache(c *gin.Context) {
	c.Header("Cache-Control", "no-cache, no-store, max-age=0, must-revalidate, value")
	c.Header("Expires", "Thu, 01 Jan 1970 00:00:00 GMT")
	c.Header("Last-Modified", time.Now().UTC().Format(http.TimeFormat))
	c.Next()
}
```

Nocache 中间件，让客户端不要缓存 HTTP 的请求结果，每一次都访问服务器来获取最新的结果。

---

```go
// Cors 是一个 Gin 中间件，用来设置 options 请求的返回头，然后退出中间件链，并结束请求（浏览器跨域设置）
func Cors(c *gin.Context) {
	if c.Request.Method != "OPTIONS" {
		c.Next()
	} else {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET,POST,PATCH,DELETE,OPTIONS")
		c.Header("Access-Control-Allow-Headers", "authorization, origin, content-type, accept")
		c.Header("Allow", "HEAD,GET,POST,PUT,PATCH,DELETE,OPTIONS")
		c.Header("Content-Type", "application/json")
		c.AbortWithStatus(200)
	}
}
```

golang 中的 Option 类的方法，不涉及具体的业务处理，而是做一个“探测”。比如说探测，我们这个服务是不是允许跨域处理、都允许什么方法、都允许什么 Header、Content-Type 允许什么类型之类的。或者说就是做了一个询问，询问完之后，直接返回 200 状态码就行。

> 跨域就是在处理请求的过程中，请求被转发到了别的“域”。比如说前端处理在 myapp.com:3000，后端处理在 `api.myapp.com:8000`，这时候就是发生了跨域请求。前后使用的协议（http 和 https）不同、域名不同、端口不同等，都可以视为跨域请求。
>
> 我们在这个 Header 中设置的 `Access-Control-Allow-Origin` 为 `*`，表示允许跨域请求被转发到所有的域中。

---

```go
// RequestID 是一个 Gin 中间件，用来在每一个 HTTP 请求的 context.response 中注入 `x-request-id` 键值对
func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 从请求头中获取 `x-request-id`，如果不存在则生成新的 UUID
		requestID := c.Request.Header.Get(known.XRequestID)

		if requestID == "" {
			requestID = uuid.New().String()
		}

		// 将 RequestID 保存到 context.Context 中，以便后续程序使用
		ctx := contextx.WithRequestID(c.Request.Context(), requestID)
		c.Request = c.Request.WithContext(ctx)

		// 将 RequestID 保存到 HTTP 返回头中，Header 的键为 `x-request-id`
		c.Header(known.XRequestID, requestID)

		// 继续处理请求
		c.Next()
	}
}
```

从请求头中获取 `x-request-id` 的键值对，如果不存在生成一个新的 `x-request-id`。

得到新的 `x-request-id` 之后，将这个键值对保存到 gin.Request 的上下文中。这里就是使用了 With 类方法，通过将原本的一个 ctx 进行修改，得到一个新的 ctx，再去覆盖原本的 ctx。这是因为 c.Request 是不可变的，所以只能通过 ctx 覆盖的方式，来修改 c.Request 中的内容。

之后通过 `c.Header()` 在响应头中设置好 `x-request-id` 的键值对。

---

```go
// Authn 是认证中间件，用来从 gin.Context 中提取 token 并验证 token 是否合法
// 如果合法，就将 token 中的 sub 作为 <用户名> 存放在 gin.Context 的 XUsernameKey 键中
func Authn() gin.HandlerFunc {
	return func(c *gin.Context) {
		// 解析 JWT Token
		userID, err := token.ParseRequest(c)
		if err != nil {
			core.WriteResponse(c, errorsx.ErrTokenInvalid, nil)
			c.Abort()
			return
		}

		// 将用户 ID 和用户名注入到上下文中
		ctx := contextx.WithUserID(c.Request.Context(), userID)
		c.Request = c.Request.WithContext(ctx)

		// 继续后续的操作
		c.Next()
	}
}
```

这个中间键绑定在了 post 相关的所有操作中，以及除了 Login 和 Create 的所有 user 操作中。也就是说，做别的操作的时候，都需要有 token 令牌。检验 token 令牌的方式就是首先从 c.Request.Header 中去获取 `Authorization` 相关的内容，之后解析出本次使用的令牌中的 userid。如果解析 token 令牌的过程中出错了，就直接返回错误。

如果解析用户令牌成功了，就在 c.Request 上下文中，将 `UserIDKey{} -> userID` 这个键值对放到 Request 的 context 中。

## rid

首先在 salt.go 中提供了一个根据机器的 id 获取随机盐值的方法，这里定义了一个 `ReadMachineID()` 的方法，其中使用了很多种获取机器 id 的方法，比如说查看文件 `/etc/machine-id`，或者是查看文件 `/sys/class/dmi/id/product_uuid` 或者是直接使用 `os.Hostname()` 等，找到一种能用的方法，作为机器的 id 值。

之后就是对机器的 id 值计算一个哈希值：

```go
// Salt 计算机器 ID 的哈希值并返回一个 uint64 类型的盐值
func Salt() uint64 {
	// 使用 FNV-1a 哈希算法计算字符串的哈希值
	hasher := fnv.New64a()
	hasher.Write(ReadMachineID())

	// 将哈希值转换为 uint64 型盐
	hashValue := hasher.Sum64()
	return hashValue
}
```

虽然其中使用的是 FNV 哈希算法，但是在接口上跟 SHA256 方法，除了输出的长度不同，其余的接口都一样的，就当 SHA256 使用就行。所以 `Salt()` 方法就是根据机器 ID 获得了一段哈希值。

之后又设置了两个 ResourceID 类型的常量，分别是 UserID 和 PostID：

```go
type ResourceID string

const (
	// UserID 定义用户资源标识符
	UserID ResourceID = "user"
	// PostID 定义博文资源标识符
	PostID ResourceID = "post"
)
```

随后提供了一个 `New()` 方法：

```go
// New 创建带前缀的唯一标识符
func (rid ResourceID) New(counter uint64) string {
	// 使用自定义选项生成唯一标识符
	// 其实就是做了一个“伪装”，不能将原本的 id 直接暴露给用户，而是结合一些 options 对 id 进行了伪装，最后生成一个结果字符串
	uniqueStr := id.NewCode(
		counter,
		id.WithCodeChars([]rune(defaultABC)),
		id.WithCodeL(6),
		id.WithCodeSalt(Salt()),
	)

	return rid.String() + "-" + uniqueStr
}
```

方法中使用的 id 包是 github 上的 onexstack 中的包，这里我们只做抽象理解。调用 `id.NewCode()`，其中传入一些固定的字符串，还有我们的机器盐值，就是为了生成一个特定的字符串。counter 部分其实是加密算法的一个参数，不过后面我们调用的时候，是传入了这个参数的 `user.ID` 或者 `post.ID`。然后通过 `id.NewCode()` 生成一个长度为 5 的特定字符串。

这部分是用来生成 `userID` 和 `postID` 的，于是最后对于一个 user 资源类型，我们就可以得到 `user-rhdmke`、`user-p86ggd` 这样的 `userID`。

## validation

首先是定义了一个 `Validator` 的验证的结构体，结构体中只有一个字段，是一个 IStore 类型。

```go
// Validator 是验证逻辑的实现结构体
type Validator struct {
	// 有些复杂的验证逻辑，可能需要直接查询数据库
	// 这里只是一个举例，如果验证时，有其他依赖的客户端/服务/资源等
	// 都可以一并注入进来
	store store.IStore
}
```

同时也提供了创建一个新的 Validator 的方法 `NewValidator()`，其中的参数也比较简单，就是一个 IStore 类型的参数，之后可以直接通过这个 store 参数创建出新的 Validator：

```go
// NewValidator 创建一个新的 Validator 实例
func NewValidator(store store.IStore) *Validator {
	return &Validator{store: store}
}
```

之后其他的内容就是与 `pkg/api/apiserver/v1` 中的内容联动了，通过 Validator 检查每一个 Request 的内容是不是合理的。比如说在这个文件夹中的 `user.go` 中，就有如下的一些 api：

| API                         | 作用                                                         |
| --------------------------- | ------------------------------------------------------------ |
| `ValidateCreateUserRequest` | 检查 Request 中的 username、password、nickname 等字段是不是合法的 |
| `ValidateUpdateUserRequest` | 检查更新用户的 Request 是不是合法的                          |
| `ValidateDeleteUserRequest` | 检查删除用户的 Request 是不是合法的                          |
| ……                          | ……                                                           |

## 总结

这部分内容主要还是讲了业务中会使用到的包，从 contextx、conversion、core 等包中来看，里面用到的数据类型都是这个项目独有的，所以跟项目的联系比较紧。

| 包         | 作用                                                         |
| ---------- | ------------------------------------------------------------ |
| contextx   | 给上下文中加入 `x-request-id` 之类的键值对                   |
| conversion | 在 user 和 post 的 model 类型和 proto 类型之间进行转换       |
| core       | 提供了 `WriteResponse()` 方法，统一 http Response 的结构     |
| errorsx    | 定义了自定义的错误类型，由错误的 Code、Reason、Message 组成，统一了项目返回 error 的结构 |
| known      | 定义了整个项目中共用的一些环境常量，比如说 `x-request-id`、`x-user-id` 等 |
| middleware | 定义 gin 处理请求时使用到的中间件，比如说设定 `x-request-id`、设置统一的响应 Header、从 Request Header 中查看 token 令牌等 |
| rid        | 用于生成随机的 userID 或者 postID，比如说 `user-p86ggd`      |
| validation | 用于做请求的验证，比如说验证 CreateUserRequest 中的每个参数是否都是合法的 |



































