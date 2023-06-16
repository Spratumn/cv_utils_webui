import streamlit as st

from utils.classify import *

st.title(":mag_right: Classification")
st.subheader(':gear: Classification Config')


def target_type_changed():
    global cls_config
    update_cls_config(cls_config, target_type=st.session_state.cls_target_type)
    update_candidate_weights(cls_config)


def model_size_changed():
    global cls_config
    update_cls_config(cls_config, model_size=st.session_state.cls_model_size)
    update_candidate_weights(cls_config)



cfg_c11, cfg_c12, *_ = st.columns(4)

with cfg_c11:
    target_type = st.selectbox('Target Type:',
                               tuple(target_type_dict.keys()), index=target_type_dict[cls_config['target_type']],
                               on_change=target_type_changed, key='cls_target_type')
with cfg_c12:
    model_size = st.selectbox('Model Size:',
                              tuple(model_size_dict.keys()), index=model_size_dict[cls_config['model_size']],
                              on_change=model_size_changed, key='cls_model_size')

update_candidate_weights(cls_config)

cfg_c21, *_ = st.columns([2, 1, 1])
with cfg_c21:
    candidate_weight_name = st.selectbox('Select model to run classification',
                                         cls_config['candidate_weights'])

update_cls_config(cls_config, weight_name=candidate_weight_name)


st.subheader(':film_frames: Classify image')
st.write(
    "Try uploading an image to run classification, Full quality images can be downloaded from the sidebar."
)
cls_succeed = False
image_col1, image_col2 = st.columns(2)
image_upload = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], label_visibility='hidden')
if image_upload is not None:
    image = Image.open(image_upload)
    image_col1.write("Original:")
    image_col1.image(image)
else:
    image = None
image_c2, image_c3 = st.columns(2)
with image_c2:
    if st.button("Classify Image :point_left:"):
        if image_upload is not None:
            result_image, info = classify_image(cls_config, image)
            if result_image is not None:
                image_col2.write("Result:")
                image_col2.image(result_image)
                cls_succeed = True
        else:
            st.error('Please upload an image and then click "Classify Image" button.')
with image_c3:
    if cls_succeed:
        st.download_button("Download reuslt image", convert_image(result_image), "reuslt.png", "image/png")
if cls_succeed:st.info(info)

st.subheader(':camera: Classify Video')
st.write(
    "Try uploading a video to run classification, Full quality video can be downloaded from the sidebar."
)
video_det_num = st.number_input('Number of frames to classify :', max_value=5000, min_value=-1, value=-1)
cls_succeed = False
video_col1, video_col2 = st.columns(2)
video_upload = st.file_uploader("Upload a video", type=["mp4",], label_visibility='hidden')
if video_upload is not None:
    # video_file = open(image_upload)
    video_col1.write("Original:")
    video_col1.video(video_upload.read())

video_c2, _, video_c3, _ = st.columns([2, 2, 2, 2])
with video_c2:

    if st.button("Classify Video :point_left:"):
        if video_upload is not None:
            result_video, info = classify_video(cls_config, video_upload, video_det_num)
            if result_video is not None:
                video_col2.write("Result:")
                video_col2.video(result_video.read())
                cls_succeed = True
        else:
            st.error('Please upload a video and then click "Classify Video" button.')
with video_c3:
    if cls_succeed:
        st.download_button("Download reuslt video", result_video, f"cls_reuslt_{video_upload.name}", "video/mp4")
if cls_succeed:st.info(info)


st.subheader(':file_folder: Classify Sequence')
st.write(
    "Try selecting an image folder run classification, The result images can be found in the image folder."
)
with st.form("Classify Sequence"):
    image_dir = st.text_input('Select image directory:')
    image_cls_num = st.number_input('Number of images to classify :', max_value=5000, min_value=-1, value=-1)

    if st.form_submit_button("Classify Sequence :point_left:"):
        ret, info = classify_sequence(cls_config, image_dir, cls_num=image_cls_num)
        if ret:st.info(info)