import streamlit as st

from utils.mot import *
from utils.detect import *

st.title(":mag_right: 多目标跟踪")

if 'det_config' not in st.session_state:
    st.session_state.det_config = DEFAULT_DET_CONFIG


def arch_type_changed():
    update_detect_config(st.session_state.det_config, arch_type=st.session_state.arch_type)
    update_candidate_weights(st.session_state.det_config)


def target_type_changed():
    update_detect_config(st.session_state.det_config, target_type=st.session_state.det_target_type)
    update_candidate_weights(st.session_state.det_config)


def model_size_changed():
    update_detect_config(st.session_state.det_config, model_size=st.session_state.det_model_size)
    update_candidate_weights(st.session_state.det_config)


st.subheader(':gear: 检测器参数配置')
cfg_c11, cfg_c12, cfg_c13, cfg_c14 = st.columns(4)
with cfg_c11:
    arch_type = st.selectbox('算法模型:',
                             tuple(ARCH_TYPE.keys()),
                             index=ARCH_TYPE[st.session_state.det_config['arch_type']],
                             on_change=arch_type_changed, key='arch_type')
with cfg_c12:
    det_target_type = st.selectbox('目标检测任务:',
                               tuple(DET_TARGET_TYPE.keys()),
                               index=DET_TARGET_TYPE[st.session_state.det_config['target_type']],
                               on_change=target_type_changed,
                               key='det_target_type')
with cfg_c13:
    score_thresh = st.slider('检测器置信度:', 0.1, 1.0, st.session_state.det_config['score_thresh'], step=0.05)
with cfg_c14:
    det_model_size = st.selectbox('模型尺寸:',
                              tuple(DET_MODEL_SIZE.keys()),
                              index=DET_MODEL_SIZE[st.session_state.det_config['model_size']],
                              on_change=model_size_changed,
                              key='det_model_size')

# update_candidate_weights(st.session_state.det_config)

cfg_c21, cfg_c22, cfg_c23 = st.columns([2, 1, 1])
with cfg_c21:
    candidate_weight_name = st.selectbox('选择模型权重',
                                        st.session_state.det_config['candidate_weights'])
with cfg_c22:
    iou_thresh = st.slider('检测器IOU阈值:', 0.3, 1.0, st.session_state.det_config['iou_thresh'], step=0.05)

with cfg_c23:
    cfg_c231, cfg_c232 = st.columns(2)
    with cfg_c231:
        rgb_input = st.checkbox('RGB input', st.session_state.det_config['rgb_input'])
        nms_in_same_class = st.checkbox('同类别NMS', st.session_state.det_config['nms_in_same_class'])
    with cfg_c232:
        draw_label = st.checkbox('绘制目标标签', st.session_state.det_config['draw_label'])


update_detect_config(st.session_state.det_config,
                     score_thresh=score_thresh,
                     iou_thresh=iou_thresh,
                     rgb_input=rgb_input,
                     nms_in_same_class=nms_in_same_class,
                     draw_label=draw_label,
                     weight_name=candidate_weight_name
                     )

cfg_c31, cfg_c32, *_ = st.columns(4)
with cfg_c31:
    max_detect_count = st.number_input('最大检测目标数量:',
                                        max_value=500, min_value=1, value=mot_params['max_detect_count'])
with cfg_c32:
    lag_frame_num = st.number_input('检测器的模拟滞后帧数:',
                                    max_value=10, min_value=0, value=mot_params['lag_frame_num'])



st.subheader(':gear: 多目标参数配置')

cfg_c41, cfg_c42, cfg_c43, cfg_c44 = st.columns(4)
with cfg_c41:
    mot_track_type = st.selectbox('跟踪器类型:',
                                  tuple(mot_track_type_dict.keys()),
                                  mot_track_type_dict[mot_config['mot_track_type']])
    distance_type = st.selectbox('匹配距离类型:',
                                 tuple(distance_type_dict.keys()),
                                 distance_type_dict[mot_config['distance_type']])
with cfg_c42:
    max_track_nums = st.number_input('最大跟踪数量:',
                                     max_value=100, min_value=1, value=mot_config['max_track_nums'])
    max_track_id = st.number_input('最大跟踪ID:',
                                     max_value=500, min_value=1, value=mot_config['max_track_id'])
with cfg_c43:
    confidence_thresh = st.slider('多目标跟踪目标置信度:', 0.3, 1.0, mot_config['confidence_thresh'], step=0.05)
    distance_thresh = st.slider('匹配距离阈值:', 0.3, 1.0, mot_config['distance_thresh'], step=0.05)
with cfg_c44:
    st.write('')
    st.write('')
    st.write('')
    lag_compensate = st.checkbox('开启滞后补偿:', value=mot_config['lag_compensate'])
    match_with_velocity = st.checkbox('使用速度信息辅助跟踪:', mot_config['match_with_velocity'])
    class_diff_type = st.checkbox('使用目标类别信息辅助跟踪:', mot_config['class_diff_type'])


st.subheader(':gear: 跟踪器内部参数配置')
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

st.subheader(':camera: 视频帧多目标跟踪')
cfg_c71, *_ = st.columns(4)
with cfg_c71:
    mot_frame_num = st.number_input('运行多目标跟踪的视频帧数:', max_value=5000, min_value=0, value=0)
st.write("选择并上传一个mp4格式的视频文件，然后逐帧做多目标跟踪.")

video_upload = st.file_uploader("上传视频", type=["mp4",], label_visibility='hidden')
if video_upload is not None:
    st.write("原视频:")
    st.video(video_upload.read())

video_c1,  video_c2 = st.columns(2)
if st.button("运行多目标跟踪 :point_left:"):
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
        mot_results, mot_info = mot_on_video(mot_params, mot_config,
                                             st.session_state.det_config,
                                             video_upload, mot_frame_num)

        if mot_info is not None:
            st.info(mot_info)
            with video_c1:
                if mot_results['det_video'] is not None:
                    st.write("目标检测结果:")
                    st.video(mot_results['det_video'].read())

            with video_c2:
                if mot_results['mot_video'] is not None:
                    st.write("多目标跟踪结果:")
                    st.video(mot_results['mot_video'].read())

        with st.expander("详细检测和跟踪结果"):
            txt_c1,  txt_c2 = st.columns(2)
            with txt_c1:
                if mot_results['det_txt'] is not None:
                            st.write("目标检测:")
                            st.dataframe(mot_results['det_txt'])
            with txt_c2:
                if mot_results['mot_txt'] is not None:
                            st.write("多目标跟踪:")
                            st.dataframe(mot_results['mot_txt'])

    else:
        st.error('请先上传一个视频，然后再点击 “运行多目标跟踪” 按钮')








