import os
import re
import json
from io import BytesIO
from PIL import Image
import streamlit as st
import time
import shutil

from .main import CFG_DIR, IMAGE_DIR, VIDEO_DIR


WEIGHT_DIR = '/home/orangepi/weights/det'
TOOLKITS = '/home/orangepi/CCode/BOARD_TEST_TOOL/toolkits/bin/det_mot'


arch_type_dict = {
    'yolox': 0,
    'damoyolo': 1,
    'yolov8': 2,
}

target_type_dict = {
    'person-vehicle': 0,
    'ship': 1,
    'multi-targets': 2,
    'person-vehicle-chestring': 3
}

def paras_target_type(target_type):
    if target_type == 'multi-targets':
        return ["Person", "Land Vehicle", "Air Vehicle", "Water Vehicle", "Animal", "Bird"]
    return target_type.split('-')


model_size_dict = {
    '960-576': 0,
    '704-416': 1,
    '640-384': 2,
    '576-352': 3,
    '640-640': 4,
}

strides_dict = {
    'yolox': [4, 8, 16, 32],
    'damoyolo': [8, 16, 32],
    'yolov8': [8, 16, 32]

}


detect_config = {
    "arch_type": 'yolox',
    "target_type": 'person-vehicle',
    "model_size": '960-576',
    "nms_in_same_class": True,
    "score_thresh": 0.5,
    "iou_thresh": 0.5,
    "strides": [4, 8, 16, 32],
    "label_names": ["Person", "Vehicle"],
    "candidate_weights": ('None',),
    "weight_name": None,
    "rgb_input": False,
    "draw_label": True
}


def update_detect_config(detect_config, **kwargs):
    for key in kwargs:
        if key not in detect_config: continue
        if key in ('arch_type', 'target_type', 'model_size', 'rgb_input',
                   'score_thresh', 'iou_thresh', 'nms_in_same_class',
                   'weight_name', 'draw_label'
                   ):
            detect_config[key] = kwargs[key]

    detect_config['label_names'] = paras_target_type(detect_config['target_type'])


def update_candidate_weights(config):
    weight_name_fmt = f'{config["arch_type"]}_v\d+_{config["target_type"]}_{config["model_size"]}'
    candidate_weights = []
    for weight_name in os.listdir(WEIGHT_DIR):
        if re.match(weight_name_fmt, weight_name): candidate_weights.append(weight_name)
    config["candidate_weights"] = tuple(candidate_weights) if len(candidate_weights) else ('None', )


def convert_image(image:Image):
    buf = BytesIO()
    image.save(buf, format="PNG")
    byte_image = buf.getvalue()
    return byte_image


def write_detect_config(config):
    if config['weight_name'] == 'None': return None
    model_width, model_height = [int(v) for v in config['model_size'].split('-')]
    json_config = {
        "model_path": os.path.join(WEIGHT_DIR, config['weight_name']),
        "arch_type": arch_type_dict[config['arch_type']],
        "model_width": model_width,
        "model_height": model_height,
        "rgb_input": config['rgb_input'],
        "nms_in_same_class": 1 if config['nms_in_same_class'] else 0,
        "score_thresh": config['score_thresh'],
        "iou_thresh": config['iou_thresh'],
        "strides": strides_dict[config['arch_type']],
        "label_names": config['label_names']
    }
    time_uid = str(time.time())
    cur_cfg_path = os.path.join(CFG_DIR, f'{time_uid}.json')
    with open(cur_cfg_path, 'wt') as f:
        f.write(json.dumps(json_config, indent=4))
    return time_uid


def detect_image(config, image:Image, imagename):
    time_uid = write_detect_config(config)
    if time_uid is None:
        st.error('Invalid config settings!')
        return None, None
    cur_cfg_path = os.path.join(CFG_DIR, f'{time_uid}.json')
    cur_image_dir = os.path.join(IMAGE_DIR, time_uid)
    if not os.path.exists(cur_image_dir): os.mkdir(cur_image_dir)
    image.save(os.path.join(cur_image_dir, imagename))
    cmd_str = f'{TOOLKITS} --source_path {cur_image_dir} --det_cfg_path {cur_cfg_path}'
    cmd_str +=  ' --save_to_video 0 --no_log 1 --run_mot 0 --save_to_sequence 1 --save_to_txt 0'
    if not config['draw_label']:
        cmd_str +=  ' --draw_label 0'
    with st.spinner('Running Detection with the given image...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
    result_image_path = result_image_path = cur_image_dir + f'-det/{imagename}'
    if not os.path.exists(result_image_path):
        st.error('Run detection error!')
        return None, None
    result_image = Image.open(result_image_path)
    os.remove(cur_cfg_path)
    shutil.rmtree(cur_image_dir)
    shutil.rmtree(cur_image_dir + '-det')
    return result_image, info_str


def detect_video(config, video, det_num):
    time_uid = write_detect_config(config)
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

    cmd_str = f'{TOOLKITS} --source_path "{video_path}" --det_cfg_path "{cur_cfg_path}"'
    cmd_str +=  ' --save_to_video 1 --no_log 1 --run_mot 0 --save_to_sequence 0 --save_to_txt 0'
    if det_num > 0:
        cmd_str += f' --run_frame_num {det_num}'
    if not config['draw_label']:
        cmd_str +=  ' --draw_label 0'
    with st.spinner('Running Detection with the given video...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
        result_video_path = os.path.join(cur_video_dir, f'{video.name}-det.mp4')
        if not os.path.exists(result_video_path):
            st.error('Run detection error!')
            return None, None
        result_video = open(result_video_path, 'rb')
        os.remove(cur_cfg_path)
        shutil.rmtree(cur_video_dir)
        return result_video, info_str


def detect_sequence(config, image_dir, det_num, save_to_txt=False):
    if not os.path.exists(image_dir):
        st.error('Invalid sequence directory!')
        return None, None
    time_uid = write_detect_config(config)
    if time_uid is None:
        st.error('Invalid config settings!')
        return None, None
    cur_cfg_path = os.path.join(CFG_DIR, f'{time_uid}.json')
    cmd_str = f'{TOOLKITS} --source_path "{image_dir}" --det_cfg_path "{cur_cfg_path}"'
    cmd_str +=  ' --no_log 1 --run_mot 0 --save_to_sequence 1'
    if det_num > 0:
        cmd_str += f' --run_frame_num {det_num}'
    if save_to_txt:
        cmd_str += '  --save_to_txt 1'
    else:
        cmd_str += '  --save_to_txt 0'
    if not config['draw_label']:
        cmd_str +=  ' --draw_label 0'
    with st.spinner('Detecting with the given sequence...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
    return True, info_str