import streamlit as st
from stqdm import stqdm
from data import GearInfo
from PIL import Image, ImageDraw
from pathlib import Path
import json
import easyocr
import numpy as np
from typing import List, Dict
import re


def output_image(image):
    if st.session_state["debug"]:
        st.image(image)


def output_result(result):
    if st.session_state["debug"]:
        st.text(result)


def on_change_gear_info(index: int):
    gear_config = st.session_state['gear_config']
    
    if gear_config["level"].count(int(st.session_state[f"selectbox_gear_info_level_{index}"])) == 0:
        st.session_state["gears_info"][index].level = -1
    else:
        st.session_state["gears_info"][index].level = int(st.session_state[f"selectbox_gear_info_level_{index}"])
    
    st.session_state["gears_info"][index].rank = gear_config["rank"].get(st.session_state[f"selectbox_gear_info_rank_{index}"], "")

    if gear_config["enhance"].count(int(st.session_state[f"selectbox_gear_info_enhance_{index}"])) == 0:
        st.session_state["gears_info"][index].enhance = -1
    else:
        st.session_state["gears_info"][index].enhance = int(st.session_state[f"selectbox_gear_info_enhance_{index}"])
    
    st.session_state["gears_info"][index].gear = gear_config["gear"].get(st.session_state[f"selectbox_gear_info_gear_{index}"], "")
    st.session_state["gears_info"][index].set = gear_config["set"].get(st.session_state[f"selectbox_gear_info_set_{index}"], "")

    st.session_state["gears_info"][index].main.type = gear_config["stat_type"].get(st.session_state[f"selectbox_gear_info_main_type_{index}"], "")

    st.session_state["gears_info"][index].main.value = int(st.session_state[f"selectbox_gear_info_main_value_{index}"])
    for j in range(4):
        st.session_state["gears_info"][index].substats[j].type = gear_config["stat_type"].get(st.session_state[f"selectbox_gear_info_substats_type_{index}_{j}"], "")
        st.session_state["gears_info"][index].substats[j].value = int(st.session_state[f"selectbox_gear_info_substats_value_{index}_{j}"])


# @st.cache_resource
def load_json_file(json_file_path: str):
    with open(json_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ocr_digit(image: Image, reader: easyocr.Reader, plus_symbol_interval=0, percentage_symbol_interval=0) -> str:
    output_image(image)
    symbols = ["+", ",", "%"]
    has_symbols = [False for _ in symbols]

    for i, symbol in enumerate(symbols):
        if i == 0:
            if plus_symbol_interval != 0:
                result = reader.readtext(np.asarray(image.crop([0, 0, plus_symbol_interval, image.size[1]])), allowlist=symbol)
            else:
                result = None
        elif i == 2:
            if percentage_symbol_interval != 0:
                result = reader.readtext(np.asarray(image.crop([image.size[0] - percentage_symbol_interval, 0, image.size[0], image.size[1]])), allowlist=symbol)
            else:
                result = None
        else:
            result = reader.readtext(np.asarray(image), allowlist=symbol)
        output_result(result)
        if result != [] and result is not None:
            if result[0][2] > 0.50:
                has_symbols[i] = True

    if has_symbols[0]:
        result = reader.readtext(np.asarray(image.crop([image.size[0] - plus_symbol_interval, 0, image.size[0], image.size[1]])), allowlist="0123456789")
    elif has_symbols[1]:
        result = reader.readtext(np.asarray(image), allowlist="0123456789,")
    elif has_symbols[2]:
        result = reader.readtext(np.asarray(image.crop([0, 0, image.size[0] - percentage_symbol_interval, image.size[1]])), allowlist="0123456789")
    else:
        result = reader.readtext(np.asarray(image), allowlist="0123456789")

    output_result(result)
    if result != [] and result is not None:
        if result[0][2] > 0.50:
            result_value = result[0][1]
            if has_symbols[0]:
                result_value = "+" + result_value
            elif has_symbols[1]:
                result_value = re.findall("\d+", result_value)
            elif has_symbols[2]:
                result_value = result_value + "%"
            return str(result_value)
        else:
            return "-1"
    else:
        return "-1"


def ocr_str(image: Image, reader: easyocr.Reader, gear_config: Dict, allowlist_key: str) -> str:
    output_image(image)
    result = reader.readtext(np.asarray(image), allowlist="".join(gear_config[allowlist_key].keys()))
    output_result(result)
    if result != [] and result is not None:
        return result[0][1]
    else:
        return "空值"


def ocr(image: Image, reader: easyocr.Reader, gear_crop_config: Dict, gear_config: Dict) -> GearInfo:
    gear_info = GearInfo()

    ocr_image = image.crop(gear_crop_config["ocr_border"])
    draw = ImageDraw.Draw(ocr_image)

    for item in gear_crop_config["fill_white"]:
        draw.rectangle(item, fill=(255, 255, 255))

    output_image(image)

    result = ocr_digit(ocr_image.crop(gear_crop_config["level"]), reader)
    if gear_config["level"].count(int("".join(re.findall("-?\d+", result)))) == 0:
        gear_info.level = -1
    else:
        gear_info.level = int("".join(re.findall("-?\d+", result)))
    output_result(result)

    result = ocr_digit(ocr_image.crop(gear_crop_config["enhance"]), reader, plus_symbol_interval=30)
    if gear_config["enhance"].count(int("".join(re.findall("-?\d+", result)))) == 0:
        gear_info.enhance = -1
    else:
        gear_info.enhance = int("".join(re.findall("-?\d+", result)))
    output_result(result)

    result = ocr_str(ocr_image.crop(gear_crop_config["rank"]), reader, st.session_state["gear_config"], "rank")
    gear_info.rank = gear_config["rank"].get(result, "")
    output_result(result)

    result = ocr_str(ocr_image.crop(gear_crop_config["gear"]), reader, st.session_state["gear_config"], "gear")
    gear_info.gear = gear_config["gear"].get(result, "")
    output_result(result)

    result = ocr_str(ocr_image.crop(gear_crop_config["set"]), reader, st.session_state["gear_config"], "set")
    gear_info.set = gear_config["set"].get(result, "")
    output_result(result)

    result = ocr_str(ocr_image.crop(gear_crop_config["main_type"]), reader, st.session_state["gear_config"], "stat_type")
    gear_info.main.type = gear_config["stat_type"].get(result, "")
    output_result(result)

    result = ocr_digit(ocr_image.crop(gear_crop_config["main_value"]), reader, percentage_symbol_interval=55)
    if "%" in result:
        if gear_info.main.type in ["Health", "Attack", "Defense"]:
            gear_info.main.type = gear_info.main.type + "Percent"
    output_result(result)
    gear_info.main.value = int("".join(re.findall("-?\d+", result)))

    for i in range(4):
        substat_crop_interval = (gear_crop_config["substats_type"][3] - gear_crop_config["substats_type"][1]) // 4
        substat_crop_box = [
            gear_crop_config["substats_type"][0],
            gear_crop_config["substats_type"][1] + i * substat_crop_interval,
            gear_crop_config["substats_type"][2],
            gear_crop_config["substats_type"][1] + (i + 1) * substat_crop_interval,
        ]
        result = ocr_str(ocr_image.crop(substat_crop_box), reader, st.session_state["gear_config"], "stat_type")
        output_result(result)
        gear_info.substats[i].type = gear_config["stat_type"].get(result, "")

    for i in range(4):
        substat_crop_interval = (gear_crop_config["substats_value"][3] - gear_crop_config["substats_value"][1]) // 4
        substat_crop_box = [
            gear_crop_config["substats_value"][0],
            gear_crop_config["substats_value"][1] + i * substat_crop_interval,
            gear_crop_config["substats_value"][2],
            gear_crop_config["substats_value"][1] + (i + 1) * substat_crop_interval,
        ]
        result = ocr_digit(ocr_image.crop(substat_crop_box), reader, percentage_symbol_interval=50)
        if "%" in result:
            if gear_info.substats[i].type in ["Health", "Attack", "Defense"]:
                gear_info.substats[i].type = gear_info.substats[i].type + "Percent"
        output_result(result)
        gear_info.substats[i].value = int("".join(re.findall("-?\d+", result)))

    return gear_info


def build_gears_info_ui(uploaded_images, gears_info: List[GearInfo]):
    for i, (uploaded_image, gear_info) in enumerate(zip(uploaded_images, gears_info)):
        col_1, col_2 = st.columns(2)
        with col_1:
            image = Image.open(uploaded_image)
            st.image(image.crop([32, 180, 505, 1075]), use_column_width=True)

        with col_2:
            col_2_1, col_2_2 = st.columns(2)
            with col_2_1:
                st.selectbox(
                    label="装备等级",
                    key=f"selectbox_gear_info_level_{i}",
                    options=st.session_state["gear_config"]["level"],
                    index=st.session_state["gear_config"]["level"].index(gear_info.level),
                    on_change=on_change_gear_info,
                    kwargs={'index':i},
                )
                st.selectbox(
                    label="装备品质",
                    key=f"selectbox_gear_info_rank_{i}",
                    options=st.session_state["gear_config"]["rank"].keys(),
                    index=list(st.session_state["gear_config"]["rank"].values()).index(gear_info.rank),
                    on_change=on_change_gear_info,
                    kwargs={'index':i},
                )

            with col_2_2:
                st.selectbox(
                    label="装备强化",
                    key=f"selectbox_gear_info_enhance_{i}",
                    options=st.session_state["gear_config"]["enhance"],
                    index=st.session_state["gear_config"]["enhance"].index(gear_info.enhance),
                    on_change=on_change_gear_info,
                    kwargs={'index':i},
                )

                st.selectbox(
                    label="装备类型",
                    key=f"selectbox_gear_info_gear_{i}",
                    options=st.session_state["gear_config"]["gear"].keys(),
                    index=list(st.session_state["gear_config"]["gear"].values()).index(gear_info.gear),
                    on_change=on_change_gear_info,
                    kwargs={'index':i},
                )

            st.selectbox(
                label="装备套装",
                key=f"selectbox_gear_info_set_{i}",
                options=st.session_state["gear_config"]["set"].keys(),
                index=list(st.session_state["gear_config"]["set"].values()).index(gear_info.set),
                on_change=on_change_gear_info,
                kwargs={'index':i},
            )

            col_2_3, col_2_4 = st.columns(2)
            with col_2_3:
                st.selectbox(
                    "装备主属性",
                    options=st.session_state.gear_config["stat_type"].keys(),
                    key=f"selectbox_gear_info_main_type_{i}",
                    index=list(st.session_state.gear_config["stat_type"].values()).index(gear_info.main.type),
                    on_change=on_change_gear_info,
                    kwargs={'index':i},
                )
                for j, item in enumerate(gear_info.substats):
                    st.selectbox(
                        label=f"装备副属性{j+1}",
                        options=st.session_state.gear_config["stat_type"].keys(),
                        key=f"selectbox_gear_info_substats_type_{i}_{j}",
                        index=list(st.session_state.gear_config["stat_type"].values()).index(item.type),
                        on_change=on_change_gear_info,
                        kwargs={'index':i},
                    )
            with col_2_4:
                st.number_input("装备主属性的值", step=1, key=f"selectbox_gear_info_main_value_{i}", value=gear_info.main.value, on_change=on_change_gear_info, kwargs={'index':i})
                for j, item in enumerate(gear_info.substats):
                    st.number_input(label=f"装备副属性{j+1}的值", step=1, value=item.value, key=f"selectbox_gear_info_substats_value_{i}_{j}", on_change=on_change_gear_info, kwargs={'index':i})
        
        st.button(label="当前装备数据保存", key=f"save_gear_{i}", use_container_width=True, on_click=save_gear, kwargs={'index': i})

def save_gear(index):
    st.session_state.export['items'].append(st.session_state.gears_info[index].__dict__)

def main():
    st.title("第七史诗装备导入器")

    st.info('装备强化评估和分级评估请到https://e7.d3tekim.top/')
    st.info('该网站仅用于和Fribble配装器进行对接，支持批量截图OCR')
    
    uploaded_images = st.file_uploader(label="上传装备截图（可单张/多张上传）", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

    json_string = json.dumps(st.session_state.export)
    st.download_button(label="所有装备结果导出", data=json_string, file_name="export.json", mime="application/json", key="download", use_container_width=True)

    if uploaded_images is not None:
        for uploaded_image in uploaded_images:
            if uploaded_image not in st.session_state["uploaded_images"]:
                st.session_state["uploaded_images"].append(uploaded_image)
                st.session_state["reader_tasks"].append(False)
                st.session_state["gears_info"].append(None)
            else:
                pass
        for i, uploaded_image in enumerate(st.session_state["uploaded_images"]):
            if uploaded_image not in uploaded_images:
                del st.session_state["uploaded_images"][i]
                del st.session_state["reader_tasks"][i]
                del st.session_state["gears_info"][i]
            else:
                pass
    else:
        st.session_state["uploaded_images"] = []
        st.session_state["reader_tasks"] = []
        st.session_state["gears_info"] = []

    # TEST
    # for reader_task, uploaded_image in zip(st.session_state['reader_tasks'], st.session_state['uploaded_images']):
    #     st.text(f'{reader_task}, {uploaded_image}')

    if st.session_state["uploaded_images"] is not None:
        for i, uploaded_image in stqdm(
            enumerate(st.session_state["uploaded_images"]),
            total=len(st.session_state["uploaded_images"]),
            desc="OCR识别中...",
        ):
            if not st.session_state["reader_tasks"][i]:
                st.session_state["gears_info"][i] = ocr(Image.open(uploaded_image), st.session_state["reader"], st.session_state["gear_crop_config"], st.session_state["gear_config"])

                st.session_state["reader_tasks"][i] = True
            else:
                pass

        build_gears_info_ui(st.session_state["uploaded_images"], st.session_state["gears_info"])

    


if __name__ == "__main__":
    if "gear_config" not in st.session_state:
        st.session_state["gear_config"] = load_json_file("./config/gear_config.json")

    if "gear_crop_config" not in st.session_state:
        st.session_state["gear_crop_config"] = load_json_file("./config/gear_crop_config.json")

    if "reader" not in st.session_state:
        st.session_state["reader"] = easyocr.Reader(["en", "ch_sim"], gpu=True)
        st.session_state["reader_tasks"] = []
        st.session_state["gears_info"] = []

    if "uploaded_images" not in st.session_state:
        st.session_state["uploaded_images"] = []

    if "debug" not in st.session_state:
        st.session_state["debug"] = False

    if "export" not in st.session_state:
        st.session_state.export = {"heroes": [], "items": []}

    main()
