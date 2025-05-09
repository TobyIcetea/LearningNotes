# Go 技巧

## 1. GoLand 与 Leetcode 联动

最近刷 Leetcode 的时候，每次都是在网站上刷的题目。因为现在没有会员，所以没有语法高亮，调试的时候也比较麻烦。而且，Leetcode 网页版的环境跟 GoLand 这种比较流行的 IDE 之间的差别还是挺大的。

所以心里面一直想着如果能在 GoLand 上直接刷 Leetcode 多好！

现在就可以通过一个插件实现这个功能：

1. 在 Goland 的 Plugins 插件市场中安装插件 `Leetcode Editor`，安装这个插件。

    ![image-20250406202700805](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250406202700805.png)

2. 之后对插件进行配置，插件的配置按钮在 GoLand IDE 的左上角的位置：

    ![image-20250406202751461](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250406202751461.png)

    里面需要填写自己 Leetcode 账户的信息，以及一些其他的配置。我目前使用的配置如下：

    ![image-20250406202851428](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250406202851428.png)

    其中，下面的几个栏中：

    - Code FileName：

        ```js
        ${question.frontendQuestionId}.$!velocityTool.camelCaseName(${question.titleSlug})_test
        ```

    - Code Template：

        ```js
        package cn
        
        import (
            "testing"
        )
        
        func Test$!velocityTool.camelCaseName(${question.titleSlug})(t *testing.T) {
            
        }
        
        ${question.code}
        ```

    - Template Constant：

        ```js
        ${question.title}	题目标题	示例:两数之和
        ${question.titleSlug}	题目标记	示例:two-sum
        ${question.frontendQuestionId}	题目编号
        ${question.content}	题目描述
        ${question.code}	题目代码
        $!velocityTool.camelCaseName(str)	转换字符为大驼峰样式（开头字母大写）
        $!velocityTool.smallCamelCaseName(str)	转换字符为小驼峰样式（开头字母小写）
        $!velocityTool.snakeCaseName(str)	转换字符为蛇形样式
        $!velocityTool.leftPadZeros(str,n)	在字符串的左边填充0，使字符串的长度至少为n
        $!velocityTool.date()	获取当前时间
        ```

    配置完成之后点 `Apply` 然后 `OK`。

3. 如果想要在本地对 Leetcode 代码进行调试，这时候就要注意配置上面插件配置中的 `TempFilePath` 目录。我推荐专门创建一个 GoLand 项目来刷 Leetcode，比如项目的名称叫 `LeetcodeSolutions`，然后我们就将 `TempFilePath` 的地址直接定位这个项目文件夹就好了。

    之后在每个题目的 go 源文件中，在 Leetcode 题目的函数上面会多一个 Test 函数。如果后期要做一些案例的测试，可以使用 Test 函数进行 `Run`、`Debug` 这些操作。

## 2. Go 使用 github 的包

今天在完成一个项目的时候，需要使用 github 上的 walk 包，直接使用命令：

```bash
go get github.com/lxn/walk
```

但是会报错：

```bash
go: module github.com/lxn/walk: Get "https://proxy.golang.org/github.com/lxn/walk/@v/list": dial tcp [2607:f8b0:400a:800::2011]:443: connectex: A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond.
```

大概意思就是连接失败，还是网络问题。

此时可以通过设置国内的 go 代理：

```bash
go env -w GOPROXY=https://goproxy.cn,direct
```

之后再执行 `go get` 的命令：

```bash
go get github.com/lxn/walk
```

























