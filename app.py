import streamlit as st
from openai import OpenAI

# ==========================================
# 0. 基础配置：请在这里填写你的大模型密钥 (API Key)
# 如果你使用的是国内代理或其他模型，可以修改 base_url
# ==========================================
API_KEY = "这里换成你的API_KEY"  # 填入你的大模型Key
BASE_URL = "https://api.openai.com/v1"  # 如果用了代理，换成代理地址

# 初始化大模型客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def call_llm(system_prompt: str, user_prompt: str, history: list = None) -> str:
    """调用大模型的通用函数"""
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # 这里可以换成你拥有的模型名称，如 gpt-4o, claude-3-5-sonnet 等
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"接口调用出错，请检查API_KEY或网络配置。错误信息: {str(e)}"

# ==========================================
# 网页界面与状态机控制
# ==========================================
st.set_page_config(page_title="15s海外广告提示词生成器", layout="wide")
st.title("🎬 15秒海外短视频广告提示词生成器")
st.write("以编程形式，将产品资料转化为完全符合AI视频模型规范的15秒分镜提示词。")

# 使用 Streamlit 的 session_state 来记录用户进行到哪一步了（保存状态）
if "stage" not in st.session_state:
    st.session_state.stage = "STAGE_1"
    st.session_state.product_info = ""
    st.session_state.ideas_output = ""
    st.session_state.selected_idea = ""
    st.session_state.script_history = []
    st.session_state.current_script = ""

# ------------------------------------------
# 第一步：分析资料，给出3个创意方向
# ------------------------------------------
if st.session_state.stage == "STAGE_1":
    st.header("第一步：输入产品资料")
    product_input = st.text_area(
        "请粘贴或输入你的产品资料（包括核心卖点、人群定位、对标视频描述等）：", 
        height=200,
        placeholder="例如：产品是Goreta NAD+软糖，15合1，0糖，紫色调，主打欧美高知女性..."
    )
    
    if st.button("开始分析并生成创意方向"):
        if not product_input.strip():
            st.error("请输入产品资料！")
        else:
            st.session_state.product_info = product_input
            with st.spinner("导演正在脑暴中，请稍候..."):
                sys_prompt = "你是一名顶尖的海外DTC广告导演。请分析用户提供的产品资料，给出3个截然不同的15秒短片创意方向。每个方向需包含：1. 核心创意概念 2. 核心卖点融合 3. 为什么这个方向能吸引海外受众（原因分析）。请务必保持创新、节奏轻快、符合欧美审美。"
                user_prompt = f"产品资料如下：{product_input}"
                
                output = call_llm(sys_prompt, user_prompt)
                st.session_state.ideas_output = output
                st.session_state.stage = "STAGE_2_SELECT"
                st.rerun()

# ------------------------------------------
# 第二步准备：展示创意并让用户选择/调整
# ------------------------------------------
elif st.session_state.stage == "STAGE_2_SELECT":
    st.header("💡 导演为你生成的3个创意方向：")
    st.markdown(st.session_state.ideas_output)
    
    st.hr()
    st.subheader("请选择一个你喜欢的方向，或提出你的微调意见：")
    user_choice = st.text_input("在这里输入你选择的方向（例如：‘方案二，能量可视化’，或‘方案二，但我希望角色是一个男白领’）")
    
    if st.button("确认选择并生成初版分镜脚本"):
        if not user_choice.strip():
            st.error("请输入你的选择！")
        else:
            st.session_state.selected_idea = user_choice
            with st.spinner("正在为你规划10镜头左右的分镜脚本..."):
                sys_prompt = "你是一名专业广告导演。根据用户选择的创意方向，输出一份15秒的分镜脚本草案（控制在10个镜头左右）。注意控制节奏，景别变化要丰富（避免相邻镜头景别相同），设计富有想象力的动作匹配（Match Cut）和快慢变速。"
                user_prompt = f"原始产品资料：{st.session_state.product_info}\n用户选择的创意方向和要求：{user_choice}"
                
                # 记录多轮对话历史
                st.session_state.script_history.append({"role": "user", "content": user_prompt})
                output = call_llm(sys_prompt, user_prompt)
                
                st.session_state.current_script = output
                st.session_state.script_history.append({"role": "assistant", "content": output})
                st.session_state.stage = "STAGE_2_LOOP"
                st.rerun()

# ------------------------------------------
# 第二步循环：多轮修改分镜脚本
# ------------------------------------------
elif st.session_state.stage == "STAGE_2_LOOP":
    st.header("📝 15秒分镜脚本草案（当前版本）")
    st.markdown(st.session_state.current_script)
    
    st.hr()
    st.subheader("🔁 脚本多轮修改反馈")
    feedback = st.text_input("如果你对目前的镜头节奏、演员、运镜不满意，请在这里输入修改意见（如果觉得没问题，请留空直接点下方确认）：")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("提交修改意见"):
            if not feedback.strip():
                st.error("请输入修改意见后再提交！")
            else:
                with st.spinner("正在根据你的意见修改脚本..."):
                    sys_prompt = "你是一名专业导演。根据用户对当前脚本提出的修改意见，重新调整并输出完整的10镜头左右脚本。继续保持景别丰富、动作匹配和变速节奏的优势。"
                    st.session_state.script_history.append({"role": "user", "content": f"请根据意见修改脚本：{feedback}"})
                    
                    # 传入历史记录实现多轮对话
                    output = call_llm(sys_prompt, f"修改意见：{feedback}", history=st.session_state.script_history[:-1])
                    
                    st.session_state.current_script = output
                    st.session_state.script_history.append({"role": "assistant", "content": output})
                    st.rerun()
                    
    with col2:
        if st.button("✅ 脚本完美，进入第三步生成最终AI提示词"):
            st.session_state.stage = "STAGE_3"
            st.rerun()

# ------------------------------------------
# 第三步：最终交付完全符合规范的 Prompt
# ------------------------------------------
elif st.session_state.stage == "STAGE_3":
    st.header("🚀 最终交付：符合AI视频生成模型规范的提示词（Prompt）")
    
    with st.spinner("正在进行最后的格式化转换..."):
        sys_prompt = """
        你是一名专业的导演兼提示词工程师。请将用户确认的最终分镜脚本，严格转化为符合AI视频生成模型规范的提示词（Prompt）。
        
        【严格规范限制】：
        1. 全程遵循特定演员设定（如：欧美中年女性），统一所有镜头的角色一致性。
        2. 去除所有人物具体的服装描述和多余的空间场景布局描述（把想象空间留给AI）。
        3. 【基础设定】部分：明示不需要配乐和背景音乐，不要氛围音，仅保留音效和英文版台词，全部台词为英文。
        4. 【序列分镜】部分严格采用以下格式：
           镜头X（秒数）：【景别】，拍摄角度，运镜方式，画面内容。
           音效：以拟音为主（如物品撞击、摩擦声等，不要环境氛围音）。
           台词：【[角色名]】（说话语气，需标注是否开口或画外音）：“纯英文台词”（绝对不能出现任何中文）。如果该镜头无台词，则不写台词这一项。
        5. 【氛围与画质】部分：固定输出“风格核心:短剧剧组拍摄、真实摄影、极致逼真细节、Photirealism-真人实景拍摄、动作自然流程、逻辑正常。”
        """
        user_prompt = f"这是最终通过的分镜脚本：\n{st.session_state.current_script}\n请根据上述规范将其转化为标准的AI视频提示词输出。"
        
        final_prompt_output = call_llm(sys_prompt, user_prompt)
        
        st.text_area("直接复制下方文本到你的AI视频生成工具（如Sora、Runway、Luma等）：", value=final_prompt_output, height=500)
        
    if st.button("🔄 重新制作新广告"):
        st.session_state.clear()
        st.rerun()
