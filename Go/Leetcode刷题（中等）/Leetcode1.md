# Leetcode1

## 1. 两数相加（2）

给你两个 **非空** 的链表，表示两个非负的整数。它们每位数字都是按照 **逆序** 的方式存储的，并且每个节点只能存储 **一位** 数字。

请你将两个数相加，并以相同形式返回一个表示和的链表。

你可以假设除了数字 0 之外，这两个数都不会以 0 开头。

```go
func addTwoNumbers(l1 *ListNode, l2 *ListNode) *ListNode {
    head := &ListNode{}
    tail := head
    carry := 0
    sum := 0

    for l1 != nil || l2 != nil {
        var num1 int
        var num2 int
        if l1 != nil {
            num1 = l1.Val
            l1 = l1.Next
        }
        if l2 != nil {
            num2 = l2.Val
            l2 = l2.Next
        }
        sum = num1 + num2 + carry
        carry, sum = sum / 10, sum % 10

        tail.Next = &ListNode{Val: sum}
        tail = tail.Next
    }

    if carry != 0 {
        tail.Next = &ListNode{Val: carry}
        tail = tail.Next
    }

    return head.Next
}
```

## 2. 无重复字符的最长子串（3）

给定一个字符串 `s` ，请你找出其中不含有重复字符的 **最长 子串** 的长度。

```go
func lengthOfLongestSubstring(s string) int {
	res := 0

	hasAppear := make([]bool, 128)
	left := 0
	right := 0
	for right < len(s) {
		for hasAppear[s[right]] {
			hasAppear[s[left]] = false
			left++
		}
		hasAppear[s[right]] = true
		right++
		res = max(res, right-left)
	}

	return res
}
```

## 3. 最长回文子串（5）

给你一个字符串 `s`，找到 `s` 中最长的 回文 子串。

```go
func longestPalindrome(s string) string {
	// 以每一个为中心，向外扩散
	res := ""
	maxLength := 0

	for mid := 0; mid < len(s); mid++ {
		// mid 是字符串的中心
		left := mid - 1
		right := mid + 1
		for left >= 0 && right < len(s) && s[left] == s[right] {
			left--
			right++
		}
		// left 和 right 都是开区间的边界
		if right-left-1 > maxLength {
			maxLength = right - left - 1
			res = s[left+1 : right]
		}

		// 另一种想法是，中间是两个一样，也就是说是偶数长度的最长回文串
		left = mid
		right = mid + 1
		hasCalculate := false
		for left >= 0 && right < len(s) && s[right] == s[left] {
			left--
			right++
			hasCalculate = true
		}
		// 这里的 left 和 right 也是开区间的边界
		if hasCalculate && right-left-1 > maxLength {
			maxLength = right - left - 1
			res = s[left+1 : right]
		}
	}

	return res
}
```

## 4. Z 字形变换（6）

将一个给定字符串 `s` 根据给定的行数 `numRows` ，以从上往下、从左到右进行 Z 字形排列。

比如输入字符串为 `"PAYPALISHIRING"` 行数为 `3` 时，排列如下：

```
P   A   H   N
A P L S I I G
Y   I   R
```

之后，你的输出需要从左往右逐行读取，产生出一个新的字符串，比如：`"PAHNAPLSIIGYIR"`。

请你实现这个将字符串进行指定行数变换的函数：

```
string convert(string s, int numRows);
```

Solution：

```go
func convert(s string, numRows int) string {
	if numRows == 1 {
		return s
	}

	var builder strings.Builder
	// 每 2n-2 是一个周期
	cycle := 2*numRows - 2
	for i := 0; i < len(s); i += cycle {
		builder.WriteByte(s[i])
	}

	left := 1
	right := cycle - 1
	for left != right {
		for i := 0; i < len(s); i += cycle {
			if i+left < len(s) {
				builder.WriteByte(s[i+left])
			}
			if i+right < len(s) {
				builder.WriteByte(s[i+right])
			}
		}
		left++
		right--
	}

	for i := 0; i < len(s); i += cycle {
		if i+left < len(s) {
			builder.WriteByte(s[i+left])
		}
	}

	return builder.String()
}
```

## 5. 整数反转（7）

给你一个 32 位的有符号整数 `x` ，返回将 `x` 中的数字部分反转后的结果。

如果反转后整数超过 32 位的有符号整数的范围 `[−231,  231 − 1]` ，就返回 0。

**假设环境不允许存储 64 位整数（有符号或无符号）。**

```go
func reverse(x int) int {
	res := 0
	for x != 0 {
		res = res*10 + x%10
		x = x / 10
	}

	if res > math.MaxInt32 || res < math.MinInt32 {
		return 0
	}

	return res
}
```

## 6. 字符串转换整数 (atoi)（8）

请你来实现一个 `myAtoi(string s)` 函数，使其能将字符串转换成一个 32 位有符号整数。

函数 `myAtoi(string s)` 的算法如下：

1. **空格：**读入字符串并丢弃无用的前导空格（`" "`）
2. **符号：**检查下一个字符（假设还未到字符末尾）为 `'-'` 还是 `'+'`。如果两者都不存在，则假定结果为正。
3. **转换：**通过跳过前置零来读取该整数，直到遇到非数字字符或到达字符串的结尾。如果没有读取数字，则结果为0。
4. **舍入：**如果整数数超过 32 位有符号整数范围 `[−231,  231 − 1]` ，需要截断这个整数，使其保持在这个范围内。具体来说，小于 `−231` 的整数应该被舍入为 `−231` ，大于 `231 − 1` 的整数应该被舍入为 `231 − 1` 。

返回整数作为最终结果。

```go
func myAtoi(s string) int {
	if s == "" {
		return 0
	}

	index := 0
	res := 0
	flagIsPositive := true

	// 丢弃无用的前导空格
	for index < len(s) && s[index] == ' ' {
		index++
	}

	if index < len(s) {
		if s[index] == '+' {
			index++
		} else if s[index] == '-' {
			flagIsPositive = false
			index++
		} else if !(s[index] >= '0' && s[index] <= '9') {
			return 0
		}
	}

	for index < len(s) && s[index] >= '0' && s[index] <= '9' {
		res = res*10 + int(s[index]-'0')
		index++

		if res > math.MaxInt32 {
			if flagIsPositive {
				return math.MaxInt32
			} else if -res < math.MinInt32 {
				return math.MinInt32
			}
		}
	}

	if !flagIsPositive {
		res = -res
	}

	return res
}
```

## 7. 盛最多水的容器（11）

给定一个长度为 `n` 的整数数组 `height` 。有 `n` 条垂线，第 `i` 条线的两个端点是 `(i, 0)` 和 `(i, height[i])` 。

找出其中的两条线，使得它们与 `x` 轴共同构成的容器可以容纳最多的水。

返回容器可以储存的最大水量。

**说明：**你不能倾斜容器。

```go
func maxArea(height []int) int {
	res := 0
	left := 0
	right := len(height) - 1
	for left < right {
		width := right - left
		res = max(res, width*min(height[left], height[right]))

		if height[left] < height[right] {
			left++
		} else {
			right--
		}
	}
	return res
}
```

## 8. 整数转罗马数字（12）

七个不同的符号代表罗马数字，其值如下：

| 符号 | 值   |
| ---- | ---- |
| I    | 1    |
| V    | 5    |
| X    | 10   |
| L    | 50   |
| C    | 100  |
| D    | 500  |
| M    | 1000 |

罗马数字是通过添加从最高到最低的小数位值的转换而形成的。将小数位值转换为罗马数字有以下规则：

- 如果该值不是以 4 或 9 开头，请选择可以从输入中减去的最大值的符号，将该符号附加到结果，减去其值，然后将其余部分转换为罗马数字。
- 如果该值以 4 或 9 开头，使用 **减法形式**，表示从以下符号中减去一个符号，例如 4 是 5 (`V`) 减 1 (`I`): `IV` ，9 是 10 (`X`) 减 1 (`I`)：`IX`。仅使用以下减法形式：4 (`IV`)，9 (`IX`)，40 (`XL`)，90 (`XC`)，400 (`CD`) 和 900 (`CM`)。
- 只有 10 的次方（`I`, `X`, `C`, `M`）最多可以连续附加 3 次以代表 10 的倍数。你不能多次附加 5 (`V`)，50 (`L`) 或 500 (`D`)。如果需要将符号附加4次，请使用 **减法形式**。

给定一个整数，将其转换为罗马数字。

```go
func intToRoman(num int) string {
	type ValueSymbol struct {
		value  int
		symbol string
	}
	arr := []ValueSymbol{
		{1000, "M"}, {900, "CM"}, {500, "D"}, {400, "CD"},
		{100, "C"}, {90, "XC"}, {50, "L"}, {40, "XL"},
		{10, "X"}, {9, "IX"}, {5, "V"}, {4, "IV"}, {1, "I"},
	}

	builder := &strings.Builder{}
	for _, vs := range arr {
		for num >= vs.value {
			builder.WriteString(vs.symbol)
			num -= vs.value
		}
	}

	return builder.String()
}
```

## 9. 三数之和（15）

给你一个整数数组 `nums` ，判断是否存在三元组 `[nums[i], nums[j], nums[k]]` 满足 `i != j`、`i != k` 且 `j != k` ，同时还满足 `nums[i] + nums[j] + nums[k] == 0` 。请你返回所有和为 `0` 且不重复的三元组。

**注意：**答案中不可以包含重复的三元组。

第一遍的思路：固定两个数字，再查找一个数字。

```go
func threeSum(nums []int) [][]int {
	sort.Ints(nums)

	res := make([][]int, 0)

	for i := 0; i < len(nums); i++ {
		if i > 0 && nums[i] == nums[i-1] {
			continue
		}
		for j := len(nums) - 1; j > i; j-- {
			if j != len(nums)-1 && nums[j] == nums[j+1] {
				continue
			}
			target := 0 - nums[i] - nums[j]
			// 在 i 和 j 之间寻找第一个等于 target 的值
			left := i + 1
			right := j - 1
			for left <= right {
				mid := left + (right-left)>>1
				if nums[mid] >= target {
					right = mid - 1
				} else {
					left = mid + 1
				}
			}
			// 最终得到的 left 就是第一个等于 target 的值
			if left > i && left < j && nums[left] == target {
				res = append(res, []int{nums[i], nums[j], nums[left]})
			}
		}
	}

	return res
}
```

第二种思路：固定一个数字，再查找两个数字：

```go
func threeSum(nums []int) [][]int {
	sort.Ints(nums)
	res := make([][]int, 0)

	for i := 0; i < len(nums)-2; i++ {
		if i > 0 && nums[i] == nums[i-1] {
			continue
		}

		// 第一个数字是 nums[i]
		// 在后续去查找 target 元素
		target := -nums[i]

		left := i + 1
		right := len(nums) - 1
		for left < right {
			if nums[left]+nums[right] == target {
				res = append(res, []int{nums[i], nums[left], nums[right]})
				left++
				right--
				for left < right && nums[left] == nums[left-1] {
					left++
				}
				for left < right && nums[right] == nums[right+1] {
					right--
				}
			} else if nums[left]+nums[right] < target {
				left++
			} else {
				right--
			}
		}
	}

	return res
}
```

将效率从 O(n^2logn) 提升到了 O(n^2)。









待做题目：

```python
16. 最接近的三数之和
44.8%
中等

17. 电话号码的字母组合
62.1%
中等

18. 四数之和
36.8%
中等

19. 删除链表的倒数第 N 个结点
51.1%
中等

22. 括号生成
78.8%
中等

24. 两两交换链表中的节点
74.3%
中等

29. 两数相除
22.4%
中等

31. 下一个排列
40.9%
中等

33. 搜索旋转排序数组
45.1%
中等

34. 在排序数组中查找元素的第一个和最后一个位置
45.2%
中等

36. 有效的数独
64.2%
中等

38. 外观数列
61.5%
中等

39. 组合总和
73.8%
中等

40. 组合总和 II
60.0%
中等

43. 字符串相乘
44.7%
中等

45. 跳跃游戏 II
44.9%
中等

46. 全排列
80.4%
中等

47. 全排列 II
66.7%
中等

48. 旋转图像
78.4%
中等

49. 字母异位词分组
69.9%
中等

50. Pow(x, n)
38.8%
中等

53. 最大子数组和
56.1%
中等

54. 螺旋矩阵
53.4%
中等

55. 跳跃游戏
43.8%
中等

56. 合并区间
51.5%
中等

57. 插入区间
42.8%
中等

59. 螺旋矩阵 II
70.7%
中等

61. 旋转链表
41.4%
中等

62. 不同路径
69.5%
中等

63. 不同路径 II
42.2%
中等

64. 最小路径和
72.0%
中等

71. 简化路径
47.2%
中等

72. 编辑距离
63.7%
中等

73. 矩阵置零
70.4%
中等

74. 搜索二维矩阵
51.2%
中等

75. 颜色分类
62.5%
中等

77. 组合
77.7%
中等

78. 子集
82.3%
中等

79. 单词搜索
48.9%
中等

80. 删除有序数组中的重复项 II
63.4%
中等

81. 搜索旋转排序数组 II
41.5%
中等

82. 删除排序链表中的重复元素 II
55.0%
中等

86. 分隔链表
65.6%
中等

89. 格雷编码
75.4%
中等

90. 子集 II
64.0%
中等

91. 解码方法
34.4%
中等

92. 反转链表 II
57.4%
中等

93. 复原 IP 地址
61.3%
中等

95. 不同的二叉搜索树 II
74.6%
中等

96. 不同的二叉搜索树
71.5%
中等

97. 交错字符串
45.9%
中等

98. 验证二叉搜索树
39.3%
中等

99. 恢复二叉搜索树
61.3%
中等
```





