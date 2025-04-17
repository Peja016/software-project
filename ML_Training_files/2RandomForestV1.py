import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import holidays

# 1. Data loading and preprocessing
data = pd.read_csv("cleandata.csv")
data['date'] = pd.to_datetime(data[['year', 'month', 'day']])

# 2. Feature engineering
# 2.1 Geographical clustering
ie_holidays = holidays.Ireland(years=data['year'].unique())
data['is_holiday'] = data['date'].apply(lambda x: int(x in ie_holidays))

coords = data[['lat', 'lon']].values
holiday_feature = data['is_holiday'].astype(int).values.reshape(-1, 1)
clustering_features = np.hstack((coords, holiday_feature))
kmeans = KMeans(n_clusters=10, random_state=42)
data['area_cluster'] = kmeans.fit_predict(clustering_features)

# 2.2 Time features
data['hour_sin'] = np.sin(2 * np.pi * data['hour'] / 24)
data['hour_cos'] = np.cos(2 * np.pi * data['hour'] / 24)
data['is_weekend'] = data['date'].dt.dayofweek >= 5

# 2.3 Lag features
data = data.sort_values(['station_id', 'date', 'hour'])
data['lag_1h'] = data.groupby('station_id')['num_bikes_available'].shift(1)
data['lag_24h'] = data.groupby('station_id')['num_bikes_available'].shift(24)

# 3. Define features and target
features = [
    'station_id', 'area_cluster', 'hour_sin', 'hour_cos',
    'temp', 'humidity', 'capacity', 'is_weekend', 'lag_1h', 'lag_24h',
    'pressure', 'is_holiday'
]
target = 'num_bikes_available'
data = data.dropna(subset=features + [target])

# 4. Time series split
data = data.sort_values('date')
train_size = int(0.7 * len(data))
train_data = data.iloc[:train_size]
test_data = data.iloc[train_size:]

X_train = train_data[features]
y_train = train_data[target]
X_test = test_data[features]
y_test = test_data[target]

# 5. Train the model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# 6. Model evaluation
y_pred = model.predict(X_test)
y_pred_int = np.floor(y_pred).astype(int)
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"R²: {r2_score(y_test, y_pred):.4f}")

# 7. Feature importance analysis
feature_importance = model.feature_importances_
importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': feature_importance
}).sort_values(by='Importance', ascending=False)

# Print feature importance
print("\nFeature Importance:")
print(importance_df)

# 8. Generate feature importance bar chart
plt.figure(figsize=(10, 6))
plt.barh(importance_df['Feature'], importance_df['Importance'], color='skyblue')
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importance in Random Forest Model')
plt.gca().invert_yaxis()  # Put the most important feature on top
plt.tight_layout()
plt.savefig('feature_importance_with_lag_1h.png')
plt.show()
