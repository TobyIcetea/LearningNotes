# Go 刷题（2）

[TOC]

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











待做的题目：

349

543、108、203、110、392、344、387、144、415、2413、100、977、541







