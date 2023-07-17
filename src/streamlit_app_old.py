import streamlit as st
from data import GearItem, Substats, Main
from PIL import Image
import numpy as np
import pandas as pd

from button_func import (
    clear_gear_info,
    ocr_screenshot,
    on_change_gear_info,
    on_change_classify_stragety,
    on_change_enhance_stragety,
    analyze_enhance,
    analyze_classify,
    save_gear_item,
    save_multi_gear_item
)
from pathlib import Path
import json


@st.cache_resource
def load_gear_config(gear_config_path: Path):
    with open(gear_config_path, "r", encoding="utf-8") as f:
        gear_config = json.load(f)
        return gear_config


@st.cache_resource
def load_enhance_stragety_config(enhance_stragety_config: Path):
    with open(enhance_stragety_config, "r", encoding="utf-8") as f:
        enhance_strategy_dict = json.load(f)
    return enhance_strategy_dict


@st.cache_resource
def load_classify_stragety_config(classify_stragety_config: Path):
    with open(classify_stragety_config, "r", encoding="utf-8") as f:
        classify_strategy_dict = json.load(f)
    return classify_strategy_dict


def main():
    st.title("第七史诗装备导入器")

    st.warning("【1920*1080】模拟器【320dpi】全屏截取【管理装备】页面的装备")
    screenshot = st.file_uploader("【1920*1080】模拟器【320dpi】全屏截取【管理装备】页面的装备", label_visibility="collapsed")
    if screenshot is not None:
        screenshot = Image.open(screenshot)
        chopped_screenshot = screenshot.crop([35, 190, 500, 885 + 190])
        st.session_state.screenshot = screenshot
    else:
        chopped_screenshot = Image.fromarray(np.ones([885, 465]).astype("uint8"), "L")

    gear_info_row = [item for item in st.columns(2)]

    with gear_info_row[0]:
        st.markdown("装备截图")
        st.image(chopped_screenshot)

    with gear_info_row[1]:
        st.markdown("识别结果")

        gear_info_row_top_left, gear_info_row_top_right = st.columns(2)

        with gear_info_row_top_left:
            try:
                st.selectbox(
                    "装备类型",
                    options=st.session_state.gear_config["gear"],
                    key="selectbox_gear_gear",
                    index=list(st.session_state.gear_config["gear"].values()).index(st.session_state.gear_info.gear),
                    on_change=on_change_gear_info,
                )
            except Exception as e:
                st.session_state['selectbox_gear_gear'] = list(st.session_state.gear_config["gear"].values())[0]

            try:    
                st.selectbox(
                    "装备品质",
                    options=st.session_state.gear_config["rank"],
                    key="selectbox_gear_rank",
                    index=list(st.session_state.gear_config["rank"].values()).index(st.session_state.gear_info.rank),
                    on_change=on_change_gear_info,
                )
            except Exception as e:
                st.session_state['selectbox_gear_rank'] = list(st.session_state.gear_config["rank"].values())[0]

            try:
                st.selectbox(
                    "装备强化",
                    options=st.session_state.gear_config["enhance"],
                    key="selectbox_gear_enhance",
                    index=st.session_state.gear_config["enhance"].index(st.session_state.gear_info.enhance),
                    on_change=on_change_gear_info,
                )
            except Exception as e:
                st.session_state['selectbox_gear_enhance'] = st.session_state.gear_config["enhance"][0]

        with gear_info_row_top_right:
            try:
                st.selectbox(
                    "装备等级",
                    options=st.session_state.gear_config["level"],
                    key="selectbox_gear_level",
                    index=st.session_state.gear_config["level"].index(st.session_state.gear_info.level),
                    on_change=on_change_gear_info,
                )
            except Exception as e:
                st.session_state['selectbox_gear_level'] = st.session_state.gear_config["level"][0]

            try:
                st.selectbox(
                    "装备套装",
                    options=st.session_state.gear_config["set"],
                    key="selectbox_gear_set",
                    index=list(st.session_state.gear_config["set"].values()).index(st.session_state.gear_info.set),
                    on_change=on_change_gear_info,
                )
            except Exception as e:
                st.session_state['selectbox_gear_set'] = list(st.session_state.gear_config["set"].values())[0]

        gear_info_row_middle_left, gear_info_row_middle_right = st.columns(2)

        with gear_info_row_middle_left:
            try:
                st.selectbox(
                    "装备主属性",
                    options=st.session_state.gear_config["stat_type"].keys(),
                    key="selectbox_main_type",
                    index=list(st.session_state.gear_config["stat_type"].values()).index(st.session_state.gear_info.main.type),
                    on_change=on_change_gear_info,
                )
            except Exception as e:
                st.session_state["selectbox_main_type"] = list(st.session_state.gear_config["stat_type"].values())[0]

        with gear_info_row_middle_right:
            try:
                st.number_input("装备主属性的值", step=1, key="selectbox_main_value", value=st.session_state.gear_info.main.value, on_change=on_change_gear_info)
            except Exception as e:
                st.session_state['selectbox_main_value'] = 0

        gear_info_row_bottom_left, gear_info_row_bottom_right = st.columns(2)

        with gear_info_row_bottom_left:
            for i, item in enumerate(st.session_state.gear_info.substats):
                try:
                    st.selectbox(
                        label=f"装备副属性{i+1}",
                        options=st.session_state.gear_config["stat_type"].keys(),
                        key=f"selectbox_gear_substats_type_{i}",
                        index=list(st.session_state.gear_config["stat_type"].values()).index(st.session_state.gear_info.substats[i].type),
                        on_change=on_change_gear_info,
                    )
                except Exception as e:
                    st.session_state[f'selectbox_gear_substats_type_{i}'] = list(st.session_state.gear_config["stat_type"].values())[0]

        with gear_info_row_bottom_right:
            for i, item in enumerate(st.session_state.gear_info.substats):
                try:
                    st.number_input(
                        label=f"装备副属性{i+1}的值", step=1, value=item.value, key=f"selectbox_gear_substats_value_{i}", on_change=on_change_gear_info
                    )
                except Exception as e:
                    st.session_state[f'selectbox_gear_substats_value_{i}'] = -1

    strategy_setting_row = [item for item in st.columns(2)]

    with strategy_setting_row[0]:
        st.markdown("强化评估策略")
        st.selectbox(
            label="强化评估策略",
            options=st.session_state.enhance_strategy_dict.keys(),
            label_visibility="collapsed",
            key="selectbox_enhance_strategy",
            on_change=on_change_enhance_stragety,
            index=7,
        )

    with strategy_setting_row[1]:
        st.markdown("分级评估策略")
        st.selectbox(
            label="分级评估策略",
            options=st.session_state.classify_strategy_dict.keys(),
            label_visibility="collapsed",
            key="selectbox_classify_strategy",
            on_change=on_change_classify_stragety,
            index=1,
        )

    control_row = [item for item in st.columns(6)]
    with control_row[0]:
        st.button(label="识别当前装备数据", key="0", use_container_width=True, on_click=ocr_screenshot)
    with control_row[1]:
        btn_1 = st.button(label="清空当前装备数据", key="1", use_container_width=True, on_click=clear_gear_info)
    with control_row[2]:
        st.button(label="当前装备强化评估", key="2", use_container_width=True, on_click=analyze_enhance)
    with control_row[3]:
        st.button(label="当前装备分级评估", key="3", use_container_width=True, on_click=analyze_classify)
    with control_row[4]:
        st.button(label="当前装备数据保存", key="4", use_container_width=True, on_click=save_gear_item)
    with control_row[5]:
        json_string = json.dumps(st.session_state.export)
        st.download_button(label="所有装备结果导出", data=json_string, file_name="export.json", mime="application/json", key="5", use_container_width=True)

    st.info(st.session_state.info, icon="ℹ️")

    st.markdown(f'{st.session_state["selectbox_enhance_strategy"]}')
    enhance_strategy_df = pd.DataFrame(np.array(st.session_state.enhance_stragety), index=["+0","+3","+6","+9"])
    enhance_strategy_df.columns = ["红装速度","红装装备分数","紫装速度","紫装装备分数"]
    st.table(enhance_strategy_df)

    st.markdown(f'{st.session_state["selectbox_classify_strategy"]}')
    classify_str = [f'- {key}: {value}' for key, value in st.session_state.classify_stragety.items()]
    st.markdown('\n'.join(classify_str))

    multi_screenshots = st.file_uploader("【1920*1080】模拟器【320dpi】全屏截取【管理装备】页面的装备", label_visibility="collapsed", accept_multiple_files=True)
    if multi_screenshots is not None:
        st.session_state.multi_screenshots = multi_screenshots

    st.button(label="多个装备数据保存", key="multi_button", use_container_width=True, on_click=save_multi_gear_item)



if __name__ == "__main__":
    st.session_state.gear_config = load_gear_config(Path("./config/gear_config.json"))
    st.session_state.enhance_strategy_dict = load_enhance_stragety_config(Path("./config/enhance_strategy_config.json"))
    st.session_state.classify_strategy_dict = load_classify_stragety_config(Path("./config/classify_strategy_config.json"))
    if "info" not in st.session_state:
        st.session_state.info = ""
    if "gear_info" not in st.session_state:
        st.session_state["gear_info"] = GearItem()
        st.session_state.gear_info.substats = [Substats() for _ in range(4)]
        st.session_state.gear_info.main = Main()
    if "enhance_stragety" not in st.session_state:
        st.session_state.enhance_stragety = st.session_state.enhance_strategy_dict["方案18：兼顾速度和高分装备方案"]
    if "classify_stragety" not in st.session_state:
        st.session_state.classify_stragety = st.session_state.classify_strategy_dict["方案2：阿吉"]

    if "export" not in st.session_state:
        st.session_state.export = {"heroes": [], "items": []}

    main()
