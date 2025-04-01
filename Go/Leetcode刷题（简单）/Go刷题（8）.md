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









待做题目：

```bash
993. 二叉树的堂兄弟节点
1227
59.4%
简单
997. 找到小镇的法官
1040
52.2%
简单
999. 可以被一步捕获的棋子数
761
72.8%
简单
1002. 查找共用字符
953
70.4%
简单
1005. K 次取反后最大化的数组和
1903
51.8%
简单
1009. 十进制整数的反码
403
58.6%
简单
1013. 将数组分成和相等的三个部分
1101
38.5%
简单
1018. 可被 5 整除的二进制前缀
478
50.1%
简单
1021. 删除最外层的括号
1125
81.5%
简单
1022. 从根到叶的二进制数之和
700
75.1%
简单
1025. 除数博弈
881
70.9%
简单
1030. 距离顺序排列矩阵单元格
564
70.9%
简单
1037. 有效的回旋镖
447
48.2%
简单
1046. 最后一块石头的重量
1361
65.3%
简单
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



