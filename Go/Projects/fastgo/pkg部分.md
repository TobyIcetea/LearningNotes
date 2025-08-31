# pkg 部分

这里说的 pkg 是项目最外层的根目录中的 pkg 部分。这里的 pkg 的意思是，逻辑是比较通用的，除了本地的这个 fastgo 项目可以使用，也欢迎其他的项目中使用这里的包。

pkg 中的目录树结构如下所示：

```go
pkg
├── api
│   └── apiserver
│       └── v1
│           ├── post.go
│           └── user.go
├── auth
│   └── auth.go
├── options
│   └── mysql_options.go
├── token
│   └── token.go
└── version
    ├── flag.go
    └── version.go
```

接下来就一个一个讲解这些包。

## api/apiserver/v1

### User

首先是对 User 的定义：

```go
// User 表示用户信息
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

之后就都是定义的各种结构体：

| 结构体                 | 说明           |
| ---------------------- | -------------- |
| LoginRequest           | 用户登录请求   |
| LoginResponse          | 用户登录响应   |
| RefreshTokenRequest    | 刷新令牌的请求 |
| RefreshTokenResponse   | 刷新令牌的响应 |
| ChangePasswordRequest  | 修改密码的请求 |
| ChangePasswordResponse | 修改密码的响应 |
| CreateUserRequest      | 创建用户的请求 |
| CreateUserResponse     | 创建用户的响应 |
| UpdateUserRequest      | 更新用户的请求 |
| UpdateUserResponse     | 更新用户的响应 |
| DeleteUserRequest      | 删除用户的请求 |
| DeleteUserResponse     | 删除用户的响应 |
| GetUserRequest         | 获取用户的请求 |
| GetUserResponse        | 获取用户的响应 |
| ListUserRequest        | 用户列表请求   |
| ListUserResponse       | 用户列表响应   |

### Post

首先是对 Post 结构体的定义：

```go
// Post 表示博客文章
type Post struct {
	// postID 表示博文 ID
	PostID string `json:"postID"`
	// userID 表示用户 ID
	UserID string `json:"userID"`
	// title 表示博客标题
	Title string `json:"title"`
	// content 表示博客内容
	Content string `json:"content"`
	// createdAt 表示博客创建时间
	CreatedAt time.Time `json:"createdAt"`
	// updatedAt 表示博客最后更新时间
	UpdatedAt time.Time `json:"updatedAt"`
}
```

之后是对 Post 业务结构体准备的一些 API。因为 Post 这里没有改密码、刷新令牌之类的 API 的需求，所以 Post 部分提供的 API 数量相对较少：

| 结构体             | 说明               |
| ------------------ | ------------------ |
| CreatePostRequest  | 创建文章的请求     |
| CreatePostResponse | 创建文章的响应     |
| UpdatePostRequest  | 更新文章的请求     |
| UpdatePostResponse | 更新文章的响应     |
| DeletePostRequest  | 删除文章的请求     |
| DeletePostResponse | 删除文章的响应     |
| GetPostRequest     | 获取文章的请求     |
| GetPostResponse    | 获取文章的响应     |
| ListPostRequest    | 获取文章列表的请求 |
| ListPostResponse   | 获取文章列表的响应 |

## auth

auth 包中的内容比较简单，就两个函数：

```go
import "golang.org/x/crypto/bcrypt"

// Encrypt 使用 bcrypt 加密纯文本
func Encrypt(source string) (string, error) {
	// GenerateFromPassword 用于安全地生成密码哈希，其中的 cost 表示哈希计算的“工作因子”
	hashedBytes, err := bcrypt.GenerateFromPassword([]byte(source), bcrypt.DefaultCost)

	return string(hashedBytes), err
}

// Compare 比较密文和明文是否相同
func Compare(hashedPassword, password string) error {
	// CompareHashAndPassword 用于比较哈希后的密码和明文密码是否匹配
	return bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
}
```

这里是使用了 golang 的 bcrypt 包中的函数，多了一层包装。其实就是首先将一个密码转换为哈希形式进行存储，之后还提供了一个 compare，用于比较一个明文和加密之后的哈希密文是不是一样的。

这里在实际的工程中，是用来比较密码的。比如说做密码比较的时候，我们都是比较的密文，明文是最好不要出现，后端比较的逻辑肯定也不能暴露给用户。

## options

### MySQLOptions

这里在 cmd 部分已经说过了。在 cmd 部分，我们说那时候使用的是一个 ServerOptions，ServerOptions 中包含 `MySQLOptions`、`Address`、`JWTKey`、`Expiration` 等字段，而其中的 MysqlOptions 就是使用了 外部的 pkg 中的这个 MySQLOptions。

这个包中首先是给出了 MySQLOptions 的定义：

```go
// MySQLOptions defines options for mysql database.
type MySQLOptions struct {
	Addr                  string        `json:"addr,omitempty" mapstructure:"addr"`
	Username              string        `json:"username,omitempty" mapstructure:"username"`
	Password              string        `json:"-" mapstructure:"password"`
	Database              string        `json:"database" mapstructure:"database"`
	MaxIdleConnections    int           `json:"max-idle-connections" mapstructure:"max-idle-connections,omitempty"`
	MaxOpenConnections    int           `json:"max-open-connections" mapstructure:"max-open-connections"`
	MaxConnectionLifeTime time.Duration `json:"max-connection-life-time,omitempty" mapstructure:"max-connection-life-time"`
}
```

之后提供了一个 `NewMySQLOptions()` 的函数，函数的作用是返回一个新的、所有字段均为默认值的 `MySQLOptions` 对象。

以及提供了 MySQLOptions 的 `Validate()` 函数，函数的作用是验证这个 MySQLOptions 中各个字段的值是否是合理的，比如说 Addr 是不是 `Host:Port` 的类型，username 是不是空，连接池参数设定限制是不是小于 0，之类的验证。

还提供了 `DSN()` 函数，函数的作用就是返回一个 string，定义如下：

```go
// DSN return DSN from MySQLOptions.
func (o *MySQLOptions) DSN() string {
	return fmt.Sprintf(`%s:%s@tcp(%s)/%s?charset=utf8mb4&parseTime=%t&loc=%s`,
		o.Username,
		o.Password,
		o.Addr,
		o.Database,
		true,
		"Local",
	)
}
```

也就是说，根据 MySQLOptions 中各个字段的值，生成一个连接选项的 DSN。之后再使用 mysql 库中的连接方式，就可以连接上 mysql 的数据库，得到一个与 mysql 连接的 db 对象。这部分内容就是最后一个函数：`NewDB()` 做的事情。

`NewDB()` 函数的返回值是一个 `*gorm.DB` 对象，也就是 db。函数的实现中，首先调用了 `DSN()` 方法，根据 MySQLOptions 的配置，生成一个对应的连接使用的 DSN 字符串，然后调用 mysql 库，与 MySQL 建立连接，并得到 db 对象。随后根据 db 对象，创建出一个 sqlDB 对象，并用 sqlDB 对象来设定连接的最大空闲数量、连接时长等参数。最后再返回 db 值。

- db：做增删改查的时候用的数据库实体。
- sqlDB：由 db 通过 `db.DB()` 创建。设定数据库连接最大空闲数量、连接生命周期的时候会用到。

## token

token 部分的内容都是为 JWT 部分做验证的。

首先是 token 中 Config 结构体的定义：

```go
// Config 包括 token 包的配置选项
type Config struct {
	// key 用于签发和解析 token 的密钥
	key string
	// identityKey 是 token 中用户身份的键
	identityKey string
	// expiration 是签发的 token 过期时间
	expiration time.Duration
}
```

其中，key 是签发和解析 token 的密钥。也就是我们之前说的，token 的密钥在一次服务器启动的生命周期中只能有一个，并且这个是服务器必须要仔细保密的，绝对不能泄露，否则就会造成 token 令牌造假之类的问题。

identityKey，这就是一个 KV 键值对的 key 的概念。前面经过分析已经知道了，我们提供的这一套 token 认证体系中，只能保存一个键值对，也就是用户身份的键值对。这是设计的一种局限性，不过这样项目结构也比较简单。所以之后查看 token 的时候，就直接在 token 的所有键值对列表中，直接搜 `identityKey` 这个键对应的值，就是用户身份的 id 了。

`expiration` 是一个 `time.Duration` 类型的值，是用来设置 token 签发时，token 的默认过期时间的。在 golang 项目开发中，这个值一般是 2 小时。

```go
var (
	config = Config{"Rtg8BPKNEf2mB4mgvKONGPZZQSaJWNLijxR42qRgq0iBb5", "identityKey", 2 * time.Hour}
	once   sync.Once // 确保配置只被初始化一次
)
```

这里是设置了一个包级别的初始变量值。给 `key`、`identity`、`expiration` 都设置了一个初始的值。

同时，还设置了一个 once。这是因为后面这几个默认值是可以被修改的。但是在一个服务器启动的生命周期内，一个服务的 key 和 identityKey 都是固定统一的。

```go
// Init 设置包级别的配置 config，config 会用于本包后面的 token 签发和解析
func Init(key string, identityKey string, expiration time.Duration) {
	once.Do(func() {
		if key != "" {
			config.key = key // 设置密钥
		}
		if identityKey != "" {
			config.identityKey = identityKey // 设置身份键
		}
		if expiration != 0 {
			config.expiration = expiration
		}
	})
}
```

`Init()` 函数就是在导入这个包的时候，设置这个包里面的几个全局变量的值。如果传入的是空，就不设置，否则就按照传入的时候设置的值来。

---

接下来是一段 `Parse()` 代码，`Parse()` 代码的逐行的解析如下：

首先是函数的定义：

```go
func Parse(tokenString string, key string) (string, error) {
	// ...
}
```

传入的参数中，一个是 tokenString，这就是系统给用户发放的 token 令牌，那个由三部分组成的 token 令牌。key 是服务器中使用的那个不能告诉别人的私有的验证 key。

接下来是解析 token：

```go
	// 解析 token
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// 确保 token 加密算法是预期的加密算法
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.ErrSignatureInvalid
		}

		return []byte(key), nil // 返回密钥
	})
	// 解析失败
	if err != nil {
		return "", nil
	}
```

这一段主要是是调用了 jwt 的 `Parse()` 函数。函数的作用是检验 token 的加密算法是不是我们指定的 HMAC 算法。因为 token 的签名算法有很多，所以这里要检验 token 的签名算法是不是某一种。如果检验的时候使用的签名算法和系统中使用的不一样，那就报错。

这个过程中要使用到用户传入的 tokenString，还有系统中的 key。token 三个组成部分中的验证部分，就是由 token 信息 + 系统中的 key 一起生成的。

这一步结束之后，那就说明了 token 是合法的了，接下来就是解析 token 中都含有什么键值对：

```go
	var identityValue string
	// 如果解析成功，从 token 中取出 token 的主题
	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		if value, exists := claims[config.identityKey]; exists {
			if identity, valid := value.(string); valid {
				identityValue = identity
			}
		}
	}
	if identityValue == "" {
		return "", jwt.ErrSignatureInvalid
	}

	return identityValue, nil
```

上面的 `jwt.Parse()` 方法返回的是一个 `*jwt.Token` 类型的结构体。之后我们从这个结构体中去取数据。比如说我们在 token 令牌中使用的是 `"user" -> "toby"` 这个键值对吧。

那么首先就是将 `jwt.Cliams` 断言为 `jwt.MapClaims` 这种结构体，这其实就是一个 `map[string]interface{}` 的类型。之后假设这里我们的 `config.identity` 这个值就是 `"user"`，也就是从这个 map 中去取一个 `user` 对应的值，并将值保存在 value 中。

此时因为原本 map 的 value 类型定义的是 `interface{}` 泛型，所以这里我们再将它断言为 `string` 类型。如果确实可以断言为 `string` 类型，说明是可以的。

最后需要确保我们得到的 `identityValue` 不是一个空字符串。如果是一个空字符串，就说明我们 token 中并没有存这个键值对，或者是这个键值对的 value 就是一个控制，那么认证就无法通过。此时会返回签名不合法的错误。

如果上述的检验都通过了，那就说明这是一个合法的类型。返回我们系统中唯一 `identityKey` 对应的 `identityValue`。

---

接下来是 `ParseRequest()` 函数。从一个 gin 的 context 中取出 Request 部分，然后从 Request 中取出请求的令牌：

```go
// ParseRequest 从请求头中获取令牌，并将其传递给 Parse 函数以解析令牌
func ParseRequest(c *gin.Context) (string, error) {
	header := c.Request.Header.Get("Authorization")

	if len(header) == 0 {
		return "", errors.New("the length of the `Authorization` header is zero") // 返回错误
	}

	var token string
	// 从请求头中取出 token
	fmt.Sscanf(header, "Bearer %s", &token)

	return Parse(token, config.key)
}
```

首先从 gin 的 context 中取出 Request 部分。因为后面我们访问的时候，如果使用 token 令牌的话，大概是使用：

```go
curl -X POST -H 'Authorization: Bearer ${token}' 127.0.0.1:6666
```

这样的方式的。也就是说 token 令牌的内容是在请求的 Header 中的。之后使用 `c.Request.Header.Get("Authorization")` 就可以得到 Header 中 `Authorization` 部分的内容，也就是 header 的内容就是 `Bearer: ${token}`。其中的 `Bearer` 表示身份验证的类型，也是最常用的一种方式。还有一些其他的方式，比如说 `Basic`、`Digest` 之类的类型，但是这些都比较少见。

之后再通过一个 `fmt.Sscanf()` 的方式，去除其中的 `Bearer` 部分，取出真实的 token 字符串，然后就可以传给 `Parse()` 函数了，这个函数我们在上面刚分析完。

---

最后是一个签发 token 的函数：`Sign()` 函数。

```go
// Sign 使用 jwtSecret 签发 token，token 的 claims 中会存放传入的 subject
func Sign(identityKey string) (string, time.Time, error) {
	// 计算过期时间
	expireAt := time.Now().Add(config.expiration)

	// Token 的内容
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		config.identityKey: identityKey,
		"nbf":              time.Now().Unix(), // token 生效时间
		"iat":              time.Now().Unix(), // token 签发时间
		"exp":              expireAt.Unix(),   // token 过期时间
	})
	if config.key == "" {
		return "", time.Time{}, jwt.ErrInvalidKey
	}

	// 签发 token
	tokenString, err := token.SignedString([]byte(config.key))
	if err != nil {
		return "", time.Time{}, err
	}

	return tokenString, expireAt, nil // 返回 token 字符串、过期时间和错误
}
```

我们知道 token 是由三部分组成的，分别是 token 的 header 部分、payload 部分和 signature 部分。一般来说，header 部分存的都是一些很宏观的信息，业务中几乎不会涉及，比如说：

```go
{
  "alg": "HS256",
  "typ": "JWT"
}
```

这里表示使用的是 HS256 的签名算法，并且 token 类型是 JWT 类型的。

那么在签名函数中，`jwt.MapClaims` 中保存的部分，比如说 `identityKey`、`iat`、`exp` 之类的信息，都是保存在 payload 中的。

之后就是我们提供好 token 使用的算法、token 中要保存的负载部分、加上我们服务器中使用的 key，就可以得出最后的 token 三元组了。

## version

说实话当时看 version 部分的代码是感觉做抽象的。其中构建的各个变量、函数错综复杂，让我一时间摸不着头脑。

首先先看其中的 `version.go` 文件。这里首先是定义了几个包级别的全局变量：

```go
var (
	gitVersion   = "v0.0.0-master+$Format:%H$"
	gitCommit    = "$Format:%H$"
	gitTreeState = ""
	buildDate    = "1970-01-01T00:00:00Z"
)
```

这里的值都只是做个样子，没有实际的意义，作用就是告诉使用者，时候给这几个变量填充数据的时候，都使用哪些值来填充数据。

实际上，在编译程序的时候，在 `build.sh` 中提到：

```bash
# 设置 VERSION_PACKAGE
VERSION_PACKAGE=github.com/TobyIcetea/fastgo/pkg/version

# 设置 VERSION
if [[ -z "${VERSION}" ]];then
  VERSION=$(git describe --tags --always --match='v*')
fi

# 设置 GIT_COMMIT
GIT_COMMIT=$(git rev-parse HEAD)

# 设置 GIT_TREE_STATE
GIT_TREE_STATE="dirty"
is_clean=$(shell git status --porcelain 2>/dev/null)
if [[ -z ${is_clean} ]];then
  GIT_TREE_STATE="clean"
fi

# 将这几个值直接编译到可执行程序的变量中
GO_LDFLAGS="-X ${VERSION_PACKAGE}.gitVersion=${VERSION} \
  -X ${VERSION_PACKAGE}.gitCommit=${GIT_COMMIT} \
  -X ${VERSION_PACKAGE}.gitTreeState=${GIT_TREE_STATE} \
  -X ${VERSION_PACKAGE}.buildDate=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# 编译
go build -ldflags "${GO_LDFLAGS}" ...
```

所以说上面提到的几个包级别的变量，在代码中没有赋值的操作，赋值的操作都是在编译的时候通过参数直接写进去的。

---

在有了上面几个变量之后，现在我们定义一个版本信息 `Info` 的结构体：

```go
// Info 是包含版本信息的结构体
type Info struct {
	GitVersion   string `json:"gitVesion"`
	GitCommit    string `json:"gitCommit"`
	GitTreeState string `json:"gitTreeState"`
	BuildDate    string `json:"buildDate"`
	GoVersion    string `json:"goVersion"`
	Compiler     string `json:"compiler"`
	Platform     string `json:"platform"`
}
```

然后提供一个创建 Info 的方法。这里叫做 `Get()` 方法，其实叫做 `NewInfo()` 之类的名字可能还会更好理解：

```go
// Get 根据包中的变量，获取一个新的 Info 对象
func Get() Info {
	return Info{
		GitVersion:   gitVersion,
		GitCommit:    gitCommit,
		GitTreeState: gitTreeState,
		BuildDate:    buildDate,
		GoVersion:    runtime.Version(),
		Compiler:     runtime.Compiler,
		Platform:     fmt.Sprintf("%s/%s", runtime.GOOS, runtime.GOARCH),
	}
}
```

`Get()` 方法返回了一个 `Info` 的对象，其中的几个跟版本相关的变量，都直接使用包级别的，我们在编译的时候设置好的。还有 GoVersion 之类的字段，就使用 runtime 包中提供的 Golang 版本信息。

除此之外，`version.go` 中还提供了几个不同的方法，都是 Info 结构体中的字段方法：

- `String() string`
- `ToJSON() string`
- `Text() string`

几个方法都是 Info 结构体中的字段方法，而且都是返回一个可以直接打印的 string 字符串。其实区别就是简单的以不同方式打印出 `Info` 结构体。

---

之后我们看 flag.go 文件中的代码。

首先在主函数中出现的一个地方是，对 cmd 的持久性绑定 flag，加上可以识别 verison 的功能：

```go
version.AddFlags(cmd.PersistentFlags())
```

其中 version 包中，对 `AddFlags()` 的定义为：

```go
func AddFlags(fs *flag.FlagSet) {
	fs.AddFlag(flag.Lookup(versionFlagName))
}

// fplag 中对 Lookup() 方法的定义：
// Lookup() 的作用就是将一个 string 转换为 *Flag
func Lookup(name string) *Flag {
	return CommandLine.Lookup(name)
}
```

之后主函数中就调用了方法 `PrintAndExitIfRequested()`：

```go
var versionFlag = Version(versionFlagName, VersionNotSet, "Print version information and quit")

func PrintAndExitIfRequested() {
	// 检查版本标志的值并打印相应的信息
	switch *versionFlag {
	case VersionRaw:
		fmt.Printf("%s\n", Get().Text())
		os.Exit(0)
	case VersionEnabled:
		fmt.Printf("%s\n", Get().String())
		os.Exit(0)
	}
}
```

意思就是 version 包中有一个全局变量叫做 `versionFlag`，然后通过包中的 `Version` 等函数，给这个全局变量绑定了一些 flag 的参数。

如果没有在命令行设置，这个参数的默认值就是 `VersionNotSet`，这是这个包中定义的一些常量。或者是如果在命令行中调用的时候制定了 `version` 或者 `version=raw` 之类的，就表示设置了参数，之后就根据打印版本的级别打印对应的版本即可。

这里主要难理解的地方，是前面定义了很多的函数，对 `versionValue` 定义了很多的 `IsBoolFlag()`、`Get()`、`Set()` 这样的函数，但是作用比较抽象，后面也从来没使用过。后来才发现，这些就是一些接口函数，都是接口中在使用的。就像是如果要创建一个 heap 堆，需要自己实现很多的排序规则等的接口一样。抛开这些函数先不管，其余的参数绑定的部分还不算很难懂。

虽然仍然比较绕，不过没关系，这部分代码在一个完整的项目中也就顶多出现一次。

## 总结

这部分首先给出了后端数据库数据类型 User 和 Post 的业务有好的结构体定义，方便业务中对这几种类型进行处理。之后在 auth 中给出了将明文编码为密文，以及验证明文和密文是否一致的方法。options 中给出了配置、连接 mysql 的基本写法。token 部分提供认证的方法，其中的 api 可以签名 token、从 token 中拿数据等。最后的 version 可以在一个项目中绑定 version 命令行选项，并打印不同的版本信息。

这部分包都是比较通用的包，并不只是这个项目可以用，而是很多项目都有会验证密码、连接 mysql、签名 token 的需求。





















