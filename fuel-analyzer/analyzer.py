import pandas as pd

def detect_anomalies(df):
    events = []
    df = df.sort_values("timestamp")
    df["fuel_diff"] = df["fuel_level"].diff()
    for i in range(1, len(df)):
        drop = df.iloc[i]["fuel_diff"]
        if drop < -10:
            window = df.iloc[i:i+5]
            restored = window["fuel_level"].max() - df.iloc[i]["fuel_level"]
            if restored > 8:  # мнимый слив
                continue
            if df.iloc[i]["speed"] < 5 and df.iloc[i]["satellites"] >= 5:
                scenario = "двигатель работает" if df.iloc[i]["voltage"] > 12.4 or df.iloc[i]["rpm"] > 500 else "двигатель выключен"
                events.append((df.iloc[i]["timestamp"], drop, scenario))
    return events