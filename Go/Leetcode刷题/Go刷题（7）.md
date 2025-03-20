# Go 刷题（7）

## 181. 托普利茨矩阵

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

## 186. 写字符串需要的行数

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











待做题目：

```markdown
824. 山羊拉丁文
789
65.4%
简单
830. 较大分组的位置
764
54.5%
简单
832. 翻转图像
1209
79.6%
简单
836. 矩形重叠
823
49.7%
简单
844. 比较含退格的字符串
2412
48.0%
简单
859. 亲密字符串
969
35.1%
简单
860. 柠檬水找零
1821
59.3%
简单
867. 转置矩阵
987
68.5%
简单
868. 二进制间距
761
70.1%
简单
872. 叶子相似的树
1049
65.4%
简单
876. 链表的中间结点
4074
71.9%
简单
883. 三维形体投影面积
601
76.9%
简单
884. 两句话中的不常见单词
703
71.5%
简单
888. 公平的糖果交换
674
63.9%
简单
892. 三维形体的表面积
801
65.3%
简单
896. 单调数列
1237
56.6%
简单
897. 递增顺序搜索树
960
73.8%
简单
905. 按奇偶排序数组
1617
71.3%
简单
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





