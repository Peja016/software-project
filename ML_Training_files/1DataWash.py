import pandas as pd

# 1. Load the data
data = pd.read_csv("final_merged_data.csv")

# 2. Calculate the average values for max/min indicators and create new columns
# Temperature: temp = (max_air_temperature_celsius + min_air_temperature_celsius) / 2
if 'max_air_temperature_celsius' in data.columns and 'min_air_temperature_celsius' in data.columns:
    data['temp'] = (data['max_air_temperature_celsius'] + data['min_air_temperature_celsius']) / 2

# Humidity: humidity = (max_relative_humidity_percent + min_relative_humidity_percent) / 2
if 'max_relative_humidity_percent' in data.columns and 'min_relative_humidity_percent' in data.columns:
    data['humidity'] = (data['max_relative_humidity_percent'] + data['min_relative_humidity_percent']) / 2

# Pressure: pressure = (max_barometric_pressure_hpa + min_barometric_pressure_hpa) / 2
if 'max_barometric_pressure_hpa' in data.columns and 'min_barometric_pressure_hpa' in data.columns:
    data['pressure'] = (data['max_barometric_pressure_hpa'] + data['min_barometric_pressure_hpa']) / 2

# 3. Define the features to drop
# Includes features that are not available (grass temperature, soil temperature, standard deviation, quality indicators) and original max/min columns
columns_to_drop = [
    # Original max/min columns
    'max_air_temperature_celsius',
    'min_air_temperature_celsius',
    'max_relative_humidity_percent',
    'min_relative_humidity_percent',
    'max_barometric_pressure_hpa',
    'min_barometric_pressure_hpa',

    # Grass temperature related
    'max_grass_temperature_celsius',
    'min_grass_temperature_celsius',
    'grass_temperature_std_deviation',
    'max_grass_temp_quality_indicator',
    'min_grass_temp_quality_indicator',
    'grass_temp_std_quality_indicator',

    # Soil temperature related (5cm, 10cm, 20cm, 30cm, 50cm, 100cm)
    'max_soil_temperature_5cm_celsius',
    'min_soil_temperature_5cm_celsius',
    'soil_temperature_std_deviation_5cm',
    'max_soil_temp_5cm_quality_indicator',
    'min_soil_temp_5cm_quality_indicator',
    'soil_temp_std_5cm_quality_indicator',

    'max_soil_temperature_10cm_celsius',
    'min_soil_temperature_10cm_celsius',
    'soil_temperature_std_deviation_10cm',
    'max_soil_temp_10cm_quality_indicator',
    'min_soil_temp_10cm_quality_indicator',
    'soil_temp_std_10cm_quality_indicator',

    'max_soil_temperature_20cm_celsius',
    'min_soil_temperature_20cm_celsius',
    'soil_temperature_std_deviation_20cm',
    'max_soil_temp_20cm_quality_indicator',
    'min_soil_temp_20cm_quality_indicator',
    'soil_temp_std_20cm_quality_indicator',

    'max_earth_temperature_30cm_celsius',
    'min_earth_temperature_30cm_celsius',
    'earth_temperature_std_deviation_30cm',
    'max_earth_temp_30cm_quality_indicator',
    'min_earth_temp_30cm_quality_indicator',
    'earth_temp_std_30cm_quality_indicator',

    'max_earth_temperature_50cm_celsius',
    'min_earth_temperature_50cm_celsius',
    'earth_temperature_std_deviation_50cm',
    'max_earth_temp_50cm_quality_indicator',
    'min_earth_temp_50cm_quality_indicator',
    'earth_temp_std_50cm_quality_indicator',

    'max_earth_temperature_100cm_celsius',
    'min_earth_temperature_100cm_celsius',
    'earth_temperature_std_deviation_100cm',
    'max_earth_temp_100cm_quality_indicator',
    'min_earth_temp_100cm_quality_indicator',
    'earth_temp_std_100cm_quality_indicator',

    # Standard deviation
    'air_temperature_std_deviation',
    'relative_humidity_std_deviation',
    'barometric_pressure_std_deviation',

    # Quality indicators
    'max_air_temp_quality_indicator',
    'min_air_temp_quality_indicator',
    'air_temp_std_quality_indicator',
    'max_humidity_quality_indicator',
    'min_humidity_quality_indicator',
    'humidity_std_quality_indicator',
    'max_pressure_quality_indicator',
    'min_pressure_quality_indicator',
    'pressure_std_quality_indicator'
]

# 4. Drop the features that are not available and the original max/min columns
# Only drop columns that exist in the dataset to avoid KeyError
columns_to_drop = [col for col in columns_to_drop if col in data.columns]
data_cleaned = data.drop(columns=columns_to_drop)

# 5. Print the remaining features to confirm
print("Remaining features:", data_cleaned.columns.tolist())

# 6. Save the cleaned dataset
data_cleaned.to_csv("cleandata.csv", index=False)
print("The cleaned dataset has been saved as bike_usage_weather_cleaned_avg.csv")

# Notes:
# - The new columns 'temp', 'humidity', 'pressure' are calculated from the arithmetic average of the original max/min columns.
# - These column names are consistent with the OpenWeatherMap API field names (temp, humidity, pressure).
# - The original max/min columns have been removed.
# - If data is later retrieved from the OpenWeatherMap API, the temp, humidity, pressure fields can be used directly.
