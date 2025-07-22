# Viper

## 介绍

Viper 是 golang 中的一个配置管理的工具。主要是管理配置文件的。

它是一个 golang 与 json、yaml、toml 之类格式的配置文件进行交互的利器。

主要特点有：

- 支持的格式多。比如 json、yaml、toml 等文件。
- 配置文件可以有多个来源。比如说除了从文件中获取，这个配置还可以来自环境变量、命令行显式标志等。
- 运行的程序中，读取的配置可以跟随配置文件的变化实时变化。

## 安装

```go
go get github.com/spf13/viper
```

## QuickStart

1. 写好配置文件（或者环境变量）
2. 用 viper 去读取配置文件
3. 将 viper 对象转换成实际的 golang 结构体（可选）
4. 开始读配置

`config.yaml`：

```yaml
server:
  port: 8080
  env: development
  debug: true
 
database:
  host: localhost
  user: admin
  password: secret
```

`main.go`：

```go
package main

import (
	"fmt"
	"log"

	"github.com/fsnotify/fsnotify"
	"github.com/spf13/viper"
)

type Config struct {
	Server struct {
		Port  int    `mapstructure:"port"`
		Env   string `mapstructure:"env"`
		Debug bool   `mapstructure:"debug"`
	} `mapstructure:"server"`
	Database struct {
		Host     string `mapstructure:"host"`
		User     string `mapstructure:"user"`
		Password string `mapstructure:"password"`
	} `mapstructure:"database"`
}

func main() {
	// 初始化Viper实例
	v := viper.New()

	// 1. 配置文件处理
	v.SetConfigName("config") // 配置文件名 (不带扩展)
	v.SetConfigType("yaml")   // 显式指定配置格式
	v.AddConfigPath(".")      // 搜索路径

	// 2. 环境变量配置
	v.SetEnvPrefix("MYAPP") // 环境变量前缀 MYAPP_SERVER_PORT
	v.AutomaticEnv()        // 自动加载环境变量

	// 3. 读取配置文件
	if err := v.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			log.Println("Warning: config file not found, using defaults/env")
		} else {
			log.Fatal("Fatal error in config file:", err)
		}
	}

	// 4. 解析配置到结构体
	var config Config
	if err := v.Unmarshal(&config); err != nil {
		log.Fatal("Failed to unmarshal config:", err)
	}

	// 打印最终配置
	fmt.Printf("Running in [%s] mode\n", config.Server.Env)
	fmt.Printf("Server port: %d\n", config.Server.Port)
	fmt.Printf("Database host: %s\n", config.Database.Host)

	// 5. 监听配置变更（热加载）
	v.WatchConfig()
	v.OnConfigChange(func(e fsnotify.Event) {
		fmt.Println("Config changed:", e.Name)
		// 这里可以添加重新加载配置的逻辑
	})

	// （保持运行以便演示监听）
	select {}
}

```





## API 学习

### 初始化配置

| API                          | 说明                                                   |
| ---------------------------- | ------------------------------------------------------ |
| `SetConfigName(name string)` | 设置配置文件名，不带扩展名，如：`config`               |
| `SetConfigType(type string)` | 明确配置文件格式，如 `json`、`yaml`、`toml`            |
| `AddConfigPath(path string)` | 添加配置文件搜索路径（可以多次调用）                   |
| `SetConfigFile(file string)` | 直接指定配置文件的完整路径，例如直接传入 `config.json` |
| `ReadInConfig() error`       | 读取配置文件。这一步是必须要做的。                     |

第一种配置方式：

```go
// 假如说我们现在要读取当前文件夹下的 config.json
viper.SetConfigName("config")
viper.SetConfigType("yaml")
viper.AddConfigPath(".")

if err := viper.ReadInConfig(); err != nil {
    fmt.Println("读取配置文件出错", err)
}
```

第二种配置方式：

```go
// 假如说我们现在要读取当前文件夹下的 config.json
viper.SetConfigFile("config.yaml")

if err := viper.ReadInConfig(); err != nil {
    fmt.Println("读取配置文件出错", err)
}
```

两种方式是等价的。

但是其中有一个问题是，必须要加上 `viper.ReadInConfig()` 函数，否则设置的各种配置文件路径都不会生效。

### 值获取

| API                                     | 说明                          |
| --------------------------------------- | ----------------------------- |
| `Get(key string) interface{}`           | 获取任意类型的值              |
| `GetString(key string) string`          | 获取字符串类型的值            |
| `GetInt(key string) int`                | 获取 `int` 类型的值           |
| `GetBool(key string) bool`              | 获取 `bool` 类型的值          |
| `GetDuration(key string) time.Duration` | 获取 `time.Duration` 类型的值 |

其中，主要是参数中的 `(key string)` 这个位置的填写，填写方式其实就是直接按照 `item1.item2.item3` 这种方式填写就可以。

比如说对于如下的一个配置文件 `config.yaml`：

```yaml
server:
  port: 808000000
database:
  host: local
  port: 543
time:
  duration1: 6h5m30s
  duration2: 666
```

那么我们在读取的时候就可以试试：

```go
// 首先将指定配置文件路径，并读取
viper.SetConfigFile("config.yaml")
if err := viper.ReadInConfig(); err != nil {
    fmt.Println("出错", err)
}

// 打印不同类型的数据
fmt.Println(viper.GetInt("server.port"))         // 808000000
fmt.Println(viper.GetString("database.host"))    // local
fmt.Println(viper.GetDuration("time.duration1")) // 6h5m30s
fmt.Println(viper.GetDuration("time.duration2")) // 666ns
```

> 需要注意一下其中的 `Duration` 类型。标准的 `yaml` 语法中，其实是不包含 `time` 这种类型的。`yaml` 处理的时候，实际上还是会将其当作数据类型或者是字符串类型来读取。
>
> Go 的处理中，如果是数据类型，就将这个数字的单位默认设置为 `ns`。或者我们也可以直接指定 `2h3m4s` 这样格式，直接指定多少时间。

### 默认值设置

| API                                         | 说明                                                 |
| ------------------------------------------- | ---------------------------------------------------- |
| `SetDefault(key string, value interface{})` | 如果配置文件中没有配置这个类型字段的值，则使用默认值 |

使用方法：

```go
viper.SetDefault("person.name", "张三")
fmt.Println(viper.GetString("person.name"))  // 直接输出：张三
```

实际上在配置文件中并没有配置 `person.name` 这个字段，但是可以输出 `张三`。

但是，如果配置文件中设置过这个字段，那么这里的 `Default` 设置就不生效了。

### 环境变量绑定

| API                                     | 说明                         |
| --------------------------------------- | ---------------------------- |
| `AutomaticEnv()`                        | 自动匹配环境变量             |
| `BindEnv(key string, envVar ...string)` | 显示绑定某个配置键到环境变量 |
| `SetEnvPrefix(prefix, string)`          | 设置环境变量前缀             |

这里的主要是，在读取配置的时候，有时候我们想要从环境变量中去读取。这个时候我们如何去读取环境变量。

一般来说，在 Linux 中我们都习惯通过全大写 + 中间用 `_` 隔开来设置不同的环境变量。并且，为了让我们一个 APP 的环境变量能独立出来，我们会在一个 APP 的环境变量前面加上特定的标识。比如说我要设置 `viper` 的环境变量，那么我会设置：

- `VIPER_NAME`
- `VIPER_USER`
- `VIPER_PASSWORD`

其中的 `VIPER` 就是前缀。

同时也说明了一个事实，就是 `AutomativEnv()` 这个 API 是会自动转大写的。

那么有的时候，如果我们设置了一个 APP 的前缀，但是还有一些环境变量是我们并没有包含在前缀中的，这时候就可以使用 `BindEnv(key string, env string)` 去做一个手动绑定。

下面是一个这部分的演示：

```go
viper.SetEnvPrefix("APP")

viper.AutomaticEnv()

viper.BindEnv("name")
viper.BindEnv("debug", "DEBUG_MODE")

fmt.Println(viper.GetString("name"))
fmt.Println(viper.GetString("debug"))
```

此时对于 `name`，我们做了前缀的设置，所以这时候键 `name` 匹配的是系统中的环境变量 `APP_NAME`。

对于 `debug`，这是我们直接显示指定的，这时候就不受前缀的约束，设置的啥就是啥，所以匹配的是系统中 的环境变量 `DEBUG_MODE`。

此时我们运行：

```go
export APP_NAME=qqq
export DEBUG_MODE=error
go run main.go
```

程序就会输出：

```go
qqq
error
```

### 文件操作

| API                                    | 说明                         |
| -------------------------------------- | ---------------------------- |
| `MergeInConfig() error`                | 合并另一个配置文件到当前配置 |
| `WriteConfigAs(filename string) error` | 将当前配置写入到新文件       |

对于一个 `viper` 对象，可以设置多个配置文件。第一次做设置的时候，使用 `ReadInConfig()`，后续如果又来了一个新的配置，有一些其他的设置，就可以通过 `MergeInConfig()` 加入进去。

后续，如果想将此时的配置导出为一个文件，可以使用 `WriteConfigAs(filename string) error`，将配置写入为新的文件。

示例：

```go
func main() {
	v := viper.New()

	// 1. 读取基础配置 config.yaml
	v.SetConfigFile("config.yaml")
	v.ReadInConfig()

	// 2. 合并覆盖配置 override.yaml
	v.SetConfigFile("override.yaml")
	v.MergeInConfig()

	// 3. 将最终配置写入 merged.yaml
	if err := v.WriteConfigAs("merged.yaml"); err != nil {
		fmt.Println(err)
	}
}
```

其中，`config.yaml`：

```yaml
app:
  name: "MyApp"
  port: 8080
database:
  host: "localhost"
  port: 3306
```

`override.yaml`：

```yaml
app:
  port: 9090
database:
  user: "admin"
  password: "secret"
```

`merged.yaml`：

```yaml
app:
    name: MyApp
    port: 9090
database:
    host: localhost
    password: secret
    port: 3306
    user: admin
```

可以看到，对于重复的地方（`app.port`），`viper` 会使用后来的配置。对于不冲突的部分，`viper` 会取一个并集。

### 配置监听

| API                                         | 说明                                   |
| ------------------------------------------- | -------------------------------------- |
| `WatchConfig()`                             | 开启配置文件变更的监控                 |
| `OnConfigChange(f func(in fsnotify.Event))` | 每次监控到配置文件变化之后，执行的函数 |

其中 `OnConfigChange(f func(in fsnotify))` 也可以不设置，文件也会跟着变化，只不过之后变化的时候不会提醒。

示例：

```go
func main() {
	v := viper.New()
	v.SetConfigName("config")
	v.SetConfigType("yaml")
	v.AddConfigPath(".")

	v.ReadInConfig()

	// 监控配置文件变化
	v.WatchConfig()

   	// 自定义：配置文件发生变化之后，要做一些什么事儿
	v.OnConfigChange(func(e fsnotify.Event) {
		fmt.Println("Config file changed:", e.Name)
	})

	for {
		fmt.Println(v.GetString("app.name"))
		time.Sleep(1 * time.Second)
	}
}
```

输出：

```go
My
...
Config file changed: /root/goProjects/package-demo/viper-demo/config.yaml
Myaaa
...
```

### 配置反序列化

| API                             | 说明                                              |
| ------------------------------- | ------------------------------------------------- |
| `Unmarshal(rawVal interface{})` | 将一个 `viper` 对象中的内容反序列化到一个结构体中 |

其实就是将一个 `json` 序列或者说 `yaml` 序列，转换成一个实际的 `golang` 对象，方便操作。

需要注意：在做自定义的结构体的时候，每一个字段后面要加上 **`mapstructure:"port"`** 这样的反射字段。就像是 `json` 的一样。

示例如下。

`config.yaml`

```yaml
server:
  port: 8080
  timeout: 30s
database:
  host: "localhost"
  users:
    - name: "user1"
      role: "admin"
    - name: "user2"
      role: "user"
```

`main.go`

```go
package main

type ServerConfig struct {
    Port    int           `mapstructure:"port"`
    Timeout time.Duration `mapstructure:"timeout"`
}
 
type User struct {
    Name string `mapstructure:"name"`
    Role string `mapstructure:"role"`
}
 
type DatabaseConfig struct {
    Host  string `mapstructure:"host"`
    Users []User `mapstructure:"users"`
}
 
type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
}
 
func main() {
    v := viper.New()
    v.SetConfigFile("config.yaml")
    if err := v.ReadInConfig(); err != nil {
        panic(err)
    }
 
    var cfg Config
    if err := v.Unmarshal(&cfg); err != nil {
        panic(err)
    }
 
    fmt.Printf("Server Port: %d\n", cfg.Server.Port) // 输出 8080
    fmt.Printf("DB Users: %+v\n", cfg.Database.Users) // 输出两个用户信息
}
```



## 理解

### `viper.API` 和 `v.API` 之间的区别

`viper` 中提供了做全局配置和做局部配置的方法。在小型的单个文件的项目中，肯定没有区别。

但是在大的模块化的设计中，如果不同的模块有不同的配置，还是推荐使用局部配置。也就是：

```go
v := viper.New()
v.SetConfigFile("config.yaml")
```

### viper 是什么

我觉得可以简单将 `viper` 理解为一段“已经被序列化的、可以直接通过 API 修改的配置文件数据”。

```go
配置文件.yaml
	⬇️
viper 对象
	⬇️
Go 结构体
```

`viper` 就是这样一个层级关系。















