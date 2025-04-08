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

## 231. 高度检查器（1051）

学校打算为全体学生拍一张年度纪念照。根据要求，学生需要按照 **非递减** 的高度顺序排成一行。

排序后的高度情况用整数数组 `expected` 表示，其中 `expected[i]` 是预计排在这一行中第 `i` 位的学生的高度（**下标从 0 开始**）。

给你一个整数数组 `heights` ，表示 **当前学生站位** 的高度情况。`heights[i]` 是这一行中第 `i` 位学生的高度（**下标从 0 开始**）。

返回满足 `heights[i] != expected[i]` 的 **下标数量** 。

```go
func heightChecker(heights []int) int {
    sorted := make([]int, len(heights))
    copy(sorted, heights)

    sort.Ints(sorted)

    res := 0

    for i := range sorted {
        if sorted[i] != heights[i] {
            res++
        }
    }

    return res
}
```

## 232. Bigram分词（1078）

给出第一个词 `first` 和第二个词 `second`，考虑在某些文本 `text` 中可能以 `"first second third"` 形式出现的情况，其中 `second` 紧随 `first` 出现，`third` 紧随 `second` 出现。

对于每种这样的情况，将第三个词 "`third`" 添加到答案中，并返回答案。

```go
func findOcurrences(text string, first string, second string) []string {
    res := make([]string, 0)

    words := strings.Split(text, " ")
    for i := 0; i + 2 < len(words); i++ {
        if words[i] == first && words[i + 1] == second {
            res = append(res, words[i + 2])
        }
    }

    return res
}
```

## 233. 复写零（1089）

给你一个长度固定的整数数组 `arr` ，请你将该数组中出现的每个零都复写一遍，并将其余的元素向右平移。

注意：请不要在超过该数组长度的位置写入元素。请对输入的数组 **就地** 进行上述修改，不要从函数返回任何东西。

```go
func duplicateZeros(arr []int)  {
    curLength := 0
    index := 0
    for curLength < len(arr) {
        if arr[index] == 0 {
            curLength += 2
        } else {
            curLength++
        }
        index++
    }
    index -= 1  // 此时 index 指向的元素是之后要放进 arr 中的元素

    pos := len(arr) - 1  // 最后填充 arr 的时候使用的下标
    if curLength > len(arr) {
        // 说明最后一个是 0 元素，而且最后一个 0 元素只占用一个位置
        arr[len(arr) - 1] = 0
        pos = len(arr) - 2
        index -= 1
    }

    for pos >= 0 {
        if arr[index] == 0 {
            arr[pos] = 0
            arr[pos - 1] = 0
            pos -= 2
        } else {
            arr[pos] = arr[index]
            pos -= 1
        }
        index -= 1
    }
}
```

## 234. 分糖果II（1103）

排排坐，分糖果。

我们买了一些糖果 `candies`，打算把它们分给排好队的 **`n = num_people`** 个小朋友。

给第一个小朋友 1 颗糖果，第二个小朋友 2 颗，依此类推，直到给最后一个小朋友 `n` 颗糖果。

然后，我们再回到队伍的起点，给第一个小朋友 `n + 1` 颗糖果，第二个小朋友 `n + 2` 颗，依此类推，直到给最后一个小朋友 `2 * n` 颗糖果。

重复上述过程（每次都比上一次多给出一颗糖果，当到达队伍终点后再次从队伍起点开始），直到我们分完所有的糖果。注意，就算我们手中的剩下糖果数不够（不比前一次发出的糖果多），这些糖果也会全部发给当前的小朋友。

返回一个长度为 `num_people`、元素之和为 `candies` 的数组，以表示糖果的最终分发情况（即 `ans[i]` 表示第 `i` 个小朋友分到的糖果数）。

```go
func distributeCandies(candies int, numPeople int) []int {
    arr := make([]int, numPeople)
    count := 0
    for candies > 0 {
        // 本次要给的小朋友是 count % numPeople 这个编号位置处的
        // 要给的数量是 count + 1
        if candies >= count + 1 {
            // 给 count + 1 个
            arr[count % numPeople] += count + 1
            candies -= count + 1
        } else {
            // 给 candies 个
            arr[count % numPeople] += candies
            candies = 0
        }
        count++
    }

    return arr
}
```

## 235. IP地址无效化（1108）

给你一个有效的 IPv4 地址 address，返回这个 IP 地址的无效化版本。

所谓无效化 IP 地址，其实就是用 "[.]" 代替了每个 "."。

```go
func defangIPaddr(address string) string {
    var builder strings.Builder
    for i := 0; i < len(address); i++ {
        if address[i] == '.' {
            builder.WriteString("[.]")
        } else {
            builder.WriteByte(address[i])
        }
    }
    return builder.String()
}
```

## 236. 数组的相对排序（1122）

给你两个数组，`arr1` 和 `arr2`，`arr2` 中的元素各不相同，`arr2` 中的每个元素都出现在 `arr1` 中。

对 `arr1` 中的元素进行排序，使 `arr1` 中项的相对顺序和 `arr2` 中的相对顺序相同。未在 `arr2` 中出现过的元素需要按照升序放在 `arr1` 的末尾。

```go
func relativeSortArray(arr1 []int, arr2 []int) []int {
    res := make([]int, 0, len(arr1))

    counts := make([]int, 1005)
    for _, num := range arr1 {
        counts[num]++
    }

    for _, num := range arr2 {
        count := counts[num]
        for i := 0; i < count; i++ {
            res = append(res, num)
        }
        counts[num] = 0
    }

    for i, num := range counts {
        for num != 0 {
            res = append(res, i)
            num--
        }
    }

    return res
}
```

## 237. 等价多米诺古牌对的数量（1128）

给你一组多米诺骨牌 `dominoes` 。

形式上，`dominoes[i] = [a, b]` 与 `dominoes[j] = [c, d]` **等价** 当且仅当 (`a == c` 且 `b == d`) 或者 (`a == d` 且 `b == c`) 。即一张骨牌可以通过旋转 `0` 度或 `180` 度得到另一张多米诺骨牌。

在 `0 <= i < j < dominoes.length` 的前提下，找出满足 `dominoes[i]` 和 `dominoes[j]` 等价的骨牌对 `(i, j)` 的数量。

```go
func numEquivDominoPairs(dominoes [][]int) int {
	// 保证每一个数对都是：[小，大]
	for i := range dominoes {
		if dominoes[i][0] > dominoes[i][1] {
			dominoes[i][0], dominoes[i][1] = dominoes[i][1], dominoes[i][0]
		}
	}

	// 以第一个数字为优先，进行升序排序
	sort.Slice(dominoes, func(i, j int) bool {
		if dominoes[i][0] < dominoes[j][0] {
			return true
		} else if dominoes[i][0] > dominoes[j][0] {
			return false
		} else {
			return dominoes[i][1] < dominoes[j][1]
		}
	})

	// 传入一个值 n，返回 n! / 2!
	// value 初始值为 1，从 3 开始乘，一直乘到 n
	getValue := func(num int) int {
		return num * (num - 1) / 2
	}

	res := 0
	index := 0
	count := 1 // 有多少一样的
	for index < len(dominoes) {
		for index+1 < len(dominoes) &&
			dominoes[index][0] == dominoes[index+1][0] &&
			dominoes[index][1] == dominoes[index+1][1] {
			count++
			index++
		}
		if count >= 2 {
			res += getValue(count)
		}
		index++
		count = 1
	}

	return res
}
```

## 238. 一年中的第几天（1154）

给你一个字符串 date ，按 YYYY-MM-DD 格式表示一个 现行公元纪年法 日期。返回该日期是当年的第几天。

```go
func dayOfYear(date string) int {
	year, _ := strconv.Atoi(date[0:4])
	month, _ := strconv.Atoi(date[5:7])
	day, _ := strconv.Atoi(date[8:])

	res := 0
    isLeapYear := false
	if year%4 == 0 && year%100 != 0 || year%400 == 0 {
		isLeapYear = true
	}

    for i := 1; i < month; i++ {
        if i == 1 || i == 3 || i == 5 || i == 7 || i == 8 || i == 10 || i == 12 {
            res += 31
        } else if i == 2 {
            if isLeapYear {
                res += 29
            } else {
                res += 28
            }
        } else {
            res += 30
        }
    }

    res += day

    return res
}
```

## 239. 拼写单词（1160）

给你一份『词汇表』（字符串数组） `words` 和一张『字母表』（字符串） `chars`。

假如你可以用 `chars` 中的『字母』（字符）拼写出 `words` 中的某个『单词』（字符串），那么我们就认为你掌握了这个单词。

注意：每次拼写（指拼写词汇表中的一个单词）时，`chars` 中的每个字母都只能用一次。

返回词汇表 `words` 中你掌握的所有单词的 **长度之和**。

```go
func countCharacters(words []string, chars string) int {
	charsCount := make([]int, 26)
	for i := 0; i < len(chars); i++ {
		charsCount[chars[i]-'a']++
	}

	res := 0

Outer:
	for _, word := range words {
		tempCount := make([]int, 26)
		for i := 0; i < len(word); i++ {
			tempCount[word[i]-'a']++
		}
		for i := 0; i < 26; i++ {
			if tempCount[i] > charsCount[i] {
				continue Outer
			}
		}
		res += len(word)
	}

	return res
}
```

## 240. 质数排列（1175）

请你帮忙给从 `1` 到 `n` 的数设计排列方案，使得所有的「质数」都应该被放在「质数索引」（索引从 1 开始）上；你需要返回可能的方案总数。

让我们一起来回顾一下「质数」：质数一定是大于 1 的，并且不能用两个小于它的正整数的乘积来表示。

由于答案可能会很大，所以请你返回答案 **模 mod `10^9 + 7`** 之后的结果即可。

```go
func numPrimeArrangements(n int) int {
	// 计算出质数的 num 和 非质数的 num
	arr := make([]bool, n+1)
	for i := 2; i <= n; i++ {
		arr[i] = true
	}
	for i := 2; i <= n; i++ {
		for index := i + i; index <= n; index += i {
			arr[index] = false
		}
	}

	primeCount := 0
	notPrimeCount := 0
	for i := 1; i <= n; i++ {
		if arr[i] {
			primeCount++
		} else {
			notPrimeCount++
		}
	}

	getFactorial := func(num int) int {
		res := 1
		for i := 2; i <= num; i++ {
			res = (res * i) % (1e9 + 7)
		}
		return res
	}

	return (getFactorial(primeCount) * getFactorial(notPrimeCount)) % (1e9 + 7)
}
```











