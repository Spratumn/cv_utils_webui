import os
import json
import pandas as pd
import streamlit as st
import time
import shutil

from .main import CFG_DIR, VIDEO_DIR
from .detect import write_detect_config

TOOLKITS = '/home/orangepi/CCode/BOARD_TEST_TOOL/toolkits/bin/det_mot'


mot_params = {
    'max_detect_count': 100,
    'lag_frame_num': 0,
    'draw_label': 1
}


distance_type_dict = {
    'iou': 0,
    'giou': 1,
}

mot_track_type_dict = {
    'simpletrack': 0,
    'bytetrack': 1,
}




mot_config = {
    "confidence_thresh": 0.6,
    "distance_thresh": 0.5,
    "image_width": -1,
    "image_height": -1,
    "max_track_nums": 10,
    "max_track_id": 15,
    "distance_type": 'giou',
    "mot_track_type": 'bytetrack',
    "class_diff_type": True,
    "lag_compensate": False,
    "match_with_velocity": False,
    "strack_class_nums": 2,
    "strack_activate_frame_nums": 3,
    "strack_sleep_frame_nums": 8,
    "strack_dead_frame_nums":  18,
    "strack_miss_increse": 3,
    "strack_smooth_window_size": 7,
    "strack_smooth_window_loc": 21,
    "strack_smooth_window_class": 11,
    "strack_lag_frame_nums": 0,
    "strack_velocity_thresh": 12,
    "strack_min_target_size": 2,
    "strack_max_target_scale": 7
}


def update_mot_params(mot_params, **kwargs):
    for key in kwargs:
        if key not in mot_params: continue
        mot_params[key] = kwargs[key]


def update_mot_config(mot_config, **kwargs):
    for key in kwargs:
        if key not in mot_config: continue
        mot_config[key] = kwargs[key]


def write_mot_config(mot_config):
    time_uid = str(time.time())
    cur_mot_cfg_path = os.path.join(CFG_DIR, f'{time_uid}.json')
    with open(cur_mot_cfg_path, 'wt') as f:
        f.write(json.dumps(mot_config, indent=4))
    return time_uid

def mot_on_video(params, config, detect_config, video, run_frame_num):
    config_to_save = {}
    config_to_save.update(config)
    config_to_save["distance_type"] = distance_type_dict[config["distance_type"]]
    config_to_save["mot_track_type"] = mot_track_type_dict[config["mot_track_type"]]
    config_to_save["class_diff_type"] = 1 if config["class_diff_type"] else 0
    config_to_save["lag_compensate"] = 1 if config["lag_compensate"] else 0
    config_to_save["match_with_velocity"] = 1 if config["match_with_velocity"] else 0
    time_uid_mot = write_mot_config(config_to_save)
    time_uid_det = write_detect_config(detect_config)
    if time_uid_det is None:
        st.error('Invalid det config settings!')
        return None, None
    cur_mot_cfg_path = os.path.join(CFG_DIR, f'{time_uid_mot}.json')
    cur_det_cfg_path = os.path.join(CFG_DIR, f'{time_uid_det}.json')
    cur_video_dir = os.path.join(VIDEO_DIR, time_uid_mot)
    if not os.path.exists(cur_video_dir): os.mkdir(cur_video_dir)
    video_path = os.path.join(cur_video_dir, video.name)
    byte_video = video.getvalue()
    with open(video_path, 'wb') as f:
        f.write(byte_video)

    cmd_str = f'{TOOLKITS} --source_path "{video_path}" --det_cfg_path "{cur_det_cfg_path}" --mot_cfg_path "{cur_mot_cfg_path}"'
    cmd_str +=  ' --save_to_video 1 --no_log 1 --run_mot 1 --save_to_sequence 0'
    if run_frame_num > 0:
        cmd_str += f'  --run_frame_num {run_frame_num}'
    cmd_str += f'  --save_to_txt 1'
    cmd_str += f'  --max_detect_count {params["max_detect_count"]}'
    cmd_str += f'  --lag_frame_num {params["lag_frame_num"]}'
    if not params['draw_label']:
        cmd_str +=  ' --draw_label 0'
    with st.spinner('Running MOT with the given video...'):
        info_str = "".join(os.popen(cmd_str).readlines()[-1])
        results = {
            'det_video': cur_video_dir + f'/{video.name}-det.mp4',
            'mot_video': cur_video_dir + f'/{video.name}-mot.mp4',
            'det_txt': cur_video_dir + f'/{video.name}_det.txt',
            'mot_txt': cur_video_dir + f'/{video.name}_mot.txt',
        }
        mot_succeed = False
        for key, result_path in results.items():
            if not os.path.exists(result_path):
                results[key] = None
            else:
                if result_path.endswith('.mp4'):
                    results[key] = open(result_path, 'rb')
                elif result_path.endswith('.txt'):
                    results[key] = pd.read_csv(result_path,
                                                  names=['frame_id', 'track_id', 'x', 'y', 'w', 'h', 'class_id', 'score'],
                                                  header=None)
                mot_succeed = True
        if mot_succeed:
            os.remove(cur_mot_cfg_path)
            os.remove(cur_det_cfg_path)
            shutil.rmtree(cur_video_dir)
            return results, info_str
        return None, None
