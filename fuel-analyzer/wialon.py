import requests

API_URL = "https://hosting.wln-hst.com/wialon/ajax.html"

def login(token):
    r = requests.get(f"{API_URL}?svc=token/login&params={{\"token\":\"{token}\"}}")
    return r.json()["eid"]

def get_units(session_id):
    params = {
        "svc": "core/search_items",
        "params": {
            "spec": {"itemsType":"avl_unit","propName":"sys_name","propValueMask":"*","sortType":"sys_name"},
            "force":1,"flags":1,"from":0,"to":0
        },
        "sid": session_id
    }
    return requests.post(API_URL, json=params).json()

def get_messages(session_id, unit_id, time_from, time_to):
    params = {
        "svc": "messages/load_interval",
        "params": {
            "itemId": unit_id,
            "timeFrom": time_from,
            "timeTo": time_to,
            "flags": 0x0001,
            "flagsMask": 0x0001,
            "loadCount": 1000,
            "loadTime": 0
        },
        "sid": session_id
    }
    return requests.post(API_URL, json=params).json()