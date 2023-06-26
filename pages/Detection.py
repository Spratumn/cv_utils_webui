import streamlit as st
from PIL import Image

from utils.detect import *

st.title(":mag_right: Detection")
st.subheader(':gear: Detection Config')


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
    score_thresh = st.slider('Score Thresh:', 0.1, 1.0, detect_config['score_thresh'], step=0.05)
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
    iou_thresh = st.slider('IOU Thresh:', 0.3, 1.0, detect_config['iou_thresh'], step=0.05)

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


st.subheader(':film_frames: Detect image')
st.write(
    "Try uploading an image to run detection, Full quality images can be downloaded from the sidebar."
)
detect_succeed = False
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
    if st.button("Detect Image :point_left:"):
        if image_upload is not None:
            result_image, info = detect_image(detect_config, image)
            if result_image is not None:
                image_col2.write("Result:")
                image_col2.image(result_image)
                detect_succeed = True
        else:
            st.error('Please upload an image and then click "Detect Image" button.')
with image_c3:
    if detect_succeed:
        st.download_button("Download reuslt image", convert_image(result_image), "reuslt.png", "image/png")
if detect_succeed:st.info(info)

st.subheader(':camera: Detect Video')
st.write(
    "Try uploading a video to run detection, Full quality video can be downloaded from the sidebar."
)
video_det_num = st.number_input('Number of frames to detect :', max_value=5000, min_value=-1, value=-1)
detect_succeed = False
video_col1, video_col2 = st.columns(2)
video_upload = st.file_uploader("Upload a video", type=["mp4",], label_visibility='hidden')
if video_upload is not None:
    # video_file = open(image_upload)
    video_col1.write("Original:")
    video_col1.video(video_upload.read())

video_c2, _, video_c3, _ = st.columns([2, 2, 2, 2])
with video_c2:

    if st.button("Detect Video :point_left:"):
        if video_upload is not None:
            result_video, info = detect_video(detect_config, video_upload, video_det_num)
            if result_video is not None:
                video_col2.write("Result:")
                video_col2.video(result_video.read())
                detect_succeed = True
        else:
            st.error('Please upload a video and then click "Detect Video" button.')
with video_c3:
    if detect_succeed:
        st.download_button("Download reuslt video", result_video, f"det_reuslt_{video_upload.name}", "video/mp4")
if detect_succeed:st.info(info)


st.subheader(':file_folder: Detect Sequence')
st.write(
    "Try selecting an image folder run detection, The result images can be found in the image folder."
)
with st.form("Detect Sequence"):
    seq_c1, seq_c2, seq_c3 = st.columns(3)
    with seq_c1:
        image_dir = st.text_input('Select image directory:')
    with seq_c2:
        image_det_num = st.number_input('Number of images to detect :', max_value=5000, min_value=-1, value=-1)
    with seq_c3:
        save_to_txt = st.checkbox('Save to txt', False)
    if st.form_submit_button("Detect Sequence :point_left:"):
        ret, info = detect_sequence(detect_config, image_dir, det_num=image_det_num,
                                    save_to_txt=save_to_txt)
        if ret:st.info(info)



