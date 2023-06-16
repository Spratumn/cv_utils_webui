from PIL import Image

import streamlit as st



st.set_page_config(
    page_title="ReadMe",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.vizvision.com/',
        'Report a bug': "https://www.vizvision.com/",
        'About': "This is a vision tool running on RK3588, you can run detection, classification."
    }
)


st.markdown("# This is a toolkit for common vision tasks running on a **:red[RK3588]** device.")
st.markdown("Supported tasks: ")
st.markdown("- :blue[Image Classification] ")
st.markdown("- :blue[Object Detection]")
st.markdown("- :blue[Multi Object Tracking]")



@st.cache_resource
def show_object_detection():
    st.markdown("## 1. Object Detection")
    st.markdown("### 1.1 检测器参数设置")

    st.image(Image.open('./assets/detection_config.png'))
    st.markdown("""
    参数说明：

    - Arch Type: 算法模型
    - Target Type: 检测目标类型
    - Model Size: 模型输入尺寸
    - Score Thresh: 目标置信度阈值
    - IOU Thresh: NMS IOU阈值
    - NMS in same class: 同类别执行NMS(选择默认配置即可)

    设置好上面几个参数后，'Select model to run detection' 会自动给出可用的模型列表，用户可从中选择要用于检测的模型权重（若显示为'None'表示对应参数暂时无可用模型）。

    ### 1.2 检测图片
    """
                )
    st.image(Image.open('./assets/detection_image-1.png'))
    st.markdown("点击 'Drag and drop file here' 或 'Browse files' 上传一张待检测的图像，左侧会显示上传的图片。")
    st.image(Image.open('./assets/detection_image-2.png'))
    st.markdown("点击 'Detect image' 运行检测，完成后右侧会显示检测结果，并打印运行时间信息。用户可点击 'Download result image' 下载结果到本地。")
    st.image(Image.open('./assets/detection_image-3.png'))

    st.markdown("""
    ### 1.3 检测视频

    Tips: 在运行检测视频前，建议先通过截图或其他方式获得视频帧，使用 '检测图片' 功能找到效果更好的参数和权重，再用于视频检测。
    """
                )
    st.image(Image.open('./assets/detection_video-1.png'))
    st.markdown("点击 'Drag and drop file here' 或 'Browse files' 上传一个待检测的视频文件(mp4格式)，左侧会显示上传的视频。")
    st.image(Image.open('./assets/detection_video-2.png'))
    st.markdown("通过'Number of frames to detect' 设置待检测的视频帧数(-1表示检测全部视频帧),点击 'Detect Video' 运行检测，完成后右侧会显示检测结果，并打印运行时间信息。用户可点击 'Download result video' 下载结果到本地。")
    st.image(Image.open('./assets/detection_video-3.png'))
    st.markdown("### 1.4 检测序列 (内部测试功能，未开放)")

show_object_detection()
