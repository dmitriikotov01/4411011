import requests
import sqlite3
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://hosting.wln-hst.com/wialon/ajax.html"
TOKEN = "aa6f378db93797003b401d0eda4828510B2C1C6B907C5C376A07E73EA2C75513BD1DCB59"

def wialon_request(svc, params, sid=None):
    data={"svc":svc,"params":json.dumps(params)}
    if sid: data["sid"]=sid
    r=requests.get(API_URL, params=data, timeout=30)
    r.raise_for_status()
    return r.json()

class WialonClient:
    def __init__(self, token: str):
        self.token = token
        self.sid = None

    def login(self):
        resp = requests.get(API_URL, params={"svc": "token/login", "params": json.dumps({"token": self.token})}, timeout=30)
        resp.raise_for_status()
        self.sid = resp.json().get("eid")
        return self.sid

    def get_units(self):
        params = {
            "spec": {"itemsType": "avl_unit", "propName": "sys_name", "propValueMask": "*", "sortType": "sys_name"},
            "force": 1,
            "flags": 1,
            "from": 0,
            "to": 0,
        }
        data = wialon_request("core/search_items", params, self.sid)
        return data.get("items", [])

    def load_messages(self, unit_id: int, time_from: int, time_to: int):
        params = {
            "itemId": unit_id,
            "timeFrom": time_from,
            "timeTo": time_to,
            "flags": 0x0001,
            "flagsMask": 0x0001,
            "loadCount": 0,
            "loadTime": 0,
        }
        data = wialon_request("messages/load_interval", params, self.sid)
        return data.get("messages", [])

def init_db(db_path: str = "fuel_data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS fuel_data(
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
        )
        """
    )
    conn.commit()
    conn.close()


def save_records(records, db_path: str = "fuel_data.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executemany(
        "INSERT INTO fuel_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        records,
    )
    conn.commit()
    conn.close()


def detect_fuel_drains(df: pd.DataFrame):
    events = []
    df = df.sort_values("timestamp").reset_index(drop=True)
    prev_level = df.loc[0, "fuel_level"]
    prev_time = df.loc[0, "timestamp"]
    for idx in range(1, len(df)):
        current_level = df.loc[idx, "fuel_level"]
        drop = prev_level - current_level
        if drop > 10 and df.loc[idx, "speed"] < 5 and df.loc[idx, "satellites"] >= 5:
            # check false drain
            end_time = df.loc[idx, "timestamp"] + timedelta(minutes=20)
            window = df[(df["timestamp"] > df.loc[idx, "timestamp"]) & (df["timestamp"] <= end_time)]
            if not window.empty and window["fuel_level"].max() >= prev_level - 2:
                # fuel restored
                pass
            else:
                scenario = (
                    "двигатель работает"
                    if df.loc[idx, "voltage"] > 12.5 or df.loc[idx, "rpm"] > 500
                    else "двигатель выключен"
                )
                events.append(
                    {
                        "time": df.loc[idx, "timestamp"],
                        "delta": drop,
                        "speed": df.loc[idx, "speed"],
                        "voltage": df.loc[idx, "voltage"],
                        "rpm": df.loc[idx, "rpm"],
                        "satellites": df.loc[idx, "satellites"],
                        "lat": df.loc[idx, "lat"],
                        "lon": df.loc[idx, "lon"],
                        "scenario": scenario,
                    }
                )
        if current_level != current_level:
            # NaN
            prev_level = prev_level
        else:
            prev_level = current_level
        prev_time = df.loc[idx, "timestamp"]
    return events


def plot_fuel(df: pd.DataFrame):
    df.plot(x="timestamp", y="fuel_level", title="Уровень топлива")
    plt.xlabel("Время")
    plt.ylabel("Топливо, л")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    init_db()
    client = WialonClient(TOKEN)
    sid = client.login()
    if not sid:
        print("Ошибка авторизации")
        return
    units = client.get_units()
    if not units:
        print("Нет доступных объектов")
        return
    unit = units[0]
    unit_id = unit["id"] if isinstance(unit, dict) else unit.get("id")
    unit_name = unit["nm"] if isinstance(unit, dict) else unit.get("nm")
    now = int(time.time())
    start = now - 6 * 3600
    messages = client.load_messages(unit_id, start, now)
    records = []
    for msg in messages:
        pos = msg.get("pos", {})
        p = msg.get("p", {})
        records.append(
            (
                datetime.fromtimestamp(msg.get("t")),
                unit_name,
                p.get("lls1"),
                p.get("speed", 0),
                p.get("rpm", 0),
                pos.get("y"),
                pos.get("x"),
                pos.get("z"),
                p.get("pwr_voltage", 0),
                pos.get("sc", 0),
            )
        )
    if not records:
        print("Нет данных")
        return
    save_records(records)
    df = pd.DataFrame(
        records,
        columns=["timestamp", "unit_name", "fuel_level", "speed", "rpm", "lat", "lon", "altitude", "voltage", "satellites"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["fuel_level"].interpolate(inplace=True)
    events = detect_fuel_drains(df)
    for e in events:
        print(
            f"{e['time']} | Δтоплива: {e['delta']:.1f} л | скорость: {e['speed']} км/ч | напряжение: {e['voltage']} В | rpm: {e['rpm']} | satellites: {e['satellites']} | ({e['lat']}, {e['lon']}) | {e['scenario']}"
        )
    plot_fuel(df)


if __name__ == "__main__":
    main()
