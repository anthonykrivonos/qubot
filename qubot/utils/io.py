from typing import Dict
import json
import pickle
from os.path import isabs, abspath, exists
import sys
from pathlib import Path

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def read_json(path: str) -> Dict:
    absolute_path = path if isabs(path) else abspath(path)
    absolute_path = absolute_path if (absolute_path.endswith(".qu") or absolute_path.endswith(".json")) else "%s.qu.json" % absolute_path
    try:
        with open(absolute_path, "r+") as f:
            res = json.load(f)
    except:
        res = {}
    return res

def write_json(path: str, data: dict) -> bool:
    absolute_path = path if isabs(path) else abspath(path)
    absolute_path = absolute_path if (absolute_path.endswith(".qu") or absolute_path.endswith(".json")) else "%s.qu.json" % absolute_path
    try:
        with open(absolute_path, "w+") as f:
            json.dump(data, f, indent=4)
            return True
    except Exception as e:
        raise e
        return False

def read_pickle(path: str):
    absolute_path = path if isabs(path) else abspath(path)
    absolute_path = absolute_path if absolute_path.endswith(".qu.pkl") else "%s.qu.pkl" % absolute_path
    if not exists(absolute_path):
        return None
    with open(absolute_path, "rb") as pickle_file:
        res = pickle.load(pickle_file, errors="warning")
    return res

def write_pickle(path: str, data: any) -> bool:
    absolute_path = path if isabs(path) else abspath(path)
    absolute_path = absolute_path if absolute_path.endswith(".qu.pkl") else "%s.qu.pkl" % absolute_path
    folder = absolute_path[:absolute_path.rindex("/")] if "/" in absolute_path else absolute_path
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(absolute_path, "wb") as pickle_file:
        pickle.dump(data, pickle_file)
        return True

def safe_filename(filename: str) -> str:
    return filename.replace("/", "∕")
