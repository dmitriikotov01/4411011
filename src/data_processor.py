import pandas as pd

DRAIN_THRESHOLD = -10  # liters
FILL_THRESHOLD = 10  # liters


def compute_differences(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["diff"] = df["fuel_level"].diff().fillna(0)
    return df


def filter_events(df: pd.DataFrame, drain_threshold: float = DRAIN_THRESHOLD, fill_threshold: float = FILL_THRESHOLD) -> pd.DataFrame:
    drains = df[df["diff"] <= drain_threshold]
    fills = df[df["diff"] >= fill_threshold]
    events = pd.concat([drains, fills]).sort_values("timestamp").reset_index(drop=True)
    return events
