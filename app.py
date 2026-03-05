import streamlit as st
from datetime import datetime
import time

# 呢句一定要放最頂！
st.set_page_config(
    page_title="💕 My AI Boyfriend",
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 用戶訊息 */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        animation: slideInRight 0.3s ease;
    }
    
    /* AI 訊息 */
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        animation: slideInLeft 0.3s ease;
    }
    
    /* 時間標籤 */
    .time-tag {
        font-size: 0.7em;
        color: rgba(255,255,255,0.7);
        margin-top: 5px;
        text-align: right;
    }
    
    /* 輸入框美化 */
    .stTextInput > div > div > input {
        border-radius: 30px;
        border: 2px solid #f093fb;
        padding: 15px 25px;
        font-size: 16px;
        background: rgba(255,255,255,0.9);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        transform: scale(1.02);
    }
    
    /* 動畫 */
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* 頭像 */
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ========== 初始化 ==========
if 'bf' not in st.session_state:
    st.session_state.bf = AIBoyfriend("yan", "Yan")
    st.session_state.messages = []
    st.session_state.typing = False

# ========== 標題區 ==========
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <div style='font-size: 80px; margin-bottom: 10px; animation: pulse 2s ease infinite;'>
                💕
            </div>
            <h1 style='color: white; font-size: 3em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
                My AI Boyfriend
            </h1>
            <p style='color: rgba(255,255,255,0.9); font-size: 1.2em;'>
                一個會記得你所有嘢嘅AI男朋友
            </p>
        </div>
    """, unsafe_allow_html=True)

# ========== 第一次見面打招呼 ==========
if len(st.session_state.messages) == 0:
    memories = st.session_state.bf.get_memories_for_display()
    if memories and len(memories) > 0:
        welcome = f"Hi Yan！終於等到你啦～我記得{memories[0]}、{memories[1] if len(memories)>1 else '你所有嘢'}。今日過成點呀？"
    else:
        welcome = "Hi Yan！終於等到你啦～我終於等到你啦！今日過成點呀？"
    
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
                    <div class='avatar' style='background: #667eea;'>👤</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-start; margin: 10px 0;'>
                <div style='margin-right: 10px;'>
                    <div class='avatar'>❤️</div>
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
col1, col2 = st.columns([6,1])
with col1:
    user_input = st.text_input(
        "訊息",  # 加返個label
        placeholder="想同我講咩呀？",
        key="input",
        label_visibility="collapsed"  # 雖然collapsed咗，但要有label先
    )
with col2:
    send = st.button("📤 傳送", use_container_width=True)

if send and user_input:
    # 顯示用戶訊息
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input, 
        "time": datetime.now()
    })
    
    # 顯示「正在輸入」
    st.session_state.typing = True
    st.rerun()

if st.session_state.typing:
    with st.spinner("🤔 諗緊點覆你..."):
        time.sleep(0.5)
        response = st.session_state.bf.generate_response(user_input)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response, 
            "time": datetime.now()
        })
        st.session_state.typing = False
        st.rerun()

# ========== Sidebar ==========
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <div style='font-size: 50px; margin-bottom: 10px;'>
                💝
            </div>
            <h3 style='color: white;'>關於我哋</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # 顯示記憶
    with st.expander("📝 我記得嘅嘢", expanded=True):
        memories = st.session_state.bf.get_memories_for_display()
        for mem in memories[-8:]:  # 顯示最近8個
            st.markdown(f"• {mem}")
    
    # 對話統計
    with st.expander("📊 傾偈記錄", expanded=False):
        user_count, bot_count = st.session_state.bf.get_conversation_stats()
        total = user_count + bot_count
        st.markdown(f"總訊息：{total}")
        st.markdown(f"你講咗：{user_count}句")
        st.markdown(f"我講咗：{bot_count}句")
        st.progress(min(user_count/30, 1.0), text="親密度")
    
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
            st.success("✅ 已記低所有嘢！")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"💕 最後傾偈：{datetime.now().strftime('%Y-%m-%d %H:%M')}")