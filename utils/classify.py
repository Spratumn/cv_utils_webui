import os
import re
import json
from io import BytesIO
from PIL import Image
import streamlit as st

from .main import TMP_DIR, TMP_IMAGE_DIR, TMP_IMAGE_PATH


WEIGHT_DIR = '/home/orangepi/weights/cls'
TOOLKITS = '/home/orangepi/CCode/BOARD_TEST_TOOL/toolkits/bin/cls'


CLS_CFG_PATH = os.path.join(TMP_DIR, 'cls.json')


target_type_dict = {
    'forestfire': 0
}

def paras_target_type(target_type):
    if target_type == 'forestfire':
        return ["no-fire", "fire"]


model_size_dict = {
    '512-512': 0,
}


cls_config = {
    "target_type": 'forestfire',
    "model_size": '512-512',
    "label_names": ["no-fire", "fire"],
    "candidate_weights": ('None',),
    "weight_name": None
}


def update_cls_config(cls_config, **kwargs):
    for key in kwargs:
        if key not in cls_config: continue
        if key in ('target_type', 'model_size',
                   'weight_name',
                   ):
            cls_config[key] = kwargs[key]

    cls_config['label_names'] = paras_target_type(cls_config['target_type'])


def update_candidate_weights(config):
    weight_name_fmt = f'{config["target_type"]}_v\d+_{config["model_size"]}'
    candidate_weights = []
    for weight_name in os.listdir(WEIGHT_DIR):
        if re.match(weight_name_fmt, weight_name): candidate_weights.append(weight_name)
    config["candidate_weights"] = tuple(candidate_weights) if len(candidate_weights) else ('None', )


def convert_image(image:Image):
    buf = BytesIO()
    image.save(buf, format="PNG")
    byte_image = buf.getvalue()
    return byte_image


def write_cls_config(config):
    if config['weight_name'] == 'None': return False
    json_config = {
        "model_path": os.path.join(WEIGHT_DIR, config['weight_name']),
        "label_names": config['label_names']
    }
    with open(CLS_CFG_PATH, 'wt') as f:
        f.write(json.dumps(json_config, indent=4))
    return True


def classify_image(config, image:Image):
    if not write_cls_config(config):
        st.error('Invalid config settings!')
        return None, None
    image.save(TMP_IMAGE_PATH)
    cmd_str = f'{TOOLKITS} --source_path {TMP_IMAGE_DIR} --cls_cfg_path {CLS_CFG_PATH}'
    cmd_str +=  ' --save_to_video 0 --no_log 1 --save_to_sequence 1 --save_to_txt 0'
    with st.spinner('Running classification with the given image...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
    result_image_path = TMP_IMAGE_DIR + '-cls/tmp.jpg'
    if not os.path.exists(result_image_path):
        st.error('Run classification error!')
        return None, None
    return Image.open(result_image_path), info_str


def classify_video(config, video, cls_num):
    if not write_cls_config(config):
        st.error('Invalid config settings!')
        return None, None
    suffix = video.name.split('.')[-1]
    video_path = TMP_DIR + f'/tmp.{suffix}'
    byte_video = video.getvalue()
    with open(video_path, 'wb') as f:
        f.write(byte_video)

    cmd_str = f'{TOOLKITS} --source_path "{video_path}" --cls_cfg_path "{CLS_CFG_PATH}"'
    cmd_str +=  ' --save_to_video 1 --no_log 1 --save_to_sequence 0 --save_to_txt 0'
    if cls_num > 0:
        cmd_str += f' --run_frame_num {cls_num}'
    with st.spinner('Running classification with the given video...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
        result_video_path = TMP_DIR + f'/tmp.{suffix}-cls.mp4'
        if not os.path.exists(result_video_path):
            st.error('Run classification error!')
            return None, None
        return open(result_video_path, 'rb'), info_str


def classify_sequence(config, image_dir, cls_num):
    if not os.path.exists(image_dir):
        st.error('Invalid sequence directory!')
        return None, None
    if not write_cls_config(config):
        st.error('Invalid config settings!')
        return None, None
    cmd_str = f'{TOOLKITS} --source_path "{image_dir}" --cls_cfg_path "{CLS_CFG_PATH}"'
    cmd_str +=  ' --save_to_video 0 --no_log 1 --save_to_sequence 1 --save_to_txt 0'
    if cls_num > 0:
        cmd_str += f' --run_frame_num {cls_num}'
    with st.spinner('Classifying with the given sequence...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
    return True, info_str