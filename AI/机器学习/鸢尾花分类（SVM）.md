# 鸢尾花分类（SVM）

## 项目概述

我们可以通过一个简单的项目，一步步实现支持向量机（SVM）模型来学习它的原理和应用。我们可以用一个常见的二分类数据集，比如鸢尾花数据集（Iris Dataset），来搭建和训练SVM模型。以下是项目的主要步骤：

1. **导入数据和库**：加载数据集并导入所需的Python库。
2. **数据预处理**：对数据进行基本的处理，比如特征选择和标准化。
3. **模型训练**：使用支持向量机对数据进行训练。
4. **模型评估**：测试模型的效果，并查看分类的准确率。
5. **模型优化**：尝试调整SVM的参数以优化模型。

## 代码

```python
# 导入所需的库
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

# 加载鸢尾花数据集
iris = datasets.load_iris()
X = iris.data[:, :2]  # 选择前两个特征（方便可视化）
y = (iris.target != 0) * 1  # 将数据简化为二分类任务

# 查看数据的基本信息
print("特征数据：", X[:5])
print("标签数据：", y[:5])

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 标准化数据
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 查看标准化后的特征数据
print("标准化后的训练集特征：", X_train[:5])
print("标准化后的测试集特征：", X_test[:5])

# 初始化支持向量机模型，使用线性核
svm_model = SVC(kernel='linear', random_state=42)

# 训练模型
svm_model.fit(X_train, y_train)

# 输出模型的训练结果
print("训练完成！支持向量的数量：", len(svm_model.support_vectors_))

# 使用测试集进行预测
y_pred = svm_model.predict(X_test)

# 计算模型的准确率
accuracy = accuracy_score(y_test, y_pred)
print(f"模型准确率：{accuracy:.2f}")

# 输出分类报告
print("分类报告：")
print(classification_report(y_test, y_pred))
```

## 运行结果

```
特征数据： [[5.1 3.5]
 [4.9 3. ]
 [4.7 3.2]
 [4.6 3.1]
 [5.  3.6]]
标签数据： [0 0 0 0 0]
标准化后的训练集特征： [[-1.47393679  1.20365799]
 [-0.13307079  2.99237573]
 [ 1.08589829  0.08570939]
 [-1.23014297  0.75647855]
 [-1.7177306   0.30929911]]
标准化后的测试集特征： [[ 0.35451684 -0.58505976]
 [-0.13307079  1.65083742]
 [ 2.30486738 -1.0322392 ]
 [ 0.23261993 -0.36147005]
 [ 1.2077952  -0.58505976]]
训练完成！支持向量的数量： 10
模型准确率：1.00
分类报告：
              precision    recall  f1-score   support

           0       1.00      1.00      1.00        10
           1       1.00      1.00      1.00        20

    accuracy                           1.00        30
   macro avg       1.00      1.00      1.00        30
weighted avg       1.00      1.00      1.00        30


```

