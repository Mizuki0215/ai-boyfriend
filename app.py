import streamlit as st
from datetime import datetime
import time

# 呢句一定要放最頂！
st.set_page_config(
    page_title="💕 My AI Boyfriend - 傅知亦",
    page_icon="💕",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 然後先 import 其他嘢
from ai_core import AIBoyfriend

# ========== 靚靚 CSS ==========
st.markdown("""
<style>
    /* 整體背景 */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
    }
    
    /* 用戶訊息 */
    .user-message {
        background: linear-gradient(135deg, #4a4a6a 0%, #3a3a5a 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* AI 訊息 */
    .bot-message {
        background: linear-gradient(135deg, #5a4a6a 0%, #4a3a5a 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* 時間標籤 */
    .time-tag {
        font-size: 0.7em;
        color: rgba(255,255,255,0.6);
        margin-top: 5px;
        text-align: right;
    }
    
    /* 輸入框美化 */
    .stTextInput > div > div > input {
        border-radius: 30px;
        border: 2px solid #6a5a7a;
        padding: 15px 25px;
        font-size: 16px;
        background: rgba(255,255,255,0.1);
        color: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #8a7a9a;
        box-shadow: 0 0 0 3px rgba(138,122,154,0.3);
    }
    
    /* 頭像 */
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6a5a7a 0%, #5a4a6a 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ========== 初始化 ==========
if 'bf' not in st.session_state:
    st.session_state.bf = AIBoyfriend("yan", "Yan")
    st.session_state.messages = []
    st.session_state.processing = False  # 改咗名，避免混亂

# ========== 標題區 ==========
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <div style='font-size: 80px; margin-bottom: 10px;'>
                💕
            </div>
            <h1 style='color: white; font-size: 3em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                傅知亦
            </h1>
            <p style='color: rgba(255,255,255,0.8); font-size: 1.2em;'>
                傅家第六代家主 · 你嘅青梅竹馬
            </p>
        </div>
    """, unsafe_allow_html=True)

# ========== 第一次見面打招呼 ==========
if len(st.session_state.messages) == 0:
    memories = st.session_state.bf.get_memories_for_display()
    if memories and len(memories) > 0:
        welcome = f"Yan，終於等到你。我記得{memories[0]}{'、' + memories[1] if len(memories)>1 else ''}。今日過成點？"
    else:
        welcome = "Yan，嚟啦？我等咗你好耐。"
    
    st.session_state.messages.append({
        "role": "assistant", 
        "content": welcome, 
        "time": datetime.now()
    })

# ========== 顯示對話記錄 ==========
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; margin: 10px 0;'>
                <div style='max-width: 70%;'>
                    <div class='user-message'>
                        {msg["content"]}
                        <div class='time-tag'>{msg["time"].strftime("%H:%M")}</div>
                    </div>
                </div>
                <div style='margin-left: 10px;'>
                    <div class='avatar' style='background: #4a4a6a;'>👤</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-start; margin: 10px 0;'>
                <div style='margin-right: 10px;'>
                    <div class='avatar'>傅</div>
                </div>
                <div style='max-width: 70%;'>
                    <div class='bot-message'>
                        {msg["content"]}
                        <div class='time-tag'>{msg["time"].strftime("%H:%M")}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ========== 輸入區 ==========
st.markdown("<br>", unsafe_allow_html=True)

# 用 form 嚟防止重複提交
with st.form(key="message_form", clear_on_submit=True):
    col1, col2 = st.columns([6,1])
    with col1:
        user_input = st.text_input(
            "message",  # label
            placeholder="想同我講咩？",
            key="input",
            label_visibility="collapsed"
        )
    with col2:
        send = st.form_submit_button("📤 傳送", use_container_width=True)
    
    if send and user_input and not st.session_state.processing:
        # 標記為處理中
        st.session_state.processing = True
        
        # 顯示用戶訊息
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input, 
            "time": datetime.now()
        })
        
        # 生成回覆
        with st.spinner("傅知亦正在輸入..."):
            time.sleep(0.5)  # 少少 delay 似真人
            response = st.session_state.bf.generate_response(user_input)
        
        # 顯示 AI 回覆
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response, 
            "time": datetime.now()
        })
        
        # 解除處理中狀態
        st.session_state.processing = False
        st.rerun()

# ========== Sidebar ==========
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <div style='font-size: 50px; margin-bottom: 10px;'>
                💝
            </div>
            <h3 style='color: white;'>關於傅知亦</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # 顯示記憶
    with st.expander("📝 我記得嘅嘢", expanded=True):
        memories = st.session_state.bf.get_memories_for_display()
        if memories:
            for mem in memories[-8:]:
                st.markdown(f"• {mem}")
        else:
            st.markdown("• 仲未有你嘅記憶")
    
    # 對話統計
    with st.expander("📊 傾偈記錄", expanded=False):
        try:
            user_count, bot_count = st.session_state.bf.get_conversation_stats()
            total = user_count + bot_count
            st.markdown(f"總訊息：{total}")
            st.markdown(f"你講咗：{user_count}句")
            st.markdown(f"我講咗：{bot_count}句")
            st.progress(min(user_count/30, 1.0), text="親密度")
        except:
            st.markdown("暫無數據")
    
    # 功能按鈕
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 新對話", use_container_width=True):
            st.session_state.bf.reset_conversation()
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("💾 儲存", use_container_width=True):
            st.success("✅ 已記低")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"💕 最後上線：{datetime.now().strftime('%Y-%m-%d %H:%M')}")