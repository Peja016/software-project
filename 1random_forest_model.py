import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import pickle
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# 1. Data loading and preprocessing
data = pd.read_csv("bike_usage_weather_dec2024_90min.csv")  # Replace with your new file name
data['date'] = pd.to_datetime(data[['year', 'month', 'day']])

# 2. Feature engineering
# 2.1 Geographic clustering (including holiday and weekday effects)
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

# 2.4 Add weather and holiday features
label_encoder = LabelEncoder()
data['weather_main_encoded'] = label_encoder.fit_transform(data['weather_main'])

# 3. Define features and target
features = [
    'station_id', 'area_cluster', 'hour_sin', 'hour_cos',
    'temp_max', 'humidity', 'capacity', 'is_weekend', 'lag_1h', 'lag_24h',
    'wind_speed', 'pressure', 'clouds_all', 'is_holiday', 'weather_main_encoded'
]
target = 'num_bikes_available'
data = data.dropna(subset=features + [target])

X = data[features]
y = data[target]

# 4. Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 5. Train model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# 6. Evaluation
y_pred = model.predict(X_test)
y_pred_int = np.floor(y_pred).astype(int)
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"R-square: {r2_score(y_test, y_pred):.4f}")

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
plt.gca().invert_yaxis()  # Put most important features at the top
plt.tight_layout()
plt.savefig('feature_importance.png')  # Save as image file
plt.show()

# 9. Save model
joblib.dump(model, "bike_availability_rf_model_with_new_features.joblib")
with open("bike_availability_rf_model_with_new_features.pkl", "wb") as f:
    pickle.dump(model, f)

# 10. Compute default lag values (based on December data)
december_data = data[data['date'].dt.month == 12]
default_lags = december_data.groupby(['station_id', 'hour']).agg({
    'lag_1h': 'mean',
    'lag_24h': 'mean'
}).reset_index()
default_lags.to_csv("default_lags.csv", index=False)

# 11. Generate station info table
station_info = data[['station_id', 'capacity', 'area_cluster', 'lat', 'lon', 'name']].drop_duplicates()
station_info.to_csv("station_info.csv", index=False)

# 12. Save KMeans model and LabelEncoder
joblib.dump(kmeans, "kmeans_model.joblib")
joblib.dump(label_encoder, "weather_label_encoder.joblib")

print("Model saved as .joblib and .pkl files")
print("Default lag values saved as default_lags.csv")
print("Station info saved as station_info.csv")
print("KMeans model saved as kmeans_model.joblib")
print("Weather encoder saved as weather_label_encoder.joblib")
print("Feature importance chart saved as feature_importance.png")
