# Go 刷题（4）

## 91. 有效的完全平方数（367）

给你一个正整数 `num` 。如果 `num` 是一个完全平方数，则返回 `true` ，否则返回 `false` 。

**完全平方数** 是一个可以写成某个整数的平方的整数。换句话说，它可以写成某个整数和自身的乘积。

不能使用任何内置的库函数，如 `sqrt` 。

```go
func isPerfectSquare(num int) bool {
    // 二分查找
    left := 0
    right := num
    for left <= right {
        mid := left + (right - left) / 2
        mid2 := mid * mid
        if mid2 > num {
            right = mid - 1
        } else if mid2 < num {
            left = mid + 1
        } else {
            return true
        }
    }
    return false
}
```

## 92. 完全二叉树的节点个数（222）

给你一棵 **完全二叉树** 的根节点 `root` ，求出该树的节点个数。

[完全二叉树](https://baike.baidu.com/item/完全二叉树/7773232?fr=aladdin) 的定义如下：在完全二叉树中，除了最底层节点可能没填满外，其余每层节点数都达到最大值，并且最下面一层的节点都集中在该层最左边的若干位置。若最底层为第 `h` 层（从第 0 层开始），则该层包含 `1~ 2h` 个节点。

```go
func countNodes(root *TreeNode) int {
    // 获取完全二叉树的高度
    var getCompleteHeight func(root *TreeNode) int
    getCompleteHeight = func(root *TreeNode) int {
        height := 0
        for root != nil {
            height++
            root = root.Left
        }
        return height
    }

    // 根据完全二叉树的高度，获取节点数量
    // 高度为 h 的完全二叉树的节点数量是 2^n - 1
    var getNodes func(height int) int
    getNodes = func(height int) int {
        return (1 << height) - 1
    }

    // 遍历树
    var traverse func(root *TreeNode) int
    traverse = func(root *TreeNode) int {
        if root == nil {
            return 0
        }
        height1 := getCompleteHeight(root.Left)
        height2 := getCompleteHeight(root.Right)
        if height1 == height2 {
            // 左边一定是完全二叉树
            return getNodes(height1) + 1 + countNodes(root.Right)
        } else if height1 > height2 {
            // 右边一定是完全二叉树
            return getNodes(height2) + 1 + countNodes(root.Left)
        }
        return -1
    }

    return traverse(root)
}
```

## 93. 翻转图像（832）

给定一个 `n x n` 的二进制矩阵 `image` ，先 **水平** 翻转图像，然后 **反转** 图像并返回 *结果* 。

**水平**翻转图片就是将图片的每一行都进行翻转，即逆序。

- 例如，水平翻转 `[1,1,0]` 的结果是 `[0,1,1]`。

**反转**图片的意思是图片中的 `0` 全部被 `1` 替换， `1` 全部被 `0` 替换。

- 例如，反转 `[0,1,1]` 的结果是 `[1,0,0]`。

```go
func flipAndInvertImage(image [][]int) [][]int {
    row := len(image)
    column := len(image[0])
    
    for i := 0; i < row; i++ {
        left := 0
        right := column - 1
        for left < right {
            image[i][left], image[i][right] = image[i][right], image[i][left]
            left++
            right--
        }

        for j := 0; j < column; j++ {
            image[i][j] = 1 - image[i][j]
        }
    }  

    return image
}
```

## 94. 连续字符（1446）

给你一个字符串 `s` ，字符串的**「能量」**定义为：只包含一种字符的最长非空子字符串的长度。

请你返回字符串 `s` 的 **能量**。

```go
func maxPower(s string) int {
    res := 1
    curCount := 1
    for i := 1; i < len(s); i++ {
        if s[i] == s[i - 1] {
            curCount++
            res = max(res, curCount)
        } else {
            curCount = 1
        }
    }
    return res
}
```

## 95. 构成整天的下标对数目I（3184）

给你一个整数数组 `hours`，表示以 **小时** 为单位的时间，返回一个整数，表示满足 `i < j` 且 `hours[i] + hours[j]` 构成 **整天** 的下标对 `i`, `j` 的数目。

**整天** 定义为时间持续时间是 24 小时的 **整数倍** 。

例如，1 天是 24 小时，2 天是 48 小时，3 天是 72 小时，以此类推。

```go
import "sort"

func countCompleteDayPairs(hours []int) int {
	for i := 0; i < len(hours); i++ {
		hours[i] %= 24
	}
	sort.Ints(hours)

	res := 0

	for i := 0; i < len(hours); i++ {
		target := (24 - hours[i]) % 24
		for j := i + 1; j < len(hours); j++ {
			if hours[j] == target {
				res++
			}
		}
	}

	return res
}
```

## 96. 单调数列（896）

如果数组是单调递增或单调递减的，那么它是 **单调** *的*。

如果对于所有 `i <= j`，`nums[i] <= nums[j]`，那么数组 `nums` 是单调递增的。 如果对于所有 `i <= j`，`nums[i]> = nums[j]`，那么数组 `nums` 是单调递减的。

当给定的数组 `nums` 是单调数组时返回 `true`，否则返回 `false`。

```go
func isMonotonic(nums []int) bool {
    if len(nums) == 0 || len(nums) == 1 {
        return true
    }
    hasRisen := false  // 已经上升过
    hasFell := false  // 已经下降过
    for i := 1; i < len(nums); i++ {
        if nums[i] > nums[i - 1] {
            hasRisen = true
            if hasFell {
                return false
            }
        } else if nums[i] < nums[i - 1] {
            hasFell = true
            if hasRisen {
                return false
            }
        }
    }
    return true
}
```

## 97. 删除回文子序列（1332）

给你一个字符串 `s`，它仅由字母 `'a'` 和 `'b'` 组成。每一次删除操作都可以从 `s` 中删除一个回文 **子序列**。

返回删除给定字符串中所有字符（字符串为空）的最小删除次数。

「子序列」定义：如果一个字符串可以通过删除原字符串某些字符而不改变原字符顺序得到，那么这个字符串就是原字符串的一个子序列。

「回文」定义：如果一个字符串向后和向前读是一致的，那么这个字符串就是一个回文。

```go
func removePalindromeSub(s string) int {
    // 要么一次删完，要么两次删完
    left := 0
    right := len(s) - 1
    for left < right {
        if s[left] != s[right] {
            return 2
        }
        left++
        right--
    }
    return 1
}
```

## 98. 买票需要的时间（2073）

有 `n` 个人前来排队买票，其中第 `0` 人站在队伍 **最前方** ，第 `(n - 1)` 人站在队伍 **最后方** 。

给你一个下标从 **0** 开始的整数数组 `tickets` ，数组长度为 `n` ，其中第 `i` 人想要购买的票数为 `tickets[i]` 。

每个人买票都需要用掉 **恰好 1 秒** 。一个人 **一次只能买一张票** ，如果需要购买更多票，他必须走到 **队尾** 重新排队（**瞬间** 发生，不计时间）。如果一个人没有剩下需要买的票，那他将会 **离开** 队伍。

返回位于位置 `k`（下标从 **0** 开始）的人完成买票需要的时间（以秒为单位）。

```go
func timeRequiredToBuy(tickets []int, k int) int {
    count := k + 1  // 还有多少轮才到我们关注的那个人
    res := 0
    for true {
        count--
        res++
        if tickets[0] == 1 {
            // 这个人买完票了
            if count == 0 {  // 这是我们关注的那个人
                return res
            }
            // 将这个人清除出队列
            tickets = tickets[1:]
        } else {
            // 这个人还没有买完票
            if count == 0 {  // 这是我们关注的那个人
                count = len(tickets)
            }
            // 将这个人移动到队列最后
            tickets[0] -= 1
            tickets = append(tickets[1:], tickets[0])
        }
    }
    return -1
}
```

一开始我以为做这个题会遇到一些困难，因为 go 中没有官方提供的 queue 队列。当我还在为繁琐的入队出队操作而烦恼的时候，发现 go 中这样写其实也不是很难：

- 入队：`queue = append(queue, element)`
- 出队：`queue = queue[1:]`
- 取队头元素：`queue[0]`

其实主要是那个出队的操作，我们如何进行频繁出队，也就是每次都从 1 开始截断一个数组，这让我开始担心 queue 的性能问题。但是 Slice 切片好像在这块儿有性能优化，所以平时刷题的时候不用很担心这个操作！

如果想要解决，一个方法就是使用环形队列。不过那样就要自己建结构体了。

## 99. 矩阵对角线元素的和（1572）

给你一个正方形矩阵 `mat`，请你返回矩阵对角线元素的和。

请你返回在矩阵主对角线上的元素和副对角线上且不在主对角线上元素的和。

```go
func diagonalSum(mat [][]int) int {
    n := len(mat)
    index1 := 0
    index2 := n - 1
    res := 0

    for i := 0; i < n; i++ {
        if index1 == index2 {
            res += mat[i][index1]
        } else {
            res += mat[i][index1] + mat[i][index2]
        }
        index1++
        index2--
    }

    return res
}
```

## 100. 与车相交的点（2848）

给你一个下标从 **0** 开始的二维整数数组 `nums` 表示汽车停放在数轴上的坐标。对于任意下标 `i`，`nums[i] = [starti, endi]` ，其中 `starti` 是第 `i` 辆车的起点，`endi` 是第 `i` 辆车的终点。

返回数轴上被车 **任意部分** 覆盖的整数点的数目。

```go
func numberOfPoints(nums [][]int) int {
    // 本题的数据量较小，所以直接开 100 的数组
    arr := make([]bool, 101)
    for i := 0; i < len(nums); i++ {
        begin := nums[i][0]
        end := nums[i][1]
        for begin <= end {
            arr[begin] = true
            begin++
        }
    }

    res := 0
    for i := 1; i <= 100; i++ {
        if arr[i] { res += 1 }
    }

    return res
}
```















待做的题目：

3131、872、520





