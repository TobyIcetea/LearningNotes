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













待做题目：

```bash
1290. 二进制链表转整数
1135
80.1%
简单
1295. 统计位数为偶数的数字
843
79.3%
简单
1299. 将每个元素替换为右侧最大元素
701
77.9%
简单
1304. 和为零的 N 个不同整数
532
70.5%
简单
1309. 解码字母到整数映射
519
76.7%
简单
1313. 解压缩编码列表
684
83.4%
简单
1317. 将整数转换为两个无零整数的和
292
62.7%
简单
1323. 6 和 9 组成的最大数字
736
75.5%
简单
1331. 数组序号转换
566
60.5%
简单
1332. 删除回文子序列
399
78.1%
简单
1337. 矩阵中战斗力最弱的 K 行
981
68.6%
简单
1342. 将数字变成 0 的操作次数
1855
75.4%
简单
1346. 检查整数及其两倍数是否存在
619
41.9%
简单
1351. 统计有序矩阵中的负数
908
74.8%
简单
1356. 根据数字二进制下 1 的数目排序
756
74.6%
简单
1360. 日期之间隔几天
280
52.6%
简单
1365. 有多少小于当前数字的数字
1436
82.4%
简单
1370. 上升下降字符串
691
79.0%
简单
1374. 生成每种字符都是奇数个的字符串
574
77.9%
简单
1379. 找出克隆二叉树中的相同节点
359
85.5%
简单
1380. 矩阵中的幸运数
792
76.0%
简单
1385. 两个数组间的距离值
656
66.1%
简单
1389. 按既定顺序创建目标数组
620
82.7%
简单
1394. 找出数组中的幸运数
498
67.5%
简单
1399. 统计最大组的数目
239
66.6%
简单
1403. 非递增顺序的最小子序列
802
73.6%
简单
1408. 数组中的字符串匹配
600
64.4%
简单
1413. 逐步求和得到正数的最小值
759
73.3%
简单
1417. 重新格式化字符串
660
54.9%
简单
```





