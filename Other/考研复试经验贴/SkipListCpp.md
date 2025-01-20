# 跳表简介

（本教程来源于 ka ma wang，本人当时买了相应的教程，现在以学习笔记的形式分享给学弟学妹们，但是为了保护原作者的利益，尽量不要随便传播。）

本节是 K-V 存储引擎项目的第一章节，最主要目的是用于介绍项目中的核心数据结构 —— 跳表的基本原理。次要目的则是了解整个项目的结构，以及全部章节的内容安排。

## 1. 章节安排

完整章节总共有 9 章（包括本章）。9 章的内容分别如下：

**第一章、跳表简介（本章节）**

在实现一个基于跳表的 K-V 存储引擎之前，我们需要了解一下跳表的基本原理，第一章将会介绍跳表的基本概念和原理，并不涉及到具体的实现细节。并且将会介绍一些工业软件上使用跳表的案例。

**第二章、跳表的定义**

第二章将会介绍在具体实现基于跳表的 K-V 存储引擎时底层使用的数据结构。具体来说，我们会在第二章明确跳表类的定义，介绍对外提供各种操作的接口，并且在后续章节中会详细介绍各个接口的具体实现。

**第三章、跳表的层级**

作为一种用于存储有序元素，并且可以替代平衡树的数据结构，跳表的分层机制在这其中起到了关键的作用，第三章将会介绍这个关键并且十分简单易懂的概念以及具体实现。

**第四章、跳表的插入**

第四章的主题是跳表的插入，在这章我们会具体介绍跳表中是如何插入节点的，并且由于跳表的插入操作是依赖于跳表的搜索操作的，所以跳表的搜索操作也将会在这章进行介绍。

**第五章、跳表的删除**

第五章的主题是跳表的删除。在这章我们会具体介绍跳表中是如何删除节点的。

**第六章、跳表的展示**

第六章的主题是跳表的展示。在实现了跳表的插入操作和删除操作后，我们需要验证这两种操作的正确性，所以我们需要将跳表中的数据打印出来。

**第七章、生成持久化文件**

第七章的主题是生成持久化文件。在本章中，我们会介绍如何将内存中跳表的数据生成持久化文件，以及将持久化文件中的数据读取内存中的跳表内。

**第八章、模块合并**

第八章的主题是模块合并，在本章中，我们会介绍如何将前面所有章节分别介绍的各个模块合并成一个完整的 K-V 存储引擎，并将其编译为可执行文件。

**第九章、压力测试**

第九章的主题是压力测试，将会提供一些对 K-V 存储引擎进行压力测试的方案。

## 2. 存储引擎简介

本项目是使用 C++ 开发、基于跳表实现的轻量级键值数据库。实现了插入数据、删除数据、查询数据、数据展示、生成持久化文件、恢复数据以及数据库大小显示等功能。

### 2.1 存储引擎项目结构

项目整体上拥有一个 skiplist.h 文件。

拥有两个核心类：

1. Node 类
2. SkipList 类

Node 类是存储引擎中用于存放实际数据的类，而 SkipList 则对外提供了组织，访问，操作 Node 类的功能。

### 2.2 应用技术

在本项目中，除 了 C++ 语法基础外，还使用到以下 C++ 具体核心特性：

- 面向对象
- 类模板
- IO 操作
- 多线程（压测阶段）

## 3. 什么是跳表

为了深入理解本项目中采用的数据结构 — 跳表，我们必须从其基础出发：链表。链表是许多复杂数据结构的基石，在这其中也包括了跳表。

> 跳表（Skip List）是由 William Pugh 发明的一种数据结构，他本人对跳表的评价是：“跳跃列表是在很多应用中有可能替代平衡树而作为实现方法的一种数据结构。跳跃列表的算法有同平衡树一样的渐进的预期时间边界，并且更简单、更快速和使用更少的空间。”

设想我们的存储引擎是以有序链表作为基础构建的。在这样的设置下，存储引擎中的数据结构呈现如下特点：

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011042732.png)

其中每个节点都存储着一对键值对。为了便于理解，假设其中键是数字，值是字符串，并且它们按键的顺序排列。

这便构成了一个基于**有序链表**的简易键值（K-V）存储引擎。

设想现在我们需要在存储引擎中查找特定键（比如 key = 6）对应的值。由于单链表的线性结构，我们不得不从头节点开始，逐个遍历节点。

例如，在查找 key = 6 的过程中，我们需要按顺序检查每个节点，即查找路径为 1 -> 2 -> 3 -> 4 -> 5 -> 6。这种方法的时间复杂度为 O(n)，在数据量庞大时效率低下。

因此，需要一种更高效的查找方法，而跳表正是这样的一种解决方案。

> 首先需要明确，我们所有的优化操作都基于链表是有序的这一前提。

那么，问题来了：我们该如何提升原有链表的查找速度呢？

如下图所示：

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011046845.png)

为了提高查找效率，我们采取了一种独特的策略：**从原链表中选取关键节点作为索引层。这些被选出的节点形成了一个新的，较原链表更为简短的链表**。由于原链表本身是有序的，索引层中的节点也同样保持有序，利用这个有序性，我们能够加快查找速度。

以查找 key = 6 的节点为例。在传统的单链表中，我们需要从头至尾逐个检查节点。例如，我们首先比较 key = 1 的节点，发现它小于 6，然后继续比较 key = 2 的节点，如此循环。

但在跳表中，情况就大不相同了。我们首先检查第一层索引，比较 key = 1 的节点后，可以直接跳到 key = 3 的节点，因为 6 大于 3，我们再跳到 key = 5 的节点。在这个过程中，我们省略了与 key = 2 和 key = 4 的节点的比较，但实际上，通过与 key = 3 和 key = 5 的比较，我们已经间接地排除了它们。

如此一来，查找路径缩短为 1 -> 3 -> 5 -> 6。与原始的单链表相比，效率有所提升。

那么，如果我们在第一层索引上再构建一层索引会怎样呢？

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011050633.png)

当我们从第二层索引开始进行查找时，查找会变得更加高效。在比较了 key = 1 的节点 和 key = 6 的节点后，我们不再逐个检查 key = 2、key = 3 和 key = 4 的节点，而是直接跳到 key = 5 节点进行比较。如此一来，整个查找路径便缩短为 1 -> 5 -> 6。

在节点数量众多且索引层级充足的情况下，这种查找方法的效率极高。例如，如果在每层索引中，每两个节点就有一个被提升为上一层的索引，那么查找的时间复杂度可以降至 O(log n)，这与二分查找的效率相仿。

> 这样的机制不仅显著提升了查找效率，还在保持链表灵活性的同时，为我们的存储引擎带来了接近二分查找的高效性能。

## 4. 跳表如何搜索节点

由于搜索操作是跳表中最基础的功能，不管是跳表的插入、删除，都依赖其搜索操作。所以我们先从跳表的搜索机制说起。

**跳表的搜索流程：**

1. 开始于顶层索引：首先定位到跳表最顶层索引的首个节点
2. 水平遍历：从最顶层的首个节点开始向右遍历。如果当前节点的下一个节点的值小于或等于待查找的值，表明该节点左侧的所有节点都小于或等于待查找值，此时跳转到下一个节点
3. 下沉操作：若当前节点的下一个节点的值大于待查找值，意味着所需查找的节点位于当前位置左侧的某处，此时执行下沉操作，即向下移动到较低层的同一位置
4. 重复查找与下沉：继续执行第二步和第三步的操作，直到到达最底层链表。在此层继续向右移动，直到找到目标节点或达到链表末端

现有一个跳表结构，目标是查找值为 70 的数据，让我们模拟一下这一查询过程：

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011051534.png)

如图一所示，从最顶层开始，首个节点为 30，既然 30 小于 70，我们继续向右，比较下一个节点 80。发现 80 大于 70，此时，我们需要执行下沉操作，移动到下一层索引，如图二所示。

在图二中，我们比较节点 50 与 70。由于 50 小于 70，我们向右移动到下一个节点，如图三所示。

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011052612.png)

在图三，我们继续比较节点 50 的下一个节点 80 与 70。由于 70 小于 80，再次执行下沉操作，如图四所示。

在图四，我们将节点 60（即 50 的下一个节点）与 70 进行比较。此时，70 大于 60，因此我们向右移动，结果如图五所示。

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011053591.png)

到了图五，我们比较节点 60 的下一个节点 80 与 70。由于 70 小于 80，我们再次下沉到更底层的索引，如图六所示。

最后，在图六中，我们比较节点 60 的下一个节点 70。发现我们已经成功找到了目标值 70，此时查找成功。

## 5. 跳表如何插入节点

### 5.1 跳表节点的有序性

因为跳表的所有**节点都是有序排列的**，无论是插入还是删除操作，都必须维持这种有序性。

> 这一点使得跳表具有与平衡树相似的特性，即它的任何操作都密切依赖于高效的查询机制。

为了维护跳表中节点的有序性，我们必须先通过搜索找到一个合适的位置进行操作。

以插入一个新节点为例，假设我们需要插入数值为 61 的节点。如下图所示，在执行跳表的搜索操作后，我们可以定位到一个特定的区域：此区域的左侧节点值小于 61，而右侧节点值大于 61。在确定了这一位置之后，我们便可在此处插入新节点 61。

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011055335.png)

实际上，我们已经成功地在跳表中插入了一个节点，并且能够有效地搜索到这个节点。

然而，如果我们持续向跳表中添加数据，而忽视对索引的更新，这将导致跳表效率的显著退化。在最极端的情况下，这种效率下降甚至可能使跳表的查询效率降至 O(n)，与普通链表的查询效率相当。

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011057551.png)

### 5.2 插入数据时需要维护索引

从以上案例中，我们可以看出，为了保持跳表的高查询效率，其**索引必须进行动态更新。**

考虑到这一点，一种可能的思路是，在每次插入新节点时，删除所有现有索引，并从每两个节点中抽取一个作为新索引，再逐层执行此操作。虽然这个方法概念上简单，但实际上它效率低下，并且实现起来相当复杂。

### 5.3 随机过程决定索引层级

跳表的索引构建是一个层层递进的过程。理想情况下，在原始链表中，我们每隔一个节点选择一个作为上层的索引。然后，把这一层的索引视为新的基础链表，重复同样的选择过程，直到顶层索引仅包含两个节点。

换句话说，由于任何节点都有一半的概率被选为上层的索引，一个节点出现在不同层级的概率呈逐层减半的趋势。例如，一个节点在第 1 层的出现概率是 100%，在第 2 层是 50%，在第 3 层是 25%，以此类推。

> 在跳表中，如果一个节点出现在较高层级，它必然出现在所有较低的层级。例如，一个节点若出现在第 3 层，那么它必定存在于第 2 层和第 1 层。

所以，我们可以在节点插入的时候，就通过某种随机分层机制，确定它所在的层级。

而这种机制需要保证每个节点有 100% 的概率出现在第 1 层，50% 的概率出现在第 2 层，25% 的概率出现在第 3 层，依此类推，通过这种概率分布，我们能有效地平衡跳表的层级结构和搜索效率。

下面是一个简单的算法实现，用于确定跳表中节点的层级：

```cpp
int randomLevel() {
    int level = 1;
    while (random() % 2) {
        level++;
    }
    return level;
}
```

在这个算法中，`random()` 函数每次生成一个随机数。如果这个随机数是奇数，节点的层级就增加 1；如果是偶数，循环结束并返回当前层级 level。我们可以假设 `random()` 生成的奇数和偶数的概率各为 50%。

因此，节点层级增加到 2 的概率是 50%。而层级增加到 3 的概率，即连续两次产生奇数，概率为 25%，以此类推。

根据这个算法确定的层级，我们可以将节点插入到跳表中的相应层级。例如，在下图中，我们插入了数值为 61 的节点，并且 `randomLevel()` 方法返回了 3，表示它会出现在第 1 层、第 2 层和第 3 层。

![img](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/202403011057698.png)

最后，让我们解释为什么这种方法能有效维护跳表的索引。根据大数定律，**当我们进行足够多的试验时，某个事件发生的实际频率会逐渐接近于该事件发生的理论概率**。应用到跳表中，随着节点数量的增加，我们可以合理地假设每一层的节点数量大约是下一层的一半。这是因为每个节点在每一层出现的概率都是前一层的一半。因此，通过这种方法，跳表的索引能够得到有效的维护，保持其结构和效率。

## 6. 跳表如何删除节点

理解了跳表的搜索操作与插入操作之后，删除操作也就不难理解了。此同样十分依赖于跳表的查询操作。在跳表中搜索到想要删除的节点后，需要将**该节点以及该节点的索引一并删除**。

## 7. 应用跳表的工业软件

Redis：这是最著名的使用跳表的例子。Redis 是一个开源的高性能键值存储数据库，广泛用于缓存和消息队列等场景。在 Redis 中，跳表被用于实现有序集合（sorted sets）数据类型，这主要是因为跳表在处理有序数据时可以提供良好的性能，尤其是在插入、删除和搜索操作上。

LevelDB：LevelDB 是一个由 Google 开发的快速键值存储库，用于存储非结构化数据。它使用跳表作为其内存中的数据结构，以支持快速的写入操作。跳表在 LevelDB 中帮助实现高效的数据插入和排序。

RocksDB：RocksDB 是 LevelDB 的一个分支，由 Facebook 进行了大量优化。它同样使用跳表来处理内存中的数据，以优化读写操作的性能。

Apache HBase：HBase 是一个分布式、可伸缩的大数据存储，基于 Google 的 BigTable 模型。在 HBase 中，跳表被用于实现 MemStore，即内存中的存储结构，以支持快速的数据写入和读取。

# 跳表的定义

本节将深入探讨 K-V 存储引擎实现的关键组成部分：Node 类与 SkipList 类。**Node 类的核心在于其属性**，**特别是其 forward 属性**。可以说理解了 forward 属性，就理解了整个 K-V 存储引擎底层使用数据结构 —— 跳表。

**而 SkipList 类的重点在于其提供的一系列公共成员函数**，这些函数负责组织和管理 Node 类的实例。后续的章节将围绕这些函数进行展开，详细介绍它们的实现和应用。

## 1. Node 类

### 1.1 Node 类中的关键属性

在开发一个基于跳表的 K-V 存储引擎、设计用于实际存储数据的 Node 类（节点）时，我们需要考虑以下三个因素。

> 为了明确语义以及方便叙述，后文中所有的名词「节点」都是代指 Node 类，更具体的来说是指 Node 类的实例。

1. **键值存储机制**：如何存储键和对应的值
2. **跳转机制实现**：跳表的搜索操作核心在于节点间的跳转，这如何实现
3. **层级确定**：如何确定节点存在于跳表中的哪些层级

针对上述第一点和第三点考虑因素，Node 类需要包含两个主要私有属性：key 和 value，分别用于存储键和值。此外，Node 类还有一个 node_level 公共属性，用于标识节点在跳表中的层级位置。

- 当 node_level = 1 时，表示当前的节点只会出现在跳表中的第 1 层
- 当 node_level = 2 时，表示当前的节点会出现在跳表中的第 2 层和第 1 层
- 以此类推

此时，Node 类的结构如下：

```cpp
template <typename K, typename V>
class Node {
public:
    int node_level;
private:
    K key;
    V value;
}
```

在介绍了 Node 类中负责键值存储和标识节点层次的属性之后，下文将会介绍用于支持节点间跳转机制的属性。

> 所谓跳转，指的是通过定义一种特定的指针机制，使得该指针能够以一定规则指向跳表中的各个节点。以单链表为例，其 next 指针便是一种实现节点间顺序跳转功能的关键属性。

在 “跳表简介” 章节中模拟跳表搜索部份，我们知道节点间的跳转机制可以分为两大类：

1. 同一节点的多层跳转：在相同键值、不同层级节点之间的跳转
2. 不同节点的单层跳转：在相同层级、不同键值节点之间的跳转

通过这两类跳转机制的结合，我们可以在跳表中灵活地实现不同层级和不同节点之间的跳转。

> 就像通过 x 坐标和 y 坐标结合，可以表示坐标轴内上的任意一个点一样。

那么，能够支持这两种节点间的跳转机制的属性长什么样子呢？

让我们先聚焦于第二种跳转机制：不同节点的单层跳转。**这实际上与单链表的结构相似。**

在单链表中，每个节点由两部分组成：数据域和指针域。数据域负责存储当前节点的值，而指针域则指向下一个节点，将各个单独的节点链接起来。

链表结构的实现如下：

```cpp
/**
 * 单链表结构简单示例
 */
class LinkList {
  int data;
  LinkList* next;
}
```

在单链表的结构中，可以通过访问当前节点的 next 指针，来实现从当前节点到下一个节点之间跳转的功能。这个 next 指针指向链表中的后续节点，从而使我们能够从当前节点顺利跳转到紧随其后的节点。

```cpp
// 单链表实现节点跳转的简单实现
void travasal(LinkList* listHeader) {
    LinkList* current = listHeader;
    while (current->next != nullptr) {
        current = current->next;
    }
}
```

所以，我们可以借鉴单链表中访问 next 指针的成员函数，来实现跳表内同一层级上不同节点间的跳转功能。也就是说，**节点内部用于支持跳转功能的属性，实质上是一种指针**。这个指针将会指向当前节点同一层中的后一个节点。

现在还需要解决节点跳转的第一个问题，就是节点内的该属性如何支持节点在其不同层级间的跳转呢？

到目前为止，我们可以通过 node_level 属性确定一个节点会在跳表的哪些层级出现。基于这一点，我们可以采用数组结构来组织一个节点在不同层级的指针。这意味着，用于支持两种跳转功能的属性，实际上是一个指针数组，数组其中的每个指针对应节点在一个特定层级的后继节点。**通过变更数组下标，我们便能够实现同一节点在不同层级之间的跳转功能**。这样的设计不仅保持了结构的简洁性，也为跳表提供了必要的灵活性和效率。

为了保持一致性和易于理解，我们将这个指针数组命名为 forward，这个命名方式与大多数跳表实现中的惯例相同。

最终的节点定义如下：

```cpp
template <typename K, typename V>
class Node {
public:
    Node<K, V>** forward; // 在 C++ 中，二维指针等价于指针数组 
    int node_level;
private:
    K key;
    V value;
};
```

> 假设一个节点在跳表中的层级为 3，那么这个节点的 forward 指针数组的大小为 3。其 forward[0] 指向该节点在第一层的下一个节点；forward[1] 指向该节点在第二层的下一个节点，forward[2] 指向该节点在第三层的下一个节点。

完成节点的最终定义后，我们再介绍这个结构的跳转机制是如何运作的。

**同一层级内节点的跳转：**

```cpp
/**
 * 遍历跳表的底层链表
 * current : 指向当前遍历节点的指针
 */
Node<K,V>* current = head; // 假设 head 是跳表第一层的头节点
while (current->forward[0] != nullptr) {
    // 通过迭代的方式，实现同一层内的不同节点之间的跳转
    current = current->forward[0];
}
```

**不同层级内同一节点的跳转：**

```cpp
/**
 * 同一个节点，不同层级之间的跳转
 * node : 当前节点
 * n : 节点所在的最高层级
 */
Node<K,V>* node; // 假设 node 是当前节点
int n = node->forward.size(); // 假设 forward 是动态数组
for (int i = n - 1; i >= 0; i--) {
    // 通过变更数组下标进行同一个节点在不同层级之间的跳转
    Node<K,V>* current = node->forward[i];
}
```

### 1.2 Node 类的代码实现

在定义完毕 Node 类关键的属性之后，还需要一些基本的问题需要处理。例如获取 / 设置key 对应的 value、构造函数的实现、析构函数的实现等。由于相对简单，就不做过多的介绍，以下是详细实现。

```cpp
template <typename K, typename V>
class Node {
public:
    Node() {}
    Node(K k, V v, int);
    ~Node();
    K get_key() const;
    V get_value() const;
    void set_value(V);
    Node<K, V> **forward;
    int node_level;
private:
    K key;
    V value;
};

template <typename K, typename V>
Node<K, V>::Node(const K k, const V v, int level) {
    this->key = k;
    this->value = v;
    this->node_level = level;
    this->forward = new Node<K, V> *[level + 1];
    memset(this->forward, 0, sizeof(Node<K, V> *) * (level + 1));
};

template <typename K, typename V>
Node<K, V>::~Node() {
    delete[] forward;
};

template <typename K, typename V>
K Node<K, V>::get_key() const {
    return key;
};

template <typename K, typename V>
V Node<K, V>::get_value() const {
    return value;
};

template <typename K, typename V>
void Node<K, V>::set_value(V value) {
    this->value = value;
};
```

## 2. SkipList 类

在确定了具体用于存储键值对的 Node 类之后，现在我们需要设计一个能组织和管理存储引擎 Node 类的 SkipList 类。

### 2.1 SkipList 属性

1. 头节点：作为跳表中所有节点组织的入口点，类似于单链表
2. 最大层数：跳表中允许的最大层数
3. 当前层数：跳表当前的层数
4. 节点数量：跳表当前的组织的所有节点总数
5. 文件读写：跳表生成持久化文件和读取持久化文件的写入器和读取器

具体定义如下：

```cpp
template <typename K, typename V>
class SkipList {
private:
    int _max_level;              // 跳表允许的最大层数
    int _skip_list_level;        // 跳表当前的层数
    Node<K, V> *_header;         // 跳表的头节点
    int _element_count;          // 跳表中组织的所有节点的数量
    std::ofstream _file_writer;  // 文件写入器
    std::ifstream _file_reader;  // 文件读取器
};
```

### 2.2 SkipList 成员函数

在定义完毕 SkipList 类的关键属性后，我们还需要设计出组织和管理 Node 类的成员函数。

核心成员函数：

1. 节点创建：生成新的节点实例
2. 层级分配：为每个新创建的节点分配一个合适的层数
3. 节点插入：将节点加入到跳表中的适当位置
4. 节点搜索：在跳表中查找特定的节点
5. 节点删除：从跳表中移除指定的节点
6. 节点展示：显示跳表中所有节点的信息
7. 节点计数：获取跳表中当前的节点总数
8. 数据持久化：将跳表的数据保存到磁盘中
9. 数据加载：从磁盘加载持久化的数据到跳表中
10. 垃圾回收：对于删除的节点，需要回收其内存空间
11. 获取节点数量：获取跳表组织的节点个数

接口的具体代码如下：

```cpp
template <typename K, typename V>
class SkipList {
public:
    SkipList(int);                      // 构造函数
    ~SkipList();                        // 析构函数
    int get_random_level();             // 获取节点的随机层级
    Node<K, V> *create_node(K, V, int); // 节点创建
    int insert_element(K, V);           // 插入节点
    void display_list();                // 展示节点
    bool search_element(K);             // 搜索节点
    void delete_element(K);             // 删除节点
    void dump_file();                   // 持久化数据到文件
    void load_file();                   // 从文件加载数据
    void clear(Node<K, V> *);           // 递归删除节点
    int size();                         // 跳表中的节点个数
private:
    // ...
};
```

在定义完毕 SkipList 类中的属性和成员函数之后，**后续的章节内容就是实现上述的各个函数**。

## 3. 题解（可提交）

题目要求我们实现一个 Node 类，用于表示跳表中的节点。

Node 类的定义如下，这是本存储引擎项目中拥有完整功能的类，在定义完毕之后，我们分别实现 Node 类的构造函数，析构函数，获取值，设置值等成员函数。

```cpp
#include <iostream>
#include <cstdlib>
#include <cmath>
#include <cstring>

// 定义节点
template <typename K, typename V>
class Node {
public:
    Node() {}
    Node(K k, V v, int);
    ~Node();
    K get_key() const;
    V get_value() const;
    void set_value(V);
    Node<K, V> **forward;
    int node_level;
private:
    K key;
    V value;
};

// 类拥有的构造函数
template <typename K, typename V>
Node<K, V>::Node(const K k, const V v, int level) {
    this->key = k;
    this->value = v;
    this->node_level = level;
    this->forward = new Node<K, V> *[level + 1];
    memset(this->forward, 0, sizeof(Node<K, V> *) * (level + 1));
};

// 类拥有的析构函数
template <typename K, typename V>
Node<K, V>::~Node() {
    delete[] forward;
};

// 类拥有的获取 key 成员函数
template <typename K, typename V>
K Node<K, V>::get_key() const {
    return key;
};

// 类拥有的获取 value 成员函数
template <typename K, typename V>
V Node<K, V>::get_value() const {
    return value;
};

// 类拥有的设置 value 成员函数
template <typename K, typename V>
void Node<K, V>::set_value(V value) {
    this->value = value;
};

int main() {
    int K, V, L;  // 定义变量
    std::cin >> K >> V >> L;  // 获取变量
    // 创造对应的类
    Node<int, int> *node = new Node<int, int>(K, V, L);
    // 调用 get_key 成员函数和 set 成员函数
    std::cout << node->get_key() << " " << node->get_value() << std::endl;
    // 释放内存
    delete node;
    return 0;
}
```

# 跳表的层级

通过之前的简介，我们已经了解到跳表是一种极为高效的数据结构，其独特之处在于节点层级的设定，这一层级是通过一个随机过程来选择的。为了实现这一过程，我们设计了一个专门的成员函数，通过该函数，可以在跳表中实现随机层级的选择。

## 1. 随机层级的选择过程

想象你在玩抛硬币游戏，决定你在游戏中可以前进多远：

1. 起点：每当添加一个新元素，从地面层（即跳表的最底层，第0层）开始
2. 抛硬币决定层级：
    - 正面：向上升一层并继续抛硬币
    - 反面：停止升层，确定当前层级作为元素的最终层级
3. **重复过程**：持续此过程直至得到反面为止

这个随机过程的结果是：

许多元素会停留在较低层级，一部分元素会到达较高层级，极少数元素可能会到达非常高的层级。

## 2. 为什么采用随机过程

- 平衡性：随机层级分配自然保持跳表平衡，无需额外操作（如AVL或红黑树的旋转）
- 效率：随机分配层级保证节点在各层均匀分布，实现对数时间复杂度的查找、插入和删除
- 简单性：这种方法易于实现且效果显著，使跳表成为性能优异的简洁数据结构

来看具体代码的实现：

```cpp
template <typename K, typename V>
int SkipList<K, V>::get_random_level() {
   // 初始化层级：每个节点至少出现在第一层。
   int k = 1;
   // 随机层级增加：使用 rand() % 2 实现抛硬币效果，决定是否升层。
   while (rand() % 2) {
      k++;
   }
   // 层级限制：确保节点层级不超过最大值 _max_level。
   k = (k < _max_level) ? k : _max_level;
   // 返回层级：返回确定的层级值，决定节点插入的层。
   return k;
};
```

相比于前面的跳表简介一节，这一节我们的随机过程的实现方式中多了一行代码。

```cpp
k = (k < _max_level) ? k : _max_level;
```

这是因为在具体的实现中，我们的跳表有一个最大层级限制，限制了索引的最高层，所以这里额外添加一行代码对随机生成的层级进行限制。

这个函数通过简单的随机过程（模拟抛硬币），以概率方式决定节点的层级，同时确保层级不会超过设定的最大值。这种随机层级分配策略有助于保持跳表的性能，确保操作（如搜索、插入、删除）的时间复杂度在平均情况下接近 O(log n)。

# 跳表的插入

本文将正式介绍跳表的创建和搜索、插入操作几个核心部分：

**1、创建跳表**

我们将从基础开始，介绍如何创建跳表的方法。

**2、实现搜索方法**

详细介绍跳表中如何实现搜索操作。

**3、实现插入方法**

解析跳表中插入新节点的过程，包括如何通过随机过程函数，比如 get_random_level()，决定新插入节点的层级，以及如何搜索到合适的位置进行节点插入。

**4、题解**

## 1. 创建跳表

下面是跳表的基础代码框架，仅仅包括本节内容中必要的类定义和成员函数，其余内容为了保证篇幅长度均已省略：

```cpp
#include <iostream>
#include <cstdlib>
#include <cmath>
#include <cstring>

// 节点类定义
template <typename K, typename V>
class Node {
    // 节点类成员变量和方法（省略）
};

// 跳表类定义
template <typename K, typename V>
class SkipList {
public:
    SkipList(int);  // 构造函数
    ~SkipList();  // 析构函数
    int get_random_level();  // 生成随机层级
    Node<K, V> *create_node(K, V, int);  // 创建新节点
    int insert_element(K, V);  // 插入元素
    bool search_element(K);  // 搜索元素
    // 其他成员变量和函数（省略）
private:
    int _max_level;  // 最大层级
    int _skip_list_level;  // 当前层级
    Node<K, V> *_header;  // 头节点
    // 其他私有成员（省略）
    int _element_count;  // 节点数量
};
```

跳表的构造函数负责初始化跳表，主要包括以下步骤：

1. 设置最大层级：根据预设值确定跳表的最大层级
2. 初始化成员变量：设置跳表当前层级为 0，节点计数为 0
3. 创建头节点：初始化一个头节点，其层级等于跳表的最大层级

具体代码如下：

```cpp
template <typename K, typename V>
SkipList<K, V>::SkipList(int max_level) {
    this->_max_level = max_level;  // 设置最大层级
    this->_skip_list_level = 0;    // 初始化当前层级为 0
    this->_element_count = 0;      // 初始化节点计数为 0
    K k;  // 默认键
    V v;  // 默认值
    // 创建头节点，并初始化键值为默认值
    this->_header = new Node<K, V>(k, v, _max_level);
};
```

完成跳表的初始化之后，接下来的环节是实现节点创建的方法。

创建新节点的过程涉及以下主要步骤：

1. 节点实例化：依据提供的键（k）和值（v），创建一个新的节点实例。同时，为这个新节点指定一个层级（level），这一层级决定了节点在跳表中的高度
2. 返回新节点：完成节点的创建后，返回这个新创建的节点实例，以便于进一步在跳表中进行插入操作。

具体代码如下：

```cpp
/**
 * 创建一个新节点
 * @param k 节点的键
 * @param v 节点的值
 * @param level 节点的层级
 * @return 新创建的节点指针
 */
template <typename K, typename V>
Node<K, V> *SkipList<K, V>::create_node(const K k, const V v, int level) {
    // 实例化新节点，并为其分配指定的键、值和层级
    Node<K, V> *n = new Node<K, V>(k, v, level);
    return n; // 返回新创建的节点
}
```

## 2. 实现搜索方法

### 2.1 理论基础

完成跳表的创建之后，让我们先了解跳表的搜索方法，因为后续的插入方法和删除方法都依赖于搜索方法。

我们之前已经简要介绍过跳表的搜索机制。搜索开始于跳表的顶层，这一点在我们的 SkipList 类中通过变量 _skip_list_level 得到体现，该变量记录了跳表当前的最高层级。

并且在 “跳表的定义” 章节中，我们曾经介绍过，每个节点都维护一个 forward 数组，该数组记录了**该节点在每一层的下一个节点的指针**。

> _header 作为跳表的头节点，为操作跳表提供了一个统一的入口。跳表的本质是由原始链表经过筛选部分节点构建成的多级索引链表。因此，跳表可视为多个层级的单链表组合而成。在单链表结构中，通常会有一个头节点，其 next 指针指向链表的第一个实际节点。相应地，对于多层级的跳表结构，我们需要多个头节点来指向各层的第一个节点。这些头节点被存储在 _header 节点的 forward 数组中。例如，_header->forward[0] 指向最底层的第一个节点，_header->forward[1] 指向第二层的第一个节点，依此类推。

基于这个结构，利用 _header 节点和 _skip_list_level（记录跳表实际最高层级的变量）作为起点，我们可以从跳表的最顶层开始进行搜索。

### 2.2 代码实现

以下是拥有详细注释的搜索方法代码：

```cpp
/**
 * 搜索指定的键值是否存在于跳表中。
 * @param key 待查找的键值
 * @return 如果找到键值，返回 true；否则返回 false。
 */
template <typename K, typename V>
bool SkipList<K, V>::search_element(K key) {
    // 定义一个指针 current，初始化为跳表的头节点 _header
    Node<K, V> *current = _header;
    // 从跳表的最高层开始搜索
    for (int i = _skip_list_level; i >= 0; i--) {
        // 遍历当前层级，直到下一个节点的键值大于或等于待查找的键值
        while (current->forward[i] && current->forward[i]->get_key() < key) {
            // 移动到当前层的下一个节点
            current = current->forward[i];
        }
        // 当前节点的下一个节点的键值大于待查找的键值时，进行下沉到下一层
        // 下沉操作通过循环的 i-- 实现
    }
    // 检查当前层（最底层）的下一个节点的键值是否为待查找的键值
    current = current->forward[0];
    if (current && current->get_key() == key) {
        // 如果找到匹配的键值，返回 true
        return true;
    }
    // 如果没有找到匹配的键值，返回 false
    return false;
}
```

## 3. 实现插入方法

### 3.1 理论基础

继搜索节点的逻辑之后，我们现在转向如何在跳表中插入新节点。

插入过程主要涉及三个关键步骤：

**1、确定节点层级**

首先，我们需要为新插入的节点随机确定其所在的层级

**2、寻找插入位置**

通过之前讨论的搜索方法，我们能够定位到了新节点应当插入的具体位置

**3、更新指针关系**

最关键的步骤是在插入节点时更新各层的指针关系。

具体而言，这包括两个方面：

1. 将新节点在各层的前驱节点（即在该层中小于新节点且最接近新节点的节点）的 forward 指针指向新节点。
2. 同时，新节点的 forward 指针需要指向其在各层的前驱节点原本指向的节点。

此操作和单链表的插入操作类似，区别在于跳表需要在多层中的重复进行此操作，而链表只需要进行一次。

### 3.2 代码实现

在插入新节点前，我们首先需要定位插入位置，此过程与 search_element 函数的逻辑相似。下面的代码框架展示了如何执行这一操作：

```cpp
/**
 * 在跳表中插入一个新元素。
 * @param key 待插入节点的 key
 * @param value 待插入节点的 value
 * @return 如果元素已存在，返回 1；否则，进行更新 value 操作并返回 0。
 */
template <typename K, typename V>
int SkipList<K, V>::insert_element(const K key, const V value) {
    Node<K, V> *current = this->_header;
    // 用于在各层更新指针的数组
    Node<K, V> *update[_max_level + 1];  // 用于记录每层中待更新指针的节点
    memset(update, 0, sizeof(Node<K, V> *) * (_max_level + 1));

    // 从最高层向下搜索插入位置
    for (int i = _skip_list_level; i >= 0; i--) {
        // 寻找当前层中最接近且小于 key 的节点
        while (current->forward[i] != NULL && current->forward[i]->get_key() < key) {
            current = current->forward[i]; // 移动到下一节点
        }
        // 保存每层中该节点，以便后续插入时更新指针
        update[i] = current;
    }

    // 移动到最底层的下一节点，准备插入操作
    current = current->forward[0];
    // 检查待插入的节点的键是否已存在
    if (current != NULL && current->get_key() == key) {
        // 键已存在，取消插入
        return 1;
    }
    // 后续插入操作（略）
}
```

在这段代码中，`Node<K, V>* update[_max_level + 1]` 是用于实现插入节点的关键数据结构，它是一个节点指针数组，用于记录在上文中提到的，待插入节点的前驱节点（即在该层中小于新节点且最接近新节点的节点）。这个数组解决了之前提到的关键问题：在插入新节点时如何更新每层的指针关系。

通过内层的 while 循环，一旦发现 current->forward[i] 指向的节点的 key 值 > 待插入节点的 key，那么 current 就是待插入节点的前驱节点。而通过外层的 for 循环，我们可以寻找出待插入节点在不同层的所有前驱节点。

接下来的判断逻辑是为了确保不会插入重复的节点。如果 current 指向的节点的 key 与待插入的节点的 key 相等，说明跳表中已存在与待插入节点相同 key 的节点，此时我们只需要将该节点的 value 更新，并且返回 1；

继续深入跳表的插入逻辑，以下是插入操作的代码实现：

```cpp
/**
 * 在跳表中插入一个新元素。
 * @param key 新元素的键。
 * @param value 新元素的值。
 * @return 如果元素已存在，返回 1；否则，进行插入操作并返回 0。
 */
template <typename K, typename V>
int SkipList<K, V>::insert_element(const K key, const V value) {
    // ...
    // 检查待插入的节点是否已存在于跳表中
    if (current == NULL || current->get_key() != key) {
        // 通过随机函数决定新节点的层级高度
        int random_level = get_random_level();
        // 如果新节点的层级超出了跳表的当前最高层级
        if (random_level > _skip_list_level) {
            // 对所有新的更高层级，将头节点设置为它们的前驱节点
            for (int i = _skip_list_level + 1; i <= random_level; i++) {
                update[i] = _header;
            }
            // 更新跳表的当前最高层级为新节点的层级
            _skip_list_level = random_level;
        }
        
        Node<K, V> *inserted_node = create_node(key, value, random_level);
        // 在各层插入新节点，同时更新前驱节点的forward指针
        for (int i = 0; i <= random_level; i++) {
            // 新节点指向当前节点的下一个节点
            inserted_node->forward[i] = update[i]->forward[i];
            // 当前节点的下一个节点更新为新节点
            update[i]->forward[i] = inserted_node;
        }
        _element_count++;
    }
    return 0;
}
```

当新插入节点的层级高于跳表当前层级时，我们需要在 update 数组中为这些新层级指定头节点（_header），因为这些层级在插入之前是不存在节点的。这样，新节点在这些高层级直接作为第一个节点。

新节点按照确定的层级被插入。对每一层，我们首先设置新节点的 forward 指针指向当前节点的下一个节点，然后更新当前节点的 forward 指针指向新节点。这一过程确保了新节点正确地被链入每一层。

通过这些步骤，我们不仅完成了新节点的插入操作，还确保了跳表结构的正确性和索引的有效维护。

### 3.3 完整代码与解释

```cpp
/**
 * 在跳表中插入一个新元素。
 * @param key 新元素的键。
 * @param value 新元素的值。
 * @return 如果元素已存在，返回 1；否则，进行插入操作并返回 0。
 */
template <typename K, typename V>
int SkipList<K, V>::insert_element(const K key, const V value) {
        Node<K, V> *current = this->_header;
    // 用于在各层更新指针的数组
    Node<K, V> *update[_max_level + 1];  // 用于记录每层中待更新指针的节点
    memset(update, 0, sizeof(Node<K, V> *) * (_max_level + 1));

    // 从最高层向下搜索插入位置
    for (int i = _skip_list_level; i >= 0; i--) {
        // 寻找当前层中最接近且小于 key 的节点
        while (current->forward[i] != NULL && current->forward[i]->get_key() < key) {
            current = current->forward[i]; // 移动到下一节点
        }
        // 保存每层中该节点，以便后续插入时更新指针
        update[i] = current;
    }

    // 移动到最底层的下一节点，准备插入操作
    current = current->forward[0];
    // 检查待插入的键是否已存在
    if (current != NULL && current->get_key() == key) {
        // 键已存在，取消插入
        return 1;
    }
    // 检查待插入的键是否已存在于跳表中
    if (current == NULL || current->get_key() != key) {
        // 通过随机函数决定新节点的层级高度
        int random_level = get_random_level();
        // 如果新节点的层级超出了跳表的当前最高层级
        if (random_level > _skip_list_level) {
            // 对所有新的更高层级，将头节点设置为它们的前驱节点
            for (int i = _skip_list_level + 1; i <= random_level; i++) {
                update[i] = _header;
            }
            // 更新跳表的当前最高层级为新节点的层级
            _skip_list_level = random_level;
        }
        
        Node<K, V> *inserted_node = create_node(key, value, random_level);
        // 在各层插入新节点，同时更新前驱节点的 forward 指针
        for (int i = 0; i <= random_level; i++) {
            // 新节点指向当前节点的下一个节点
            inserted_node->forward[i] = update[i]->forward[i];
            // 当前节点的下一个节点更新为新节点
            update[i]->forward[i] = inserted_node;
        }
        _element_count++;
    }
    return 0;
}
```

## 4. 题解

本题完整的代码结构如下：

```cpp
#include <iostream>
#include <cstdlib>
#include <cmath>
#include <cstring>

template <typename K, typename V>
class Node {
public:
    Node() {}
    Node(K k, V v, int);
    ~Node();
    K get_key() const;
    V get_value() const;
    void set_value(V);
    Node<K, V> **forward;
    int node_level;
private:
    K key;
    V value;
};

template <typename K, typename V>
Node<K, V>::Node(const K k, const V v, int level) {
    this->key = k;
    this->value = v;
    this->node_level = level;
    this->forward = new Node<K, V> *[level + 1];
    memset(this->forward, 0, sizeof(Node<K, V> *) * (level + 1));
};

template <typename K, typename V>
Node<K, V>::~Node() {
    delete[] forward;
};

template <typename K, typename V>
K Node<K, V>::get_key() const {
    return key;
};

template <typename K, typename V>
V Node<K, V>::get_value() const {
    return value;
};

template <typename K, typename V>
void Node<K, V>::set_value(V value) {
    this->value = value;
};

// 跳表结构
template <typename K, typename V>
class SkipList {
public:
    SkipList(int);
    int get_random_level();
    Node<K, V> *create_node(K, V, int);
    int insert_element(K, V);
    bool search_element(K);
private:
    int _max_level;
    int _skip_list_level;
    Node<K, V> *_header;
    int _element_count;
};

template <typename K, typename V>
Node<K, V> *SkipList<K, V>::create_node(const K k, const V v, int level) {
    Node<K, V> *n = new Node<K, V>(k, v, level);
    return n;
}

template <typename K, typename V>
int SkipList<K, V>::insert_element(const K key, const V value) {
    Node<K, V> *current = this->_header;
    Node<K, V> *update[_max_level + 1];
    memset(update, 0, sizeof(Node<K, V> *) * (_max_level + 1));
    for (int i = _skip_list_level; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->get_key() < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }
    current = current->forward[0];
    if (current != NULL && current->get_key() == key) {
        return 1;
    }
    if (current == NULL || current->get_key() != key) {
        int random_level = get_random_level();
        if (random_level > _skip_list_level) {
            for (int i = _skip_list_level + 1; i < random_level + 1; i++) {
                update[i] = _header;
            }
            _skip_list_level = random_level;
        }
        Node<K, V> *inserted_node = create_node(key, value, random_level);
        for (int i = 0; i <= random_level; i++) {
            inserted_node->forward[i] = update[i]->forward[i];
            update[i]->forward[i] = inserted_node;
        }
        _element_count++;
    }
    return 0;
}

template <typename K, typename V>
bool SkipList<K, V>::search_element(K key) {
    Node<K, V> *current = _header;
    for (int i = _skip_list_level; i >= 0; i--)
    {
        while (current->forward[i] && current->forward[i]->get_key() < key) {
            current = current->forward[i];
        }
    }
    current = current->forward[0];
    if (current and current->get_key() == key) {
        return true;
    }
    return false;
}

template <typename K, typename V>
SkipList<K, V>::SkipList(int max_level) {
    this->_max_level = max_level;
    this->_skip_list_level = 0;
    this->_element_count = 0;
    K k;
    V v;
    this->_header = new Node<K, V>(k, v, _max_level);
};

template<typename K, typename V>
int SkipList<K, V>::get_random_level(){
    int k = 1;
    while (rand() % 2) {
        k++;
    }
    k = (k < _max_level) ? k : _max_level;
    return k;
};

int main() {
    int N;
    int M;
    SkipList<int, int> *skip_list = new SkipList<int, int>(16);
    std::cin >> N >> M;
    for (int i = 0; i < N; i++) {
        int key;
        int value;
        std::cin >> key >> value;
        if (skip_list->insert_element(key, value) == 0) {
            std::cout << "Insert Success" << std::endl;
        } else {
            std::cout << "Insert Failed" << std::endl;
        }
    }

    // 搜索
    for (int i = 0; i < M; i++) {
        int key;
        std::cin >> key;
        if (skip_list->search_element(key)) {
            std::cout << "Search Success" << std::endl;
        } else {
            std::cout << "Search Failed" << std::endl;
        }
    }
    return 0;
}
```

# 跳表的删除

## 1. 删除跳表中的节点

### 1.1 理论基础

删除操作是跳表功能的重要组成部分。

它涉及以下几个关键步骤：

1. 定位待删除节点：通过搜索确定需要删除的节点位置
2. 更新指针关系：调整相关节点的指针，以从跳表中移除目标节点
3. 内存回收：释放被删除节点所占用的资源

### 1.2 代码实现

删除操作首先需要定位到待删除的节点，这一过程与 search_element 和 insert_element 函数类似。

此外，我们同样使用 update 数组记录每层待删除节点的前驱节点，以便更新指针关系。

具体实现如下：

```cpp
/**
 * 删除跳表中的节点
 * @param key 待删除节点的 key 值
*/
template <typename K, typename V>
void SkipList<K, V>::delete_element(K key) {
    Node<K, V> *current = this->_header;
    Node<K, V> *update[_max_level + 1];
    memset(update, 0, sizeof(Node<K, V> *) * (_max_level + 1));

    // 从最高层开始向下搜索待删除节点
    for (int i = _skip_list_level; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->get_key() < key) {
            current = current->forward[i];
        }
        update[i] = current; // 记录每层待删除节点的前驱
    }

    current = current->forward[0];
    // 确认找到了待删除的节点
    if (current != NULL && current->get_key() == key) {
        // 逐层更新指针，移除节点
        for (int i = 0; i <= _skip_list_level; i++) {
            if (update[i]->forward[i] != current) break;
            update[i]->forward[i] = current->forward[i];
        }
        // 调整跳表的层级
        while (_skip_list_level > 0 && _header->forward[_skip_list_level] == NULL) {
            _skip_list_level--;
        }
        delete current; // 释放节点占用的内存
        _element_count--; // 节点计数减一
    }
    return;
}
```

## 2. 题解

在处理跳表的删除操作时，我们依赖于之前实现的 search_element 和 insert_element 函数。

完整的代码如下：

```cpp
#include <iostream>
#include <cstdlib>
#include <cmath>
#include <cstring>

template <typename K, typename V>
class Node {
public:
    Node() {}
    Node(K k, V v, int);
    ~Node();
    K get_key() const;
    V get_value() const;
    void set_value(V);
    Node<K, V> **forward;
    int node_level;
private:
    K key;
    V value;
};

template <typename K, typename V>
Node<K, V>::Node(const K k, const V v, int level) {
    this->key = k;
    this->value = v;
    this->node_level = level;
    this->forward = new Node<K, V> *[level + 1];
    memset(this->forward, 0, sizeof(Node<K, V> *) * (level + 1));
};

template <typename K, typename V>
Node<K, V>::~Node() {
    delete[] forward;
};

template <typename K, typename V>
K Node<K, V>::get_key() const {
    return key;
};

template <typename K, typename V>
V Node<K, V>::get_value() const {
    return value;
};

template <typename K, typename V>
void Node<K, V>::set_value(V value) {
    this->value = value;
};

// 跳表结构
template <typename K, typename V>
class SkipList {
public:
    SkipList(int);
    int get_random_level();
    Node<K, V> *create_node(K, V, int);
    int insert_element(K, V);
    bool search_element(K);
    void delete_element(K);
private:
    int _max_level;
    int _skip_list_level;
    Node<K, V> *_header;
    int _element_count;
};

template <typename K, typename V>
Node<K, V> *SkipList<K, V>::create_node(const K k, const V v, int level) {
    Node<K, V> *n = new Node<K, V>(k, v, level);
    return n;
}

template <typename K, typename V>
int SkipList<K, V>::insert_element(const K key, const V value) {
    Node<K, V> *current = this->_header;
    Node<K, V> *update[_max_level + 1];
    memset(update, 0, sizeof(Node<K, V> *) * (_max_level + 1));
    for (int i = _skip_list_level; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->get_key() < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }
    current = current->forward[0];
    if (current != NULL && current->get_key() == key) {
        return 1;
    }
    if (current == NULL || current->get_key() != key) {
        int random_level = get_random_level();
        if (random_level > _skip_list_level) {
            for (int i = _skip_list_level + 1; i < random_level + 1; i++) {
                update[i] = _header;
            }
            _skip_list_level = random_level;
        }
        Node<K, V> *inserted_node = create_node(key, value, random_level);
        for (int i = 0; i <= random_level; i++) {
            inserted_node->forward[i] = update[i]->forward[i];
            update[i]->forward[i] = inserted_node;
        }
        _element_count++;
    }
    return 0;
}

template <typename K, typename V>
bool SkipList<K, V>::search_element(K key) {
    Node<K, V> *current = _header;
    for (int i = _skip_list_level; i >= 0; i--)
    {
        while (current->forward[i] && current->forward[i]->get_key() < key) {
            current = current->forward[i];
        }
    }
    current = current->forward[0];
    if (current and current->get_key() == key) {
        return true;
    }
    return false;
}

template <typename K, typename V>
void SkipList<K, V>::delete_element(K key) {
    Node<K, V> *current = this->_header;
    Node<K, V> *update[_max_level + 1];
    memset(update, 0, sizeof(Node<K, V> *) * (_max_level + 1));

    for (int i = _skip_list_level; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->get_key() < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }

    current = current->forward[0];
    if (current != NULL && current->get_key() == key) {
        for (int i = 0; i <= _skip_list_level; i++) {
            if (update[i]->forward[i] != current)
                break;
            update[i]->forward[i] = current->forward[i];
        }
        while (_skip_list_level > 0 && _header->forward[_skip_list_level] == 0) {
            _skip_list_level--;
        }
        delete current;
        _element_count--;
    }
    return;
}

template <typename K, typename V>
SkipList<K, V>::SkipList(int max_level) {
    this->_max_level = max_level;
    this->_skip_list_level = 0;
    this->_element_count = 0;
    K k;
    V v;
    this->_header = new Node<K, V>(k, v, _max_level);
};

template<typename K, typename V>
int SkipList<K, V>::get_random_level(){
    int k = 1;
    while (rand() % 2) {
        k++;
    }
    k = (k < _max_level) ? k : _max_level;
    return k;
};

int main() {
    int N, K, M;

    std::cin >> N >> K >> M;

    SkipList<int, int> *skiplist = new SkipList<int, int>(16);

    // 插入数据
    for (int i = 0; i < N; i++) {
        int k, v;
        std::cin >> k >> v;
        if (skiplist->insert_element(k, v) == 0) {
            std::cout << "Insert Success" << std::endl;
        } else {
            std::cout << "Insert Failed" << std::endl;
        }
    }

    // 删除数据
    for (int i = 0; i < K; i++) {
        int k;
        std::cin >> k;
        skiplist->delete_element(k);
    }

    // 查找数据
    for (int i = 0; i < M; i++) {
        int k;
        std::cin >> k;
        if (skiplist->search_element(k)) {
            std::cout << "Search Success" << std::endl;
        } else {
            std::cout << "Search Failed" << std::endl;
        }
    }
    return 0;
}
```

# 跳表的展示

在完成跳表的节点插入和搜索功能后，展示跳表的结构成为了下一个重要的任务。这不仅有助于理解跳表的工作原理，也是验证实现正确性的一个有效手段。

## 1. 理论基础

跳表的结构本质上是一个通过对原始链表的部分节点进行筛选而构建的多级索引链表，可以视为多个层级的单链表的组合。

跳表的每一层都有一个头节点，通过这些头节点可以访问到该层的所有节点。我们首先遍历这些头节点，从而实现对每一层的访问。

## 2. 代码实现

为了遍历跳表的每一层，我们利用跳表的头节点数组_header，其中_header[i]代表第i层的头节点。通过以下代码，我们可以实现对每一层头节点的遍历：

```cpp
for (int i = 0; i <= _skip_list_level; i++) {
    Node<K, V> *node = _header->forward[i];
}
```

在获取到每一层的头节点后，我们通过迭代的方式遍历该层的所有节点，并打印出节点中的键和值：

```cpp
while (node != NULL) {
    std::cout << node->get_key() << ":" << node->get_value() << ";";
}
```

将上述步骤综合起来，我们得到了展示跳表内容的完整方法：

```cpp
template <typename K, typename V>
void SkipList<K, V>::display_list() {
    // 从最上层开始向下遍历所有层
    for (int i = _skip_list_level; i >= 0; i--) {
        Node<K, V>* node = this->_header->forward[i]; // 获取当前层的头节点
        std::cout << "Level " << i << ": ";
        // 遍历当前层的所有节点
        while (node != nullptr) {
            // 打印当前节点的键和值，键值对之间用":"分隔
            std::cout << node->get_key() << ":" << node->get_value() << ";";
            // 移动到当前层的下一个节点
            node = node->forward[i];
        }
        std::cout << std::endl; // 当前层遍历结束，换行
    }
}
```

# 生成和读取持久化文件

作为核心的存储引擎功能，数据的持久化保存与高效读取是至关重要的。

## 1. 数据的保存

在之前的章节中，我们介绍了如何在存储引擎中实现数据的搜索、插入和删除操作。这些操作都是在内存中进行的，意味着一旦程序终止，所有的数据就会丢失。因此，实现数据的持久化保存变得尤为重要。

考虑到键值对数据结构的特点，我们选择将数据保存到文件中，采用 key:value 格式进行存储，每行存储一个键值对。这种格式既简单又易于解析，适合快速的数据存取。

目标文件结构如下：

```txt
1:store
2:engine
3:text
```

在 C++ 中，我们利用 std::ofstream 来打开文件、写入数据，并在数据写入完成后关闭文件。

实现代码：

```cpp
template <typename K, typename V>
void SkipList<K, V>::dump_file() {
    _file_writer.open(STORE_FILE); // 打开文件
    Node<K, V>* node = this->_header->forward[0]; // 从头节点开始遍历

    while (node != nullptr) {
        _file_writer << node->get_key() << ":" << node->get_value() << ";\n"; // 写入键值对
        node = node->forward[0]; // 移动到下一个节点
    }

    _file_writer.flush(); // 刷新缓冲区，确保数据完全写入
    _file_writer.close(); // 关闭文件
}
```

> STORE_FILE 是代码中定义的一个路径

## 2. 数据的读取

数据持久化之后，下一步就是实现其读取过程。在这个过程中，我们面临两个挑战：一是如何将文件中的key:value字符串解析为键值对；二是如何将读取的数据插入到内存中的跳表并建立索引。

我们首先需要定义一个工具函数，用于验证字符串的合法性。这包括检查字符串是否为空，以及是否包含分隔符:。

```cpp
template <typename K, typename V>
bool SkipList<K, V>::is_valid_string(const std::string& str) {
    return !str.empty() && str.find(delimiter) != std::string::npos;
}
```

验证字符串合法性后，我们将字符串分割为键和值。

```cpp
template <typename K, typename V>
void SkipList<K, V>::get_key_value_from_string(const std::string& str, std::string* key, std::string* value) {
    if (!is_valid_string(str)) {
        return;
    }
    *key = str.substr(0, str.find(delimiter));
    *value = str.substr(str.find(delimiter) + 1);
}
```

有了上述工具函数，我们可以继续实现从磁盘加载数据到跳表的过程。

在对字符串进行校验了之后，此时我们就需要将磁盘中 key:value 串转换成内存中的 key 和 value 了。

通过使用 std::string::substr 函数，我们可以将字符串切片，得到我们想要的 key 和 value。

```cpp
template <typename K, typename V>
void SkipList<K, V>::get_key_value_from_string(const std::string &str, std::string *key, std::string *value) {
    if (!is_valid_string(str)) {
        return;
    }
    *key = str.substr(0, str.find(delimiter));
    *value = str.substr(str.find(delimiter) + 1, str.length());
}
```

写完所需的工具函数之后，下一步就是具体的操作了。

```cpp
// Load data from disk
template <typename K, typename V>
void SkipList<K, V>::load_file() {
    _file_reader.open(STORE_FILE);
    std::string line;
    std::string *key = new std::string();
    std::string *value = new std::string();

    while (getline(_file_reader, line)) {
        get_key_value_from_string(line, key, value);
        if (key->empty() || value->empty()) {
            continue;
        }
        // Define key as int type
        insert_element(stoi(*key), *value);
        std::cout << "key:" << *key << "value:" << *value << std::endl;
    }

    delete key;
    delete value;
    _file_reader.close();
}
```

这段代码展示了如何将数据从磁盘读取并恢复到跳表中，同时建立必要的索引，以保持存储引擎的效率和响应性。

## 3. 题解

将上述代码整合到一起后，可在本地进行运行检查，最终文件中的内容应该为如下格式：

```text
key1:value1
key2:value2
...
key3:value3
```

# 模块合并

通过前面的章节，我们已经将本 K-V 存储引擎拆分成的多个模块分别都介绍完了，但是会有一部份的内容没有涉及到，例如在跳表插入和删除数据的过程中，没有进行加锁，在多线程的情况下，可能会出现数据不一致的问题等。

现在我们将之前所有模块合并，同时补齐那些没有涉及到的内容。

不过因为篇幅原因，会有一部份的函数实现会省略，可以到 GitHub 上查看完整代码。

[K-V 存储引擎项目地址](https://github.com/youngyangyang04/SkipList-CPP)

合并过程：

- 创建一个 skiplist.h 文件
- 添加需要的头文件

```cpp
#include <iostream>
#include <cstdlib>  // 随机函数
#include <cmath>
#include <cstring>
#include <mutex>    // 引入互斥锁
#include <fstream>  // 引入文件操作
```

- 定义数据保存和加载时的文件路径
- 定义互斥锁

```cpp
#define STORE_FILE "store/dumpFile"  // 存储文件路径
std::mutex mtx; // 定义互斥锁
```

- 对插入节点成员函数和删除节点成员函数进行加锁

```cpp
// 只有在插入和删除的时候，才会进行加锁
template <typename K, typename V>
int SkipList<K, V>::insert_element(const K key, const V value) {
    mtx.lock();  // 在函数第一句加锁
    // ... 算法过程（省略）

    if (current != NULL && current->get_key() == key) {
        std::cout << "key: " << key << ", exists" << std::endl;
        // 在算法流程中有一个验证 key 是否存在的过程
        // 在此处需要提前 return，所以提前解锁
        mtx.unlock();
        return 1;
    }

    // ... 
    mtx.unlock();  // 函数执行完毕后解锁
    return 0;
}

template <typename K, typename V>
void SkipList<K, V>::delete_element(K key) {
    mtx.lock();  // 加锁
    // ... 算法过程（省略）
    mtx.unlock();  // 解锁
    return;
}
```

**本章完整文件如下：**

```cpp
#include <iostream>
#include <cstdlib>  // 随机函数
#include <cmath>
#include <cstring>
#include <mutex>    // 引入互斥锁
#include <fstream>  // 引入文件操作

#define STORE_FILE "store/dumpFile"  // 存储文件路径

std::mutex mtx; // 定义互斥锁
std::string delimiter = ":";

template <typename K, typename V>
class Node {
public:
    Node() {}
    Node(K k, V v, int);
    ~Node();
    K get_key() const;
    V get_value() const;
    void set_value(V);
    Node<K, V> **forward;
    int node_level;
private:
    K key;
    V value;
};

// ... Node 类的所有方法实现（省略）

template <typename K, typename V>
class SkipList {
    public:
    SkipList(int);
    ~SkipList();
    int get_random_level();
    Node<K, V> *create_node(K, V, int);
    int insert_element(K, V);
    void display_list();
    bool search_element(K);
    void delete_element(K);
    void dump_file();
    void load_file();
    void clear(Node<K, V> *);
    int size();

private:
    void get_key_value_from_string(const std::string &str, std::string *key, std::string *value);
    bool is_valid_string(const std::string &str);

private:
    int _max_level;
    int _skip_list_level;
    Node<K, V> *_header;
    std::ofstream _file_writer;
    std::ifstream _file_reader;
    int _element_count;
};

// ... SkipList 类的大部分方法实现（省略）

// 只有在插入和删除的时候，才会进行加锁
template <typename K, typename V>
int SkipList<K, V>::insert_element(const K key, const V value) {
    mtx.lock();  // 在函数第一句加锁
    // ... 算法过程（省略）

    if (current != NULL && current->get_key() == key) {
        std::cout << "key: " << key << ", exists" << std::endl;
        // 在算法流程中有一个验证 key 是否存在的过程
        // 在此处需要提前 return，所以提前解锁
        mtx.unlock();
        return 1;
    }

    // ... 
    mtx.unlock();  // 函数执行完毕后解锁
    return 0;
}

template <typename K, typename V>
void SkipList<K, V>::delete_element(K key) {
    mtx.lock();  // 加锁
    // ... 算法过程（省略）
    mtx.unlock();  // 解锁
    return;
}
```

至此，我们已经将所有的分散的模块合并。

在将所有的模块合并了之后，可以将 skiplist.h include 到其他文件中，就可以使用该存储引擎了。

# 压力测试

将 “模块合并” 章节创建的 skiplist.h 包含到当前压力测试程序中。

测试程序主要的内容为编写在随机读写下，测试项目每秒可处理写请求数，和每秒可处理读请求数

具体可以通过多线程(pthread)以及计时(chrono)来执行插入和检索操作。

压力测试文件的内容如下：

```cpp
// 引入必要的头文件
#include <iostream> // 用于输入输出流
#include <chrono> // 用于高精度时间测量
#include <cstdlib> // 包含一些通用的工具函数，如随机数生成
#include <pthread.h> // 用于多线程编程
#include <time.h> // 用于时间处理函数
#include "./skiplist.h" // 引入自定义的跳表实现

// 定义宏常量
#define NUM_THREADS 1 // 线程数量
#define TEST_COUNT 100000 // 测试用的数据量大小
SkipList<int, std::string> skipList(18); // 创建一个最大层级为18的跳表实例

// 插入元素的线程函数
void *insertElement(void* threadid) {
    long tid; // 线程ID
    tid = (long)threadid; // 将void*类型的线程ID转换为long型
    std::cout << tid << std::endl; // 输出线程ID
    int tmp = TEST_COUNT/NUM_THREADS; // 计算每个线程应该插入的元素数量
    // 循环插入元素
    for (int i=tid*tmp, count=0; count<tmp; i++) {
        count++;
        skipList.insert_element(rand() % TEST_COUNT, "a"); // 随机生成一个键，并插入带有"a"的元素
    }
    pthread_exit(NULL); // 退出线程
}

// 检索元素的线程函数
void *getElement(void* threadid) {
    long tid; // 线程ID
    tid = (long)threadid; // 将void*类型的线程ID转换为long型
    std::cout << tid << std::endl; // 输出线程ID
    int tmp = TEST_COUNT/NUM_THREADS; // 计算每个线程应该检索的元素数量
    // 循环检索元素
    for (int i=tid*tmp, count=0; count<tmp; i++) {
        count++;
        skipList.search_element(rand() % TEST_COUNT); // 随机生成一个键，并尝试检索
    }
    pthread_exit(NULL); // 退出线程
}

int main() {
    srand(time(NULL)); // 初始化随机数生成器
    {
        pthread_t threads[NUM_THREADS]; // 定义线程数组
        int rc; // 用于接收pthread_create的返回值
        int i; // 循环计数器

        auto start = std::chrono::high_resolution_clock::now(); // 开始计时

        // 创建插入元素的线程
        for( i = 0; i < NUM_THREADS; i++ ) {
            std::cout << "main() : creating thread, " << i << std::endl;
            rc = pthread_create(&threads[i], NULL, insertElement, (void *)i); // 创建线程

            if (rc) {
                std::cout << "Error:unable to create thread," << rc << std::endl;
                exit(-1); // 如果线程创建失败，退出程序
            }
        }

        void *ret; // 用于接收pthread_join的返回值
        // 等待所有插入线程完成
        for( i = 0; i < NUM_THREADS; i++ ) {
            if (pthread_join(threads[i], &ret) != 0 )  {
                perror("pthread_create() error");
                exit(3); // 如果线程等待失败，退出程序
            }
        }
        auto finish = std::chrono::high_resolution_clock::now(); // 结束计时
        std::chrono::duration<double> elapsed = finish - start; // 计算耗时
        std::cout << "insert elapsed:" << elapsed.count() << std::endl; // 输出插入操作耗时
    }

    // 下面的代码块与上面类似，用于创建并管理检索操作的线程
    {
        pthread_t threads[NUM_THREADS];
        int rc;
        int i;
        auto start = std::chrono::high_resolution_clock::now();

        for( i = 0; i < NUM_THREADS; i++ ) {
            std::cout << "main() : creating thread, " << i << std::endl;
            rc = pthread_create(&threads[i], NULL, getElement, (void *)i);

            if (rc) {
                std::cout << "Error:unable to create thread," << rc << std::endl;
                exit(-1);
            }
        }

        void *ret;
        for( i = 0; i < NUM_THREADS; i++ ) {
            if (pthread_join(threads[i], &ret) != 0 )  {
                perror("pthread_create() error");
                exit(3);
            }
        }

        auto finish = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = finish - start;
        std::cout << "get elapsed:" << elapsed.count() << std::endl;
    }

    pthread_exit(NULL); // 主线程退出

    return 0;
}
```

在测试文件中的 NUM_THREADS（执行线程数量） 和 TEST_COUNT（测试数量） 可自定义。

编译测试文件，执行测试文件，观察输出结果。

编译命令如下：

```bash
g++ --std=c++11 main.cpp -o stress -pthread
```

使用 C++11 的语法特性进行编译，并且链接线程库。

最后，关于项目的课程写法，大家可以参考如下内容。需要注意的是，第3点基于LRU算法，课程中并没有实现该功能，大家可以自行扩展。![WeChatWorkScreenshot_97f56cb9-c9cb-472c-82c7-31a314b96315](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/WeChatWorkScreenshot_97f56cb9-c9cb-472c-82c7-31a314b96315.png)

## 简历写法

最后，关于项目的课程写法，大家可以参考如下内容。需要注意的是，第3点基于LRU算法，课程中并没有实现该功能，大家可以自行扩展。

![WeChatWorkScreenshot_97f56cb9-c9cb-472c-82c7-31a314b96315](https://kstar-1253855093.cos.ap-nanjing.myqcloud.com/baguwen1.0/WeChatWorkScreenshot_97f56cb9-c9cb-472c-82c7-31a314b96315.png)

## 常见面试问题及回答

### 1、什么是跳表，它是如何工作的？

答：

跳表是一种概率性数据结构，基于多层链表，每一层都是下一层的一个子集。最底层是原始数据的完整列表，每个元素在上面一层出现的概率是 P（通常取 1/2）。

每层都有两个指针，一个指向同层的下一个元素，另一个指向下层的相同元素（如果存在）。查找、插入或删除操作的平均时间复杂度为 O(log n)。

### 2、跳表与平衡树相比有什么优势和劣势？

答：

跳表的优势：

- 简单性：跳表的算法和数据结构比平衡树简单得多。对于许多开发者而言，理解和实现跳表比实现一个红黑树或 AVL 树要容易。
- 并发友好：跳表由于其分层和链表的本质，更容易实现锁的细粒度管理，使其更适合于并发操作。在多线程环境中，跳表可以较容易地通过锁分离技术实现高效的并发操作。
- 动态性：跳表可以很自然地扩展，添加更多层级以应对数据增长，而不需要复杂的重平衡操作。

跳表的劣势：

- 空间消耗：跳表使用多层指针，意味着每个元素都需要额外的空间来存储指向其他元素的引用。这比平衡树的空间开销要大。
- 平均性能：虽然跳表的平均操作时间复杂度为 O(log n)，但这是一种概率性表现，在某些极端情况下可能不如平衡树表现稳定。
- 随机性：跳表的效率依赖于随机化过程，用于确定元素应该出现在哪些层上。这种随机性使得性能具有一定的不可预测性。

平衡树的优势：

- 稳定性：平衡树如 AVL 树或红黑树保证了最坏情况下的时间复杂度为 O(log n)，这比跳表的概率性保证更稳定。
- 空间效率：平衡树通常每个节点只需存储几个额外指针（父节点、左右子节点），不需要像跳表那样存储多个层次的指针。
- 理论优化：平衡树在理论研究和优化方面更为成熟，众多变种如红黑树、B树等都被广泛用于文件系统和数据库。

平衡树的劣势：

- 实现复杂性：平衡树的算法和维护平衡的逻辑相对复杂，实现错误可能导致树结构损坏。
- 并发难度：在多线程环境中，维持树的平衡状态需要复杂的锁机制或其他并发控制技术，这可能导致性能下降。

### 3、跳表这一数据结构 有哪些实际应用？

答：

1、数据库

索引构建：跳表可用于构建内存数据库和数据库索引，特别是那些需要快速插入和删除的场景，如LevelDB 和 RocksDB 使用跳表来维护内存中的数据结构，便于快速的键值查找和范围查询。

LSM 树：在基于日志结构合并树（LSM Tree）的存储引擎中，跳表用于处理写入操作，因为它支持高效的插入性能，并能快速构建新的索引。

2、 缓存系统

内存存储：在需要有序键值对的缓存系统中，跳表可以提供比纯哈希表更丰富的功能，例如Redis中的Sorted Sets就是通过跳表实现的，支持基于分数的数据排序和快速访问。

3、 网络路由

高效路由表：跳表由于其高效的搜索、插入和删除操作，可以用于网络路由表的构建，特别是在动态变化的网络环境中，跳表能快速更新路由信息。

4、 实时数据分析

排行榜和计分板：在需要实时更新和查询的系统中，例如在线游戏的排行榜，跳表可以快速插入新的得分并调整排名，同时也能快速响应排名查询。

5、 并发系统

多线程访问：由于跳表的设计允许更简单的并发实现，它们经常被用在需要多线程安全访问的应用中，尤其是在实现细粒度锁或锁自由结构时。

### 4、跳表如何支持快速插入、删除和搜索操作？

答：

1、快速搜索

跳表通过多层的链表结构实现快速搜索。在跳表中，最底层包含所有元素，而上层是下层的子集，并作为快速通道使用，每一层都为有序链表。

搜索过程：

- 搜索从最顶层开始，比较当前节点的下一个节点的值与目标值。
- 如果目标值大于下一个节点的值，则向右移动。
- 如果目标值小于下一个节点的值，或者没有下一个节点，则向下移动到下一层继续搜索。
- 重复此过程，直至到达最底层。
- 在最底层，如果找到目标值，则搜索成功；如果没有找到，则搜索失败。

这种层级结构大大减少了搜索路径的长度，平均搜索时间复杂度为 O(logn)。

2、快速插入

跳表的插入操作不仅要在底层插入元素，还可能需要在上层中插入该元素的额外引用（通过随机算法决定）。

插入过程：

- 首先进行搜索操作，找到在底层应该插入元素的位置。
- 在底层插入元素。
- 使用抛硬币或伪随机数决定该元素是否参与上层。
- 如果决定插入上层，则在相应位置进行插入，并可能继续向上扩展。
- 重复此过程直到不再插入更高层为止。

这个过程确保了插入的时间复杂度平均也是 O(logn)。

3、 快速删除

删除操作类似于插入操作，需要在所有包含目标元素的层中删除该元素。

删除过程：

- 使用搜索操作找到目标元素的位置。
- 从最底层开始，逐层向上删除所有指向该元素的节点。
- 对于每一层，调整指针以绕过被删除的节点。

删除操作的时间复杂度同样为 O(logn)，因为删除操作涉及到的层数也是对数级别的。

### 5、redis中如何使用跳表这一数据结构

跳表在 Redis Sorted Set 中的使用

1、 功能实现

跳表在 Sorted Set 中实现了以下关键功能：

- 插入操作：当一个新元素添加到 Sorted Set 中时，它会被插入到跳表中，元素位置基于其分数。如果多个元素具有相同的分数，它们会基于字典序进行排序。
- 删除操作：可以从跳表中移除元素，无论它们的分数或位置。
- 搜索操作：可以快速找到具有特定分数的元素，或者根据分数范围（如范围查询）获取元素列表。
- 排名查找：可以快速确定元素在跳表中的排名，或者查找特定排名的元素。 效率

由于跳表的平均时间复杂度为 O(log N)，这使得即使是在非常大的数据集中，插入、删除和查找操作也非常快速。

这种效率是通过在多个层级上维护指向元素的指针来实现的，这样搜索时可以快速跳过大量元素。

2、 为什么选择跳表而不是红黑树

Redis 的作者 Antirez 选择跳表来实现 Sorted Set 的主要原因之一是跳表代码实现起来更简单，而且在并发环境下，跳表更易于进行锁分离（fine-grained locking）。

尽管从理论上讲，红黑树在最坏情况下提供了相同的时间复杂度保证，跳表的实现和维护却更为直观。

3、 应用场景示例

在实际应用中，例如，开发者可能会使用 Redis Sorted Set 来实现一个实时排行榜系统，用户的分数更新后，可以即时反映在排行榜中，而不需要重新排序整个数据集。

这对于需要高性能和实时性的应用来说非常重要。

### 6、为什么平衡树在并发方面不够友好

复杂的平衡操作：

平衡树通过旋转和重新平衡来维护树的平衡状态。在并发环境中，每次插入或删除操作后都需要执行这些操作，这增加了同步的难度。多个线程同时尝试进行这些修改可能会导致数据结构损坏，除非非常小心地控制这些操作的并发。

锁的需求和管理：

为了保证操作的正确性，平衡树在并发环境中通常需要细粒度的锁或者全局锁来防止多个线程同时修改同一个部分的树结构。这种锁机制可能导致：

- 死锁：多个线程尝试获取彼此持有的锁。
- 锁竞争：高并发下，多个线程竞争相同的锁，增加了等待时间，降低了系统的整体性能。
- 锁开销：管理锁和处理锁冲突会带来额外的时间和空间开销。

不一致性风险：

在高并发操作中，如果锁的使用不当，可能导致数据不一致性。例如，在执行树旋转或重新平衡的过程中，如果多个线程交叉读写同一个节点，可能会导致一部分线程看到的数据是不一致的。

范围查询复杂性：

平衡树常用于执行范围查询，如在数据库索引中查找所有符合特定条件的项。在并发环境下，保持这种操作的正确性而不引入重大性能损失是具有挑战性的，尤其是在需要锁定多个节点进行操作时。

设计和调试难度

平衡树的并发实现比单线程实现复杂得多，设计和调试也更加困难。这可能需要更深入的理解树结构操作和并发控制技术。

替代方案的可用性：

由于上述挑战，一些系统可能选择使用其他数据结构作为替代，例如跳表或锁自由（lock-free）数据结构，它们可以更简单地支持并发操作。







