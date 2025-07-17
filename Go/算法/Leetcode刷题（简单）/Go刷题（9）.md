# Go刷题（9）

## 241. 公交站间的距离（1184）

环形公交路线上有 `n` 个站，按次序从 `0` 到 `n - 1` 进行编号。我们已知每一对相邻公交站之间的距离，`distance[i]` 表示编号为 `i` 的车站和编号为 `(i + 1) % n` 的车站之间的距离。

环线上的公交车都可以按顺时针和逆时针的方向行驶。

返回乘客从出发点 `start` 到目的地 `destination` 之间的最短距离。

```go
func distanceBetweenBusStops(distance []int, start int, destination int) int {
    if start > destination {
        start, destination = destination, start
    }
    target := 0  // 从 start 到 destination 的距离
    sum := 0  // 整个环路的距离
    for i := 0; i < len(distance); i++ {
        if i >= start && i < destination {
            target += distance[i]
        }
        sum += distance[i]
    }
    return min(target, sum - target)
}
```

## 242. 一周中的第几天（1185）

给你一个日期，请你设计一个算法来判断它是对应一周中的哪一天。

输入为三个整数：`day`、`month` 和 `year`，分别表示日、月、年。

您返回的结果必须是这几个值中的一个 `{"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}`。

```go
func dayOfTheWeek(day int, month int, year int) string {
    t := time.Date(year, time.Month(month), day, 0, 0, 0, 0, time.UTC)
    return t.Weekday().String()
}
```

## 243. “气球” 的最大数量（1186）

给你一个字符串 `text`，你需要使用 `text` 中的字母来拼凑尽可能多的单词 **"balloon"（气球）**。

字符串 `text` 中的每个字母最多只能被使用一次。请你返回最多可以拼凑出多少个单词 **"balloon"**。

```go
func maxNumberOfBalloons(text string) int {
	countOfB := 0
	countOfA := 0
	countOfL := 0
	countOfO := 0
	countOfN := 0

	for i := 0; i < len(text); i++ {
		switch text[i] {
		case 'b':
			countOfB++
		case 'a':
			countOfA++
		case 'l':
			countOfL++
		case 'o':
			countOfO++
		case 'n':
			countOfN++
		}
	}

	return min(countOfB, countOfA, countOfL/2, countOfO/2, countOfN)
}
```

## 244. 最小绝对差（1200）

给你个整数数组 `arr`，其中每个元素都 **不相同**。

请你找到所有具有最小绝对差的元素对，并且按升序的顺序返回。

每对元素对 `[a,b`] 如下：

- `a , b` 均为数组 `arr` 中的元素
- `a < b`
- `b - a` 等于 `arr` 中任意两个元素的最小绝对差

```go
func minimumAbsDifference(arr []int) [][]int {
	sort.Ints(arr)
	minDiff := math.MaxInt
	for i := 1; i < len(arr); i++ {
		minDiff = min(minDiff, arr[i]-arr[i-1])
	}

	res := make([][]int, 0)

	for i := 1; i < len(arr); i++ {
		if arr[i] - arr[i - 1] == minDiff {
			res = append(res, []int{arr[i - 1], arr[i]})
		}
	}

	return res
}
```

## 245. 独一无二的出现次数（1207）

给你一个整数数组 `arr`，如果每个数的出现次数都是独一无二的，就返回 `true`；否则返回 `false`。

```go
func uniqueOccurrences(arr []int) bool {
    counts := make(map[int]int)
    for _, num := range arr {
        counts[num]++
    }
    countHasAppeared := make(map[int]struct{})
    for _, count := range counts {
        if _, ok := countHasAppeared[count]; ok {
            return false
        }
        countHasAppeared[count] = struct{}{}
    }
    return true
}
```

## 246. 玩筹码（1217）

有 `n` 个筹码。第 `i` 个筹码的位置是 `position[i]` 。

我们需要把所有筹码移到同一个位置。在一步中，我们可以将第 `i` 个筹码的位置从 `position[i]` 改变为:

- `position[i] + 2` 或 `position[i] - 2` ，此时 `cost = 0`
- `position[i] + 1` 或 `position[i] - 1` ，此时 `cost = 1`

返回将所有筹码移动到同一位置上所需要的 *最小代价* 。

```go
func minCostToMoveChips(position []int) int {
    countOfEven := 0
    for _, num := range position {
        if num & 1 == 0 {
            countOfEven++
        }
    }
    return min(countOfEven, len(position) - countOfEven)
}
```

## 247. 分割平衡字符串（1221）

**平衡字符串** 中，`'L'` 和 `'R'` 字符的数量是相同的。

给你一个平衡字符串 `s`，请你将它分割成尽可能多的子字符串，并满足：

- 每个子字符串都是平衡字符串。

返回可以通过分割得到的平衡字符串的 **最大数量** **。**

```go
func balancedStringSplit(s string) int {
    // 如果是 L 就 +1
    // 如果是 R 就 -1
    count := 0
    res := 0
    for i := 0; i < len(s); i++ {
        if s[i] == 'L' {
            count++
        } else {
            count--
        }
        if count == 0 {
            res++
        }
    }
    return res
}
```

## 248. 缀点成线（1232）

给定一个数组 `coordinates` ，其中 `coordinates[i] = [x, y]` ， `[x, y]` 表示横坐标为 `x`、纵坐标为 `y` 的点。请你来判断，这些点是否在该坐标系中属于同一条直线上。

```go
func checkStraightLine(coordinates [][]int) bool {
	verticalLine := false
	deltaX := coordinates[1][0] - coordinates[0][0]
	deltaY := coordinates[1][1] - coordinates[0][1]
	var k float64
	if deltaX == 0 {
		verticalLine = true
	} else {
		k = float64(deltaY) / float64(deltaX)
	}

    for i := 2; i < len(coordinates); i++ {
        deltaX := coordinates[i][0] - coordinates[0][0]
        deltaY := coordinates[i][1] - coordinates[0][1]
        if verticalLine && deltaX != 0 || !verticalLine && deltaX == 0 {
            return false
        }
        if !verticalLine {
            curK := float64(deltaY) / float64(deltaX)
            if curK != k {
                return false
            }
        }
    }

    return true
}
```

## 249. 奇数值单元格的数目（1252）

给你一个 `m x n` 的矩阵，最开始的时候，每个单元格中的值都是 `0`。

另有一个二维索引数组 `indices`，`indices[i] = [ri, ci]` 指向矩阵中的某个位置，其中 `ri` 和 `ci` 分别表示指定的行和列（**从 `0` 开始编号**）。

对 `indices[i]` 所指向的每个位置，应同时执行下述增量操作：

1. `ri` 行上的所有单元格，加 `1` 。
2. `ci` 列上的所有单元格，加 `1` 。

给你 `m`、`n` 和 `indices` 。请你在执行完所有 `indices` 指定的增量操作后，返回矩阵中 **奇数值单元格** 的数目。

```go
func oddCells(m int, n int, indices [][]int) int {
    rows := make([]int, m)
    columns := make([]int, n)

    for _, pair := range indices {
        rows[pair[0]]++
        columns[pair[1]]++
    }

    res := 0

    for i := 0; i < m; i++ {
        for j := 0; j < n; j++ {
            num := rows[i] + columns[j]
            if num & 1 == 1 {
                res++
            }
        }
    }

    return res
}
```

## 250. 二维网格迁移（1260）

给你一个 `m` 行 `n` 列的二维网格 `grid` 和一个整数 `k`。你需要将 `grid` 迁移 `k` 次。

每次「迁移」操作将会引发下述活动：

- 位于 `grid[i][j]`（`j < n - 1`）的元素将会移动到 `grid[i][j + 1]`。
- 位于 `grid[i][n - 1]` 的元素将会移动到 `grid[i + 1][0]`。
- 位于 `grid[m - 1][n - 1]` 的元素将会移动到 `grid[0][0]`。

请你返回 `k` 次迁移操作后最终得到的 **二维网格**。

```go
func shiftGrid(grid [][]int, k int) [][]int {
    m := len(grid)
    n := len(grid[0])
    arr := make([]int, m)

    for count := 0; count < k; count++ {
        // 进行 k 次迁移
        for i := 0; i < m; i++ {
            arr[i] = grid[i][n - 1]
        }

        for j := n - 1; j > 0; j-- {
            for i := 0; i < m; i++ {
                grid[i][j] = grid[i][j - 1]
            }
        }

        for i := 1; i < m; i++ {
            grid[i][0] = arr[i - 1]
        }
        grid[0][0] = arr[m - 1]
    }

    return grid
}
```

## 251. 访问所有点的最小时间（1266）

平面上有 `n` 个点，点的位置用整数坐标表示 `points[i] = [xi, yi]` 。请你计算访问所有这些点需要的 **最小时间**（以秒为单位）。

你需要按照下面的规则在平面上移动：

- 每一秒内，你可以：
    - 沿水平方向移动一个单位长度，或者
    - 沿竖直方向移动一个单位长度，或者
    - 跨过对角线移动 `sqrt(2)` 个单位长度（可以看作在一秒内向水平和竖直方向各移动一个单位长度）。
- 必须按照数组中出现的顺序来访问这些点。
- 在访问某个点时，可以经过该点后面出现的点，但经过的那些点不算作有效访问。

```go
func minTimeToVisitAllPoints(points [][]int) int {
    res := 0

    Abs := func(num int) int {
        if num < 0 {
            return -num
        } else {
            return num
        }
    }

    for i := 1; i < len(points); i ++ {
        dx := points[i][0] - points[i-1][0]
        dy := points[i][1] - points[i-1][1]
        res += max(Abs(dx), Abs(dy))
    }

    return res
}
```

## 252. 找出井字棋的获胜者（1275）

**井字棋** 是由两个玩家 `A` 和 `B` 在 `3 x 3` 的棋盘上进行的游戏。井字棋游戏的规则如下：

- 玩家轮流将棋子放在空方格 (`' '`) 上。
- 第一个玩家 `A` 总是用 `'X'` 作为棋子，而第二个玩家 `B` 总是用 `'O'` 作为棋子。
- `'X'` 和 `'O'` 只能放在空方格中，而不能放在已经被占用的方格上。
- 只要有 **3** 个相同的（非空）棋子排成一条直线（行、列、对角线）时，游戏结束。
- 如果所有方块都放满棋子（不为空），游戏也会结束。
- 游戏结束后，棋子无法再进行任何移动。

给你一个数组 `moves`，其中 `moves[i] = [rowi, coli]` 表示第 `i` 次移动在 `grid[rowi][coli]`。如果游戏存在获胜者（`A` 或 `B`），就返回该游戏的获胜者；如果游戏以平局结束，则返回 `"Draw"`；如果仍会有行动（游戏未结束），则返回 `"Pending"`。

你可以假设 `moves` 都 **有效**（遵循 **井字棋** 规则），网格最初是空的，`A` 将先行动。

```go
func tictactoe(moves [][]int) string {
    matrix := make([][]rune, 3)
    for i := 0; i < 3; i++ {
        matrix[i] = make([]rune, 3)
    }

    for i := 0; i < len(moves); i++ {
        if i % 2 == 0 {
            matrix[moves[i][0]][moves[i][1]] = 'X'
        } else {
            matrix[moves[i][0]][moves[i][1]] = 'O'
        }
    }

    // 0 没有输赢，1 A 获胜，2 B 获胜
    res := 0
    if matrix[0][0] == matrix[0][1] && matrix[0][1] == matrix[0][2] {
        if matrix[0][0] == 'X' {
            res = 1
        } else if matrix[0][0] == 'O' {
            res = 2
        }
    }
    if matrix[1][0] == matrix[1][1] && matrix[1][1] == matrix[1][2] {
        if matrix[1][0] == 'X' {
            res = 1
        } else if matrix[1][0] == 'O' {
            res = 2
        }
    }
    if matrix[2][0] == matrix[2][1] && matrix[2][1] == matrix[2][2] {
        if matrix[2][0] == 'X' {
            res = 1
        } else if matrix[2][0] == 'O' {
            res = 2
        }
    }
    if matrix[0][0] == matrix[1][0] && matrix[1][0] == matrix[2][0] {
        if matrix[0][0] == 'X' {
            res = 1
        } else if matrix[0][0] == 'O' {
            res = 2
        }
    }
    if matrix[0][1] == matrix[1][1] && matrix[1][1] == matrix[2][1] {
        if matrix[0][1] == 'X' {
            res = 1
        } else if matrix[0][1] == 'O' {
            res = 2
        }
    }
    if matrix[0][2] == matrix[1][2] && matrix[1][2] == matrix[2][2] {
        if matrix[0][2] == 'X' {
            res = 1
        } else if matrix[0][2] == 'O' {
            res = 2
        }
    }
    if matrix[0][0] == matrix[1][1] && matrix[1][1] == matrix[2][2] {
        if matrix[0][0] == 'X' {
            res = 1
        } else if matrix[0][0] == 'O' {
            res = 2
        }
    }
    if matrix[2][0] == matrix[1][1] && matrix[1][1] == matrix[0][2] {
        if matrix[2][0] == 'X' {
            res = 1
        } else if matrix[2][0] == 'O' {
            res = 2
        }
    }

    if res == 1 {
        return "A"
    } else if res == 2 {
        return "B"
    } else {
        if len(moves) == 9 {
            return "Draw"
        } else {
            return "Pending"
        }
    }
}
```

## 253. 整数的各位积和之差（1281）

给你一个整数 `n`，请你帮忙计算并返回该整数「各位数字之积」与「各位数字之和」的差。

```go
func subtractProductAndSum(n int) int {
    digitProduct := 1
	sum := 0

    for n != 0 {
        lastNum := n % 10
        n = n / 10
        digitProduct *= lastNum
        sum += lastNum
    }

    return digitProduct - sum
}
```

## 254. 有序数组中出现次数超过25%的元素（1287）

给你一个非递减的 **有序** 整数数组，已知这个数组中恰好有一个整数，它的出现次数超过数组元素总数的 25%。

请你找到并返回这个整数。

```go
func findSpecialInteger(arr []int) int {
    target := len(arr) / 4
    index := 0
    for index < len(arr) {
        count := 1
        for index + 1 < len(arr) && arr[index + 1] == arr[index] {
            index++
            count++
        }

        // 最后一共有 count 个数字
        if count > target {
            return arr[index]
        }

        index++
    }
    return -1
}
```

## 255. 二进制链表转整数（1290）

给你一个单链表的引用结点 `head`。链表中每个结点的值不是 0 就是 1。已知此链表是一个整数数字的二进制表示形式。

请你返回该链表所表示数字的 **十进制值** 。

```go
func getDecimalValue(head *ListNode) int {
	res := 0
	node := head
	for node != nil {
		res = (res << 1) + node.Val
		node = node.Next
	}
	return res
}
```

## 256. 统计位数为偶数的数字（1295）

给你一个整数数组 `nums`，请你返回其中位数为 **偶数** 的数字的个数。

```go
func findNumbers(nums []int) int {
    res := 0
    for _, num := range nums {
        if num >= 10 && num <= 99 || num >= 1000 && num <= 9999 || num == 100000 {
            res++
        }
    }
    return res
}
```

## 257. 将每个元素替换为右侧最大元素（1299）

给你一个数组 `arr` ，请你将每个元素用它右边最大的元素替换，如果是最后一个元素，用 `-1` 替换。

完成所有替换操作后，请你返回这个数组。

```go
func replaceElements(arr []int) []int {
    maxNum := -1
    for i := len(arr) - 1; i >= 0; i-- {
        maxNumNext := max(maxNum, arr[i])
        arr[i] = maxNum
        maxNum = maxNumNext
    }
    return arr
}
```

## 258. 和为零的N个不同整数（1304）

给你一个整数 `n`，请你返回 **任意** 一个由 `n` 个 **各不相同** 的整数组成的数组，并且这 `n` 个数相加和为 `0` 。

```go
func sumZero(n int) []int {
    res := make([]int, 0, n)

    half := n / 2
    for i := 1; i <= half; i++ {
        res = append(res, i, -i)
    }
    if n & 1 == 1 {
        res = append(res, 0)
    }

    return res
}
```

## 259. 解码字母到整数映射（1309）

给你一个字符串 `s`，它由数字（`'0'` - `'9'`）和 `'#'` 组成。我们希望按下述规则将 `s` 映射为一些小写英文字符：

- 字符（`'a'` - `'i'`）分别用（`'1'` - `'9'`）表示。
- 字符（`'j'` - `'z'`）分别用（`'10#'` - `'26#'`）表示。

返回映射之后形成的新字符串。

题目数据保证映射始终唯一。

```go
func freqAlphabets(s string) string {
    var builder strings.Builder

    for i := 0; i < len(s); i++ {
        if i + 2 < len(s) && s[i + 2] == '#' {
            // 将 s[i], s[i+1], s[i+2] 整理为一个字母
            num := (s[i] - '0') * 10 + (s[i + 1] - '0')
            builder.WriteRune(rune(num - 1 + 'a'))
            i += 2
        } else {
            builder.WriteRune(rune(s[i] - '1' + 'a'))
        }
    }

    return builder.String()
}
```

## 260. 解压缩编码列表（1313）

给你一个以行程长度编码压缩的整数列表 `nums` 。

考虑每对相邻的两个元素 `[freq, val] = [nums[2*i], nums[2*i+1]]` （其中 `i >= 0` ），每一对都表示解压后子列表中有 `freq` 个值为 `val` 的元素，你需要从左到右连接所有子列表以生成解压后的列表。

请你返回解压后的列表。

```go
func decompressRLElist(nums []int) []int {
    res := make([]int, 0)
    for i := 0; i < len(nums); i += 2 {
        for j := 0; j < nums[i]; j++ {
            res = append(res, nums[i + 1])
        }
    }
    return res
}
```

## 261. 将整数转换为两个无零整数的和（1317）

「无零整数」是十进制表示中 **不含任何 0** 的正整数。

给你一个整数 `n`，请你返回一个 **由两个整数组成的列表** `[a, b]`，满足：

- `a` 和 `b` 都是无零整数
- `a + b = n`

题目数据保证至少有一个有效的解决方案。

如果存在多个有效解决方案，你可以返回其中任意一个。

```go
func isValid(num int) bool {
    if num == 0 {
        return false
    }
    for num != 0 {
        if num % 10 == 0 {
            return false
        }
        num = num / 10
    }
    return true
}

func getNoZeroIntegers(n int) []int {
    for left := 1; left < n; left++ {
        right := n - left
        // 检测 left 和 right 是不是无零整数
        if isValid(left) && isValid(right) {
            return []int{left, right}
        }
    }
    return []int{-1, -1}
}
```

## 262. 6和9组成的最大数字（1323）

给你一个仅由数字 6 和 9 组成的正整数 `num`。

你最多只能翻转一位数字，将 6 变成 9，或者把 9 变成 6 。

请返回你可以得到的最大数字。

```go
func maximum69Number (num int) int {
    // 将 6 变成 9
    arr := make([]int, 0)
    for num != 0 {
        arr = append(arr, num % 10)
        num /= 10
    }

    for i := len(arr) - 1; i >= 0; i-- {
        if arr[i] == 6 {
            arr[i] = 9
            break
        }
    }

    res := 0
    for i := len(arr) - 1; i >= 0; i-- {
        res = res * 10 + arr[i]
    }

    return res
}
```

## 263. 数组序号转换（1331）

给你一个整数数组 `arr` ，请你将数组中的每个元素替换为它们排序后的序号。

序号代表了一个元素有多大。序号编号的规则如下：

- 序号从 1 开始编号。
- 一个元素越大，那么序号越大。如果两个元素相等，那么它们的序号相同。
- 每个数字的序号都应该尽可能地小。

```go
func arrayRankTransform(arr []int) []int {
    sorted := make([]int, len(arr))
    copy(sorted, arr)
    sort.Ints(sorted)

    numPosMap := make(map[int]int)
    pos := 1
    for i, num := range sorted {
        if i - 1 >= 0 && sorted[i - 1] == sorted[i] {
            continue
        }
        numPosMap[num] = pos
        pos++
    }

    res := make([]int, len(arr))
    for i, num := range arr {
        res[i] = numPosMap[num]
    }

    return res
}
```

## 264. 矩阵中战斗力最弱的 K 行（1337）

给你一个大小为 `m * n` 的矩阵 `mat`，矩阵由若干军人和平民组成，分别用 1 和 0 表示。

请你返回矩阵中战斗力最弱的 `k` 行的索引，按从最弱到最强排序。

如果第 ***i*** 行的军人数量少于第 ***j*** 行，或者两行军人数量相同但 ***i*** 小于 ***j***，那么我们认为第 ***i*** 行的战斗力比第 ***j*** 行弱。

军人 **总是** 排在一行中的靠前位置，也就是说 1 总是出现在 0 之前。

```go
func kWeakestRows(mat [][]int, k int) []int {
    res := make([]int, 0)

    resSet := make(map[int]struct{})

    for j := 0; k > 0 && j < len(mat[0]); j++ {
        for i := 0; k > 0 && i < len(mat); i++ {
            if _, ok := resSet[i]; ok {
                continue
            }
            if mat[i][j] == 0 {
                res = append(res, i)
                resSet[i] = struct{}{}
                k--
            }
        }
    }

    if k > 0 {
        for i := 0; k > 0 && i < len(mat); i++ {
            if _, ok := resSet[i]; !ok {
                res = append(res, i)
                resSet[i] = struct{}{}
                k--
            }
        }
    }

    return res
}
```

## 265. 将数字变成 0 的操作次数（1342）

```go
func numberOfSteps(num int) int {
    res := 0
    for num != 0 {
        if num & 1 == 1 {
            num -= 1
        } else {
            num /= 2
        }
        res++
    }

    return res
}
```

## 266. 检查整数及其两倍数是否存在（1346）

给你一个整数数组 `arr`，请你检查是否存在两个整数 `N` 和 `M`，满足 `N` 是 `M` 的两倍（即，`N = 2 * M`）。

更正式地，检查是否存在两个下标 `i` 和 `j` 满足：

- `i != j`
- `0 <= i, j < arr.length`
- `arr[i] == 2 * arr[j]`

```go
func checkIfExist(arr []int) bool {
	numSet := make(map[int]struct{})

	for _, num := range arr {
		if _, ok := numSet[num/2]; ok && (num%2 == 0) {
			return true
		}
		if _, ok := numSet[num*2]; ok {
			return true
		}
		numSet[num] = struct{}{}
	}

	return false
}
```

注意：

- Go 的语法中，在一个 if 判断条件的框框中，只允许出现一个初始化语句。
- 所以可以 `_, ok := numSet[num/2]; ok && (num%2 == 0)` 将两个条件包起来，这样是可以的，因为只有一个初始化语句。
- 但是无法将上述代码中两个 if 再合并为一个 if 语句。因为这两个 if 语句的条件中各有一个初始化 ok 的语句。

## 267. 统计有序矩阵中的负数（1351）

给你一个 `m * n` 的矩阵 `grid`，矩阵中的元素无论是按行还是按列，都以非严格递减顺序排列。 请你统计并返回 `grid` 中 **负数** 的数目。

```go
func countNegatives(grid [][]int) int {
	res := 0

	m := len(grid)
	n := len(grid[0])

	// 在第一行中找第一个负数
	left := 0
	right := n - 1
	for left <= right {
		mid := left + (right-left)>>1
		if grid[0][mid] >= 0 {
			left = mid + 1
		} else {
			right = mid - 1
		}
	}
	// 第一个负数就是 grid[0][left]
	// 最后一个大于等于 0 的数就是 left - 1
	left -= 1
	res += n - (left + 1)
	for i := 1; i < m; i++ {
		for left >= 0 && grid[i][left] < 0 {
			left--
		}
		res += n - (left + 1)
	}

	return res
}
```

## 268. 根据数字二进制下 1 的数目排序（1356）

如果存在多个数字二进制中 **1** 的数目相同，则必须将它们按照数值大小升序排列。

请你返回排序后的数组。

```go
// 第一次写的错误的代码
func sortByBits(arr []int) []int {
	countOfOne := make([]int, len(arr))
	for i, num := range arr {
		count := 0
		for num != 0 {
			if num&1 == 1 {
				count++
			}
			num = num >> 1
		}
		countOfOne[i] = count
	}

	sort.Slice(arr, func(i, j int) bool {
		if countOfOne[i] == countOfOne[j] {
			return arr[i] < arr[j]
		}
		return countOfOne[i] < countOfOne[j]
	})

	return arr
}
```

在第一次的代码中，计算每个元素二进制中 1 的数目时，将其存储在 `countOfOne` 数组中。然而，当对原数组进行排序时，元素的顺序发生了变化，但 `countOfOne` 数组的索引仍然对应于原数组的索引。这导致在比较两个元素时，使用了错误的 1 的数目，从而导致排序结果错误。

修改代码的思路：绑定元素值和 1 的关系。将每个元素与其对应的二进制中 1 的数目组合成一个结构体，确保在排序过程中数目和元素始终对应。

```go
// 正确的代码
func sortByBits(arr []int) []int {
	type elem struct {
		num   int
		count int
	}

	elems := make([]elem, len(arr))
	for i, num := range arr {
		count := bits.OnesCount(uint(num))
		elems[i] = elem{num: num, count: count}
	}

	sort.Slice(elems, func(i, j int) bool {
		if elems[i].count == elems[j].count {
			return elems[i].num < elems[j].num
		}
		return elems[i].count < elems[j].count
	})

	res := make([]int, len(arr))
	for i := range res {
		res[i] = elems[i].num
	}
	return res
}
```

## 269. 日期之间隔几天（1360）

请你编写一个程序来计算两个日期之间隔了多少天。

日期以字符串形式给出，格式为 `YYYY-MM-DD`，如示例所示。

```go
func daysBetweenDates(date1 string, date2 string) int {
	isLeapYear := func(year int) bool {
		return year%4 == 0 && (year%100 != 0 || year%400 == 0)
	}

	splits1 := strings.Split(date1, "-")
	splits2 := strings.Split(date2, "-")

	year1, _ := strconv.Atoi(splits1[0])
	month1, _ := strconv.Atoi(splits1[1])
	day1, _ := strconv.Atoi(splits1[2])
	year2, _ := strconv.Atoi(splits2[0])
	month2, _ := strconv.Atoi(splits2[1])
	day2, _ := strconv.Atoi(splits2[2])

	prefixDayOfMonth := []int{31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365}

	getTimeStamp := func(year, month, day int) int {
		res := 0
		for i := 1971; i < year; i++ {
			if isLeapYear(i) {
				res += 366
			} else {
				res += 365
			}
		}
        if month > 1 {
            res += prefixDayOfMonth[month-2]
        }
		if month >= 3 && isLeapYear(year) {
			res++
		}
		res += day
		return res
	}

	Abs := func(num int) int {
		if num < 0 {
			return -num
		} else {
			return num
		}
	}

	timeStamp1 := getTimeStamp(year1, month1, day1)
	timeStamp2 := getTimeStamp(year2, month2, day2)

	return Abs(timeStamp1 - timeStamp2)
}
```

简洁版代码：

```go
func Abs(x int) int {
    if x < 0 {
        return -x
    } else {
        return x
    }
}

func daysBetweenDates(date1 string, date2 string) int {
    time1, _ := time.Parse("2006-01-02", date1)
    time2, _ := time.Parse("2006-01-02", date2)
    return Abs(int(time1.Sub(time2).Hours() / 24))
}
```

- 必须使用 `2006-01-02 15:04:05` 这样的数字作为格式模板，不能替换年份或数字顺序！
- 若输入字符串与 `layout` 的字面值不匹配（如用 `2007` 去解析 `2023`），会直接报错。
- 这种设计是 Go 语言的刻意选择，旨在通过规范化的方式简化时间处理。

## 270. 有多少小于当前数字的数字（1365）

给你一个数组 `nums`，对于其中每个元素 `nums[i]`，请你统计数组中比它小的所有数字的数目。

换而言之，对于每个 `nums[i]` 你必须计算出有效的 `j` 的数量，其中 `j` 满足 `j != i` **且** `nums[j] < nums[i]` 。

以数组形式返回答案。

```go
func smallerNumbersThanCurrent(nums []int) []int {
    sorted := make([]int, len(nums))
    copy(sorted, nums)
    sort.Ints(sorted)

    // 对于每一个数字，查找这个数字在 sorted 中第一次出现的下标
    find := func(target int) int {
        left := 0
        right := len(sorted) - 1
        for left <= right {
            mid := left + (right-left)>>1
            if sorted[mid] >= target {
                right = mid - 1
            } else {
                left = mid + 1
            }
        }
        return left
    }

    res := make([]int, len(nums))
    for i, num := range nums {
        res[i] = find(num)
    }

    return res
}
```













