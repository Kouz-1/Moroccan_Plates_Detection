import mysql.connector
import json
import os
from datetime import datetime

def store_plate_to_mysql(
    json_path='json_plates/plates.json',
    mysql_config={
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'vehicules_parking'
    }
):
    if not os.path.exists(json_path):
        print("No JSON plate data found.")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    if not data:
        print("No plate data in JSON.")
        return

    last = data[-1]
    number = last.get("number")
    char = last.get("char")
    region = last.get("region")
    arrived_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    # Make sure the table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Number VARCHAR(50),
            Charactere VARCHAR(10),
            Region VARCHAR(10),
            arrived_at DATETIME,
            UNIQUE KEY unique_plate (Number, Charactere, Region)
        )
    """)

    # Insert or update based on unique combination
    cursor.execute("""
        INSERT INTO vehicules (Number, Charactere, Region, arrived_at)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE arrived_at = VALUES(arrived_at)
    """, (number, char, region, arrived_at))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Plate [{number}-{char}-{region}] stored or updated at {arrived_at}")
