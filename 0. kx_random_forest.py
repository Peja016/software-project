import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import pickle
from sklearn.cluster import KMeans

# 1. 数据加载与预处理
data = pd.read_csv("final_merged_data_with_availability.csv")
data['date'] = pd.to_datetime(data[['year', 'month', 'day']])

# 2. 特征工程
# 2.1 地理聚类
coords = data[['lat', 'lon']].values
kmeans = KMeans(n_clusters=10, random_state=42)  # 创建 KMeans 对象
data['area_cluster'] = kmeans.fit_predict(coords)  # 计算并赋值 area_cluster

# 2.2 时间特征
data['hour_sin'] = np.sin(2 * np.pi * data['hour'] / 24)
data['hour_cos'] = np.cos(2 * np.pi * data['hour'] / 24)
data['is_weekend'] = data['date'].dt.dayofweek >= 5

# 2.3 计算滞后特征
data = data.sort_values(['station_id', 'date', 'hour'])
data['lag_1h'] = data.groupby('station_id')['num_bikes_available'].shift(1)
data['lag_24h'] = data.groupby('station_id')['num_bikes_available'].shift(24)

# 3. 定义特征和目标
features = [
    'station_id', 'area_cluster', 'hour_sin', 'hour_cos',
    'max_air_temperature_celsius', 'max_relative_humidity_percent',
    'capacity', 'is_weekend', 'lag_1h', 'lag_24h'
]
target = 'num_bikes_available'
data = data.dropna(subset=features + [target])

X = data[features]
y = data[target]

# 4. 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 5. 训练模型
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# 6. 评估
y_pred = model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"R²: {r2_score(y_test, y_pred):.4f}")

# 7. 保存模型
joblib.dump(model, "bike_availability_rf_model_with_lags.joblib")
with open("bike_availability_rf_model_with_lags.pkl", "wb") as f:
    pickle.dump(model, f)

# 8. 计算默认滞后值（基于12月数据）
december_data = data[data['date'].dt.month == 12]
default_lags = december_data.groupby(['station_id', 'hour']).agg({
    'lag_1h': 'mean',
    'lag_24h': 'mean'
}).reset_index()
default_lags.to_csv("default_lags.csv", index=False)

# 9. 生成站点信息表（包含 station_id, capacity, area_cluster）
station_info = data[['station_id', 'capacity', 'area_cluster']].drop_duplicates()
station_info.to_csv("station_info.csv", index=False)

# 10. 保存 KMeans 模型（可选，适用于新站点）
joblib.dump(kmeans, "kmeans_model.joblib")

print("模型已保存为 .joblib 和 .pkl 文件")
print("默认滞后值已保存为 default_lags.csv")
print("站点信息已保存为 station_info.csv")
print("KMeans 模型已保存为 kmeans_model.joblib")