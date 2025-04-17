import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import pickle
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import holidays
from datetime import timedelta

# 1. Data loading and preprocessing
data = pd.read_csv("cleandata.csv")
data['date'] = pd.to_datetime(data[['year', 'month', 'day']])
data['last_reported'] = pd.to_datetime(data['last_reported'])


# 2. Generate restock points and schedule
def identify_restock_points(df):
    restock_points = []
    df = df.sort_values(['station_id', 'last_reported'])

    for station_id, group in df.groupby('station_id'):
        last_restock = None
        for idx, row in group.iterrows():
            if row['num_bikes_available'] == row['capacity']:
                # Check if it is the first restock or more than 6 hours since last restock
                if last_restock is None or (row['last_reported'] - last_restock) > timedelta(hours=6):
                    restock_points.append({
                        'station_id': station_id,
                        'last_reported': row['last_reported'],
                        'hour': row['hour']
                    })
                    last_restock = row['last_reported']

    return pd.DataFrame(restock_points)


# Generate restock points
restock_df = identify_restock_points(data)


# 3. Calculate restock frequency (consider ±1 hour window)
def calculate_restock_frequency(restock_df, days=30):
    restock_freq = []
    for station_id, group in restock_df.groupby('station_id'):
        for hour in range(24):
            # Consider hour ± 1 window
            hour_window = [(hour - 1) % 24, hour, (hour + 1) % 24]
            count = group[group['hour'].isin(hour_window)].shape[0]
            frequency = count / days  # Frequency = occurrences / days
            restock_freq.append({
                'station_id': station_id,
                'hour_window': hour,
                'frequency': frequency
            })

    return pd.DataFrame(restock_freq)


# Assume data spans 30 days
restock_schedule = calculate_restock_frequency(restock_df, days=30)
restock_schedule.to_csv("restock_schedule.csv", index=False)


# 4. Add is_restocked feature
def add_is_restocked(df, schedule, freq_threshold=0.5):
    df = df.copy()
    df['is_restocked'] = False
    for idx, row in df.iterrows():
        station_id = row['station_id']
        hour = row['hour']
        # Check ±1 hour window
        hour_window = [(hour - 1) % 24, hour, (hour + 1) % 24]
        # Query schedule
        matches = schedule[
            (schedule['station_id'] == station_id) &
            (schedule['hour_window'].isin(hour_window)) &
            (schedule['frequency'] >= freq_threshold)
            ]
        if not matches.empty:
            df.at[idx, 'is_restocked'] = True
    return df


# Add is_restocked column (frequency threshold of 0.5, meaning at least one restock every two days)
data = add_is_restocked(data, restock_schedule, freq_threshold=0.5)

# 5. Feature engineering
# 5.1 Geographical clustering
ie_holidays = holidays.Ireland(years=data['year'].unique())
data['is_holiday'] = data['date'].apply(lambda x: int(x in ie_holidays))

coords = data[['lat', 'lon']].values
holiday_feature = data['is_holiday'].astype(int).values.reshape(-1, 1)
clustering_features = np.hstack((coords, holiday_feature))
kmeans = KMeans(n_clusters=10, random_state=42)
data['area_cluster'] = kmeans.fit_predict(clustering_features)

# 5.2 Time features
data['hour_sin'] = np.sin(2 * np.pi * data['hour'] / 24)
data['hour_cos'] = np.cos(2 * np.pi * data['hour'] / 24)
data['is_weekend'] = data['date'].dt.dayofweek >= 5

# 5.3 Lag features (only lag_24h)
data = data.sort_values(['station_id', 'date', 'hour'])
data['lag_24h'] = data.groupby('station_id')['num_bikes_available'].shift(24)

# 6. Define features and target
features = [
    'station_id', 'area_cluster', 'hour_sin', 'hour_cos',
    'temp', 'humidity', 'capacity', 'is_weekend', 'lag_24h',
    'pressure', 'is_holiday', 'is_restocked'
]
target = 'num_bikes_available'
data = data.dropna(subset=features + [target])

# 7. Time series split
data = data.sort_values('date')
train_size = int(0.7 * len(data))
train_data = data.iloc[:train_size]
test_data = data.iloc[train_size:]

X_train = train_data[features]
y_train = train_data[target]
X_test = test_data[features]
y_test = test_data[target]

# 8. Train the model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# 9. Model evaluation
y_pred = model.predict(X_test)
y_pred_int = np.floor(y_pred).astype(int)
print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
print(f"R²: {r2_score(y_test, y_pred):.4f}")

# 10. Feature importance analysis
feature_importance = model.feature_importances_
importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': feature_importance
}).sort_values(by='Importance', ascending=False)

# Print feature importance
print("\nFeature Importance:")
print(importance_df)

# 11. Generate feature importance bar chart
plt.figure(figsize=(10, 6))
plt.barh(importance_df['Feature'], importance_df['Importance'], color='skyblue')
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importance in Random Forest Model (With Restock)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('feature_importance_with_restock.png')

# 12. Save the model
joblib.dump(model, "bike_availability_rf_model_with_restock.joblib", compress=3)
with open("bike_availability_rf_model_with_restock.pkl", "wb") as f:
    pickle.dump(model, f)

# 13. Calculate default lag values (only lag_24h)
default_lags = data.groupby(['station_id', 'hour']).agg({
    'lag_24h': 'mean'
}).reset_index()
default_lags['lag_24h'] = default_lags['lag_24h'].fillna(
    default_lags.groupby('station_id')['lag_24h'].transform('mean')
)
default_lags.to_csv("default_lags.csv", index=False)

# 14. Generate station information table
station_info = data[['station_id', 'capacity', 'area_cluster', 'lat', 'lon', 'name']].drop_duplicates()
station_info.to_csv("station_info.csv", index=False)

# 15. Save KMeans model
joblib.dump(kmeans, "kmeans_model.joblib")

print("Model saved as .joblib and .pkl files")
print("Default lag values saved as default_lags.csv")
print("Station info saved as station_info.csv")
print("Restock schedule saved as restock_schedule.csv")
print("KMeans model saved as kmeans_model.joblib")
print("Feature importance chart saved as feature_importance_with_restock.png")
