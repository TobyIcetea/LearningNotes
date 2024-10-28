# Go 语言知识（2）

## 11. 值传递和引用传递

其实严格来说，Go 语言中，所有的参数传递都是值传递。这意味着，当我们将一个变量作为参数传递给函数时，函数收到的是该变量的一个拷贝。然而，通过传递指针（即变量的内存地址），我们可以在函数内部修改原始变量的值，从而实现类似引用传递的效果。

### 11.1 值传递

特点：

- 拷贝数据：函数接收到的是参数的一个副本，对副本的修改不会修改原始数据。
- 数据安全：避免了函数对原始数据的意外修改，提高了数据的安全性。

适用场景：

1. 基本类型和小型结构体：对于像 `int`、`float64`、`bool` 等基本类型，以及尺寸较小的结构体，值传递的性能开销很小。
2. 不需要修改原始数据：当函数仅需要读取数据而不修改时，值传递是理想的选择。
3. 保证数据不变性：值传递可以确保函数内部对参数的修改不会影响外部变量，有助于维护代码的可读性和可靠性。

示例：

```go
func double(n int) int {
	n = n * 2
    return n
}

func main() {
    num := 5
    result := double(num)
    fmt.Println(num)  // 输出：5，原始变量未改变
    fmt.Println(result)  // 输出：10
}
```

### 11.2 引用传递（通过指针）

特点：

- 传递地址：函数接收到的是参数的内存地址，可以直接修改原始数据。
- 节省内存：避免了大对象的内存拷贝，提升了性能。

适用场景：

1. 需要修改原始数据：当函数需要对传入的变量进行修改，并希望这些修改在函数外部可见时，应该使用指针。
2. 大型数据结构：对于占用内存较大的结构体或数组，值传递会导致性能下降，此时使用指针可以避免不必要的内存拷贝。
3. 共享数据：当多个函数需要操作同一份数据时，使用指针可以实现数据的共享和同步。

示例：

```go
type LargeStruct struct {
    Data [1024]int
}

func modifyStruct(ls *LargeStruct) {
    ls.Data[0] = 100
}

func main() {
    var ls LargeStruct
    modifyStruct(&ls)
    fmt.Println(ls.Data[0])  // 输出：100，原始数据被修改
}
```

### 11.3 如何选择

- 使用值传递：
    - 当数据类型较小，拷贝开销可以忽略不计。
    - 当你希望保护原始数据不被修改。
    - 当函数只是读取数据，而不需要对其进行修改。
- 使用引用传递（指针）：
    - 当需要在函数内部修改原始数据。
    - 当传递大型数据结构，避免高额的内存拷贝成本。
    - 当需要多个函数协同操作同一份数据。

### 11.4 注意事项

- 指针的安全性：使用指针时，要注意避免空指针和悬空指针，确保指针在使用前已被正确初始化。
- 并发环境：在多线程或并发环境中，传递指针可能会引起数据竞态问题，需要使用同步机制（如互斥锁）来保护共享数据。
- 性能考虑：虽然指针可以提高性能，但过度使用可能会增加代码的复杂性和错误风险，应根据具体情况权衡。

### 11.5 与 for 循环的结合

在 Go 语言的 `for range` 循环中，理解变量的作用域和赋值方式对于正确修改集合中的元素非常重要。

#### 11.5.1 `for range` 循环的工作原理

当你使用 `for i, element := range elements` 遍历一个切片（`elements`）时，`element` 是 `elements[i]` 的一个副本。这意味着：

- 对于基本类型和结构体类型的元素：`element` 是一个值拷贝，对 `element` 的修改不会影响到 `element` 中的原始数据。
- 对于指针类型的元素：`element` 是一个指针的拷贝，但它指向的内存地址与 `element[i]` 相同，因此对 `element` 所指对象的修改会影响到原始数据。

#### 11.5.2 示例分析

假设 `element` 是一个结构体类型：

```go
type Item struct {
    Value int
}

func main() {
    elements := []Item{{Value :1}, {Value: 2}, {Value: 3}}
    for _, element := range elements {
        element.Value *= 2
    }
    fmt.Println(elements)  // 输出：[{1} {2} {3}]，元素未修改
}
```

在上述代码中，对 `element.Value` 的修改不会影响到 `elements` 中的数据，因为 `element` 是 `element[i]` 的副本。

#### 11.5.3 如何让修改影响到 `elements` 中的原始数据

**方法一：使用索引直接修改 `elements[i]`**

```go
for i := range elements {
    elements[i].Value *= 2
}

fmt.Println(elements)  // 输出：[{2} {4} {6}]
```

解释：使用索引 `i` 直接访问并修改 `elements[i]`，确保修改作用于原始数据。

---

**方法二：指针遍历**

（1）取元素的地址

```go
for i := range elements {
    element := &elements[i]
    element.Value *= 2
}

fmt.Println(elements)  // 输出：[{2} {4} {6}]
```

（2）修改 `elements` 为指针切片

```go
elements := []*Item{{Value: 1}, {Value: 2}, {Value: 3}}

for _, element := range elements {
    element.Value *= 2
}

fmt.Println(elements)  // 输出：[{2} {4} {6}]，元素被成功修改
```

解释：

- 方案 1 中，通过 `&elements[i]` 获取元素的地址，`element` 成为指向原始元素的指针，对其修改将影响原始数据。
- 方案 2 中，将 `elements` 定义为指针切片，`element` 本身就是一个指针，修改 `element.Value` 会直接影响原始数据。

#### 11.5.4 深入理解：值类型与引用类型

- 值类型：包括基本类型（`int`、`float64`、`bool`、`struct`）等，赋值和传递时会复制数据。
- 引用类型：包括指针、切片、映射、通道、接口等，赋值和传递时复制的是引用，指向同一块内存地址。

在 `for range` 中：

- 值类型元素：`element` 是元素的副本，修改 `element` 不会影响原始数据。
- 引用类型元素：`element` 是引用的副本，但引用指向的底层数据相同，修改 `element` 指向的数据会影响原始数据。

#### 11.5.5 总结

- 默认情况下，在 `for i, element := range elements` 循环中，`element` 是元素的副本，对其修改不会影响到 `elements` 中的原始数据。
- 如果需要修改原始数据：
    - 使用索引直接修改：通过 `elements[i]` 方法并修改原始数据。
    - 使用指针：获取元素的地址或将集合定义为指针类型，对指针指向的数据进行修改。
- 如果不希望修改原始数据，直接使用 `element` 进行操作即可，因其为副本，修改不会影响原数据。

## 12. go 项目结构

在 Go 语言项目中，项目结构的设计非常重要，因为一个良好的项目结构可以帮助你更好地组织代码，增强可维护性和可扩展性。Go 社区已经有一些约定俗成的项目结构标准。以下是一些推荐的项目结构，以及各个目录和文件的用途。

### 12.1 常见的 Go 项目目录结构

一个典型的 Go 项目目录结构可能如下所示：

```go
project-name/
├── cmd/
│   └── app-name/
│       └── main.go
├── pkg/
│   └── mypackage/
│       ├── file1.go
│       └── file2.go
├── internal/
│   └── mypackage/
│       ├── file1.go
│       └── file2.go
├── api/
│   └── myapi.go
├── web/
│   ├── templates/
│   └── static/
├── scripts/
│   └── some-script.sh
├── deployments/
│   └── docker/
│       └── Dockerfile
├── docs/
│   └── some-document.md
├── go.mod
├── go.sum
└── README.md
```

### 12.2 各目录的用途

- cmd/
    - 作用：包含项目的主要应用程序。各个子目录代表一个可执行程序（通常是 main 包）。
    - 示例：`cmd/app-name/main.go` 通常是项目的入口点，包含 `main()` 函数。
- pkg/
    - 作用：存放对外开放的公共库和函数，可以在多个项目中共享。任何放在 `pkg/` 目录下的内容通常是为了其他项目可以使用的公共 API。
    - 示例：`pkg/mypackage/` 可能包含你的核心业务逻辑或通用功能。
- internal/
    - 作用：内部包，只对当前项目可见。这是 Go 的特殊机制，防止外部项目引用这些包。适合存放只在当前项目中使用的工具函数或逻辑。
    - 示例：`internal/mypackage/`
- api/
    - 作用：通常存放与 API 相关的内容，如 API 协议的定义、数据模型、Swagger 文件等。
    - 示例：`api/myapi.go`，可能包含 API 路由、数据结构和接口定义。
- web/
    - 作用：存放 Web 相关资源，如模板文件、静态文件（图片、JavaScript、CSS 等）等。
    - 示例：`web/template/` 可能包含 HTML 模板，`web/static/` 可以包含 CSS 或 JavaScript 文件。
- scripts/
    - 作用：存放与项目相关的脚本文件，通常是一些自动化任务脚本，如部署、构建、测试等。
    - 示例：`scripts/some-script.sh` 可能是构建脚本或清理脚本。
- deployments/
    - 作用：存放与部署相关的配置文件，如 Dockerfile、Kubernetes 配置等。
    - 示例：`deployments/docker/Dockerfile` 可以是 Docker 容器的配置文件。
- docs/
    - 作用：项目文档，如设计文档、API 文档等。可以包括 README 文件、架构设计等。
    - 示例：`docs/some-document.md` 可以是一个功能说明文档。
- 根目录：
    - `go.mod`：Go 项目的模块定义文件，记录项目依赖的包版本信息。
    - `go.sum`：记录依赖的校验和，确保项目依赖一致性。
    - `README.md`：项目说明文件，用于解释项目的功能、安装步骤等信息。

### 12.3 其他项目结构约定

- 单一 `main.go` 文件的项目：适合于小型项目，不需要复杂的目录结构，直接在项目根目录中编写 `main.go` 即可。
- `vendor/` 目录：存放项目的第三方依赖库，但现在更常用 Go 模块化工具 `go.mod` 来管理依赖，`verdor/` 通常不是必须的。

### 12.4 项目模块化与依赖管理

- 使用 `go mod init <module_name>` 初始化项目，并生成 `go.mod` 文件。
- 使用 `go get <package>` 来添加依赖，并自动更新 `go.mod` 和 `go.sum` 文件。
- `go build` 可以编译项目。
- `go run` 可以直接运行项目。

### 12.5 `go.mod`

`go.mod` 文件是 Go 项目用来管理依赖和模块的配置文件，它是 Go 语言模块化机制的核心部分。通过 `go.mod` 文件，你可以制定项目的模块名称、依赖的外部包及其版本等。下面是 `go.mod` 文件的一些内容和编写规则。

#### 12.5.1 `go.mod` 文件的基本内容

`go.mod` 文件通常包含以下几部分内容：

```go
module example.com/my-module

go 1.20

require (
	github.com/some/package v1.3.2
    golang.org/x/some/package v0.4.5
)

replace (
	github.com/some/package v1.3.2 => github.com/another/package v1.3.3
)

exclude (
	github.com/some/package v1.2.0
)

retrack (
	v1.0.0  // replaced due to critical bug
)
```

#### 12.5.2 主要字段说明

`module`

- 作用：定义模块的名称，通常是项目的根路径，包含域名。模块名可以是 Git 仓库的路径，比如 `github.com/user/project`。
- 示例：`module example.com/my_module`

`go`

- 作用：指定项目所使用的 Go 语言版本。这不是一个严格的限制，但表示项目期望使用的版本。
- 示例：`go 1.20` 表示项目适合在 Go 1.20 版本中运行。

`require`

- 作用：指定项目所依赖的第三方包及其版本。可以单独列出依赖项，也可以使用括号 `()` 一次性列出多个依赖。

- 示例：

    ```go
    require github.com/some/package v1.3.2
    require (
    	golang.org/x/some/package v0.4.5
        github.com/another/package v2.1.0
    )
    ```

`replace`

- 作用：替换依赖包的路径或版本，通常用于替换某个依赖包的版本，或者在开发调试时使用本地路径替换远程路径。

- 示例：

    ```go
    replace github.com/some/package v1.3.2 => github.com/another/package v1.3.3
    replace example.com/my-package -> ../my-local-package
    ```

`exclude`

- 作用：排除某个依赖包的特定版本，确保在依赖解析时不会使用特定的版本。
- 示例：`exclude github.com/some/package v1.2.0`

`retract`

- 作用：用于声明某些版本不再被推荐使用（一般是因为重大错误或其他原因），仅用于项目内部的参考。
- 示例：`retract v1.0.0  // replaced due to critical bug`

#### 12.5.3 `go.mod` 文件的一些规则 

1. 模块名称

    - 模块名称通常是项目的路径，可以是 Git 仓库的路径，或自定义路径。建议使用项目托管位置作为模块名（如 `github.com/user/repo`），用于依赖管理和项目共享。

2. 版本规范

    - Go 使用语义版本号（Semantic Versioning, semver）。版本格式通常为 `vX.Y.Z`，其中：
        - `X` 表示主版本（有破坏性变化时更新）。
        - `Y` 表示次版本（新功能且兼容时更新）。
        - `Z` 表示修订版本（错误修复时更新）。
    - Go 的版本管理可以区分不同的主版本（如 `v1` 和 `v2`），这也是 Go 模块的一大特性。

3. 依赖管理

    - `go get` 命令可以用来添加依赖，例如：`go get github.com/some/package@v1.2.3` 会将指定包添加到 `require` 中。
    - 运行 `go mod tidy` 可以清理 `go.mod` 文件，移出不再使用的依赖。

4. 模块版本选择

    - `Go` 的模块机制会自动选择依赖项的最新版本，或者遵循最小版本选择策略。
    - 可以使用 `go list -m all` 来查看所有的依赖及其版本。

5. 替换依赖

    - 在测试或调试时，可以使用 `replace` 来临时替换依赖。例如将远程以来替换为本地路径，用于本地调试。

        ```go
        replace example.com/my-package => ../local/my-package
        ```

#### 12.5.4 常用命令

- `go mod init <module_name>`：初始化 `go.mod` 文件。
- `go mod tidy`：清理 `go.mod` 和 `go.sum`，删除无用依赖。
- `go mod vendor`：将依赖下载到 `verdor/` 目录中。
- `go mod edit`：手动编辑 `go.mod` 文件内容。
- `go mod download`：下载 `go.mod` 中列出的依赖。

### 12.6 Go 编译命令

编译一个 Go 项目是一个相对简单的过程，Go 提供了内置的工具来帮助你见源代码编译成执行文件。下面是一些编译 Go 项目的基本步骤和常用命令。

#### 12.6.1 使用 `go build` 命令

`go build` 是 Go 中用于编译项目的主要命令。以下是一些编译方法：

（1）编译单个文件：如果只有一个单独的 Go 文件，比如 `main.go`，可以使用以下命令来编译：

```bash
go build main.go
```

- 这会在当前目录生成一个名为 `main` 的可执行文件（Windows 下为 `main.exe`）。
- 注意：编译后文件的名称取决于源文件名。

（2）编译整个项目：如果有一个完整的项目，可以直接在项目的根目录下运行 `go build`：

```bash
go build
```

- 这会根据 `main.go` 文件所在的位置生成可执行文件。
- 可执行文件的默认名称为项目所在的目录名。

（3）指定输出文件名：通过 `-o` 选项指定输出文件的名称。

```bash
go build -o myapp
```

- 生成的可执行文件名将是 `myapp`。

（4）编译特定的 `cmd` 目录：在遵循推荐的项目结构中，通常会有 `cmd` 目录存放可执行文件入口。如果你的项目目录结构是这样的：

```css
project-name/
└── cmd/
    └── app-name/
        └── main.go
```

你可以通过指定目录来编译：

```bash
go build -o myapp ./cmd/app-name
```

#### 12.6.2 交叉编译

Go 原生支持交叉编译，你可以编译适用于不同平台的可执行文件。通过设置 `GOOS` 和 `GOARCH` 环境变量，可以指定目标操作系统和架构。

示例：

- 编译 Linux 平台的可执行文件：

    ```bash
    GOOS=linux GOARCH=amd64 go build -o myapp-linux
    ```

- 编译 Windows 平台的可执行文件;

    ```bash
    GOOS=linux GOARCH=amd64 go build -o myapp.exe
    ```

- 编译 Mac 平台的可执行文件：

    ```bash
    GOOS=darwin GOARCH=amd64 go build -o myapp-mac
    ```

#### 12.6.3 常用编译命令总结

- 编译单个文件

    ```bash
    go build main.go
    ```

- 编译整个项目：

    ```bash
    go build
    ```

- 指定输出文件名：

    ```bash
    go build -o output-file
    ```

- **指定 `main.go` 位置**：

    ```
    go build -o output-file ./src/main
    ```

- 交叉编译（针对不同平台）：

    ```bash
    GOOS-linux GOARCH=amd64 go build -o myapp-linux
    ```

- 安装可执行文件：

    ```bash
    go install
    ```

- 直接运行项目（开发阶段）：

    ```bash
    go run main.go
    ```

#### 12.6.4 编译常见问题

1. 未找到 `go.mod` 文件
    - 如果项目是基于模块的，需要确保在项目根目录运行 `go mod init <module-name>` 初始化 `go.mod` 文件。
    - 如果没有 `go.mod`，Go 会假设项目在 `GOPATH` 下进行编译。
2. 依赖问题
    - 如果有缺少依赖的情况，可以使用 `go mod tidy` 清理和修复 `go.mod` 和 `go.sum`。
    - 确保网络环境良好，因为 Go 需要下载外部依赖。

### 12.7 Go 编译环境变量

在 Go 语言开发和编译过程中，`GOROOT`、`GOPATH` 和 `GOPROXY` 是一些非常重要的环境变量，它们用于管理 Go 语言工具链、依赖包以及模块。下面是每个参数的具体解释：

1. **GOROOT**
    - 用途：`GOROOT` 指定 Go 语言安装的根目录，也就是 Go 工具链（编译器、标准库等）所在的位置。
    - 默认值：通常安装 Go 时，会自动设置 `GOROOT`，一般无需手动更改。如果你从官方提供的二进制文件安装 Go，那么默认的 `GOROOT` 可能是 `/usr/local/go`（在 Linux 系统或 MacOS 系统上）。
    - 设置场景：通常只在你从源码编译 Go 或者安装了多个版本的 Go 需要切换时，才会手动设置 `GOROOT`。
2. **GOPATH**
    - 用途：`GOPATH` 是用来指定你的工作空间目录的。工作空间是用来存放 Go 项目源码、已编译的二进制文件和缓存的依赖包的地方。早期（Go 1.11 之前）管理 Go 项目必须依赖 `GOPATH`，但在引入 Go 模块（`go.mod` 文件）之后，`GOPATH` 主要用于缓存和一些工具存储。
    - 典型结构：
        - `$GOPATH/src`：源码目录，放置你的 Go 项目代码。
        - `$GOPATH/bin`：编译后的可执行文件。
        - `$GOPATH/pkg`：已编译的包。
    - 设置场景：即使你使用 Go 模块系统，也需要设置 `GOPATH`，因为它用于存放缓存包文件。如果不设置，Go 会使用默认目录（`$HOME/go` 或 `C:\User\<用户名>\go`）。
3. **GOPROXY**
    - 用途：`GOPROXY` 是用于指定 Go 模块代理的 URL，用于下载模块依赖。它解决了直接从 `VCS`（版本控制系统，如 Github）下载时可能出现的网络问题和稳定性问题。Go 模块代理提供了更快、更可靠的依赖包下载方式。
    - 默认值：默认值通常是 `https://proxy.golang.org`，但在中国大陆等地区，由于访问限制，常用的设置是：`https://goproxy.cn`。
    - 设置场景：在网络环境不稳定或者访问受限的情况下，可以设置 `GOPROXY` 来选择合适的代理。

**总结**：

- `GOROOT`：Go 安装路径，不常修改。
- `GOPATH`：工作空间路径，用于缓存和开发环境。
- `GOPROXY`：模块代理，用于加速和稳定依赖下载。

如果项目正在使用 Go 模块（即项目根目录有 `go.mod` 文件），大多数情况下可以不需要关心 `GOROOT` 和 `GOPATH`，只要 `GOPROXY` 配置好即可。

## 13. interface

在 Go 语言中，`interface` 是一个非常强大的特性，它用于定义一组方法的集合。任何类型只要实现了某个 `interface` 中定义的所有方法，那么这个类型就被视为实现了该 `interface`。`interface` 提供了一种灵活的、多态的编程方式，可以帮助实现更解耦的代码结构。

### 13.1 定义 `interface`

在 Go 语言中，`interface` 是一组方法签名的集合。定义一个 `interface` 的语法如下：

```go
type InterfaceName interface {
    Method1(param1 Type1, param2 Type2) ReturnType1
    Method2(param3 Type3) ReturnType2
}
```

`InterfaceName` 是接口的名称，`Method1` 和 `Method2` 是接口中定义的方法。这些方法只有方法签名，没有具体的实现。

### 13.2 实现 `interface`

在 Go 中，一个类型不需要显式声明它实现了某个接口，只要这个类型实现了接口中所有的方法，那么它就隐式地实现了该接口。例如：

```go
type MyStruct struct {
    // 结构体字段
}

func (m MyStruct) Method1(param1 Type1, param2 Type2) ReturnType1 {
    // 方法的实现
}

func (m MyStruct) Method2(param3 Type3) ReturnType3 {
    // 方法的实现
}
```

如果 `MyStruct` 结构体实现了 `InterfaceName` 接口中的所有方法，那么 `MyStruct` 类型就可以作为 `InterfaceName` 类型使用。

### 13.3 `interface{}` 类型

Go 语言中的空接口 `interface{}` 是一个特殊的接口类型，因为它不包含任何方法。因此，任何类型都隐式实现了 `interface{}`。这使得空接口可以用来存储任意类型的值，例如：

```go
var anyType interface{}
anyType = 42
anyType = "Hello"
anyType = MyStruct{}
```

这种特性在需要处理未知类型的数据时非常有用，例如在编写通用函数或数据结构时。

### 13.4 接口的使用

接口通常用于实现多态性。可以定义一个接收接口类型参数的函数，从而在不修改函数代码的情况下接受不同的实现。例如：

```go
package main

import "fmt"

type Animal interface {
	Speak() string
}

type Dog struct{}

func (d Dog) Speak() string {
	return "Woof!"
}

type Cat struct{}

func (c Cat) Speak() string {
	return "Meow!"
}

func MakeSound(a Animal) {
	fmt.Println(a.Speak())
}

func main() {
	dog := Dog{}
	cat := Cat{}

	MakeSound(dog)
	MakeSound(cat)
}
```

在这个例子中，`Dog` 和 `Cat` 都实现了 `Animal` 接口，因此可以将它们作为 `Animal` 类型传递给 `MakeSound` 函数。

### 13.5 类型断言和类型切换

在处理接口时，可能会遇到需要将接口类型转换回具体类型的情况。这可以通过类型断言来实现：

```go
var a Animal = Dog{}
dog, ok := a.(Dog)
if ok {
    fmt.Println("It's a dog!")
}
```

类型切换用于根据接口值的具体类型执行不同的操作：

```go
switch v := a.(type) {
case Dog:
    fmt.Println("This is a dog!")
case Cat"
    fmt.Println("This is a cat!")
default:
    fmt.Println("Unknown type!")
}
```

### 13.6 接口嵌套

接口可以嵌套另一个接口。例如：

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}
```

在这个例子中，`ReadWriter` 接口包含了 `Reader` 和 `Writer` 的方法，所以只要一个类型实现了 `Read` 和 `Write` 方法，它就被视为实现了 `ReadWriter` 接口。

### 13.7 接口的零值

接口的零值是 `nil`，当一个接口变量没有被初始化或没有赋予具体的实现时，它的值是 `nil`。因此，在使用接口时要注意检查是否为 `nil`，以避免运行时错误。

```go
var a Animal
if a == nil {
    fmt.Println("a is nil")
}
```

### 13.8 总结

- `interface` 定义了一组方法的集合。
- Go 中类型通过实现接口中的方法来隐式实现该接口。
- `interface{}` 是空接口，可以保存任意类型的值。
- 通过类型断言和类型切换可以从接口类型转换为具体类型。
- 接口支持嵌套，允许更复杂的接口定义。

## 14. 引号

在 Go 语言中，`""`、`''`、` `` ` 这三种引号有不同的用途和含义，具体如下：

**双引号 `""`：**

- 用于定义字符串（`string`）。

- 双引号内的内容支持转义字符（如 `\n` 表示换行，`\t` 表示制表符）。

- 适合用于需要包含特殊字符或格式化字符串的情况。

- 示例：

    ```go
    str := "Hello, World\nWelcome to Go."
    fmt.Println(str)
    ```

**单引号 `''`：**

- 用于定义字符（`rune`）类型。

- Go 中 `rune` 是一个特殊的类型，用来表示单个 Unicode 字符，实际上是一个 `int32` 类型的值。

- 适合用于需要单个字符而非字符串的情况。

- 示例：

    ```go
    ch := 'A'
    fmt.Printf("Character: %c, Unicode: %U\n", ch, ch)
    ```

**反引号 ` `` `（称为「原样字符串」或「原生字符串」）：**

- 用于定义原样字符串字面值（`raw string literal`）。

- 反引号内的内容会保持原样，不进行转义，即可以包含换行、特殊字符甚至双引号，而不会被解释。

- 适合用于定义多行文本或需要避免转义的字符串内容。

- 示例：

    ```go
    package main
    
    import "fmt"
    
    func main() {
    	rawStr := `This is a raw string.
    It can span multiple lines. Special characters like \n and \t will not be escaped.`
    	fmt.Println(rawStr)
    }
    ```

**总结：**

- `""` ：字符串，支持转义，用于普通字符串操作。
- `''`：字符，表示单个字符，用于需要单个 Unicode 字符的场景。
- ` `` `：原样字符串，保持原样，不转义，适合多行文本或特殊字符。



























