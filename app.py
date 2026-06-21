import streamlit as st
from openai import OpenAI

# ==========================================
# 0. 基础配置（已配置你的中转站与最新模型）
# ==========================================
# 提示：现在是在你电脑本地测试，所以直接放Key。等以后要发布上线了，记得换成 st.secrets["GEMINI_API_KEY"]
API_KEY = "sk-7IFiLvmhRAgnQb6StgTYPxMbBVGS4G4ORMi5shfRMn9gFyyP"  
BASE_URL = "https://api.vectorengine.ai/v1"  

客户端 = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def 调用大模型(系统提示词: str, 用户提示词: str, 历史记录: list = None) -> str:
    """优化后的通用调用函数，清晰处理历史记录"""
    消息列表 = [{"role": "system", "content": 系统提示词}]
    if 历史记录:
        # 如果有历史记录，直接扩展（历史记录中已包含最新的一条用户发言）
        消息列表.extend(历史记录)
    if 用户提示词:
        消息列表.append({"role": "user", "content": 用户提示词})
        
    try:
        请求回复 = 客户端.chat.completions.create(
            model="gemini-3.1-pro-preview",  # 已经换成你截图里专属的 Gemini 模型名字啦！
            messages=消息列表,
            temperature=0.7
        )
        return 请求回复.choices[0].message.content
    except Exception as 异常信息:
        return f"接口调用出错，请检查API_KEY或网络配置。错误信息: {str(异常信息)}"

# ==========================================
# 网页界面与状态机控制
# ==========================================
st.set_page_config(page_title="15s海外广告提示词生成器", layout="wide")
st.title("🎬 15秒海外短视频广告提示词生成器")

# 初始化状态机
if "当前步骤" not in st.session_state:
    st.session_state.当前步骤 = "步骤一_输入资料"
    st.session_state.产品资料 = ""
    st.session_state.创意方案输出 = ""
    st.session_state.选定的创意 = ""
    st.session_state.剧本历史记录 = []
    st.session_state.当前剧本草案 = ""

# --- 步骤一：输入资料 ---
if st.session_state.当前步骤 == "步骤一_输入资料":
    st.header("第一步：输入产品资料")
    产品输入 = st.text_area(
        "请粘贴或输入你的产品资料：", 
        height=200,
        placeholder="例如：产品是Goreta NAD+软糖，主打欧美高知女性..."
    )
    
    if st.button("开始分析并生成创意方向", type="primary"):
        if not 产品输入.strip():
            st.error("请输入产品资料！")
        else:
            st.session_state.产品资料 = 产品输入
            with st.spinner("导演正在脑暴中..."):
                系统提示词 = "你是一名顶尖的海外DTC广告导演。请分析用户提供的产品资料，给出3个截然不同的15秒短片创意方向..."
                输出结果 = 调用大模型(系统提示词, f"产品资料如下：{产品输入}")
                st.session_state.创意方案输出 = 输出结果
                st.session_state.当前步骤 = "步骤二_选择创意"
                st.rerun()

# --- 步骤二
