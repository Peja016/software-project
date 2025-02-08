from db import getCursor

cursor, connection = getCursor()

def dropAllTables(cursor):
    # show all tables
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    
    # delete each table
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
        print(f"Table {table[0]} has been dropped.")

dropAllTables(cursor)