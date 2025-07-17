# ChatApp

## Golang DeepSeek-V3

```go
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
)

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
	Stream   bool      `json:"stream"`
}

func main() {
	url := "https://api.deepseek.com/chat/completions"
	apiKey := "密钥密钥密钥"

	// 初始化对话历史
	var conversation []Message

	conversation = append(conversation, Message{
		Role:    "system",
		Content: "你是一个致力于以安全、有益、尊重的方式为用户提供广泛支持的通用型AI助手。始终以温暖、耐心和富有同理心的语气交流。努力理解用户的核心需求，提供清晰、准确的信息（明确标注不确定性），并主动提出可行的方案或思路。乐于进行头脑风暴和创造性合作，通过提问来深入了解需求。请严格遵守以下规则：1. **绝对不说谎**或捏造事实；2. **拒绝所有非法、有害、危险或不道德的请求**；3. **不泄露、推测或讨论未公开的个人隐私信息**；4. 保持中立与客观，在争议话题中平衡呈现不同观点（如适用）；5. 明确告知用户你是AI，能力有限，信息可能不完美，建议用户自行验证重要结论。始终使用礼貌用语，表达尊重和乐于助人的态度。",
	})

	reader := bufio.NewReader(os.Stdin)

	fmt.Println("===   DeepSeek V3 Chat App    ===")
	fmt.Println("Enter `exit` or `quit` to finish.")

	for {
		fmt.Print("\n\n🤔 You: ")
		userInput, err := reader.ReadString('\n')
		if err != nil {
			fmt.Println("Error reading input:", err)
			continue
		}

		userInput = strings.TrimSpace(userInput)
		if strings.ToLower(userInput) == "exit" || strings.ToLower(userInput) == "quit" {
			fmt.Println("Goodbye!")
			break
		}

		// 添加用户对话到对话历史
		conversation = append(conversation, Message{
			Role:    "user",
			Content: userInput,
		})

		// 创建请求体
		requestBody := ChatRequest{
			Model:    "deepseek-chat",
			Messages: conversation,
			Stream:   true,
		}

		jsonBody, err := json.Marshal(requestBody)
		if err != nil {
			fmt.Println("Error creating request:", err)
			continue
		}

		// 发送请求
		req, err := http.NewRequest("POST", url, strings.NewReader(string(jsonBody)))
		if err != nil {
			fmt.Println("Error creating request:", err)
			continue
		}

		req.Header.Add("Content-Type", "application/json")
		req.Header.Add("Accept", "application/json")
		req.Header.Add("Authorization", apiKey)

		client := &http.Client{}
		res, err := client.Do(req)
		if err != nil {
			fmt.Println("Error sending request:", err)
			continue
		}
		defer res.Body.Close()

		// 处理流式响应
		var assistantResponse strings.Builder
		scanner := bufio.NewScanner(res.Body)
		scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
			if i := bytes.Index(data, []byte("\n\n")); i >= 0 {
				return i + 2, data[:i], nil
			}
			return 0, nil, nil
		})

		fmt.Print("\n🧐 Assistant: ")
		for scanner.Scan() {
			event := scanner.Text()
			if strings.HasPrefix(event, "data: ") {
				jsonData := event[6:] // 去掉 "data: " 前缀
				if jsonData == "[DONE]" {
					break
				}

				var resp struct {
					Choices []struct {
						Delta struct {
							Content string `json:"content"`
						}
					}
				}

				if err := json.Unmarshal([]byte(jsonData), &resp); err != nil {
					continue
				}

				if len(resp.Choices) > 0 && resp.Choices[0].Delta.Content != "" {
					content := resp.Choices[0].Delta.Content
					fmt.Print(content)
					assistantResponse.WriteString(content)
				}
			}
		}

		// 添加助手回复到对话历史
		if assistantResponse.Len() > 0 {
			conversation = append(conversation, Message{
				Role:    "assistant",
				Content: assistantResponse.String(),
			})
		}
	}

}

```





