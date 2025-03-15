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

## 165. 图片平滑器（661）

**图像平滑器** 是大小为 `3 x 3` 的过滤器，用于对图像的每个单元格平滑处理，平滑处理后单元格的值为该单元格的平均灰度。

每个单元格的 **平均灰度** 定义为：该单元格自身及其周围的 8 个单元格的平均值，结果需向下取整。（即，需要计算蓝色平滑器中 9 个单元格的平均值）。

如果一个单元格周围存在单元格缺失的情况，则计算平均灰度时不考虑缺失的单元格（即，需要计算红色平滑器中 4 个单元格的平均值）。

![img](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/smoother-grid.jpg)

给你一个表示图像灰度的 `m x n` 整数矩阵 `img` ，返回对图像的每个单元格平滑处理后的图像 。

```go
func imageSmoother(img [][]int) [][]int {
	m := len(img)
	n := len(img[0])

	res := make([][]int, m)
	for i := 0; i < m; i++ {
		res[i] = make([]int, n)
	}

	for i := 0; i < m; i++ {
		for j := 0; j < n; j++ {
			sum := 0
			count := 0

			if i-1 >= 0 && j-1 >= 0 {
				sum += img[i-1][j-1]
                count++
			}
            if i-1 >= 0 {
				sum += img[i-1][j]
                count++
			}
            if i-1 >= 0 && j+1 < n  {
				sum += img[i-1][j+1]
                count++
			}

            if j-1 >= 0 {
				sum += img[i][j-1]
                count++
			}
			sum += img[i][j]
            count++
            if j+1 < n {
				sum += img[i][j+1]
                count++
			}

            if i+1 < m && j-1 >= 0 {
				sum += img[i+1][j-1]
                count++
			}
            if i+1 < m {
				sum += img[i+1][j]
                count++
			}
            if i+1 < m && j+1 < n {
				sum += img[i+1][j+1]
                count++
			}

            res[i][j] = sum / count
		}
	}

    return res
}
```

## 166. 二叉树中第二小的节点（671）

给定一个非空特殊的二叉树，每个节点都是正数，并且每个节点的子节点数量只能为 `2` 或 `0`。如果一个节点有两个子节点的话，那么该节点的值等于两个子节点中较小的一个。

更正式地说，即 `root.val = min(root.left.val, root.right.val)` 总成立。

给出这样的一个二叉树，你需要输出所有节点中的 **第二小的值** 。

如果第二小的值不存在的话，输出 -1 **。**

```go
func findSecondMinimumValue(root *TreeNode) int {
    minValue := root.Val
    res := -1

    var dfs func(root *TreeNode)
    dfs = func(root *TreeNode) {
        if root == nil {
            return
        }
        if root.Val != minValue {
            // 此时只需要判断一下这个 root 就行了，root 再往下的不可能成为答案
            if res == -1 {
                res = root.Val
            } else {
                res = min(res, root.Val)
            }
            return
        }
        dfs(root.Left)
        dfs(root.Right)
    }

    dfs(root)

    return res
}
```

## 167. 验证回文串II（680）

给你一个字符串 `s`，**最多** 可以从中删除一个字符。

请你判断 `s` 是否能成为回文字符串：如果能，返回 `true` ；否则，返回 `false` 。

```go
func validPalindrome(s string) bool {
    // 遇到不匹配的字符，要么是左边那个不要了，要么是右边那个不要了
    i := 0
    j := len(s) - 1

    var isPalindrome func(left int, right int) bool
    isPalindrome = func(left int, right int) bool {
        for left < right {
            if s[left] != s[right] {
                return false
            }
            left++
            right--
        }
        return true
    }

    for i < j {
        if s[i] == s[j] {
            i++
            j--
        } else {
            return isPalindrome(i + 1, j) || isPalindrome(i, j - 1) 
        }
    }
    return true
}
```

## 168. 棒球比赛（682）

你现在是一场采用特殊赛制棒球比赛的记录员。这场比赛由若干回合组成，过去几回合的得分可能会影响以后几回合的得分。

比赛开始时，记录是空白的。你会得到一个记录操作的字符串列表 `ops`，其中 `ops[i]` 是你需要记录的第 `i` 项操作，`ops` 遵循下述规则：

1. 整数 `x` - 表示本回合新获得分数 `x`
2. `"+"` - 表示本回合新获得的得分是前两次得分的总和。题目数据保证记录此操作时前面总是存在两个有效的分数。
3. `"D"` - 表示本回合新获得的得分是前一次得分的两倍。题目数据保证记录此操作时前面总是存在一个有效的分数。
4. `"C"` - 表示前一次得分无效，将其从记录中移除。题目数据保证记录此操作时前面总是存在一个有效的分数。

请你返回记录中所有得分的总和。

```go
import "strconv"

func calPoints(operations []string) int {
    res := 0

    nums := make([]int, 0)
    for _, operation := range operations {
        if operation == "+" {
            nums = append(nums, nums[len(nums) - 1] + nums[len(nums) - 2])
        } else if operation == "D" {
            nums = append(nums, nums[len(nums) - 1] * 2)
        } else if operation == "C" {
            nums = nums[:len(nums) - 1]
        } else {
            num, _ := strconv.Atoi(operation)
            nums = append(nums, num)
        }
    }
    for _, num := range nums {
        res += num
    }

    return res
}
```

## 169. 交替位二进制数（693）

给定一个正整数，检查它的二进制表示是否总是 0、1 交替出现：换句话说，就是二进制表示中相邻两位的数字永不相同。

```go
func hasAlternatingBits(n int) bool {
	if n&1 == 1 {
		for n != 0 && n != 1 {
			if n&1 != 1 || n&2 != 0 {
				return false
			}
			n >>= 2
		}
        return n == 1
	} else {
        for n != 0 && n != 1 {
			if n&1 != 0 || n&2 != 2 {  // 做题的时候在这里出问题了
				return false
			}
			n >>= 2
		}
        return n == 0
    }
}
```

做题的时候一开始提交总是不过，还使用 Goland 调试了一下。后来发现问题出在了：`n&2 != 2` 这个语句上。

这里我本来想表达的意思是，判断一下 n 的第 2 位，要求 n 的第 2 位不能是 1，所以一开始我一直写的都是 `n&2 != 1`。但是实际上，如果 n 的第 2 位是 1，这样相与之后的结果就是 `10b`（二进制），所对应的数字是 2。

## 170. 计数二进制子串（696）

给定一个字符串 `s`，统计并返回具有相同数量 `0` 和 `1` 的非空（连续）子字符串的数量，并且这些子字符串中的所有 `0` 和所有 `1` 都是成组连续的。

重复出现（不同位置）的子串也要统计它们出现的次数。

code1：

```go
// 使用额外空间
func countBinarySubstrings(s string) int {
    // arr 中存储每个元素出现的次数
    arr := make([]int, 0)
    
    count := 0
    for i, _ := range s {
        if i == 0 {
            count++
        } else {
            if s[i] == s[i - 1] {
                count++
            } else {
                arr = append(arr, count)
                count = 1
            }
        }
    }
    arr = append(arr, count)
    
    res := 0

    for i := 1; i < len(arr); i++ {
        res += min(arr[i], arr[i - 1])
    }

    return res
}
```

code2：

```go
// 不使用额外空间
func countBinarySubstrings(s string) int {
    count := 0
    preCount := 0  // 当前元素的前一个元素出现了多少次
    res := 0
    for i, _ := range s {
        if i == 0 {
            count++
        } else {
            if s[i] == s[i - 1] {
                count++
            } else {
                res += min(count, preCount)
                preCount = count
                count = 1
            }
        }
    }
    res += min(count, preCount)
    
    return res
}
```

## 171. 二叉搜索树中的搜索（700）

给定二叉搜索树（BST）的根节点 `root` 和一个整数值 `val`。

你需要在 BST 中找到节点值等于 `val` 的节点。 返回以该节点为根的子树。 如果节点不存在，则返回 `null` 。

```go
func searchBST(root *TreeNode, val int) *TreeNode {
    if root == nil {
        return nil
    }
    if root.Val == val {
        return root
    } else if root.Val > val {
        return searchBST(root.Left, val)
    } else {
        return searchBST(root.Right, val)
    }
}
```

## 172. 数据流中的第K大元素（703）

设计一个找到数据流中第 `k` 大元素的类（class）。注意是排序后的第 `k` 大元素，不是第 `k` 个不同的元素。

请实现 `KthLargest` 类：

- `KthLargest(int k, int[] nums)` 使用整数 `k` 和整数流 `nums` 初始化对象。
- `int add(int val)` 将 `val` 插入数据流 `nums` 后，返回当前数据流中第 `k` 大的元素。

```go
import "sort"

type KthLargest struct {
    k int
    nums []int
}


func Constructor(k int, nums []int) KthLargest {
    sort.Ints(nums)
    return KthLargest{
        k: k,
        nums: nums,
    }
}


func (this *KthLargest) Add(val int) int {
    index := 0
    for index < len(this.nums) && this.nums[index] <= val {
        index++
    }
    // 当前的 index 已经越界或者 nums[index] > val
    this.nums = append(this.nums, 0)
    // for i := index + 1; i < len(this.nums); i++ {
    //     this.nums[i] = this.nums[i - 1]
    // }
    for i := len(this.nums) - 1; i > index; i-- {
        this.nums[i] = this.nums[i - 1]
    }
    this.nums[index] = val
    
    return this.nums[len(this.nums) - this.k]
}
```

## 173. 设计哈希集合（705）

不使用任何内建的哈希表库设计一个哈希集合（HashSet）。

实现 `MyHashSet` 类：

- `void add(key)` 向哈希集合中插入值 `key` 。
- `bool contains(key)` 返回哈希集合中是否存在这个值 `key` 。
- `void remove(key)` 将给定值 `key` 从哈希集合中删除。如果哈希集合中没有这个值，什么也不做。

```go
type MyHashSet struct {
    size int
    data [][]int
}


func Constructor() MyHashSet {
    data := make([][]int, 1024)
    for i := 0; i < 1024; i++ {
        data[i] = make([]int, 0)
    }
    return MyHashSet{
        size: 1024,
        data: data,
    }
}

func (this *MyHashSet) Add(key int)  {
    index := key % this.size
    for _, num := range this.data[index] {
        if num == key {
            return
        }
    }
    this.data[index] = append(this.data[index], key)
}


func (this *MyHashSet) Remove(key int)  {
    index := key % this.size
    for i, num := range this.data[index] {
        if num == key {
            this.data[index] = append(this.data[index][:i], this.data[index][i+1:]...)
            break
        }
    }
}


func (this *MyHashSet) Contains(key int) bool {
    index := key % this.size
    for _, num := range this.data[index] {
        if num == key {
            return true
        }
    }
    return false
}
```

## 174. 设计哈希映射（706）

不使用任何内建的哈希表库设计一个哈希映射（HashMap）。

实现 `MyHashMap` 类：

- `MyHashMap()` 用空映射初始化对象
- `void put(int key, int value)` 向 HashMap 插入一个键值对 `(key, value)` 。如果 `key` 已经存在于映射中，则更新其对应的值 `value` 。
- `int get(int key)` 返回特定的 `key` 所映射的 `value` ；如果映射中不包含 `key` 的映射，返回 `-1` 。
- `void remove(key)` 如果映射中存在 `key` 的映射，则移除 `key` 和它所对应的 `value` 。

```go
type KeyValue struct {
    key int
    value int
}

func NewKeyValue(key int, value int) KeyValue {
    return KeyValue{
        key: key,
        value: value,
    }
}

type MyHashMap struct {
    size int
    data [][]KeyValue
}

func Constructor() MyHashMap {
    size := 1024
    data := make([][]KeyValue, size)
    for i := 0; i < size; i++ {
        data[i] = make([]KeyValue, 0)
    }
    return MyHashMap{
        size: size,
        data: data,
    }
}   

func (this *MyHashMap) Put(key int, value int)  {
    index := key % this.size
    for i, kv := range this.data[index] {
        if kv.key == key {
            this.data[index][i].value = value
            return
        }
    }
    this.data[index] = append(this.data[index], NewKeyValue(key, value))
}


func (this *MyHashMap) Get(key int) int {
    index := key % this.size
    for _, kv := range this.data[index] {
        if kv.key == key {
            return kv.value
        }
    }
    return -1
}


func (this *MyHashMap) Remove(key int)  {
    index := key % this.size
    for i, kv := range this.data[index] {
        if kv.key == key {
            this.data[index] = append(this.data[index][:i], this.data[index][i+1:]...)
            break
        }
    }
}
```

## 175. 转换成小写字母（709）

给你一个字符串 `s` ，将该字符串中的大写字母转换成相同的小写字母，返回新的字符串。

```go
func toLowerCase(s string) string {
    runes := []rune(s)
    for i, r := range runes {
        if r >= 'A' && r <= 'Z' {
            runes[i] += 32
        }
    }
    return string(runes)
}
```

## 176. 1比特与2比特（717）

有两种特殊字符：

- 第一种字符可以用一比特 `0` 表示
- 第二种字符可以用两比特（`10` 或 `11`）表示

给你一个以 `0` 结尾的二进制数组 `bits` ，如果最后一个字符必须是一个一比特字符，则返回 `true` 。

```go
func isOneBitCharacter(bits []int) bool {
    // 最后一个数字必须是 0
    // 0 前面必须是 0 或者 偶数个 1
    if bits[len(bits) - 1] != 0 {
        return false
    }
    if len(bits) - 2 >= 0 && bits[len(bits) - 2] == 0 {
        return true
    }
    countOfOne := 0
    for i := len(bits) - 2; i >= 0; i-- {
        if bits[i] == 1 {
            countOfOne++
        } else {
            break
        }
    }
    return countOfOne % 2 == 0
}
```

## 177. 寻找比目标字母大的最小字母（744）

给你一个字符数组 `letters`，该数组按**非递减顺序**排序，以及一个字符 `target`。`letters` 里**至少有两个不同**的字符。

返回 `letters` 中大于 `target` 的最小的字符。如果不存在这样的字符，则返回 `letters` 的第一个字符。

```go
func nextGreatestLetter(letters []byte, target byte) byte {
    // 二分，寻找第一个比 target 大的数字
    left := 0
    right := len(letters) - 1
    for left <= right {
        mid := (left + right) / 2
        if letters[mid] <= target {
            left = mid + 1
        } else {
            right = mid - 1
        }
    }
    if left == len(letters) {
        return letters[0]
    } else {
        return letters[left]
    }
}
```

## 178. 至少是其他数字两倍的最大数（747）

给你一个整数数组 `nums` ，其中总是存在 **唯一的** 一个最大整数 。

请你找出数组中的最大元素并检查它是否 **至少是数组中每个其他数字的两倍** 。如果是，则返回 **最大元素的下标** ，否则返回 `-1` 。

```go
func dominantIndex(nums []int) int {
    // 保留两个数字，一个是最大的，另一个是第二大的
    maxNumIndex := -1
    maxNum := 0
    secondMaxNum := 0
    for i, num := range nums {
        if num > secondMaxNum {
            secondMaxNum = num
            if secondMaxNum > maxNum {
                maxNum, secondMaxNum = secondMaxNum, maxNum
                maxNumIndex = i
            }
        }
    }
    if maxNum >= secondMaxNum * 2 {
        return maxNumIndex
    }
    return -1
}
```

## 179. 最短补全词（748）

```go
func shortestCompletingWord(licensePlate string, words []string) string {
    countOfPlate := make(map[rune]int)
    for _, r := range licensePlate {
        if r >= 'a' && r <= 'z' {
            countOfPlate[r]++
        } else if r >= 'A' && r <= 'Z' {
            countOfPlate[r + 32]++
        }
    }
    
    res := ""
    first := true
Outer:
    for _, word := range words {
        countOfWord := make(map[rune]int)
        for _, r := range word {
            countOfWord[r]++
        }
        for r, count := range countOfPlate {
            if countOfWord[r] < count {
                continue Outer
            }
        }
        // 此时 word 在字符上是符合答案要求的
        if first {
            first = false
            res = word
        } else if len(word) < len(res) {
            res = word
        }
    }
    return res
}
```

## 180. 二进制表示中质数个计算置位

给你两个整数 `left` 和 `right` ，在闭区间 `[left, right]` 范围内，统计并返回 **计算置位位数为质数** 的整数个数。

**计算置位位数** 就是二进制表示中 `1` 的个数。

- 例如， `21` 的二进制表示 `10101` 有 `3` 个计算置位。

```go
import "math"

func IsPrime(num int) bool {
    if num <= 1 {
        return false
    }
    if num == 2 {
        return true
    }
    // 排除所有偶数
    if num % 2 == 0 {
        return false
    }
    // 从 3 开始，每次加 2（跳过偶数）
    sqrt := int(math.Sqrt(float64(num)))
    for i := 3; i <= sqrt; i += 2 {
        if num % i == 0 {
            return false
        }
    }
    return true
}

func countPrimeSetBits(left int, right int) int {
    res := 0
    for num := left; num <= right; num++ {
        countOfOne := 0
        n := num
        for n != 0 {
            if n & 1 == 1 {
                countOfOne++
            }
            n >>= 1
        }
        if IsPrime(countOfOne) {
            res++
        }
    }
    return res
}
```







