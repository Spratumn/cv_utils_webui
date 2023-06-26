import streamlit as st

from utils.mot import *
from utils.detect import *

st.title(":mag_right: MOT")

def arch_type_changed():
    global detect_config
    update_detect_config(detect_config, arch_type=st.session_state.arch_type)
    update_candidate_weights(detect_config)


def target_type_changed():
    global detect_config
    update_detect_config(detect_config, target_type=st.session_state.target_type)
    update_candidate_weights(detect_config)


def model_size_changed():
    global detect_config
    update_detect_config(detect_config, model_size=st.session_state.model_size)
    update_candidate_weights(detect_config)


st.subheader(':gear: Detector Config')
cfg_c11, cfg_c12, cfg_c13, cfg_c14 = st.columns(4)
with cfg_c11:
    arch_type = st.selectbox('Arch Type:',
                             tuple(arch_type_dict.keys()),
                             index=arch_type_dict[detect_config['arch_type']],
                             on_change=arch_type_changed, key='arch_type')
with cfg_c12:
    target_type = st.selectbox('Target Type:',
                               tuple(target_type_dict.keys()), index=target_type_dict[detect_config['target_type']],
                               on_change=target_type_changed, key='target_type')
with cfg_c13:
    score_thresh = st.slider('Det Score Thresh:', 0.1, 1.0, detect_config['score_thresh'], step=0.05)
with cfg_c14:
    model_size = st.selectbox('Model Size:',
                              tuple(model_size_dict.keys()), index=model_size_dict[detect_config['model_size']],
                              on_change=model_size_changed, key='model_size')

update_candidate_weights(detect_config)

cfg_c21, cfg_c22, cfg_c23 = st.columns([2, 1, 1])
with cfg_c21:
    candidate_weight_name = st.selectbox('Select model to run detection',
                                        detect_config['candidate_weights'])
with cfg_c22:
    iou_thresh = st.slider('Det IOU Thresh:', 0.3, 1.0, detect_config['iou_thresh'], step=0.05)

with cfg_c23:
    cfg_c231, cfg_c232 = st.columns(2)
    with cfg_c231:
        rgb_input = st.checkbox('RGB input', detect_config['rgb_input'])
        nms_in_same_class = st.checkbox('NMS in same class', detect_config['nms_in_same_class'])
    with cfg_c232:
        draw_label = st.checkbox('Draw label', detect_config['draw_label'])


update_detect_config(detect_config,
                     score_thresh=score_thresh,
                     iou_thresh=iou_thresh,
                     rgb_input=rgb_input,
                     nms_in_same_class=nms_in_same_class,
                     draw_label=draw_label,
                     weight_name=candidate_weight_name
                     )

cfg_c31, cfg_c32, cfg_c33, _ = st.columns(4)
with cfg_c31:
    max_detect_count = st.number_input('Max detect nums:',
                                        max_value=500, min_value=1, value=mot_params['max_detect_count'])
with cfg_c32:
    lag_frame_num = st.number_input('Frame lags:',
                                    max_value=10, min_value=0, value=mot_params['lag_frame_num'])

with cfg_c33:
    mot_frame_num = st.number_input('Number of frames to run mot:', max_value=5000, min_value=0, value=0)

st.subheader(':gear: MOT Configs')

cfg_c41, cfg_c42, cfg_c43, cfg_c44 = st.columns(4)
with cfg_c41:
    mot_track_type = st.selectbox('MOT type:',
                                  tuple(mot_track_type_dict.keys()),
                                  mot_track_type_dict[mot_config['mot_track_type']])
    distance_type = st.selectbox('Distance type:',
                                 tuple(distance_type_dict.keys()),
                                 distance_type_dict[mot_config['distance_type']])
with cfg_c42:
    max_track_nums = st.number_input('Max target nums:',
                                     max_value=100, min_value=1, value=mot_config['max_track_nums'])
    max_track_id = st.number_input('Max target id:',
                                     max_value=500, min_value=1, value=mot_config['max_track_id'])
with cfg_c43:
    confidence_thresh = st.slider('MOT Score Thresh:', 0.3, 1.0, mot_config['confidence_thresh'], step=0.05)
    distance_thresh = st.slider('MOT IOU Thresh:', 0.3, 1.0, mot_config['distance_thresh'], step=0.05)
with cfg_c44:
    st.write('')
    st.write('')
    st.write('')
    lag_compensate = st.checkbox('Lag compensate:', value=mot_config['lag_compensate'])
    match_with_velocity = st.checkbox('Match with velocity:', mot_config['match_with_velocity'])
    class_diff_type = st.checkbox('Class diff type:', mot_config['class_diff_type'])


st.subheader(':gear: Strack Configs')
cfg_c61, cfg_c62, cfg_c63, cfg_c64 = st.columns(4)

with cfg_c61:
    strack_activate_frame_nums = st.number_input('Activate frame nums:',
                                        max_value=10, min_value=1, value=mot_config['strack_activate_frame_nums'])
    strack_sleep_frame_nums = st.number_input('Sleep frame_nums:',
                                        max_value=10, min_value=1, value=mot_config['strack_sleep_frame_nums'])
    strack_dead_frame_nums = st.number_input('Dead frame nums:',
                                        max_value=50, min_value=1, value=mot_config['strack_dead_frame_nums'])
with cfg_c62:
    strack_smooth_window_size = st.number_input('Smooth window size:',
                                        max_value=50, min_value=1, value=mot_config['strack_smooth_window_size'])
    strack_smooth_window_loc = st.number_input('Smooth window loc:',
                                        max_value=50, min_value=1, value=mot_config['strack_smooth_window_loc'])
    strack_smooth_window_class = st.number_input('Smooth window class:',
                                        max_value=50, min_value=1, value=mot_config['strack_smooth_window_class'])
with cfg_c63:
    strack_class_nums = st.number_input('Class nums:',
                                        max_value=10, min_value=1, value=mot_config['strack_class_nums'])
    strack_lag_frame_nums = st.number_input('Lag frame nums:',
                                        max_value=10, min_value=0, value=mot_config['strack_lag_frame_nums'])
    strack_miss_increse = st.number_input('Miss increse:',
                                        max_value=10, min_value=0, value=mot_config['strack_miss_increse'])
with cfg_c64:
    strack_velocity_thresh = st.number_input('Velocity thresh:',
                                        max_value=50, min_value=1, value=mot_config['strack_velocity_thresh'])
    strack_min_target_size = st.number_input('Min target size:',
                                        max_value=50, min_value=1, value=mot_config['strack_min_target_size'])
    strack_max_target_scale = st.number_input('Max target scale:',
                                        max_value=50, min_value=1, value=mot_config['strack_max_target_scale'])

st.subheader(':camera: MOT on Video')
st.write(
    "Try uploading a video to run detection, Full quality video can be downloaded from the sidebar."
)



video_upload = st.file_uploader("Upload a video", type=["mp4",], label_visibility='hidden')
if video_upload is not None:
    st.write("Original:")
    st.video(video_upload.read())

video_c1,  video_c2 = st.columns(2)
if st.button("Run MOT :point_left:"):
    if video_upload is not None:
        mot_param_kwargs = {
            'max_detect_count': max_detect_count,
            'lag_frame_num': lag_frame_num,
            'draw_label': draw_label,
        }
        update_mot_params(mot_params, **mot_param_kwargs)
        mot_cfg_kwargs = {
            "confidence_thresh": confidence_thresh,
            "distance_thresh": distance_thresh,
            "max_track_nums": max_track_nums,
            "max_track_id": max_track_id,
            "distance_type": distance_type,
            "mot_track_type": mot_track_type,
            "class_diff_type": class_diff_type,
            "lag_compensate": lag_compensate,
            "match_with_velocity": match_with_velocity,
            "strack_class_nums": strack_class_nums,
            "strack_activate_frame_nums": strack_activate_frame_nums,
            "strack_sleep_frame_nums": strack_sleep_frame_nums,
            "strack_dead_frame_nums":  strack_dead_frame_nums,
            "strack_miss_increse": strack_miss_increse,
            "strack_smooth_window_size": strack_smooth_window_size,
            "strack_smooth_window_loc": strack_smooth_window_loc,
            "strack_smooth_window_class": strack_smooth_window_class,
            "strack_lag_frame_nums": strack_lag_frame_nums,
            "strack_velocity_thresh": strack_velocity_thresh,
            "strack_min_target_size": strack_min_target_size,
            "strack_max_target_scale": strack_max_target_scale
        }
        update_mot_config(mot_config, **mot_cfg_kwargs)
        mot_results, mot_info = mot_on_video(mot_params, mot_config, video_upload, mot_frame_num)

        if mot_info is not None:
            st.info(mot_info)
            with video_c1:
                if mot_results['det_video'] is not None:
                    st.write("Detection result video:")
                    st.video(mot_results['det_video'].read())

            with video_c2:
                if mot_results['mot_video'] is not None:
                    st.write("MOT result video:")
                    st.video(mot_results['mot_video'].read())

        with st.expander("See detial results"):
            txt_c1,  txt_c2 = st.columns(2)
            with txt_c1:
                if mot_results['det_txt'] is not None:
                            st.write("Detection result txt:")
                            st.dataframe(mot_results['det_txt'])
            with txt_c2:
                if mot_results['mot_txt'] is not None:
                            st.write("MOT result txt:")
                            st.dataframe(mot_results['mot_txt'])

    else:
        st.error('Please upload a video and then click "Run MOT" button.')








