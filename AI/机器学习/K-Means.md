# K-Means

## 项目概述

这个项目的流程将包括：

1. **引入必要的库和数据准备**
2. **理解 K-均值的工作原理**
3. **选择初始的 K 值**
4. **执行聚类并评估结果**

## 代码

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

# 生成一个样本数据集
# make_blobs 是一个用于生成指定特征的数据点集的函数，常用于聚类等机器学习相关任务的数据准备
# n_samples=30:0：表示生成的样本数量为 300 个
# centers=4：指定了数据将围绕 4 个中心进行分布。
# random_state=42：这是一个随机种子
# cluster_std=0.6：每个簇的标准差。
X, y = make_blobs(n_samples=300, centers=4, random_state=42, cluster_std=0.6)

# 可视化数据
# X[:, 0] 表示取 X 中每一行的第 0 列数据
# X[:, 1] 表示取 取每一行的第 1 列数据
# 在二维数据的情况下，这两列数据分别代表了数据点在二维平面中的 x 坐标和 y 坐标
# s=50：设置了散点的大小（size）为 50。
plt.scatter(X[:, 0], X[:, 1], s=50)
plt.show()

# 使用肘部法则确定 K 值
sse = []  # 存储每个 K 值对应的误差平方和
k_range = range(1, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    sse.append(kmeans.inertia_)  # inertia_ 表示 KMeans 聚类中代表样本到其最近的聚类中心的距离之和

# 回执肘部图
plt.plot(k_range, sse, marker='o')
plt.xlabel('Number of clusters(K)')
plt.ylabel('Sum of squared distances (SSE)')
plt.title('Elbow Method for Optimal K')
plt.show()

# 使用 K=4 来初始化 KMeans 模型
# 这里使用 KMeans 类来创建一个 KMeans 聚类模型，n_clusters=4 表示将数据聚类成 4 个不同的簇
kmeans = KMeans(n_clusters=4, random_state=42)
# fit_predict 首先使用数据 X 来拟合模型（即找到每个簇的中心和其他模型参数），然后对数据 X 中的每个样本进行预测，返回每个样本所属的簇的标签
y_kmeans = kmeans.fit_predict(X)

# 绘制聚类结果
# c=kmeans 表示使用 y_kmeans 中的簇标签来为每个数据点分配颜色，这样属于同一个簇的数据点会有相同的颜色
# cmap='viridis' 指定了使用 `viridis` 颜色映射，它会根据簇标签自动分配一组美观且易于区分的颜色
plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, cmap='viridis')  # 使用颜色区分不同簇
# 获取 KMeans 模型拟合后得到的每个簇的中心坐标
centers = kmeans.cluster_centers_  # 获取簇中心

# 绘制簇中心
# centers[:,0] 和 centers[:,1] 分别是簇中心的 x 和 y 坐标
# c='red' 表示将簇中心的颜色设置为红色
# s=200 指定了散点的大小，这里设置为 200
# alpha=0.75 设置了透明度为 0.75
# marker='X' 表示使用 'X' 形状来标记簇中心，使其在图中更易于识别
plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.75, marker='X')
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.title("K-Means Clustering with K=4")
plt.show()
```

## 运行结果

![image-20241030163432166](https://xubowen-bucket.oss-cn-beijing.aliyuncs.com/img/image-20241030163432166.png)









