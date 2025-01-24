# Go 刷题（6）

## 151. N叉树的最大深度（559）

给定一个 N 叉树，找到其最大深度。

最大深度是指从根节点到最远叶子节点的最长路径上的节点总数。

N 叉树输入按层序遍历序列化表示，每组子节点由空值分隔（请参见示例）。

```go
/**
 * Definition for a Node.
 * type Node struct {
 *     Val int
 *     Children []*Node
 * }
 */

func maxDepth(root *Node) int {
    if root == nil {
        return 0
    }

    // 广度优先搜索
    queue := []*Node{root}
    res := 0
    for len(queue) != 0 {
        // 将 queue 中的数据的孩子都放进来
        size := len(queue)
        for i := 0; i < size; i++ {
            node := queue[0]
            queue = queue[1:]
            for _, child := range node.Children {
                queue = append(queue, child)
            }
        }
        res++
    }
    return res
}
```

## 152. 二叉树的坡度（563）

给你一个二叉树的根节点 `root` ，计算并返回 **整个树** 的坡度 。

一个树的 **节点的坡度** 定义即为，该节点左子树的节点之和和右子树节点之和的 **差的绝对值** 。如果没有左子树的话，左子树的节点之和为 0 ；没有右子树的话也是一样。空结点的坡度是 0 。

**整个树** 的坡度就是其所有节点的坡度之和。

```go
func findTilt(root *TreeNode) int {
    
    res := 0

    var Abs func(num int) int
    Abs = func(num int) int {
        if num < 0 {
            return num * -1
        } else {
            return num
        }
    }

    var GetNodeValueSum func(root *TreeNode) int
    GetNodeValueSum = func(root *TreeNode) int {
        if root == nil {
            return 0
        }
        leftNodeValueSum := GetNodeValueSum(root.Left)
        rightNodeValueSum := GetNodeValueSum(root.Right)
        res += Abs(leftNodeValueSum - rightNodeValueSum)
        return leftNodeValueSum + rightNodeValueSum + root.Val
    }

    GetNodeValueSum(root)

    return res
}
```

## 153. 重塑矩阵（566）

在 MATLAB 中，有一个非常有用的函数 `reshape` ，它可以将一个 `m x n` 矩阵重塑为另一个大小不同（`r x c`）的新矩阵，但保留其原始数据。

给你一个由二维数组 `mat` 表示的 `m x n` 矩阵，以及两个正整数 `r` 和 `c` ，分别表示想要的重构的矩阵的行数和列数。

重构后的矩阵需要将原始矩阵的所有元素以相同的 **行遍历顺序** 填充。

如果具有给定参数的 `reshape` 操作是可行且合理的，则输出新的重塑矩阵；否则，输出原始矩阵。

```go
func matrixReshape(mat [][]int, r int, c int) [][]int {
    m := len(mat)
    n := len(mat[0])

    if m * n != r * c {
        return mat
    }

    res := make([][]int, r)
    for i := 0; i < r; i++ {
        res[i] = make([]int, c)
    }
    
    curRow := 0
    curColumn := 0
    for i := 0; i < m; i++ {
        for j := 0; j < n; j++ {
            res[curRow][curColumn] = mat[i][j]
            curColumn++
            if curColumn == c {
                curRow++
                curColumn = 0
            }
        }
    }
    return res
}
```

## 154. 另一棵树的子树（572）

给你两棵二叉树 `root` 和 `subRoot` 。检验 `root` 中是否包含和 `subRoot` 具有相同结构和节点值的子树。如果存在，返回 `true` ；否则，返回 `false` 。

二叉树 `tree` 的一棵子树包括 `tree` 的某个节点和这个节点的所有后代节点。`tree` 也可以看做它自身的一棵子树。

```go
func isSame(root1 *TreeNode, root2 *TreeNode) bool {
    if root1 == root2 {
        return true
    }
    if root1 == nil && root2 != nil || root1 != nil && root2 == nil {
        return false
    }
    return root1.Val == root2.Val && isSame(root1.Left, root2.Left) && isSame(root1.Right, root2.Right)
}

func isSubtree(root *TreeNode, subRoot *TreeNode) bool {
    if root == subRoot {
        return true
    }
    if root == nil && subRoot != nil || root != nil && subRoot == nil {
        return false
    }
    return isSame(root, subRoot) || isSubtree(root.Left, subRoot) || isSubtree(root.Right, subRoot)
}
```

判断两棵树是否相等的三个条件是**与**的关系：

- 当前两个树的根节点的值一样
- 并且，`root1.Left` 和 `root2.Left` 相等
- 并且，`root1.Right` 和 `root2.Right` 相等

判断第一棵树是不是第二个树的子树的三个条件是**或**的关系：

- `root1` 和 `root2` 相等
- 或者，`root1` 是 `root2.Left` 的子树
- 或者，`root1` 是 `root2.Right` 的子树

## 155. 分糖果（575）

Alice 有 `n` 枚糖，其中第 `i` 枚糖的类型为 `candyType[i]` 。Alice 注意到她的体重正在增长，所以前去拜访了一位医生。

医生建议 Alice 要少摄入糖分，只吃掉她所有糖的 `n / 2` 即可（`n` 是一个偶数）。Alice 非常喜欢这些糖，她想要在遵循医生建议的情况下，尽可能吃到最多不同种类的糖。

给你一个长度为 `n` 的整数数组 `candyType` ，返回： Alice *在仅吃掉 `n / 2` 枚糖的情况下，可以吃到糖的 **最多** 种类数*。

```go
func distributeCandies(candyType []int) int {
    typeSet := make(map[int]struct{})
    for _, t := range candyType {
        typeSet[t] = struct{}{}
    }
    return min(len(typeSet), len(candyType) / 2)
}
```

## 156. N叉树的前序遍历（589）

给定一个 n 叉树的根节点 `root` ，返回 *其节点值的 **前序遍历*** 。

n 叉树 在输入中按层序遍历进行序列化表示，每组子节点由空值 `null` 分隔。

```go
func preorder(root *Node) []int {
    if root == nil {
        return []int{}
    }
    res := []int{root.Val}
    for _, node := range root.Children {
        res = append(res, preorder(node)...)
    }
    return res
}
```

## 157. N叉树的后序遍历（590）

给定一个 n 叉树的根节点 `root` ，返回 *其节点值的 **后序遍历*** 。

n 叉树 在输入中按层序遍历进行序列化表示，每组子节点由空值 `null` 分隔（请参见示例）。

```go
func postorder(root *Node) []int {
    if root == nil {
        return []int{}
    }
    var res []int

    for _, child := range root.Children {
        res = append(res, postorder(child)...)
    }

    res = append(res, root.Val)

    return res
}
```

## 158. 最长和谐子序列（594）

和谐数组是指一个数组里元素的最大值和最小值之间的差别 **正好是 `1`** 。

给你一个整数数组 `nums` ，请你在所有可能的子序列中找到最长的和谐子序列的长度。

数组的 **子序列** 是一个由数组派生出来的序列，它可以通过删除一些元素或不删除元素、且不改变其余元素的顺序而得到。

```go
func findLHS(nums []int) int {
    res := 0

    counts := make(map[int]int)
    for _, num := range nums {
        counts[num]++
    }
    for num, count := range counts {
        if plusOneCount, ok := counts[num + 1]; ok {
            res = max(res, count + plusOneCount)
        }
    }

    return res
}
```

## 159. 区间加法II（598）

给你一个 `m x n` 的矩阵 `M` 和一个操作数组 `op` 。矩阵初始化时所有的单元格都为 `0` 。`ops[i] = [ai, bi]` 意味着当所有的 `0 <= x < ai` 和 `0 <= y < bi` 时， `M[x][y]` 应该加 1。

在 *执行完所有操作后* ，计算并返回 *矩阵中最大整数的个数* 。

```go
func maxCount(m int, n int, ops [][]int) int {
    minRow := 0
    minColumn := 0
    first := true

    for _, arr := range ops {
        if first {
            minRow = arr[0]
            minColumn = arr[1]
            first = false
        } else {
            minRow = min(minRow, arr[0])
            minColumn = min(minColumn, arr[1])
        }
    }

    if first {
        return m * n
    }
    
    return minRow * minColumn
}
```









待做题目：
599
617
637
653
657
661
671
680
682
693
696
700



