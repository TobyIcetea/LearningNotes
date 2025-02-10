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

## 160. 两个列表的最小索引总和（599）

假设 Andy 和 Doris 想在晚餐时选择一家餐厅，并且他们都有一个表示最喜爱餐厅的列表，每个餐厅的名字用字符串表示。

你需要帮助他们用**最少的索引和**找出他们**共同喜爱的餐厅**。 如果答案不止一个，则输出所有答案并且不考虑顺序。 你可以假设答案总是存在。

```go
func findRestaurant(list1 []string, list2 []string) []string {
    var res []string
    var resIndexSum int
    var first bool = true

    // 先将 list1 中的数据按照名字 - 索引的格式存储下来
    strIndexMap1 := make(map[string]int)
    for i, str := range list1 {
        strIndexMap1[str] = i
    }

    // 然后看 list2 中的元素
    for index2, str := range list2 {
        if index1, ok := strIndexMap1[str]; ok {
            indexSum := index1 + index2
            if first {
                res = []string{str}
                resIndexSum = indexSum
                first = false
            } else {
                if indexSum == resIndexSum {
                    res = append(res, str)
                } else if indexSum < resIndexSum {
                    resIndexSum = indexSum
                    res = []string{str}
                }
            }
        }
    }

    return res
}
```

## 161. 合并二叉树（617）

给你两棵二叉树： `root1` 和 `root2` 。

想象一下，当你将其中一棵覆盖到另一棵之上时，两棵树上的一些节点将会重叠（而另一些不会）。你需要将这两棵树合并成一棵新二叉树。合并的规则是：如果两个节点重叠，那么将这两个节点的值相加作为合并后节点的新值；否则，**不为** null 的节点将直接作为新二叉树的节点。

返回合并后的二叉树。

**注意:** 合并过程必须从两个树的根节点开始。

```go
func mergeTrees(root1 *TreeNode, root2 *TreeNode) *TreeNode {
    if root1 == nil && root2 == nil {
        return nil
    }
    if root1 == nil && root2 != nil {
        return root2
    }
    if root1 != nil && root2 == nil {
        return root1
    }
    res := &TreeNode{Val: root1.Val + root2.Val}
    res.Left = mergeTrees(root1.Left, root2.Left)
    res.Right = mergeTrees(root1.Right, root2.Right)
    return res
}
```

## 162. 二叉树的层平均值（637）

给定一个非空二叉树的根节点 `root` , 以数组的形式返回每一层节点的平均值。与实际答案相差 `10-5` 以内的答案可以被接受。

```go
func averageOfLevels(root *TreeNode) []float64 {
    var res []float64

    // 层序遍历，使用 queue
    queue := []*TreeNode{root}
    for len(queue) != 0 {
        curSize := len(queue)
        valSum := 0
        valCount := 0
        for i := 0; i < curSize; i++ {
            node := queue[0]

            valSum += node.Val
            valCount++

            queue = queue[1:]
            if node.Left != nil {
                queue = append(queue, node.Left)
            }
            if node.Right != nil {
                queue = append(queue, node.Right)
            }
        }
        res = append(res, float64(valSum) / float64(valCount))
    }

    return res
}
```

## 163. 两数之和IV-输入二叉搜索树（653）

给定一个二叉搜索树 `root` 和一个目标结果 `k`，如果二叉搜索树中存在两个元素且它们的和等于给定的目标结果，则返回 `true`。

```go
func findTarget(root *TreeNode, k int) bool {
    nums := make([]int, 0)
    var dfs func(root *TreeNode)
    dfs = func(root *TreeNode) {
        if root == nil {
            return
        }
        dfs(root.Left)
        nums = append(nums, root.Val)
        dfs(root.Right)
    }

    dfs(root)

    i := 0
    j := len(nums) - 1
    for i < j {
        if nums[i] + nums[j] > k {
            j--
        } else if nums[i] + nums[j] < k {
            i++
        } else {
            return true
        }
    }

    return false
}
```

## 164. 机器人能否返回原点（657）

在二维平面上，有一个机器人从原点 `(0, 0)` 开始。给出它的移动顺序，判断这个机器人在完成移动后是否在 **`(0, 0)` 处结束**。

移动顺序由字符串 `moves` 表示。字符 `move[i]` 表示其第 `i` 次移动。机器人的有效动作有 `R`（右），`L`（左），`U`（上）和 `D`（下）。

如果机器人在完成所有动作后返回原点，则返回 `true`。否则，返回 `false`。

**注意：**机器人“面朝”的方向无关紧要。 `“R”` 将始终使机器人向右移动一次，`“L”` 将始终向左移动等。此外，假设每次移动机器人的移动幅度相同。

```go
func judgeCircle(moves string) bool {
    vertical := 0
    horizon := 0
    
    for _, move := range moves {
        switch move {
        case 'U':
            vertical++
        case 'D':
            vertical--
        case 'L':
            horizon--
        case 'R':
            horizon++
        }
    }

    return vertical == 0 && horizon == 0
}
```







待做题目：
661
671
680
682
693
696
700



