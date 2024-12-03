# Markdown 笔记

## 1. Markdown 实现标题跳转与超链接的技巧

在 Markdown 文件中，我们可以通过锚点链接来实现跳转到本文件或其他文件中的某个标题。以下是详细说明：

### 1.1 本文件内的标题跳转

1. Markdown 中的标题（`#` 开头的标题）会自动生成一个对应的 HTML 锚点。

2. 锚点生成规则：

    - 标题中的**字母**都会被转换为**小写**。
    - 标题中的**空格**会被替换为 `-`**（连字符）**。
    - 标题中的特殊字符（如 `.`、`!` 等）会被忽略。

    例如：

    ```markdown
    # 我的标题
    ```

    会生成一个默认的锚点：`#我的标题`，写成 URL 格式为：

    ```bash
    #我的标题 → #我的标题
    ```

3. 创建跳转链接：使用 `[文本](#锚点)` 的形式实现跳转。例如：

    ```markdown
    [跳转到标题](#我的标题)
    ```

4. 完整示例

    ```markdown
    # 第一部分
    
    这里是一些内容
    
    [跳转到第二部分](#第二部分)
    
    # 第二部分
    
    这里是第二部分的内容。
    ```

### 1.2 跳转到 Markdown 文件中的标题

Markdown 支持引用其他文件中的标题，格式如下：

```markdown
[文本](文件名.md#锚点)
```

示例：

假设有一个 `other-file.md` 文件，内容如下：

```markdown
# 另一个标题
```

在当前文件中，可以这样写：

```markdown
[跳转到另一个文件的标题](other-file.md#另一个标题)
```

### 1.3 自定义锚点（HTML ID）

如果默认的锚点不符合需求（如标题中包含特殊字符），可以手动定义一个自定义 ID：

```markdown
<h1 id="custom-id">我的标题</h1>
```

然后在连接中引用这个 ID：

```markdown
[跳转到我的标题](#custom-id)
```

示例：

```markdown
<h1 id="special-header">特别的标题</h1>

[跳转到特别的标题](#special-header)
```

### 1.4 注意事项

1. 注意锚点规则：各种 Markdown 渲染器生成锚点的方式可能略有差异，需测试确认。
2. 处理特殊字符：标题中的特殊字符（如 `#`、`&`、中文标点等）可能会需要特殊的编码。但是这种情况很少见，见到的时候再问 AI 就行了。

## 2. md 文件转 docx 文件

转换文件的前提是下载好 pandoc：[pandoc 下载地址](https://github.com/jgm/pandoc/releases)

之后在 windows 找到 pandoc 的可执行文件的地址，在这个地址里面，需要添加两个东西：

- `convert_md_to_docx.bat`

    就是 Windows 的批处理文件，批处理文件中的内容如下：

    ```bat
    @echo off
    chcp 65001
    setlocal enabledelayedexpansion
    
    :: 设置 Pandoc 所在目录路径
    set "pandoc_dir=D:\Other\pandoc-3.5"
    
    :: 设置模板文件路径
    set "template_file=%pandoc_dir%\template.docx"
    
    :: 提示用户输入 MD 文件路径
    echo 请输入要转换的 MD 文件路径：
    set /p md_file=""
    
    :: 获取输入文件的目录路径
    for %%f in ("%md_file%") do set "input_dir=%%~dpf"
    
    :: 检查文件是否存在
    if not exist "%md_file%" (
        echo 文件 %md_file% 不存在！
        exit /b
    )
    
    :: 获取文件名（不带扩展名）
    for %%f in ("%md_file%") do set "filename=%%~nf"
    
    :: 使用 Pandoc 转换为 DOCX 文件（输出到与输入文件相同的目录）
    "%pandoc_dir%\pandoc.exe" "%md_file%" -o "%input_dir%%filename%.docx" --reference-doc="%template_file%"
    
    :: 提示转换完成
    echo 转换完成：%input_dir%%filename%.docx
    pause
    ```

- `template.docx`

    就是转换成的 docx 中想要的格式。这个东西从 github 上下载即可：[下载地址](https://github.com/Achuan-2/pandoc_word_template)

之后将 `convert_md_to_docx.bat` 文件加入 utools 的本地文件启动，之后直接调用就可以啦。

























