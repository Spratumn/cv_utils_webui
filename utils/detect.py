import os
import re
import json
from io import BytesIO
from PIL import Image
import streamlit as st

from .main import TMP_DIR, TMP_IMAGE_DIR, TMP_IMAGE_PATH


WEIGHT_DIR = '/home/orangepi/weights/det'
TOOLKITS = '/home/orangepi/CCode/BOARD_TEST_TOOL/toolkits/bin/det_mot'


DET_CFG_PATH = os.path.join(TMP_DIR, 'detection.json')


arch_type_dict = {
    'yolox': 0,
    'damoyolo': 1,
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
}

strides_dict = {
    'yolox': [4, 8, 16, 32],
    'damoyolo': [8, 16, 32]

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
    if config['weight_name'] == 'None': return False
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
    with open(DET_CFG_PATH, 'wt') as f:
        f.write(json.dumps(json_config, indent=4))
    return True


def detect_image(config, image:Image):
    if not write_detect_config(config):
        st.error('Invalid config settings!')
        return None, None
    image.save(TMP_IMAGE_PATH)
    cmd_str = f'{TOOLKITS} --source_path {TMP_IMAGE_DIR} --det_cfg_path {DET_CFG_PATH}'
    cmd_str +=  ' --save_to_video 0 --no_log 1 --run_mot 0 --save_to_sequence 1 --save_to_txt 0'
    if not config['draw_label']:
        cmd_str +=  ' --draw_label 0'
    with st.spinner('Running Detection with the given image...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
    result_image_path = TMP_IMAGE_DIR + '-det/tmp.jpg'
    if not os.path.exists(result_image_path):
        st.error('Run detection error!')
        return None, None
    return Image.open(result_image_path), info_str


def detect_video(config, video, det_num):
    if not write_detect_config(config):
        st.error('Invalid config settings!')
        return None, None
    suffix = video.name.split('.')[-1]
    video_path = TMP_DIR + f'/tmp.{suffix}'
    byte_video = video.getvalue()
    with open(video_path, 'wb') as f:
        f.write(byte_video)

    cmd_str = f'{TOOLKITS} --source_path "{video_path}" --det_cfg_path "{DET_CFG_PATH}"'
    cmd_str +=  ' --save_to_video 1 --no_log 1 --run_mot 0 --save_to_sequence 0 --save_to_txt 0'
    if det_num > 0:
        cmd_str += f' --run_frame_num {det_num}'
    if not config['draw_label']:
        cmd_str +=  ' --draw_label 0'
    with st.spinner('Running Detection with the given video...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
        result_video_path = TMP_DIR + f'/tmp.{suffix}-det.mp4'
        if not os.path.exists(result_video_path):
            st.error('Run detection error!')
            return None, None
        return open(result_video_path, 'rb'), info_str


def detect_sequence(config, image_dir, det_num, save_to_txt=False):
    if not os.path.exists(image_dir):
        st.error('Invalid sequence directory!')
        return None, None
    if not write_detect_config(config):
        st.error('Invalid config settings!')
        return None, None
    cmd_str = f'{TOOLKITS} --source_path "{image_dir}" --det_cfg_path "{DET_CFG_PATH}"'
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