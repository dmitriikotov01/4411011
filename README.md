# Fuel Anomaly Detection

This project fetches fuel level data from Wialon, stores it in a database and detects anomalies using `anomalib`.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a configuration JSON file:

```json
{
  "token": "YOUR_WIALON_TOKEN",
  "unit_id": 12345,
  "start_time": 0,
  "end_time": 0,
  "interval": 3600,
  "db_url": "sqlite:///fuel_data.db",
  "drain_threshold": -10,
  "fill_threshold": 10
}
```

Set `start_time` and `end_time` as Unix timestamps. The script will periodically fetch data every `interval` seconds.

## Running

```bash
python detect_fuel_anomalies.py config.json
```

## Files

- `src/wialon_fetcher.py` – fetches fuel data from Wialon API.
- `src/db.py` – initializes database and stores data.
- `src/data_processor.py` – computes fuel differences and filters events.
- `src/anomaly_detector.py` – trains anomaly detection model and detects anomalies.
- `detect_fuel_anomalies.py` – CLI entry point.
