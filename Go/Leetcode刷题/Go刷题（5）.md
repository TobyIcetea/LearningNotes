# Go 刷题（5）

## 121. 二叉树的所有路径（257）

给你一个二叉树的根节点 `root` ，按 **任意顺序** ，返回所有从根节点到叶子节点的路径。

**叶子节点** 是指没有子节点的节点。

```go
import (
    "strings"
    "strconv"
)

func binaryTreePaths(root *TreeNode) []string {
    res := make([]string, 0)

    path := make([]int, 0)

    var generateRes func()
    generateRes = func() {
        // 根据 path 产生一个结果到 res 中
        var sb strings.Builder
        sb.WriteString(strconv.Itoa(path[0]))
        for i := 1; i < len(path); i++ {
            sb.WriteString("->" + strconv.Itoa(path[i]))
        }
        res = append(res, sb.String())
    }

    var dfs func(node *TreeNode)
    dfs = func(node *TreeNode) {
        if node == nil {
            return
        }
        path = append(path, node.Val)
        if node.Left == nil && node.Right == nil {
            generateRes()
        } else {
            dfs(node.Left)
            dfs(node.Right)
        }
        path = path[:len(path) - 1]
    }

    dfs(root)
    return res
}
```

## 122. 丢失的数字（268）

给定一个包含 `[0, n]` 中 `n` 个数的数组 `nums` ，找出 `[0, n]` 这个范围内没有出现在数组中的那个数。

```go
func missingNumber(nums []int) int {
    // 计算 0 + 1 + 2 + ... + n 的和
    n := len(nums)
    expectedSum := n * (n + 1) / 2
    actualSum := 0
    for _, num := range nums {
        actualSum += num
    }
    return expectedSum - actualSum
}
```

## 123. 第一个错误的版本（278）

你是产品经理，目前正在带领一个团队开发新的产品。不幸的是，你的产品的最新版本没有通过质量检测。由于每个版本都是基于之前的版本开发的，所以错误的版本之后的所有版本都是错的。

假设你有 `n` 个版本 `[1, 2, ..., n]`，你想找出导致之后所有版本出错的第一个错误的版本。

你可以通过调用 `bool isBadVersion(version)` 接口来判断版本号 `version` 是否在单元测试中出错。实现一个函数来查找第一个错误的版本。你应该尽量减少对调用 API 的次数。

```go
func firstBadVersion(n int) int {
    // 二分查找
    left := 1
    right := n
    for left <= right {
        mid := left + (right - left) / 2
        if isBadVersion(mid) {
            right = mid - 1
        } else {
            left = mid + 1
        }
    }
    return left
}
```

## 124. Nim游戏（292）

你和你的朋友，两个人一起玩 [Nim 游戏](https://baike.baidu.com/item/Nim游戏/6737105)：

- 桌子上有一堆石头。
- 你们轮流进行自己的回合， **你作为先手** 。
- 每一回合，轮到的人拿掉 1 - 3 块石头。
- 拿掉最后一块石头的人就是获胜者。

假设你们每一步都是最优解。请编写一个函数，来判断你是否可以在给定石头数量为 `n` 的情况下赢得游戏。如果可以赢，返回 `true`；否则，返回 `false` 。

```go
func canWinNim(n int) bool {
    return n%4 != 0
}
```

## 125. 区域和检索-数组不可变（303）

给定一个整数数组  `nums`，处理以下类型的多个查询:

1. 计算索引 `left` 和 `right` （包含 `left` 和 `right`）之间的 `nums` 元素的 **和** ，其中 `left <= right`

实现 `NumArray` 类：

- `NumArray(int[] nums)` 使用数组 `nums` 初始化对象
- `int sumRange(int i, int j)` 返回数组 `nums` 中索引 `left` 和 `right` 之间的元素的 **总和** ，包含 `left` 和 `right` 两点（也就是 `nums[left] + nums[left + 1] + ... + nums[right]` )

```go
type NumArray struct {
    prefixSum []int
}


func Constructor(nums []int) NumArray {
    n := len(nums)
    prefixSum := make([]int, n+1)
    
    for i := 0; i < n; i++ {
        prefixSum[i+1] = prefixSum[i] + nums[i]  // 计算前缀和
    }

    return NumArray{prefixSum: prefixSum}
}


func (this *NumArray) SumRange(left int, right int) int {
    return this.prefixSum[right + 1] - this.prefixSum[left]
}
```









待做题目：
326
342
350
374
383
389
401
404
405
412
441
455

