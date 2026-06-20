import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 0. 基础配置
# ==========================================
# 在 Streamlit Cloud 的 Secrets 中设置 GEMINI_API_KEY
API_KEY = st.secrets["GEMINI_API_KEY"]

# 配置 Gemini
genai.configure(api_key=API_KEY)

def 调用Gemini(提示词: list, 是否有图: bool = False) -> str:
    """
    通用调用函数
    提示词参数可以是一个列表，包含字符串和图片数据
    """
    try:
        # 使用 gemini-1.5-flash (速度快且支持多模态，适合脚本生成)
        # 如果追求更高质量，可以换成 gemini-1.5-pro
        模型 = genai.GenerativeModel('gemini-1.5-flash')
        
        回答 = 模型.generate_content(提示词)
        return 回答.text
    except Exception as 异常信息:
        return f"Gemini 接口调用出错: {str(异常信息)}"

# ==========================================
# 网页界面与状态机控制
# ==========================================
st.set_page_config(page_title="Gemini 海外广告大师", layout="wide")
st.title("🎬 15秒海外短视频广告生成器 (Gemini 多模态版)")

# 初始化状态机
if "当前步骤" not in st.session_state:
    st.session_state.当前步骤 = "步骤一_输入资料"
    st.session_state.产品资料 = ""
    st.session_state.创意方案输出 = ""
    st.session_state.剧本历史记录 = [] # Gemini 习惯直接传内容列表
    st.session_state.当前剧本草案 = ""

# --- 步骤一：输入资料（增加图片识别） ---
if st.session_state.当前步骤 == "步骤一_输入资料":
    st.header("第一步：提供产品信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        上传图片 = st.file_uploader("上传产品图片或参考风格图（可选）", type=["jpg", "jpeg", "png"])
        if 上传图片:
            图片 = Image.open(上传图片)
            st.image(图片, caption="已上传图片", use_container_width=True)
        else:
            图片 = None

    with col2:
        产品输入 = st.text_area(
            "手动输入产品资料：", 
            height=200,
            placeholder="例如：产品是Goreta NAD+软糖，主打欧美高知女性..."
        )
    
    if st.button("开始 AI 分析并生成创意", type="primary"):
        if not 产品输入.strip() and not 上传图片:
            st.error("请至少提供文字说明或上传一张图片！")
        else:
            st.session_state.产品资料 = 产品输入
            with st.spinner("Gemini 正在观察图片并构思创意..."):
                # 构建给 Gemini 的指令
                指令 = ["你是一名顶尖海外DTC广告导演。请分析提供的产品资料和图片（如果有），给出3个截然不同的15秒短片创意方向。"]
                if 上传图片:
                    指令.append(图片)
                if 产品输入:
                    指令.append(f"文字资料如下：{产品输入}")
                
                输出结果 = 调用Gemini(指令)
                st.session_state.创意方案输出 = 输出结果
                st.session_state.当前步骤 = "步骤二_选择创意"
                st.rerun()

# --- 步骤二：选择创意 ---
elif st.session_state.当前步骤 == "步骤二_选择创意":
    st.header("💡 导演为你生成的 3 个创意方向：")
    st.markdown(st.session_state.创意方案输出)
    
    st.hr()
    用户选择 = st.text_input("请选择一个方向或提出修改意见：")
    
    if st.button("确认选择并生成脚本"):
        if not 用户选择.strip():
            st.error("请输入你的选择！")
        else:
            with st.spinner("正在规划 10 镜头脚本..."):
                指令 = [f"基于之前的分析和用户的选择：'{用户选择}'，请输出一份专业的15秒分镜脚本。包含视觉画面和旁白。"]
                输出结果 = 调用Gemini(指令)
                st.session_state.当前剧本草案 = 输出结果
                st.session_state.当前步骤 = "步骤二_多轮迭代"
                st.rerun()

# --- 步骤二：多轮迭代 ---
elif st.session_state.当前步骤 == "步骤二_多轮迭代":
    st.header("📝 15秒分镜脚本草案")
    st.markdown(st.session_state.当前剧本草案)
    
    st.hr()
    反馈意见 = st.text_input("请输入修改意见（或留空直接确认）：")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("提交修改"):
            with st.spinner("修改中..."):
                指令 = [f"这是目前的脚本：{st.session_state.当前剧本草案}", f"请根据此意见修改：{反馈意见}"]
                st.session_state.当前剧本草案 = 调用Gemini(指令)
                st.rerun()
    with c2:
        if st.button("✅ 脚本定稿，生成AI提示词", type="primary"):
            st.session_state.当前步骤 = "步骤三_最终交付"
            st.rerun()

# --- 步骤三：最终交付 ---
elif st.session_state.当前步骤 == "步骤三_最终交付":
    st.header("🚀 最终交付：AI视频生成提示词")
    
    if "最终提示词输出" not in st.session_state:
        with st.spinner("正在转换提示词格式..."):
            指令 = [f"请将以下脚本转化为专业的 AI 视频生成提示词（如 Sora, Runway, Kling 适用格式）：\n{st.session_state.当前剧本草案}"]
            st.session_state.最终提示词输出 = 调用Gemini(指令)
        
    st.text_area("直接复制提示词：", value=st.session_state.最终提示词输出, height=500)
        
    if st.button("🔄 重新开始"):
        st.session_state.clear()
        st.rerun()