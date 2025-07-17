# Go 语言 Package 学习（3）

## 16. container/heap

实际上 container 包中是有三个子包的，分别是：

- `container/list`：实现双向链表。
- `container/heap`：实现堆接口，通常用于优先级队列。
- `container/ring`：实现环形缓冲区。

但是目前看来，`list` 和 `ring` 用得比较少，一个是双向链表的结构，一个是环形链表的结构。如果用到了这些结构，我首先使用的方法还是自己手敲 ListNode 链表，所以那两种就不记录了，我们将学习的重心放在 `contain/heap` 上。

### 16.1 主要概念

`container/heap` 提供了一个通用的堆实现，支持最小堆和最大堆。最小堆中，父结点的值总是小于或等于其子节点的值；最大值则相反。

`heap.Interface`

要使用 `container/heap`，需要实现一个类型并实现 `heap.Interface` 接口。该接口包含以下方法：

```go
type Interface interface {
	sort.Interface
	Push(x interface{})  // 添加元素
	Pop() interface{}  // 移除并返回堆的最后一个元素
}
```

此外，`sort.Interface` 要求实现以下方法：

```go
type Interface interface {
	Len() int
	Less(i, j int) bool
	Swap(i, j int)
}
```

### 16.2 使用步骤

1. 定义一个类型：通常是选择一个切片，用于存储堆中的元素。
2. 实现 `heap.Interface` 接口：包括 `Len`、`Less`、`Swap`、`Push` 和 `Pop` 方法。
3. 使用堆函数：通过 `heap.Init` 初始化堆，使用 `heap.Push` 添加元素，使用 `heap.Pop` 移除元素等。

### 16.3 示例：实现最小堆

```go
package main

import (
	"container/heap"
	"fmt"
)

// IntHeap 定义一个 IntHeap 类型，它是一个整数切片
type IntHeap []int

// Len 实现 heap.Interface 接口的 Len 方法
func (h *IntHeap) Len() int { return len(*h) }

// Less 实现 heap.Interface 接口的 Less 方法（最小堆）
func (h *IntHeap) Less(i, j int) bool { return (*h)[i] < (*h)[j] }

// Swap 实现 heap.Interface 接口的 Swap 方法
func (h *IntHeap) Swap(i, j int) { (*h)[i], (*h)[j] = (*h)[j], (*h)[i] }

// Push 实现 heap.Interface 接口的 Push 方法（添加元素）
func (h *IntHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}

// Pop 实现 heap.Interface 接口的 Pop 方法（移除元素）
func (h *IntHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

func main() {
	// 创建一个 IntHeap，并初始化
	h := &IntHeap{5, 3, 8, 1}
	heap.Init(h)

	// 添加元素
	heap.Push(h, 2)
	heap.Push(h, 7)

	fmt.Println("最小堆中的元素：")
	for h.Len() > 0 {
		// 移除并打印最小元素
		fmt.Printf("%d ", heap.Pop(h))
	}
    // 输出: 1 2 3 5 7 8
}
```

### 16.4 示例：使用最大堆

要实现最大堆，只需修改 `Less` 方法，使其反向比较：

```go
func (h IntHeap) Less(i, j int) bool {
	return h[i] > h[j]  // 最大堆
}
```

### 16.5 总结

在 Go 语言中如果想要使用 `container/heap`，只需要按照 Slice 构造一个堆类型，然后给这个类型构建五个函数：`Len`、`Less`、`Swap`、`Push`、`Pop` 即可。其中的 `Push` 和 `Pop` 的参数类型或者返回值类型都必须定义成 `interface{}`，而且在实现的时候，需要进行类型断言（其中的 `x.(int)` 就是将 `x` 断言为 `int` 类型）。



















