# cmd 部分

## 定义 cmd 与配置的映射

首先可以在 `cmd/fg-apiserver` 中找到 `main.go` 入口文件，也就是说整个项目的入口就是在这里。

观察项目的目录树，可以发现，项目的根目录中，有三个大的文件夹：

- `cmd`
- `internal`
- `pkg`

一般来说，他们的作用分别是：

| 文件夹     | 作用                                                         |
| ---------- | ------------------------------------------------------------ |
| `cmd`      | 项目的可执行文件的入口。比如说 main.go 就存放在这里，一些命令行的解析也在这里。也就是说这里属于项目的外围代码。 |
| `internal` | 项目的内部处理的代码。其实其中也是一些包，但是这些包我们希望就这个项目独有，外部不可见。 |
| `pkg`      | 其中是一些 pkg，这些 pkg 中的处理逻辑偏通用，本项目可以使用，其他的项目也可以直接拿来用，因为逻辑比较通用。比如说认证部分的代码，version 部分的代码等。 |

所以说可以从这里找到 main.go 文件。

之后看 `main.go` 文件的内容：

```go
import (
	"os"

	"github.com/TobyIcetea/fastgo/cmd/fg-apiserver/app"
	_ "go.uber.org/automaxprocs"
)

func main() {
	// 创建 Go 极速项目
	command := app.NewFastGoCommand()

	// 执行命令并处理错误
	if err := command.Execute(); err != nil {
		// 如果发生错误，则退出程序
		// 返回退出码，可以使其他程序（例如 bash 脚本）根据退出码来判断服务运行状态
		os.Exit(1)
	}
}
```

其中导入 uber 的 `automaxprocs` 是为了让项目能够自动识别出来环境中的 CPU 的数量，即便是在容器中也能正常工作。

然后我们首先看 `app.NewFastGoCommand()` 中说了什么：

```go
// NewFastGoCommand 创建一个 *cobra.Command 对象，用于启动应用程序
func NewFastGoCommand() *cobra.Command {
	// 创建默认的应用命令行选项
	opts := options.NewServerOptions()

	cmd := &cobra.Command{
		// 指定命令的名字，该名字会出现在帮助信息中
		Use: "fg-apiserver",
		// 命令的简短描述
		Short: "A very lightweight full go project",
		Long: `A very lightweight full go project, designed to help beginners quickly
		learn Go project development.`,
		// 命令出错时，不打印帮助信息。设置为 true 可以确保命令出错时一眼就能看到错误信息
		SilenceUsage: true,
		// 指定调用 cmd.Execute() 时，执行的 Run 函数
		RunE: func(cmd *cobra.Command, args []string) error {
			return run(opts)
		},
		// 设置命令运行时的参数检查，不需要指定命令行参数。例如：./fg-apiserver param1 param2
		Args: cobra.NoArgs,
	}

	// 初始化配置函数，在每个命令运行时调用
	cobra.OnInitialize(onInitialize)

	// cobra 支持持久性绑定（PersistentFlag），该标志可用于它所分配的命令及该命令下的每个子命令
	// 推荐使用配置文件来配置应用，便于管理配置项
	cmd.PersistentFlags().StringVarP(&configFile, "config", "c", filePath(), "Path to the fg-apiserver configuration file.")

	version.AddFlags(cmd.PersistentFlags())

	return cmd
}
```

其中的一些定义：

```go
type ServerOptions struct {
	MySQLOptions *genericoptions.MySQLOptions `json:"mysql" mapstructure:"mysql"`
	Addr         string                       `json:"addr" mapstructure:"addr"`
	// JWTKey 定义 JWT 密钥
	JWTKey string `json:"jwt-key" mapstructure:"jwt-key"`
	// Expiration 定义 JWT Token 的过期时间
	Expiration time.Duration `json:"expiration" mapstructure:"expiration"`
}
```

也就是说，这里我们是创建了一个 cobra 包中的 cmd 对象，之后通过 `onInitialize`、`PersistentFlags()` 之类的函数，给这个 `cmd` 对象添加了一些配置，比如说读取配置文件的时候去哪里找配置文件、应该去识别哪些参数等。其中还有一个 `version.AddFlags`，这也是一些解析参数的配置，是给 cmd 绑定了 version 相关的参数的解析。

同时我们指定了 `cmd` 中的一个 `runE` 字段，这个字段是指定一个函数，之后执行 `cmd.Execute()` 的时候，会去执行这个函数。然后我们在这个字段中指定了 `run()` 函数。也就是说，当我们后面执行 `Execute()` 的时候，函数会跑去执行这里的 `run()` 函数。

`run()` 函数的定义如下：

```go
// run 是主运行逻辑，负责初始化日志、解析配置、校验选项并启动服务器。
func run(opts *options.ServerOptions) error {
	// 如果传入 --version，则打印版本信息并退出
	version.PrintAndExitIfRequested()

	// 初始化 slog
	initLog()

	// 将 viper 中的配置解析到 opts
	if err := viper.Unmarshal(opts); err != nil {
		return err
	}

	// 校验命令行选项
	if err := opts.Validate(); err != nil {
		return err
	}

	// 获取应用配置
	// 将命令行选项和应用配置分开，可以更加灵活的处理 2 种不同类型的配置
	cfg, err := opts.Config()
	if err != nil {
		return err
	}

	// 创建服务器实例
	server, err := cfg.NewServer()
	if err != nil {
		return err
	}

	// 启动服务器
	return server.Run()
}
```

首先是检验是不是传入了 version 选项，如果是的话，就直接退出。接下来通过 `initLog()` 定义了一些 `slog` 包的默认行为，比如说之后输出的时候都使用 json 方式输出什么的。

我们在这个函数中传入的类型是一个 ServerOptions 类型的对象，上面已经说过这个结构体的定义。这里我们创建初始的 opts 的时候，是通过 `NewServerOptions()` 创建了一个新的、空的、默认的对象：

```go
// NewServerOptions 创建带有默认值的 ServerOptions 实例
func NewServerOptions() *ServerOptions {
	return &ServerOptions{
		MySQLOptions: genericoptions.NewMySQLOptions(),
		Addr:         "0.0.0.0:6666",
		Expiration:   time.Hour * 2,
	}
}
```

之后通过 `viper.Unmarshal()` 将 viper 中的配置，投影到这个实际的对象中。这样这个实际的对象中就有数据了。其中 viper 中的数据也是通过前面一个函数将配置映射进来的。viper 读取的配置文件大概如下：

```yaml
# JWT 签发密钥
jwt-key: Rtg8BPKNEf2mB4mgvKONGPZZQSaJWNLijxR42qRgq0iBb5
# JWT Token 过期时间
expiration: 1000h

# MySQL 数据库相关配置
mysql:
  # MySQL 机器 IP 和端口，默认 127.0.0.1:3306
  addr: 127.0.0.1:3306
  # MySQL 用户名（建议授权最小权限集）
  username: fastgo
  # ....
```

那么 viper 怎么知道如何去将一个配置项正确映射到结构体的哪一个字段中的呢？这是通过结构体中的 `mapstructure` 反射标签定义的。

例如 ServerOptions 中就有：

```go
type ServerOptions struct {
	MySQLOptions *genericoptions.MySQLOptions `json:"mysql" mapstructure:"mysql"`
	Addr         string                       `json:"addr" mapstructure:"addr"`
	// JWTKey 定义 JWT 密钥
	JWTKey string `json:"jwt-key" mapstructure:"jwt-key"`
	// Expiration 定义 JWT Token 的过期时间
	Expiration time.Duration `json:"expiration" mapstructure:"expiration"`
}
```

其中的 `mapstructure:"mysql"` 就表示将配置的 yaml 文件中的 `mysql` 映射到 `MySQLOptions` 这个字段上。

而 `MySQLOptions` 的定义中：

```go
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

又有 `mapstructure:"addr"` 之类的字段。所以说之后配置的 yaml 中，就将 `mysql.addr` 给映射到结构体中的 `MySQLOptions.Addr` 上了。其他的配置也是类似的。

所以说在 `run()` 逻辑中，到这里我们就可以有了一个 `opts` 对象，类型是 `ServerOptions`。

## run() 的后续处理

之后首先是做了一个 `opts.Validate()` 的操作。这部分是做了一个配置的检验：

```go
// Validate 校验 ServerOptions 中的选项是否合法
func (o *ServerOptions) Validate() error {
	// 验证 mysql 配置是否正确
	if err := o.MySQLOptions.Validate(); err != nil {
		return err
	}
    // ...
}
```

随后接下来是这样一段代码：

```go
	// 获取应用配置
	// 将命令行选项和应用配置分开，可以更加灵活的处理 2 种不同类型的配置
	cfg, err := opts.Config()
	if err != nil {
		return err
	}
```

这段代码是调用了 opts 的 `Config()` 函数，就是通过 opts 去生成了一个 cfg。而 `Config` 的定义如下：

```go
// Config 基于 ServerOptions 构建 apiserver.Config
func (o *ServerOptions) Config() (*apiserver.Config, error) {
	return &apiserver.Config{
		MySQLOptions: o.MySQLOptions,
		Addr:         o.Addr,
		JWTKey:       o.JWTKey,
		Expiration:   o.Expiration,
	}, nil
}
```

这里的 Config 的定义是在 apiserver 中的，可以看到 `Config` 也是四个字段，apiserver 中使用的 Config 的结构是和 `ServerOptions` 几乎一模一样的。我觉得这里或许只是在不同地方有两个一样的配置？比如说命令行这边一个，apiserver 内部也有一个一样的。因为 apiserver 内部也不好完全使用 cmd 这里的配置。不过要是完全合起来呢，似乎也不是不行。

反正这里记住：**`apiserver` 的 `Config` 和 `cmd` 的 `ServerOptions` 是一模一样的结构**。

```go
// Config 配置结构体，用于存储应用相关的配置
// 不用 viper.Get，是因为这种方式能更加清晰的知道应用提供了哪些配置项。
type Config struct {
	MySQLOptions *genericoptions.MySQLOptions
	Addr         string
	JWTKey       string
	Expiration   time.Duration
}
```

> 硬要说不同的话，其实 ServerOptions 中的代码还要比 Options 中多一点，就是多一点反射的解释。但是这个也确实是解释一次就够了，因为解析配置文件的部分都在 cmd 包中，之后只需要根据 cmd 中对 ServerOptions 解析的结果，再复制一份作为 apiserver 中的 Config 就行了。

## 根据 Config 创建 Server 实例

`run()` 中根据如下代码创建了 Server 的实例：

```go
	// 创建服务器实例
	server, err := cfg.NewServer()
	if err != nil {
		return err
	}
```

这里就是根据上面创建出来的 apiserver 中的 `Config` 创建了一个新的 Server。

Server 也是定义在 `apiserver` 包中的，定义为：

```go
// Server 定义一个服务器结构类型
type Server struct {
	cfg *Config
	srv *http.Server
}
```

其中包含两个内容，一个是 `Config`，其中的内容就是我们上面定义的，另一个是 `http.Server` 这个标准库中的 `Server` 结构体。

所以 `Config.NewServer()` 实际上就是根据一个 `Config` 去创建了一个新的 `Server` 对象：

> 这里其实就像是套娃🪆，首先我们直接根据 yaml 配置文件中的配置，将配置映射到了一个 `ServerOptions` 结构体中。但是这个结构体是用在 cmd 包中的，我们又根据这个结构创建了一个一模一样的 `Config` 放在 `apiserver` 中。之后我们又根据这个 `Config`，作为一个字段，构成了一个新的 `Server`。也就是：
>
> `ServerOptions` => `Config` => `Server`

```go
// NewServer 根据配置创建服务器
func (cfg *Config) NewServer() (*Server, error) {
	// 初始化 token 包的签名密钥、认证 key 及 token 默认过期时间
	token.Init(cfg.JWTKey, known.XUserID, cfg.Expiration)

	// 创建 Gin 引擎
	engine := gin.New()

	// gin.Recovery() 中间件，用来捕获任何 panic，并恢复
	mws := []gin.HandlerFunc{gin.Recovery(), mw.NoCache, mw.Cors, mw.RequestID()}
	engine.Use(mws...)

	// 初始化数据库连接
	db, err := cfg.MySQLOptions.NewDB()
	if err != nil {
		return nil, err
	}
	store := store.NewStore(db)

	cfg.InstallRESTAPI(engine, store)

	// 创建 HTTP Server 实例
	httpsrv := &http.Server{Addr: cfg.Addr, Handler: engine}

	return &Server{cfg: cfg, srv: httpsrv}, nil
}
```

在 `NewServer()` 函数中，首先做了一个 token 的 `Init()` 工作。因为我们知道，在 JWT 验证机制中，一个 Server 在一次提供 token 服务的过程中，自己要保留一个 key，并且这个 key 是不能告诉别人的、是全局唯一的。所以这里的 `token.Init()` 就是做了一个设置全局的操作。其中 `cfg.JWTKey` 和 `cfg.Expiration` 分别代表全局的 `key` 和过期时间，这部分是在 `Config` 对象中的。`known.XUserID` 的值是 `"x-user-id"`，其实就是说之后拿着这个 token，通过这个 `"x-user-id"` 来找对应的 `value`。实际上这里是限制死了，让 token 中只能保存 `x-user-id` 这一组键值对。

```go
	// 创建 Gin 引擎
	engine := gin.New()
```

这一部分创建了一个 `gin` 的 `engine` 引擎。这一部分我们在做简单的 demo 的时候，就直接管他叫 `router` 了，比如说 `router := gin.Default()` 这样的。但是实际上是在后端中，`gin` 的定义中，这个结构体的名字叫做 `Engine`，它不光具有 `router` 的功能，还具有配置 `middleware` 的功能，还可以启动服务器后端，之类的很多功能。

所以后面的这部分代码：

```go
	// gin.Recovery() 中间件，用来捕获任何 panic，并恢复
	mws := []gin.HandlerFunc{gin.Recovery(), mw.NoCache, mw.Cors, mw.RequestID()}
	engine.Use(mws...)
```

就是将一些中间件绑定到了 `gin` 的 `engine` 上。之后这个 `gin.Engine` 就具有了：

- `Recovery()`：发生 `panic` 的时候自己恢复
- `NoCache`：禁止客户端缓存 HTTP 请求的返回结果
- `Cors`：用来 `OPTIONS` 请求的返回头，然后结束请求
- `RequestID()`：在每一个 `http` 请求中，给 `response` 中加入一个 `x-request-id` 的键值对

这几个中间件的功能。

## 初始化数据库连接

首先是这部分代码：

```go
	// 初始化数据库连接
	db, err := cfg.MySQLOptions.NewDB()
	if err != nil {
		return nil, err
	}
```

`MySQLOptions` 是 `apiserver` 的 `Config` 中的一个字段，也是一个结构体。具体一下，`MySQLOptions` 的定义如下：

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

其实就是 MySQL 的连接选项。同时这部分还是和配置部分绑定比较紧密的，后面都做了 `mapstructure` 的映射。也就是说，之后这个结构体的值，大概就是前面的 yaml 配置文件中的内容：

```yaml
# MySQL 数据库相关配置
mysql:
  # MySQL 机器 IP 和端口，默认 127.0.0.1:3306
  addr: 127.0.0.1:3306
  # MySQL 用户名（建议授权最小权限集）
  username: fastgo
  # MySQL 用户密码
  password: fastgo1234
  # fastgp 系统所用的数据库名
  database: fastgo
  # MySQL 最大空闲连接数，默认 100
  max-idle-connections: 100
  # MySQL 最大打开的连接数，默认 100
  max-open-connections: 100
  # 空闲连接最大存活时间，默认 10s
  max-connections-life-time: 10s
```

同时在 `NewServer()` 这里，我们是调用了 `NewDB()` 函数。这里函数的定义如下：

```go
// NewDB create mysql store with the given config.
func (o *MySQLOptions) NewDB() (*gorm.DB, error) {
	db, err := gorm.Open(mysql.Open(o.DSN()), &gorm.Config{
		// PrepareStmt executes the given query in cached statement.
		// This can improve performance.
		PrepareStmt: true,
	})
	if err != nil {
		return nil, err
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	// SetMaxOpenConns sets the maximum number of open connections to the database.
	sqlDB.SetMaxOpenConns(o.MaxOpenConnections)

	// SetConnMaxLifetime sets the maximum amount of time a connection may be reused.
	sqlDB.SetConnMaxLifetime(o.MaxConnectionLifeTime)

	// SetMaxIdleConns sets the maximum number of connections in the idle connection pool.
	sqlDB.SetMaxIdleConns(o.MaxIdleConnections)

	return db, nil
}
```

首先是使用了一个 `gorm.Open()` 函数，其中传入了 `DSN()`，这是先前就定义好的一个函数，作用是返回连接 mysql 用的一个描述配置的字符串。这是 mysql 连接部分的知识，`mysql` 库中的作用也就是创建和 MySQL 的连接，后续的操作都是在 `db` 中进行的。

其中还提到了一个 `sqlDB`，这是我们通过 `db.DB()` 新创建出来的一个变量。这个 `sqlDB` 和前面的 `db` 的作用是不同的。具体来说：

- `sqlDB` 主要是做一些宏观的设置，比如说设置 mysql 连接池的最大数量、最大的空闲时间等。
- `db` 才是干活儿的主体，增删改查的操作都是在 `db` 上去做的。同时，一般不推荐 `db` 频繁的打开和关闭，而是在一次生命周期中，就使用一个 db，等项目终止之后，再去关闭这个 `db`。

## 根据 db 创建 store

紧跟着上面 `db` 的代码之后，是一个创建 `store` 的代码：

```go
	store := store.NewStore(db)
```

这种代码前面已经见过和多次了，就是 `db` 作为 `store` 中的一个字段，并且还是一个主要的字段（其他的字段都可以自动生成），这样就可以根据 db 去创建一个 `store`。接下来看 `NewStore()` 的定义：

```go
// NewStore 创建一个 IStore 类型的实例
func NewStore(db *gorm.DB) *datastore {
	// 确保 S 只被初始化一次
	once.Do(func() {
		S = &datastore{db}
	})

	return S
}
```

确实是传入一个 `*gorm.DB` 类型的数据，之后返回一个 `*datastore` 类型的数据。同时其中还加入了一个 `once.Do()` 方法，确保这个 datastore 只会被初始化一次。这说明这里的这个 store 的生命周期等于整个项目的周期，整个项目中一直会用到这个 store，同时这个 store 也只会有一个。

`datastore` 类型的定义如下：

```go
// datastore 是 IStore 的具体实现
type datastore struct {
	core *gorm.DB
}
```

不出所料，其中的字段只有一个，也就是我们在构造函数中传入的 `*gorm.DB` 类型的数据。看来 datastore 类型也是用来操作 `db` 的，这里不过是在 db 上又套了一层封装。之后操作 db 的时候就可以使用 `store.core.Create()` 之类的方法来操作了。

这里的 datastore 其实并没有这么简单，还有什么 IStore 接口的实现，还有很多其他的函数，不过这些我们之后放到另一个文件中分析。

## 注册 API 路由

在创建完 db 并且根据 db 创建了一个 store 之后，下面的一行代码是：

```go
	cfg.InstallRESTAPI(engine, store)
```

这个 `InstallRESTAPI(engine, store)` 函数就是在这个 `apiserver` 的 `server.go` 文件中定义的，函数的定义如下：

```go
// 注册 API 路由。路由的路径和 HTTP 方法，严格遵循 REST 规范
func (cfg *Config) InstallRESTAPI(engine *gin.Engine, store store.IStore) {
	// 注册 404 Handler
	engine.NoRoute(func(c *gin.Context) {
		core.WriteResponse(c, nil, errorsx.ErrNotFound.WithMessage("Page not found"))
	})

	// 注册 /healthz handler
	engine.GET("/healthz", func(c *gin.Context) {
		core.WriteResponse(c, map[string]string{"status": "ok"}, nil)
	})

	// 创建核心业务处理器
	handler := handler.NewHandler(biz.NewBiz(store), validation.NewValidator(store))

	// 注册用户登录和令牌刷新接口。这两个接口比较简单，所以没有 API 版本
	engine.POST("/login", handler.Login)
	// 注意：认证中间件要在 handler.RefreshToken 之前加载
	engine.PUT("/refresh-token", mw.Authn(), handler.RefreshToken)

	authMiddlewares := []gin.HandlerFunc{mw.Authn()}

	v1 := engine.Group("/v1")
	{
		// 用户相关路由
		userv1 := v1.Group("/users")
		{
			// 创建用户。这里要注意：创建用户是不用进行认证和授权的
			userv1.POST("", handler.CreateUser)
			userv1.Use(authMiddlewares...)
			userv1.PUT(":userID/change-password", handler.ChangePassword) // 修改用户密码
			userv1.PUT(":userID", handler.UpdateUser)                     // 更新用户信息
			userv1.DELETE(":userID", handler.DeleteUser)                  // 删除用户
			userv1.GET(":userID", handler.GetUser)                        // 查询用户详情
			userv1.GET("", handler.ListUser)                              // 查询用户列表
		}

		// 博客相关路由
		postv1 := v1.Group("/posts", authMiddlewares...)
		{
			postv1.POST("", handler.CreatePost)       // 创建博客
			postv1.PUT(":postID", handler.UpdatePost) // 更新博客
			postv1.DELETE("", handler.DeletePost)     // 删除博客
			postv1.GET(":postID", handler.GetPost)    // 查询博客详情
			postv1.GET("", handler.ListPost)          // 查询博客列表
		}
	}
}
```

首先就是注册了几个 API 的路由，比如说 `/healthz` 检查路由，还有 `Noroute` 找不到的路由。其中注册的方法就是通过 gin 框架中，前面创建的 engine 来创建路由。其中，路由的处理方式，我们在这里都定义为执行一个函数。函数的写法都是：`core.WriteResponse(...)`。

前面说到，我们创建了一个 db，之后又通过 db 创建了一个 `store`，而这个 `store` 中就只有一个字段，字段的名字就叫做 `core`，类型是 `*gorm.DB`。

但是这里的 `core` 可不是说 store 中的那个 core，具体来说跟 store 中那个 core 没有关系。这里的 core 是我们定义的一个包，其中对 `WriteResponse()` 函数的定义如下：

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

这个函数传入的参数，首先是 `c *gin.Context`，这是肯定的，`gin` 的 `Context` 上下文中，包含了本次请求和返回的所有信息，所以只要是和请求或者返回相关的事务，都要在 `c` 中去做。第二个参数是 `data any`，表示返回的时候，需要额外带的信息是什么。最后的 err 用来判断是不是要返回一些错误。

观察函数体可以发现，不管 err 是不是空的，最后都会执行一个 `c.JSON()`，也就是说本次请求就终止了，直接返回一个 JSON 结构体给客户端。

具体到 `NoRouter` 和 `/healthz` 这样的路由中，这种设计是合理的。如果碰到没有定义过的路由，就直接返回不存在；如果碰到 `/healthz` 这样的健康检查路由，就直接返回健康，或者是不健康，不做后续的其他处理。

之后这个函数中做的操作就是创建了一个 `Handler`，然后在 Handler 中继续去创建了很多的路由，也就是访问每一个路由的时候，都分别使用什么函数来进行处理。其中还创建了 Biz、Validation 等数据类型，其实这两个数据类型都是对 store 做了又一层的数据封装。这部分知识之后在另一个文件中再详细研究。

注册完所有的 API 之后，就返回一个最终的服务器：

```go
	// 创建 HTTP Server 实例
	httpsrv := &http.Server{Addr: cfg.Addr, Handler: engine}

	return &Server{cfg: cfg, srv: httpsrv}, nil
```

这里的服务器使用了标准的 http 包中的服务器，其中服务器的 Handler 部分就使用我们上面创建的 engine。这里的 `http.Handler` 类型是一个接口，接口的要求是实现 `ServeHTTP()` 方法，而 gin 框架中的 `Engine` 类型就实现了这个方法。

## 启动服务器

在前面执行完了 `cfg.NewServer()` 之后，我们就得到了一个 `apiserver` 中的 Server 类型的数据。

前面说到，整个程序执行函数的流程就是主要执行的函数一直在变，现在是执行了 `cmd` 的 `Execute()` 函数之后，来到了自定义的一个 `run()` 函数。`run()` 函数的最后一行是：

```go
	// 启动服务器
	return server.Run()
```

所以这里我们再转到 `server.Run()` 函数中看看情况：

```go
// Run 运行应用
func (s *Server) Run() error {
	// 运行 http 服务器
	// 打印一条日志，用来提示 HTTP 服务已经起来，方便排除故障
	slog.Info("Start to listening the incoming requests on http address", "addr", s.cfg.Addr)

	go func() {
		if err := s.srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			slog.Error(err.Error())
			os.Exit(1)
		}
	}()

	// 创建一个 os.Signal 类型的 channel，用于接收系统信号
	quit := make(chan os.Signal, 1)
	// 当执行 kill 命令时（不带参数），默认会发送 syscall.SIGTERM 信号
	// 当使用 kill -2 命令会发送 syscall.SIGINT 信号（例如按 Ctrl + C 触发）
	// 使用 kill -9 命令会发送 syscall.SIGKILL 信号，但 SIGKILL 信号无法被捕获，因此无需监听和处理
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	// 阻塞程序，等待从 quit channel 中接收到信号
	<-quit

	slog.Info("Shutting down server ...")

	// 优雅关闭服务
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 先关闭依赖的服务，再关闭被依赖的服务
	// 10 秒内优雅关闭服务（将未处理完的请求处理完再关闭服务），超过 10 秒就超时退出
	if err := s.srv.Shutdown(ctx); err != nil {
		slog.Error("Insecure Server forced to shutdown", "err", err)
		return err
	}

	slog.Info("Server exited")

	return nil
}
```

这个函数首先做的第一件事，通过 slog 打印一条信息，说明服务器现在已经启动了。

随后执行服务器的 `ListenAndServe()` 函数，这是 golang 中 http 标准库的函数，表示服务器这里就开始执行了，去监听指定的端口，监听到访问的请求之后，再对这个请求做 Response。这里打开服务器，让服务器运行，是通过一个 goroutine 去启动的，这样可以不影响之后的进程。

同时，服务器的启动，我们还捕捉了一下 `ListenAndServe()` 函数的返回值，返回的 err 中会带有出错的原因。如果函数停止执行的原因不是我们主动关闭服务器，就会报错。

后面的处理就是创建了一个 `channel`，这个 channel 负责监听系统中的 `SIGTERM`、`SIGINT` 这两个信号，如果捕获到了这两个信号，就打印一条信息的日志，之后优雅地关闭服务。

关闭服务的方式是执行 http 标准包中 Server 类型的 `Shutdown()` 方法。同时我们还通过 `context.WithTimeout()` 创建了一个上下文，用于限制时间。如果在 10 秒钟之内，服务器的 `Shutdown()` 自己执行结束了，那就无事发生。如果没有自己执行结束，那就只能强行停止服务器。

最后打印一条日志：`Server exited`，表示服务器彻底退出。

## 总结

一开始我们创建了一个 cmd 命令行对象，创建好之后做一些初始化的操作。其实初始化的操作就是通过 viper 把 yaml 配置文件中的信息，填充到了一个对象中。

之后创建了一些 Config 对象，然后又通过 Config 创建了 Server，给 Server 添加了很多实际会用到的路由。并且在后台注册了 db 以及由 db 组成的 store，作为参数传入给一些路由的选项中，用于后期操作后端的数据库。

最后启动服务器，监听访问的请求，并且返回 Response。同时，监听退出服务器的信号。监听到退出服务器的信号之后，优雅地退出服务。







































