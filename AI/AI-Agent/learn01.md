# AI Agent

## Python 调 DeepSeek API

进入 DeepSeek 的 API 的官网：[api-keys](https://platform.deepseek.com/api_keys)。

前提当时是要先充好钱，比如我这次充了十块钱，之后可以在 API Keys 中创建一个 API。但是需要注意的是，API 创建之后需要马上保存好，之后就不能查看这个 API 是啥了。

再然后，就可以使用 Python 代码来调用 DeepSeek 的 API：

```python
from openai import OpenAI

client = OpenAI(api_key="密钥密钥密钥", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model = "deepseek-chat",
    messages= [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream = False
)

print(response.choices[0].message.content)
```

运行代码会输出：

> Hello! How can I assist you today? 😊

官网还提供了其他的 API 调用方式，一共有三种，分别是 curl 模型、Python 模型、Nodejs 模式。

调用大语言模型的 API 就需要两个参数，一个是 `api_key`，一个是 `base_url`。其中：

- `base_url` 用于指示我们调用是哪个平台的模型。也就是说，这里是用来确定我们是使用的 deepseek，还是 openai 还是 Gemini 之类的平台的大模型。
- `api_key` 就是我们花钱才能买到的东西，用于确定我们使用 api 的账号。也就是使用的是谁的额度。

## Golang 调 DeepSeek API

`requests.json`：

```json
{
    "messages": [
        {
        "content": "You are a helpful assistant",
        "role": "system"
        },
        {
        "content": "Hi",
        "role": "user"
        }
    ],
    "model": "deepseek-chat",
    "frequency_penalty": 0,
    "max_tokens": 2048,
    "presence_penalty": 0,
    "response_format": {
        "type": "text"
    },
    "stop": null,
    "stream": false,
    "stream_options": null,
    "temperature": 1,
    "top_p": 1,
    "tools": null,
    "tool_choice": "none",
    "logprobs": false,
    "top_logprobs": null
}
```

`main.go`：

```go
package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

func main() {

	url := "https://api.deepseek.com/chat/completions"
	method := "POST"

	// 读取 json 文件内容
	jsonBytes, err := os.ReadFile("request.json")
	if err != nil {
		panic(err)
	}

	payload := strings.NewReader(string(jsonBytes))

	client := &http.Client{}
	req, err := http.NewRequest(method, url, payload)

	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Accept", "application/json")
	req.Header.Add("Authorization", "Bearer 密钥密钥密钥")

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(string(body))
}

```

运行结果：

```json
{"id":"2dba9597-458f-4869-abe1-382374bdc306","object":"chat.completion","created":1748422906,"model":"deepseek-chat","choices":[{"index":0,"message":{"role":"assistant","content":"Hello! How can I assist you today? 😊"},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":9,"completion_tokens":11,"total_tokens":20,"prompt_tokens_details":{"cached_tokens":0},"prompt_cache_hit_tokens":0,"prompt_cache_miss_tokens":9},"system_fingerprint":"fp_8802369eaa_prod0425fp8"}
```



## DeepSeek API 文档

### 对话部分

#### `message`

在 Deepseek 的文档中，API 请求的 `body` 部分通常包含一个 `message` 数组，这个数组由不同角色的消息对象组成。这些消息对象遵循类似 OpenAI Chat Completion API 的设计模型，用于构建多轮对话的上下文。

`message` 数组中的每个元素是一个对象，其 `role` 字段标识消息的发送者角色，常见类型包括：

- `system`：系统消息，用于设置助手的行为或背景（例如指令、角色设定）。
- `user`：用户消息，标识用户的输入或问题。
- `assistant`：助手消息，表示助手之前的回复（用于多轮对话上下文）。
- `tool`（如有支持）：工具调用的返回结果（类似 OpenAI 的 `function` 角色）。

每种消息类型共享通用结构，但可能有特定用途的字段。

在代码中，可以看到 `message` 这个数组中的对象的 `role` 部分，就是 `system`、`user` 等四种类型中其中一个。其实也就是说，这个消息是对谁指定的。在我们上面的 demo 中，就是对系统指定，`You are a helpful assistant`，然后用户发送的请求就是 `Hello`。

之后的 `content` 字段就比较好理解，就是这个消息发送的内容是什么。比如说我们上面的 `demo` 中的 `Hello`。

还有一个字段叫做 `name`，也是一个 `string` 类型的。官方的说明是：“可以选填的参与者的名称，为模型提供信息以区分相同角色的参与者。”这个字段的核心作用是：一个用户使用多个 AI 助手，或者是多个用户使用一个 AI 助手，或者是多个用户使用多个 AI 助手。通过一些 demo 来看：

#### `message.name`

首先使用 DeepSeek V3 使用如下的 json 输入：

```json
    "messages": [
        {
            "content": "你是一个客服助手。",
            "role": "system"
        },
        {
            "content": "我的订单状态是什么？",
            "role": "user",
            "name": "Alice"
        },
        {
            "content": "苹果的营养价值怎么样？",
            "role": "user",
            "name": "Bob"
        }
    ],
```

运行代码之后，AI 会返回如下的信息：

>关于您的问题：  
>
>1. **订单状态查询**：请您提供订单号或登录账户查看，也可以联系对应平台的客服获取最新信息。  
>
>2. **苹果的营养价值**：  
>   - **富含膳食纤维**：助消化、促进肠道健康。  
>   - **维生素C**：增强免疫力，抗氧化。  
>   - **低热量**：约95大卡/个（中等大小），适合健康饮食。  
>   - **含钾和抗氧化物质**：有益心脏健康。  
>
>如需其他帮助，请随时告诉我！ 😊

虽然说正确返回了，但是这并不是我想要的。这相当于是将输出全都压缩到一起了，但是我以为它会对不同的角色输出不同的解答。

那么我们换一下呢：

```json
    "messages": [
        {
            "content": "你是一个客服助手。请针对不同的用户返回不同的答案。回答的时候带上你回复的客户的名字。",
            "role": "system"
        },
        {
            "content": "我的订单状态是什么？",
            "role": "user",
            "name": "Alice"
        },
        {
            "content": "苹果的营养价值怎么样？",
            "role": "user",
            "name": "Bob"
        }
    ],
```

本次输出信息：

>亲爱的用户，您好！
>
>关于您的问题：
>
>1. 订单状态查询：很抱歉，我无法直接查看您的订单状态。请您提供订单号或登录您的账户查看最新状态。
>2. 苹果的营养价值：苹果富含维生素C、膳食纤维和抗氧化物质，有助于消化和提高免疫力。每天一个苹果对身体很有好处。
>
>如果您需要进一步帮助，请随时告诉我。
>
>祝您生活愉快！

好像也就是将两个问题放到一起处理了。实际上，如果不带有这个 name，好像输出的结果也是一样的。

这是 DeepSeek V3 的输出结构，R1 的输出结构跟这个有一些不同，但是还得重新编写结构体，这里我就不重新写了。

`role`、`content`、`name` 这三个字段是 `system` 和 `user` 这两个字段使用的，但是 `assistant` 和 `tool` 的使用略有不同。具体看[DeepSeek官方文档](https://api-docs.deepseek.com/zh-cn/api/create-chat-completion)。

#### `model`

就是本次我们使用的是哪个 DeepSeek 的模型。`model` 这里有两个选项，分别是：

- `deepseek-chat`，对应 DeepSeek V3。
- `deepseek-reasoner`，对应 DeepSeek R1。

#### `frequency_penalty`

取值范围是 `[-2, 2]`。具体含义是，对已经出现过的词，要不要施加惩罚以及施加惩罚的力度。如果这个值大于 0，那就是会对已经出现过的词（token）施加惩罚，之后会避免再出现这些词。

比如说在与 AI 的对话过程中，上下文中已经多次出现了“人工智能”这个词，那么如果我们的 `frequency_penalty` 设置的值比较大，之后模型就会对“人工智能”这个词施加惩罚，后面会出现更少的“人工智能”，转而换成是“AI”、“机器学习”之类的词语。相反，如果我们设置的 `frequency_penalty` 设置的是一个负数，模型则会更频繁地去重复“人工智能”。

所以：

- `frequency_penalty > 0`：生成的文本更具有多样性，但是可能比较跳跃，可能会偏离主题。
- `frequency_penalty < 0`：生成的文本更加固定，比较准确、保守，但是可能会一直强调某一个词语，让回答比较冗长。

参数的默认值是 `0`，表示对 `token` 没有惩罚或者奖励，完全由模型自己来决定。

#### `max_tokens`

这里说的 `max_tokens` 是输出部分的 `token` 限制，而不是输入。

但是实际上也是有一个不等式的关系在输入和输出之间的，具体可以表现为：
$$
input\_tokens + output\_tokens \leq model\_context\_limit
$$
其中提到几个参数，分别介绍一下：

- `input_tokens`：输入的内容的长度（`tokens`）。
- `output_tokens`：输出的内容的长度（输出 `tokens`）。
- `model_context_limit`：模型固定的最大 `tokens` 数量。这是三个参数中唯一一个不可变的参数，完全由所使用的 model 决定。这个东西的单位一般都是多少 K，比如说 `gpt-4-turbo` 的上下文长度最多是 `128k`，`DeepSeekR1` 的上下文长度限制也是 `128K`。但是我们之前说的满血版 DeepSeek 说的 `671B` 说的是模型内部的参数量，表示一个模型的复杂程度，跟上下文长度限制不是一个东西。

于是在上述的不等式中，`model_context_limit` 这个参数已经固定死了，`output_tokens` 又是模型的返回值我们自己只能确定一个 `input_tokens`。在确定好了 `input_tokens` 之后，`output_tokens` 就会有一个上限值。

举个例子，比如说我们一个模型的上下文限制是 8192，然后在输入的时候，我们的输入 `token` 已经达到了 5000。那么输出的时候，输出的最大 `token` 就是 3192。

说到现在好像还没有提到上面说的 `max_tokens`。实际上这是一个双重限制，上面的不等式和这个 `max_tokens` 一起限制输出，让输出不要太长了。用代码表明可以是：

```go
output_tokens = min(max_tokens, model_context_limit - input_tokens)
```

所以说如果输入特别长，可能会挤压输出的长度。但是这通常不是主要的原因，因为大部分时候上限都是卡在 `max_tokens` 的限制，这个参数让我们的输出不会特别长。

在 DeepSeek 中，`max_tokens` 参数的取值区间是 `[1, 8192]`，默认值是 `4096`。

#### 多轮对话与 `input_tokens`

上面总结说 `input_tokens` 就是输入的文本的长度，但是我觉得还应该跟之前的对话内容有关系。也就是说，在 `DeepSeek` 网页中，如果一组对话前面已经有很长了，那么后面的输出也会被前面的输入挤压。但是在我自己的 Coding 方面，每次调 API 的时候，还是无法实现出网页端多轮对话的效果，这一点让我比较疑惑。

通过查文档发现，OpenAI 的 API 本身是无状态的，也就是不保存状态、不保存历史记录的。

所以如果要进行多轮的对话，就要开发者显示传入完整的对话历史。这个对话历史包括开发者前面输入的内容，还有模型给出的输出内容。将所有的内容都放到一个 `messages` 中，再将这个 `messages` 传给 API。

这就像是：

```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "第一轮问题"},
    {"role": "assistant", "content": "模型的第一轮回复"},
    {"role": "user", "content": "新的问题"} // 包含历史内容
  ]
}
```

套到我们之前的 golang 的 json 结构体中，第一次的结构体我们这样写：

```json
    "messages": [
        {
            "content": "你是一个通用的AI助手，很擅长为我解答问题。",
            "role": "system"
        },
        {
            "content": "你可以为我讲一个简单的笑话吗？",
            "role": "user"
        }
    ],
```

第一次调用之后，AI 给出了它的回复，这次我们将 AI 的回复，以及我们的第二个问题，重新传给 AI：

```json
    "messages": [
        {
            "content": "你是一个通用的AI助手，很擅长为我解答问题。",
            "role": "system"
        },
        {
            "content": "你可以为我讲一个简单的笑话吗？",
            "role": "user"
        },
        {
            "content": "当然可以！这里有一个简单的笑话：\n\n**为什么数学书总是很忧郁？**  \n——因为它有太多“问题”要解决！  \n\n希望这个笑话能让你笑一笑！ 😄",
            "role": "assistant"
        },
        {
            "content": "这个笑话的笑点在哪里？",
            "role": "user"
        }
    ],
```

我们还可以继续：

```json
    "messages": [
        {
            "content": "你是一个通用的AI助手，很擅长为我解答问题。",
            "role": "system"
        },
        {
            "content": "你可以为我讲一个简单的笑话吗？",
            "role": "user"
        },
        {
            "content": "当然可以！这里有一个简单的笑话：\n\n**为什么数学书总是很忧郁？**  \n——因为它有太多“问题”要解决！  \n\n希望这个笑话能让你笑一笑！ 😄",
            "role": "assistant"
        },
        {
            "content": "这个笑话的笑点在哪里？",
            "role": "user"
        },
        {
            "content": "这个笑话的笑点在于利用了“问题”一词的双关意义：\n\n1. **字面意义**：数学书里确实充满了需要解决的数学问题（题目、习题）。\n2. **引申义**：日常用语中，“有太多问题”也可以形容一个人烦恼多、情绪低落（比如：“他最近问题很多”）。\n\n通过把数学书拟人化（忧郁），将客观的“数学题目”和主观的“烦恼”巧妙挂钩，制造了一种反差幽默。简单来说，就是让书本像人一样“抱怨工作太多”，从而显得可爱又好笑。\n\n类似逻辑的笑话还有：  \n**“为什么电脑很冷？”**  \n——因为它总是开着Windows（窗户）！  \n\n（这种笑话适合喜欢“冷幽默”或文字游戏的人😉",
            "role": "assistant"
        },
        {
            "content": "用大白话重述一遍。",
            "role": "user"
        }
    ],
```

AI 最后回答说：

> 哈哈，说白了就是：  
>
> 数学书里全是“题目”（1+1=？这种），但“题目”这个词也能用来形容“烦心事”。  
>
> 笑话故意把书当成人，假装它因为“题目太多”而发愁——就像你作业写不完时的心情一样！  
>
> **举个栗子🌰：**  
>
> 你妈说：“你问题很多诶！” 其实是在骂你事儿多，不是真让你做数学题。  
>
> 笑话就是把这两层意思拧在一起，逗你玩呢！  
>
> （是不是像“小明每天走路上学——因为他不会飞”一样无聊又好笑？😆）

很明显这就是一个多轮对话，每次 AI 回答的问题，都会受到之前所有输入的影响。

那么历史记录如何计入 tokens 呢？其实就是所有的历史记录都会以 `input` 的形式计入 tokens，所有的历史记录，都会放到 `messages` 数组中，全部都传给 API。在网页端，如果我们已经和 AI 聊了 200 `tokens` 的内容，接下来一次输入，我们输入了 50 `tokens` 的文本，那么本次一共给 AI 传过去的 `input_tokens` 就一共是 `200 + 50 = 250 tokens`。

这样的话也就能理解为什么一轮对话累计太多之后，AI 的输出会越来越少，后面会被严重挤压：

| 轮次     | 输入 token 累计                                              | 输出 token 累计      |
| -------- | ------------------------------------------------------------ | -------------------- |
| 第 1 轮  | 用户输入 100，所以就是 100                                   | 4096 - 100 = 3996    |
| 第 2 轮  | 上一次对话 API 返回 150，本次我们再问一个 100 的问题，所以本次的输入一共是：100 + 150 + 100 = 350tokens | 4096 - 350 = 3746    |
| 第 10 轮 | 之前所有的问答上下文 + 本次输入的 tokens，一共是 4000 tokens | **4096 - 4000 = 96** |

可以看到，后面输出会被严重挤压！

所以我们在一些大模型平台上使用的时候，也会有一些选项，让我们可以「只保留最近的三次对话」。其实也就是让 `messages` 数组不要变得太长，只保留最近的几次就行。

或者是我们也可以让 `messages` 中的上下文信息变得精简一些，比如说虽然 AI 之前给我们回复了很多的东西，但是我们将 AI 回复的很多内容给缩短成很短的一段话。

所以这也解释了为什么我们在 DeepSeek 之类的网页聊天中，聊到中途竟然还能换模型！将对话模型由之前的 `DeepSeek V3` 换成 `DeepSeek R1`，其实就是把相同的参数发给了另一个 AI 而已。

#### `presence_penalty`

取值的范围是 `[-2, 2]`，默认值是 `0`。

不管是从表面上看，还是从功能的描述上看，都感觉这个 `presence_penalty` 和之前的 `frequency_penalty` 差不多。后来发现，这两个虽然都是对之前的文本添加惩罚的参数，但是一个重点在**存在**，另一个重点在**频率**。

通过举例说明，如果说我们的 `presence_penalty` 设置的是一个正数，那么对于一份之前的对话，如果已经出现过「人工智能」这个词语，也就是说这个词语已经出现过了，之后的生成的输出中，就会尽可能的去避免再次出现「人工智能」这个词语。惩罚的是一个固定的值，就是一个简单的黑名单，如果你出现过，就生效一次且仅生效一次；如果你还没出现过，就不生效。

但是我们之前谈过的 `frequency_penalty` 说的是频率。比如说之前的上下文中出现过「人工智能」这个词语，大模型就会记住这个词语出现过多少次，出现的次数越多，罚的越狠，之后再出现的概率也更小。也就是说，如果只出现过一次，那么其实给的惩罚就并不是很高，但是如果后面再出现，这个惩罚会越来越高，直到后面再也不会出现这个词语了。

有点像是，`presence` 是一个布尔类型的变量，你出现就是 `true`，不出现就是 `false`，但是出现了多少次我并不是很关心。但是 `frequency` 就是，像是一个 `int` 类型，我会关心你出现的次数是多少。

总结：`presence_penalty` 的出现是为了让我们的对话能够「出现新主题」，但是 `frequency_penalty` 的出现意义在于在我们的对话中「抑制高频词」。

#### `response_format`

AI 大模型返回的输出的类型，提供了两种取值：`text` 和 `json_object`。默认是 `text`，也就是返回文本内容。

如果指定 `json-object` 的话，模型会**尽最大努力**返回一个 JSON 的结构体。这样会有什么好处呢？一些网络框架可能就直接用返回的 JSON 框架去嵌入到一些代码中，这样会让开发更简单些。

但是需要注意：

1. 如果真要这样做，单纯在这里指定 `json_object` 为返回的类型是不够的，因为虽然你指定输出类型为 `json` 类型，但是呢，`json` 是有结构的呀！你要一个什么样的 `json`，你的 `json` 中需要哪几个字段，每个字段的类型、取值范围是多少？这些都没有说。
2. 因为输出 `json` 会比较多，所以在接收到返回值的时候，需要看看返回值类型参数中的 `finish_reason`，如果是 `length`，那就要注意了，是不是本来 AI 可以生成更多，但是受限于长度，被截断了。那 `json` 作为一个语法还比较严格的结构体，从中间直接截断再直接部署到代码里，这会导致严重的错误。

这个值在请求的时候可以不设置或者设置为空，这样会使用默认值 `text`。

#### `stop`

控制文本生成中，如果输出什么词之后，就中断生成。

有两种接收类型：

- `string`，单个字符串
- `[]string`，字符串列表，就是很多个字符串

大概想到几个用途：

- 我们可以设置 `\n` 为 `stop` 的字符串，这样可以保证输出中肯定只会有一段话。
- 设置 `end`、`End`、`结束` 之类的关键字，可以让输出中出现这样的词之后，就立马结束（虽然不知道这样做的意义……）。
- 屏蔽一些碰都不能碰的滑梯？

比如说我们还是设置：

```json
    "messages": [
        {
            "content": "你是一个通用的AI助手，很擅长为我解答问题。",
            "role": "system"
        },
        {
            "content": "你可以为我讲一个简单的笑话吗？",
            "role": "user"
        }
    ],
	// ......
    "stop": "笑话",
```

然后 AI 会输出：

>当然可以！这里有一个简单的

这个参数的取值默认是 `null`。

> 后记：
>
> ![image-20250529173500606](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20250529173500606.png)
>
> CherryStudio 中，DeepSeek 上面还在说这种做法存在严重缺陷，但是后面又把自己的回答掐断了。今天见到的最好笑的笑话🤣。

#### `stream`

就是输出的时候要不要使用流式输出。如果使用流式输出，输出的内容就是一段一段的，AI 输出的内容不会打包成完整的一段话再返回，而是每生成一个 token 就返回一次。

例如说，我们使用如下的 golang 接收方式：

```go
	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
```

那么之后 `body` 中就会持续受到数据块，最后将所有数据块拼接成一个字符串，每个数据块都是以 `data:` 开头，数据块之间用 `\n\n` 来连接。最后，再输出一个 `data: [NONE]`。

例如，我们如果使用 `fmt.Println(string(body))`，会发现 `body` 中的数据大概是：

```go
data: {"id":"728c5695-1c40-4d02-8a60-d7ebd3cf7590","object":"chat.completion.chunk","created":1748586048,"model":"deepseek-chat","system_fingerprint":"fp_8802369eaa_prod0425fp8","choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":null,"finish_reason":null}]}

data: {"id":"728c5695-1c40-4d02-8a60-d7ebd3cf7590","object":"chat.completion.chunk","created":1748586048,"model":"deepseek-chat","system_fingerprint":"fp_8802369eaa_prod0425fp8","choices":[{"index":0,"delta":{"content":"当然"},"logprobs":null,"finish_reason":null}]}

data: {"id":"728c5695-1c40-4d02-8a60-d7ebd3cf7590","object":"chat.completion.chunk","created":1748586048,"model":"deepseek-chat","system_fingerprint":"fp_8802369eaa_prod0425fp8","choices":[{"index":0,"delta":{"content":"可以"},"logprobs":null,"finish_reason":null}]}

// ...
data: {"id":"728c5695-1c40-4d02-8a60-d7ebd3cf7590","object":"chat.completion.chunk","created":1748586048,"model":"deepseek-chat","system_fingerprint":"fp_8802369eaa_prod0425fp8","choices":[{"index":0,"delta":{"content":""},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":23,"completion_tokens":38,"total_tokens":61,"prompt_tokens_details":{"cached_tokens":0},"prompt_cache_hit_tokens":0,"prompt_cache_miss_tokens":23}}

data: [DONE]
```

其中的块主要有几种类型：

**【初始块】（角色声明）：**

```json
{
  "id": "728c5695-1c40-4d02-8a60-d7ebd3cf7590",
  "object": "chat.completion.chunk",
  "created": 1748586048,
  "model": "deepseek-chat",
  "system_fingerprint": "fp_8802369eaa_prod0425fp8",
  "choices": [{
    "index": 0,
    "delta": {
      "role": "assistant",  // 声明AI角色
      "content": ""         // 初始内容为空
    },
    "logprobs": null,
    "finish_reason": null   // 生成未结束
  }]
}
```

建立对话上下文，像是一个 AI 发出消息之前的声明，声明接下来发出来的消息是 `assistant` 的回复。其中的 `content` 部分为空，仅用来设置角色。

**【内容增量块】（多次出现）**

```json
{
  "id": "728c5695-1c40-4d02-8a60-d7ebd3cf7590",
  ... // 元数据相同
  "choices": [{
    "index": 0,
    "delta": {
      "content": "当然"  // 实际生成的内容片段
    },
    "logprobs": null,
    "finish_reason": null
  }]
}
```

这部分就是 AI 生成的回复了，只不过每次生成的内容都是一个分词之后的 token。每个块中仅仅包含新增的内容，生成的回复内容就放在 `content` 中。例如，第一个增量块中，`content` 的内容是 `当然`，第二个增量块中，`content` 的内容是 `可以`，之后再下一个就是 `！`，以此类推。

有的时候也会发送一些空的 `content` 块，比如说 `content: ""`，表示心跳或处理中。

**【结束块】（关键信息）**

```json
{
  "id": "728c5695-1c40-4d02-8a60-d7ebd3cf7590",
  ... // 元数据相同
  "choices": [{
    "index": 0,
    "delta": {
      "content": ""  // 内容结束
    },
    "logprobs": null,
    "finish_reason": "stop"  // 停止原因
  }],
  "usage": {  // 关键！Token使用统计
    "prompt_tokens": 23,         // 问题消耗Token
    "completion_tokens": 38,     // 回答消耗Token
    "total_tokens": 61,          // 总Token
    "prompt_tokens_details": {   // 详细统计
      "cached_tokens": 0
    },
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 23
  }
}
```

这个块跟前面的块中的消息有几个不一样，其中一个是 `finish_reason: "stop"`，前面其他的 `finish_reason` 都是 `null`，说明前面的都没有停止，一直到这一条消息这里，生成才停止了。

以及还会包含本次对话的一些信息，比如本次 API 调用所消耗的输入 `token`、输出 `token`，还有使用的总 `token`，以及缓存是否命中之类的信息。

生成的文本，就是所有的块中的 `choices.delta.content` 拼接到一起之后的结果。

#### 使用 SSE 处理 Stream

```go
func TestStreamSSE(t *testing.T) {
	// io.ReadAll() 会一直阻塞直到流完全结束，失去流式处理的优势。
	// 推荐使用 SSE 解析器进行处理
	url := "https://api.deepseek.com/chat/completions"
	method := "POST"

	// 读取 json 文件内容
	jsonBytes, err := os.ReadFile("request.json")
	if err != nil {
		panic(err)
	}

	payload := strings.NewReader(string(jsonBytes))

	client := &http.Client{}
	req, err := http.NewRequest(method, url, payload)

	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Accept", "application/json")
	req.Header.Add("Authorization", "Bearer sk-ef1919aca52c421a9b6d1e60756e8acd")

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer res.Body.Close()

	scanner := bufio.NewScanner(res.Body)
	scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
		// 自定义 SSE 分割逻辑
		if i := bytes.Index(data, []byte("\n\n")); i >= 0 {
			return i + 2, data[:i], nil
		}
		return 0, nil, nil
	})

	for scanner.Scan() {
		event := scanner.Text()
		if strings.HasPrefix(event, "data: ") {
			jsonData := event[6:] // 去掉 "data: " 前缀

			// 处理结束标记
			if jsonData == "[DONE]" {
				break
			}

			// 解析 JSON
			var resp struct {
				Choices []struct {
					Delta struct {
						Content string `json:"content"`
					}
				}
				Usage *struct {
					PromptTokens     int `json:"prompt_tokens"`
					CompletionTokens int `json:"completion_tokens"`
					TotalTokens      int `json:"total_tokens"`
				}
			}
			json.Unmarshal([]byte(jsonData), &resp)

			// 处理内容
			if len(resp.Choices) > 0 {
				fmt.Print(resp.Choices[0].Delta.Content)
			}

			// 处理用量统计
			if resp.Usage != nil {
				fmt.Printf("\nUsage: %+v\n", resp.Usage)
			}
		}
	}

}

```

运行之后会**陆陆续续**输出：

```go
苹果是一种营养丰富的水果，具有以下主要健康价值：

// ...

苹果的"每天一苹果，医生远离我"虽夸张，但其均衡营养确为健康饮食的良好选择。
Usage: &{PromptTokens:22 CompletionTokens:294 TotalTokens:316}
```

其中，`SSE(Server-Sent Events)` 处理流式的请求相比 `ReadAll()` 有以下几个优势：

- 内存占用比较小。`ReadAll()` 是将所有的返回体内容都放到一起，然后一块返回给用户。这样就会导致，如果返回的内容比较多，会一下占满内存。但是如果使用 SSE，接收到一小块内容之后就会立马将这一小块内容倒出来，然后再去接受新的内容。这样需要放在内存中的数据就不会特别大。
- 可以让用户看到即时响应的效果。`ReadAll()` 是将所有数据都放到一起，所有的数据都接收完毕之后，才会一次全部输出。但是流式输出就可以实现：返回多少内容，输出多少内容。这样从视觉效果上就实现了实时性。
- 可以在中间随时停止继续接受。比如说我的一个业务需求就是，在中间接收到某一个消息（比如其中包含 `End` 的消息）之后，后面所有的数据就都不要了，停止数据的接收。`SSE` 可以实现这个需求。

#### ~~`stream_options`~~

这个选项只有 `stream` 设置为 `true` 的时候才可以使用。我们就用 `ReadAll()` 方法来看区别。

如果只是设置了 `stream`，但是没有设置额外的 `stream_options`，最后的输出：

```go
data: {"id":"cc216c42-98fa-4f26-ade8-aa11feed1e11","object":"chat.completion.chunk","created":1748589142,"model":"deepseek-chat","system_fingerprint":"fp_8802369eaa_prod0425fp8","choices":[{"index":0,"delta":{"content":"）。"},"logprobs":null,"finish_reason":null}]}

data: {"id":"cc216c42-98fa-4f26-ade8-aa11feed1e11","object":"chat.completion.chunk","created":1748589142,"model":"deepseek-chat","system_fingerprint":"fp_8802369eaa_prod0425fp8","choices":[{"index":0,"delta":{"content":""},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":22,"completion_tokens":230,"total_tokens":252,"prompt_tokens_details":{"cached_tokens":0},"prompt_cache_hit_tokens":0,"prompt_cache_miss_tokens":22}}

data: [DONE]
```

如果设置：

```json
    "stream": true,
    "stream_options": {
        "include_usage": true
    },
```

那么调用 API 就会输出：

```go
ata: {"id":"4c9d1c89-5521-4c41-88aa-4fad4cd85bf1","object":"chat.completion.chunk","created":1748589225,"model":"deepseek-chat","system_fingerprint":"fp_8802369eaa_prod0425fp8","choices":[{"index":0,"delta":{"content":"。"},"logprobs":null,"finish_reason":null}],"usage":null}

data: {"id":"4c9d1c89-5521-4c41-88aa-4fad4cd85bf1","object":"chat.completion.chunk","created":1748589225,"model":"deepseek-chat","system_fingerprint":"fp_8802369eaa_prod0425fp8","choices":[{"index":0,"delta":{"content":""},"logprobs":null,"finish_reason":"stop"}],"usage":{"prompt_tokens":22,"completion_tokens":267,"total_tokens":289,"prompt_tokens_details":{"cached_tokens":0},"prompt_cache_hit_tokens":0,"prompt_cache_miss_tokens":22}}

data: [DONE]
```

可以看到输出的内容完全一样！

情况是就算没有在 `stream_options` 中明确声明 `include_usage`，也会输出实际使用的 `Usage`。

推测是这个选项已经被移除了。

#### `temperature` 和 `top_p`

作用差不多，都是用来调整模型的活跃度的。

如果 `temprature` 设置的比较高，那么输出的文本中会有更多不确定的词，比较适合用于创作一些诗词之类的东西。如果 `temprature` 设置的比较低，那么输出的文本就会更加保守，这时候就比较适合去写一些综述之类的文档，这样信息会更加准确。

`top_p` 也是差不多的效果，值设置的比较高，生成内容自由度就更高，比较低的话，生成内容就比较保守。

但是实现原理是不一样的。

比如说模型对下一个出现的词的概率是：

| A：0.4 | B：0.3 | C：0.2 | D：0.1 |
| ------ | ------ | ------ | ------ |

那么如果我们设置了低 `temprature`，那么之后可能会变成：

| A：0.6 | B：0.2 | C：0.15 | D：0.05 |
| ------ | ------ | ------- | ------- |

意思就是原本出现频率就比较高的词，之后出现频率会更高；原本就比较低的词，之后出现的频率也会更低。

如果我们是设置了低的 `top_p`，那么原本出现频率比较低的选项 C 和 D 就会直接被删去，出现概率变成下面这样：

| A：0.57 | B：0.43 |
| ------- | ------- |

但是要注意，`temperature` 和 `top_p` 不可以同时修改，会导致不可预测的后果！









