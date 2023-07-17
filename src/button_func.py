import streamlit as st
from PIL import ImageDraw, Image
import easyocr
import numpy as np
import json
from interpreter import build_gear
from data import GearItem, Substats, Main

def save_gear_item():
    st.session_state.export['items'].append(st.session_state.gear_info.__dict__)
    st.session_state.info = f'已经保存当前装备数据，目前保存的装备总共有{len(st.session_state.export["items"])}个'

def download():
    pass

def save_multi_gear_item():
    for screenshot_item in st.session_state.multi_screenshots:
        screenshot = Image.open(screenshot_item)

        st.session_state.screenshot = screenshot
        ocr_screenshot()
        st.session_state.export['items'].append(st.session_state.gear_info.__dict__)



def on_change_enhance_stragety():
    st.session_state.enhance_stragety = st.session_state.enhance_strategy_dict[st.session_state["selectbox_enhance_strategy"]]


def on_change_classify_stragety():
    st.session_state.classify_stragety = st.session_state.classify_strategy_dict[st.session_state["selectbox_classify_strategy"]]


def analyze_enhance():
    st.session_state.info = ""

    gear_score = calc_gear_score()
    speed = 0
    for i in range(4):
        if st.session_state.gear_info.substats[i].type == "Speed":
            speed = st.session_state.gear_info.substats[i].value

    row_index = st.session_state.gear_config["enhance"].index(st.session_state.gear_info.enhance)
    if row_index <=9:
        if row_index <3:
            row_index = 0
        elif row_index < 6:
            row_index =3
        elif row_index < 9:
            row_index = 6
        elif row_index == 9:
            row_index = 9
        if st.session_state.gear_info.rank == "Epic":
            if (speed - st.session_state.enhance_stragety[row_index][0]) >= 0 or (gear_score - st.session_state.enhance_stragety[row_index][1]) >= 0:
                st.session_state.info = f"【可以】进一步强化，判断条件为【装备速度{speed}】大于等于【{st.session_state.enhance_stragety[row_index][0]}】或【装备分{gear_score}】大于等于【{st.session_state.enhance_stragety[row_index][1]}】"
            else:
                st.session_state.info = f"【无需】进一步强化，判断条件为【装备速度{speed}】大于等于【{st.session_state.enhance_stragety[row_index][0]}】或【装备分{gear_score}】大于等于【{st.session_state.enhance_stragety[row_index][1]}】"
        elif st.session_state.gear_info.rank == "Heroic":
            if (speed - st.session_state.enhance_stragety[row_index][2]) >= 0 or (gear_score - st.session_state.enhance_stragety[row_index][3]) >= 0:
                st.session_state.info = f"【可以】进一步强化，判断条件为【装备速度{speed}】大于等于【{st.session_state.enhance_stragety[row_index][2]}】或【装备分{gear_score}】大于等于【{st.session_state.enhance_stragety[row_index][3]}】"
            else:
                st.session_state.info = f"【无需】进一步强化，判断条件为【装备速度{speed}】大于等于【{st.session_state.enhance_stragety[row_index][2]}】或【装备分{gear_score}】大于等于【{st.session_state.enhance_stragety[row_index][3]}】"
    else:
        st.session_state.info = f"当前装备已经强化到+{st.session_state.gear_info.enhance}或强化程度未知，【装备分{gear_score}】，不需要进行强化评估"


def analyze_classify():
    st.session_state.info = ""
    gear_score = calc_gear_score()
    speed = 0
    for i in range(4):
        if st.session_state.gear_info.substats[i].type == "Speed":
            speed = st.session_state.gear_info.substats[i].value

    if st.session_state.gear_info.enhance != 15:
        st.session_state.info = f"只评估+15的85级装备，当前装备等级为{st.session_state.gear_info.enhance}"
    else:
        if len(list(st.session_state.classify_stragety.items())) == 5:
            for key, value in st.session_state.classify_stragety.items():
                if gear_score >= value[0] and gear_score <= value[1]:
                    st.session_state.info += f'该装备的【装备分{gear_score}】满足【{key}】条件{value}'
                    break
            else:
                st.session_state.info += f'该装备的【装备分{gear_score}】过低，低于最小评级标准分数【{list(st.session_state.classify_stragety.items())[0][1][0]}】'
        else:
            if st.session_state.gear_info.rank == 'Epic':
                for key, value in st.session_state.classify_stragety["红装"].items():
                    if gear_score >= value[0] and gear_score <= value[1]:
                        st.session_state.info += f'该装备的【装备分{gear_score}】满足【{key}】条件{value}'
                        break
                else:
                    st.session_state.info += f'该装备的【装备分{gear_score}】过低，低于最小评级标准分数【{list(st.session_state.classify_stragety["红装"].items())[0][1][0]}】'
            if st.session_state.gear_info.rank == 'Heroic':
                for key, value in st.session_state.classify_stragety["紫装"].items():
                    if gear_score >= value[0] and gear_score <= value[1]:
                        st.session_state.info += f'该装备的【装备分{gear_score}】满足【{key}】条件{value}'
                        break
                else:
                    st.session_state.info += f'该装备的【装备分{gear_score}】过低，低于最小评级标准分数【{list(st.session_state.classify_stragety["紫装"].items())[0][1][0]}】'
        if speed >= 19:
            st.session_state.info += f'该装备的【速度{speed}】较高，可以保留'


def calc_gear_score():
    gear_score = 0
    for i in range(4):
        if st.session_state.gear_info.substats[i].type == "CriticalHitChancePercent":
            gear_score += st.session_state.gear_info.substats[i].value * 1.5
        elif st.session_state.gear_info.substats[i].type == "CriticalHitDamagePercent":
            gear_score += st.session_state.gear_info.substats[i].value * 1.1
        elif st.session_state.gear_info.substats[i].type == "Speed":
            gear_score += st.session_state.gear_info.substats[i].value * 2
        elif st.session_state.gear_info.substats[i].type == "Health":
            gear_score += st.session_state.gear_info.substats[i].value / 50
        elif st.session_state.gear_info.substats[i].type == "Attack":
            gear_score += st.session_state.gear_info.substats[i].value / 9
        elif st.session_state.gear_info.substats[i].type == "Defense":
            gear_score += st.session_state.gear_info.substats[i].value / 6
        else:
            if st.session_state.gear_info.substats[i].value > 0:
                gear_score += st.session_state.gear_info.substats[i].value

    gear_score = np.floor(gear_score)
    return gear_score


def on_change_gear_info():
    st.session_state.gear_info.gear = st.session_state.gear_config["gear"][st.session_state["selectbox_gear_gear"]]
    st.session_state.gear_info.rank = st.session_state.gear_config["rank"][st.session_state["selectbox_gear_rank"]]
    st.session_state.gear_info.enhance = int(st.session_state["selectbox_gear_enhance"])
    st.session_state.gear_info.level = int(st.session_state["selectbox_gear_level"])
    st.session_state.gear_info.set = st.session_state.gear_config["set"][st.session_state["selectbox_gear_set"]]
    st.session_state.gear_info.main.type = st.session_state.gear_config["stat_type"][st.session_state["selectbox_main_type"]]
    st.session_state.gear_info.main.value = int(st.session_state["selectbox_main_value"])
    for i in range(4):
        st.session_state.gear_info.substats[i].type = st.session_state.gear_config["stat_type"][st.session_state[f"selectbox_gear_substats_type_{i}"]]
        st.session_state.gear_info.substats[i].value = int(st.session_state[f"selectbox_gear_substats_value_{i}"])


def ocr_screenshot():
    reader = easyocr.Reader(["en", "ch_sim"], gpu=False)

    with open("./config/allowlist.json", "r", encoding="utf-8") as f:
        allowlist = json.load(f)
        allowlist = "".join(set(allowlist))

    screenshot = st.session_state.screenshot.crop([35, 190, 500, 790])
    draw = ImageDraw.Draw(screenshot)
    for item in [[0, 480, 475, 540], [180, 75, 500, 200]]:
        draw.rectangle(item, fill=(255, 255, 255))

    result = []
    for item in reader.detect(np.asarray(screenshot))[0][0]:
        box = [item[0], item[2], item[1], item[3]]
        screenshot_item = screenshot.crop(box)
        st.image(screenshot_item)

        is_percentage = False
        if box[0] > 320:
            w, h = screenshot_item.size[0], screenshot_item.size[1]
            percentage_w = 30 if box[1] > 290 else 35

            if w > percentage_w:
                is_percentage_ocr_result = reader.readtext(np.asarray(screenshot_item.crop([w - percentage_w, 0, w, h])), allowlist="%")
                # st.text(f"MAYBE %, {is_percentage_ocr_result}")
                if is_percentage_ocr_result != []:
                    if "%" in is_percentage_ocr_result[0][1]:
                        is_percentage = True

        if is_percentage:
            result_item = reader.readtext(np.asarray(screenshot_item.crop([0, 0, w - percentage_w, h])), allowlist=allowlist, text_threshold=0.5)[0][1] + "%"
        else:
            result_item = reader.readtext(np.asarray(screenshot_item), allowlist=allowlist, text_threshold=0.5)[0][1]

        result.append(result_item)

    st.session_state["gear_info"] = build_gear(result)

    st.session_state.info = ''


def clear_gear_info():
    st.session_state["gear_info"] = GearItem()
    st.session_state["gear_info"].substats = [Substats() for _ in range(4)]
    st.session_state["gear_info"].main = Main()

    st.session_state.info = ''

    # st.session_state['selectbox_gear_gear'] = '空值'
    # st.session_state['selectbox_gear_rank'] = '空值'
    # st.session_state['selectbox_gear_enhance'] = -1
    # st.session_state['selectbox_gear_level'] = -1
    # st.session_state['selectbox_gear_set'] = '空值'
    # st.session_state['selectbox_main_type'] = '空值'
    # st.session_state['selectbox_main_value'] = 0
    # for i in range(4):
    #     st.session_state[f'selectbox_gear_substats_type_{i}'] = '空值'
    #     st.session_state[f'selectbox_gear_substats_value_{i}'] = 0
