# Counter

## 源码分析

### 边缘端（counter-mapper）

#### `device/device.go`

首先是常量定义：

```go
const (
	ON = iota
    OFF
)
```

这里定义了两个常量 ON 和 OFF，分别代表设备的开启和关闭状态。第一个常量 ON 会被赋值为 0，第二个常量 OFF 会被赋值为 1。

然后是 Counter 类型：

```go
type Counter struct {
    status chan int  // 用于接收设备的状态
    handle func(int)  // 用于处理计数结果的函数
}
```

其中的 `status` 是一个通道，用于接收设备的状态（ON 或 OFF）。`handel` 是一个函数类型，用于接收计数器的当前值并进行处理。

`runDevice` 方法：

```go
func (counter *Counter) runDevice(interrupt chan struct{}) {
    data := 0

    for {
        select {
        case <-interrupt:
            counter.handle(0)
            return
        default:
            data++
            counter.handle(data)
            fmt.Println("Counter value:", data)
            time.Sleep(1 * time.Second)
        }
    }
}
```

- `runDevice` 是 `Counter` 结构体的方法，用来模拟设备的工作。它会不断增加 `data` 的值（模拟计数），每秒输出一次计数器的值。
- `interrupt` 是一个通道，用于接收中断信号，当收到中断信号的时候，调用 `counter.handle(0)` 处理并终止计数。
- `select` 语句用于等待接收通道中的数据。如果接收到 `interrupt` 的数据（即中断信号），则调用 `counter.handle(0)` 并返回终止计数；否则每秒增加计数并输出。

`initDevice` 方法：

```go
func (counter *Counter) initDevice() {
    interrupt := make(chan struct{})

    for {
        select {
        case status := <-counter.status:
            if status == ON {
                go counter.runDevice(interrupt)
            }
            if status == OFF {
                interrupt <- struct{}{}
            }
    }
}
```

- `initDevice` 方法负责启动和控制设备。它从 `counter.status` 通道接收设备的状态（`ON` 或 `OFF`）。
- 当设备状态是 `ON` 的时候，启动一个新的 goroutine 来运行 `runDevice` 方法（即开始计数）。
- 当设备状态是 `OFF` 的时候，向 `interrupt` 通道发送一个信号，以终止设备的计数。

开启和关闭设备的方法：

```go
func (counter *Counter) TurnOn() {
    counter.status <- ON
}

func (counter *Counter) TurnOff() {
    counter.status <- OFF
}
```

- `TurnOn` 和 `TurnOff` 方法分别用于设置设备的状态为 `ON` 或 `OFF`。
- 这两个方法通过向 `counter.status` 通道发送信号来控制设备的状态。

`NewCounter` 函数：

```go
func NewCounter(h func(x int)) *Counter {
    counter := &Counter{
        status: make(chan int),
        handle: h,
    }

    go counter.initDevice()

    return counter
}
```

- `NewCounter` 是工厂函数，用于创建并初始化一个 `Counter` 对象。
- 在创建 `Counter` 示例时，会传入一个处理函数 `h`，用于每次处理计数器更新时的行为（例如打印或记录日志）。
- 在返回 `Counter` 对象之前，它启动了一个 goroutine 来执行 `initDevice` 方法，从而开始等待并处理设备状态的变化。

`closeCounter` 函数：

```go
func CloseCounter(counter *Counter) {
    close(counter.status)
}
```

- `CloseCounter` 函数用于关闭 `counter.status` 通道，停止设备的状态监听。
- 一旦通道被关闭，`initDevice` 方法中的 `select` 将不再能够从 `counter.status` 通道读取数据，最终导致整个设备的停止。

总结：

这段代码模拟了一个简单的设备控制系统。设备通过 `ON` 和 `OFF` 信号进行控制，`runDevice` 方法会持续进行计数，直到收到外部中断信号为止。`Counter` 类型使用了 Go 的 goroutine 来并发处理设备的状态变化，并且可以通过外部的 `handle` 函数来响应计数结果。

- `Counter` 类型是通过控制设备状态（`ON` 和 `OFF`）来实现设备的开启与关闭。
- 通过 `go counter.runDevice(interrupt)` 实现并发执行设备计数，利用 `select` 来处理中断和计数。
- 设计中的通道（`status` 和 `interrupt`）用于协调设备的状态管理和计数过程。

#### `main.go`

这段代码是一个完整的程序，主要实现了通过 MQTT 协议与设备通信，控制计数器的开关。该程序利用了 KubeEdge 和 MQTT 组件，模拟了一个设备（`counter`）的远程控制，设备通过 MQTT 定于和发布设备双胞胎（Device Twin）数据。

以下是逐部分的详细分析：

**首先是引入依赖：**

```go
import (
        "encoding/json"
        "fmt"
        "os"
        "os/signal"
        "strconv"
        "syscall"

        mqtt "github.com/eclipse/paho.mqtt.golang"

        "github.com/kubeedge/examples/kubeedge-counter-demo/counter-mapper/device"
        "github.com/kubeedge/kubeedge/cloud/pkg/devicecontroller/types"
)
```

- 引入了几个包，其中 `github.com/eclipse/paho.mqtt.golang` 是用于 MQTT 客户端的 Go 库，`github.com/kubeedge/kubeedge/cloud/pkg/devicecontroller/types` 是 KubeEdge 设备控制器的相关类型定义。
- 其他包如 `encoding/json`、`fmt`、`os`、`syscall` 等则是用于数据处理、打印、系统信号处理等功能。

**常量定义：**

```go
const (
    mqttUrl = "tcp://127.0.0.1:1883"
    topic = "$hw/events/device/counter/twin/update"
)
```

- `mqttUrl` 是 MQTT 代理的地址（本地的 1883 端口）。
- `topic` 是 MQTT 消息的主题，用于更新设备状态（即设备双胞胎的状态更新）。

**设备消息结构体定义：**

定义了几个结构体，用于封装设备双胞胎的消息格式：

```go
type BaseMessage struct {
        EventID   string `json:"event_id"`
        Timestamp int64  `json:"timestamp"`
}

type TwinValue struct {
        Value    *string        `json:"value, omitempty"`
        Metadata *ValueMetadata `json:"metadata,omitempty"`
}

type ValueMetadata struct {
        Timestamp int64 `json:"timestamp, omitempty"`
}

type TypeMetadata struct {
        Type string `json:"type,omitempty"`
}

type TwinVersion struct {
        CloudVersion int64 `json:"cloud"`
        EdgeVersion  int64 `json:"edge"`
}

type MsgTwin struct {
        Expected        *TwinValue    `json:"expected,omitempty"`
        Actual          *TwinValue    `json:"actual,omitempty"`
        Optional        *bool         `json:"optional,omitempty"`
        Metadata        *TypeMetadata `json:"metadata,omitempty"`
        ExpectedVersion *TwinVersion  `json:"expected_version,omitempty"`
        ActualVersion   *TwinVersion  `json:"actual_version,omitempty"`
}

type DeviceTwinUpdate struct {
        BaseMessage
        Twin map[string]*MsgTwin `json:"twin"`
}
```

这些结构体用于封装设备的状态更新信息（设备双胞胎文档）。主要的结构体是 `DeviceTwinUpdate`，它包含了 `BaseMessage`（事件信息）和 `Twin`（设备双胞胎数据）。每个 `MsgTwin` 可以包含设备的预期状态（Expected）、实际状态（`Actual`），以及元数据（例如时间戳）。

**函数：`createAcutalUpdateMessage`**

```go
func createActualUpdateMessage(actualValue string) DeviceTwinUpdate {
        var deviceTwinUpdateMessage DeviceTwinUpdate
        actualMap := map[string]*MsgTwin{"status": {Actual: &TwinValue{Value: &actualValue}, Metadata: &TypeMetadata{Type: "Updated"}}}
        deviceTwinUpdateMessage.Twin = actualMap
        return deviceTwinUpdateMessage
}
```

- 该函数用于创建设备的状态更新消息，接收一个字符串 `actualValue`，然后将其封装为 `DeviceTwinUpdate` 消息。
- `actualMap` 是一个映射，表示设备的实际状态。

**函数：`publishToMqtt`**

```go
func publishToMqtt(data int) {
        updateMessage := createActualUpdateMessage(strconv.Itoa(data))
        twinUpdateBody, _ := json.Marshal(updateMessage)

        token := cli.Publish(topic, 0, false, twinUpdateBody)

        if token.Wait() && token.Error() != nil {
                fmt.Println(token.Error())
        }
}
```

- 该函数用于将计数器的当前值通过 MQTT 发布到 Device Twin 更新的主题。
- `data` 被转换为字符串，然后通过 `createActualUpdateMessage` 生成设备的状态更新消息。
- `cli.Publish` 用于发布消息到 MQTT 代理。

**函数：`connectToMqtt`**

```go
func connectToMqtt() mqtt.Client {
        opts := mqtt.NewClientOptions()
        opts.AddBroker(mqttUrl)

        cli = mqtt.NewClient(opts)

        token := cli.Connect()
        if token.Wait() && token.Error() != nil {
                fmt.Println(token.Error())
        }

        return cli
}
```

- 该函数用于创建一个 MQTT 客户端并连接到代理。
- `mqtt.NewClientOptions()` 创建一个新的 MQTT 客户端选项并设置代理地址，然后使用这些选项创建客户端 `cli`。
- 连接后返回 `cli`。

**`main` 函数：**

```go
func main() {
        stopchan := make(chan os.Signal)
        signal.Notify(stopchan, syscall.SIGINT, syscall.SIGKILL)
        defer close(stopchan)

        cli = connectToMqtt()

        // Link to pseudo device counter
        ctr := counter.NewCounter(publishToMqtt)

        current_status := "OFF"

        token := cli.Subscribe(topic+"/document", 0, func(client mqtt.Client, msg mqtt.Message) {
                Update := &types.DeviceTwinDocument{}
                err := json.Unmarshal(msg.Payload(), Update)
                if err != nil {
                        fmt.Printf("Unmarshal error: %v\n", err)
                }

                cmd := *Update.Twin["status"].CurrentState.Expected.Value

                if cmd == "ON" && cmd != current_status {
                        ctr.TurnOn()
                        fmt.Printf("turn on counter.\n")
                }

                if cmd == "OFF" && cmd != current_status {
                        ctr.TurnOff()
                        fmt.Printf("turn off counter.\n")
                }

                current_status = cmd
        })

        if token.Wait() && token.Error() != nil {
                fmt.Println(token.Error())
        }

        select {
        case <-stopchan:
                fmt.Printf("Interrupt, exit.\n")
                break
        }
}
```

- `main` 函数是程序的入口，首先会设置一个 `stopchan` 来监听系统中断信号（如 `SIGINT` 和 `SIGKILL`），在接收到中断信号时退出程序。
- 然后调用 `connectToMqtt` 来连接到 MQTT 代理，并初始化计数器 `ctr`。
- 订阅主题 `topic/document`，一旦接收到消息，解析出设备的状态命令（`ON` 或 `OFF`），并根据命令调用 `TurnOn` 或 `TurnOff` 来控制计数器的开关。
- `current_status` 用于跟踪当前设备的状态，防止重复控制设备。

**总结：**

- 该程序通过 MQTT 协议与远程设备进行交互，控制一个模拟计数器设备的开启与关闭。设备的状态更新通过双胞胎文档（Device Twin）实现。
- 使用了 KubeEdge 中的设备控制机制（例如 `DeviceTwin`），并通过 `paho.mqtt.golang` 实现与 MQTT 代理的通信。
- 程序通过订阅设备状态更新主题来动态控制设备，通过 `counter` 包模拟计数器的运行。





















