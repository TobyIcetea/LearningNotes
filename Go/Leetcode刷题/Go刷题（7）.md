# Go 刷题（7）

## 181. 托普利茨矩阵（766）

给你一个 `m x n` 的矩阵 `matrix` 。如果这个矩阵是托普利茨矩阵，返回 `true` ；否则，返回 `false` *。*

如果矩阵上每一条由左上到右下的对角线上的元素都相同，那么这个矩阵是 **托普利茨矩阵** 。

```go
func isToeplitzMatrix(matrix [][]int) bool {
    m := len(matrix)
    n := len(matrix[0])
    
    var checkLine func(i int, j int) bool
    checkLine = func(i int, j int) bool {
        num := matrix[i][j]
        i++
        j++
        for i < m && j < n {
            if matrix[i][j] != num {
                return false
            }
            i++
            j++
        }
        return true
    }

    // 检查第一行
    for j := 0; j < n; j++ {
        if !checkLine(0, j) {
            return false
        }
    }
    // 检查第一列
    for i := 1; i < m; i++ {
        if !checkLine(i, 0) {
            return false
        }
    }

    return true
}
```

## 182. 宝石与石头（771）

给你一个字符串 `jewels` 代表石头中宝石的类型，另有一个字符串 `stones` 代表你拥有的石头。 `stones` 中每个字符代表了一种你拥有的石头的类型，你想知道你拥有的石头中有多少是宝石。

字母区分大小写，因此 `"a"` 和 `"A"` 是不同类型的石头。

```go
func numJewelsInStones(jewels string, stones string) int {
    jewelSet := make(map[rune]struct{})
    for _, r := range jewels {
        jewelSet[r] = struct{}{}
    }
    
    res := 0

    for _, stone := range stones {
        if _, ok := jewelSet[stone]; ok {
            res++
        }
    }

    return res
}
```

## 183. 二叉搜索树节点最小距离（783）

给你一个二叉搜索树的根节点 `root` ，返回 **树中任意两不同节点值之间的最小差值** 。

差值是一个正数，其数值等于两值之差的绝对值。

```go
import "math"
func minDiffInBST(root *TreeNode) int {
    // 二叉搜索树就用中序遍历
    res := math.MaxInt
    pre := -1
    first := true

    var inorder func(root *TreeNode)
    inorder = func(root *TreeNode) {
        if root == nil {
            return
        }
        inorder(root.Left)
        
        if first {
            pre = root.Val
            first = false
        } else {
            diff := root.Val - pre
            res = min(res, diff)
            pre = root.Val
        }

        inorder(root.Right)
    }

    inorder(root)

    return res
}
```

## 184. 旋转字符串（796）

给定两个字符串, `s` 和 `goal`。如果在若干次旋转操作之后，`s` 能变成 `goal` ，那么返回 `true` 。

`s` 的 **旋转操作** 就是将 `s` 最左边的字符移动到最右边。 

- 例如, 若 `s = 'abcde'`，在旋转一次之后结果就是`'bcdea'` 。

```go
import "strings"

func rotateString(s string, goal string) bool {
    if len(s) != len(goal) {
        return false
    }
    return strings.Contains(s + s, goal)
}
```

## 185. 唯一摩尔斯密码词（804）

国际摩尔斯密码定义一种标准编码方式，将每个字母对应于一个由一系列点和短线组成的字符串， 比如:

- `'a'` 对应 `".-"` ，
- `'b'` 对应 `"-..."` ，
- `'c'` 对应 `"-.-."` ，以此类推。

为了方便，所有 `26` 个英文字母的摩尔斯密码表如下：

```
[".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--.."]
```

给你一个字符串数组 `words` ，每个单词可以写成每个字母对应摩尔斯密码的组合。

- 例如，`"cab"` 可以写成 `"-.-..--..."` ，(即 `"-.-."` + `".-"` + `"-..."` 字符串的结合)。我们将这样一个连接过程称作 **单词翻译** 。

对 `words` 中所有单词进行单词翻译，返回不同 **单词翻译** 的数量。

```go
import "strings"
func uniqueMorseRepresentations(words []string) int {
    morseCode := map[rune]string{
        'a': ".-",
        'b': "-...",
        'c': "-.-.",
        'd': "-..",
        'e': ".",
        'f': "..-.",
        'g': "--.",
        'h': "....",
        'i': "..",
        'j': ".---",
        'k': "-.-",
        'l': ".-..",
        'm': "--",
        'n': "-.",
        'o': "---",
        'p': ".--.",
        'q': "--.-",
        'r': ".-.",
        's': "...",
        't': "-",
        'u': "..-",
        'v': "...-",
        'w': ".--",
        'x': "-..-",
        'y': "-.--",
        'z': "--..",
    }

    translatedSet := make(map[string]struct{})
    for _, word := range words {
        // 翻译 word
        var builder strings.Builder
        for _, r := range word {
            builder.WriteString(morseCode[r])
        }
        translatedSet[builder.String()] = struct{}{}
    }

    return len(translatedSet)
}
```

## 186. 写字符串需要的行数（806）

我们要把给定的字符串 `S` 从左到右写到每一行上，每一行的最大宽度为100个单位，如果我们在写某个字母的时候会使这行超过了100 个单位，那么我们应该把这个字母写到下一行。我们给定了一个数组 `widths` ，这个数组 widths[0] 代表 'a' 需要的单位， widths[1] 代表 'b' 需要的单位，...， widths[25] 代表 'z' 需要的单位。

现在回答两个问题：至少多少行能放下`S`，以及最后一行使用的宽度是多少个单位？将你的答案作为长度为2的整数列表返回。

```go
func numberOfLines(widths []int, s string) []int {
    // widths 表示 a、b、c、d 这些字母分别占用多少行
    // 所以每一个字母占用的宽度就是 widths[r - 'a']
    line := 1
    curWidth := 0
    for _, r := range s {
        curWidth += widths[r - 'a']
        if curWidth > 100 {
            line++
            curWidth = widths[r - 'a']
        }
    }
    return []int{line, curWidth}
}
```

## 187. 最大三角形面积（812）

给你一个由 **X-Y** 平面上的点组成的数组 `points` ，其中 `points[i] = [xi, yi]` 。从其中取任意三个不同的点组成三角形，返回能组成的最大三角形的面积。与真实值误差在 `10-5` 内的答案将会视为正确答案。

```go
import "math"
func largestTriangleArea(points [][]int) float64 {
    // 计算三个点的三角形的面积：
    // S = 1/2[x1(y2-y3) + x2(y3-y1) + x3(y1-y2)]
    var calculateArea func(x1, y1, x2, y2, x3, y3 int) float64
    calculateArea = func(x1, y1, x2, y2, x3, y3 int) float64 {
        return math.Abs(float64(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2)
    }

    var res float64

    // 暴力遍历所有的点
    n := len(points)
    for i := 0; i < n; i++ {
        for j := i + 1; j < n; j++ {
            for k := j + 1; k < n; k++ {
                res = max(res, calculateArea(points[i][0], points[i][1], points[j][0], points[j][1], points[k][0], points[k][1]))
            }
        }
    }

    return res
}
```

纯数学题，用到的公式叫做“鞋带公式”，这个公式广泛用于计算平面中多边形的面积。

## 188. 最常见的单词（819）

给你一个字符串 `paragraph` 和一个表示禁用词的字符串数组 `banned` ，返回出现频率最高的非禁用词。题目数据 **保证** 至少存在一个非禁用词，且答案 **唯一** 。

`paragraph` 中的单词 **不区分大小写** ，答案应以 **小写** 形式返回。

```go
import (
	"fmt"
	"regexp"
	"strings"
	"unicode"
)

func mostCommonWord(paragraph string, banned []string) string {
    // 判断一个字符是不是标点符号
    isSeparator := func(r rune) bool {
        return !unicode.IsLetter(r)
    }

	words := strings.FieldsFunc(strings.ToLower(paragraph), isSeparator)

    // 将所有的非小写字母都删除
	re := regexp.MustCompile(`[^a-z]`)
	for i, word := range words {
		if !unicode.IsLetter(rune(word[len(word)-1])) {
			words[i] = re.ReplaceAllString(word, "")
		}
	}

	wordCounts := make(map[string]int)
	for _, word := range words {
		wordCounts[word]++
	}

	bannedWordSet := make(map[string]struct{})
	for _, word := range banned {
		bannedWordSet[word] = struct{}{}
	}

	maxCount := 0
	res := ""
	for word, count := range wordCounts {
		if _, ok := bannedWordSet[word]; ok {
			continue
		}
		if count > maxCount {
			maxCount = count
			res = word
		}
	}

	return res
}
```

## 189. 字符的最短距离（821）

给你一个字符串 `s` 和一个字符 `c` ，且 `c` 是 `s` 中出现过的字符。

返回一个整数数组 `answer` ，其中 `answer.length == s.length` 且 `answer[i]` 是 `s` 中从下标 `i` 到离它 **最近** 的字符 `c` 的 **距离** 。

两个下标 `i` 和 `j` 之间的 **距离** 为 `abs(i - j)` ，其中 `abs` 是绝对值函数。

```go
import "math"

func shortestToChar(s string, c byte) []int {
    // 左边遍历一次，右边遍历一次
    answer := make([]int, len(s))

    preCharIndex := -1
    for i := 0; i < len(answer); i++ {
        if s[i] == c {
            preCharIndex = i
        }
        if preCharIndex == -1 {
            answer[i] = math.MaxInt
        } else {
            answer[i] = i - preCharIndex
        }
    }

    preCharIndex = -1
    for i := len(answer) - 1; i >= 0; i-- {
        if s[i] == c {
            preCharIndex = i
        }
        if preCharIndex != -1 {
            answer[i] = min(answer[i], preCharIndex - i)
        }
    }

    return answer
}
```

## 190. 山羊拉丁文（824）

给你一个由若干单词组成的句子 sentence ，单词间由空格分隔。每个单词仅由大写和小写英文字母组成。

请你将句子转换为 “山羊拉丁文（Goat Latin）”（一种类似于 猪拉丁文 - Pig Latin 的虚构语言）。山羊拉丁文的规则如下：

- 如果单词以元音开头（'a', 'e', 'i', 'o', 'u'），在单词后添加"ma"。
    - 例如，单词 "apple" 变为 "applema" 。
- 如果单词以辅音字母开头（即，非元音字母），移除第一个字符并将它放到末尾，之后再添加"ma"。
    - 例如，单词 "goat" 变为 "oatgma" 。
- 根据单词在句子中的索引，在单词最后添加与索引相同数量的字母'a'，索引从 1 开始。
    - 例如，在第一个单词后添加 "a" ，在第二个单词后添加 "aa" ，以此类推。

返回将 sentence 转换为山羊拉丁文后的句子。

```go
import (
    "strings"
    "unicode"
)

func toGoatLatin(sentence string) string {
	vowels := make(map[rune]struct{})
	vowels['a'] = struct{}{}
	vowels['e'] = struct{}{}
	vowels['i'] = struct{}{}
	vowels['o'] = struct{}{}
	vowels['u'] = struct{}{}

	words := strings.Fields(sentence)
	for i, word := range words {
		runes := []rune(word)

		_, ok1 := vowels[runes[0]]
		_, ok2 := vowels[unicode.ToLower(runes[0])]
		if ok1 || ok2 {
			// 单词以元音字母开头
			runes = append(runes, 'm', 'a')
		} else {
			// 单词以辅音字母开头
			runes = append(runes[1:], runes[0], 'm', 'a')
		}
		// 再添加 i+1 个 'a'
		for j := 0; j < i+1; j++ {
			runes = append(runes, 'a')
		}
		words[i] = string(runes)
	}

	// 将 words 拼接成一个句子
	var builder strings.Builder
	for i, word := range words {
		builder.WriteString(word)
		if i != len(words)-1 {
			builder.WriteString(" ")
		}
	}

	return builder.String()
}
```

## 191. 较大分组的位置（830）

在一个由小写字母构成的字符串 `s` 中，包含由一些连续的相同字符所构成的分组。

例如，在字符串 `s = "abbxxxxzyy"` 中，就含有 `"a"`, `"bb"`, `"xxxx"`, `"z"` 和 `"yy"` 这样的一些分组。

分组可以用区间 `[start, end]` 表示，其中 `start` 和 `end` 分别表示该分组的起始和终止位置的下标。上例中的 `"xxxx"` 分组用区间表示为 `[3,6]` 。

我们称所有包含大于或等于三个连续字符的分组为 **较大分组** 。

找到每一个 **较大分组** 的区间，**按起始位置下标递增顺序排序后**，返回结果。

```go
func largeGroupPositions(s string) [][]int {
    begin := -1
    res := make([][]int, 0)

    for i, _ := range s {
        if begin == -1 {
            // 还没开始
            begin = i
        } else {
            // 已经开始了
            if s[i] != s[i - 1] {
                len := i - begin
                if len >= 3 {
                    res = append(res, []int{begin, i - 1})
                }
                begin = i
            }
        }
    }
    if len(s) - begin >= 3 {
        res = append(res, []int{begin, len(s) - 1})
    }

    return res
}
```

## 192. 矩阵重叠（836）

矩形以列表 `[x1, y1, x2, y2]` 的形式表示，其中 `(x1, y1)` 为左下角的坐标，`(x2, y2)` 是右上角的坐标。矩形的上下边平行于 x 轴，左右边平行于 y 轴。

如果相交的面积为 **正** ，则称两矩形重叠。需要明确的是，只在角或边接触的两个矩形不构成重叠。

给出两个矩形 `rec1` 和 `rec2` 。如果它们重叠，返回 `true`；否则，返回 `false` 。

```go
func isRectangleOverlap(rec1 []int, rec2 []int) bool {
    // 如果两个矩阵在 x 轴和 y 轴上的投影都重叠，那么这两个矩阵就重叠
    overlapX := !(rec1[2] <= rec2[0] || rec2[2] <= rec1[0])
    overlapY := !(rec1[3] <= rec2[1] || rec2[3] <= rec1[1])
    return overlapX && overlapY
}
```

## 193. 比较含退格的字符串（844）

给定 `s` 和 `t` 两个字符串，当它们分别被输入到空白的文本编辑器后，如果两者相等，返回 `true` 。`#` 代表退格字符。

**注意：**如果对空文本输入退格字符，文本继续为空。

```go
func backspaceCompare(s string, t string) bool {
    runes1 := make([]rune, 0, len(s))
    runes2 := make([]rune, 0, len(t))
    
    for _, c := range s {
        if c == '#' {
            if len(runes1) > 0 {
                runes1 = runes1[:len(runes1) - 1]
            }            
        } else {
            runes1 = append(runes1, c)
        }
    }
    for _, c := range t {
        if c == '#' {
            if len(runes2) > 0 {
                runes2 = runes2[:len(runes2) - 1]
            }
        } else {
            runes2 = append(runes2, c)
        }
    }
    if len(runes1) != len(runes2) {
        return false
    }
    for i := 0; i < len(runes1); i++ {
        if runes1[i] != runes2[i] {
            return false
        }
    }

    return true
}
```

## 194. 亲密字符串（859）

给你两个字符串 `s` 和 `goal` ，只要我们可以通过交换 `s` 中的两个字母得到与 `goal` 相等的结果，就返回 `true` ；否则返回 `false` 。

交换字母的定义是：取两个下标 `i` 和 `j` （下标从 `0` 开始）且满足 `i != j` ，接着交换 `s[i]` 和 `s[j]` 处的字符。

- 例如，在 `"abcd"` 中交换下标 `0` 和下标 `2` 的元素可以生成 `"cbad"` 。

```go
func buddyStrings(s string, goal string) bool {
    // 1. 有两个地方不相同，其他地方都相同，且这两个地方处的元素一样
    // 2. 全都相同，且有一个元素出现了两次
    if len(s) != len(goal) {
        return false
    }
    n := len(s)
    
    hasAppear := make([]bool, 128)  // 看一个元素是不是出现过
    hasDuplicate := false
    diffIndexes := make([]int, 0)  // 所有不同元素的下标
    for i := 0; i < n; i++ {
        if s[i] != goal[i] {
            diffIndexes = append(diffIndexes, i)
        }
        if !hasDuplicate {
            if hasAppear[int(s[i])] {
                hasDuplicate = true
            } else {
                hasAppear[int(s[i])] = true
            }
        }
    }

    if len(diffIndexes) == 0 {
        return hasDuplicate
    } else if len(diffIndexes) == 2 {
        return s[diffIndexes[0]] == goal[diffIndexes[1]] && s[diffIndexes[1]] == goal[diffIndexes[0]]
    } else {
        return false
    }
}
```

## 195. 柠檬水找零（860）

在柠檬水摊上，每一杯柠檬水的售价为 `5` 美元。顾客排队购买你的产品，（按账单 `bills` 支付的顺序）一次购买一杯。

每位顾客只买一杯柠檬水，然后向你付 `5` 美元、`10` 美元或 `20` 美元。你必须给每个顾客正确找零，也就是说净交易是每位顾客向你支付 `5` 美元。

注意，一开始你手头没有任何零钱。

给你一个整数数组 `bills` ，其中 `bills[i]` 是第 `i` 位顾客付的账。如果你能给每位顾客正确找零，返回 `true` ，否则返回 `false` 。

```go
func lemonadeChange(bills []int) bool {
    countOf5 := 0
    countOf10 := 0

    for _, num := range bills {
        if num == 5 {
            countOf5++
        } else if num == 10 {
            if countOf5 >= 1 {
                countOf10++
                countOf5--
            } else {
                return false
            }
        } else {
            if countOf10 >= 1 && countOf5 >= 1 {
                countOf10--
                countOf5--
            } else if countOf5 >= 3 {
                countOf5 -= 3
            } else {
                return false
            }
        }
    }

    return true
}
```

## 196. 二进制间距（868）

给定一个正整数 `n`，找到并返回 `n` 的二进制表示中两个 **相邻** 1 之间的 **最长距离** 。如果不存在两个相邻的 1，返回 `0` 。

如果只有 `0` 将两个 `1` 分隔开（可能不存在 `0` ），则认为这两个 1 彼此 **相邻** 。两个 `1` 之间的距离是它们的二进制表示中位置的绝对差。例如，`"1001"` 中的两个 `1` 的距离为 3 。

```go
func binaryGap(n int) int {
    first := true
    indexDiff := 0
    res := 0

    for n != 0 {
        if n & 1 == 1 {
            // 是 1
            if first {
                first = false
            } else {
                res = max(res, indexDiff)
            }
            indexDiff = 0
        }
        indexDiff++
        n = n >> 1
    }

    return res
}
```

## 197. 三维形体投影面积（883）

在 `n x n` 的网格 `grid` 中，我们放置了一些与 x，y，z 三轴对齐的 `1 x 1 x 1` 立方体。

每个值 `v = grid[i][j]` 表示 `v` 个正方体叠放在单元格 `(i, j)` 上。

现在，我们查看这些立方体在 `xy` 、`yz` 和 `zx` 平面上的*投影*。

**投影** 就像影子，将 **三维** 形体映射到一个 **二维** 平面上。从顶部、前面和侧面看立方体时，我们会看到“影子”。

返回 *所有三个投影的总面积* 。

```go
func projectionArea(grid [][]int) int {
    m := len(grid)
    n := len(grid[0])
    
    res1 := 0
    for i := 0; i < m; i++ {
        for j := 0; j < n; j++ {
            if grid[i][j] != 0 {
                res1++
            }
        }
    }

    res2 := 0
    for i := 0; i < m; i++ {
        maxHeight := 0
        for j := 0; j < n; j++ {
            maxHeight = max(maxHeight, grid[i][j])
        }
        res2 += maxHeight
    }

    res3 := 0
    for j := 0; j < n; j++ {
        maxHeight := 0
        for i := 0; i < m; i++ {
            maxHeight = max(maxHeight, grid[i][j])
        }
        res3 += maxHeight
    }

    return res1 + res2 + res3
}
```

## 198. 两句话中的不常见单词（884）

**句子** 是一串由空格分隔的单词。每个 **单词** 仅由小写字母组成。

如果某个单词在其中一个句子中恰好出现一次，在另一个句子中却 **没有出现** ，那么这个单词就是 **不常见的** 。

给你两个 **句子** `s1` 和 `s2` ，返回所有 **不常用单词** 的列表。返回列表中单词可以按 **任意顺序** 组织。

```go
func uncommonFromSentences(s1 string, s2 string) []string {
    // 直接哈希
    countS1 := make(map[string]int)
    countS2 := make(map[string]int)

    begin := 0
    for i, c := range s1 {
        if c == ' ' {
            countS1[s1[begin:i]]++
            begin = i + 1
        }
    }
    countS1[s1[begin:]]++

    begin = 0
    for i, c := range s2 {
        if c == ' ' {
            countS2[s2[begin:i]]++
            begin = i + 1
        }
    }
    countS2[s2[begin:]]++

    res := make([]string, 0)

    for word, count := range countS1 {
        if count == 1 && countS2[word] == 0 {
            res = append(res, word)
        }
    }
    for word, count := range countS2 {
        if count == 1 && countS1[word] == 0 {
            res = append(res, word)
        }
    }
    
    return res
}
```

## 199. 公平的糖果交换（888）

爱丽丝和鲍勃拥有不同总数量的糖果。给你两个数组 `aliceSizes` 和 `bobSizes` ，`aliceSizes[i]` 是爱丽丝拥有的第 `i` 盒糖果中的糖果数量，`bobSizes[j]` 是鲍勃拥有的第 `j` 盒糖果中的糖果数量。

两人想要互相交换一盒糖果，这样在交换之后，他们就可以拥有相同总数量的糖果。一个人拥有的糖果总数量是他们每盒糖果数量的总和。

返回一个整数数组 `answer`，其中 `answer[0]` 是爱丽丝必须交换的糖果盒中的糖果的数目，`answer[1]` 是鲍勃必须交换的糖果盒中的糖果的数目。如果存在多个答案，你可以返回其中 **任何一个** 。题目测试用例保证存在与输入对应的答案。

```go
import "sort"

func fairCandySwap(aliceSizes []int, bobSizes []int) []int {
    sort.Ints(aliceSizes)
    sort.Ints(bobSizes)

    binaryFind := func(arr []int, target int) int {
        left := 0
        right := len(arr) - 1
        for left <= right {
            mid := (left + right) / 2
            if arr[mid] > target {
                right = mid - 1
            } else if arr[mid] < target {
                left = mid + 1
            } else {
                return mid
            }
        }
        return -1
    }

    sum1 := 0
    sum2 := 0
    for _, num := range aliceSizes {
        sum1 += num
    }
    for _, num := range bobSizes {
        sum2 += num
    }
    half := (sum1 + sum2) / 2

    if sum1 < half {
        diff := sum2 - half
        // 对于 arr1 中的每一个数字 num，差值为 target - sum1
        // 看 num + diff 在不在 arr2 中
        for i, num := range aliceSizes {
            if i > 0 && aliceSizes[i] == aliceSizes[i - 1] {
                continue
            }
            if binaryFind(bobSizes, num + diff) != -1 {
                return []int{num, num + diff}
            }
        }
    } else {
        // sum1 > target
        diff := sum1 - half
        for i, num := range bobSizes {
            if i > 0 && bobSizes[i] == bobSizes[i - 1] {
                continue
            }
            if binaryFind(aliceSizes, num + diff) != -1 {
                return []int{num + diff, num}
            }
        }
    }
    return []int{}

}
```

## 200. 三维形体的表面积（892）

给你一个 `n * n` 的网格 `grid` ，上面放置着一些 `1 x 1 x 1` 的正方体。每个值 `v = grid[i][j]` 表示 `v` 个正方体叠放在对应单元格 `(i, j)` 上。

放置好正方体后，任何直接相邻的正方体都会互相粘在一起，形成一些不规则的三维形体。

请你返回最终这些形体的总表面积。

**注意：**每个形体的底面也需要计入表面积中。

```go
func surfaceArea(grid [][]int) int {
    res := 0

    n := len(grid)
    // 上面和底面
    for i := 0; i < n; i++ {
        for j := 0; j < n; j++ {
            if grid[i][j] != 0 {
                res++
            }
        }
    }
    res += res

    // 四面
    pre := 0
    for i := 0; i < n; i++ {
        pre = 0
        for j := 0; j < n; j++ {
            if grid[i][j] > pre {
                res += grid[i][j] - pre
            }
            pre = grid[i][j]
        }
    }

    for i := 0; i < n; i++ {
        pre = 0
        for j := n - 1; j >= 0; j-- {
            if grid[i][j] > pre {
                res += grid[i][j] - pre
            }
            pre = grid[i][j]
        }
    }


    for j := 0; j < n; j++ {
        pre = 0
        for i := 0; i < n; i++ {
            if grid[i][j] > pre {
                res += grid[i][j] - pre
            }
            pre = grid[i][j]
        }
    }

    
    for j := 0; j < n; j++ {
        pre = 0
        for i := n - 1; i >= 0; i-- {
            if grid[i][j] > pre {
                res += grid[i][j] - pre
            }
            pre = grid[i][j]
        }
    }

    return res
}
```

## 201. 递增顺序搜索树（897）

给你一棵二叉搜索树的 `root` ，请你 **按中序遍历** 将其重新排列为一棵递增顺序搜索树，使树中最左边的节点成为树的根节点，并且每个节点没有左子节点，只有一个右子节点。

```go
func increasingBST(root *TreeNode) *TreeNode {
    var pre *TreeNode
    var res *TreeNode

    var inorder func(root *TreeNode)
    inorder = func(root *TreeNode) {
        if root == nil {
            return
        }
        inorder(root.Left)
        root.Left = nil
        if pre == nil {
            res = root
        } else {
            pre.Right = root
        }
        pre = root
        inorder(root.Right)
    }
    inorder(root)

    return res
}
```

## 202. 按奇偶排序数组（905）

给你一个整数数组 `nums`，将 `nums` 中的的所有偶数元素移动到数组的前面，后跟所有奇数元素。

返回满足此条件的 **任一数组** 作为答案。

```go
func sortArrayByParity(nums []int) []int {
    // 对撞指针
    i := 0
    j := len(nums) - 1
    for i < j {
        for i < j && nums[i] & 1 == 0 {
            i++
        }
        for i < j && nums[j] & 1 == 1 {
            j--
        }
        if i < j {
            nums[i], nums[j] = nums[j], nums[i]
        }
    }
    return nums
}
```









待做题目：

```markdown
908. 最小差值 I
726
76.8%
简单
914. 卡牌分组
798
37.1%
简单
917. 仅仅反转字母
1175
59.3%
简单
922. 按奇偶排序数组 II
1278
72.5%
简单
925. 长按键入
903
37.3%
简单
929. 独特的电子邮件地址
582
68.5%
简单
```





