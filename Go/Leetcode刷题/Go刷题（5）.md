# Go 刷题（5）

## 121. 二叉树的所有路径（257）

给你一个二叉树的根节点 `root` ，按 **任意顺序** ，返回所有从根节点到叶子节点的路径。

**叶子节点** 是指没有子节点的节点。

```go
import (
    "strings"
    "strconv"
)

func binaryTreePaths(root *TreeNode) []string {
    res := make([]string, 0)

    path := make([]int, 0)

    var generateRes func()
    generateRes = func() {
        // 根据 path 产生一个结果到 res 中
        var sb strings.Builder
        sb.WriteString(strconv.Itoa(path[0]))
        for i := 1; i < len(path); i++ {
            sb.WriteString("->" + strconv.Itoa(path[i]))
        }
        res = append(res, sb.String())
    }

    var dfs func(node *TreeNode)
    dfs = func(node *TreeNode) {
        if node == nil {
            return
        }
        path = append(path, node.Val)
        if node.Left == nil && node.Right == nil {
            generateRes()
        } else {
            dfs(node.Left)
            dfs(node.Right)
        }
        path = path[:len(path) - 1]
    }

    dfs(root)
    return res
}
```

## 122. 丢失的数字（268）

给定一个包含 `[0, n]` 中 `n` 个数的数组 `nums` ，找出 `[0, n]` 这个范围内没有出现在数组中的那个数。

```go
func missingNumber(nums []int) int {
    // 计算 0 + 1 + 2 + ... + n 的和
    n := len(nums)
    expectedSum := n * (n + 1) / 2
    actualSum := 0
    for _, num := range nums {
        actualSum += num
    }
    return expectedSum - actualSum
}
```

## 123. 第一个错误的版本（278）

你是产品经理，目前正在带领一个团队开发新的产品。不幸的是，你的产品的最新版本没有通过质量检测。由于每个版本都是基于之前的版本开发的，所以错误的版本之后的所有版本都是错的。

假设你有 `n` 个版本 `[1, 2, ..., n]`，你想找出导致之后所有版本出错的第一个错误的版本。

你可以通过调用 `bool isBadVersion(version)` 接口来判断版本号 `version` 是否在单元测试中出错。实现一个函数来查找第一个错误的版本。你应该尽量减少对调用 API 的次数。

```go
func firstBadVersion(n int) int {
    // 二分查找
    left := 1
    right := n
    for left <= right {
        mid := left + (right - left) / 2
        if isBadVersion(mid) {
            right = mid - 1
        } else {
            left = mid + 1
        }
    }
    return left
}
```

## 124. Nim游戏（292）

你和你的朋友，两个人一起玩 [Nim 游戏](https://baike.baidu.com/item/Nim游戏/6737105)：

- 桌子上有一堆石头。
- 你们轮流进行自己的回合， **你作为先手** 。
- 每一回合，轮到的人拿掉 1 - 3 块石头。
- 拿掉最后一块石头的人就是获胜者。

假设你们每一步都是最优解。请编写一个函数，来判断你是否可以在给定石头数量为 `n` 的情况下赢得游戏。如果可以赢，返回 `true`；否则，返回 `false` 。

```go
func canWinNim(n int) bool {
    return n%4 != 0
}
```

## 125. 区域和检索-数组不可变（303）

给定一个整数数组  `nums`，处理以下类型的多个查询:

1. 计算索引 `left` 和 `right` （包含 `left` 和 `right`）之间的 `nums` 元素的 **和** ，其中 `left <= right`

实现 `NumArray` 类：

- `NumArray(int[] nums)` 使用数组 `nums` 初始化对象
- `int sumRange(int i, int j)` 返回数组 `nums` 中索引 `left` 和 `right` 之间的元素的 **总和** ，包含 `left` 和 `right` 两点（也就是 `nums[left] + nums[left + 1] + ... + nums[right]` )

```go
type NumArray struct {
    prefixSum []int
}


func Constructor(nums []int) NumArray {
    n := len(nums)
    prefixSum := make([]int, n+1)
    
    for i := 0; i < n; i++ {
        prefixSum[i+1] = prefixSum[i] + nums[i]  // 计算前缀和
    }

    return NumArray{prefixSum: prefixSum}
}


func (this *NumArray) SumRange(left int, right int) int {
    return this.prefixSum[right + 1] - this.prefixSum[left]
}
```

## 126. 3的幂（326）

给定一个整数，写一个函数来判断它是否是 3 的幂次方。如果是，返回 `true` ；否则，返回 `false` 。

整数 `n` 是 3 的幂次方需满足：存在整数 `x` 使得 `n == 3x`。

```go
func isPowerOfThree(n int) bool {
    for n > 0 && n % 3 == 0 {
        n = n / 3
    }
    return n == 1
}
```

或者有一种更加巧妙的办法：在 32 位有符号数中，最大的 3 的幂是 3^19 = 1162261467。所以我们只需要判断 n 是否是 3^19 的约数即可：

```go
func isPowerOfThree(n int) bool {
    return n > 0 && 1162261467 % n == 0
}
```

## 127. 4的幂（342）

给定一个整数，写一个函数来判断它是否是 4 的幂次方。如果是，返回 `true` ；否则，返回 `false` 。

整数 `n` 是 4 的幂次方需满足：存在整数 `x` 使得 `n == 4x`。

```go
func isPowerOfFour(n int) bool {
    // 三个条件：
    // 1. 大于 0
    // 2. 整个数字中只能有一个 1 存在（是2的幂）
    // 3. 这个 1 必须是在奇数位的位数上
    return n>0 && n&(n-1)==0 && n&0x55555555!=0
}
```

## 128. 两个数组的交集II（350）

给你两个整数数组 `nums1` 和 `nums2` ，请你以数组形式返回两数组的交集。返回结果中每个元素出现的次数，应与元素在两个数组中都出现的次数一致（如果出现次数不一致，则考虑取较小值）。可以不考虑输出结果的顺序。

```go
func intersect(nums1 []int, nums2 []int) []int {
    sort.Ints(nums1)
    sort.Ints(nums2)
    i := 0
    j := 0
    res := make([]int, 0)
    for i < len(nums1) && j < len(nums2) {
        if nums1[i] < nums2[j] {
            i++
        } else if nums1[i] > nums2[j] {
            j++
        } else {
            res = append(res, nums1[i])
            i++
            j++
        }
    }
    return res
}
```

## 129. 猜数字大小（374）

我们正在玩猜数字游戏。猜数字游戏的规则如下：

我会从 `1` 到 `n` 随机选择一个数字。 请你猜选出的是哪个数字。

如果你猜错了，我会告诉你，我选出的数字比你猜测的数字大了还是小了。

你可以通过调用一个预先定义好的接口 `int guess(int num)` 来获取猜测结果，返回值一共有三种可能的情况：

- `-1`：你猜的数字比我选出的数字大 （即 `num > pick`）。
- `1`：你猜的数字比我选出的数字小 （即 `num < pick`）。
- `0`：你猜的数字与我选出的数字相等。（即 `num == pick`）。

返回我选出的数字。

```go
func guessNumber(n int) int {
    left := 1
    right := n
    for left <= right {
        mid := (left + right) / 2
        guessRes := guess(mid)
        if guessRes == 1 {
            left = mid + 1
        } else if guessRes == -1 {
            right = mid - 1
        } else {
            return mid
        }
    }
    return -1
}
```

## 130. 赎金信（383）

给你两个字符串：`ransomNote` 和 `magazine` ，判断 `ransomNote` 能不能由 `magazine` 里面的字符构成。

如果可以，返回 `true` ；否则返回 `false` 。

`magazine` 中的每个字符只能在 `ransomNote` 中使用一次。

```go
func canConstruct(ransomNote string, magazine string) bool {
    counts := make([]int, 128)
    for _, char := range magazine {
        counts[char]++
    }
    for _, char := range ransomNote {
        counts[char]--
    }
    for i := 'a'; i <= 'z'; i++ {
        if counts[i] < 0 {
            return false
        }
    }
    return true
}
```

## 131. 找不同（389）

给定两个字符串 `s` 和 `t` ，它们只包含小写字母。

字符串 `t` 由字符串 `s` 随机重排，然后在随机位置添加一个字母。

请找出在 `t` 中被添加的字母。

```go
func findTheDifference(s string, t string) byte {
    var res byte
    for i := 0; i < len(s); i++ {
        res = res ^ s[i]
    }
    for i := 0; i < len(t); i++ {
        res = res ^ t[i]
    }
    return res
}
```

## 132. 二进制手表（401）

二进制手表顶部有 4 个 LED 代表 **小时（0-11）**，底部的 6 个 LED 代表 **分钟（0-59）**。每个 LED 代表一个 0 或 1，最低位在右侧。

例如，下面的二进制手表读取 `"4:51"` 。

<img src="https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/binarywatch.jpg" alt="img" style="zoom:50%;" />

给你一个整数 `turnedOn` ，表示当前亮着的 LED 的数量，返回二进制手表可以表示的所有可能时间。你可以 **按任意顺序** 返回答案。

小时不会以零开头：

- 例如，`"01:00"` 是无效的时间，正确的写法应该是 `"1:00"` 。

分钟必须由两位数组成，可能会以零开头：

- 例如，`"10:2"` 是无效的时间，正确的写法应该是 `"10:02"` 。

```go
import (
    "strings"
    "strconv"
)

func readBinaryWatch(turnedOn int) []string {
    path := make([]int, 10)
    res := make([]string, 0)
    curSize := 0  // 当前已经设置为 1 的 LED
    
    // 计算 hour
    var calculateHour func() int
    calculateHour = func() int {
        return 8*path[0] + 4*path[1] + 2*path[2] + 1*path[3]
    }
    // 计算 minute
    var calculateMinute func() int
    calculateMinute = func() int {
        return 32*path[4] + 16*path[5] + 8*path[6] + 4*path[7] + 2*path[8] + 1*path[9]
    }
    // 产生结果。此函数的执行的前提是 curSize == turnOn
    var generateRes func()
    generateRes = func() {
        hour := calculateHour()
        minute := calculateMinute()
        if hour > 11 || minute > 59 { return }
        var builder strings.Builder
        builder.WriteString(strconv.Itoa(hour))
        builder.WriteString(":")
        if minute < 10 { builder.WriteString("0") }
        builder.WriteString(strconv.Itoa(minute))
        res = append(res, builder.String())
    }

    var dfs func(begin int)
    dfs = func(begin int) {
        if curSize == turnedOn {
            generateRes()
            return
        }
        if begin >= 10 {
            return  // 防止越界
        }
        // 灯亮
        path[begin] = 1
        curSize++
        dfs(begin + 1)
        path[begin] = 0
        curSize--
        // 灯不亮
        dfs(begin + 1)
    }

    dfs(0)
    return res
}
```

对回溯进行优化之后：
```go
import (
    "fmt"
)

func readBinaryWatch(turnedOn int) []string {
    res := make([]string, 0)
    path := make([]int, 10)

    var backtrack func(begin int, turnedOnLeft int)
    backtrack = func(begin int, turnedOnLeft int) {
        if turnedOnLeft == 0 {
            hour := 8*path[0] + 4*path[1] + 2*path[2] + 1*path[3]
            minute := 32*path[4] + 16*path[5] + 8*path[6] + 4*path[7] + 2*path[8] + 1*path[9]
            if hour <= 11 && minute <= 59 {
                res = append(res, fmt.Sprintf("%d:%02d", hour, minute))
            }
            return
        }
        for i := begin; i < 10; i++ {
            path[i] = 1
            backtrack(i + 1, turnedOnLeft - 1)
            path[i] = 0
        }
    }

    // 从第 0 个位置开始，尝试点亮 turnedOn 个 LED
    backtrack(0, turnedOn)
    return res
}
```

其实为什么优化之后为什么代码量看起来少了很多呢？主要是将原本的那个 `strings.Builder` 给移除了，换成了 `fmt.Sprintf`。这就给我一个启示：是否之后在处理这种格式化的字符串的时候，并不是一定得借助于 `Builder`。如果最终的字符串的格式是很固定的，那么就可以使用 `Sprintf()` 进行字符串流的拼接。这种写法是更简洁的。

除此之外，这个题目还唤醒了我很久之前的 `backtrack` 部分的记忆。看起来 `backtrack` 主要就是这样的格式：

```go
func backtrack(begin) {
    if (满足终止条件) {
        计算结果
    }
    for (i := begin, i < maxLen; i++) {
        path[i] = 1
        backtrack(begin + 1)
        path[i] = 0
    }
}
```

## 133. 左叶子之和（404）

给定二叉树的根节点 `root` ，返回所有左叶子之和。

```go
func sumOfLeftLeaves(root *TreeNode) int {
    // flag 表示这个根节点是不是靠左边的节点
    var dfs func(root *TreeNode, flag bool) int
    dfs = func(root *TreeNode, flag bool) int {
        if root == nil {
            return 0
        }
        if root.Left == nil && root.Right == nil && flag {
            return root.Val
        }
        return dfs(root.Left, true) + dfs(root.Right, false)
    }

    return dfs(root, false)
}
```

## 134. 数字转换为十六进制数（405）

给定一个整数，编写一个算法将这个数转换为十六进制数。对于负整数，我们通常使用 [补码运算](https://baike.baidu.com/item/补码/6854613?fr=aladdin) 方法。

答案字符串中的所有字母都应该是小写字符，并且除了 0 本身之外，答案中不应该有任何前置零。

**注意:** 不允许使用任何由库提供的将数字直接转换或格式化为十六进制的方法来解决这个问题。

```go
import (
    "math"
)

func toHex(num int) string {
    if num < 0 {
        num += int(math.Pow(2, 32))
    } else if num == 0 {
        return "0"
    }

    var res []byte
    for num != 0 {
        remainder := byte(num % 16)
        if remainder < 10 {
            res = append(res, remainder + '0')
        } else {
            res = append(res, remainder - byte(10) + 'a')
        }
        num = num / 16
    }
    
    // 将 res 转置
    left := 0
    right := len(res) - 1
    for left < right {
        res[left], res[right] = res[right], res[left]
        left++
        right--
    }

    return string(res)
}
```

悟：处理负数的补码可以直接给负数加上 `2^32`！

## 135. Fizz Buzz（412）

给你一个整数 `n` ，找出从 `1` 到 `n` 各个整数的 Fizz Buzz 表示，并用字符串数组 `answer`（**下标从 1 开始**）返回结果，其中：

- `answer[i] == "FizzBuzz"` 如果 `i` 同时是 `3` 和 `5` 的倍数。
- `answer[i] == "Fizz"` 如果 `i` 是 `3` 的倍数。
- `answer[i] == "Buzz"` 如果 `i` 是 `5` 的倍数。
- `answer[i] == i` （以字符串形式）如果上述条件全不满足。

```go
import "strconv"

func fizzBuzz(n int) []string {
    res := make([]string, n + 1)

    for i := 1; i <= n; i++ {
        if i % 3 == 0 && i % 5 == 0 {
            res[i] = "FizzBuzz"
        } else if i % 3 == 0 {
            res[i] = "Fizz"
        } else if i % 5 == 0 {
            res[i] = "Buzz"
        } else {
            res[i] = strconv.Itoa(i)
        }
    }

    return res[1:]
}
```

## 136. 排列硬币（441）

你总共有 `n` 枚硬币，并计划将它们按阶梯状排列。对于一个由 `k` 行组成的阶梯，其第 `i` 行必须正好有 `i` 枚硬币。阶梯的最后一行 **可能** 是不完整的。

给你一个数字 `n` ，计算并返回可形成 **完整阶梯行** 的总行数。

```go
func arrangeCoins(n int) int {
    // 在 1 3 6 10 这样的序列中找到最后一个小于等于自己的
    // 序列就是 n(n+1)/2
    left := 1
    right := n
    for left <= right {
        mid := (left + right) / 2
        midSum := mid*(mid+1)/2
        if midSum > n {
            right = mid - 1
        } else if midSum <= n {
            left = mid + 1
        }
    }
    return right
}
```

## 137. 分发饼干（455）

假设你是一位很棒的家长，想要给你的孩子们一些小饼干。但是，每个孩子最多只能给一块饼干。

对每个孩子 `i`，都有一个胃口值 `g[i]`，这是能让孩子们满足胃口的饼干的最小尺寸；并且每块饼干 `j`，都有一个尺寸 `s[j]` 。如果 `s[j] >= g[i]`，我们可以将这个饼干 `j` 分配给孩子 `i` ，这个孩子会得到满足。你的目标是满足尽可能多的孩子，并输出这个最大数值。

```go
import "sort"

func findContentChildren(g []int, s []int) int {
    // 先让胃口小的孩子挑
    res := 0

    sort.Ints(g)
    sort.Ints(s)
    i := 0
    j := 0
    
    for i < len(g) && j < len(s) {
        if g[i] <= s[j] {
            res++
            i++
            j++
        } else {
            j++
        }
    }

    return res
}
```

## 138. 汉明距离（461）

两个整数之间的 [汉明距离](https://baike.baidu.com/item/汉明距离) 指的是这两个数字对应二进制位不同的位置的数目。

给你两个整数 `x` 和 `y`，计算并返回它们之间的汉明距离。

```go
func hammingDistance(x int, y int) int {
    res := 0

    num := x ^ y
    for num != 0 {
        res += num & 1
        num = num >> 1
    }

    return res
}
```

## 139. 数字的补数（476）

对整数的二进制表示取反（`0` 变 `1` ，`1` 变 `0`）后，再转换为十进制表示，可以得到这个整数的补数。

- 例如，整数 `5` 的二进制表示是 `"101"` ，取反后得到 `"010"` ，再转回十进制表示得到补数 `2` 。

给你一个整数 `num` ，输出它的补数。

```go
func findComplement(num int) int {
    // 先找到第一个大于等于它的序列数
    // 也就是 1、3、7、15
    upper := 1
    for num > upper {
        upper = ((upper + 1) << 1) - 1
    }
    return upper - num
}
```

## 140. 密钥格式化（482）

给定一个许可密钥字符串 `s`，仅由字母、数字字符和破折号组成。字符串由 `n` 个破折号分成 `n + 1` 组。你也会得到一个整数 `k` 。

我们想要重新格式化字符串 `s`，使每一组包含 `k` 个字符，除了第一组，它可以比 `k` 短，但仍然必须包含至少一个字符。此外，两组之间必须插入破折号，并且应该将所有小写字母转换为大写字母。

返回 *重新格式化的许可密钥* 。

```go
import "strings"

func licenseKeyFormatting(s string, k int) string {
    // 从后往前
    var builder strings.Builder
    count := 0  // 计数：已经加了多少个字母、数字
    for i := len(s) - 1; i >= 0; i-- {
        if s[i] == '-' {
            continue
        } else {
            if s[i] >= 'a' && s[i] <= 'z' {
                builder.WriteByte(s[i] - byte(32))
            } else {
                builder.WriteByte(s[i])
            }
        }
        count++
        if count != 0 && count % k == 0 {
            builder.WriteByte('-')
        }
    }
    
    bytes := []byte(builder.String())
    if len(bytes) != 0 && bytes[len(bytes) - 1] == '-' {
        bytes = bytes[:len(bytes) - 1]
    }
    left := 0
    right := len(bytes) - 1
    for left < right {
        bytes[left], bytes[right] = bytes[right], bytes[left]
        left++
        right--
    }

    return string(bytes)
}
```

做完这个题，学到的新的知识点：

- `builder` 一旦构建之后，是不可以从中再删除元素的。如果要删除元素，只能是先转换成 `string`，`string` 再转 `[]byte` 或者 `[]rune`，然后再继续进行转换。
- `builder` 里面除了有 `WriteString` 方法，还有 `WriteRune` 和 `WriteByte` 方法。但是没有 `WriteInt` 之类的方法。

## 141. 构造矩形（492）

作为一位web开发者， 懂得怎样去规划一个页面的尺寸是很重要的。 所以，现给定一个具体的矩形页面面积，你的任务是设计一个长度为 L 和宽度为 W 且满足以下要求的矩形的页面。要求：

1. 你设计的矩形页面必须等于给定的目标面积。
2. 宽度 `W` 不应大于长度 `L` ，换言之，要求 `L >= W `。
3. 长度 `L` 和宽度 `W` 之间的差距应当尽可能小。

返回一个 *数组* `[L, W]`，其中 *`L` 和 `W` 是你按照顺序设计的网页的长度和宽度*。

```go
import "math"

func constructRectangle(area int) []int {
    sqrt := int(math.Sqrt(float64(area)))
    res := make([]int, 2)
    
    for width := 1; width <= sqrt; width++ {
        if area % width == 0 {
            res = []int{area / width, width}
        }
    }

    return res
}
```

## 142. 提莫攻击（495）

在《英雄联盟》的世界中，有一个叫 “提莫” 的英雄。他的攻击可以让敌方英雄艾希（编者注：寒冰射手）进入中毒状态。

当提莫攻击艾希，艾希的中毒状态正好持续 `duration` 秒。

正式地讲，提莫在 `t` 发起攻击意味着艾希在时间区间 `[t, t + duration - 1]`（含 `t` 和 `t + duration - 1`）处于中毒状态。如果提莫在中毒影响结束 **前** 再次攻击，中毒状态计时器将会 **重置** ，在新的攻击之后，中毒影响将会在 `duration` 秒后结束。

给你一个 **非递减** 的整数数组 `timeSeries` ，其中 `timeSeries[i]` 表示提莫在 `timeSeries[i]` 秒时对艾希发起攻击，以及一个表示中毒持续时间的整数 `duration` 。

返回艾希处于中毒状态的 **总** 秒数。

```go
func findPoisonedDuration(timeSeries []int, duration int) int {
    lastEnd := 0
    res := 0
    for _, begin := range timeSeries {
        end := begin + duration
        begin = max(begin, lastEnd)
        res += end - begin
        lastEnd = end
    }
    return res
}
```

## 143. 键盘行（500）

给你一个字符串数组 `words` ，只返回可以使用在 **美式键盘** 同一行的字母打印出来的单词。键盘如下图所示。

**请注意**，字符串 **不区分大小写**，相同字母的大小写形式都被视为在同一行**。**

**美式键盘** 中：

- 第一行由字符 `"qwertyuiop"` 组成。
- 第二行由字符 `"asdfghjkl"` 组成。
- 第三行由字符 `"zxcvbnm"` 组成。

![American keyboard](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/keyboard.png)

```go
func findWords(words []string) []string {
	line1 := "qwertyuiop"
	line2 := "asdfghjkl"
	line3 := "zxcvbnm"

	var lowercase func(b byte) byte
	lowercase = func(b byte) byte {
		if b >= 'A' && b <= 'Z' {
			return b + byte(32)
		}
		return b
	}

	var contains func(b byte) int
	contains = func(b byte) int {
		for i := 0; i < 10; i++ {
			if b == line1[i] {
				return 1
			}
		}
		for i := 0; i < 9; i++ {
			if b == line2[i] {
				return 2
			}
		}
		for i := 0; i < 7; i++ {
			if b == line3[i] {
				return 3
			}
		}
		return -1
	}

	var res []string

outer:
	for _, word := range words {
		first := contains(lowercase(word[0]))
		for _, c := range word {
			if contains(lowercase(byte(c))) != first {
                continue outer
			}
		}
        res = append(res, word)
	}

	return res
}
```

题目不难，就是麻烦。

感觉自己后期的代码写得挺答辩的。主要是字符串处理这块儿。之后可以给自己加一个规范，比如说处理字符串的时候，之后就不要用 byte 了，字符都用 rune 来遍历。

另一个是，go 是强类型语言，如果函数的参数类型是 byte，传入的时候就不能用 rune；如果参数设置的是 rune，传入的时候就不能用 byte。包括 math 包里面的 `Sqrt()` 之类的函数也是一样的，float64 和 int 分得比较开，比 C++ 的类型要强。所以为了规范，之后遍历字符串的时候就都用 rune 来操作了。











待做题目：
504
506
507
521
530
551
557
559
563
566
572
575
589
590
594
598
599
617
637
653
657
661
671
680
682
693
696
700







