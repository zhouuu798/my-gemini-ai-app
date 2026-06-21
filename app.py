import streamlit as st
from openai import OpenAI
import base64

# ==========================================
# 0. 基础配置与高级 UI 样式注入
# ==========================================
API_KEY = "sk-7IFiLvmhRAgnQb6StgTYPxMbBVGS4G4ORMi5shfRMn9gFyyP"  
BASE_URL = "https://api.vectorengine.ai/v1"  

客户端 = OpenAI(api_key=API_KEY, base_url=BASE_URL)

st.set_page_config(page_title="Pro-15s海外广告提示词生成器", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
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
""", unsafe_allow_html=True)


# ==========================================
# 1. 核心多模态调用函数
# ==========================================
def 调用大模型(系统提示词: str, 用户提示词: str, 历史记录: list = None, 图片列表: list = None) -> str:
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
        return 请求回复.choices[0].message.content
    except Exception as 异常信息:
        return f"接口调用出错，请检查配置。错误信息: {str(异常信息)}"

def 图片转base64(上传文件):
    return base64.b64encode(上传文件.read()).decode("utf-8")


# ==========================================
# 2. 全局状态机与历史记录初始化
# ==========================================
if "当前步骤" not in st.session_state:
    st.session_state.当前步骤 = "步骤一_输入资料"
    st.session_state.步骤历史 = ["步骤一_输入资料"] 
    st.session_state.产品资料 = ""
    st.session_state.产品图片base64 = []
    st.session_state.当前方案数量 = 3
    st.session_state.创意方案输出 = ""
    st.session_state.选定的创意 = ""
    st.session_state.剧本历史记录 = []
    st.session_state.当前剧本草案 = ""
    st.session_state.最终提示词输出 = ""
    st.session_state.提示词修改历史 = []

def 跳转至(目标步骤):
    st.session_state.current_step = 目标步骤
    st.session_state.当前步骤 = 目标步骤
    if 目标步骤 not in st.session_state.步骤历史:
        st.session_state.步骤历史.append(目标步骤)
    st.rerun()

def 返回上一步():
    if len(st.session_state.步骤历史) > 1:
        st.session_state.步骤历史.pop() 
        上一步 = st.session_state.步骤历史[-1]
        st.session_state.当前步骤 = 上一步
        st.rerun()

st.markdown('<div class="main-title">🎬 15秒海外短视频广告提示词大师</div>', unsafe_allow_html=True)
st.markdown(f'<span class="step-indicator">📍 当前位置：{st.session_state.当前步骤.replace("_", " -> ")}</span>', unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.title("🗂️ 导演监视器 (Session History)")
    st.metric("已构思创意方案数", f"{st.session_state.当前方案数量} 个")
    if st.session_state.产品资料:
        st.text_area("📦 已锁定的原始产品文本:", value=st.session_state.产品资料, height=100, disabled=True)
    if st.session_state.选定的创意:
        st.info(f"🎯 选定核心创意：{st.session_state.选定的创意}")
    st.caption("⚡ Powered by Gemini 3.1 Pro & Streamlit")


# ==========================================
# 3. 页面渲染分流
# ==========================================

# --- 步骤一：输入资料 ---
if st.session_state.当前步骤 == "步骤一_输入资料":
    st.subheader("第一步：输入多维产品资料")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        产品输入 = st.text_area(
            "✍️ 请输入产品核心卖点与受众描述：", 
            value=st.session_state.产品资料,
            height=250,
            placeholder="例如：产品是Goreta NAD+软糖，主打欧美高知女性..."
        )
    with col2:
        上传图片列表 = st.file_uploader(
            "🖼️ 上传产品实拍图/包装图/视觉风格参考（最多10张）：", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )
        if 上传图片列表:
            if len(上传图片列表) > 10:
                st.error("⚠️ 最多只能上传 10 张图片哦！")
            else:
                st.image(上传图片列表, width=80, caption=["已添加"]*len(上传图片列表))

    if st.button("🚀 开始高级创意脑暴", type="primary", use_container_width=True):
        if not 产品输入.strip() and not 上传图片列表:
            st.error("❌ 老师，请至少提供文字描述或上传一张产品图片！")
        elif 上传图片列表 and len(上传图片列表) > 10:
            st.error("❌ 图片数量超过10张限制。")
        else:
            st.session_state.产品资料 = 产品输入
            st.session_state.产品图片base64 = [图片转base64(f) for f in 上传图片列表] if 上传图片列表 else []
            st.session_state.当前方案数量 = 3 
            
            with st.spinner("🧠 顶尖导演团队正在进行第一轮多模态脑暴..."):
                系统提示词 = "你是一名顶尖的海外DTC广告导演。请结合用户提供的产品文字资料 and 视觉图片，给出3个截然不同的15秒短片创意方向，分别命名为：【方案一】、【方案二】、【方案三】。"
                用户提示词 = f"产品文本资料如下：{产品输入}\n请结合我上传的图片，综合给出首批3个创意方案。" if 产品输入 else "请根据我上传的图片视觉风格，给出首批3个创意方案。"
                
                输出结果 = 调用大模型(系统提示词, 用户提示词, 图片列表=st.session_state.产品图片base64)
                st.session_state.創意方案输出 = 输出结果
                st.session_state.创意方案输出 = 输出结果
                跳转至("步骤二_选择创意")


# --- 步骤二：选择创意与分镜脚本初版生成 ---
elif st.session_state.当前步骤 == "步骤二_选择创意":
    if st.button("⬅️ 返回上一步修改产品资料"):
        返回上一步()
        
    st.subheader("💡 导演团队为您激荡出的创意灵感池：")
    st.markdown(f'<div class="custom-card">{st.session_state.创意方案输出}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    col_more, col_empty = st.columns([1, 1])
    with col_more:
        if st.button("🔄 对现有方案都不满意？继续生成下3个方案！", use_container_width=True):
            st.session_state.当前方案数量 = st.session_state.当前方案数量 + 3
            下一起始编号 = st.session_state.当前方案数量 - 2
            
            with st.spinner(f"🎬 导演正在推翻重来，正在为您构思方案 {下一起始编号} ~ {st.session_state.当前方案数量}..."):
                系统提示词 = "你是一名顶尖的海外DTC广告导演。用户对之前的创意方案都不太满意。请在之前的基础上，避开旧思路，提供3个全新且更炸裂的15秒短片创意方向。"
                用户提示词 = f"原始资料文本：{st.session_state.产品资料}\n\n这是你之前生成的方案记录：\n{st.session_state.创意方案输出}\n\n请绝对不要重复上述思路，继续给出3个更出彩的全新方案，分别命名为：【方案{下一起始编号}】、【方案{下一起始编号+1}】、【方案{st.session_state.当前方案数量}】。"
                
                新输出 = 调用大模型(系统提示词, 用户提示词, 图片列表=st.session_state.产品图片base64)
                st.session_state.创意方案输出 += f"\n\n---\n\n### 🔄 延展脑暴批次 (方案 {下一起始编号}~{st.session_state.当前方案数量})\n{新输出}"
                st.rerun()

    st.write("")
    st.subheader("🎯 锁定理想创意")
    用户选择 = st.text_input("请输入您最终选定的方案名称或微调意见（例如：‘方案二，但是节奏再快一点’）：")
    
    if st.button("🔥 确认选择，生成初版10镜头分镜脚本", type="primary", use_container_width=True):
        if not 用户选择.strip():
            st.error("请输入您的选择选择后再点击哦！")
        else:
            st.session_state.选定的创意 = 用户选择
            with st.spinner("🎬 正在按照【极简实拍高转化公式】为您雕刻15秒广告脚本..."):
                
                系统提示词 = """你是一名顶级海外DTC广告导演。请根据用户选择的创意方向，输出一份15秒的高转化率广告分镜脚本（严格控制在10个镜头左右），包含：镜头序号、镜头时长（秒数）、景别/运动、画面视觉描写、音频旁白、设计意图。

在进行分镜表设计时，你必须死死遵守并实践以下【高转化率分镜原则】：

一、场景与演员极端精简铁律（控本控流）
1. 整体影调必须高度统一：从始至终色调、光影风格前后一致，拒绝突兀变化。
2. 场景极简：全片【场景尽量只有一个】，严禁频繁跨大场景切镜。
3. 演员极简：全片【演员尽量只有一个】，进行单人全流程沉浸式表演。
4. ❌ 绝对禁止分屏：全片分镜【禁止出现分屏、画面一分为二、画中画、多画面拼接】等设计，必须全部是纯粹的单一完整大画面。

二、台词极少化规则
- 全片【台词尽量不要有】。如果根据剧情必须要说话，单镜头或全片的台词总量【绝对不能超过三句】！尽量依靠环境音、高级音效和视觉画面来表达。

三、节奏有快慢变化（打造叙事呼吸感）
每个镜头的秒数时长绝对禁止平铺直叙。你必须根据具体的镜头剧情和戏剧张力来动态判断镜头时长：
- 在需要视觉渲染、产品深度质感刻画、或情感沉淀沉浸的镜头，使用慢动作（Slow Motion）并拉长单镜头秒数。
- 在展现痛点冲突、高频动作、或情节快速推进的镜头，采用快速切镜和短秒数。

四、严格符合广告分镜设计的底层逻辑公式（目标导向 + 节奏层次 + 视觉呈现）
1. 目标导向：每个镜头都应指向叙事核心（推动故事/刻画人物/传达情感）。
2. 节奏层次：通过运用时长、景别变化与运动速率营造叙事呼吸感。
3. 视觉呈现：把抽象意图完全转化为【具体的、可直接拍摄的影像画面】（例如：“孤独”表现为空房间与单人剪影）。

五、严苛符合脚本三要素铁律
1. 开头噱头（黄金前3秒）：前3秒必须一开始就抛出冲击力视觉或悬念痛点把观众吸引住。
2. 中间论述：条理清晰，通过具体共鸣点引导受众产生深度认同感。
3. 结尾总结与产品亮相：精简总结卖点。⚠️产品和品牌只能在短片最后阶段作为终极解法“压轴登场”，绝对不准在视频刚开头或前中期过早出现！"""

                用户提示词 = f"原始产品文本：{st.session_state.产品资料}\n选定的创意方向及微调建议：{用户选择}"
                
                st.session_state.剧本历史记录 = [{"role": "user", "content": 用户提示词}]
                输出结果 = 调用大模型(系统提示词, 用户提示词=None, 历史记录=st.session_state.剧本历史记录, 图片列表=st.session_state.产品图片base64)
                
                st.session_state.当前剧本草案 = 输出结果
                st.session_state.剧本历史记录.append({"role": "assistant", "content": 输出结果})
                跳转至("步骤二_多轮迭代")


# --- 步骤二：分镜脚本多轮迭代 ---
elif st.session_state.当前步骤 == "步骤二_多轮迭代":
    if st.button("⬅️ 返回上一步重新选择创意"):
        返回上一步()
        
    st.subheader("📝 15秒分镜脚本草案（当前精修版本）")
    st.markdown(f'<div class="custom-card">{st.session_state.当前剧本草案}</div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("🔁 导演工作室：对剧本提出修改反馈")
    反馈意见 = st.text_input("请输入修改意见（例如：‘把第3镜头的场景换成办公室’）：")
    
    栏目1, 栏目2 = st.columns(2)
    with 栏目1:
        if st.button("⚡ 提交修改意见", use_container_width=True):
            if not 反馈意见.strip():
                st.error("请输入具体修改意见后再提交！")
            else:
                with st.spinner("🛠️ 导演正在严格遵循三大原则，逐镜重修剧本..."):
                    
                    系统提示词 = """你是一名顶级海外广告导演。请根据用户的反馈意见对分镜脚本进行重修调整。
                    
在调整过程中，你必须始终雷打不动地坚守以下核心生产原则：
1. 单人单场景：场景尽量只有一个，演员尽量只有一个，影调高度统一。
2. ❌ 绝对禁止分屏：禁止一切分屏、画面一分为二等多分割画面的分镜设计。
3. 节奏快慢结合：错落编排镜头秒数，需要视觉渲染处用慢动作。
4. 台词尽量不要有，若有全片总数绝对不能超过三句。
5. 产品及品牌只能在结尾总结部分压轴出现，绝不提前暴露。"""

                    st.session_state.剧本历史记录.append({"role": "user", "content": f"请根据意见修改脚本：{反馈意见}"})
                    
                    输出结果 = 调用大模型(系统提示词, 用户提示词=None, 历史记录=st.session_state.剧本历史记录)
                    st.session_state.当前剧本草案 = 输出结果
                    st.session_state.剧本历史记录.append({"role": "assistant", "content": 输出结果})
                    st.rerun()
                    
    with 栏目2:
        if st.button("👑 脚本完美，去生成最终AI提示词", type="primary", use_container_width=True):
            跳转至("步骤三_最终交付")


# --- 步骤三：最终交付与提示词精修迭代（全面植入秒数与极简场景逻辑） ---
elif st.session_state.当前步骤 == "步骤三_最终交付":
    if st.button("⬅️ 返回上一步微调分镜脚本"):
        返回上一步()
        
    st.subheader("🚀 最终交付：符合AI视频生成模型规范的提示词（Prompt）")
    
    固定_基础设定 = "【图片1】为产品图，全部台词为英文 。"
    固定_氛围与画质 = """风格核心:短剧剧组拍摄、真实摄影、极致逼真细节、Photirealism-真人实景拍摄、动作自然流程、逻辑正常 。高端摄影系统+经典胶片美学+真实原生皮肤+自然光影+生活化瑕疵细节=原生真实画面
1、摄影设备参数(奠定画质基底)Shot on ARRI Alexa 65, Vintage Cooke 焦头, SonyVenice2机身，大光圈f/1.4，高端电影摄影机光学色散、轻微镜头畸变
2、胶片质感参数(破除光滑塑胶)KodakVision3 500T胶片色调，35mm胶片颗粒，胶片划痕、灰尘、细微破损，模拟老式胶片物理质感
3、原生皮肤细节(告别磨皮假面)可见毛孔、细微皱纹、天然雀斑、肌肤细微瑕疵，零过度磨皮，原生皮肤肌理，皮肤自然血色与肤质起伏
4、光影氛围(光影遮瑕，优化画面短板)真实硬质阴影，体积光，环境漫反射光影"""

    if not st.session_state.最终提示词输出:
        with st.spinner("🤖 提示词专家正在将分镜脚本转化为高精度 AI 视频生成模型提示词..."):
            系统提示词 = f"""你是一名顶尖的导演兼提示词工程师。请将用户确认的最终分镜脚本，严格转化为符合AI视频模型规范的提示词。
            
⚠️ 格式、结构和输出规范铁律：
1. 最终输出有且只能包含【基础设定】、【分镜序列】、【氛围与画质】三个部分。
2. 【基础设定】和【氛围与画质】这两部分内容是固定死模板，你必须一字不差地直接抄写输出，不得进行任何增减。
3. 在重构【分镜序列】时，你必须无条件严格死守以下【提示词精细化原则】：
   - 【必须带上秒数】：每个镜头名称必须严格按 `镜头X (Y秒)` 格式输出，括号里是该镜头的具体时间跨度（例如：镜头1 (3秒)）。
   - 【极端控制台词】：提示词中台词尽量不要有。如果分镜中有，台词总量绝对不能超过三句！
   - 【严格限制视觉】：确保所有镜头的画面提示词中，全片场景尽量只有一个，演员尽量只有一个，整体影调高度统一。
   - 【❌ 严禁出现分割画面】：在所有镜头的画面描述文本中，【绝对禁止出现分屏、画面一分为二、画中画、多画幅并存】等任何形式的设计。
   
每个镜头必须严格按照以下无任何多余符号的纯净干净结构输出：
镜头X (Y秒)
音效：...
台词：... (尽量没有，有也绝不超过三句)

请完整输出符合以下结构的规范文本：

【基础设定】
{固定_基础设定}

【分镜序列】
(请在此处按顺序生成各个镜头的转化内容)

【氛围与画质】
{固定_氛围与画质}
"""
            用户提示词 = f"这是最终通过的分镜脚本：\n{st.session_state.当前剧本草案}"
            st.session_state.最终提示词输出 = 调用大模型(系统提示词, 用户提示词)
            st.session_state.提示词修改历史 = [{"role": "assistant", "content": st.session_state.最终提示词输出}]

    st.text_area("📋 直接复制下方文本到你的AI视频生成工具：", value=st.session_state.最终提示词输出, height=450)
    
    st.divider()
    
    st.subheader("🛠️ 针对AI提示词进行微调修改")
    提示词反馈 = st.text_input("请输入对提示词的微调意见（例如：‘把第2镜头的慢动作渲染秒数拉长到3秒’）：")
    
    col_pt1, col_pt2 = st.columns(2)
    with col_pt1:
        if st.button("✨ 优化提示词", use_container_width=True):
            if not 提示词反馈.strip():
                st.error("请输入对提示词的微调要求哦！")
            else:
                with st.spinner("⚙️ 提示词重组工程进行中..."):
                    系统提示词 = f"""你是一名资深提示词专家。请根据用户最新的风格化修改意见，对目前的AI视频提示词文本进行全局润色与重构。
                    
⚠️ 核心绝不动摇原则：
1. 最终输出必须严格且仅包含【基础设定】、【分镜序列】、【氛围与画质】三部分。
2. 【基础设定】和【氛围与画质】是固定模板，任何时候都绝不允许做任何改动，直接原样粘贴即可：
   【基础设定】内容：{固定_基础设定}
   【氛围与画质】内容：{固定_氛围与画质}
3. 用户的修改意见只能体现在【分镜序列】内部。
4. 【分镜序列】中的每个镜头依然必须死死保持如下纯净格式：
   镜头X (Y秒)
   音效：...
   台词：...
5. 必须再次强制核准：全片场景尽量只有一个、演员尽量只有一个、整体影调统一、【绝对严禁分屏、画面一分为二】、台词总量绝对不能超过三句！"""
                    
                    st.session_state.提示词修改历史.append({"role": "user", "content": f"请根据此要求精修提示词：{提示词反馈}"})
                    
                    新提示词结果 = 调用大模型(系统提示词, 用户提示词=None, 历史记录=st.session_state.提示词修改历史)
                    st.session_state.最终提示词输出 = 新提示词结果
                    st.session_state.提示词修改历史.append({"role": "assistant", "content": 新提示词结果})
                    st.rerun()
                    
    with col_pt2:
        if st.button("🔄 彻底重置，重新制作新广告", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
