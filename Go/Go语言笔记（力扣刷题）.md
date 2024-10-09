# Go 语言笔记（实践版）

看了一些 Go 语言的语法，但是又感觉比较无聊。因为已经有很多语言的基础了，不想再去打那些简单的代码了。

所以，还是决定回归老本行，通过刷 Leetcode 的方式，来提升自己对 Go 语言的熟悉程度。

## 1. 两数之和

### 1.1 暴力枚举

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

### 1.2 哈希表

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

## 2. 合并两个有序数组

![image-20241009102720407](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241009102720407.png)

### 2.1 合并后排序

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

















待做的题目：

70、20、14、121、21、206、2235、704、27、26

9、169、283、35、28、141、160、136、69、13、118、104

125、202、226、509、66、67、459、746、94、234、1047、349

543、108、203、110、392、344、387、144、415、2413、100、977、541





