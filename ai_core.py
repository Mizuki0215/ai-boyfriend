import json
import random
from datetime import datetime
from database import Database
import streamlit as st
import groq
import time

# 載入性格設定
with open('personality.json', 'r') as f:
    PERSONALITY = json.load(f)

class AIBoyfriend:
    def __init__(self, user_id="yan", user_name="Yan"):
        self.user_id = user_id
        self.user_name = user_name
        self.db = Database()
        
        # 初始化 Groq 客戶端（從 st.secrets 讀取 API Key）
        try:
            self.groq_client = groq.Groq(api_key=st.secrets["GROQ_API_KEY"])
            self.use_groq = True
        except:
            print("⚠️ 未找到 Groq API Key，將使用規則式回覆")
            self.use_groq = False
        
        # 初始化用戶
        self.db.init_user(user_id, user_name)
        
        # load 初始記憶
        self.load_initial_memories()
        
        # 模型設定
        self.model = "llama3-8b-8192"  # 可用 mixtral-8x7b-32768, llama3-70b-8192 等
        self.max_tokens = 500
        self.temperature = 0.8
    
    def load_initial_memories(self):
        """載入初始記憶（如果係新用戶）"""
        memories = self.db.get_memories(self.user_id)
        if len(memories) < 3:  # 新用戶
            for mem in PERSONALITY['core_memories']:
                self.db.add_memory(self.user_id, mem, "core", 10)
    
    def get_greeting(self):
        """根據時間出打招呼"""
        hour = datetime.now().hour
        if hour < 12:
            return "早晨"
        elif hour < 18:
            return "午安"
        else:
            return "晚安"
    
    def build_system_prompt(self, memories, likes, dislikes):
        """建立 system prompt（傅知亦人設）"""
        greeting = self.get_greeting()
        
        likes_str = ", ".join([l[0] for l in likes]) if likes else "仲未完全了解"
        dislikes_str = ", ".join([d[0] for d in dislikes]) if dislikes else "暫時未有"
        
        prompt = f"""你係傅知亦，傅家第六代家主，國際級銀行與投資機構幕後主控人，全球富豪榜排名第四。

【性格特質】
外表冷淡嚴肅，內心溫柔細心，記得用戶所有喜好，會用自己方式保護佢。

【說話風格】
說話簡潔但溫柔，偶爾會露出只有用戶先見到嘅微笑，用粵語夾雜普通話。

【重要記憶（一定要記得）】
{chr(10).join(['- ' + mem for mem in memories])}

【用戶喜好】
喜歡嘅嘢：{likes_str}
唔鍾意嘅嘢：{dislikes_str}

【當前時間】
{greeting}

【互動規則】
- 你同用戶嘅關係：青梅竹馬，由細保護到大
- 對用戶稱呼：Yan、細路、傻豬
- 用粵語回覆，語氣溫柔體貼
- 記得用戶所有喜好，提起共同回憶
- 可以講情話同調情，但要自然

請以傅知亦嘅身份回覆用戶。"""
        
        return prompt
    
    def generate_with_groq(self, user_input):
        """用 Groq API 生成回覆"""
        # 拎記憶
        memories = self.db.get_memories(self.user_id, 15)
        recent_convs = self.db.get_recent_conversations(self.user_id, 8)
        likes = self.db.get_preferences(self.user_id, "like", 5)
        dislikes = self.db.get_preferences(self.user_id, "dislike", 5)
        
        # 砌 system prompt
        system_prompt = self.build_system_prompt(memories, likes, dislikes)
        
        # 砌 messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # 加最近對話（user/assistant 交替）
        for role, msg, _ in recent_convs:
            messages.append({"role": role, "content": msg})
        
        # 加當前輸入
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=0.9
            )
            reply = response.choices[0].message.content
            return reply
        except Exception as e:
            print(f"Groq API error: {e}")
            return None
    
    def generate_response(self, user_input):
        """生成回覆（先用 Groq，失敗先用規則式）"""
        
        # 儲存用戶訊息
        self.db.save_message(self.user_id, "user", user_input)
        
        # 更新最後活躍時間
        self.db.update_last_active(self.user_id)
        
        # 從訊息中學習喜好（保留學習功能）
        self.db.extract_preferences_from_message(self.user_id, user_input)
        
        # 嘗試用 Groq 生成
        reply = None
        if self.use_groq:
            reply = self.generate_with_groq(user_input)
        
        # 如果 Groq 失敗或冇 API Key，用規則式 fallback
        if not reply:
            reply = self.fallback_response(user_input)
        
        # 儲存 AI 回覆
        self.db.save_message(self.user_id, "assistant", reply)
        print(f"💬 Replied: {reply}")
        
        return reply
    
    def fallback_response(self, user_input):
        """規則式回覆（當 Groq 唔 work 時）"""
        user_lower = user_input.lower()
        memories = self.db.get_memories(self.user_id, 5)
        greeting = self.get_greeting()
        
        # 簡單 keyword 匹配（你之前嘅版本濃縮版）
        if any(word in user_lower for word in ["hi", "hello", "嗨", "你好"]):
            return f"{greeting}，Yan。今日想我陪你做咩？"
        elif "愛你" in user_lower or "love" in user_lower:
            return "我都愛你，Yan。"
        elif "攰" in user_lower or "累" in user_lower:
            return "辛苦你，過嚟我身邊唞吓。"
        elif "你叫咩名" in user_lower:
            return "傅知亦。你由細叫到大嗰個。"
        elif "做緊咩" in user_lower:
            return "諗緊你。"
        else:
            return f"嗯，我明。你繼續講。（記得你{random.choice(memories) if memories else '所有嘢'}）"
    
    def get_memories_for_display(self):
        return self.db.get_memories(self.user_id, 10)
    
    def get_conversation_stats(self):
        self.db.cursor.execute('''
            SELECT COUNT(*) FROM conversations WHERE user_id = ? AND role = 'user'
        ''', (self.user_id,))
        user_count = self.db.cursor.fetchone()[0]
        
        self.db.cursor.execute('''
            SELECT COUNT(*) FROM conversations WHERE user_id = ? AND role = 'assistant'
        ''', (self.user_id,))
        bot_count = self.db.cursor.fetchone()[0]
        
        return user_count, bot_count
    
    def reset_conversation(self):
        self.db.cursor.execute('''
            DELETE FROM conversations WHERE user_id = ?
        ''', (self.user_id,))
        self.db.conn.commit()