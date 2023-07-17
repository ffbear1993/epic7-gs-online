from typing import List, Dict
from data import GearItem, Substats, Main
import re
import json
from fuzzywuzzy import process
import streamlit as st


def build_gear(result: List):
    gear = GearItem()
    gear.substats = [Substats() for i in range(4)]
    gear.main = Main()

    with open("./config/gear_config.json", "r", encoding="utf-8") as f:
            gear_config = json.load(f)

    for i, result_item in enumerate(result):
        if i == 0:
            try:
                fuzzy_result = process.extractOne(str(ocr_result_interpreter(result_item, gear_config)), [str(item) for item in gear_config['enhance']])
            except Exception as e:
                fuzzy_result = [0]
            gear.enhance = int(fuzzy_result[0])
        if i == 1:
            try:
                fuzzy_result = process.extractOne(str(ocr_result_interpreter(result_item, gear_config)), [str(item) for item in gear_config['level']])
            except Exception as e:
                fuzzy_result = [0]
            gear.level = int(fuzzy_result[0])
        if i == 2:
            gear.rank = ocr_result_interpreter(result_item[:2], gear_config, label="rank")
            gear.gear = ocr_result_interpreter(result_item[2:], gear_config, label="gear")
        if i == 3:
            gear.main.type = ocr_result_interpreter(result_item, gear_config, label="stat_type")
        if i == 4:
            gear.main.value = ocr_result_interpreter(result_item, gear_config)
            if "%" in result_item and gear.main.type in ["Health", "Attack", "Defense"]:
                gear.main.type = gear.main.type + "Percent"
        if i == len(result) - 1:
            gear.set = ocr_result_interpreter(result_item, gear_config, label="set")

    for i in range((len(result[5:]) - 1) // 2):
        gear.substats[i].type = ocr_result_interpreter(result[5 + i * 2], gear_config, label="stat_type")
        gear.substats[i].value = ocr_result_interpreter(result[5 + i * 2 + 1], gear_config)
        if "%" in result[5 + i * 2 + 1] and gear.substats[i].type in ["Health", "Attack", "Defense"]:
            gear.substats[i].type = gear.substats[i].type + "Percent"

    return gear


def ocr_result_interpreter(result: str, gear_config: Dict, label=""):
    st.text(result)
    if label == "":
        try:
            result = int("".join(re.findall("\d+", result)))
        except Exception as e:
            result = 0
        return result
    else:
        if "(" in result and ")" in result and "/" in result:
            return gear_config[label].get(result[:-5], f"error_key_{result}")
       
        return gear_config[label].get(result, f"error_key_{result}")
