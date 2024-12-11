# Go 刷题

看了一些 Go 语言的语法，但是又感觉比较无聊。因为已经有很多语言的基础了，不想再去打那些简单的代码了。

所以，还是决定回归老本行，通过刷 Leetcode 的方式，来提升自己对 Go 语言的熟悉程度。

[TOC]

## 1. 两数之和（1）

给定一个整数数组 `nums` 和一个整数目标值 `target`，请你在该数组中找出 **和为目标值** *`target`* 的那 **两个** 整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。

你可以按任意顺序返回答案。

暴力枚举解法：

```go
func twoSum(nums []int, target int) []int {
	for i, x := range nums {
		for j := i + 1; j < len(nums); j++ {
			if x + nums[j] == target {
				return [] int {i, j}
			}
		}
	}
	return nil
}
```

代码解释：

1. `for i, x := range nums` 表示对一个数组进行遍历，其中 `i` 表示当前的下标，`x` 表示当前遍历到的值。
2. go 语言中如果要对一个数组求长度，那就是直接加上 `len()`，比如说 `len(nums)`
3. go 语言中如果要返回一个包含几个元素的数组，那就是 `return []int{num1, num2, ....}` 这样的形式。
4. go 语言中表示数据类型：
    - `int`：`int` 类型的元素
    - `*int`：`int` 类型的指针
    - `[]int`：`int` 类型的数组

哈希表解法：

```go
func twoSum(nums []int, target int) []int {
    hashTable := map[int]int{}
    for i, x := range nums {
        if p, ok := hashTable[target-x]; ok {
            return []int{p, i}
        }
        hashTable[x] = i
    }
    return nil
}
```

代码解释：

1. 首先是 go 语言中构建哈希表的语句：`hashTable := map[int]int{}`。其中第一个 `int` 表示 key 的类型是 `int`，第二个 `int` 表示 value 的类型是 `int`。最后的 `{}` 里面是空的，这表示我们构建的哈希表一开始是空的。
2. `if p, ok := hashTable[target - x]; ok {...}`
    - 在 go 语言中，`hashTable[target - x]` 表示从哈希表中查询 key 为 `target - x` 的值。Go 语言允许通过两种方式从哈希表中查询值：
        - 只获取值：`value := hashTable[target - x]`
        - 获取值并检查键是否存在：`value, ok := hashTable[key]`
    - 其中的 `ok` 是一个布尔类型的值，它表示哈希表中是否存在这个键。如果键存在，则 `ok` 为 `true`，并且 `value` 是与该 key 相关联的值。如果 key 不存在，则 `ok`  为 `false`，而 `value` 为该类型的零值。
    - 因此，`p, ok := hashTable[target - x]` 中，`p` 是哈希表中键 `target - x` 对应的值，`ok` 是一个布尔值，用来检查键 `target - x` 是否存在。
3. `if` 语句中分号的作用：go 语言允许在 `if` 语句中进行一个简单的赋值语句，并用分号隔开，接着再判断条件。这种写法很常见，尤其是在需要同时赋值和判断的场景下。
4. go 语言中的 `nil` 表示空指针。

## 2. 合并两个有序数组（88）

给你两个按 **非递减顺序** 排列的整数数组 `nums1` 和 `nums2`，另有两个整数 `m` 和 `n` ，分别表示 `nums1` 和 `nums2` 中的元素数目。

请你 **合并** `nums2` 到 `nums1` 中，使合并后的数组同样按 **非递减顺序** 排列。

**注意：**最终，合并后数组不应由函数返回，而是存储在数组 `nums1` 中。为了应对这种情况，`nums1` 的初始长度为 `m + n`，其中前 `m` 个元素表示应合并的元素，后 `n` 个元素为 `0` ，应忽略。`nums2` 的长度为 `n` 。

```go
func merge(nums1 []int, m int, nums2 []int, n int) {
    copy(nums1[m:], nums2)
    sort.Ints(nums1)
}
```

代码解释：

- `copy(nums1[m:], nums2)`：将 `nums2` 中的值全部复制到 `nums1` 从 `m` 开始往后的位置。
    - 这个题目中，是已经将 `nums1` 的容量设置为 `m + n` 了，才可以这样操作。否则就要先扩充 `nums1` 的容量，才能继续后面的 `copy` 操作。
- go 语言中调用系统排序库的方法：`sort.Ints(nums)`。

## 3. 爬楼梯（70）

假设你正在爬楼梯。需要 `n` 阶你才能到达楼顶。

每次你可以爬 `1` 或 `2` 个台阶。你有多少种不同的方法可以爬到楼顶呢？

```go
func climbStairs(n int) int {
	if n <= 2 {
		return n
	}
	prepre := 1 // 上上次计算的结果
	pre := 2    // 上次计算的结果
	for i := 3; i <= n; i++ {
		prepre, pre = pre, prepre+pre
	}
	return pre
}
```

实际上就是一个斐波那契数列的知识，但是其中用到了 Go 的一个语法，就是元组赋值还是什么东西的。哦！原来叫作多重赋值。

在代码中的体现就是：

```go
prepre, pre = pre, prepre + pre
```

这样有一个并行赋值的意思。实际上在 go 中也有类似的语法，比如说：

```go
num1, num2 = num2, num1
```

这样就是一个很简洁的交换元素的写法。

## 4. 有效的括号（20）

给定一个只包括 `'('`，`')'`，`'{'`，`'}'`，`'['`，`']'` 的字符串 `s` ，判断字符串是否有效。

有效字符串需满足：

1. 左括号必须用相同类型的右括号闭合。
2. 左括号必须以正确的顺序闭合。
3. 每个右括号都有一个对应的相同类型的左括号。

```go
func isValid(s string) bool {
    var stack []rune
    bracketMap := map[rune]rune{
        ')': '(',
        ']': '[',
        '}': '{',
    }

    for _, c := range s {
        if value, ok := bracketMap[c]; ok {
            // c 是右括号，value 是左括号
            if len(stack) == 0 || stack[len(stack)-1] != value {
                return false
            }
            stack = stack[:len(stack)-1]
        } else {
            // c 是左括号
            stack = append(stack, c)
        }
    }
    return len(stack) == 0
}
```

从这个题目中主要学到了 go 语言中栈的写法。Go 语言中没有其他编程语言直接现成的 stack 供使用，只能通过切片来进行模拟。

- 栈的建立：`var stack []int`
- 取栈顶元素：`stack[len(stack) - 1]`
- 压栈：`stack = append(stack, value)`
- 判断栈空：`if len(stack) == 0`

还有就是映射 map 的建立：`bracketMap := map[rune]rune {...}`。

如果是建立一个数字对应字符的 map：`mp := map[int]rune`。

除此之外，还有判断一个元素是不是在 map 中的时候：

```go
if _, ok := mp[key]; ok {
    ...
}
```

我们是要从这里开始想的，即使是我们的目的是查询一个 hashmap，我们也是要从一个 hashset 开始思考的。思考的过程大概就是这个代码的样子。

先写完这里之后，想起来，欸，我需要的是一个 hashmap，这时候就把 `_` 的地方换一下就行了：

```go
if value, ok := mp[key]; ok {
    ...
}

// 实际上和这种写法是等价的：
// 但是肯定推荐第一种，因为第一种里面我们只需要对 mp 进行一次查询
if _, ok := mp[key]; ok {
    value, _ := mp[key]
}
```

这样就可以取出 `mp[key]` 的值。

## 5. 最长公共前缀（14）

编写一个函数来查找字符串数组中的最长公共前缀。

如果不存在公共前缀，返回空字符串 `""`。

```go
func longestCommonPrefix(strs []string) string {
    prefix := strs[0]

    for i := 1; i < len(strs); i++ {
        for len(prefix) > 0 && !strings.HasPrefix(strs[i], prefix) {
            prefix = prefix[:len(prefix) - 1]
        }     
    }

    return prefix
}
```

Go 语言里面，如果要判断前缀，可以直接使用 strings 包里面的函数：HasPrefix。

## 6. 买卖股票的最佳时机（121）

给定一个数组 `prices` ，它的第 `i` 个元素 `prices[i]` 表示一支给定股票第 `i` 天的价格。

你只能选择 **某一天** 买入这只股票，并选择在 **未来的某一个不同的日子** 卖出该股票。设计一个算法来计算你所能获取的最大利润。

返回你可以从这笔交易中获取的最大利润。如果你不能获取任何利润，返回 `0` 。

 ```go
 func maxProfit(prices []int) int {
     preMin := prices[0]
     res := 0
 
     for i := 1; i < len(prices); i++ {
         res = max(res, prices[i] - preMin)
         preMin = min(preMin, prices[i])
     }
 
     return res
 }
 ```

在 go 语言中，如果要判断最大值和最小值，直接使用 max、min 函数即可。

## 7. 合并两个有序链表（21）

将两个升序链表合并为一个新的 **升序** 链表并返回。新链表是通过拼接给定的两个链表的所有节点组成的。 

```go
func mergeTwoLists(list1 *ListNode, list2 *ListNode) *ListNode {
    res := &ListNode{}
    tail := res

    for list1 != nil || list2 != nil {
        if list1 == nil {
            tail.Next = list2
            break
        } else if list2 == nil {
            tail.Next = list1
            break
        }
        if list1.Val < list2.Val {
            tail.Next = list1
            tail = list1
            list1 = list1.Next
        } else {
            tail.Next = list2
            tail = list2
            list2 = list2.Next
        }
    }

    return res.Next
}
```

Go 语言中对链表节点的定义是：

```go
type ListNode struct {
    Val int
    Next *ListNode
}
```

那么之后在建立节点的之后，有以下几种方法：

- 建立一个空节点：`node := &ListNode{}`
- 建立一个值为 10 的节点：`node := &ListNode{Val: 10}`
- 建立一个值为 10，Next 为 nil 的节点：`node := &ListNode{Val: 10, Next: nil}`

## 8. 反转链表（206）

给你单链表的头节点 `head` ，请你反转链表，并返回反转后的链表。

```go
func reverseList(head *ListNode) *ListNode {
    var pre *ListNode
    for head != nil {
        next := head.Next
        head.Next = pre
        pre = head
        head = next
    }
    return pre
}
```

遇到一个问题是，假如说我们现在要声明一个空值类型的指针，如果直接使用：`pre := nil` 这样是不行的。因为这样并不知道你声明的是一个什么类型的指针。

这时候我们应该这样做：`var pre *ListNode` 或者是 `var pre *ListNode = nil`。这样才可以建立一个空的指针变量。

## 9. 两整数相加（2235）

给你两个整数 `num1` 和 `num2`，返回这两个整数的和。

代码：

```go
func sum(num1 int, num2 int) int {
    return num1 + num2
}
```

没什么好说的。

## 10. 二分查找（704）

给定一个 `n` 个元素有序的（升序）整型数组 `nums` 和一个目标值 `target` ，写一个函数搜索 `nums` 中的 `target`，如果目标值存在返回下标，否则返回 `-1`。

```go
func search(nums []int, target int) int {
    left := 0
    right := len(nums) - 1
    for left <= right {
        mid := left + (right - left) / 2
        if target > nums[mid] {
            left = mid + 1
        } else  if target < nums[mid] {
            right = mid - 1
        } else {
            return mid
        }
    }
    return -1
}
```

## 11. 移除元素（27）

给你一个数组 `nums` 和一个值 `val`，你需要 **[原地](https://baike.baidu.com/item/原地算法)** 移除所有数值等于 `val` 的元素。元素的顺序可能发生改变。然后返回 `nums` 中与 `val` 不同的元素的数量。

假设 `nums` 中不等于 `val` 的元素数量为 `k`，要通过此题，您需要执行以下操作：

- 更改 `nums` 数组，使 `nums` 的前 `k` 个元素包含不等于 `val` 的元素。`nums` 的其余元素和 `nums` 的大小并不重要。
- 返回 `k`。

```go
func removeElement(nums []int, val int) int {
    // 使用双指针
    left := 0
    right := 0
    for right < len(nums) {
        if nums[right] != val {
            nums[left] = nums[right]
            left++
        }
        right++
    }
    return left
}
```

## 12. 删除有序数组中的重复项（26）

给你一个 **非严格递增排列** 的数组 `nums` ，请你**[ 原地](http://baike.baidu.com/item/原地算法)** 删除重复出现的元素，使每个元素 **只出现一次** ，返回删除后数组的新长度。元素的 **相对顺序** 应该保持 **一致** 。然后返回 `nums` 中唯一元素的个数。

考虑 `nums` 的唯一元素的数量为 `k` ，你需要做以下事情确保你的题解可以被通过：

- 更改数组 `nums` ，使 `nums` 的前 `k` 个元素包含唯一元素，并按照它们最初在 `nums` 中出现的顺序排列。`nums` 的其余元素与 `nums` 的大小不重要。
- 返回 `k` 。

```go
func removeDuplicates(nums []int) int {
    left := 1
    right := 1
    for right < len(nums) {
        if nums[right] != nums[right - 1] {
            nums[left] = nums[right]
            left += 1
        }
        right += 1
    }
    return left
}
```

## 13. 回文数（9）

给你一个整数 `x` ，如果 `x` 是一个回文整数，返回 `true` ；否则，返回 `false` 。

回文数是指正序（从左向右）和倒序（从右向左）读都是一样的整数。

- 例如，`121` 是回文，而 `123` 不是。

 经典写法：

```go
func isPalindrome(x int) bool {
    if (x < 0) {
        return false
    }
    nums := []int{}
    for x != 0 {
        nums = append(nums, x % 10)
        x /= 10
    }
    // 判断 nums 是不是对称的
    left := 0
    right := len(nums) - 1
    for left < right {
        if nums[left] != nums[right] {
            return false
        }
        left++
        right--
    }
    return true
}
```

这种写法将 num 的每一位的值都存进数组里面，这样的好处是简单、好想，但是存在空间复杂度。空间复杂度是和数字的位数正相关的。虽然也不是很大，但是可以优化。

进阶写法：

```go
func isPalindrome(x int) bool {
    // 将后一半进行反转
    if (x < 0 || x % 10 == 0 && x != 0) {
        return false
    }
    
    reverse := 0
    for (x > reverse) {
        reverse = reverse * 10 + x % 10
        x /= 10 
    }
    return x == reverse || x == reverse / 10
}
```

这种算法是将数字的后半部分进行翻转，这样做就消除了时间复杂度。

最后的 return 是考虑了两种情况：原本的 num 的位数是偶数或者奇数。

## 14. 多数元素（169）

给定一个大小为 `n` 的数组 `nums` ，返回其中的多数元素。多数元素是指在数组中出现次数 **大于** `⌊ n/2 ⌋` 的元素。

你可以假设数组是非空的，并且给定的数组总是存在多数元素。

常规解法：

```go
func majorityElement(nums []int) int {
    counts := map[int]int{}
    for _, num := range(nums) {
        counts[num] += 1
    }
    maxCount := 0
    maxNum := nums[0]
    for num, count := range(counts) {
        // num 是数字
        // count 是出现的次数
        if count > maxCount {
            maxCount = count
            maxNum = num
        }
    }
    return maxNum
}
```

这种就是通过一个哈希表来记录出现的数字和这个数字出现的次数。最后通过遍历一边哈希表，得出出现次数最多的 num 和 count 就是答案。

这个题目还有一个更巧妙的算法：摩尔投票。

```go
func majorityElement(nums []int) int {
    candidate := 0  // x 是我们目前假定的数组中的众数
    count := 0
    for _, num := range(nums) {
        if count == 0 {
            candidate = num
        }
        if num == candidate {
            count++
        } else {
            count--
        }
    }
    return candidate
}
```

就是我们先假定数组中出现最多的元素就是 candidate。之后遇到 candidate，count 就加一，否则 count 减一。这样如果某一时刻我们发现 count 是 0 了，说明有很多的 candidate 和非 candidate 撞上了，导致结果归零了。

这时候有两种情况：

- candidate 就是最后的数值。这时候说明我们消去了同等数量的 candidate 和 else。但是根据我们数值的特性，剩下的数组中，res 的数量仍然是最多的。
- candidate 不是最后的数值。相当于所有的 else 在“黑吃黑”。这种更好，剩下的数组中，我们的 res 肯定也是数量最多的。

无论如何，遍历一次数组之后，最后 candidate 中存的数字就是我们的结果。

## 15. 移动零（283）

给定一个数组 `nums`，编写一个函数将所有 `0` 移动到数组的末尾，同时保持非零元素的相对顺序。

**请注意** ，必须在不复制数组的情况下原地对数组进行操作。

```go
func moveZeroes(nums []int)  {
    // 使用双指针
    left := 0
    right := 0
    for right < len(nums) {
        if nums[right] != 0 {
            nums[left] = nums[right]
            left++
        }
        right++
    }
    for left < right {
        nums[left] = 0
        left++
    }
}
```

## 16. 搜索插入位置（35）

给定一个排序数组和一个目标值，在数组中找到目标值，并返回其索引。如果目标值不存在于数组中，返回它将会被按顺序插入的位置。

请必须使用时间复杂度为 `O(log n)` 的算法。

```go
func searchInsert(nums []int, target int) int {
    // 二分查找
    // 如果没有搜索到，就返回比 target 小的最大的值
    left := 0
    right := len(nums) - 1
    for left <= right {
        mid := left + (right - left) / 2
        if target > nums[mid] {
            left = mid + 1
        } else if target < nums[mid] {
            right = mid - 1
        } else {
            return mid
        }
    }
    return left
}
```

## 17. 找出字符串中第一个匹配项的下标（28）

给你两个字符串 `haystack` 和 `needle` ，请你在 `haystack` 字符串中找出 `needle` 字符串的第一个匹配项的下标（下标从 0 开始）。如果 `needle` 不是 `haystack` 的一部分，则返回 `-1` 。

```go
func strStr(haystack string, needle string) int {
    return strings.Index(haystack, needle)
}
```

kmp 算法！再做一次，我还是选择了调库。

列出一些 strings 包中常用的 API：

- `strings.Contains(s, substr string) bool`：判断 substr 在不在 s 中。
- `strings.HasPrefix(s, prefix string) bool`：判断 s 是不是以 prefix 开头。
- `strings.HasSuffix(s, suffix string) bool`：判断 s 是不是以 suffix 结尾。
- `strings.Index(s, substr string) int`：查找 substr 在 s 中的位置，如果找不到，返回 -1。

## 18. 环形链表（141）

给你一个链表的头节点 `head` ，判断链表中是否有环。

如果链表中有某个节点，可以通过连续跟踪 `next` 指针再次到达，则链表中存在环。 为了表示给定链表中的环，评测系统内部使用整数 `pos` 来表示链表尾连接到链表中的位置（索引从 0 开始）。**注意：`pos` 不作为参数进行传递** 。仅仅是为了标识链表的实际情况。

*如果链表中存在环* ，则返回 `true` 。 否则，返回 `false` 。

```go
func hasCycle(head *ListNode) bool {
    // 定义快慢指针
    slow := head
    fast := head
    for fast != nil && fast.Next != nil {
        fast = fast.Next.Next
        slow = slow.Next
        if fast == slow {
            return true
        }
    }
    return false
}
```

## 19. 相交链表（160）

给你两个单链表的头节点 `headA` 和 `headB` ，请你找出并返回两个单链表相交的起始节点。如果两个链表不存在相交节点，返回 `null` 。

图示两个链表在节点 `c1` 开始相交**：**

![img](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/160_statement.png)

题目数据 **保证** 整个链式结构中不存在环。

**注意**，函数返回结果后，链表必须 **保持其原始结构** 。

```go
func getIntersectionNode(headA, headB *ListNode) *ListNode {
    if headA == nil || headB == nil {
        return nil
    }
    nodeA := headA
    nodeB := headB
    for nodeA != nodeB {
        if nodeA == nil {
            nodeA = headB
        } else {
            nodeA = nodeA.Next
        }
        
        if nodeB == nil {
            nodeB = headA
        } else {
            nodeB = nodeB.Next
        }
    }
    return nodeA
}
```

这个代码是让 AI 给我修改了之后的，我原本的代码的思路和这个差不多，但是我的代码的逻辑更生硬，属于是完全硬搬着把自己的想法写出来，但是 AI 这个代码就比较简洁。

实际上，nodeA 确实只有两种可能的变化，要么变为 nodeA 的下一个，要么变为 headB。

nodeB 也是只有两种可能的变化，要么变为 nodeB 的 Next，要么变为 headA。

把这些逻辑都写到一起就是答案。最后才发现代码描述起来原来这么简洁。

## 20. 只出现一次的数字（136）

给你一个 **非空** 整数数组 `nums` ，除了某个元素只出现一次以外，其余每个元素均出现两次。找出那个只出现了一次的元素。

你必须设计并实现线性时间复杂度的算法来解决此问题，且该算法只使用常量额外空间。

 ```go
 func singleNumber(nums []int) int {
     res := 0
     for _, num := range nums {
         res = res ^ num
     }
     return res
 }
 ```

之前做过好几次的问题，通过异或操作，得出整个数组中只出现一次的数字。

## 21. x 的平方根（69）

给你一个非负整数 `x` ，计算并返回 `x` 的 **算术平方根** 。

由于返回类型是整数，结果只保留 **整数部分** ，小数部分将被 **舍去 。**

**注意：**不允许使用任何内置指数函数和算符，例如 `pow(x, 0.5)` 或者 `x ** 0.5` 。

 ```go
 func mySqrt(x int) int {
     // 使用二分查找来解决
     left := 0
     right := x
     for left <= right {
         mid := left + (right - left) / 2
         mid2 := mid * mid
         if x > mid2 {
             left = mid + 1
         } else if x < mid2 {
             right = mid - 1
         } else {
             return mid
         }
     }
     return right
 }
 ```

这个其实也是一种二分查找的题目。这个题目的模型其实是要查找：小于等于 x 的数字中的最大值。

为什么返回 right 呢？

我后来想到，如果上面的循环可以退出，那么退出的时候一定是 left 在右边，right 在左边的。那么 x 真正应该对应的值呢，实际上这时候应该是在 [right, left] 中间这里放着。

这时候我们要返回的是比 x 小的最大值，所以就是 right。

之前有的时候是求比 x 大的最小值的，这时候就要返回 left 才对。

## 22. 罗马数字转整数（13）

罗马数字包含以下七种字符: `I`， `V`， `X`， `L`，`C`，`D` 和 `M`。

```go
字符          数值
I             1
V             5
X             10
L             50
C             100
D             500
M             1000
```

例如， 罗马数字 `2` 写做 `II` ，即为两个并列的 1 。`12` 写做 `XII` ，即为 `X` + `II` 。 `27` 写做 `XXVII`, 即为 `XX` + `V` + `II` 。

通常情况下，罗马数字中小的数字在大的数字的右边。但也存在特例，例如 4 不写做 `IIII`，而是 `IV`。数字 1 在数字 5 的左边，所表示的数等于大数 5 减小数 1 得到的数值 4 。同样地，数字 9 表示为 `IX`。这个特殊的规则只适用于以下六种情况：

- `I` 可以放在 `V` (5) 和 `X` (10) 的左边，来表示 4 和 9。
- `X` 可以放在 `L` (50) 和 `C` (100) 的左边，来表示 40 和 90。 
- `C` 可以放在 `D` (500) 和 `M` (1000) 的左边，来表示 400 和 900。

给定一个罗马数字，将其转换成整数。

```go
func romanToInt(s string) int {
    romanIntMap := map[rune]int {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000,
    }

    res := 0
    pre := romanIntMap[rune(s[0])]
    for i := 1; i < len(s); i++ {
        cur := romanIntMap[rune(s[i])]
        if pre < cur {
            res -= pre
        } else {
            res += pre
        }
        pre = cur
    }
    res += pre

    return res
}
```

原本最后一步我写的是：`res += romanIntMap[rune(s[len(s) - 1])`，然后我让 AI 看了看我的代码，它竟然能直接发现我最后这个计算是多余的，因为这个值已经算出来并且保存到 pre 中了。

第一次写的时候，我尝试使用 `romanIntMap[s[i]]` 这种写法，但是报错了。后来一查，才知道，go 语言中对 byte 类型和 rune 类型区分的还是比较严格的。byte 是一个字节，而 rune 是一个 Unicode 码点，其实就是一个 Unicode 字符。一个字母是一个 Unicode 字符，一个汉字也是一个 Unicode 字符。

而 go 中的 string 类型是用 byte 类型来存储其中的每一个值的。于是我创建了一个键值为 rune 的 map，然后传入的时候却使用的是 byte 类型，这样就不对了，会导致一个传入类型不匹配的错误。这时候就要使用 `rune()` 函数进行一个强制转换。

除此之外，其实也有第二种解决方法：在定义 map 的时候，直接将 map 的键值定义为 byte 类型。这样之后在进行键值传入的时候，直接写 `romanIntMap[s[i]]` 也是可以的。因为这样就是 byte 对 byte，其中不会有 rune 的事儿。但是这样也会带来一个问题，那就是要确保 map 中的每一个键值都是 ASCII 字符（可以用一个字节来描述的）。如果 map 中我们定义了某一个汉字的键值对，这样就不行了。

另外，虽然字符串是以 byte 进行存储的，但是如果我们需要使用 rune 类型的元素，也可以通过 range 来访问字符串中的元素。总结如下：

```go
s := "hello, 世界"

// 按 byte 处理
for i := 0; i < len(s); i++ {
    fmt.Printf("byte: %c\n", s[i])
}

// 按 rune 处理
for _, char := range s {
    fmt.Printf("rune: %c\n", char)
}
```

## 23. 杨辉三角（118）

给定一个非负整数 *`numRows`，*生成「杨辉三角」的前 *`numRows`* 行。

在「杨辉三角」中，每个数是它左上方和右上方的数的和。

![img](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/1626927345-DZmfxB-PascalTriangleAnimated2.gif)

```go
func generate(numRows int) [][]int {
    res := [][]int{}
    
    for i := 0; i < numRows; i++ {
        // 每一行有 i + 1 个元素
        arr := make([]int, i + 1)
        arr[0] = 1
        arr[i] = 1
        for j := 1; j < i; j++ {
            arr[j] = res[i - 1][j - 1] + res[i - 1][j]
        }
        res = append(res, arr)
    }

    return res
}
```

做这个题目的时候，突然感觉想不起来之前数组切片的创建方式了。然后去查了一下才回忆起来。

如果想要创建一个长度为 i 的切片，可以使用 make 函数：`arr := make([]int, i)`。

但是 go 语言中，如果想要创建一个二维的 m 行 n 列的切片，并不像 C++ 中那么方便，还需要做一些额外的操作：

```go
// 比如说我们想要创建一个 m 行 n 列的切片
m, n := 3, 4  // 3 行 4 列
res := make([][]int, m)  // 创建一个长度为 m 的切片，此时其中每个元素都是 nil 切片

for i := 0; i < m; i++ {
    res[i] := make([]int, n)  // 给每一行分配长度为 n 的切片
}
```

## 24. 二叉树的最大深度（104）

给定一个二叉树 `root` ，返回其最大深度。

二叉树的 **最大深度** 是指从根节点到最远叶子节点的最长路径上的节点数。

```go
func maxDepth(root *TreeNode) int {
    if root == nil {
        return 0
    }
    leftDepth := maxDepth(root.Left)
    rightDepth := maxDepth(root.Right)
    return max(leftDepth, rightDepth) + 1
}
```

## 25. 验证回文串（125）

如果在将所有大写字符转换为小写字符、并移除所有非字母数字字符之后，短语正着读和反着读都一样。则可以认为该短语是一个 **回文串** 。

字母和数字都属于字母数字字符。

给你一个字符串 `s`，如果它是 **回文串** ，返回 `true` ；否则，返回 `false` 。

```go
import (
	"strings"
	"unicode"
)
func isPalindrome(str string) bool {
    runes := make([]rune, 0)
    str = strings.ToLower(str)
    for _, c := range str {
        if unicode.IsDigit(c) || unicode.IsLetter(c) {
            runes = append(runes, c)
        }
    }
    left := 0
    right := len(runes) - 1
    for left < right {
        if runes[left] != runes[right] {
            return false
        }
        left++
        right--
    }

    return true
}
```

一开始做的时候是遇到了一些问题的。第一次我尝试创建一个 s1 字符串，之后每次找到合适的字符之后，就将这个字符使用一个 `append(s1, c)` 的操作加入进 s1 里面。

但是后来就失败了，因为 go 语言中的字符串是不能进行修改的。`append()` 函数只能用于切片的操作。查了一下，Go 语言中，如果想要修改一个字符串，一般的我们选择的做法是：将字符串转换为切片，然后对切片就可以做：取值修改、加入元素之类的操作。

除此之外，Go 语言中也有比较方便的判断数字和字母的方式，主要使用了 unicode 包中的东西：

- `unicode.IsDigit(rune)`：可以判断一个 rune 类型的字符是不是数字。
- `unicode.IsLetter(rune)`：可以判断一个 rune 类型的字符是不是字母。

## 26. 快乐数（202）

编写一个算法来判断一个数 `n` 是不是快乐数。

**「快乐数」** 定义为：

- 对于一个正整数，每一次将该数替换为它每个位置上的数字的平方和。
- 然后重复这个过程直到这个数变为 1，也可能是 **无限循环** 但始终变不到 1。
- 如果这个过程 **结果为** 1，那么这个数就是快乐数。

如果 `n` 是 *快乐数* 就返回 `true` ；不是，则返回 `false` 。

```go
func isHappy(n int) bool {
    happySet := make(map[int]bool)  // 存放所有已经过出现的数的集合
    for n != 1 {
        if happyMap[n] {
            return false
        }
        happyMap[n] = true
        num := 0  // 即将作为新的 n
        for n != 0 {
            digit := n % 10  // n 的最后一位数
            num += digit * digit
            n /= 10
        }
        n = num
    }
    return true
}
```

一开始我陷入了一个误区：因为之前查询 map 的方式比较单一，所以我一直以为 go 中不好实现 HashSet，只能用 HashMap 来代替。但是这里让我有了一些新的认识。

我们知道 go 中没有提供 set 的类型，只提供了 map 的类型。而在建立一个 map 的时候，需要指定 map 的 key 和 value 的类型。key 的类型好说，不过是 value 的类型这方面，就很容易让人犯难。实际上这里的 value 是“取什么都行”，但是如果能有一个确定的取值，那一定是比不确定要更好的。

所以 go 中就可以这样做：在建立一个 set 的时候，就让 value 的类型为：bool。所有在集合中的元素，value 的类型都是 true。不在集合中的元素，就不在集合中。也就是说，只要是在 map 中的元素，它们的 value 都是为 true 的。

这样做有什么好处呢？看下面的代码：
```go
if happySet[n] {
    // ...
}
```

这个语句很简单，它的功能是：判断 n 在不在 map 中。如果 n 在 map 中，就执行框框里面的语句。

其中体现了 go 的一个 map 的特性：如果某一个键值对的值没有指定，那么默认是返回该值类型的“零元素”的。

而 bool 类型的零元素就是 false。于是这就让【查询】的操作简化了很多。直接查找该键所对应的值，如果在就返回 true，如果不在就返回 false。

这种判断的写法和之前的有一些不一样，这里我们把 map 和 set 的查询类型总结一下：

```go
// map
if _, ok := mp[num]; ok {
    // 在一个 map 中查询一个键值在不在
}

if value, ok := mp[num]; ok {
    // 这种就是完成了两个操作：
    // 一是可以判断 num 在不在集合中，二是可以查询 mp[num] 的值是多少
}

// set
if mp[num] {
    // 如果 num 在 map 中就如何如何
}
```

然后是我做的一些其他的思考：

**【命名上的考虑】**

我们上面说了 go 中对于 set 和 map 这两种数据结构的不同：

- set：在逻辑上是 set，在代码上是 map。
- map：在逻辑上是 map，在代码上是 map。

于是之后在命名 map 类型的变量的时候，变量名中加一个 map 这是理所应当，但是 set 的命名就比较让人犯难了。应该是称呼它为 set 呢，还是就按照语法来，叫它 map 呢？

我们想一下我们给变量命名的动机是什么。如果我们想要的是让自己清楚代码的逻辑，就应该使用 set 来进行命名。如果我们想要看代码的时候可以看到数据结构的底层实现原理，那么就应该使用 map 来命名。这样看下来，set 才是更好的命名方式。

只不过有时候在写代码的时候会比较奇怪。但是每次写的时候都能顺带回忆一下底层原理，那其实也挺不错的。

**【会不会增加新元素的考虑】**

我们知道在 C++ 里面，如果对于一个 map，直接使用 `map[num]` 的查询方式，会让 map 中新增加一个 `<num, 0>` 的映射（其中的 0 是广义的 0，就是 map 的 value 的数据类型的默认零值）。

这不禁让我开始考虑：go 中会不会也有这样的特性，如果这样的话，在每一次进行 `mp[num]` 的查询的时候，都会给集合中添加一个 `<num, false>` 的键值对。这样是不行的。

好在 go 不会这样。除非显式地添加元素。除此之外，只进行简单的查询，是不会给 map 中加入新的元素的。

## 27. 翻转二叉树（226）

给你一棵二叉树的根节点 `root` ，翻转这棵二叉树，并返回其根节点。

```go
func invertTree(root *TreeNode) *TreeNode {
    if root == nil {
        return nil
    }
    root.Left, root.Right = root.Right, root.Left
    invertTree(root.Left)
    invertTree(root.Right)
    return root
}
```

二叉树的题目基本都这样：

- 先做递归的出口（一般是 root 为空的时候就如何如何）
- 递归处理左边，递归处理右边
- 左右结果合并、返回根节点

## 28. 斐波那契数列（509）

**斐波那契数** （通常用 `F(n)` 表示）形成的序列称为 **斐波那契数列** 。该数列由 `0` 和 `1` 开始，后面的每一项数字都是前面两项数字的和。也就是：

```
F(0) = 0，F(1) = 1
F(n) = F(n - 1) + F(n - 2)，其中 n > 1
```

给定 `n` ，请计算 `F(n)` 。

```go
func fib(n int) int {
    if n == 0 {
        return 0
    }
    pre := 0
    cur := 1
    for i := 2; i <= n; i++ {
        pre, cur = cur, pre + cur
    }
    return cur
}
```

在其中的 `pre, cur = cur, pre + cur` 部分用到了 go 的一个特性：多重赋值。

我们想一下如果在传统的编程语言（如 C++）中，这种操作应该怎么做：

```c++
int temp = pre;
pre = cur;
cur = temp + cur;
```

如果不借助一个额外的变量，这个赋值操作是无法完成的。但是 go 语言通过多重赋值，让代码的逻辑更简单了。

## 29. 加一（66）

给定一个由 **整数** 组成的 **非空** 数组所表示的非负整数，在该数的基础上加一。

最高位数字存放在数组的首位， 数组中每个元素只存储**单个**数字。

你可以假设除了整数 0 之外，这个整数不会以零开头。

第一版代码：反转数组

```go
func plusOne(digits []int) []int {
    reverse(digits)
    // 从前往后一直找 9，找到的每一个 9 都变为 0
    // 第一个不是 9 的数字 +1
    // 如果每一位都是 9，那最后就要再额外加上一个 1
    index := 0
    for index < len(digits) && digits[index] == 9 {
        digits[index] = 0
        index++
    }
    if index < len(digits) {
        digits[index] += 1
    } else {
        digits = append(digits, 1)
    }
    reverse(digits)
    return digits
}

func reverse(nums []int) {
    left := 0
    right := len(nums) - 1
    for left < right {
        nums[left], nums[right] = nums[right], nums[left]
        left++
        right--
    }
}
```

这样的逻辑是对的。为什么其中我要反转一下数组呢？因为如果切片中存在的所有数字都是 9，那就需要在切片头部加上一个 1。在 C++ 这样的编程语言中，在数组的头部加上元素可是大忌。我们一般都推崇尾插法，头插法会让程序的性能受到很大影响。

但是后来通过和 AI 交流，我发现 Go 中也可以使用头插法。代码可以这样写：

```go
func plusOne(digits []int) []int {
    index := len(digits) - 1
    for index >= 0 && digits[index] == 9 {
        digits[index] = 0
        index--
    }
    if index >= 0 {
        digits[index] += 1
    } else {
        digits = append([]int{1}, digits...)
    }
    return digits
}
```

go 语言中的 append 方法好像是 go 的什么内部实现的，有一个内存分配和切片扩展机制，反正 append 的性能很高就是了。

## 30. 二进制求和（67）

给你两个二进制字符串 `a` 和 `b` ，以二进制字符串的形式返回它们的和。

```go

func addBinary(a string, b string) string {
    result := ""
    carry := 0

    // 将 a 和 b 从尾部开始遍历
    i, j := len(a) - 1, len(b) - 1
    for i >= 0 || j >= 0 || carry != 0 {
        x := 0
        if i >= 0 {
            x = int(a[i] - '0')
            i--
        }
        y := 0
        if j >= 0 {
            y = int(b[j] - '0')
            j--
        }
        sum := x + y + carry
        result = string(rune(sum % 2) + '0') + result
        carry = sum / 2
    }

    return result
}
```

实际上一开始做这个题目的时候，费了一些时间没做出来。是因为对 go 语言中字符和数字之间进行转换的底层原理不太清楚了。之前用 C++ 的时候，这部分知识掌握得挺好的，对底层摸得也挺清楚的。后来好像是用 python 还是什么，对函数封装得有点多，让我对底层知识慢慢模糊了。今天再处理 go 的时候，直接晕头转向了，心里面知道自己的想法是啥，但是实现出来老是不对。

实际上 go 在这一块儿做的还是比较底层的，类似于 C++ 中的处理方式。如果是数字直接和字符进行计算，是可以计算的，不过是转换成 ASCII 码进行计算。也就是说，数字 `1` 和字符 `'1'` 是不一样的。数字 1 就是 1，但是字符 `'1'` 的 ASCII 码是 49。

但是跟 C++ 里面有所不同的一点是：`'1'` 在 C++ 中是一个 char 类型的数据，占用一个字节。但是 go 语言中，这是一个 `rune` 类型的数据。`rune` 的意思是字符，从底层来看，`rune` 真实的类型是 `int32`。

那么 Go 语言中，既然有了 `int` 了，为什么还需要 `int32` 呢？实际上 `int` 和 `int32` 还是有区别的。在 C++ 中，我们都知道 `int` 就是 32 位的。但是 Go 中，`int` 的实际位数是会根据机器的属性而发生变化的。如果是 32 位系统，`int` 的大小就是 4 字节；如果是 64 位系统，`int` 的大小就是 8 字节。

可以通过下面的程序来判断自己的系统中 `int` 的位数：

```go
func main() {
	num := 1
	fmt.Printf("The size of 'int' is: %d bytes (%d bits)\n", unsafe.Sizeof(num), unsafe.Sizeof(num)*8)
}
// 输出：The size of 'int' is: 8 bytes (64 bits)
```

这时候我们看一下这个题目中遇到的一个警告：`string(sum % 2 + '0')` 爆出警告了。为什么呢？因为 `sum % 2` 是 `int` 类型的（8 位），而后面的 `'0'` 是 `rune`（`int32`）类型的。本着“包容”的原则，计算出来的数值应该是 `int` 类型的（8 bytes）。

我们知道 `string()` 函数的作用是传入一些参数，然后将传入的参数转换为 `string` 的形式。然后我们想想，`string()` 函数需要的参数最好是什么呢？或者说，既然 byte、rune、int 这些参数都可以作为 `string()` 函数的参数，那么其中哪几种是 `string()` 最喜欢的呢？

一般，我们推荐给 `string()` 传入这几种参数：`byte`、`[]byte`、`rune`、`[]rune`。

除此之外的 `int` 和 `float64` 之类的，即使有时候能跑起来，我们也极其不推荐这样做。

- `int` 转换为字符串：如果传入的是 `int` 类型，`string()` 会将该整数转换为一个对应的字符（基于 Unicode 或者 ASCII），而不是数字字符。

    ```go
    i := 65
    fmt.Println(string(i))  // 输出：A（65 对应 ASCII 字符 'A'）
    j := 1000
    fmt.Println(string(j))  // 输出：相当于 Unicode 字符 'Ϩ'（1000 的 Unicode 字符）
    ```

- `float64` 转换为字符串：与 `int` 类似，`float64` 转换为字符串也不符合预期。

    ```go
    f := 65.5
    fmt.Println(string(f))
    // 编译报错：Cannot convert an expression of the type 'float64' to the type 'string'
    ```

然后我们再回到这个题目，所以我们在计算的时候，直接使用 `string(sum % 2 + '0')`，虽然我们的数字很小，确保了我们执行不会报错，但是还是会爆出警告：不推荐这样做。解决方法，我想到两个：

- `string(rune(sum % 2) + '0')`：rune 类型和 rune 类型的数据相加，最后得到一个 rune 类型的结果，然后再将这个 rune 类型的数据转换为 string。特别的舒服。
- `string(rune(sum % 2 + '0'))`：rune 类型和 int 类型的数据相加，得到一个 int 类型。再将这个 int 类型转换为 rune 类型之后，传给 string() 函数，也不错。

其实如果想要将 int 类型的数据转换为 string 类型的数据，还有另外一种方式，那就是直接使用 `strconv` 包里面的工具。`strconv` 包里面比较常用的有以下几个函数：

- **`strconv.Itoa()`——整数转字符串。**
- **`strconv.Atoi()`——字符串转整数。**
- `strconv.FormatInt()`——整数转字符串（指定进制）。
- `strconv.ParseInt()`——字符串转整数（指定进制）。

这种方式更简单，跟前面哪种方法比起来，相当于是对底层又做了一层封装。实际上就是用两种方式来解决这个题目：是通过底层原理直接计算呢，还是通过封装好的 API 进行转换呢？

应该是这样：掌握好封装的 `strconv` 方式可以减少很多工作的难度，但是打好扎实的底层基础也是很有必要的。













