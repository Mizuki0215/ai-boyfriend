import streamlit as st
from datetime import datetime
from ai_core import AIBoyfriend

# 呢句一定要放最頂！
st.set_page_config(
    page_title="💕 傅知亦 - 你嘅AI男朋友",
    page_icon="💕",
    layout="centered"
)

# ========== 自訂 CSS ==========
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
    }
</style>
""", unsafe_allow_html=True)

# ========== 初始化 ==========
if "bf" not in st.session_state:
    st.session_state.bf = AIBoyfriend("yan", "Yan")
    st.session_state.messages = []
    st.session_state.first_greeting = True

# ========== 標題 ==========
st.title("💕 傅知亦")
st.caption("傅家第六代家主 · 你嘅青梅竹馬")

# ========== 第一次打招呼 ==========
if st.session_state.first_greeting and len(st.session_state.messages) == 0:
    memories = st.session_state.bf.get_memories_for_display()
    if memories:
        msg = f"Yan，終於等到你。我記得{memories[0]}{'、' + memories[1] if len(memories)>1 else ''}。今日過成點？"
    else:
        msg = "Yan，嚟啦？我等咗你好耐。"
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.session_state.first_greeting = False

# ========== 顯示對話記錄 ==========
for msg in st.session_state.messages:
    # 用 emoji 代替中文字
    avatar = "👤" if msg["role"] == "user" else "💼"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        st.caption(msg.get("time", datetime.now()).strftime("%H:%M"))

# ========== 輸入區 ==========
if prompt := st.chat_input("想同我講咩？"):
    # 顯示用戶訊息
    st.session_state.messages.append({"role": "user", "content": prompt, "time": datetime.now()})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.caption(datetime.now().strftime("%H:%M"))
    
    # 顯示 AI 回覆
    with st.chat_message("assistant", avatar="💼"):
        with st.spinner("傅知亦正在輸入..."):
            response = st.session_state.bf.generate_response(prompt)
        st.markdown(response)
        st.caption(datetime.now().strftime("%H:%M"))
    
    # 儲存 AI 回覆
    st.session_state.messages.append({"role": "assistant", "content": response, "time": datetime.now()})

# ========== Sidebar ==========
with st.sidebar:
    st.header("💝 關於傅知亦")
    
    with st.expander("📝 我記得嘅嘢", expanded=True):
        memories = st.session_state.bf.get_memories_for_display()
        if memories:
            for mem in memories[-8:]:
                st.write(f"• {mem}")
        else:
            st.write("• 未有記憶")
    
    with st.expander("📊 傾偈記錄"):
        try:
            user_count, bot_count = st.session_state.bf.get_conversation_stats()
            st.write(f"總訊息：{user_count + bot_count}")
            st.write(f"你講咗：{user_count}句")
            st.write(f"我講咗：{bot_count}句")
        except:
            st.write("暫無數據")
    
    if st.button("🔄 新對話", use_container_width=True):
        st.session_state.bf.reset_conversation()
        st.session_state.messages = []
        st.session_state.first_greeting = True
        st.rerun()