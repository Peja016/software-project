import requests
import schedule
import os
import re
import time
from dotenv import load_dotenv

from db import getCursor

load_dotenv() # Load environment variables from .env file

def check_table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    return result is not None  # if true，the table exists

def getBikesData():
    print('Start running')
    # Replace with your actual API key
    cursor, connection = getCursor()

    createBikesInfoTable = """
        CREATE TABLE IF NOT EXISTS bikesInfo (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            address VARCHAR(255) NOT NULL,
            banking BOOLEAN,
            bonus BOOLEAN,
            status VARCHAR(255) NOT NULL,
            last_update BIGINT
        );
    """
    cursor.execute(createBikesInfoTable)

    createPositionTable = """
        CREATE TABLE IF NOT EXISTS positions (
            id INT PRIMARY KEY,
            lat FLOAT,
            lng FLOAT,
            last_update BIGINT,
            FOREIGN KEY (id) REFERENCES bikesInfo(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    cursor.execute(createPositionTable)

    api_key = os.getenv('JCDecaux_API_KEY')
    url = 'https://api.jcdecaux.com/vls/v1/stations'

    # Optional: specify the city (e.g., Paris)
    city = 'dublin'

    # Construct the full URL (including API key and city parameter)
    full_url = f'{url}?contract={city}&apiKey={api_key}'

    # Send a GET request
    response = requests.get(full_url)

    # Check if the request was successful (status code 200 means success)
    if response.status_code == 200:
        data = response.json()
        # with open("output.json", "w", encoding="utf-8") as json_file:
        #     json.dump(data, json_file, indent=4, ensure_ascii=False)
        # Output the raw data (JSON format)
        
        # print(json.dumps(data, indent=4))  # Beautify the output JSON data
        
        # For example, extract the station name and available bike count
        for station in data:
            stationNumber = station['number']

            checkBikeInfo = f"SELECT * FROM bikesInfo WHERE id = %s"
            cursor.execute(checkBikeInfo, (stationNumber,))
            result = cursor.fetchone()
            if result is None:
                insertData = f"""
                    INSERT INTO bikesInfo (id, name, address, banking, bonus, status, last_update)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(insertData, (
                    stationNumber, 
                    station['name'], 
                    station['address'], 
                    station['banking'],
                    station['bonus'],
                    station['status'],
                    station['last_update'],
                )
            )
            else: 
                attrsName = [
                    'number',
                    'name',
                    'address',
                    'banking',
                    'bonus',
                    'status',
                    'last_update',
                ]
                for i in range(1, len(attrsName) - 1):
                    if result[i] != station[attrsName[i]]:
                        updateBikesInfo = f"""
                            UPDATE bikesInfo 
                            SET {attrsName[i]} = %s, last_update = %s
                            WHERE id = %s;
                        """
                        cursor.execute(updateBikesInfo, (station[attrsName[i]], station['last_update'], stationNumber))
        
            tableName = re.sub(r'[^a-zA-Z0-9]', '', station['address'])

            # check if the table exists, if not, create it.
            create_table_station = f"""
                CREATE TABLE IF NOT EXISTS {tableName} (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    station_id INT,
                    bike_stands INT,
                    available_bike_stands INT,
                    available_bikes INT,
                    last_update BIGINT,
                    FOREIGN KEY (station_id) REFERENCES bikesInfo(id) ON DELETE CASCADE ON UPDATE CASCADE
                );
            """
            cursor.execute(create_table_station)
            if check_table_exists(cursor, tableName): 
                insertInfo = f"""
                    INSERT INTO {tableName} (station_id, bike_stands, available_bike_stands, available_bikes, last_update)
                    VALUES (%s, %s, %s, %s, %s);
                """
                cursor.execute(insertInfo, (
                    station['number'], 
                    station['bike_stands'], 
                    station['available_bike_stands'], 
                    station['available_bikes'], 
                    station['last_update']
                    )
                )
                print(f'Storing {tableName} successfully!')
            # print('Storing station data successfully!')
            if check_table_exists(cursor, 'positions'): 
                checkData = f"SELECT * FROM positions WHERE id = %s"
                cursor.execute(checkData, (stationNumber,))
                result = cursor.fetchone()
                if result is None:
                    insertData = f"""
                        INSERT INTO positions (id, lat, lng, last_update)
                        VALUES (%s, %s, %s, %s);
                    """
                    cursor.execute(insertData, (
                        stationNumber, 
                        station['position']['lat'], 
                        station['position']['lng'], 
                        station['last_update']
                        )
                    )
                    # print('Storing position data successfully!') 
                else: 
                    if (result[1] != station['position']['lat']):
                        updateLat = f"""
                            UPDATE positions 
                            SET lat = %s, last_update = %s
                            WHERE id = %s;
                        """
                        cursor.execute(updateLat, (station['position']['lat'], station['last_update'], stationNumber))
                        # print('Updated lng data successfully!') 
                    if (result[2] != station['position']['lng']):
                        updateLng = f"""
                            UPDATE positions 
                            SET lng = %s, last_update = %s
                            WHERE id = %s;
                        """
                        cursor.execute(updateLng, (station['position']['lng'], station['last_update'], stationNumber))
                        # print('Updated lng data successfully!') 

        connection.commit()
        cursor.close()
        connection.close()
        print('finished!')
    else:
        print(f"Error: {response.status_code}")

schedule.every(5).minutes.do(getBikesData)

while True:
    schedule.run_pending()  # 執行任何等待的任務
    time.sleep(1) 