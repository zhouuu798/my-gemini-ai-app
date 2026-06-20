import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 0. 基础配置
# ==========================================
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

def 调用Gemini(提示词: list) -> str:
    try:
        # 修复：使用 gemini-1.5-flash-latest
        模型 = genai.GenerativeModel('gemini-1.5-flash-latest')
        回答 = 模型.generate_content(提示词)
        return 回答.text
    except Exception as 异常信息:
        return f"Gemini 接口调用出错: {str(异常信息)}"

# ==========================================
# 网页界面
# ==========================================
st.set_page_config(page_title="Gemini 海外广告大师", layout="wide")
st.title("🎬 15秒海外短视频广告生成器 (Gemini 多模态版)")

if "当前步骤" not in st.session_state:
    st.session_state.当前步骤 = "步骤一_输入资料"
    st.session_state.产品资料 = ""
    st.session_state.创意方案输出 = ""
    st.session_state.当前剧本草案 = ""

# --- 步骤一：输入资料 ---
if st.session_state.当前步骤 == "步骤一_输入资料":
    st.header("第一步：提供产品信息")
    col1, col2 = st.columns(2)
    with col1:
        上传图片 = st.file_uploader("上传产品图片（可选）", type=["jpg", "jpeg", "png"])
        图片对象 = None
        if 上传图片:
            图片对象 = Image.open(上传图片)
            st.image(图片对象, caption="已上传图片", use_container_width=True)
    with col2:
        产品输入 = st.text_area("产品资料：", height=200, placeholder="例如：产品是软糖，主打欧美高知女性...")
    
    if st.button("开始分析", type="primary"):
        if not 产品输入.strip() and not 上传图片:
            st.error("请提供信息！")
        else:
            st.session_state.产品资料 = 产品输入
            with st.spinner("AI 构思中..."):
                指令 = ["你是一名顶尖广告导演。分析产品并给3个15秒创意方向。"]
                if 图片对象: 指令.append(图片对象)
                if 产品输入: 指令.append(产品输入)
                st.session_state.创意方案输出 = 调用Gemini(指令)
                st.session_state.当前步骤 = "步骤二_选择创意"
                st.rerun()

# --- 步骤二：选择与迭代 ---
elif st.session_state.当前步骤 == "步骤二_选择创意" or st.session_state.当前步骤 == "步骤二_多轮迭代":
    st.header("💡 创意方案与脚本")
    st.markdown(st.session_state.创意方案输出)
    if st.session_state.当前剧本草案:
        st.divider() # 修复：这里改成了 st.divider()
        st.subheader("当前脚本草案")
        st.markdown(st.session_state.当前剧本草案)
    
    st.divider() # 修复：这里改成了 st.divider()
    意见 = st.text_input("输入你的选择或修改意见：")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("生成/修改脚本"):
            with st.spinner("脚本创作中..."):
                指令 = [f"基于以下内容写一份15秒分镜脚本：\n资料：{st.session_state.产品资料}\n当前内容：{st.session_state.创意方案输出}\n用户意见：{意见}"]
                st.session_state.当前剧本草案 = 调用Gemini(指令)
                st.session_state.当前步骤 = "步骤二_多轮迭代"
                st.rerun()
    with c2:
        if st.button("✅ 定稿生成最终提示词"):
            st.session_state.当前步骤 = "步骤三_最终交付"
            st.rerun()

# --- 步骤三：最终交付 ---
elif st.session_state.当前步骤 == "步骤三_最终交付":
    st.header("🚀 最终 AI 视频提示词")
    if "最终提示词输出" not in st.session_state:
        with st.spinner("生成中..."):
            指令 = [f"将此脚本转为 AI 视频生成提示词：\n{st.session_state.当前剧本草案}"]
            st.session_state.最终提示词输出 = 调用Gemini(指令)
    st.text_area("复制提示词：", value=st.session_state.最终提示词输出, height=400)
    if st.button("🔄 重新开始"):
        st.session_state.clear()
        st.rerun()
