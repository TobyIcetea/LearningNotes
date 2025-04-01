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

## 101. 找出与数组相加的整数I（3131）

给你两个长度相等的数组 `nums1` 和 `nums2`。

数组 `nums1` 中的每个元素都与变量 `x` 所表示的整数相加。如果 `x` 为负数，则表现为元素值的减少。

在与 `x` 相加后，`nums1` 和 `nums2` **相等** 。当两个数组中包含相同的整数，并且这些整数出现的频次相同时，两个数组 **相等** 。

返回整数 `x` 。

```go
func addedInteger(nums1 []int, nums2 []int) int {
    min1 := nums1[0]
    min2 := nums2[0]
    for i := 1; i < len(nums1); i++ {
        min1 = min(min1, nums1[i])
        min2 = min(min2, nums2[i])
    }
    return min2 - min1
}
```

## 102. 叶子相似的树（872）

请考虑一棵二叉树上所有的叶子，这些叶子的值按从左到右的顺序排列形成一个 **叶值序列** 。

![img](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/tree.png)

举个例子，如上图所示，给定一棵叶值序列为 `(6, 7, 4, 9, 8)` 的树。

如果有两棵二叉树的叶值序列是相同，那么我们就认为它们是 *叶相似* 的。

如果给定的两个根结点分别为 `root1` 和 `root2` 的树是叶相似的，则返回 `true`；否则返回 `false` 。

```go
func leafSimilar(root1 *TreeNode, root2 *TreeNode) bool {
    var dfs func(root *TreeNode, arr *[]int)
    dfs = func(root *TreeNode, arr *[]int) {
        if root == nil {
            return
        }
        dfs(root.Left, arr)
        if root.Left == nil && root.Right == nil {
            *arr = append(*arr, root.Val)
        }
        dfs(root.Right, arr)
    }

    arr1 := make([]int, 0)
    arr2 := make([]int, 0)
    dfs(root1, &arr1)
    dfs(root2, &arr2)

    if len(arr1) != len(arr2) {
        return false
    }

    for i := 0; i < len(arr1); i++ {
        if arr1[i] != arr2[i] {
            return false
        }
    }

    return true
}
```

代码简化版：
```go
func leafSimilar(root1 *TreeNode, root2 *TreeNode) bool {
    var dfs func(root *TreeNode) []int
    dfs = func(root *TreeNode) []int {
        if root == nil {
            return []int{}
        }
        left := dfs(root.Left)
        if root.Left == nil && root.Right == nil {
            return []int{root.Val}
        }
        right := dfs(root.Right)
        return append(left, right...)
    }
    
    return reflect.DeepEqual(dfs(root1), dfs(root2))
}
```

代码简化的重点不在于用 `reflect.DeepEqual()` 函数精简了比较的操作，主要在于对 `dfs()` 函数的精简化。

go 中如果要在函数中对一个数组进行 `append` 操作，传统的方法是比较繁琐的。我们要在传入切片的时候选择 `*[]int` 格式传入，之后每次使用的时候，都要 `*arr = append(*arr, num)`，在 `arr` 的前面加上一个 `*`。这也没办法，毕竟 go 中使用的 `append` 函数在新加入元素的时候，是有可能重新定址的，所以如果这个函数可能会对数组内容进行更新的时候，我们就需要传入数组的地址的地址，也就是 `*[]int`。

但是从这个题目中我又感受到，通过 go 中特殊的切片拼接方式，如果一个函数的功能是通过一个二叉树来生成一个数组，那么可以直接使用切片拼接来返回。具体的形式如下：

```go
left := 左边生成的切片
mid := 中间生成的切片（一般是一个单独的值）
right := 右边生成的切片
return append(append(left, mid...), right...)
```

## 103. 检测大写字母（520）

我们定义，在以下情况时，单词的大写用法是正确的：

- 全部字母都是大写，比如 `"USA"` 。
- 单词中所有字母都不是大写，比如 `"leetcode"` 。
- 如果单词不只含有一个字母，只有首字母大写， 比如 `"Google"` 。

给你一个字符串 `word` 。如果大写用法正确，返回 `true` ；否则，返回 `false` 。

```go
func detectCapitalUse(word string) bool {
    status := 0  // 0-全都是大写 1-大写开头 2-全都是小写
    
    var isUpperCase func(b byte) bool
    var isLowerCase func(b byte) bool
    isUpperCase = func(b byte) bool {
        return b >= 'A' && b <= 'Z'
    }
    isLowerCase = func(b byte) bool {
        return b >= 'a' && b <= 'z'
    }

    if isUpperCase(word[0]) && isUpperCase(word[len(word) - 1]) {
        status = 0
    } else if isLowerCase(word[0]) && isLowerCase(word[len(word) - 1]) {
        status = 2
    } else if isUpperCase(word[0]) && isLowerCase(word[len(word) - 1]) {
        status = 1
    } else {
        return false
    }
    
    if status == 0 {
        // 全都是大写
        for i := 1; i < len(word); i++ {
            if !isUpperCase(word[i]) {
                return false
            }
        }
    } else {
        // status == 1 或者 status == 2
        // 开头是大写，后面都是小写
        // 或者全都是小写
        for i := 1; i < len(word); i++ {
            if !isLowerCase(word[i]) {
                return false
            }
        }
    }

    return true
}
```

## 104. 最后一个单词的长度（58）

给你一个字符串 `s`，由若干单词组成，单词前后用一些空格字符隔开。返回字符串中 **最后一个** 单词的长度。

**单词** 是指仅由字母组成、不包含任何空格字符的最大子字符串。

```go
func lengthOfLastWord(s string) int {
    right := len(s) - 1
    for s[right] == ' ' {
        right--
    }
    left := right
    for left >= 0 && s[left] != ' ' {
        left--
    }
    return right - left
}
```

## 105. 删除排序链表中的重复元素（83）

给定一个已排序的链表的头 `head` ， *删除所有重复的元素，使每个元素只出现一次* 。返回 *已排序的链表* 。

```go
func deleteDuplicates(head *ListNode) *ListNode {
    node := head
    for node != nil {
        for node.Next != nil && node.Next.Val == node.Val {
            node.Next = node.Next.Next
        }
        node = node.Next
    }
    return head
}
```

## 106. 对称二叉树（101）

给你一个二叉树的根节点 `root` ， 检查它是否轴对称。

```go
func isSymmetric(root *TreeNode) bool {
    // 判断两棵树是否对称
    var mirror func(root1 *TreeNode, root2 *TreeNode) bool 
    mirror = func(root1 *TreeNode, root2 *TreeNode) bool {
        if root1 == nil && root2 == nil {
            return true
        }
        if root1 == nil && root2 != nil || root1 != nil && root2 == nil {
            return false
        }
        if root1.Val != root2.Val {
            return false
        }
        return mirror(root1.Left, root2.Right) && mirror(root1.Right, root2.Left)
    }

    return mirror(root.Left, root.Right)
}
```

## 107. 二叉树的最小深度（111）

给定一个二叉树，找出其最小深度。

最小深度是从根节点到最近叶子节点的最短路径上的节点数量。

**说明：**叶子节点是指没有子节点的节点。

```go
func minDepth(root *TreeNode) int {
    if root == nil {
        return 0
    }
    if root.Left == nil && root.Right == nil {
        return 1
    }
    if root.Left == nil && root.Right != nil {
        return minDepth(root.Right) + 1
    }
    if root.Left != nil && root.Right == nil {
        return minDepth(root.Left) + 1
    }
    left := minDepth(root.Left)
    right := minDepth(root.Right)
    return min(left, right) + 1
}
```

## 108. 路经总和（112）

给你二叉树的根节点 `root` 和一个表示目标和的整数 `targetSum` 。判断该树中是否存在 **根节点到叶子节点** 的路径，这条路径上所有节点值相加等于目标和 `targetSum` 。如果存在，返回 `true` ；否则，返回 `false` 。

**叶子节点** 是指没有子节点的节点。

```go
func hasPathSum(root *TreeNode, targetSum int) bool {
    curSum := 0
    res := false

    var dfs func(root *TreeNode)
    dfs = func(root *TreeNode) {
        if root == nil || res {
            return
        }

        curSum += root.Val
        if curSum == targetSum && root.Left == nil && root.Right == nil {
            res = true
            return
        } else {
            dfs(root.Left)
            dfs(root.Right)
            curSum -= root.Val
        }
    }

    dfs(root)
    return res
}
```

或者我们也可以不使用全局变量，直接返回 dfs 函数的运算结果：

```go
func hasPathSum(root *TreeNode, targetSum int) bool {
    curSum := 0

    var dfs func(root *TreeNode) bool
    dfs = func(root *TreeNode) bool {
        if root == nil {
            return false
        }

        curSum += root.Val
        if curSum == targetSum && root.Left == nil && root.Right == nil {
            return true
        } else {
            if (dfs(root.Left)) { return true }
            if (dfs(root.Right)) { return true }
            curSum -= root.Val
            return false
        }
    }

    return dfs(root)
}
```

## 109. 杨辉三角（119）

给定一个非负索引 `rowIndex`，返回「杨辉三角」的第 `rowIndex` 行。

在「杨辉三角」中，每个数是它左上方和右上方的数的和。

![img](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/1626927345-DZmfxB-PascalTriangleAnimated2.gif)

```go
func getRow(rowIndex int) []int {
    res := make([]int, rowIndex + 1)
    for right := 0; right <= rowIndex; right++ {
        res[right] = 1
        for i := right - 1; i > 0; i-- {
            res[i] += res[i - 1]
        }
    }
    return res
}
```

## 110. 二叉树的后序遍历（145）

给你一棵二叉树的根节点 `root` ，返回其节点值的 **后序遍历** 。

```go
func postorderTraversal(root *TreeNode) []int {
    var postorder func(root *TreeNode) []int
    postorder = func(root *TreeNode) []int {
        if root == nil {
            return []int{}
        }
        return append(append(postorder(root.Left), postorder(root.Right)...), root.Val)
    }

    return postorder(root)
}
```

## 111. Excel表列序号（171）

给你一个字符串 `columnTitle` ，表示 Excel 表格中的列名称。返回 *该列名称对应的列序号* 。

```go
func titleToNumber(columnTitle string) int {
    res := 0
    for i := 0; i < len(columnTitle); i++ {
        num := int(columnTitle[i]) - 'A' + 1
        res = res * 26 + num
    }
    return res
}
```

## 112. 颠倒二进制位（190）

颠倒给定的 32 位无符号整数的二进制位。

```go
func reverseBits(num uint32) uint32 {
    var res uint32 = 0
    for i := 0; i < 32; i++ {
        lastBit := num & 1
        res = (res << 1) | lastBit
        num = num >> 1
    }
    return res
}
```

## 113. 位1的数量（191）

给定一个正整数 `n`，编写一个函数，获取一个正整数的二进制形式并返回其二进制表达式中**设置位**的个数（也被称为[汉明重量](https://baike.baidu.com/item/汉明重量)）。

```go
func hammingWeight(n int) int {
    res := 0
    for n != 0 {
        res += n & 1
        n = n >> 1
    }
    return res
}
```

## 114. 同构字符串（205）

给定两个字符串 `s` 和 `t` ，判断它们是否是同构的。

如果 `s` 中的字符可以按某种映射关系替换得到 `t` ，那么这两个字符串是同构的。

每个出现的字符都应当映射到另一个字符，同时不改变字符的顺序。不同字符不能映射到同一个字符上，相同字符只能映射到同一个字符上，字符可以映射到自己本身。

```go
func isIsomorphic(s string, t string) bool {
    charMap := make([]byte, 128)  // byte 和 byte 的映射
    charSet := make(map[byte]bool)  // 存储已经被映射过的字符
    for i := 0; i < len(s); i++ {
        if charMap[s[i]] == 0 {
            // 还没有映射过这个字符
            charMap[s[i]] = t[i]
            if charSet[t[i]] {
                return false
            } else {
                charSet[t[i]] = true
            }
        } else {
            // 已经映射过这个字符了
            if t[i] != charMap[s[i]] {
                return false
            }
        }
    }
    return true
}
```

## 115. 存在重复元素（217）

给你一个整数数组 `nums` 。如果任一值在数组中出现 **至少两次** ，返回 `true` ；如果数组中每个元素互不相同，返回 `false` 。

```go
func containsDuplicate(nums []int) bool {
    numSet := make(map[int]bool)  // 存储已经出现过的数字
    for _, num := range nums {
        if numSet[num] {
            return true
        }
        numSet[num] = true
    }
    return false
}
```

## 116. 存在重复元素II（219）

给你一个整数数组 `nums` 和一个整数 `k` ，判断数组中是否存在两个 **不同的索引** `i` 和 `j` ，满足 `nums[i] == nums[j]` 且 `abs(i - j) <= k` 。如果存在，返回 `true` ；否则，返回 `false` 。

```go
func containsNearbyDuplicate(nums []int, k int) bool {
    // 简洁做法，用一个 map 记录好每一个元素上一次出现的下标
    prevIndexMap := make(map[int]int)
    for i, num := range nums {
        if preIndex, ok := prevIndexMap[num]; ok {
            // 之前出现过
            if i - preIndex <= k {
                return true
            }
        }
        prevIndexMap[num] = i
    }
    return false
}
```

或者是使用滑动窗口做：

```go
func containsNearbyDuplicate(nums []int, k int) bool {
    if k == 0 {
        return false
    }
    // 使用滑动窗口
    // 一般的滑动窗口都是要有 left 和 right 两个变量的
    // 但是如果一开始只是 right 变大，之后 left 和 right 一起变大，那就可以试试只维护一个 right 变量
    numSet := make(map[int]struct{})
    // 实际上本体窗口的大小应该是 k+1
    for i, num := range nums {
        if _, exists := numSet[num]; exists {
            return true
        }
        numSet[num] = struct{}{}
        // 去除 i-k 位置的元素
        if i - k >= 0 {
            delete(numSet, nums[i - k])
        }
    }
    return false
}
```

从这个题中也学到了 go 语言中效率更高的 set 的写法：将 map 的 value 类型设置成 `struct{}`，传入的值是 `struct{}{}`。这是 go 中的一个空类型，在编译的时候，就不会给它分配内存，以此来达到更高的内存效率。

如果要删除集合中的某一个元素，就可以使用 `delete()` 函数进行删除。函数有两个参数，第一个参数是 map，第二个参数是 map 中的 key。

除此之外，我在做这个题的时候，滑动窗口部分的内容可是给我造成了不少的麻烦。不过我们也能根据这个题，得出一些滑动窗口题目的解题的技巧：

- 首先一定要弄清楚滑动窗口的大小！
- 如果窗口大小一开始是从小变大，后期再保持不变（例如本题，窗口大小：1、2、3……k、k+1），那么我们就不必维护 left 和  right 两个变量（因为前半部分窗口大小正在增长的时候，left 不好确定）。只用一个 right 变量，left 直接用 `if (i>=k) left = i-k` 这样的形式计算出来就行。
- 本题中虽然我用的是 while 循环，但是滑动窗口其实和 for 是一样的：我们更新 left 和 right 的时机都是在循环的末尾。也就是说，哪怕是 while 循环，我们对 left 和 right 值得更新，也都应该放在 while 循环的最后部分，而不是 while 循环的开头或中间。

## 117. 用队列实现栈（225）

请你仅使用两个队列实现一个后入先出（LIFO）的栈，并支持普通栈的全部四种操作（`push`、`top`、`pop` 和 `empty`）。

实现 `MyStack` 类：

- `void push(int x)` 将元素 x 压入栈顶。
- `int pop()` 移除并返回栈顶元素。
- `int top()` 返回栈顶元素。
- `boolean empty()` 如果栈是空的，返回 `true` ；否则，返回 `false` 。

```go
type MyStack struct {
    // 这种做法的思想是：平时数据都只在 queue1 中存着，queue2 只有在偶尔进行 top 类操作的时候作为辅助数组用一下
    queue1 []int
    queue2 []int
}


func Constructor() MyStack {
    return MyStack{}
}


func (this *MyStack) Push(x int)  {
    this.queue1 = append(this.queue1, x)
}


func (this *MyStack) Pop() int {
    if len(this.queue1) == 0 {
        return -1
    }
    for len(this.queue1) > 1 {
        this.queue2 = append(this.queue2, this.queue1[0])
        this.queue1 = this.queue1[1:]
    }
    top := this.queue1[0]
    this.queue1 = this.queue1[1:]
    
    this.queue1, this.queue2 = this.queue2, this.queue1

    return top
}


func (this *MyStack) Top() int {
    if len(this.queue1) == 0 {
        return -1
    }
    top := 0
    for len(this.queue1) > 0 {
        top = this.queue1[0]
        this.queue2 = append(this.queue2, top)
        this.queue1 = this.queue1[1:]
    }
    this.queue1, this.queue2 = this.queue2, this.queue1
    return top
}


func (this *MyStack) Empty() bool {
    return len(this.queue1) == 0
}
```

## 118. 汇总区间（228）

给定一个  **无重复元素** 的 **有序** 整数数组 `nums` 。

返回 ***恰好覆盖数组中所有数字** 的 **最小有序** 区间范围列表* 。也就是说，`nums` 的每个元素都恰好被某个区间范围所覆盖，并且不存在属于某个范围但不属于 `nums` 的数字 `x` 。

列表中的每个区间范围 `[a,b]` 应该按如下格式输出：

- `"a->b"` ，如果 `a != b`
- `"a"` ，如果 `a == b`

```go
import "strconv"

func summaryRanges(nums []int) []string {
    if len(nums) == 0 {
        return []string{}
    }

    var generateRes func(begin int, end int) string
    generateRes = func(begin int, end int) string {
        if begin == end {
            return strconv.Itoa(begin)
        } else {
            return strconv.Itoa(begin) + "->" + strconv.Itoa(end)
        }
    }

    res := make([]string, 0)
    begin := -1
    end := -1
    first := true
    for i, num := range nums {
        if first {
            begin = num
            first = false
        } else {
            if num != nums[i - 1] + 1 {
                // 清算一次
                end = nums[i - 1]
                res = append(res, generateRes(begin, end))
                begin = num
            }
        }
    }
    end = nums[len(nums) - 1]
    res = append(res, generateRes(begin, end))
    

    return res
}
```

## 119. 2的幂（231）

给你一个整数 `n`，请你判断该整数是否是 2 的幂次方。如果是，返回 `true` ；否则，返回 `false` 。

如果存在一个整数 `x` 使得 `n == 2x` ，则认为 `n` 是 2 的幂次方。

```go
func isPowerOfTwo(n int) bool {
    // 消除最后一个 1：n & (n-1)
    if n <= 0 { return false }
    return n&(n-1) == 0
}
```

## 120. 有效的字母异位词（242）

给定两个字符串 `s` 和 `t` ，编写一个函数来判断 `t` 是否是 `s` 的字母异位词。

```go
func isAnagram(s string, t string) bool {
    if len(s) != len(t) {
        return false
    }
    counts := make([]int, 128)
    for i, _ := range s {
        counts[s[i]]++
        counts[t[i]]--
    }

    for i := 'a'; i <= 'z'; i++ {
        if counts[i] != 0 {
            return false
        }
    }

    return true
}
```

## 



























