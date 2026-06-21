import streamlit as st
from openai import OpenAI
import base64

# ==========================================
# 0. 基础配置与高级 UI 样式注入（含开场动画）
# ==========================================
API_KEY = "sk-7IFiLvmhRAgnQb6StgTYPxMbBVGS4G4ORMi5shfRMn9gFyyP"  
BASE_URL = "https://api.vectorengine.ai/v1"  

客户端 = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 注入高级设计感 CSS 样式与加载动画
st.set_page_config(page_title="Pro-15s海外广告提示词生成器", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* 1. 全屏奢华开场动画 */
    @keyframes fadeOut {
        0% { opacity: 1; visibility: visible; }
        90% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; }
    }
    @keyframes textGlow {
        0%, 100% { text-shadow: 0 0 10px rgba(255,75,75,0.5); }
        50% { text-shadow: 0 0 30px rgba(255,75,75,0.9); }
    }
    .splash-screen {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle, #1a1c24 0%, #0e1117 100%);
        z-index: 99999; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        animation: fadeOut 2.2s forwards; animation-delay: 0.5s;
        pointer-events: none;
    }
    .splash-logo {
        font-size: 3rem; font-weight: 800; color: #ff4b4b;
        margin-bottom: 20px; font-family: 'Helvetica Neue', sans-serif;
        animation: textGlow 2s infinite; letter-spacing: 2px;
    }
    .splash-loader {
        width: 50px; height: 50px; border: 3px solid #262730;
        border-radius: 50%; border-top-color: #ff4b4b;
        animation: spin 1s ease-in-out infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* 2. 网页高档卡片与渐变字体设计 */
    .main-title {
        background: linear-gradient(45deg, #ff4b4b, #ff7676);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.8rem; margin-bottom: 0.5rem;
    }
    .custom-card {
        background-color: #1a1c23; padding: 25px; border-radius: 12px;
        border-left: 5px solid #ff4b4b; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .step-indicator {
        background: #262730; padding: 8px 16px; border-radius: 30px;
        font-size: 0.85rem; color: #a3a8b4; border: 1px solid #41444c;
    }
</style>

<div class="splash-screen">
    <div class="splash-logo">🎬 AI DIRECTOR PRO</div>
    <div class="splash-loader"></div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 1. 核心多模态调用函数（支持文字+多图）
# ==========================================
def 调用大模型(系统提示词: str, 用户提示词: str, 历史记录: list = None, 图片列表: list = None) -> str:
    """支持文字与多张图片混合输入的多模态通用调用函数"""
    消息列表 = [{"role": "system", "content": 系统提示词}]
    
    if 历史记录:
        消息列表.extend(历史记录)
        
    if 用户提示词 or 图片列表:
        内容列表 = []
        if 用户提示词:
            内容列表.append({"type": "text", "text": 用户提示词})
        if 图片列表:
            for 基础64图片 in 图片列表:
                内容列表.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{基础64图片}"}
                })
        消息列表.append({"role": "user", "content": 内容列表})
        
    try:
        请求回复 = 客户端.chat.completions.create(
            model="gemini-3.1-pro-preview",  
            messages=消息列表,
            temperature=0.7
        )
        return 请求回复.choices[0].message.
