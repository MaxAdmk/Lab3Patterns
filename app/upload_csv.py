import csv
import io
from datetime import datetime
from .database import get_connection

def parse_timestamp(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.strip())
    except ValueError:
        return datetime.strptime(ts.strip(), "%Y-%m-%dT%H:%M:%S")

async def process_uploaded_csv(file):
    contents = await file.read()
    decoded = contents.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))

    reader.fieldnames = [field.strip() for field in reader.fieldnames]
    rows = [
        {key.strip(): value.strip() for key, value in row.items()}
        for row in reader
    ]

    if not rows:
        print("CSV file is empty.")
        return

    required_fields = {"name", "type", "value", "timestamp"}
    for i, row in enumerate(rows):
        if not required_fields.issubset(row):
            raise ValueError(f"Missing required fields in row {i + 1}: {row}")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT MAX(timestamp) AS latest FROM TradeHistory")
    result = cursor.fetchone()
    latest_db_timestamp = result['latest'] if result['latest'] else datetime.min

    new_rows = []
    for row in rows:
        try:
            if parse_timestamp(row['timestamp']) > latest_db_timestamp:
                new_rows.append(row)
        except Exception as e:
            print(f"Skipping invalid row: {row} ({e})")

    if not new_rows:
        print("Data from CSV file already imported. Nothing new found.")
        cursor.close()
        conn.close()
        return

    latest_data = {}
    for row in new_rows:
        name = row['name']
        type_ = row['type'].lower()
        value = float(row['value'])
        timestamp = parse_timestamp(row['timestamp'])

        if name not in latest_data or timestamp > latest_data[name]['timestamp']:
            latest_data[name] = {
                'type': type_,
                'value': value,
                'timestamp': timestamp
            }

    for name, data in latest_data.items():
        cursor.execute("SELECT * FROM Asset WHERE name = %s", (name,))
        existing_asset = cursor.fetchone()
        if existing_asset:
            if data['timestamp'] > existing_asset['timestamp']:
                cursor.execute("""
                    UPDATE Asset SET current_price = %s, timestamp = %s
                    WHERE name = %s
                """, (data['value'], data['timestamp'], name))
        else:
            cursor.execute("""
                INSERT INTO Asset (name, type, current_price, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (name, data['type'], data['value'], data['timestamp']))

    for row in new_rows:
        name = row['name']
        type_ = row['type'].lower()
        value = float(row['value'])
        timestamp = parse_timestamp(row['timestamp'])

        cursor.execute("""
            INSERT INTO TradeHistory (asset_name, type, value, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (name, type_, value, timestamp))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"New data lines imported: {len(new_rows)}")
