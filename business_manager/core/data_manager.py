import json
from pathlib import Path
from threading import Lock
from config import DATA_DIR

lock = Lock()

def _get_file_path(filename: str) -> Path:
    return DATA_DIR / filename


def read_data(filename: str):
    path = _get_file_path(filename)
    
    if not path.exists():
        return []
    
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_data(filename: str,data):
    path = _get_file_path(filename)
    
    with lock:
        with open(path,"w", encoding="utf-8") as file:
            json.dump(data,file, indent=2)
            
            
def append_data(filename: str, new_item: dict):
    data = read_data(filename)
    data.append(new_item)
    write_data(filename,data)
    return new_item


def update_data(filename: str, item_id: str, updated_item: dict):
    data = read_data(filename)
    
    for i, item in enumerate(data):
        if item.get("id") == item_id:
            data[i] = updated_item
            write_data(filename,data)
            return updated_item
    return None


def delete_data(filename: str, item_id: str):
    data = read_data(filename)
    
    new_data = [item for item in data if item.get("id") != item_id]
    
    write_data(filename,new_data)
    
    return True
            

