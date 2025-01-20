# Go 刷题（6）

## 151. N叉树的最大深度（559）

给定一个 N 叉树，找到其最大深度。

最大深度是指从根节点到最远叶子节点的最长路径上的节点总数。

N 叉树输入按层序遍历序列化表示，每组子节点由空值分隔（请参见示例）。

```go
/**
 * Definition for a Node.
 * type Node struct {
 *     Val int
 *     Children []*Node
 * }
 */

func maxDepth(root *Node) int {
    if root == nil {
        return 0
    }

    // 广度优先搜索
    queue := []*Node{root}
    res := 0
    for len(queue) != 0 {
        // 将 queue 中的数据的孩子都放进来
        size := len(queue)
        for i := 0; i < size; i++ {
            node := queue[0]
            queue = queue[1:]
            for _, child := range node.Children {
                queue = append(queue, child)
            }
        }
        res++
    }
    return res
}
```











待做题目：
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



