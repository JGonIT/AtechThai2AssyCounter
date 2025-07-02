# Data.py

import json
import os
from datetime import datetime

DATA_FILE = "plans_data.json"

# Part List를 Model, Part Name, Part Number로 구성
DEFAULT_DATA = {
    "part_list": [
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB74365234"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB74365235"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB74365246"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75005915"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75005916"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75005918"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75005922"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164715"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164716"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164727"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164732"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164733"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164713"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164714"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164727"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164729"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164731"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164735"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164718"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164720"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164726"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164722"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164728"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164730"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75164734"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744909"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744910"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744911"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744926"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744928"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744918"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744924"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744925"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744927"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744920"},
        {"model": "SJ", "part_name": "F/GRILLE", "part_number": "AEB75744930"}
    ],
    "plans": []
}

# 이하 함수는 기존과 동일하게 사용
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_part_list():
    data = load_data()
    return data["part_list"]

def get_plans():
    data = load_data()
    return data["plans"]

def add_plan(plan_data):
    required_fields = ["date", "part", "plan_count"]
    for field in required_fields:
        if field not in plan_data:
            raise ValueError(f"Missing required field: {field}")
    formatted_plan = {
        "date": str(plan_data["date"]),
        "part": str(plan_data["part"]),
        "plan_count": int(plan_data["plan_count"]),
        "completed_count": int(plan_data.get("completed_count", 0))
    }
    data = load_data()
    data["plans"].append(formatted_plan)
    save_data(data)

def update_plans(new_plans):
    validated_plans = []
    for plan in new_plans:
        validated_plans.append({
            "date": str(plan["date"]),
            "part": str(plan["part"]),
            "plan_count": int(plan["plan_count"]),
            "completed_count": int(plan.get("completed_count", 0))
        })
    data = load_data()
    data["plans"] = validated_plans
    save_data(data)
