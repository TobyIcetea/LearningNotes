# 对话-Tools专题

## API Tools 描述

### Request - tools

表示模型可能会调用的 tool 的列表。目前，只支持 function 作为大预言模型的 tools，所以基本可以将 tools 和 function 等同。

tools 是一个 tool 的列表，所以在请求的时候可以一次传入多个 tool，这个列表中的限制是 128 个。

数据类型如下所示：

```yaml
tools: []Object
	type: string (Tool 的类型，目前只支持 function)
	function: Object
		description: string（这个 function 的功能描述，供模型理解何时调用这个 function）
		name: string（要调用的 function 的名称）
		parameters: Object（function 的输入参数）
			property: any（function 的输入参数，以 JSON Schema 对象描述）
```

并且有一个 python 代码的输入示例：

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of an location, the user shoud supply a location first",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]
```

### Request - tool_choice

控制模型调用 tool 的行为，例如：

- `none`：模型不会调用任何 tool，而是生成一条消息。
- `auto`：模型自己决定要不要去调用 tool，调用一个还是多个 tool。
- `required`：指定模型必须调用哪个或哪些 tool。

如果没有 tool 存在，默认值为 `none`。如果有 tool 存在，默认值为 `auto`。

### Response

Reponse 的结构体描述如下：

```yaml
ChatCompletion:
	id: string（该对话的唯一标识符）
	choices: []Object（模型生成的 completion 选择列表）
		finish_reason: string（模型停止生成 token 的原因，比如 stop、length、content_filter、tool_calls）
		index: int（这个 completion 在 choices 中的索引）
		message: Object（模型升成的 completion 的具体消息）
			content: string（消息的内容）
			reasoning_content: string（推理过程，R1 之类的推理模型才有）
			tool_calls: []Object（模型升成的 tool 调用列表，就是调用了哪些 tool）
				id: string（本次 Tool 调用的 ID）
				type: string（Tool 调用的类型，目前只支持 function）
				function: Object（模型调用的 function）
					name: string（模型调用的 function 的名字）
					arguments: string（要调用的 function 的参数，JSON 格式，由模型生成）
			role: string（生成这条消息的角色）
	// ...
```

## 代码

### `main.go`

```go
package main

import (
	"fmt"
	"log"
	"strings"
)

func main() {
	// 获取 API 密钥
	apiKey := "sk-ef1919aca52c421a9b6d1e60756e8acd"

	// 初始化对话历史
	messages := []Message{
		{
			Role:    "system",
			Content: "你是一个有用的天气助手，可以使用工具查询实时天气信息。",
		},
	}

	fmt.Println("=== DeepSeek V3 Tools ===")
	fmt.Println("输入 `exit` 结束对话")
	fmt.Println()

	// 定义天气查询工具
	weatherTool := Tool{
		Type: "function",
		Function: &Function{
			Name:        "get_current_weather",
			Description: "获取指定城市的当前天气信息",
			Parameters: Parameters{
				Type: "object",
				Properties: map[string]Property{
					"location": {
						Type:        "string",
						Description: "城市名称，如北京、上海",
					},
					"unit": {
						Type: "string",
						Enum: []string{"celsius", "fahrenheit"},
					},
				},
				Required: []string{"location"},
			},
		},
	}

	// 主对话循环
	for {
		fmt.Print("\n🥵 你：")
		var userInput string
		fmt.Scanln(&userInput)

		if strings.ToLower(userInput) == "exit" {
			break
		}

		// 添加用户信息
		messages = append(messages, Message{
			Role:    "user",
			Content: userInput,
		})

		// 调用 DeepSeek API
		response, err := callDeepSeekAPI(apiKey, messages, []Tool{weatherTool})
		if err != nil {
			log.Printf("API 调用失败：%v", err)
			continue
		}

		// 处理响应
		if len(response.Choices) > 0 {
			choice := response.Choices[0]
			message := choice.Message

			// 检查是否有工具调用
			if len(message.ToolCalls) > 0 {
				fmt.Println("\n🔨 模型请求调用工具...")

				// 先将模型的消息（包含工具调用）添加到历史
				messages = append(messages, message)

				for _, toolCall := range message.ToolCalls {
					fmt.Printf("🛠️ 调用工具：%s\n", toolCall.Function.Name)
					fmt.Printf("🧐 参数：%s\n", toolCall.Function.Arguments)

					// 处理工具调用
					result := handleToolCall(toolCall)

					// 添加工具响应到消息历史
					messages = append(messages, Message{
						Role:       "tool",
						Content:    result,
						ToolCalls:  []ToolCall{toolCall},    // 添加工具调用引用
						ToolCallID: message.ToolCalls[0].ID, // 传入上一个回复的 ToolCallID
					})
				}

				// 再次调用 API 获取最终回复
				finalResponse, err := callDeepSeekAPI(apiKey, messages, []Tool{weatherTool})
				if err != nil {
					log.Printf("最终回复 API 调用失败：%v", err)
					continue
				}

				if len(finalResponse.Choices) > 0 {
					finalChoice := finalResponse.Choices[0]
					fmt.Printf("\n🤖 DeepSeek: %s\n", finalChoice.Message.Content)
					messages = append(messages, finalChoice.Message)
				}
			} else {
				// 没有工具调用，直接显示回复
				fmt.Printf("\n🤖 DeepSeek: %s\n", message.Content)
				messages = append(messages, message)
			}
		}
	}

	fmt.Println("\n对话结束!")
}

```

### `utils.go`

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

// 调用 DeepSeek API，传入 messages 和 tools，发送一次 http 请求，返回的是一个 http 的 Response
func callDeepSeekAPI(apiKey string, messages []Message, tools []Tool) (*DeepSeekResponse, error) {
	requestBody := DeepSeekRequest{
		Model:       "deepseek-chat",
		Messages:    messages,
		Tools:       tools,
		ToolChoice:  "auto",
		Temperature: 0.7,
	}

	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return nil, fmt.Errorf("JSON 编码失败：%w", err)
	}

	req, err := http.NewRequest("POST", "https://api.deepseek.com/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建请求失败：%w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("API 请求失败：%w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API 返回错误状态：%d, 响应: %s", resp.StatusCode, string(body))
	}

	var response DeepSeekResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("解析响应失败：%w", err)
	}

	return &response, nil
}

// 处理工具调用
func handleToolCall(toolCall ToolCall) string {
	switch toolCall.Function.Name {
	case "get_current_weather":
		// 解析参数
		var args struct {
			Location string `json:"location"`
			Unit     string `json:"unit"`
		}
		if err := json.Unmarshal([]byte(toolCall.Function.Arguments), &args); err != nil {
			return `{"error": "参数解析失败"}`
		}

		// 获取天气数据
		weather := getCurrentWeather(args.Location, args.Unit)

		// 转换为 JSON
		jsonData, err := json.Marshal(weather)
		if err != nil {
			return `{"error": "结果序列化失败"}`
		}

		return string(jsonData)
	default:
		return `{"error": "未知工具调用"}`
	}
}

// 模拟天气 API
func getCurrentWeather(location string, unit string) WeatherData {
	// 默认天气数据
	defaultWeather := WeatherData{
		Temperature: 20,
		Unit:        "celsius", // 修正拼写
		Condition:   "晴朗",
		Humidity:    50,
	}

	// 设置单位
	if unit == "" {
		unit = "celsius"
	}

	// 城市天气数据
	cityWeather := map[string]WeatherData{
		"北京": {Temperature: 25, Unit: "celsius", Condition: "晴朗", Humidity: 45},
		"上海": {Temperature: 28, Unit: "celsius", Condition: "多云", Humidity: 65},
		"广州": {Temperature: 32, Unit: "celsius", Condition: "雷阵雨", Humidity: 80},
		"深圳": {Temperature: 30, Unit: "celsius", Condition: "阵雨", Humidity: 75},
		"纽约": {Temperature: 72, Unit: "fahrenheit", Condition: "小雨", Humidity: 60},
	}

	// 查找城市天气
	if weather, ok := cityWeather[location]; ok {
		// 如果需要转换单位
		if unit != weather.Unit {
			if unit == "celsius" && weather.Unit == "fahrenheit" {
				weather.Temperature = (weather.Temperature - 32) * 5 / 9
				weather.Unit = "celsius"
			} else if unit == "fahrenheit" && weather.Unit == "celsius" {
				weather.Temperature = (weather.Temperature * 9 / 5) + 32
				weather.Unit = "fahrenheit"
			}
		}
		return weather
	}

	// 返回默认天气
	defaultWeather.Unit = unit
	return defaultWeather
}

```

### `entities.go`

```go
package main

// 定义 API 请求和响应结构体
type DeepSeekRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	Tools       []Tool    `json:"tools,omitempty"`
	ToolChoice  string    `json:"tool_choice,omitempty"`
	Temperature float32   `json:"temperature,omitempty"`
}

type Message struct {
	Role       string     `json:"role"`
	Content    string     `json:"content"`
	ToolCalls  []ToolCall `json:"tool_calls,omitempty"` // 添加工具调用字段
	ToolCallID string     `json:"tool_call_id"`
}

type Tool struct {
	Type     string    `json:"type"`
	Function *Function `json:"function,omitempty"`
}

type Function struct {
	Name        string     `json:"name"`
	Description string     `json:"description,omitempty"`
	Parameters  Parameters `json:"parameters"`
}

type Parameters struct {
	Type       string              `json:"type"`
	Properties map[string]Property `json:"properties"`
	Required   []string            `json:"required,omitempty"`
}

type Property struct {
	Type        string   `json:"type"`
	Description string   `json:"description,omitempty"`
	Enum        []string `json:"enum,omitempty"`
}

type DeepSeekResponse struct {
	ID      string   `json:"id"`
	Object  string   `json:"object"`
	Created int      `json:"created"`
	Model   string   `json:"model"`
	Choices []Choice `json:"choices"`
	Usage   Usage    `json:"usage"`
}

type Choice struct {
	Index        int     `json:"index"`
	Message      Message `json:"message"`
	FinishReason string  `json:"finish_reason"`
}

type Usage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

type ToolCall struct {
	ID       string       `json:"id"`
	Type     string       `json:"type"`
	Function FunctionCall `json:"function"`
}

type FunctionCall struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

// 模拟天气数据
type WeatherData struct {
	Temperature float64 `json:"temperature"`
	Unit        string  `json:"unit"`
	Condition   string  `json:"condition"`
	Humidity    int     `json:"humidity"`
}

```

## 调用示例

第一波我们先问一个跟天气没关系的问题：

```go
🥵 你：你好，你能介绍一下自己吗？
```

之后发现生成的 Response：

```go
{
    ID:20e3a76e-67e1-48d4-a429-7ba77ab4956b, 
    Object:chat.completion, 
    Created:1748955990, 
    Model:deepseek-chat, 
    Choices:[{0 {assistant 你好！我是一个智能天气助手，专门用来帮助你查询实时天气信息。无论是想知道某个城市当前的温度、天气状况，还是需要了解湿度、风速等详细信息，我都可以为你提供准确的数据。

    我的主要功能包括：
    1. **查询当前天气**：提供指定城市的实时天气情况，包括温度、天气状况（如晴、雨、多云等）、湿度、风速等。
    2. **单位选择**：支持摄氏度和华氏度两种温度单位。
    3. **快速响应**：只需告诉我你想查询的城市名称，我就能迅速为你提供天气信息。

    如果你有任何天气相关的需求，随时告诉我！ [] } stop}], 
    Usage:{162 128 290}
}
```

第二轮问一下跟天气有关的东西：

```go
🥵 你：我想知道北京的天气怎么样？
```

之后生成的 Response 有两个：

```go
{
    ID:57c779a6-bc49-411e-b9f6-63531524831d, 
    Object:chat.completion, 
    Created:1748956820, 
    Model:deepseek-chat, 
    Choices:[{0 {assistant  [{call_0_7d0d5b70-d669-4da6-8a41-35135b83f8ba function {get_current_weather {"location":"北京","unit":"celsius"}}}] } tool_calls}], 
    Usage:{256 25 281}
}
```

```go
{
    ID:4866e44c-2150-4be2-8c33-d94c78f030b3, 
    Object:chat.completion, 
    Created:1748956825, 
    Model:deepseek-chat, 
    Choices:[{0 {assistant 北京的当前天气是晴朗，温度为25°C，湿度为45%。天气状况非常适合外出活动！如果需要其他信息，随时告诉我哦！ 😊 [] } stop}], 
    Usage:{305 31 336}
}
```

并且本次一共使用的 `messages`：

```json
[
    {system 你是一个有用的天气助手，可以使用工具查询实时天气信息。 [] }

	{user 你好，你能介绍一下自己吗？ [] } 

	{assistant 你好！我是一个智能天气助手，专门用来查询和提供实时天气信息。我可以帮助你获取全球各地的当前天气情况，包括温度、天气状况、湿度、风速等数据。如果你需要查询某个城市的天气，只需要告诉我城市名称，我就可以为你提供最新的天气信息。另外，我还可以根据你的偏好，提供摄氏度或华氏度的温度数据。有什么天气相关的问题，随时问我哦！ 😊 [] } 

	{user 我想知道北京的天气怎么样？ [] } 

	{assistant  [{call_0_7d0d5b70-d669-4da6-8a41-35135b83f8ba function {get_current_weather {"location":"北京","unit":"celsius"}}}] } 

	{tool {"temperature":25,"unit":"celsius","condition":"晴朗","humidity":45} [{call_0_7d0d5b70-d669-4da6-8a41-35135b83f8ba function {get_current_weather {"location":"北京","unit":"celsius"}}}] call_0_7d0d5b70-d669-4da6-8a41-35135b83f8ba} 

	{assistant 北京的当前天气是晴朗，温度为25°C，湿度为45%。天气状况非常适合外出活动！如果需要其他信息，随时告诉我哦！ 😊 [] }
]
```

## 理解

一般的对话都是持续两轮：

1. `user` 给 AI 发送一个请求。
2. `assistant` 返回这个请求对应的回复。

但是如果有 tools 调用，一轮对话其实就是四个消息：

1. `user` 给 AI 发送一个请求，请求中带上 `tool` 和 `tool_choice` 之类的字段。
2. `assistant` 通过这个 `tool` 的 `description`，分析出我们本次应该调用这个 `tool`。之后返回一个消息，这个消息中的 `content` 是空的，但是其中的 `choice` 字段中的 `message` 字段的 `finish_reason` 变成了 `tool_call`，也就是因为要调用函数，才终止回复的。
3. 本地接收到请求之后，将 `assistant` 分析出要调用的本次 `tool` 的名字、参数等信息，去调用本次函数。本次处理完之后，结果包装一下，再传给 AI。这个传消息的时候，要确定本消息是在回复上面的哪个 `message`（一般就是上一个 `message`），且本条消息的 `role` 是 `tool`，表示是 `tool` 在发送这个请求。
4. `assistant` 接收到本地 `tool` 分析完的结果之后，将结果整合，最后整理成自然语言，再将消息传输回来。

通俗点说就是，我们在一开始给 AI 发请求的时候，就告诉了 AI，我们本地是有一些 tools 存在的！比如说我们本地有一个函数，可以动态获取一个地方的天气信息！（这部分就是 `Function` 中要写的 `Description`，AI 要根据这部分内容决定要不要调用函数），除此之外还给出了这个函数的调用需要用到什么参数。之后我们和 AI 的对话中要不要调用参数呢？DeepSeek 你自己决定去吧！

- 如果 AI 发现我们的对话内容和 `Description` 中说的东西压根没有交集，就不会调用函数，我们就是正常的交流。
- 如果某一次对话中 AI 觉得我们交流的东西确实用到这个函数了，可以通过这个函数来处理。它发的下一个请求就不是直接的回复了，而是一个想要调用本地函数的请求。如果这个本地解析到 AI “想调用哪个函数，想传入什么参数”之后，在本地调用好，之后再将函数的执行结果传递给 AI。AI 整理好我们执行的结果之后，再去生成最后的答案。









