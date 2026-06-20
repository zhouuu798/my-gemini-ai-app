import streamlit as st
from openai import OpenAI
import base64

# ==========================================
# 0. 基础配置
# ==========================================
# 从 Secrets 获取中转配置
API_KEY = st.secrets["GEMINI_API_KEY"]
BASE_URL = st.secrets["GEMINI_BASE_URL"]
MODEL_NAME = st.secrets["GEMINI_MODEL_NAME"]

# 初始化客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def 调用Gemini(用户指令, 上传文件=None):
    """兼容中转 API 的多模态调用函数"""
    
    # 准备消息内容
    内容列表 = [{"type": "text", "text": 用户指令}]
    
    # 如果用户上传了图片，将图片转为 Base64 编码送入内容
    if 上传文件:
        base64_image = base64.b64encode(上传文件.getvalue()).decode('utf-8')
        内容列表.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    try:
        请求回复 = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": 内容列表}],
            temperature=0.7
        )
        return 请求回复.choices[0].message.content
    except Exception as e:
        return f"❌ 调用失败。请检查：1.API地址是否带/v1 2.模型名是否正确。 错误信息: {str(e)}"

# ==========================================
# 网页界面逻辑
# ==========================================
st.set_page_config(page_title="Gemini 海外广告大师", layout="wide")
st.title("🎬 15秒海外短视频广告生成器 (中转极速版)")

# 初始化状态
if "当前步骤" not in st.session_state:
    st.session_state.当前步骤 = "步骤一"
    st.session_state.创意方案 = ""
    st.session_state.剧本草案 = ""

# --- 第一步：输入 ---
if st.session_state.当前步骤 == "步骤一":
    st.header("第一步：上传产品图或写下产品需求")
    col1, col2 = st.columns(2)
    with col1:
        上传图片 = st.file_uploader("上传产品实拍图/包装图（可选）", type=["jpg", "png", "jpeg"])
    with col2:
        文本资料 = st.text_area("产品卖点描述：", height=200, placeholder="例如：这是一款美白牙贴，适合职场女性，主打快速起效...")
    
    if st.button("开始生成创意方向", type="primary"):
        if not 文本资料 and not 上传图片:
            st.error("请至少提供图片或文字！")
        else:
            with st.spinner("AI 正在通过中转线路分析中..."):
                提示词 = f"你是一名顶尖海外DTC广告导演。请分析产品，并给出3个截然不同的15秒视频创意方向。产品文字描述：{文本资料}"
                st.session_state.创意方案 = 调用Gemini(提示词, 上传图片)
                st.session_state.当前步骤 = "步骤二"
                st.rerun()

# --- 第二步：方案与脚本 ---
elif st.session_state.当前步骤 == "步骤二":
    st.header("💡 AI 生成的创意方案")
    st.markdown(st.session_state.创意方案)
    
    if st.session_state.剧本草案:
        st.divider()
        st.subheader("📝 分镜脚本草案")
        st.markdown(st.session_state.剧本草案)
    
    st.divider()
    用户意见 = st.text_input("在这里输入你的选择（如：方案一）或修改意见：")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("生成/修改脚本", type="primary"):
            with st.spinner("脚本编写中..."):
                提示词 = f"基于以下信息写一份专业的15秒分镜脚本：\n创意库：{st.session_state.创意方案}\n用户意见：{用户意见}"
                st.session_state.剧本草案 = 调用Gemini(提示词)
                st.rerun()
    with c2:
        if st.session_state.剧本草案:
            if st.button("✅ 脚本定稿"):
                st.session_state.当前步骤 = "步骤三"
                st.rerun()

# --- 第三步：交付 ---
elif st.session_state.当前步骤 == "步骤三":
    st.header("🚀 最终 AI 视频生成提示词")
    if "最终提示词" not in st.session_state:
        with st.spinner("转化中..."):
            提示词 = f"请将以下脚本转化为 AI 视频模型（如 Sora, Kling）专用的英文提示词：\n{st.session_state.剧本草案}"
            st.session_state.最终提示词 = 调用Gemini(提示词)
    
    st.text_area("直接复制提示词到视频工具：", value=st.session_state.最终提示词, height=400)
    if st.button("🔄 重新开始新项目"):
        st.session_state.clear()
        st.rerun()
