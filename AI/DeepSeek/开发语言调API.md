# 开发语言调 API

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











