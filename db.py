import mysql.connector
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv() # Load environment variables from .env file

dbHost = os.getenv('DATABASE_HOST')
dbUser = os.getenv('DATABASE_USER')
dbPassword = os.getenv('DATABASE_PASSWORD')
dbName = os.getenv('DATABASE_NAME')
dbPort = "3006"

connection_string = "mysql+mysqldb://{}:{}@{}:{}/{}".format(dbUser, dbPassword, dbHost, dbPort, dbName)

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
    engine = create_engine(connection_string, echo = True)  
    connection = dbConnection()
    cursor = connection.cursor()
    return cursor, connection, engine

