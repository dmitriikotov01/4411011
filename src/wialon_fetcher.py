import requests
import pandas as pd
from datetime import datetime


API_BASE_URL = "https://hst-api.wialon.com/wialon/ajax.html"


def _login(token: str) -> str:
    """Authenticate with Wialon and return the session id."""
    params = {"token": token}
    response = requests.post(
        API_BASE_URL,
        params={"svc": "token/login", "params": pd.io.json.dumps(params)},
    )
    response.raise_for_status()
    data = response.json()
    return data.get("eid")


def _logout(sid: str) -> None:
    requests.post(API_BASE_URL, params={"svc": "core/logout", "sid": sid})


def get_fuel_data(token: str, unit_id: int, start_time: int, end_time: int) -> pd.DataFrame:
    """Fetch fuel level data from Wialon.

    Parameters
    ----------
    token : str
        API token
    unit_id : int
        Wialon unit id
    start_time : int
        Unix timestamp for start
    end_time : int
        Unix timestamp for end

    Returns
    -------
    pandas.DataFrame
        DataFrame with columns ["timestamp", "fuel_level"].
    """
    sid = _login(token)
    try:
        params = {
            "sid": sid,
            "svc": "unit/calc_fuel",
            "params": pd.io.json.dumps(
                {
                    "id": unit_id,
                    "from": start_time,
                    "to": end_time,
                }
            ),
        }
        response = requests.post(API_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json().get("fuel_level", [])
        df = pd.DataFrame(data, columns=["timestamp", "fuel_level"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        return df
    finally:
        _logout(sid)
