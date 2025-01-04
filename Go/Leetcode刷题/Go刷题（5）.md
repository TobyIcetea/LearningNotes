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









待做题目：
292
303
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

