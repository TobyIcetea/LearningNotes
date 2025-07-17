# Go 刷题（2）

## 31. 重复的子字符串（459）

给定一个非空的字符串 `s` ，检查是否可以通过由它的一个子串重复多次构成。

```go
import "strings"

func repeatedSubstringPattern(s string) bool {
    s2 := strings.Repeat(s, 2)

    return strings.Index(s2[1:len(s2) - 1], s) != -1
}
```

我们知道 C++ 里面的字符串的 find 函数是支持从某一个索引开始查找的。这个题目这种解法的一个要求就是查找 s2 的时候要从 1 索引开始找起。一开始想着 Go 语言中的 `strings.Index()` 有没有这个功能，结果发现 Index 函数并不原生支持这个功能，但是可以以另一种方式实现。

Go 语言中的切片性能很不错，既然我们查找的时候不想要 0 索引位置的元素，那就可以通过 `[1:]` 切片来排除 0 位置处的元素。

同理，一开始我写的最终判断结果是：`strings.Index(s2[1:], s) != len(s)`，这样是可以的，因为我不想找到最后一个 s，那个是肯定在的。后来发现也可以从查找的母串来下手，就是直接将最后一个元素给拿掉，这样原本的后一个 s 就被破坏了，肯定也就查找不到了。

## 32. 使用最小花费爬楼梯（746）

给你一个整数数组 `cost` ，其中 `cost[i]` 是从楼梯第 `i` 个台阶向上爬需要支付的费用。一旦你支付此费用，即可选择向上爬一个或者两个台阶。

你可以选择从下标为 `0` 或下标为 `1` 的台阶开始爬楼梯。

请你计算并返回达到楼梯顶部的最低花费。

```go
func minCostClimbingStairs(cost []int) int {
    // cost[i] - 爬到第 i 个台阶之后，再起步所要花费的费用
    for i := 2; i < len(cost); i++ {
        cost[i] += min(cost[i - 1], cost[i - 2])
    }
    return min(cost[len(cost) - 1], cost[len(cost) - 2])
}
```

看代码的话，可以看出其中一个特点，就是我们每次计算使用的变量都只有前面刚算过的两个变量。如果这个题目再加几个限制条件，比如不能修改原数组、使用的空间复杂度为 O(1)，这时候我们就可以通过 `pre` 和 `cur` 两个变量得出最后的结果。

代码如下所示：

```go
func minCostClimbingStairs(cost []int) int {
    pre := cost[0]
    cur := cost[1]
    for i := 2; i < len(cost); i++ {
        cur, pre = cost[i] + min(pre, cur), cur
    }
    return min(pre, cur)
}
```

## 33. 二叉树的中序遍历（94）

给定一个二叉树的根节点 `root` ，返回 *它的 **中序** 遍历* 。

我一开始的代码是这样写的：

```go
func inorderTraversal(root *TreeNode) []int {
    res := make([]int, 0)
    inorder(root, res)
    return res
}

func inorder(root *TreeNode, res []int) {
    if root == nil {
        return
    }
    inorder(root.Left, res)
    res = append(res, root.Val)
    inorder(root.Right, res)
}
```

我以为这个代码是没有问题的，但是执行之后，发现 res 一直都是一个空值，从来没有被赋值过。

这让我很是不理解，因为在我印象中，go 中的 slice 切片传递的时候本身传递的就是一个引用，所以在一个函数中对传递进来的 slice 切片进行修改，外面也是能看到的。也就是说这种影响是会传递到函数外部的。比如说下面的例子：

```go
func modifySlice(s []int) {
    s[0] = 42
}

func main() {
    slice := []int{1, 2, 3}
    modifySlice(slice)
    fmt.Println(slice) // 输出 [42 2 3]
}
```

这个例子中，我们通过一个函数 `modifySlice(s []int)` 对 `s` 进行了修改，最终也可以看到，主函数中的 slice 也被修改了。

但是我的本题的算法代码中，对 `res` 的修改就不会生效？

我们想想 `append` 方法的原理：go 语言中的切片有几个属性：

- 指针：指向切片数据的首地址。
- 长度：切片中已使用的元素数量。
- 容量：切片在不重新分配内存的情况下可以容纳的最大元素数量。

如果我们使用 `append()` 方法给一个 slice 添加了一个值，这时候如果长度还没有达到容量的上限，就只会在原本地址的后面，开一个新空间，把要添加的元素给丢进去。但是如果容量已经不够了，就会生成一个新的地址来保存切片，也就是说给原本的切片整体挪动了一个位置。

那么在我的代码中，我就相当于是给了 res 一个新的值，而不是对 res 进行修改了，是将整个 res 的指针的值给修改了。这时候外部肯定是不会感知到的。问题就出现在这里。

所以，如何修改？我们可以从中看出，问题的关键是，我们在 `inorder()` 函数内部处理切片的时候，不能让 slice 的首地址发生变化（但是这不太现实），或者是“让外部知道”我们对 `slice` 的首地址做了一个修改。这如何实现呢？实现方法就是，在传入 slice 的时候，使用指针的方式进行传入。

具体代码如下所示：

```go
func inorderTraversal(root *TreeNode) []int {
    res := make([]int, 0)
    inorder(root, &res)  // 这里修改为传入 res 的地址
    return res
}

func inorder(root *TreeNode, res *[]int) {  // 函数的参数定义修改为指针类型
    if root == nil {
        return
    }
    inorder(root.Left, res)
    *res = append(*res, root.Val)  // 调用的时候要对指针“取内容”
    inorder(root.Right, res)
}
```

也就是说，我们传入的时候，之后不是传入 slice 的首地址了，而是传入“`slice` 首地址的首地址”，这样我们再通过取内容对“`slice` 的首地址”进行修改的时候，外部就能感知到了。

于是这又引出了我对函数设计的时候传入的切片类型的思考：

- 如果在函数内部，我们只是对 `slice` 做一些简单的遍历和修改的操作（例如修改 `slice` 的某一个值），只传入 `slice` 的引用就可以。
- 如果在函数内容，我们需要对 `slice` 进行 `append()` 扩容操作，就要传入 `slice` 的地址（例如 `arr *[]int`），在其中调用的时候也要通过解引用来操作。

然后看看与 slice 类似的其他两种 go 语言原生提供的两种数据结构：map 和 channel。它们在传递的时候，如果函数内部需要对原数据结构进行插入数据等操作，需要传入指针的数据类型吗？

答案是不用，这两种数据结构不会用到 `append()` 这种有时候需要整体迁移地址的函数方法，所以 map 和 channel 就传递普通的引用类型就行了，不会用到指针类型。

最后，再介绍一种完美体现 go 语言切片魅力的写法：

```go
func inorderTraversal(root *TreeNode) []int {
    if root == nil {
        return []int{}
    }
    left := inorderTraversal(root.Left)
    right := inorderTraversal(root.Right)
    return append(append(left, root.Val), right...)
}
```

`append()` 函数的返回值也是一个和原本 slice 相同的 slice，再通过 `right...` 来表示 right 切片中的所有元素。通过链式编程，将左、中、右的结果串联在一起，构成最后的答案。

## 34. 回文链表（234）

给你一个单链表的头节点 `head` ，请你判断该链表是否为回文链表。

如果是，返回 `true` ；否则，返回 `false` 。

我一开始写了一个代码，我写的思路是：将链表的后半部分进行反转，然后判断前半部分和后半部分是否是一样的。但是写的时候改了好几个错，给代码打了好几个补丁。后来问了问 AI，发现我的代码有两个可以改进的地方：

- 实际上不需要遍历完一次之后，再去反转后半部分的链表。我们可以选择慢走一次就反转一个，这样快指针走到结尾的时候，慢指针负责的前半部分也已经反转好了。之后我们就得到了两个链：一个是 slow 开头的后半部分的链，一个是 pre 开头的前半部分的链。
- 使用 fast 和 slow 控制快慢指针，有一个比较难控制的问题就是，链表有奇数个节点和偶数个节点的时候，遇到的情况是不同的。往往要在这里做一些思考和判断。但是今天发现还有一种判断方法：我们知道 fast 指针是一次走两步的，那么**循环停止的时候，如果 fast 指针是空，就说明有偶数个节点；如果 fast 指针不是空，就说明有奇数个节点。**

修改之后的代码如下：

```go
func isPalindrome(head *ListNode) bool {
    if head.Next == nil {
        return true
    }
    fast := head
    slow := head
    var pre *ListNode
    for fast != nil && fast.Next != nil {
        fast = fast.Next.Next
        next := slow.Next
        slow.Next = pre
        pre, slow = slow, next
    }
    
    // 如果 fast 是 nil，就说明有偶数个节点
    // 如果 fast 不是 nil，就说明有奇数个节点
    // slow 及 slow 之后的，都是原本的链表，pre 以及 pre 之前的，都是被反转后的链表
    if fast != nil {
        slow = slow.Next
    }

    for slow != nil {
        if slow.Val != pre.Val {
            return false
        }
        slow = slow.Next
        pre = pre.Next
    }
    return true
}
```

## 35. 删除字符串中的所有相邻重复项（1047）

给出由小写字母组成的字符串 `s`，**重复项删除操作**会选择两个相邻且相同的字母，并删除它们。

在 `s` 上反复执行重复项删除操作，直到无法继续删除。

在完成所有重复项删除操作后返回最终的字符串。答案保证唯一。

```go
func removeDuplicates(s string) string {
    stack := make([]rune, 0)
    for _, c := range s {
        if len(stack) == 0 || stack[len(stack) - 1] != c {
            stack = append(stack, c)
        } else {
            stack = stack[:len(stack) - 1]
        }
    }
    return string(stack)
}
```

## 36. 两个数组的交集（349）

给定两个数组 `nums1` 和 `nums2` ，返回它们的交集。输出结果中的每个元素一定是 **唯一** 的。我们可以 **不考虑输出结果的顺序** 。

```go
func intersection(nums1 []int, nums2 []int) []int {
    // 先建立两个哈希表
    set1 := make(map[int]bool)
    set2 := make(map[int]bool)
    for _, num := range nums1 {
        set1[num] = true
    }
    for _, num := range nums2 {
        set2[num] = true
    }
    
    var res []int
    
    var more map[int]bool
    var less map[int]bool
    if len(set1) > len(set2) {
        more, less = set1, set2
    } else {
        more, less = set2, set1
    }
    
    for num, _ := range less {
        if more[num] {
            res = append(res, num)
        }
    }

    return res
}
```

## 37. 二叉树的直径（543）

给你一棵二叉树的根节点，返回该树的 **直径** 。

二叉树的 **直径** 是指树中任意两个节点之间最长路径的 **长度** 。这条路径可能经过也可能不经过根节点 `root` 。

两节点之间路径的 **长度** 由它们之间边数表示。

先看一版代码：

```go
var maxDiameter int

func diameterOfBinaryTree(root *TreeNode) int {
    getHeight(root)
    return maxDiameter
}

func getHeight(root *TreeNode) int {
    if root == nil {
        return 0
    }
    left := getHeight(root.Left)
    right := getHeight(root.Right)
    maxDiameter = max(maxDiameter, left + right)
    return max(left, right) + 1
}
```

这个代码的功能几乎是没啥错的。但是，在提交的时候，还是报出错误了。而且错误的原因让我百思不得其解。有一个测试案例的结果应该是 1，我甚至使用了 debug，在提交之前先查看了 maxDiamater 的值，发现是 1，但是平台上显示的一直都是我提交的是 3。

后来推测这是 Leetcode 内部的一个 bug，问题可能是因为 Leetcode 错误地共享了不同案例中地 maxDiameter。后来通过查阅资料，又了解到 go 语言中的一个特性，那就是：尽量少使用全局变量。

因此，不管 Leetcode 的问题了，我还是有必要将自己的代码改进一下的。这一次就不会使用全局变量了。

我想到了两种改进的方法：

- 将 maxDiameter 设置为主函数中的普通变量，然后在 getHeight 函数中，将 maxDiameter 以一个引用型变量的形式传入。
- 在主函数中写一个局部函数来处理。

在这里我写一下第二种处理方式的代码：

```go
func diameterOfBinaryTree(root *TreeNode) int {
    maxDiameter := 0

    var getHeight func(root *TreeNode) int
    getHeight = func(root *TreeNode) int {
        if root == nil {
            return 0
        }
        left := getHeight(root.Left)
        right := getHeight(root.Right)
        maxDiameter = max(maxDiameter, left + right)
        return max(left, right) + 1
    }

    getHeight(root)
    return maxDiameter
}
```

其中的第二种方式还体现了一个闭包的特性（我理解的闭包就是一个函数可以修改它外部的变量）。所以之后如果还有类似的需求，优先使用这种局部函数的做法吧。

## 38. 将有序数组转换为二叉搜索树（108）

给你一个整数数组 `nums` ，其中元素已经按 **升序** 排列，请你将其转换为一棵平衡二叉搜索树。

```go
func sortedArrayToBST(nums []int) *TreeNode {
    // 先取其中最中间的一个节点，作为根节点，然后递归处理左边和右边
    
    var createTree func(nums []int, left int, right int) *TreeNode
    createTree = func(nums []int, left int, right int) *TreeNode {
        if left > right {
            return nil
        }
        mid := (left + right) / 2
        root := &TreeNode{Val: nums[mid]}
        root.Left = createTree(nums, left, mid - 1)
        root.Right = createTree(nums, mid + 1, right)
        return root
    }

    return createTree(nums, 0, len(nums) - 1)
}
```

至于算法中，建立新函数的时候，是将新函数建立在原函数的外面，还是原函数的内部，主要考虑以下几点问题：

- 代码是否只在当前函数中使用？
- 代码是不是简单的、专一的逻辑？
- 除了当前的母函数之外，还有没有其他的函数可能会调用此函数？

我刷算法的时候其实考虑不太到这些问题，也不需要考虑。那之后是否使用闭包？这就比较灵活了。

## 39. 移除链表元素（203）

给你一个链表的头节点 `head` 和一个整数 `val` ，请你删除链表中所有满足 `Node.val == val` 的节点，并返回 **新的头节点** 。

```go
func removeElements(head *ListNode, val int) *ListNode {
	dummyHead := &ListNode{Next: head}
	node := dummyHead
	for node.Next != nil {
		if node.Next.Val == val {
			node.Next = node.Next.Next
		} else {
			node = node.Next
		}
	}
	return dummyHead.Next
}
```

## 40. 平衡二叉树（110）

给定一个二叉树，判断它是否是平衡二叉树。

**平衡二叉树** 是指该树所有节点的左右子树的高度相差不超过 1。

```go
func isBalanced(root *TreeNode) bool {
    return getHeight(root) != -1
}

func Abs(val int) int {
	if val > 0 {
		return val
	} else {
		return val * -1
	}
}

func getHeight(root *TreeNode) int {
	if root == nil {
		return 0
	}
	left := getHeight(root.Left)
	right := getHeight(root.Right)
	if left == -1 || right == -1 || Abs(left-right) > 1 {
		return -1
	} else {
		return max(left, right) + 1
	}
}
```

原本的第一版代码是做了一个 res，然后把 res 的地址传给所有的 getHeight 函数调用了。

后来问了问 AI，AI 说不平衡的时候直接返回 -1 就行，这样让代码更简洁，也让 getHeight 的返回值包含的信息量更大。实际上也确实不错。

## 41. 判断子序列（392）

给定字符串 **s** 和 **t** ，判断 **s** 是否为 **t** 的子序列。

字符串的一个子序列是原始字符串删除一些（也可以不删除）字符而不改变剩余字符相对位置形成的新字符串。（例如，`"ace"`是`"abcde"`的一个子序列，而`"aec"`不是）。

```go
func isSubsequence(s string, t string) bool {
    // s 是小串，t 是大串
    i := 0
    j := 0
    for i < len(s) && j < len(t) {
        if s[i] == t[j] {
            i++
            j++
        } else {
            j++
        }
    }
    return i == len(s)
}
```

## 42. 反转字符串（344）

编写一个函数，其作用是将输入的字符串反转过来。输入字符串以字符数组 `s` 的形式给出。

不要给另外的数组分配额外的空间，你必须**[原地](https://baike.baidu.com/item/原地算法)修改输入数组**、使用 O(1) 的额外空间解决这一问题。

```go
func reverseString(s []byte)  {
    left, right := 0, len(s) - 1
    for left < right {
        s[left], s[right] = s[right], s[left]
        left++
        right--
    }
}
```

## 43. 字符串中的第一个唯一字符（387）

给定一个字符串 `s` ，找到 *它的第一个不重复的字符，并返回它的索引* 。如果不存在，则返回 `-1` 。

```go
func firstUniqChar(s string) int {
    letterToCountMap := make(map[byte]int)
    for i := 0; i < len(s); i++ {
        letterToCountMap[s[i]]++
    }
    for i := 0; i < len(s); i++ {
        if letterToCountMap[s[i]] == 1 {
            return i
        }
    }
    return -1
}
```

这是哈希表的经典解法，或者我们可以使用更高效的，在数组上建立哈希表：

```go
func firstUniqChar(s string) int {
    hashMap := make([]int, 26)
    for i := 0; i < len(s); i++ {
        hashMap[s[i] - byte('a')]++
    }
    for i := 0; i < len(s); i++ {
        if hashMap[s[i] - byte('a')] == 1 {
            return i
        }
    }
    return -1
}
```

重点在于理解原理，实际上选择哪种做法没关系的。

## 44. 二叉树的前序遍历（144）

给你二叉树的根节点 `root` ，返回它节点值的 **前序** 遍历。

```go
func preorderTraversal(root *TreeNode) []int {
	res := make([]int, 0)

	var preorder func(root *TreeNode)
	preorder = func(root *TreeNode) {
		if root == nil {
			return
		}
		res = append(res, root.Val)
		preorder(root.Left)
		preorder(root.Right)
	}

	preorder(root)
	return res
}
```

## 45. 字符串相加（415）

给定两个字符串形式的非负整数 `num1` 和`num2` ，计算它们的和并同样以字符串形式返回。

你不能使用任何內建的用于处理大整数的库（比如 `BigInteger`）， 也不能直接将输入的字符串转换为整数形式。

```go
func addStrings(num1 string, num2 string) string {
    carry := 0
    i := len(num1) - 1
    j := len(num2) - 1
    
    res := make([]byte, 0)

    for i >= 0 || j >= 0 || carry != 0 {
        value1 := 0
        value2 := 0
        if i >= 0 {
            value1 = int(num1[i] - '0')
            i--
        }
        if j >= 0 {
            value2 = int(num2[j] - '0')
            j--
        }
        sum := value1 + value2 + carry
        sum, carry = sum % 10, sum / 10
        
        res = append(res, byte(sum + '0'))
    }

    return reverse(string(res))
}

func reverse(str string) string {
    bytes := []byte(str)
    left := 0
    right := len(str) - 1
    for left < right {
        bytes[left], bytes[right] = bytes[right], bytes[left]
        left++
        right--
    }
    return string(bytes)
}
```

## 46. 最小偶倍数（2413）

给你一个正整数 `n` ，返回 `2` 和 `n` 的最小公倍数（正整数）。

```go
func smallestEvenMultiple(n int) int {
    if n & 1 == 1 {
        return 2 * n
    }
    return n
}
```

## 47. 相同的树（100）

给你两棵二叉树的根节点 `p` 和 `q` ，编写一个函数来检验这两棵树是否相同。

如果两个树在结构上相同，并且节点具有相同的值，则认为它们是相同的。

```go
func isSameTree(p *TreeNode, q *TreeNode) bool {
    if p == q {
        return true
    }    
    if p == nil && q != nil || p != nil && q == nil {
        return false
    }
    if p.Val != q.Val {
        return false
    }
    return isSameTree(p.Left, q.Left) && isSameTree(p.Right, q.Right)
}
```

## 48. 有序数组的平方（977）

给你一个按 **非递减顺序** 排序的整数数组 `nums`，返回 **每个数字的平方** 组成的新数组，要求也按 **非递减顺序** 排序。

```go
func sortedSquares(nums []int) []int {
	var left int
	var right int
	for right < len(nums) {
		if nums[right] >= 0 {
			break
		}
		right++
	}
	left = right - 1

	// left 指向的值都是负数
	// right 位置的都是正数
	res := make([]int, 0, len(nums))
	for left >= 0 && right < len(nums) {
		if nums[left]*-1 <= nums[right] {
			// 左边
			res = append(res, nums[left]*nums[left])
			left--
		} else {
			// 右边
			res = append(res, nums[right]*nums[right])
			right++
		}
	}

	for left >= 0 {
		res = append(res, nums[left]*nums[left])
		left--
	}
	for right < len(nums) {
		res = append(res, nums[right]*nums[right])
		right++
	}

	return res
}
```

或者是，我们也可以从两端开始构建数组：

```go
func sortedSquares(nums []int) []int {
    res := make([]int, len(nums))
    left := 0
    right := len(nums) - 1
    pos := len(nums) - 1
    
    for left <= right {
        leftSquare := nums[left] * nums[left]
        rightSquare := nums[right] * nums[right]
        if leftSquare > rightSquare {
            res[pos] = leftSquare
            pos--
            left++
        } else {
            res[pos] = rightSquare
            pos--
            right--
        }
    }

    return res
}
```

## 49. 反转字符串II（541）

给定一个字符串 `s` 和一个整数 `k`，从字符串开头算起，每计数至 `2k` 个字符，就反转这 `2k` 字符中的前 `k` 个字符。

- 如果剩余字符少于 `k` 个，则将剩余字符全部反转。
- 如果剩余字符小于 `2k` 但大于或等于 `k` 个，则反转前 `k` 个字符，其余字符保持原样。

```go
func reverseStr(s string, k int) string {
    bytes := []byte(s)
    left := 0
    right := min(k - 1, len(s) - 1)
    
    for left < len(s) {
        reverseBytes(bytes, left, right)
        left += 2 * k
        right = min(right + 2 * k, len(s) - 1)
    }

    return string(bytes)
}

func reverseBytes(bytes []byte, left int, right int) {
    for left < right {
        bytes[left], bytes[right] = bytes[right], bytes[left]
        left++
        right--
    }
}
```

## 50. 温度转换（2469）

给你一个四舍五入到两位小数的非负浮点数 `celsius` 来表示温度，以 **摄氏度**（**Celsius**）为单位。

你需要将摄氏度转换为 **开氏度**（**Kelvin**）和 **华氏度**（**Fahrenheit**），并以数组 `ans = [kelvin, fahrenheit]` 的形式返回结果。

返回数组 *`ans`* 。与实际答案误差不超过 `10-5` 的会视为正确答案**。**

**注意：**

- `开氏度 = 摄氏度 + 273.15`
- `华氏度 = 摄氏度 * 1.80 + 32.00`

```go
func convertTemperature(celsius float64) []float64 {
    var kelvin float64
    var fahrenheit float64

    kelvin = celsius + 273.15
    fahrenheit = celsius * 1.8 + 32.0

    return []float64{kelvin, fahrenheit}
}
```

## 51. 最长回文字串（409）

给定一个包含大写字母和小写字母的字符串 `s` ，返回通过这些字母构造成的最长的回文串的长度。

在构造过程中，请注意 **区分大小写** 。比如 `"Aa"` 不能当做一个回文字符串。

```go
func longestPalindrome(s string) int {
    // 统计所有的元素的数量
    countsMap := make([]int, 128)
    for i := 0; i < len(s); i++ {
        countsMap[s[i]]++
    }
    res := 0
    for i := 'a'; i <= 'z'; i++ {
        res += countsMap[i] >> 1 << 1
    }
    for i := 'A'; i <= 'Z'; i++ {
        res += countsMap[i] >> 1 << 1
    }
    if res < len(s) {
        res += 1
    }
    return res
}
```

## 52. 种花问题（605）

假设有一个很长的花坛，一部分地块种植了花，另一部分却没有。可是，花不能种植在相邻的地块上，它们会争夺水源，两者都会死去。

给你一个整数数组 `flowerbed` 表示花坛，由若干 `0` 和 `1` 组成，其中 `0` 表示没种植花，`1` 表示种植了花。另有一个数 `n` ，能否在不打破种植规则的情况下种入 `n` 朵花？能则返回 `true` ，不能则返回 `false` 。

```go
func canPlaceFlowers(flowerbed []int, n int) bool {
    // 宽度为 n 的空地：
	// 1. 如果这个空地两边都不是边缘，那么可以种 (n - 1) / 2 个
	// 2. 如果靠近了一边的边缘，那么可以种 n / 2 个
	// 3. 如果两边都是边缘，那么可以种 (n + 1) / 2 个

    left := -1
    right := -1

    var getCapacity func(spaceNum int) int
    getCapacity = func(spaceNum int) int {
        edgeNum := 0
        if left == 0 {
            edgeNum++
        }
        if right == len(flowerbed) - 1 {
            edgeNum++
        }
        return (spaceNum + edgeNum - 1) / 2
    }

    index := 0
    capacity := 0
    for index < len(flowerbed) {
        if left == -1 && flowerbed[index] == 0 && (index == 0 || flowerbed[index - 1] == 1) {
            // 开始计数空地数量
            left = index
        }
        if left != -1 && flowerbed[index] == 1 {
            right = index - 1
            spaceNum := right - left + 1
            capacity += getCapacity(spaceNum)

            // 重置
            left = -1
        }
        index++
    }

    if left != -1 {
        right = len(flowerbed) - 1
        spaceNum := right - left + 1
        capacity += getCapacity(spaceNum)
    }

    return capacity >= n
}
```

这是我初步的算法。后面知道还有另一种处理方法——使用贪心算法。

思路就是从前到后遍历一次花坛，遇到空地“能种直接种”，同时统计好已经种的花的数量。这种算法在时间复杂度上跟我原始的算法是一样的，好处就是更简洁了。

```go
func canPlaceFlowers(flowerbed []int, n int) bool {
    plantNum := 0  // 已经种植的数量
    for i := 0; i < len(flowerbed); i++ {
        if flowerbed[i] == 1 {
            continue
        }
        leftIsEmpty := i == 0 || flowerbed[i - 1] == 0
        rightIsEmpty := i == len(flowerbed) - 1 || flowerbed[i + 1] == 0
        if leftIsEmpty && rightIsEmpty {
            flowerbed[i] = 1
            plantNum++
        }
    }
    return plantNum >= n
}
```

## 53. 找到两个数组中的公共元素（2956）

给你两个下标从 **0** 开始的整数数组 `nums1` 和 `nums2` ，它们分别含有 `n` 和 `m` 个元素。请你计算以下两个数值：

- `answer1`：使得 `nums1[i]` 在 `nums2` 中出现的下标 `i` 的数量。
- `answer2`：使得 `nums2[i]` 在 `nums1` 中出现的下标 `i` 的数量。

返回 `[answer1, answer2]`。

```go


func findIntersectionValues(nums1 []int, nums2 []int) []int {
    // 所有数值都是在 [1, 100] 之间的
    hashTable := make([]bool, 101)  // hashTable[i] 表示 i 是否出现过
    
    answer1 := 0
    for _, num := range nums2 {
        hashTable[num] = true
    }
    for i := 0; i < len(nums1); i++ {
        if hashTable[nums1[i]] {
            answer1++
        }
    }

    hashTable = make([]bool, 101)
    answer2 := 0
    for _, num := range nums1 {
        hashTable[num] = true
    }
    for i := 0; i < len(nums2); i++ {
        if hashTable[nums2[i]] {
            answer2++
        }
    }

    return []int{answer1, answer2}
}
```

一开始也用过用 map 结构来存储的方法，但是程序的运行时间比这个长。总结就是：

- 如果知道 key 的范围且 key 的范围是比较小的，就是用切片形式的哈希表。
- 如果不知道 key 范围或者 key 的范围很大，就适合使用 map 结构。

## 54. 各位相加（258）

给定一个非负整数 `num`，反复将各个位上的数字相加，直到结果为一位数。返回这个结果。

```go
func addDigits(num int) int {
    for num >= 10 {
        sum := 0
        for num != 0 {
            sum, num = sum + num % 10, num / 10
        }
        num = sum
    }
    return num
}
```

这是原始的写法，也是直接描述题意的写法。但是这个题目还可以通过一个数学规律：数字根，来进行优化。优化后的代码如下：

```go
func addDigits(num int) int {
    return (num - 1) % 9 + 1
}
```

这无疑是更简单的，但是不好想，其中的数学规律一般也是想不到的。继续探索这种规律，就违背了我刷题的初心了，所以我就不深入钻研了。

## 55. 最长连续递增子序列（674）

给定一个未经排序的整数数组，找到最长且 **连续递增的子序列**，并返回该序列的长度。

**连续递增的子序列** 可以由两个下标 `l` 和 `r`（`l < r`）确定，如果对于每个 `l <= i < r`，都有 `nums[i] < nums[i + 1]` ，那么子序列 `[nums[l], nums[l + 1], ..., nums[r - 1], nums[r]]` 就是连续递增子序列。

 ```go
 func findLengthOfLCIS(nums []int) int {
     // 这里的递增是严格的递增
     res := 1
     left := 0
     index := 1
     for index < len(nums) {
         if nums[index] <= nums[index - 1] {
             // 终止计数
             res = max(res, index - left)
             left = index
         }
         index += 1
     }
     res = max(res, len(nums) - left)
     return res
 }
 ```

## 56. 下一个更大元素I（496）

`nums1` 中数字 `x` 的 **下一个更大元素** 是指 `x` 在 `nums2` 中对应位置 **右侧** 的 **第一个** 比 `x` 大的元素。

给你两个 **没有重复元素** 的数组 `nums1` 和 `nums2` ，下标从 **0** 开始计数，其中`nums1` 是 `nums2` 的子集。

对于每个 `0 <= i < nums1.length` ，找出满足 `nums1[i] == nums2[j]` 的下标 `j` ，并且在 `nums2` 确定 `nums2[j]` 的 **下一个更大元素** 。如果不存在下一个更大元素，那么本次查询的答案是 `-1` 。

返回一个长度为 `nums1.length` 的数组 `ans` 作为答案，满足 `ans[i]` 是如上所述的 **下一个更大元素** 。

```go
func nextGreaterElement(nums1 []int, nums2 []int) []int {
    // 先用一个 map 保存 nums2 中每一个数值所对应的下标
    valueToIndexMap := make(map[int]int)  // key - 数值，value - 对应的在 nums2 中的下标
    for i := 0; i < len(nums2); i++ {
        valueToIndexMap[nums2[i]] = i
    }
    
    res := make([]int, len(nums1))
    pos := 0
    for _, num := range nums1 {
        index := valueToIndexMap[num] + 1
        for index < len(nums2) {
            if nums2[index] > num {
                res[pos] = nums2[index]
                pos++
                break
            }
            index++
        }
        if index == len(nums2) {
            res[pos] = -1
            pos++
        }
    }

    return res
}
```

这是我最初的想法，但是算法的时间复杂度比较高，直接干到了 O(mn)。后来发现这个题目可以用单调栈解决：

```go
func nextGreaterElement(nums1 []int, nums2 []int) []int {
    // 记录一下 nums2 中 value-index 的键值对
    valueToIndexMap := make(map[int]int)
    for i := 0; i < len(nums2); i++ {
        valueToIndexMap[nums2[i]] = i
    }

    // 记录一下 nums2 中的每一个元素，比它更大的都是第几个元素
    nextGreaterIndex := make([]int, len(nums2))  // i 位置的元素右边第一个更大的元素是 nextGreaterIndex[i] 位置的元素
    stack := make([]int, 0)  // 这个 stack 里面存储的都是下标
    for i := 0; i < len(nums2); i++ {
        for len(stack) != 0 && nums2[i] > nums2[stack[len(stack) - 1]] {
            nextGreaterIndex[stack[len(stack) - 1]] = i
            stack = stack[:len(stack) - 1]
        }
        stack = append(stack, i)
    }
    // 剩下的元素都是右边没有比自己更大的了
    for len(stack) != 0 {
        nextGreaterIndex[stack[len(stack) - 1]] = -1
        stack = stack[:len(stack) - 1]
    }

    res := make([]int, len(nums1))
    for i := 0; i < len(nums1); i++ {
        posInNums2 := valueToIndexMap[nums1[i]]
        if nextGreaterIndex[posInNums2] == -1 {
            res[i] = -1
        } else {
            res[i] = nums2[nextGreaterIndex[posInNums2]]
        }
    }

    return res
}
```

我是如何理解单调栈的呢？我觉得单调栈其实就是，遍历每一个元素，然后这些元素就像是争霸王一样（以底部更大的单调栈举例），如果新来的没有之前的大，那你新来的就在上面好好呆着；如果新来的比之前的一些大，就让之前垫好的一层一层元素一个一个起来，一直到一个它惹不起的元素。

这个过程中我们需要记录什么呢？我们需要记录的是“是谁杀死了这个元素”，也就是说每个元素都要知道，它自己最后是被谁击败的。如果一直到我们的比赛结束，栈中还保留着一些元素，那这些元素就是没有被击败的，最后活下来的元素。

这样一说就明白单调栈适合处理什么类型的问题了：序列中相邻元素的相对大小比较重要的问题。最经典的就是：我想知道在我右边第一个比我大的是谁。这就是经典的单调栈的问题。

## 57. 第N个泰波纳契数（1137）

泰波那契序列 Tn 定义如下： 

T0 = 0, T1 = 1, T2 = 1, 且在 n >= 0 的条件下 Tn+3 = Tn + Tn+1 + Tn+2

给你整数 `n`，请返回第 n 个泰波那契数 Tn 的值。

```go
func tribonacci(n int) int {
    if n == 0 {
        return 0
    }
    if n == 1 || n == 2 {
        return 1
    }
    prepre := 0
    pre := 1
    cur := 1
    for i := 3; i <= n; i++ {
        cur, pre, prepre = cur + pre + prepre, cur, pre
    }
    return cur
}
```

## 58. 子数组最大平均数I（643）

给你一个由 `n` 个元素组成的整数数组 `nums` 和一个整数 `k` 。

请你找出平均数最大且 **长度为 `k`** 的连续子数组，并输出该最大平均数。

任何误差小于 `10-5` 的答案都将被视为正确答案。

```go
func findMaxAverage(nums []int, k int) float64 {
    // 就是算总和
    curSum := 0
    left := 0
    right := k - 1
    
    for i := left; i <= right; i++ {
        curSum += nums[i]
    }
    maxSum := curSum

    for right < len(nums) - 1 {
        curSum -= nums[left]
        left++
        right++
        curSum += nums[right]
        maxSum = max(maxSum, curSum)
    }

    return float64(maxSum) / float64(k)
}
```

## 59. 分割字符串的最大得分（1422）

给你一个由若干 0 和 1 组成的字符串 `s` ，请你计算并返回将该字符串分割成两个 **非空** 子字符串（即 **左** 子字符串和 **右** 子字符串）所能获得的最大得分。

「分割字符串的得分」为 **左** 子字符串中 **0** 的数量加上 **右** 子字符串中 **1** 的数量。

```go
func maxScore(s string) int {
    leftScore := make([]int, len(s))
    rightScore := make([]int, len(s))
    
    // leftScore[index] 表示左边部分的右边界是 index，index 位置处的元素属于左边
    if s[0] == '0' {
        leftScore[0] = 1
    } else {
        leftScore[0] = 0
    }
    for i := 1; i < len(s); i++ {
        if s[i] == '0' {
            leftScore[i] = leftScore[i - 1] + 1
        } else {
            leftScore[i] = leftScore[i - 1]
        }
    }

    for i := len(s) - 2; i >= 0; i-- {
        if s[i + 1] == '1' {
            rightScore[i] = rightScore[i + 1] + 1
        } else {
            rightScore[i] = rightScore[i + 1]
        }
    }

    res := 0
    for i := 0; i < len(s) - 1; i++ {
        res = max(res, leftScore[i] + rightScore[i])
    }
    return res
}
```

这是第一次写的代码，时间复杂度 O(n)，但是空间复杂度也是 O(n)。通过如下的优化，可以将空间复杂度优化为 O(1)。

```go
func maxScore(s string) int {
    res := 0

    score := 0
    // 先假装所有的元素都在右边
    for i := 0; i < len(s); i++ {
        if s[i] == '1' {
            score++
        }
    }

    for i := 0; i < len(s) - 1; i++ {
        // i 表示本次将 i 位置的元素归到左边
        if s[i] == '0' {
            score++
        } else {
            score--
        }
        res = max(res, score)
    }

    return res
}
```

## 60. 三角形的最大高度（3200）

给你两个整数 `red` 和 `blue`，分别表示红色球和蓝色球的数量。你需要使用这些球来组成一个三角形，满足第 1 行有 1 个球，第 2 行有 2 个球，第 3 行有 3 个球，依此类推。

每一行的球必须是 **相同** 颜色，且相邻行的颜色必须 **不同**。

返回可以实现的三角形的 **最大** 高度。

```go
func maxHeightOfTriangle(red int, blue int) int {
    var smaller int
    var larger int
    if red < blue {
        smaller = red
        larger = blue
    } else {
        smaller = blue
        larger = red
    }

    curHeight := 1
    largerNeed := 2  // 要想再高一层，较多的球需要多少
    smallerNeed := 1  // 较少的球需要到达多少
    for larger >= largerNeed && smaller >= smallerNeed {
        curHeight++
        smallerNeed, largerNeed = largerNeed, smallerNeed + curHeight + 1
    }

    return curHeight   
}
```

我这个算法是一层一层往上升的。largerNeed 和 smallerNeed 每次都提升自己的水平，这差不多是一个 1 + 2 + 3 +... 这样？如果这样的话，我的时间复杂度就是 $\sqrt{n}$ 差不多。

题解中还有另一种更高效的解法，是用了一个二分查找。先设置了一个 `canBuild(height int)` 函数，这个函数的功能是看能不能构建一个高度为 `height` 的三角形，根据返回的结果，取二分查找一个更合适的最大高度。

如果 n 特别大，这种方法或许会有更好的返回值吧。但是这个题目只是简单题，数据量也控制在 500 以内。既然已经超过 100% 了，就说明更新的方法可能也没啥意义。那就……到此为止。















