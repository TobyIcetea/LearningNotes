# Go 刷题

看了一些 Go 语言的语法，但是又感觉比较无聊。因为已经有很多语言的基础了，不想再去打那些简单的代码了。

所以，还是决定回归老本行，通过刷 Leetcode 的方式，来提升自己对 Go 语言的熟悉程度。

## 1. 两数之和（1）

给定一个整数数组 `nums` 和一个整数目标值 `target`，请你在该数组中找出 **和为目标值** *`target`* 的那 **两个** 整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。

你可以按任意顺序返回答案。

1.1 暴力枚举

代码如下：

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

1.2 哈希表

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

























待做的题目：

13、118、104

125、202、226、509、66、67、459、746、94、234、1047、349

543、108、203、110、392、344、387、144、415、2413、100、977、541





