import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ripser import ripser
from persim import wasserstein
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

import All_methods.file_operations as imp

start_date = '2023-01-01'
end_date = '2023-12-31'
time_series=imp.get_shanghai_index(start_date, end_date,'log_return')['log_return']

print(time_series.head())


# 参数设置
window_size = 50  # 滑动窗口大小
tau = 1           # 时间延迟
m = 7             # 嵌入维度

# 时间延迟嵌入
def time_delay_embedding(series, tau, m):
    embedded = np.array([series[i - tau * j] for j in range(m) for i in range(tau * (m - 1), len(series))])
    return embedded.reshape(m, -1).T

embedded_data = time_delay_embedding(time_series, tau, m)

# 过滤持久性图中的 inf 值
def filter_finite_diagram(diagram):
    """移除持久性图中死亡时间为 inf 的点"""
    return np.array([point for point in diagram if np.isfinite(point[1])])

# 计算拓扑特征
def compute_persistent_homology(data):
    diagrams = ripser(data)['dgms']
    return diagrams

# 计算多个窗口的拓扑特征
tda_features = []
for i in range(len(embedded_data) - window_size):
    window_data = embedded_data[i:i + window_size]
    diagrams = compute_persistent_homology(window_data)
    
    # 计算 0 维拓扑特征（连通分量）
    h0 = filter_finite_diagram(diagrams[0])  # 移除 inf 值
    if len(h0) > 1:
        wasserstein_dist = wasserstein(h0[:-1], h0[1:])  # 计算 Wasserstein 距离
    else:
        wasserstein_dist = 0
    
    tda_features.append(wasserstein_dist)

tda_features = np.array(tda_features)

# **确保 X 和 y 长度一致**
# 假设 time_series 是 DataFrame 或 Series，且 index 为日期
# 使用 .iloc 切片时，建议也获取对应的索引
min_len = min(len(time_series.iloc[window_size:-1]), len(tda_features[:-1]))
# 获取对应的时间索引（确保时间顺序与特征对齐）
time_index = time_series.index[window_size:window_size+min_len]

# 如果 time_series 是 DataFrame，有多列，选择特定列，例如 log_return
y = pd.Series(time_series.iloc[window_size+1:window_size+1+min_len].values.squeeze(), 
              index=time_series.index[window_size+1:window_size+1+min_len])
# 同时对 X 中第一列也使用原始股价/收益率数值，但保留时间索引备用
X1 = pd.Series(time_series.iloc[window_size:window_size+min_len].values.squeeze(),
               index=time_series.index[window_size:window_size+min_len])
# 将原有数值与 tda_features 结合
X = pd.DataFrame({
    'price': X1,
    'tda_feature': tda_features[:min_len]
})

# 训练测试集划分
# 例如，80% 用做训练，20% 测试
split_idx = int(0.8 * len(X))
X_train = X.iloc[:split_idx]
X_test = X.iloc[split_idx:]
y_train = y.iloc[:split_idx]
y_test = y.iloc[split_idx:]

y_test = time_series.iloc[-len(y_test):]  # 重新对齐时间索引

# 训练 XGBoost 预测模型
model = XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
model.fit(X_train, y_train)

# 预测 & 评估
y_pred = model.predict(X_test)

y_pred_series = pd.Series(y_pred, index=y_test.index)  # 用 y_test 的时间索引修正


plt.figure(figsize=(12, 6))
plt.plot(y_test.index, y_test, label="True Price", marker='o')
plt.plot(y_pred_series.index, y_pred_series, label="Predicted Price", linestyle="dashed", marker='x')
plt.xlabel("Date")
plt.ylabel("Price / Log Return")
plt.legend()
plt.title("Stock Price Prediction with Correct Time Alignment")
plt.grid(True)
plt.show()