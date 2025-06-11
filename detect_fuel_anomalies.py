import time
import argparse
import json

from src import wialon_fetcher, db, data_processor, anomaly_detector


def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def main(config_path: str):
    cfg = load_config(config_path)
    engine, table, _ = db.init_db(cfg.get("db_url", "sqlite:///fuel_data.db"))
    detector = anomaly_detector.FuelAnomalyDetector()
    while True:
        df = wialon_fetcher.get_fuel_data(
            cfg["token"],
            cfg["unit_id"],
            cfg["start_time"],
            cfg["end_time"],
        )
        df = data_processor.compute_differences(df)
        db.insert_dataframe(df, engine, table)
        detector.train(df)
        anomalies = detector.detect_anomalies(df)
        print(anomalies)
        time.sleep(cfg.get("interval", 3600))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect fuel anomalies")
    parser.add_argument("config", help="Path to configuration JSON file")
    args = parser.parse_args()
    main(args.config)
