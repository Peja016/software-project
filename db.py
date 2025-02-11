import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

dbHost = os.getenv('DATABASE_HOST')
dbUser = os.getenv('DATABASE_USER')
dbPassword = os.getenv('DATABASE_PASSWORD')
dbName = os.getenv('DATABASE_NAME')

conn = False
# sg-063a97696ba8dec6a
def dbConnection():
    connect = mysql.connector.connect(
        host=dbHost,
        user=dbUser,
        password=dbPassword,
        database=dbName
    )
    return connect

def getCursor(): 
    connection = dbConnection()
    cursor = connection.cursor()
    return cursor, connection

