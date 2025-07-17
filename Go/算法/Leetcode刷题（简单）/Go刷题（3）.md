# Go 刷题（3）

## 61. 数组的度（697）

给定一个非空且只包含非负数的整数数组 `nums`，数组的 **度** 的定义是指数组里任一元素出现频数的最大值。

你的任务是在 `nums` 中找到与 `nums` 拥有相同大小的度的最短连续子数组，返回其长度。

```go
func findShortestSubArray(nums []int) int {
    // 先找到最大的度是多少
    counts := make(map[int]int)
    maxCount := 0
    for _, num := range nums {
        counts[num]++
        maxCount = max(maxCount, counts[num])
    }

    if maxCount == 1 {
        return 1
    }

    // 只有计数结果最多的那个 num 有可能成为答案
    maxCountNums := make([]int, 0)  // 存放所有 count 为 maxCount 的数值
    for num, count := range counts {
        if count == maxCount {
            maxCountNums = append(maxCountNums, num)
        }
    }
    res := len(nums)
    for _, num := range maxCountNums {
        // 查找 num 在 nums 中出现的第一次和最后一次
        left := 0
        for left < len(nums) {
            if nums[left] == num {
                break
            }
            left++
        }
        right := len(nums) - 1
        for right >= 0 {
            if nums[right] == num {
                break
            }
            right--
        }
        curLength := right - left + 1
        res = min(res, curLength)
    }
    return res
}
```

这是第一次写的代码。其中的问题挺明显的，在做的时候我也想到了，最坏的情况下，我可能会有很多的 maxCountNums，这样会让我遍历 maxCountNums 的时候，又遍历接近 n 次的 nums 数组。这样的时间复杂度就是接近于：$O(n^2)$。

后来问了问 AI，发现这个题目其实也可以只用一次遍历解决问题。实际上我一开始也想过这种方法，但是在 Go 中还没有玩过自定义结构体来解决问题的事儿，所以就没有实现。

中间插播一条 go 语言知识，是关于 map 结构映射到结构体类型的知识的。看看下面这个代码：

```go
func findShortestSubArray(nums []int) int {
    numToInfos := make(map[int]numInfo)
    for i, num := range nums {
        if _, ok := numToInfos[num]; ok {
            // 如果已经记录过 num 了
            // ================== 下面两行语句报错了 ====================
            numToInfos[num].count += 1
            numToInfos[num].last = i
        } else {
            // num 是第一次出现
            numToInfos[num] = numInfo{count: 1, first: i, last: i}
        }
    }
    // ....
}
```

为什么对 value 部分的结构体的信息进行修改会报错呢？我们知道 go 中的字符串是不能修改的，所以直接修改字符串的值是会导致报错的，这可以理解。但是结构体按理说是可以进行修改的呀，为什么对结构体进行修改也会导致报错呢？

实际上还是跟 map 的 value 部分的使用有关。我的 map 的 value 部分是一个结构体（值类型的），之后在遍历中，我直接取值 `numsToInfos[num]`，看起来这是取出了 num 对应的 value，但是实际上不是，取出来的应该是这个对应的 value 的“一个副本”。

这个副本的内容和原本的 value 是一样的。但是原本的那个真正的 value，是在内存中的，是有确定的地址的。但是这个临时的变量，可能是存在于一个类似于 tmp 区的地方，反正就是没有确定的地址，或者说是不可寻址的。只能访问一下，是不可以进行修改的。

So，如何解决？AI 给出了两个解决方法，第一个是在修改的时候，先将真正的 value 复制一份到本地，对本地那个变量进行你想做的修改，之后再用你本地这个最新修改的结构体，去替换原本的结构体。这种方法很好想，不过缺点也很明显：繁琐，而且性能很低。

之后引出第二种方法：使用结构体指针。这不是说取值的时候使用指针，而是在定义结构体的时候，我们就使用结构体指针来定义 map。如果要操作一个结构体的话，Go 中不管使用值类型还是引用类型都是很方便的，所以使用指针类型不会带来什么使用上的问题。后来经过和 AI 交流，我确定了之后的一个策略：之后只要使用 map，并且 map 的值类型是结构体，我都使用指针类型，不用值类型了。

使用指针有一些弊端：那就是可能会出现程序多个位置同时访问、修改指针所指的位置，这时候会出错。其中涉及到一些程序同步的问题。这个不难实现，但是就从我平时刷题来说，暂时还用不到，心里面先有个印象就行。

最后再来看看最后的程序：

```go
// 保存每个出现过的数字的信息
// 第一种方法中，我们只记录了每一个数字出现的 count，这里我们记录了更多的信息
type numInfo struct {
    count int
    first int
    last int
}

func findShortestSubArray(nums []int) int {
    numToInfos := make(map[int]*numInfo)

    maxCount := 1

    for i, num := range nums {
        if _, ok := numToInfos[num]; ok {
            // 如果已经记录过 num 了
            numToInfos[num].count += 1
            numToInfos[num].last = i
            maxCount = max(maxCount, numToInfos[num].count)
        } else {
            // num 是第一次出现
            numToInfos[num] = &numInfo{count: 1, first: i, last: i}
        }
    }

    // 处理极端情况
    if maxCount == 1 {
        return 1
    }
    
    res := len(nums)
    for _, info := range numToInfos {
        if info.count == maxCount {
            res = min(res, info.last - info.first + 1)
        }
    }
    
    return res
}
```

## 62. 三个数的最大乘积（628）

给你一个整型数组 `nums` ，在数组中找出由三个数组成的最大乘积，并输出这个乘积。

第一版代码是这样的：

```go
import "sort"
func maximumProduct(nums []int) int {
    n := len(nums)

    // 根据 nums 中负数的数量解答
    sort.Ints(nums)
    negativeCount := n
    for i := 0; i < n; i++ {
        if nums[i] >= 0 {
            negativeCount = i
            break
        }
    }

    if negativeCount == 0 || negativeCount == 1 {
        // 没有负数 和 有一个负数 的情况
        return nums[n - 1] * nums[n - 2] * nums[n - 3]
    } else {
        // 有两个及以上的负数
        return max(nums[n - 1] * nums[n - 2] * nums[n - 3], nums[0] * nums[1] * nums[n - 1])
    }
}
```

整理了一下，发现不管 negativeCount 是多少，答案都是一样的：

```go
import "sort"
func maximumProduct(nums []int) int {
    n := len(nums)
    sort.Ints(nums)
    return max(nums[n - 1] * nums[n - 2] * nums[n - 3], nums[0] * nums[1] * nums[n - 1])
}
```

但是这样的效率不是最高的。我使用了排序，那就是把时间复杂度干到了 O(nlogn) 了。我也能发现，其中只用到了整个数组中的三个最大值和两个最小值。如果想要强行将时间复杂度优化到 O(n) 的话，也可以写这样的一坨屎山代码：

```go

import "math"
func maximumProduct(nums []int) int {
    // 排序：min1 < min2 < max1 < max2 < max3
    min1 := math.MaxInt
    min2 := math.MaxInt
    max1 := math.MinInt
    max2 := math.MinInt
    max3 := math.MinInt
    
    n := len(nums)
    for i := 0; i < n; i++ {
        num := nums[i]
        if num < min1 {
            // num 是最小的
            min1, min2 = num, min1
        } else if num < min2 {
            // num 只是比 min2 小
            min2 = num
        }
        if num > max3 {
            max1, max2, max3 = max2, max3, num
        } else if num > max2 {
            max1, max2 = max2, num
        } else if num > max1 {
            max1 = num
        }
    }
    return max(max1 * max2 * max3, min1 * min2 * max3)
}
```

欸！不过从中也学到了有用的东西。比如，在 go 中，之后如果想要用最大或者最小的整数来初始化某一个变量，就可以直接使用 `math.MinInt` 或者是 `max.MaxInt` 来作为初始化的值了。如果想要表示最大值，就用 MinInt 来初始化；如果想要表示最小值，就用 MaxInt 来初始化。

或者这个题目还可以使用 `heap` 结构来实现。为此我还专门去学了一下 `container/heap` 的用法，最后强行用这种结构解决了这个题。代码又臭又长效率又低，我的评价是没吃过 💩 的可以试一下：

```go
import "container/heap"

// 定义大根堆
type maxHeap []int
func (h *maxHeap) Len() int { return len(*h) }
func (h *maxHeap) Less(i, j int) bool { return (*h)[i] > (*h)[j] }
func (h *maxHeap) Swap(i, j int) { (*h)[i], (*h)[j] = (*h)[j], (*h)[i] }
func (h *maxHeap) Push(x interface{}) {
    *h = append(*h, x.(int))
}
func (h *maxHeap) Pop() interface{} {
    n := len(*h)
    res := (*h)[n - 1]
    *h = (*h)[:n - 1]
    return res
}

// 定义小根堆
type minHeap []int
func (h *minHeap) Len() int { return len(*h) }
func (h *minHeap) Less(i, j int) bool { return (*h)[i] < (*h)[j] }
func (h *minHeap) Swap(i, j int) { (*h)[i], (*h)[j] = (*h)[j], (*h)[i] }
func (h *minHeap) Push(x interface{}) {
    *h = append(*h, x.(int))
}
func (h *minHeap) Pop() interface{} {
    n := len(*h)
    res := (*h)[n - 1]
    *h = (*h)[:n - 1]
    return res
}

func maximumProduct(nums []int) int {
    // 需要三个最大的元素 和 两个最小的元素
    minHeap1 := minHeap{}
    heap.Init(&minHeap1)
    maxHeap1 := maxHeap{}
    heap.Init(&maxHeap1)

    for _, num := range nums {
        // minHeap 中最多只能有三个元素
        heap.Push(&minHeap1, num)
        if len(minHeap1) > 3 {
            heap.Pop(&minHeap1)
        }
        // maxHeap 中最多只能有两个元素
        heap.Push(&maxHeap1, num)
        if len(maxHeap1) > 2 {
            heap.Pop(&maxHeap1)
        }
    }

    // min1 < min2 < max1 < max2 < max3
    max1 := heap.Pop(&minHeap1).(int)
    max2 := heap.Pop(&minHeap1).(int)
    max3 := heap.Pop(&minHeap1).(int)
    min2 := heap.Pop(&maxHeap1).(int)
    min1 := heap.Pop(&maxHeap1).(int)

    return max(max1 * max2 * max3, min1 * min2 * max3)
}
```

## 63. 最大连续1的个数（485）

给定一个二进制数组 `nums` ， 计算其中最大连续 `1` 的个数。

```go
func findMaxConsecutiveOnes(nums []int) int {
    maxCountOne := 0
    left := -1
    for i := 0; i < len(nums); i++ {
        if left == -1 && nums[i] == 1 {
            // 开始记录
            left = i
        }
        if left != -1 && nums[i] == 0 {
            // 清算
            maxCountOne = max(maxCountOne, i - left)
            left = -1
        }
    }
    if left != -1 {
        maxCountOne = max(maxCountOne, len(nums) - left)
    }
    return maxCountOne
}
```

这个思路是，每次遇到 1 的时候，就开始记录。如果遇到 0 之后，就停止记录，开始清算本次一共有多少 1。还要注意，算法的最后要看一下是不是还在记录状态。如果是的话，就要假设最后多一个元素 0，做一次切片末尾的清算。

还有另一种更简单的思路：做一个 count 变量，遇到 1 就加一并且判断最大值，遇到 0 就清零：

```go
func findMaxConsecutiveOnes(nums []int) int {
    count := 0
    res := 0
    for _, num := range nums {
        if num == 1 {
            count++
            res = max(res, count)
        } else {
            count = 0
        }
    }
    return res
}
```

相比之下，这种思路是更加简单的。

## 64. 第三大的数（414）

给你一个非空数组，返回此数组中 **第三大的数** 。如果不存在，则返回数组中最大的数。

```go
import "math"
func thirdMax(nums []int) int {
    // max1 < max2 < max3
    max1 := math.MinInt
    max2 := math.MinInt
    max3 := math.MinInt
    
    for _, num := range nums {
        if num == max1 || num == max2 || num == max3 {
            continue
        }
        if num > max3 {
            max1, max2, max3 = max2, max3, num
        } else if num > max2 {
            max1, max2 = max2, num
        } else if num > max1 {
            max1 = num
        }
    }

    if max1 == math.MinInt || max2 == math.MinInt {
        return max3
    } else {
        return max1
    }
}
```

## 65. 岛屿的周长（463）

给定一个 `row x col` 的二维网格地图 `grid` ，其中：`grid[i][j] = 1` 表示陆地， `grid[i][j] = 0` 表示水域。

网格中的格子 **水平和垂直** 方向相连（对角线方向不相连）。整个网格被水完全包围，但其中恰好有一个岛屿（或者说，一个或多个表示陆地的格子相连组成的岛屿）。

岛屿中没有“湖”（“湖” 指水域在岛屿内部且不和岛屿周围的水相连）。格子是边长为 1 的正方形。网格为长方形，且宽度和高度均不超过 100 。计算这个岛屿的周长。

```go
func islandPerimeter(grid [][]int) int {
    res := 0
    row := len(grid)
    column := len(grid[0])
    
    // 计算一个岛屿周围有几个邻接的岛屿
    var aroundLandCount func(i int, j int) int
    aroundLandCount = func(i int, j int) int {
        count := 0
        if i - 1 >= 0 && grid[i - 1][j] == 1 {
            count += 1
        }
        if i + 1 < row && grid[i + 1][j] == 1 {
            count += 1
        }
        if j - 1 >= 0 && grid[i][j - 1] == 1 {
            count += 1
        }
        if j + 1 < column && grid[i][j + 1] == 1 {
            count += 1
        }
        return count
    }
    
    for i := 0; i < row; i++ {
        for j := 0; j < column; j++ {
            if grid[i][j] == 1 {
                res += 4 - aroundLandCount(i, j)
            }
        }
    }

    return res
}
```

## 66. 数组异或操作（1486）

给你两个整数，`n` 和 `start` 。

数组 `nums` 定义为：`nums[i] = start + 2*i`（下标从 0 开始）且 `n == nums.length` 。

请返回 `nums` 中所有元素按位异或（**XOR**）后得到的结果。

```go
func xorOperation(n int, start int) int {
    res := 0
    for i := 0; i < n; i++ {
        res = res ^ start
        start += 2
    }
    return res
}
```

## 67. 优质数对的总数I（3162）

给你两个整数数组 `nums1` 和 `nums2`，长度分别为 `n` 和 `m`。同时给你一个**正整数** `k`。

如果 `nums1[i]` 可以除尽 `nums2[j] * k`，则称数对 `(i, j)` 为 **优质数对**（`0 <= i <= n - 1`, `0 <= j <= m - 1`）。

返回 **优质数对** 的总数。

```go
import "sort"
func numberOfPairs(nums1 []int, nums2 []int, k int) int {
    if k != 1 {
        for i := 0; i < len(nums2); i++ {
            nums2[i] *= k
        }
    }

    sort.Ints(nums1)

    // 定义在 nums1 中的二分查找
    // 返回大于等于 target 的第一个数字
    var indexInNums1 func(target int) int 
    indexInNums1 = func(target int) int {
        left := 0
        right := len(nums1) - 1
        result := -1
        for left <= right {
            mid := (left + right) >> 1
            if nums1[mid] >= target {
                result = mid
                right = mid - 1
            } else {
                left = mid + 1
            }
        }
        return result
    }

    var res int
    for _, num := range nums2 {
        // 查找 num 在 nums1 中出现的位置
        index := indexInNums1(num)  // num 在 nums1 中的位置
        for index < len(nums1) {
            if index >= 0 && nums1[index] % num == 0 {
                res++
            }
            index++
        }
    }

    return res
}
```

或者我们可以通过一个哈希表来记录 nums1 中所有元素的出现次数：

```go
func numberOfPairs(nums1 []int, nums2 []int, k int) int {
    if k != 1 {
        for i := 0; i < len(nums2); i++ {
            nums2[i] *= k
        }
    }

    var res int

    counts := make(map[int]int)  // 记录 nums1 中每个元素出现的次数
    for _, num := range nums1 {
        counts[num]++
    }

    for _, num := range nums2 {
        value := num  // value 表示 num 的 n 倍
        for value <= 50 {  // 这里直接用 50 是因为题目中给出了范围
            if count, ok := counts[value]; ok {
                res += count
            }
            value += num
        }
    }

    return res
}
```

实际上这两种方法都还可以继续优化，不过两种方法都已经达到这个题的标准了，时间都已经超过 100% 了，所以就不继续优化了。

不过有意思的是，在这里我在编写二分查找的时候，遇到一些问题，最后又总结出来了一些二分查找更简便的实现思路。总计就是：所想即所写。

**【查找切片中大于 target 的第一个值】**

```go
func binarySearchFirstGreater(nums []int, target int) int {
	left, right := 0, len(nums)-1

	for left <= right {
        mid := left + (right-left)/2

		if nums[mid] > target {
			right = mid - 1   // 继续在左半部分查找是否有更靠前的符合条件的元素
		} else {
			left = mid + 1    // 在右半部分继续查找
		}
	}

	return left
}
```

**【查找切片中大于等于 target 的第一个值】**

```go
func binarySearchFirstGreaterOrEqual(nums []int, target int) int {
	left, right := 0, len(nums)-1

	for left <= right {
        mid := left + (right-left)/2

		if nums[mid] >= target {
			right = mid - 1   // 继续在左半部分查找是否有更靠前的符合条件的元素
		} else {
			left = mid + 1    // 在右半部分继续查找
		}
	}

	return left
}
```

**【查找切片中小于 target 的最后一个值】**

```go
func binarySearchLastLess(nums []int, target int) int {
	left, right := 0, len(nums)-1

	for left <= right {
        mid := left + (right-left)/2

		if nums[mid] < target {
			left = mid + 1     // 继续在右半部分查找是否有更靠后的符合条件的元素
		} else {
			right = mid - 1    // 在左半部分继续查找
		}
	}

	return right
}
```

**【查找切片中小于等于 target 的最后一个值】**

```go
func binarySearchLastLessOrEqual(nums []int, target int) int {
	left, right := 0, len(nums)-1

	for left <= right {
        mid := left + (right-left)/2

		if nums[mid] <= target {
			left = mid + 1     // 继续在右半部分查找是否有更靠后的符合条件的元素
		} else {
			right = mid - 1    // 在左半部分继续查找
		}
	}

	return right
}
```

都是相对更进阶的二分查找，最传统的那一种就没有实现了，因为那个很简单。

对我之后再写二分查找的时候有以下一些启示：

- 做 if 条件判断的时候，尽量写 `nums[mid] > target` 这种，而不是 `target > nums[mid]`。也就是说，把 `nums[mid]` 放在左边比较好。
- 查找第一个大于或大于等于某值的元素 --> 返回 `left`。
- 查找最后一个小于或小于等于某值的元素 --> 返回 `right`。
- 因为在二分查找中，`left` 和 `right` 的位置分别代表了符合条件的第一个和最后一个元素的潜在位置。

## 68. 错误的集合（645）

集合 `s` 包含从 `1` 到 `n` 的整数。不幸的是，因为数据错误，导致集合里面某一个数字复制了成了集合里面的另外一个数字的值，导致集合 **丢失了一个数字** 并且 **有一个数字重复** 。

给定一个数组 `nums` 代表了集合 `S` 发生错误后的结果。

请你找出重复出现的整数，再找到丢失的整数，将它们以数组的形式返回。

 ```go
 func findErrorNums(nums []int) []int {
     n := len(nums)
     counts := make([]int, n + 1)  // counts[i] 表示 i 出现了多少次
     for _, num := range nums {
         counts[num]++
     }
     numAppearTwice := -1
     numNotAppear := -1
     for i, count := range counts {
         if count == 2 {
             numAppearTwice = i
         }
         if count == 0 {
             numNotAppear = i
         }
     }
     return []int{numAppearTwice, numNotAppear}
 }
 ```

## 69. 好数对的数目（1512）

给你一个整数数组 `nums` 。

如果一组数字 `(i,j)` 满足 `nums[i]` == `nums[j]` 且 `i` < `j` ，就可以认为这是一组 **好数对** 。

返回好数对的数目。

```go
func numIdenticalPairs(nums []int) int {
    // 如果某一个数字出现了 n 次，则它提供的好数对的个数是：
    // 1 + 2 + ... + n-1 = n(n-1)/2
    // nums[i] 的范围在 [1, 100] 之间
    counts := make([]int, 101)
    for _, num := range nums {
        counts[num]++
    }

    res := 0
    for _, count := range counts {
        if count != 0 {
            res += count * (count - 1) / 2
        }
    }

    return res
}
```

## 70. 哈沙德数（3099）

如果一个整数能够被其各个数位上的数字之和整除，则称之为 **哈沙德数**（Harshad number）。给你一个整数 `x` 。如果 `x` 是 **哈沙德数** ，则返回 `x` 各个数位上的数字之和，否则，返回 `-1` 。

```go
func sumOfTheDigitsOfHarshadNumber(x int) int {
    sum := 0
    originX := x
    for x != 0 {
        sum += x % 10
        x /= 10
    }
    if originX % sum == 0 {
        return sum
    } else {
        return -1
    }
}
```

## 71. 数组元素和与数字和的绝对差（2535）

给你一个正整数数组 `nums` 。

- **元素和** 是 `nums` 中的所有元素相加求和。
- **数字和** 是 `nums` 中每一个元素的每一数位（重复数位需多次求和）相加求和。

返回 **元素和** 与 **数字和** 的绝对差。

**注意：**两个整数 `x` 和 `y` 的绝对差定义为 `|x - y|` 。

```go
func differenceOfSum(nums []int) int {
    sum1 := 0  // 元素和
    sum2 := 0  // 数字和

    for _, num := range nums {
        sum1 += num
        for num != 0 {
            sum2 += num % 10
            num /= 10
        }
    }

    res := sum1 - sum2
    if res >= 0 {
        return res
    } else {
        return -res
    }
}
```

## 72. 找到所有数组中消失的数字（448）

给你一个含 `n` 个整数的数组 `nums` ，其中 `nums[i]` 在区间 `[1, n]` 内。请你找出所有在 `[1, n]` 范围内但没有出现在 `nums` 中的数字，并以数组的形式返回结果。

第一版代码：

```go
import "sort"
func findDisappearedNumbers(nums []int) []int {
    sort.Ints(nums)
    var res []int

    n := len(nums)
    index := 0  // 用来遍历 nums 数组
    for num := 1; num <= n; num++ {
        // 在 nums 中看看有没有 num 这个数字
        for index < n && nums[index] < num {
            index++
        }
        if index < n && nums[index] > num {
            res = append(res, num)
        }
        if index >= n {
            res = append(res, num)
        }
    }

    return res
}
```

后来问 AI 发现还有一个天才做法，可以保证时间复杂度 O(n)，空间复杂度 O(1)。算法的思想是，直接在原数组的位置处标记每一个元素。但是我之前想到，如果要标记一个每一个元素，那岂不是至少要申请一块大小为 n 的空间来保存才行。但是这里让我知道还有另一种做法：原本的数组里面都是正数。我们的标记方法是：将这个正数转换为负数。此时，一个单单的数字就可以代表两个信息：其符号决定了其是否被标记，其绝对值代表了它原来的数值。

这算不算是一种数据压缩：

```go
func findDisappearedNumbers(nums []int) []int {
    // 第一次遍历：标记
    // 将元素出现过的位置上面的数字都变成负数
    for _, num := range nums {
        num = Abs(num)
        index := num - 1
        if nums[index] > 0 {
            nums[index] *= -1
        }
    }

    res := make([]int, 0)

    // 第二次遍历，将没有出现过的元素（也就是还是正数的位置）都装进 res 里
    for i, num := range nums {
        if num > 0 {
            res = append(res, i + 1)
        }
    }

    return res
}

func Abs(num int) int {
    if num < 0 {
        return -num
    } else {
        return num
    }
}
```

## 73. 寻找数组的中心下标（724）

给你一个整数数组 `nums` ，请计算数组的 **中心下标** 。

数组 **中心下标** 是数组的一个下标，其左侧所有元素相加的和等于右侧所有元素相加的和。

如果中心下标位于数组最左端，那么左侧数之和视为 `0` ，因为在下标的左侧不存在元素。这一点对于中心下标位于数组最右端同样适用。

如果数组有多个中心下标，应该返回 **最靠近左边** 的那一个。如果数组不存在中心下标，返回 `-1` 。

```go
func pivotIndex(nums []int) int {
    // 看起来像是一个差分的题目
    sum := 0
    n := len(nums)
    for i := 0; i < n; i++ {
        sum += nums[i]
        nums[i] = sum
    }

    // 左边元素合是 nums[i - 1]
    // 右边元素合是 sum - nums[i]
    for i := 0; i < n; i++ {

        var left int
        if i == 0 {
            left = 0
        } else {
            left = nums[i - 1]
        }

        right := sum - nums[i]
        
        if left == right {
            return i
        }
    }

    return -1
}
```

或者我们可以更优化一下，这次是不修改原数组的：

```go
func pivotIndex(nums []int) int {
    sum := 0
    for _, num := range nums {
        sum += num
    }
    
    leftSum := 0
    for i, num := range nums {
        rightSum := sum - leftSum - num
        if leftSum == rightSum {
            return i
        }
        leftSum += num
    }

    return -1
}
```

从时间和空间复杂度上来看，两种方法效率相同。但是还是法二更加优秀。

## 74. 单词规律（290）

给定一种规律 `pattern` 和一个字符串 `s` ，判断 `s` 是否遵循相同的规律。

这里的 **遵循** 指完全匹配，例如， `pattern` 里的每个字母和字符串 `s` 中的每个非空单词之间存在着双向连接的对应规律。

第一遍写的答辩代码：

```go

import "strings"
func wordPattern(patterns string, s string) bool {
    i, j := 0, 0  // i 用来遍历 pattern，j 用来遍历 s
    patternWordMap := make(map[byte]string)
    wordPatternMap := make(map[string]byte)

    // check 判断 s 的下一个单词是不是 word
    var check func(word string) bool
    check = func(word string) bool {
        for i := 0; i < len(word); i++ {
            if word[i] == s[j] {
                j++
            } else {
                return false
            }
        }
        // 跳过一个空格
        j++
        return true
    }

    for i < len(patterns) {
        pattern := patterns[i]
        if word, ok := patternWordMap[pattern]; ok{
            // pattern 已经出现过了，对应的单词是 word
            if !check(word) {
                return false
            }
        } else {
            // pattern 第一次出现
            // 截取一个 word
            var builder strings.Builder
            for j < len(s) && s[j] != ' ' {
                builder.WriteByte(s[j])
                j++
            }
            // 最后跳过空格
            j++
            
            word = builder.String()
            patternWordMap[pattern] = word

            // 看看是否在此之前，已经有 word 对应的 pattern
            if wordPatternMap[word] != 0 {
                return false
            }
            wordPatternMap[word] = pattern
        }
        i++
    }

    // 防止 s 中元素的个数比 patterns 中元素的个数更多
    if j != len(s) + 1 {
        return false
    }

    return true
}
```

这个代码可谓是又臭又长。接下来看看经过 AI 修改之后的第二版代码：

```go

import "strings"
func wordPattern(pattern string, s string) bool {
    words := strings.Fields(s)  // 这样 words 里面就是 dog cat 这样的字符串
    if len(pattern) != len(words) {
        return false
    }

    patternToWordMap := make(map[byte]string)
    wordToPatternMap := make(map[string]byte)
    
    for i := 0; i < len(pattern); i++ {
        p := pattern[i]
        word := words[i]
        
        if mappedWord, ok := patternToWordMap[p]; ok {
            if mappedWord != word {
                return false
            }
        } else {
            patternToWordMap[p] = word
        }

        if mappedPattern, ok := wordToPatternMap[word]; ok {
            if mappedPattern != p {
                return false
            }
        } else {
            wordToPatternMap[word] = p
        }
    }

    return true
}
```

其中主要获得了以下的知识：

- 切分字符串的好方法：`strings.Fields(s string)`。这个可以将中间有空格或者换行符的字符串切分成一块一块的。举例如下：

    ```go
    s := "Hello  world\tthis is a test\n"
    words := strings.Fields(s)
    fmt.Println(words)  // [Hello world this is a test]
    ```

- 之后要给一个 map 中映射出来的 value 命名的时候，不知道该命名啥，就可以使用 `mappedByte`、`mappedPattern`、`mappedWord` 这样的命名方式。

## 75. 丑数（263）

**丑数** 就是只包含质因数 `2`、`3` 和 `5` 的 *正* 整数。

给你一个整数 `n` ，请你判断 `n` 是否为 **丑数** 。如果是，返回 `true` ；否则，返回 `false` 。

```go
func isUgly(n int) bool {
    // 其实就是问你，这个数字能不能被 2 3 5 表达
    if n <= 0 {
        return false
    }
    for n != 1 {
        if n % 2 == 0 {
            n /= 2
        } else if n % 3 == 0 {
            n /= 3
        } else if n % 5 == 0 {
            n /= 5
        } else {
            return false
        }
    }
    return true
}
```

## 76. 图像渲染（733）

有一幅以 `m x n` 的二维整数数组表示的图画 `image` ，其中 `image[i][j]` 表示该图画的像素值大小。你也被给予三个整数 `sr` , `sc` 和 `color` 。你应该从像素 `image[sr][sc]` 开始对图像进行上色 **填充** 。

为了完成 **上色工作**：

1. 从初始像素开始，将其颜色改为 `color`。
2. 对初始坐标的 **上下左右四个方向上** 相邻且与初始像素的原始颜色同色的像素点执行相同操作。
3. 通过检查与初始像素的原始颜色相同的相邻像素并修改其颜色来继续 **重复** 此过程。
4. 当 **没有** 其它原始颜色的相邻像素时 **停止** 操作。

最后返回经过上色渲染 **修改** 后的图像 。

```go
func floodFill(image [][]int, sr int, sc int, color int) [][]int {
    if image[sr][sc] == color {
        return image
    }

    row := len(image)
    column := len(image[0])
    originColor := image[sr][sc]

    visited := make([][]bool, row)
    for i := 0; i < row; i++ {
        visited[i] = make([]bool, column)
    }

    // 深度搜索可以涂的格子
    var dfs func(i int, j int)
    dfs = func(i int, j int) {
        if i < 0 || i >= row || j < 0 || j >= column {
            return
        }
        if visited[i][j] {
            return
        }
        visited[i][j] = true
        if image[i][j] == originColor {
            image[i][j] = color
            dfs(i - 1, j)
            dfs(i + 1, j)
            dfs(i, j - 1)
            dfs(i, j + 1)
        }
    }

    dfs(sr, sc)

    return image
}
```

## 77. 自然数（728）

**自除数** 是指可以被它包含的每一位数整除的数。

- 例如，`128` 是一个 **自除数** ，因为 `128 % 1 == 0`，`128 % 2 == 0`，`128 % 8 == 0`。

**自除数** 不允许包含 0 。

给定两个整数 `left` 和 `right` ，返回一个列表，*列表的元素是范围 `[left, right]`（包括两个端点）内所有的 **自除数*** 。

```go
func selfDividingNumbers(left int, right int) []int {
    res := make([]int, 0)

    Outer:
    for num := left; num <= right; num++ {
        numCopy := num
        // 看 num 是不是自然数
        for numCopy != 0 {
            lastNumber := numCopy % 10  // num 的最后一位
            if lastNumber == 0 || num % lastNumber != 0 {
                continue Outer
            }
            numCopy /= 10
        }
        res = append(res, num)
    }

    return res
}
```

这里用到了一个比较特殊的语法，是 Go 语言中的 for 循环外部的通过标记来 `break` 或者 `continue`。语法其实和 C 中的 goto 之类的比较像。但是这里通过 Outer 和 Inner 来标记内外层循环，可以实现直接从内层循环跳转出外层循环。

C++ 中这样做往往要加一些 flag 之类的变量，但是 Go 中在这块儿又额外的语法，所以实现起来比 C++ 要简单一些。

## 78. 字符串中的单词数（434）

统计字符串中的单词个数，这里的单词指的是连续的不是空格的字符。

请注意，你可以假定字符串里不包括任何不可打印的字符。

```go

import "strings"
func countSegments(s string) int {
    // 返回空格的个数 + 1
    return len(strings.Fields(s))
}
```

## 79. 找出最大的可达成数字（2769）

给你两个整数 `num` 和 `t` 。

如果整数 `x` 可以在执行下述操作不超过 `t` 次的情况下变为与 `num` 相等，则称其为 **可达成数字** ：

- 每次操作将 `x` 的值增加或减少 `1` ，同时可以选择将 `num` 的值增加或减少 `1` 。

返回所有可达成数字中的最大值。可以证明至少存在一个可达成数字。

```go
func theMaximumAchievableX(num int, t int) int {
    return num + 2*t
}
```

## 80. 数组拆分（561）

给定长度为 `2n` 的整数数组 `nums` ，你的任务是将这些数分成 `n` 对, 例如 `(a1, b1), (a2, b2), ..., (an, bn)` ，使得从 `1` 到 `n` 的 `min(ai, bi)` 总和最大。

返回该 **最大总和** 。

```go
import "sort"
func arrayPairSum(nums []int) int {
    sort.Ints(nums)
    res := 0
    for i := 0; i < len(nums); i += 2 {
        res += nums[i]
    }
    return res
}
```

## 81. 单值二叉树（965）

如果二叉树每个节点都具有相同的值，那么该二叉树就是*单值*二叉树。

只有给定的树是单值二叉树时，才返回 `true`；否则返回 `false`。

```go
func isUnivalTree(root *TreeNode) bool {
    if root == nil {
        return true
    }
    val := root.Val
    if root.Left != nil && root.Left.Val != val {
        return false
    }
    if root.Right != nil && root.Right.Val != val {
        return false
    }
    return isUnivalTree(root.Left) && isUnivalTree(root.Right)
}
```

## 82. 三角形的最大周长（976）

给定由一些正数（代表长度）组成的数组 `nums` ，返回 *由其中三个长度组成的、**面积不为零**的三角形的最大周长* 。如果不能形成任何面积不为零的三角形，返回 `0`。

```go

import "sort"
func largestPerimeter(nums []int) int {
    sort.Ints(nums)
    for i := len(nums) - 1; i >= 2; i-- {
        if nums[i - 1] + nums[i - 2] > nums[i] {
            return nums[i] + nums[i - 1] + nums[i - 2]
        }
    }

    return 0
}
```

## 83. 求出硬币游戏的赢家（3222）

给你两个 **正** 整数 `x` 和 `y` ，分别表示价值为 75 和 10 的硬币的数目。

Alice 和 Bob 正在玩一个游戏。每一轮中，Alice 先进行操作，Bob 后操作。每次操作中，玩家需要拿走价值 **总和** 为 115 的硬币。如果一名玩家无法执行此操作，那么这名玩家 **输掉** 游戏。

两名玩家都采取 **最优** 策略，请你返回游戏的赢家。

```go
func winningPlayer(x int, y int) string {
    turn := false  // false 表示是 bob 的回合，true 表示是 alice 的回合
    for {
        if x >= 1 && y >= 4 {
            x -= 1
            y -= 4
        } else {
            break
        }
        turn = !turn
    }
    if turn {
        return "Alice"
    } else {
        return "Bob"
    }
}
```

或者是根据代码做进一步的计算优化：

```go
func winningPlayer(x int, y int) string {
    y = y / 4
    count := min(x, y)  // count 表示可以进行多少次游戏
    if count & 1 == 0 {
        return "Bob"
    } else {
        return "Alice"
    }
}
```

## 84. 字符串的最大公因子（1071）

对于字符串 `s` 和 `t`，只有在 `s = t + t + t + ... + t + t`（`t` 自身连接 1 次或多次）时，我们才认定 “`t` 能除尽 `s`”。

给定两个字符串 `str1` 和 `str2` 。返回 *最长字符串 `x`，要求满足 `x` 能除尽 `str1` 且 `x` 能除尽 `str2`* 。

```go
func gcdOfStrings(str1 string, str2 string) string {
    res := ""

    // 先算出 len1 和 len2 的所有公因数
    minLen := min(len(str1), len(str2))
    lastLen := 0  // 上一次检测时候最终的长度

    Outer:
    for num := 1; num <= minLen; num++ {
        if len(str1) % num != 0 || len(str2) % num != 0 {
            continue
        }
        // 接下来要求 str1 和 str2 的前 num 个元素相同
        // 而且 str1 和 str2 都是可以由这 num 个元素构成 n 次
        for i := lastLen; i < num; i++ {
            if str1[i] != str2[i] {
                break Outer
            }
        }
        lastLen = num  // 保证前 lastLen 个元素肯定是相同的
        // 检查 str1
        for i := lastLen; i < len(str1); i++ {
            if str1[i] != str1[i % lastLen] {
                continue Outer
            }
        }
        // 检查 str2
        for i := lastLen; i < len(str2); i++ {
            if str2[i] != str2[i % lastLen] {
                continue Outer
            }
        }
        res = str1[:lastLen]
    }

    return res
}
```

这种解法已经满足时间要求。但是还可以利用数学结论，创造出另一种解法：

```go
func gcdOfStrings(str1 string, str2 string) string {
    var gcd func(a int, b int) int
    gcd = func(a int, b int) int {
        for b != 0 {
            a, b = b, a % b
        }
        return a
    }

    if str1 + str2 != str2 + str1 {
        return ""
    }
    maxLen := gcd(len(str1), len(str2))
    return str1[:maxLen]
}
```

这种解法主要用到几个数学结论：

- `str1` 和 `str2` 有最大公因子的充要条件是：`str1 + str2 == str2 + str1`。比如说 str1 由 m 个 abc 组成，str2 由 n 个 abc 组成，那么 `m+n 个 abc == n+m 个 abc`。
- 确定有解的情况下，`gcd(len(str1), len(str2))` 就是最优解的长度。

其中有一个数学规律，我之前还真没注意过：如果有两个数字，它们有一些公约数，那么其中的其他所有公约数也是最大公约数的约数。比如说 12 和 18 的公约数有：`1,2,3,6`，其中 `1,2,3` 也都是 `6` 的约数。

其中的数学思想一时间还有点想不清楚，那就不继续想了，再想下去方向就偏了。

本体还有一个收获是又回顾了一下 `gcd` 算法的写法：

```go
func gcd(a int, b int) int {
    for b != 0 {
        a, b := b, a % b
    }
    return a
}
```

## 85. Excel表列名称（168）

给你一个整数 `columnNumber` ，返回它在 Excel 表中相对应的列名称。

例如：

> A -> 1
> B -> 2
> C -> 3
> ...
> Z -> 26
> AA -> 27
> AB -> 28 
> ...

```go
func convertToTitle(columnNumber int) string {
    res := make([]byte, 0)
    for columnNumber != 0 {
        num := columnNumber % 26
        carry := columnNumber / 26
        if num == 0 {
            num = 26
            carry -= 1
        }
        res = append(res, 'A' + byte(num) - 1)
        columnNumber = carry
    }

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

## 86. 转置矩阵（867）

给你一个二维整数数组 `matrix`， 返回 `matrix` 的 **转置矩阵** 。

矩阵的 **转置** 是指将矩阵的主对角线翻转，交换矩阵的行索引与列索引。

![img](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/hint_transpose.png)

```go
func transpose(matrix [][]int) [][]int {
    row := len(matrix)
    column := len(matrix[0])
    
    // res 是一个 column * row 的矩阵
    res := make([][]int, column)
    for i := 0; i < column; i++ {
        res[i] = make([]int, row)
    }

    for i := 0; i < row; i++ {
        for j := 0; j < column; j++ {
            res[j][i] = matrix[i][j]
        }
    }

    return res
}
```

## 87. 比特位计数（338）

给你一个整数 `n` ，对于 `0 <= i <= n` 中的每个 `i` ，计算其二进制表示中 **`1` 的个数** ，返回一个长度为 `n + 1` 的数组 `ans` 作为答案。

```go
func countBits(n int) []int {
    res := make([]int, n + 1)
    for i := 0; i <= n; i++ {
        num := i
        for num != 0 {
            if num & 1 == 1 {
                res[i]++
            }
            num = num >> 1
        }
    }

    return res
}
```

但是这种方法时间效率很低，特别特别慢。后来根据题解，换了一种巧妙的二进制计算方法：

```go
func countBits(n int) []int {
    // 奇数：奇数一定比前面那个偶数多一个 1
    // 偶数：偶数的个数和除以二之后的那个数一样多
    res := make([]int, n + 1)

    res[0] = 0
    for i := 1; i <= n; i++ {
        if i & 1 == 1 {
            // 奇数
            res[i] = res[i - 1] + 1
        } else {
            // 偶数
            res[i] = res[i >> 1]
        }
    }

    return res
}
```

## 88. 反转字符串中的元音字母（345）

给你一个字符串 `s` ，仅反转字符串中的所有元音字母，并返回结果字符串。

元音字母包括 `'a'`、`'e'`、`'i'`、`'o'`、`'u'`，且可能以大小写两种形式出现不止一次。

```go
func reverseVowels(s string) string {
    vowels := map[byte]bool {
        'a': true, 'e': true, 'i': true, 'o': true, 'u': true,
        'A': true, 'E': true, 'I': true, 'O': true, 'U': true,
    }
    
    bytes := []byte(s)
    left := 0
    right := len(bytes) - 1

    for left < right {
        for left < len(s) && !vowels[bytes[left]] {
            left++
        }
        for right >= 0 && !vowels[bytes[right]] {
            right--
        }
        if left < right {
            bytes[left], bytes[right] = bytes[right], bytes[left]
            left++
            right--
        }
    }

    return string(bytes)
}
```

## 89. 二叉搜索树中的众数（501）

给你一个含重复值的二叉搜索树（BST）的根节点 `root` ，找出并返回 BST 中的所有 [众数](https://baike.baidu.com/item/众数/44796)（即，出现频率最高的元素）。

如果树中有不止一个众数，可以按 **任意顺序** 返回。

假定 BST 满足如下定义：

- 结点左子树中所含节点的值 **小于等于** 当前节点的值
- 结点右子树中所含节点的值 **大于等于** 当前节点的值
- 左子树和右子树都是二叉搜索树

```go
// 普通做法
func findMode(root *TreeNode) []int {
    counts := make(map[int]int)
    maxCount := 0

    var dfs func(root *TreeNode)
    dfs = func(root *TreeNode) {
        if root == nil {
            return
        }
        counts[root.Val]++
        maxCount = max(maxCount, counts[root.Val])
        dfs(root.Left)
        dfs(root.Right)
    }

    dfs(root)

    res := make([]int, 0)
    for value, count := range counts {
        if count == maxCount {
            res = append(res, value)
        }
    }

    return res
}
```

但是这样属于是使用了一种暴力的解法，没有利用好题目中原本模型中的特性。

如果算法题目中出现了“二叉搜索树”，那么二叉搜索树的一个很重要的性质就是：二叉搜索树中序遍历的结果是有序的。

```go
func findMode(root *TreeNode) []int {
    // 如何利用好二叉搜索树的性质？——中序搜索
    maxCount := 0
    curCount := 0
    curValue := 0
    res := make([]int, 0)
    first := true

    var inorderTraverse func(root *TreeNode)
    inorderTraverse = func(root *TreeNode) {
        if root == nil {
            return
        }
        inorderTraverse(root.Left)

        if first {
            curValue = root.Val
            first = false
        }

        if root.Val == curValue {
            curCount++
        } else {
            curCount = 1
        }
        curValue = root.Val

        if curCount > maxCount {
            res = []int{}
            maxCount = curCount
        }
        if curCount == maxCount {
            res = append(res, curValue)
        }

        inorderTraverse(root.Right)
    }

    inorderTraverse(root)

    return res
}
```

中间 debug 了很长时间，因为今天 Leetcode 会员刚好过期了，没有 debug 功能了。改了好久的代码，但是测试案例的返回结果一直都是 0。最后才发现原来是因为我定义了函数内部的局部函数，但是没有通过 `inorderTraverse(root)` 来调用。😓

## 90. 链表的中间节点（876）

给你单链表的头结点 `head` ，请你找出并返回链表的中间结点。

如果有两个中间结点，则返回第二个中间结点。

```go
func middleNode(head *ListNode) *ListNode {
    fast := head
    slow := head
    for fast != nil && fast.Next != nil {
        fast = fast.Next.Next
        slow = slow.Next
    }

    return slow
}
```

## 

















