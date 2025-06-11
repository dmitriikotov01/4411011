import sqlite3

def init_db():
    conn = sqlite3.connect("fuel_data.db")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS fuel_data (
        timestamp TEXT,
        unit_name TEXT,
        fuel_level REAL,
        speed REAL,
        rpm REAL,
        lat REAL,
        lon REAL,
        altitude REAL,
        voltage REAL,
        satellites INTEGER
    )''')
    conn.commit()
    conn.close()