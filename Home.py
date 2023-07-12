import streamlit as st



st.set_page_config(
    page_title="ReadMe",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.vizvision.com/',
        'Report a bug': "https://www.vizvision.com/",
        'About': "这是一个运行在RK3588s设备上的视觉算法工具集。"
    }
)


st.markdown("## 这是一个运行在 **:red[RK3588s]** 设备上的视觉算法工具集")
st.markdown("### 支持的任务: ")
st.markdown("- :blue[图像分类] ")
st.markdown("- :blue[目标检测]")
st.markdown("- :blue[多目标跟踪]")
