import streamlit as st

from utils.classify import *

st.title(":mag_right: 图像分类")
st.subheader(':gear: 图像分类参数配置')


if 'cls_config' not in st.session_state:
    st.session_state.cls_config = DEFAULT_CLS_CONFIG


def target_type_changed():
    update_cls_config(st.session_state.cls_config, target_type=st.session_state.cls_target_type)
    update_candidate_weights(st.session_state.cls_config)


def model_size_changed():
    update_cls_config(st.session_state.cls_config, model_size=st.session_state.cls_model_size)
    update_candidate_weights(st.session_state.cls_config)



cfg_c11, cfg_c12, *_ = st.columns(4)

with cfg_c11:
    cls_target_type = st.selectbox('分类任务:',
                                   tuple(CLS_TARGET_TYPE.keys()),
                                   index=CLS_TARGET_TYPE[st.session_state.cls_config['target_type']],
                                   on_change=target_type_changed,
                                   key='cls_target_type')
with cfg_c12:
    cls_model_size = st.selectbox('模型尺寸:',
                                  tuple(CLS_MODEL_SIZE.keys()),
                                  index=CLS_MODEL_SIZE[st.session_state.cls_config['model_size']],
                                  on_change=model_size_changed,
                                  key='cls_model_size')

# update_candidate_weights(st.session_state.cls_config)

cfg_c21, *_ = st.columns([2, 1, 1])
with cfg_c21:
    candidate_weight_name = st.selectbox('选择模型权重',
                                         st.session_state.cls_config['candidate_weights'])
    rgb_input = st.checkbox('RGB input', st.session_state.cls_config['rgb_input'])
update_cls_config(st.session_state.cls_config, weight_name=candidate_weight_name, rgb_input=rgb_input)


st.subheader(':film_frames: 单图像分类')
st.write("选择并上传一张图像，运行图像分类任务.")
cls_succeed = False
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
    if st.button("运行单图像分类 :point_left:"):
        if image_upload is not None:
            result_image, info = classify_image(st.session_state.cls_config, image, image_upload.name)
            if result_image is not None:
                image_col2.write("分类结果:")
                image_col2.image(result_image)
                cls_succeed = True
        else:
            st.error('请先上传一张图像，然后再点击 “运行单图像分类” 按钮')
with image_c3:
    if cls_succeed:
        st.download_button("下载分类结果图像",
                           convert_image(result_image),
                           f"cls_reuslt_{image_upload.name}", "image/png")
if cls_succeed:st.info(info)

st.subheader(':camera: 视频帧分类')
st.write("选择并上传一个mp4格式的视频文件，然后逐帧做图像分类")
video_det_num = st.number_input('运行分类的视频帧数:', max_value=5000, min_value=-1, value=-1)
cls_succeed = False
video_col1, video_col2 = st.columns(2)
video_upload = st.file_uploader("上传视频", type=["mp4",], label_visibility='hidden')
if video_upload is not None:
    # video_file = open(image_upload)
    video_col1.write("原视频:")
    video_col1.video(video_upload.read())

video_c2, _, video_c3, _ = st.columns([2, 2, 2, 2])
with video_c2:
    if st.button("运行视频帧分类:point_left:"):
        if video_upload is not None:
            result_video, info = classify_video(st.session_state.cls_config, video_upload, video_det_num)
            if result_video is not None:
                video_col2.write("分类结果:")
                video_col2.video(result_video.read())
                cls_succeed = True
        else:
            st.error('请先上传一个视频，然后再点击 “运行视频帧分类” 按钮')
with video_c3:
    if cls_succeed:
        st.download_button("下载结果视频",
                           result_video,
                           f"cls_reuslt_{video_upload.name}", "video/mp4")
if cls_succeed:st.info(info)


st.subheader(':file_folder: 图像序列分类')
st.write("选择服务器上的一个图像文件夹，批量运行图像分类.")
with st.form("图像序列分类"):
    image_dir = st.text_input('输入图像文件夹路径:')
    image_cls_num = st.number_input('运行分类的图像数:', max_value=5000, min_value=-1, value=-1)

    if st.form_submit_button("运行图像序列分类:point_left:"):
        ret, info = classify_sequence(st.session_state.cls_config, image_dir, cls_num=image_cls_num)
        if ret:st.info(info)