import streamlit as st
from PIL import Image

from utils.detect import *

st.title(":mag_right: 目标检测")
st.subheader(':gear: 目标检测参数配置')


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



cfg_c11, cfg_c12, cfg_c13, cfg_c14 = st.columns(4)
with cfg_c11:
    arch_type = st.selectbox('算法模型:',
                             tuple(ARCH_TYPE.keys()),
                             index=ARCH_TYPE[st.session_state.det_config['arch_type']],
                             on_change=arch_type_changed,
                             key='arch_type')
with cfg_c12:
    det_target_type = st.selectbox('目标检测任务:',
                                tuple(DET_TARGET_TYPE.keys()),
                                index=DET_TARGET_TYPE[st.session_state.det_config['target_type']],
                                on_change=target_type_changed,
                                key='det_target_type')
with cfg_c13:
    score_thresh = st.slider('目标置信度:', 0.1, 1.0, st.session_state.det_config['score_thresh'], step=0.05)
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
    iou_thresh = st.slider('IOU阈值:', 0.3, 1.0, st.session_state.det_config['iou_thresh'], step=0.05)

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


st.subheader(':film_frames: 单图像目标检测')
st.write(
    "选择并上传一张图像，运行目标检测任务."
)
detect_succeed = False
image_col1, image_col2 = st.columns(2)
image_upload = st.file_uploader("上传一张图像", type=["png", "jpg", "jpeg"], label_visibility='hidden')
if image_upload is not None:
    image = Image.open(image_upload)
    image_col1.write("原图:")
    image_col1.image(image)
else:
    image = None
image_c2, image_c3 = st.columns(2)
with image_c2:
    if st.button("单图像检测 :point_left:"):
        if image_upload is not None:
            result_image, info = detect_image(st.session_state.det_config, image, image_upload.name)
            if result_image is not None:
                image_col2.write("检测结果:")
                image_col2.image(result_image)
                detect_succeed = True
        else:
            st.error('请先上传一张图像，然后再点击 “运行单图像检测” 按钮')
with image_c3:
    if detect_succeed:
        st.download_button("下载检测结果图像",
                           convert_image(result_image),
                           f"det_reuslt_{image_upload.name}", "image/png")
if detect_succeed:st.info(info)

st.subheader(':camera: 视频帧检测')
st.write(
    "选择并上传一个mp4格式的视频文件，然后逐帧做目标检测"
)
video_det_num = st.number_input('运行目标检测的视频帧数 :', max_value=5000, min_value=-1, value=-1)
detect_succeed = False
video_col1, video_col2 = st.columns(2)
video_upload = st.file_uploader("上传视频", type=["mp4",], label_visibility='hidden')
if video_upload is not None:
    # video_file = open(image_upload)
    video_col1.write("原视频:")
    video_col1.video(video_upload.read())

video_c2, _, video_c3, _ = st.columns([2, 2, 2, 2])
with video_c2:

    if st.button("运行视频帧检测 :point_left:"):
        if video_upload is not None:
            result_video, info = detect_video(st.session_state.det_config, video_upload, video_det_num)
            if result_video is not None:
                video_col2.write("检测结果:")
                video_col2.video(result_video.read())
                detect_succeed = True
        else:
            st.error('请先上传一个视频，然后再点击 “运行视频帧检测” 按钮')
with video_c3:
    if detect_succeed:
        st.download_button("下载结果视频", result_video, f"det_reuslt_{video_upload.name}", "video/mp4")
if detect_succeed:st.info(info)


st.subheader(':file_folder: 图像序列检测')
st.write("选择服务器上的一个图像文件夹，批量运行目标检测.")
with st.form("图像序列检测"):
    seq_c1, seq_c2, seq_c3 = st.columns(3)
    with seq_c1:
        image_dir = st.text_input('输入图像文件夹路径:')
    with seq_c2:
        image_det_num = st.number_input('运行检测的图像数:', max_value=5000, min_value=-1, value=-1)
    with seq_c3:
        save_to_txt = st.checkbox('保存txt', False)
    if st.form_submit_button("运行图像序列检测 :point_left:"):
        ret, info = detect_sequence(st.session_state.det_config, image_dir, det_num=image_det_num,
                                    save_to_txt=save_to_txt)
        if ret:st.info(info)



