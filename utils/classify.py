import os
import re
import json
from io import BytesIO
from PIL import Image
import streamlit as st
import time
import shutil

from .main import CFG_DIR, IMAGE_DIR, VIDEO_DIR


WEIGHT_DIR = '/home/orangepi/weights/cls'
TOOLKITS = '/home/orangepi/CCode/BOARD_TEST_TOOL/toolkits/bin/cls'
LABEL_TXT_DIR = '/home/orangepi/CCode/BOARD_TEST_TOOL/toolkits/configs'



target_type_dict = {
    'forestfire': 0,
    'imagenet': 1
}

def paras_target_type(target_type):
    with open(os.path.join(LABEL_TXT_DIR, f'{target_type}.txt'), 'r') as f:
        lines = f.readlines()
    return [line.rstrip('\n').split(', ')[1] for line in lines]


model_size_dict = {
    '512-512': 0,
    '224-224': 1,
}


cls_config = {
    "target_type": 'forestfire',
    "model_size": '512-512',
    "label_names": ["no-fire", "fire"],
    "candidate_weights": ('None',),
    "weight_name": None,
    "rgb_input": False
}


def update_cls_config(cls_config, **kwargs):
    for key in kwargs:
        if key not in cls_config: continue
        if key in ('target_type', 'model_size',
                   'weight_name', "rgb_input"
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
    if config['weight_name'] == 'None': return None
    json_config = {
        "model_path": os.path.join(WEIGHT_DIR, config['weight_name']),
        "label_names": config['label_names'],
        "rgb_input": config['rgb_input']
    }
    time_uid = str(time.time())
    cur_cfg_path = os.path.join(CFG_DIR, f'{time_uid}.json')
    with open(cur_cfg_path, 'wt') as f:
        f.write(json.dumps(json_config, indent=4))
    return time_uid


def classify_image(config, image:Image, imagename):
    time_uid = write_cls_config(config)
    if time_uid is None:
        st.error('Invalid config settings!')
        return None, None
    cur_cfg_path = os.path.join(CFG_DIR, f'{time_uid}.json')

    cur_image_dir = os.path.join(IMAGE_DIR, time_uid)
    if not os.path.exists(cur_image_dir): os.mkdir(cur_image_dir)
    image.save(os.path.join(cur_image_dir, imagename))
    cmd_str = f'{TOOLKITS} --source_path {cur_image_dir} --cls_cfg_path {cur_cfg_path}'
    cmd_str +=  ' --save_to_video 0 --no_log 1 --save_to_sequence 1 --save_to_txt 0'
    with st.spinner('Running classification with the given image...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
    result_image_path = cur_image_dir + f'-cls/{imagename}'
    if not os.path.exists(result_image_path):
        st.error('Run classification error!')
        return None, None
    result_image = Image.open(result_image_path)
    os.remove(cur_cfg_path)
    shutil.rmtree(cur_image_dir)
    shutil.rmtree(cur_image_dir + '-cls')
    return result_image, info_str


def classify_video(config, video, cls_num):
    time_uid = write_cls_config(config)
    if time_uid is None:
        st.error('Invalid config settings!')
        return None, None
    cur_cfg_path = os.path.join(CFG_DIR, f'{time_uid}.json')

    cur_video_dir = os.path.join(VIDEO_DIR, time_uid)
    if not os.path.exists(cur_video_dir): os.mkdir(cur_video_dir)
    video_path = os.path.join(cur_video_dir, video.name)
    byte_video = video.getvalue()
    with open(video_path, 'wb') as f:
        f.write(byte_video)

    cmd_str = f'{TOOLKITS} --source_path "{video_path}" --cls_cfg_path "{cur_cfg_path}"'
    cmd_str +=  ' --save_to_video 1 --no_log 1 --save_to_sequence 0 --save_to_txt 0'
    if cls_num > 0:
        cmd_str += f' --run_frame_num {cls_num}'
    with st.spinner('Running classification with the given video...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
        result_video_path = os.path.join(cur_video_dir, f'{video.name}-cls.mp4')
        if not os.path.exists(result_video_path):
            st.error('Run classification error!')
            return None, None
        result_video = open(result_video_path, 'rb')
        os.remove(cur_cfg_path)
        shutil.rmtree(cur_video_dir)
        return result_video, info_str


def classify_sequence(config, image_dir, cls_num):
    if not os.path.exists(image_dir):
        st.error('Invalid sequence directory!')
        return None, None
    time_uid = write_cls_config(config)
    if time_uid is None:
        st.error('Invalid config settings!')
        return None, None
    cur_cfg_path = os.path.join(CFG_DIR, f'{time_uid}.json')
    cmd_str = f'{TOOLKITS} --source_path "{image_dir}" --cls_cfg_path "{cur_cfg_path}"'
    cmd_str +=  ' --save_to_video 0 --no_log 1 --save_to_sequence 1 --save_to_txt 0'
    if cls_num > 0:
        cmd_str += f' --run_frame_num {cls_num}'
    with st.spinner('Classifying with the given sequence...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
    return True, info_str