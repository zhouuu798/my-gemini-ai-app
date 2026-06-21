import streamlit as st
from openai import OpenAI

# ==========================================
# 0. 基础配置（已根据你的中转站截图更新）
# ==========================================
# 提示：现在是在你电脑本地测试，所以直接放Key。等以后要发布上线了，记得换成 st.secrets["GEMINI_API_KEY"]
API_KEY = "sk-7IFiLvmhRAgnQb6StgTYPxMbBVGS4G4ORMi5shfRMn9gFyyP"  
BASE_URL = "https://api.vectorengine.ai/v1"  # 换成了你截图里的新网址，后面加上了 /v1 兼容标准

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
            model="gemini-3.1-pro-preview",  # 👈 已经换成你截图里专属的 Gemini 模型名字啦！
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

# --- 步骤二：选择创意 ---
elif st.session_state.当前步骤 == "步骤二_选择创意":
    st.header("💡 导演为你生成的3个创意方向：")
    st.markdown(st.session_state.创意方案输出)
    
    st.hr()
    st.subheader("请选择一个你喜欢的方向，或提出你的微调意见：")
    用户选择 = st.text_input("在这里输入你选择的方向（例如：‘方案二，能量可视化’）")
    
    if st.button("确认选择并生成初版分镜脚本", type="primary"):
        if not 用户选择.strip():
            st.error("请输入你的选择！")
        else:
            st.session_state.选定的创意 = 用户选择
            with st.spinner("正在为你规划10镜头左右的分镜脚本..."):
                系统提示词 = "你是一名专业广告导演。根据用户选择的创意方向，输出一份15秒的分镜脚本草案（控制在10个镜头左右）..."
                用户提示词 = f"原始产品资料：{st.session_state.产品资料}\n用户选择的创意方向：{用户选择}"
                
                # 构建第一轮对话历史
                st.session_state.剧本历史记录 = [{"role": "user", "content": 用户提示词}]
                输出结果 = 调用大模型(system_prompt=系统提示词, user_prompt=None, 历史记录=st.session_state.剧本历史记录)
                
                st.session_state.当前剧本草案 = 输出结果
                st.session_state.剧本历史记录.append({"role": "assistant", "content": 输出结果})
                st.session_state.当前步骤 = "步骤二_多轮迭代"
                st.rerun()

# --- 步骤二：多轮迭代 ---
elif st.session_state.当前步骤 == "步骤二_多轮迭代":
    st.header("📝 15秒分镜脚本草案（当前版本）")
    st.markdown(st.session_state.当前剧本草案)
    
    st.hr()
    st.subheader("🔁 脚本多轮修改反馈")
    反馈意见 = st.text_input("请输入修改意见（如果觉得没问题，请留空直接点下方确认）：")
    
    栏目1, 栏目2 = st.columns(2)
    with 栏目1:
        if st.button("提交修改意见"):
            if not 反馈意见.strip():
                st.error("请输入修改意见后再提交！")
            else:
                with st.spinner("正在根据你的意见修改脚本..."):
                    系统提示词 = "你是一名专业导演。根据用户对当前脚本提出的修改意见，重新调整并输出完整的10镜头左右脚本。"
                    # 将新的用户意见追加到历史记录中
                    st.session_state.剧本历史记录.append({"role": "user", "content": f"请根据意见修改脚本：{反馈意见}"})
                    
                    # 传入完整的历史记录
                    输出结果 = 调用大模型(system_prompt=系统提示词, user_prompt=None, 历史记录=st.session_state.剧本历史记录)
                    
                    st.session_state.当前剧本草案 = 输出结果
                    st.session_state.剧本历史记录.append({"role": "assistant", "content": 输出结果})
                    st.rerun()
                    
    with 栏目2:
        if st.button("✅ 脚本完美，进入第三步生成最终AI提示词", type="primary"):
            st.session_state.当前步骤 = "步骤三_最终交付"
            st.rerun()

# --- 步骤三：最终交付 ---
elif st.session_state.当前步骤 == "步骤三_最终交付":
    st.header("🚀 最终交付：符合AI视频生成模型规范的提示词")
    
    # 防止刷新页面时重复请求 API 
    if "最终提示词输出" not in st.session_state:
        with st.spinner("正在进行最后的格式化转换..."):
            系统提示词 = """你是一名专业的导演兼提示词工程师。请将用户确认的最终分镜脚本，严格转化为符合AI视频生成模型规范的提示词..."""
            用户提示词 = f"这是最终通过的分镜脚本：\n{st.session_state.当前剧本草案}"
            st.session_state.最终提示词输出 = 调用大模型(系统提示词, 用户提示词)
        
    st.text_area("直接复制下方文本到你的AI视频生成工具：", value=st.session_state.最终提示词输出, height=500)
        
    if st.button("🔄 重新制作新广告"):
        st.session_state.clear()
        st.rerun()
