from sqlalchemy import create_engine, Column, Integer, Float, DateTime, MetaData, Table
from sqlalchemy.orm import sessionmaker
import pandas as pd


def init_db(db_url: str = "sqlite:///fuel_data.db"):
    engine = create_engine(db_url)
    metadata = MetaData()
    fuel_table = Table(
        "fuel_data",
        metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("timestamp", DateTime, nullable=False),
        Column("fuel_level", Float, nullable=False),
    )
    metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, fuel_table, Session


def insert_dataframe(df: pd.DataFrame, engine, table):
    df.to_sql(table.name, engine, if_exists="append", index=False)

