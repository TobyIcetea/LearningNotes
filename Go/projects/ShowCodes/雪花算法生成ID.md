# golang 实现雪花算法

## 介绍

雪花算法是一个开源的 ID 生成算法。

传统上生成 ID，其实是一个比较头疼事。

如果全都使用时间戳，ID 就只是 ID，没什么区分性，而且如果数据量特别大，一下需要生成很多 ID，会造成有一些 ID 是重复的。

那如果在此基础上再加一些随机数？比如说我们让 ID 的组成变成：时间戳 + 随机数。这样起始也有问题，每次生成之后，都要检验一下，当前的 ID 是不是已经出现过了。实际上也要做一个去重的操作。

这时候就可以使用雪花算法，这是一种适合分布式集群中大数据量生成 ID 的一种方法。生成的时候，可以考虑到当前生成的时间、是在哪个机器上生成的、生成的时间是什么时候等因素。通过多种方式一起协同生成，从而生成一个具有标识性、唯一的 ID。

## ID 结构

标准的雪花算法是 64 位的。64 位数据中，我们赋给每一位数据特定的含义（有点类似于当时学计网的时候说的 TCP 封装成帧之类的？）。

比如这里我们使用如下的格式：

```go
0 | 41位时间戳 | 5位数据中心ID | 5位工作机器ID | 12位序列号
```

其中：

- 先导零是一个标志，固定写法，可以保证生成的结果是一个正数。
- 时间戳就是 Unix 时间戳，用来表示现在的时间。在本算法中，我们使用的是毫秒级别的时间戳。
- 数据中心 ID + 工作机器 ID，自己定义。数据中心 ID 我觉得可以定义成集群的 ID，机器 ID 就是集群中这个节点的 ID。实际上直接定义成 10 位工作机器 ID 也是一样的，主要就是做个标识。
- 序列号标识这个 ID 是这个时间戳（这一毫秒）中，出现的第几个 ID。我们使用 12 位序列号，就表示这一毫秒、这台机器上，最多只能出现 4096 个 ID。如果这台机器这一毫秒的申请数量大于了 4096，那就将请求推到下一毫秒。

注意：在生产环境中，可能发生时间的回调（例如使用 ntpdate 同步了一次时间，导致时间往前校正了 10ms）。这样可能会导致出现重复的 ID。代码中需要补充这方面的逻辑。

## 主要代码

### const

```go
// 定义雪花算法各部分的位数
const (
	epoch          = 1735689600000 // 2025-01-01 00:00:00 UTC，这是一个毫秒级的时间戳
	timestampBits  = 41            // 时间戳
	dataCenterBits = 5             // 数据中心ID
	machineIDBits  = 5             // 工作机器ID
	sequenceBits   = 12            // 序列号。同一毫秒内产生的序列号，支持每毫秒生成 4096 个 ID

	maxDataCenterID = -1 ^ (-1 << dataCenterBits) // 数据中心 ID 最大值(31)
	maxMachineID    = -1 ^ (-1 << machineIDBits)  // 工作机器 ID 最大值(31)
	maxSequence     = -1 ^ (-1 << sequenceBits)   // 序列号最大值(4095)

	timestampShift  = dataCenterBits + machineIDBits + sequenceBits // 时间戳偏移量
	dataCenterShift = machineIDBits + sequenceBits                  // 数据中心ID偏移量
	machineShift    = sequenceBits                                  // 机器ID偏移量
)
```

这部分代码是定义了一些参数。其中：

- `epoch` 标识我们的时间戳是从哪里作为起始的，这里我是选用了 2025 年 1 月 1 日。因为我们保存时间戳的时候，并不是直接保存获取到的 Unix 时间戳，而是将现在的时间戳和这个 `epoch` 做一个差值，只保存差值就行。
- `timestampBits`、`dataCenterBits`、`machineIDBits`、`sequenceBits` 标识我们的 64 位数据中，这几个部分分别占用多少位。这一共是 63 位，按顺序排列。组合的时候，最前面再加上一个 0。
- 计算 `maxDataCenterID` 的时候，首先 -1 的二进制表示是 `111...111`，将 -1 向左移动 5 位就是 `11...1100000`，之后再与 `11..111` 进行一个异或的操作，表示将每一位反转。最后得到的结果就是 `00...0011111`，也就是 `31`。起始这也能当一个掩码 mask 来用。其余的两个 `ID` 同理。
- `Shift` 标识这一位在组合的时候，需要向左移动多少位进行组合。参考我们上面给出的格式，就知道时间戳需要向左移动 `5+5+12` 位之后进行拼接。

### Snowflake struct

```go
// Snowflake 结构体
type Snowflake struct {
	mutex         sync.Mutex // 互斥锁
	lastTimestamp int64      // 上一次生成ID的时间戳
	dataCenterID  int64      // 数据中心ID
	machineID     int64      // 机器ID
	sequence      int64      // 序列号
}
```

结构体中包含：时间戳、数据中心 ID、机器 ID、序列号，最后再加上一个互斥锁，用来保证不要出现相同的 ID。

### NewSnowflake

```go
// NewSnowflake 创建雪花算法实例
func NewSnowflake(dataCenterID, machineID int64) (*Snowflake, error) {
	if dataCenterID < 0 || dataCenterID > maxDataCenterID {
		return nil, errors.New("dataCenterID 超出范围")
	}
	if machineID < 0 || machineID > maxMachineID {
		return nil, errors.New("machineID 超出范围")
	}

	return &Snowflake{
		mutex:         sync.Mutex{},
		lastTimestamp: 0,
		dataCenterID:  dataCenterID,
		machineID:     machineID,
		sequence:      0,
	}, nil
}
```

每台机器上运行一个，创建一个用来产生 ID 的 Snowflake 实体。其中的数据中心 ID + 机器 ID 是根据 ID 决定的，其他部分的内容之后运行的时候再传入。

### GenerateID

```go
// GenerateID 生成唯一 ID
func (s *Snowflake) GenerateID() (int64, error) {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	// 1. 获取当前时间戳
	current := time.Now().UnixNano() / 1000000  // 将时间戳转换为毫秒形式
	timestamp := current - epoch

	if timestamp < 0 {
		return 0, errors.New("时间戳小于 0")
	}

	// 2. 同一毫秒内生成序列号
	if timestamp == s.lastTimestamp {
		s.sequence = (s.sequence + 1) & maxSequence
		// 序列号用尽时，等待下一毫秒
		if s.sequence == 0 {
			for current <= s.lastTimestamp {
				current = time.Now().UnixNano() / 1000000
			}
			timestamp = current - epoch
		}
	} else {
		s.sequence = 0
	}

	// 3. 时间回拨检查
	if timestamp < s.lastTimestamp {
		return 0, errors.New("时间回拨！")
	}

	// 4. 更新最后时间戳
	s.lastTimestamp = timestamp

	// 拼接 ID 各部分
	id := (timestamp << timestampShift) |
		(s.dataCenterID << dataCenterShift) |
		(s.machineID << machineShift) |
		s.sequence

	return id, nil
}
```

## 全部代码

```go
package main

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

// 定义雪花算法各部分的位数
const (
	epoch          = 1735689600000 // 2025-01-01 00:00:00 UTC，这是一个毫秒级的时间戳
	timestampBits  = 41            // 时间戳
	dataCenterBits = 5             // 数据中心ID
	machineIDBits  = 5             // 工作机器ID
	sequenceBits   = 12            // 序列号。同一毫秒内产生的序列号，支持每毫秒生成 4096 个 ID

	maxDataCenterID = -1 ^ (-1 << dataCenterBits) // 数据中心 ID 最大值(31)
	maxMachineID    = -1 ^ (-1 << machineIDBits)  // 工作机器 ID 最大值(31)
	maxSequence     = -1 ^ (-1 << sequenceBits)   // 序列号最大值(4095)

	timestampShift  = dataCenterBits + machineIDBits + sequenceBits // 时间戳偏移量
	dataCenterShift = machineIDBits + sequenceBits                  // 数据中心ID偏移量
	machineShift    = sequenceBits                                  // 机器ID偏移量
)

// Snowflake 结构体
type Snowflake struct {
	mutex         sync.Mutex // 分布式锁
	lastTimestamp int64      // 上一次生成ID的时间戳
	dataCenterID  int64      // 数据中心ID
	machineID     int64      // 机器ID
	sequence      int64      // 序列号
}

// NewSnowflake 创建雪花算法实例
func NewSnowflake(dataCenterID, machineID int64) (*Snowflake, error) {
	if dataCenterID < 0 || dataCenterID > maxDataCenterID {
		return nil, errors.New("dataCenterID 超出范围")
	}
	if machineID < 0 || machineID > maxMachineID {
		return nil, errors.New("machineID 超出范围")
	}

	return &Snowflake{
		mutex:         sync.Mutex{},
		lastTimestamp: 0,
		dataCenterID:  dataCenterID,
		machineID:     machineID,
		sequence:      0,
	}, nil
}

// GenerateID 生成唯一 ID
func (s *Snowflake) GenerateID() (int64, error) {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	// 1. 获取当前时间戳
	current := time.Now().UnixNano() / 1000000
	timestamp := current - epoch

	// 异常情况处理
	if timestamp < 0 {
		return 0, errors.New("时间戳小于 0")
	}

	// 2. 同一毫秒内生成序列号
	if timestamp == s.lastTimestamp {
		s.sequence = (s.sequence + 1) & maxSequence
		// 序列号用尽时，等待下一毫秒
		if s.sequence == 0 {
			for current <= s.lastTimestamp {
				current = time.Now().UnixNano() / 1000000
			}
			timestamp = current - epoch
		}
	} else {
		s.sequence = 0
	}

	// 3. 时间回拨检查
	if timestamp < s.lastTimestamp {
		return 0, errors.New("时间回拨！")
	}

	// 4. 更新最后时间戳
	s.lastTimestamp = timestamp

	// 拼接 ID 各部分
	id := (timestamp << timestampShift) |
		(s.dataCenterID << dataCenterShift) |
		(s.machineID << machineShift) |
		s.sequence

	return id, nil
}

func main() {
	// 创建实例（数据中心1，机器2）
	sf, _ := NewSnowflake(1, 2)

	// 生成 10 个 ID
	for range 10 {
		id, _ := sf.GenerateID()
		fmt.Println("Generated ID:", id)
	}

	// 输出结构分析
	fmt.Printf("\n64 bit ID Structure:\n")
	fmt.Printf("| 1bit 0 | 41bit timestamp | 5bit dataCenterID | 5bit machineID | 12bit sequence |\n")
}

```

运行结果：

````go
Generated ID: 57751918981816320
Generated ID: 57751918981816321
Generated ID: 57751918981816322
Generated ID: 57751918981816323
Generated ID: 57751918981816324
Generated ID: 57751918981816325
Generated ID: 57751918981816326
Generated ID: 57751918981816327
Generated ID: 57751918981816328
Generated ID: 57751918981816329
````

















