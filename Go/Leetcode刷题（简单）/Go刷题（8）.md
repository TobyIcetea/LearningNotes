# Go 刷题（8）

## 211. 有效的山脉数组（941）

给定一个整数数组 `arr`，如果它是有效的山脉数组就返回 `true`，否则返回 `false`。

让我们回顾一下，如果 `arr` 满足下述条件，那么它是一个山脉数组：

- `arr.length >= 3`

- 在 

    ```
    0 < i < arr.length - 1
    ```

     条件下，存在 

    ```
    i
    ```

     使得：

    - `arr[0] < arr[1] < ... arr[i-1] < arr[i] `
    - `arr[i] > arr[i+1] > ... > arr[arr.length - 1]`

![img](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/hint_valid_mountain_array.png)

```go
func validMountainArray(arr []int) bool {
    if len(arr) < 3 {
        return false
    }

    hasUp := false
    hasDown := false 
    for i, num := range arr {
        if i == 0 {
            continue
        }
        if num > arr[i - 1] {
            if hasDown {
                return false
            }
            hasUp = true
        } else if num < arr[i - 1] {
            if !hasUp {
                return false
            }
            hasDown = true
        } else {
            return false
        }
    }
    return hasDown
}
```

## 212. 增减字符串匹配（942）

由范围 `[0,n]` 内所有整数组成的 `n + 1` 个整数的排列序列可以表示为长度为 `n` 的字符串 `s` ，其中:

- 如果 `perm[i] < perm[i + 1]` ，那么 `s[i] == 'I'` 
- 如果 `perm[i] > perm[i + 1]` ，那么 `s[i] == 'D'` 

给定一个字符串 `s` ，重构排列 `perm` 并返回它。如果有多个有效排列perm，则返回其中 **任何一个** 。

```go
func diStringMatch(s string) []int {
    // I 就从小的这边选
    // D 就从大的这边选
    left := 0
    right := len(s)
    res := make([]int, 0, len(s))

    for _, r := range s {
        if r == 'I' {
            res = append(res, left)
            left++
        } else {
            res = append(res, right)
            right--
        }
    }
    res = append(res, left)

    return res
}
```

## 213. 删列造序（944）

给你由 `n` 个小写字母字符串组成的数组 `strs`，其中每个字符串长度相等。

这些字符串可以每个一行，排成一个网格。例如，`strs = ["abc", "bce", "cae"]` 可以排列为：

```
abc
bce
cae
```

你需要找出并删除 **不是按字典序非严格递增排列的** 列。在上面的例子（下标从 0 开始）中，列 0（`'a'`, `'b'`, `'c'`）和列 2（`'c'`, `'e'`, `'e'`）都是按字典序非严格递增排列的，而列 1（`'b'`, `'c'`, `'a'`）不是，所以要删除列 1 。

返回你需要删除的列数。

```go
func minDeletionSize(strs []string) int {
    n := len(strs[0])
    res := 0
    for j := 0; j < n; j++ {
        var pre byte = byte(0)
        for i := 0; i < len(strs); i++ {
            if strs[i][j] < pre {
                res++
                break  
            }
            pre = strs[i][j]
        }
    }

    return res
}
```

## 214. 验证外星语字典（953）

某种外星语也使用英文小写字母，但可能顺序 `order` 不同。字母表的顺序（`order`）是一些小写字母的排列。

给定一组用外星语书写的单词 `words`，以及其字母表的顺序 `order`，只有当给定的单词在这种外星语中按字典序排列时，返回 `true`；否则，返回 `false`。

```go
func isAlienSorted(words []string, order string) bool {
    dict := make(map[byte]int)
    for i := range order {
        dict[order[i]] = i
    }

    for i := range words {
        if i == 0 {
            continue
        }
        j := 0
        for j < len(words[i - 1]) && j < len(words[i]) {
            if dict[words[i - 1][j]] > dict[words[i][j]] {
                return false
            } else if dict[words[i - 1][j]] < dict[words[i][j]] {
                break
            } else {
                j++
            }
        }
        if len(words[i - 1]) > len(words[i]) && j == len(words[i]) {
            return false
        }
    }

    return true
}
```

## 215. 在长度2N的数组中找出重复N次的元素（961）

给你一个整数数组 `nums` ，该数组具有以下属性：

- `nums.length == 2 * n`.
- `nums` 包含 `n + 1` 个 **不同的** 元素
- `nums` 中恰有一个元素重复 `n` 次

找出并返回重复了 `n` 次的那个元素。

```go
func repeatedNTimes(nums []int) int {
    numSet := make(map[int]struct{})
    for _, num := range nums {
        if _, ok := numSet[num]; ok {
            return num
        }
        numSet[num] = struct{}{}
    }
    return -1
}
```

## 216. 数组形式的整数加法（989）

整数的 **数组形式** `num` 是按照从左到右的顺序表示其数字的数组。

- 例如，对于 `num = 1321` ，数组形式是 `[1,3,2,1]` 。

给定 `num` ，整数的 **数组形式** ，和整数 `k` ，返回 *整数 `num + k` 的 **数组形式*** 。

```go
func addToArrayForm(num []int, k int) []int {
    carry := 0
    for i := len(num) - 1; i >= 0 && (k != 0 || carry != 0); i-- {
        num[i] += k % 10 + carry
        k /= 10
        num[i], carry = num[i] % 10, num[i] / 10
    }
    if k != 0 || carry != 0 {
        k += carry
        arr := make([]int, 0)
        for k != 0 {
            arr = append(arr, k % 10)
            k /= 10
        }
        // 反转 arr
        left := 0
        right := len(arr) - 1
        for left < right {
            arr[left], arr[right] = arr[right], arr[left]
            left++
            right--
        }
        num = append(arr, num...)
    }
    return num
}
```

## 217. 二叉树的堂兄弟节点（993）

在二叉树中，根节点位于深度 `0` 处，每个深度为 `k` 的节点的子节点位于深度 `k+1` 处。

如果二叉树的两个节点深度相同，但 **父节点不同** ，则它们是一对*堂兄弟节点*。

我们给出了具有唯一值的二叉树的根节点 `root` ，以及树中两个不同节点的值 `x` 和 `y` 。

只有与值 `x` 和 `y` 对应的节点是堂兄弟节点时，才返回 `true` 。否则，返回 `false`。

```go
func isCousins(root *TreeNode, x int, y int) bool {
    // 防止 x 和 y 中有一个是根节点
    if root.Val == x || root.Val == y {
        return false
    }

    var fatherOfX *TreeNode
    var fatherOfY *TreeNode
    var heightOfX int
    var heightOfY int

    stk := make([]*TreeNode, 0)
    cur := root
    var pre *TreeNode

    for cur != nil || len(stk) != 0 {
        if cur != nil {
            stk = append(stk, cur)
            cur = cur.Left
        } else {
            cur = stk[len(stk) - 1]
            if cur.Right != nil && pre != cur.Right {
                cur = cur.Right
            } else {
                stk = stk[:len(stk) - 1]
                
                // 访问 cur
                // cur 所处在的树的深度是 len(stk)
                // cur 的父节点是 stk[len(stk) - 1]
                if cur.Val == x {
                    heightOfX = len(stk)
                    fatherOfX = stk[len(stk) - 1]
                } else if cur.Val == y {
                    heightOfY = len(stk)
                    fatherOfY = stk[len(stk) - 1]
                }

                pre = cur
                cur = nil
            }
        }
    }

    return heightOfX == heightOfY && fatherOfX != fatherOfY
}
```

## 218. 找到小镇的法官（997）

小镇里有 `n` 个人，按从 `1` 到 `n` 的顺序编号。传言称，这些人中有一个暗地里是小镇法官。

如果小镇法官真的存在，那么：

1. 小镇法官不会信任任何人。
2. 每个人（除了小镇法官）都信任这位小镇法官。
3. 只有一个人同时满足属性 **1** 和属性 **2** 。

给你一个数组 `trust` ，其中 `trust[i] = [ai, bi]` 表示编号为 `ai` 的人信任编号为 `bi` 的人。

如果小镇法官存在并且可以确定他的身份，请返回该法官的编号；否则，返回 `-1` 。

```go
func findJudge(n int, trust [][]int) int {
    trustCount := make([]int, n + 1)
    trustedCount := make([]int, n + 1)
    
    for _, arr := range trust {
        trustCount[arr[0]]++
        trustedCount[arr[1]]++
    }
    
    res := -1
    for i := 1; i <= n; i++ {
        if trustCount[i] == 0 && trustedCount[i] == n - 1 {
            if res == -1 {
                res = i
            } else {
                return -1
            }
        }
    }

    return res
}
```

## 219. 可以被一步捕获的棋子数（999）

给定一个 `8 x 8` 的棋盘，**只有一个** 白色的车，用字符 `'R'` 表示。棋盘上还可能存在白色的象 `'B'` 以及黑色的卒 `'p'`。空方块用字符 `'.'` 表示。

车可以按水平或竖直方向（上，下，左，右）移动任意个方格直到它遇到另一个棋子或棋盘的边界。如果它能够在一次移动中移动到棋子的方格，则能够 **吃掉** 棋子。

注意：车不能穿过其它棋子，比如象和卒。这意味着如果有其它棋子挡住了路径，车就不能够吃掉棋子。

返回白车 **攻击** 范围内 **兵的数量**。

```go
func numRookCaptures(board [][]byte) int {
    m := 0
    n := 0

    for i := 0; i < 8; i++ {
        for j := 0; j < 8; j++ {
            if board[i][j] == 'R' {
                m = i
                n = j
                break
            }
        }
    }

    // 车所处的位置是 (m, n)
    res := 0
    for i := m - 1; i >= 0; i-- {
        if board[i][n] == 'B' {
            break
        } else if board[i][n] == 'p' {
            res++
            break
        }
    }

    for i := m + 1; i < 8; i++ {
        if board[i][n] == 'B' {
            break
        } else if board[i][n] == 'p' {
            res++
            break
        }
    }

    for j := n - 1; j >= 0; j-- {
        if board[m][j] == 'B' {
            break
        } else if board[m][j] == 'p' {
            res++
            break
        }
    }

    for j := n + 1; j < 8; j++ {
        if board[m][j] == 'B' {
            break
        } else if board[m][j] == 'p' {
            res++
            break
        }
    }

    return res
}
```

## 220. 查找公用字符（1002）

给你一个字符串数组 `words` ，请你找出所有在 `words` 的每个字符串中都出现的共用字符（**包括重复字符**），并以数组形式返回。你可以按 **任意顺序** 返回答案。

```go
import "math"

func commonChars(words []string) []string {
    countOfWords := make([][]int, len(words))
    for i := 0; i < len(words); i++ {
        countOfWords[i] = make([]int, 26)
    }

    for i, word := range words {
        for j := 0; j < len(word); j++ {
            countOfWords[i][int(word[j]) - 97]++
        }
    }

    var res []string

    for i := 0; i < 26; i++ {
        minCount := math.MaxInt
        for j := 0; j < len(words); j++ {
            minCount = min(minCount, countOfWords[j][i])
        }
        // res 中增加 minCount 个 i 字母
        for j := 0; j < minCount; j++ {
            res = append(res, string(rune(i) + 'a'))
        }
    }

    return res
}
```

## 221. K次取反后最大化的数组和（1005）

给你一个整数数组 `nums` 和一个整数 `k` ，按以下方法修改该数组：

- 选择某个下标 `i` 并将 `nums[i]` 替换为 `-nums[i]` 。

重复这个过程恰好 `k` 次。可以多次选择同一个下标 `i` 。

以这种方式修改数组后，返回数组 **可能的最大和** 。

```go
import (
    "sort"
    "math"
)

func largestSumAfterKNegations(nums []int, k int) int {
    sort.Ints(nums)
    index := 0
    minAbs := math.MaxInt
    sum := 0
    for index < len(nums) && nums[index] <= 0 && k > 0 {
        nums[index] = -nums[index]
        minAbs = min(minAbs, nums[index])
        sum += nums[index]
        
        index++
        k--
    }

    // flag 表示之后是不是还需要减去 2 倍的 minAbs
    flag := (index == len(nums) || nums[index] > 0) && k % 2 == 1

    for index < len(nums) {
        if flag {
            minAbs = min(minAbs, nums[index])
        }
        
        sum += nums[index]
        
        index++
    }

    if flag {
        return sum - 2 * minAbs
    }
    return sum
}
```

## 222. 十进制整数的反码（1009）

每个非负整数 `N` 都有其二进制表示。例如， `5` 可以被表示为二进制 `"101"`，`11` 可以用二进制 `"1011"` 表示，依此类推。注意，除 `N = 0` 外，任何二进制表示中都不含前导零。

二进制的反码表示是将每个 `1` 改为 `0` 且每个 `0` 变为 `1`。例如，二进制数 `"101"` 的二进制反码为 `"010"`。

给你一个十进制数 `N`，请你返回其二进制表示的反码所对应的十进制整数。

```go
func bitwiseComplement(n int) int {
    limit := 1
    for n > limit {
        limit = ((limit + 1) << 1) - 1
    }
    return limit - n
}
```

## 223. 将数组分成和相等的三个部分（1013）

给你一个整数数组 `arr`，只有可以将其划分为三个和相等的 **非空** 部分时才返回 `true`，否则返回 `false`。

形式上，如果可以找出索引 `i + 1 < j` 且满足 `(arr[0] + arr[1] + ... + arr[i] == arr[i + 1] + arr[i + 2] + ... + arr[j - 1] == arr[j] + arr[j + 1] + ... + arr[arr.length - 1])` 就可以将数组三等分。

```go
func canThreePartsEqualSum(arr []int) bool {
    sum := 0
    for _, num := range arr {
        sum += num
    }
    if sum % 3 != 0 {
        return false
    }

    sumDiv3 := sum / 3
    index := 0
    sectors := 0
    tempSum := 0
    for index < len(arr) {
        tempSum += arr[index]
        if tempSum == sumDiv3 {
            sectors++
            tempSum = 0
        }

        index++
    }

    // 考虑一些 sectorSum 为 0 的情况
    return sectors >= 3
}
```

## 224. 可被5整除的二进制前缀（1018）

给定一个二进制数组 `nums` ( **索引从0开始** )。

我们将`xi` 定义为其二进制表示形式为子数组 `nums[0..i]` (从最高有效位到最低有效位)。

- 例如，如果 `nums =[1,0,1]` ，那么 `x0 = 1`, `x1 = 2`, 和 `x2 = 5`。

返回布尔值列表 `answer`，只有当 `xi` 可以被 `5` 整除时，答案 `answer[i]` 为 `true`，否则为 `false`。

```go
func prefixesDivBy5(nums []int) []bool {
    // 记录下每个数字的最后个位上的数字
    res := make([]bool, len(nums))
    lastNum := 0
    for i, num := range nums {
        lastNum = lastNum * 2 + num
        lastNum %= 10
        if lastNum % 5 == 0 {
            res[i] = true
        }
    }

    return res
}
```

## 225. 删除最外层的括号（1021）

有效括号字符串为空 `""`、`"(" + A + ")"` 或 `A + B` ，其中 `A` 和 `B` 都是有效的括号字符串，`+` 代表字符串的连接。

- 例如，`""`，`"()"`，`"(())()"` 和 `"(()(()))"` 都是有效的括号字符串。

如果有效字符串 `s` 非空，且不存在将其拆分为 `s = A + B` 的方法，我们称其为**原语（primitive）**，其中 `A` 和 `B` 都是非空有效括号字符串。

给出一个非空有效字符串 `s`，考虑将其进行原语化分解，使得：`s = P_1 + P_2 + ... + P_k`，其中 `P_i` 是有效括号字符串原语。

对 `s` 进行原语化分解，删除分解中每个原语字符串的最外层括号，返回 `s` 。

```go
import "strings"

func removeOuterParentheses(s string) string {
	// 分两步完成
	// 1. 进行元语化分解
	// 2. 删除每一个元语最外面的括号
	// 3. 拼接结果
	arr := make([]int, 0) // 所有要删除的下标
	stk := make([]byte, 0)
	for i, ch := range []byte(s) {
		if ch == '(' {
			if len(stk) == 0 {
				arr = append(arr, i)
			}
			stk = append(stk, ch)
		} else {
			if stk[len(stk)-1] == '(' {
				stk = stk[:len(stk)-1]
				if len(stk) == 0 {
					arr = append(arr, i)
				}
			} else {
				stk = append(stk, ch)
			}

		}
	}

	// 最终结果就是做一个 stringBuilder，但是 arr 中的下标位置的元素不要放
	var builder strings.Builder
	index := 0
	for i, ch := range s {
		if index < len(arr) && arr[index] == i {
			index++
		} else {
			// 放这个 i 位置的元素
			builder.WriteRune(ch)
		}
	}

	return builder.String()
}
```

## 226. 从根到叶的二进制数之和（1022）

给出一棵二叉树，其上每个结点的值都是 `0` 或 `1` 。每一条从根到叶的路径都代表一个从最高有效位开始的二进制数。

- 例如，如果路径为 `0 -> 1 -> 1 -> 0 -> 1`，那么它表示二进制数 `01101`，也就是 `13` 。

对树上的每一片叶子，我们都要找出从根到该叶子的路径所表示的数字。

返回这些数字之和。题目数据保证答案是一个 **32 位** 整数。

```go
func sumRootToLeaf(root *TreeNode) int {
	var dfs func(root *TreeNode, num int) int
	dfs = func(root *TreeNode, num int) int {
		if root == nil {
			return 0
		}
		num = num << 1 | root.Val
		if root.Left == nil && root.Right == nil {
			return num
		}
		return dfs(root.Left, num) + dfs(root.Right, num)
	}

	return dfs(root, 0)
}
```

## 227. 除数博弈（1025）

爱丽丝和鲍勃一起玩游戏，他们轮流行动。爱丽丝先手开局。

最初，黑板上有一个数字 `n` 。在每个玩家的回合，玩家需要执行以下操作：

- 选出任一 `x`，满足 `0 < x < n` 且 `n % x == 0` 。
- 用 `n - x` 替换黑板上的数字 `n` 。

如果玩家无法执行这些操作，就会输掉游戏。

*只有在爱丽丝在游戏中取得胜利时才返回 `true` 。假设两个玩家都以最佳状态参与游戏。*

```go
func divisorGame(n int) bool {
    return n % 2 == 0
}
```

## 228. 距离顺序排列矩阵单元格（1030）

给定四个整数 `rows` , `cols` , `rCenter` 和 `cCenter` 。有一个 `rows x cols` 的矩阵，你在单元格上的坐标是 `(rCenter, cCenter)` 。

返回矩阵中的所有单元格的坐标，并按与 `(rCenter, cCenter)` 的 **距离** 从最小到最大的顺序排。你可以按 **任何** 满足此条件的顺序返回答案。

单元格`(r1, c1)` 和 `(r2, c2)` 之间的距离为`|r1 - r2| + |c1 - c2|`。

```go
func allCellsDistOrder(rows int, cols int, rCenter int, cCenter int) [][]int {
	res := make([][]int, 0)

	for i := 0; i < rows; i++ {
		for j := 0; j < cols; j++ {
			res = append(res, []int{i, j})
		}
	}

    Abs := func(x int) int {
        if x < 0 {
            return -x
        }
        return x
    }

	sort.Slice(res, func(i int, j int) bool {
		distance1 := Abs(res[i][0] - rCenter) + Abs(res[i][1] - cCenter)
        distance2 := Abs(res[j][0] - rCenter) + Abs(res[j][1] - cCenter)
        return distance1 < distance2
	})

	return res
}
```

## 229. 有效的回旋镖（1037）

给定一个数组 `points` ，其中 `points[i] = [xi, yi]` 表示 **X-Y** 平面上的一个点，*如果这些点构成一个* **回旋镖** 则返回 `true` 。

**回旋镖** 定义为一组三个点，这些点 **各不相同** 且 **不在一条直线上** 。

```go
func isBoomerang(points [][]int) bool {
	// 其实就是不能在一条直线上

	// 判断是不是在一个点上
	if points[0][0] == points[1][0] && points[0][1] == points[1][1] ||
		points[0][0] == points[2][0] && points[0][1] == points[2][1] ||
		points[1][0] == points[2][0] && points[1][1] == points[2][1] {
		return false
	}

	deltaY1 := float64(points[2][1] - points[1][1])
	deltaX1 := float64(points[2][0] - points[1][0])

	deltaY2 := float64(points[1][1] - points[0][1])
	deltaX2 := float64(points[1][0] - points[0][0])

	if deltaX1 == 0 && deltaX2 == 0 {
		return false
	}
	if (deltaX1 == 0 && deltaX2 != 0) || (deltaX1 != 0 && deltaX2 == 0) {
		return true
	}

	k1 := deltaY1 / deltaX1
	k2 := deltaY2 / deltaX2
	return k1 != k2
}
```

## 230. 最后一块石头的重量（1046）

有一堆石头，每块石头的重量都是正整数。

每一回合，从中选出两块 **最重的** 石头，然后将它们一起粉碎。假设石头的重量分别为 `x` 和 `y`，且 `x <= y`。那么粉碎的可能结果如下：

- 如果 `x == y`，那么两块石头都会被完全粉碎；
- 如果 `x != y`，那么重量为 `x` 的石头将会完全粉碎，而重量为 `y` 的石头新重量为 `y-x`。

最后，最多只会剩下一块石头。返回此石头的重量。如果没有石头剩下，就返回 `0`。

```go
type MaxHeap []int

func (h *MaxHeap) Len() int {
	return len(*h)
}
func (h *MaxHeap) Less(i, j int) bool {
	return (*h)[i] > (*h)[j]
}
func (h *MaxHeap) Swap(i, j int) {
	(*h)[i], (*h)[j] = (*h)[j], (*h)[i]
}
func (h *MaxHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}
func (h *MaxHeap) Pop() interface{} {
	value := (*h)[len(*h)-1]
	*h = (*h)[:len(*h)-1]
	return value
}

func lastStoneWeight(stones []int) int {
	maxHeap := &MaxHeap{}
	heap.Init(maxHeap)

	for _, num := range stones {
		heap.Push(maxHeap, num)
	}

	for maxHeap.Len() >= 2 {
		y := heap.Pop(maxHeap).(int)
		x := heap.Pop(maxHeap).(int)
		if y > x {
			heap.Push(maxHeap, y-x)
		}
	}

	if maxHeap.Len() > 0 {
		return (*maxHeap)[0]
	}
	return 0
}

```







待做题目：

```bash
1047. 删除字符串中的所有相邻重复项
2087
73.4%
简单
1051. 高度检查器
747
80.4%
简单
1056. 易混淆数
201
46.4%
简单
1064. 不动点
121
65.0%
简单
1065. 字符串的索引对
121
57.2%
简单
1071. 字符串的最大公因子
1060
59.2%
简单
1078. Bigram 分词
555
65.1%
简单
1085. 最小元素各数位之和
116
78.1%
简单
1086. 前五科的均分
150
69.5%
简单
1089. 复写零
906
54.9%
简单
1099. 小于 K 的两数之和
167
61.2%
简单
1103. 分糖果 II
1403
67.9%
简单
1108. IP 地址无效化
1075
85.3%
简单
1118. 一月有多少天
73
66.1%
简单
1119. 删去字符串中的元音
195
87.3%
简单
1122. 数组的相对排序
1239
71.0%
简单
1128. 等价多米诺骨牌对的数量
580
54.6%
简单
1133. 最大唯一数
132
69.7%
简单
1134. 阿姆斯特朗数
98
78.1%
简单
1137. 第 N 个泰波那契数
1819
61.1%
简单
1150. 检查一个数是否在数组中占绝大多数
147
59.9%
简单
1154. 一年中的第几天
769
62.7%
简单
1160. 拼写单词
1128
68.2%
简单
1165. 单行键盘
174
86.1%
简单
1175. 质数排列
410
57.1%
简单

```



