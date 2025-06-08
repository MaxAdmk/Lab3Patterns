import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="11223344",
        database="yahoo_finance"
    )

def create_trade_history_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TradeHistory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(20) NOT NULL,
            asset_name VARCHAR(50) NOT NULL,
            timestamp DATETIME NOT NULL,
            value FLOAT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_asset_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Asset (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(20) NOT NULL,
            name VARCHAR(50) NOT NULL,
            timestamp DATETIME NOT NULL,
            current_price FLOAT NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def insert_trade_history(type, asset_name, timestamp, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO TradeHistory (type, asset_name, timestamp, value) VALUES (%s, %s, %s, %s)",
        (type, asset_name, timestamp, value)
    )
    conn.commit()
    cursor.close()
    conn.close()

def insert_asset(type, name, timestamp, current_value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Asset (type, name, timestamp, current_value) VALUES (%s, %s, %s, %s)",
        (type, name, timestamp, current_value)
    )
    conn.commit()
    cursor.close()
    conn.close()

