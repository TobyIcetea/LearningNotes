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













待做题目：

```python
5. 最长回文子串
39.5%
中等

6. Z 字形变换
53.8%
中等

7. 整数反转
35.6%
中等

8. 字符串转换整数 (atoi)
21.6%
中等

11. 盛最多水的容器
61.3%
中等

12. 整数转罗马数字
68.7%
中等

15. 三数之和
39.4%
中等

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





