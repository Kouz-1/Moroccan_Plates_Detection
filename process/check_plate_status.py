import mysql.connector
import json
import os

def check_plate_status(json_path='json_plates/plates.json'):
    if not os.path.exists(json_path):
        return "No plate information found."

    # Read last plate from JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    if not data:
        return "JSON is empty."
    last = data[-1]

    number = last.get("number")
    char = last.get("char")
    region = last.get("region")

    try:
        # Connect to your MySQL database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vehicules_recherchees'
        )
        cursor = conn.cursor()

        query = """
        SELECT Status FROM vehicules
        WHERE Number = %s AND Charactere = %s AND Region = %s
        """
        cursor.execute(query, (number, char, region))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return f"Statut: {result[0]}"
        else:
            return "No matching record found in database."

    except mysql.connector.Error as err:
        return f"MySQL Error: {err}"
