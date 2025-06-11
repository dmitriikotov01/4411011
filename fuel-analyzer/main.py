from wialon import login, get_units, get_messages
from db import init_db
from analyzer import detect_anomalies
import time, sqlite3, pandas as pd, matplotlib.pyplot as plt

TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН"

def main():
    init_db()
    sid = login(TOKEN)
    units = get_units(sid)["items"]
    unit_id = units[0]["id"]
    unit_name = units[0]["nm"]
    now = int(time.time())
    start = now - 3600 * 6

    data = get_messages(sid, unit_id, start, now)
    messages = data.get("messages", [])

    records = []
    for msg in messages:
        rec = (
            pd.to_datetime(msg["t"], unit="s"),
            unit_name,
            msg.get("p", {}).get("lls1", None),
            msg.get("p", {}).get("speed", 0),
            msg.get("p", {}).get("rpm", 0),
            msg.get("pos", {}).get("y", None),
            msg.get("pos", {}).get("x", None),
            msg.get("pos", {}).get("z", None),
            msg.get("p", {}).get("pwr_voltage", 0),
            msg.get("pos", {}).get("sc", 0)
        )
        records.append(rec)

    conn = sqlite3.connect("fuel_data.db")
    c = conn.cursor()
    c.executemany("INSERT INTO fuel_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
    conn.commit()

    df = pd.DataFrame(records, columns=["timestamp", "unit_name", "fuel_level", "speed", "rpm", "lat", "lon", "altitude", "voltage", "satellites"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["fuel_level"].interpolate(inplace=True)

    anomalies = detect_anomalies(df)
    for a in anomalies:
        print(f"Аномалия: {a[0]} | Слив: {a[1]:.1f} л | {a[2]}")

    df.plot(x="timestamp", y="fuel_level", title="Уровень топлива")
    plt.show()

if __name__ == "__main__":
    main()