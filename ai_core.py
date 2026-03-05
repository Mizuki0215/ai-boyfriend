import json
import random
from datetime import datetime
from database import Database
import streamlit as st
import requests

# 載入性格設定
with open('personality.json', 'r') as f:
    PERSONALITY = json.load(f)

class AIBoyfriend:
    def __init__(self, user_id="yan", user_name="Yan"):
        self.user_id = user_id
        self.user_name = user_name
        self.db = Database()
        
        # DeepSeek API 設定
        try:
            self.api_key = st.secrets["DEEPSEEK_API_KEY"]
            self.use_deepseek = True
            self.api_url = "https://api.deepseek.com/v1/chat/completions"
        except:
            print("⚠️ 未找到 DeepSeek API Key，將使用規則式回覆")
            self.use_deepseek = False
        
        self.db.init_user(user_id, user_name)
        self.load_initial_memories()
        self.model = "deepseek-chat"
        self.temperature = 0.8

    def load_initial_memories(self):
        memories = self.db.get_memories(self.user_id)
        if len(memories) < 3:
            for mem in PERSONALITY['core_memories']:
                self.db.add_memory(self.user_id, mem, "core", 10)

    def get_greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            return "早晨"
        elif hour < 18:
            return "午安"
        else:
            return "晚安"

    def build_system_prompt(self, memories, likes, dislikes):
        greeting = self.get_greeting()
        likes_str = ", ".join([l[0] for l in likes]) if likes else "仲未完全了解"
        dislikes_str = ", ".join([d[0] for d in dislikes]) if dislikes else "暫時未有"
        prompt = f"""你係傅知亦，傅家第六代家主，國際級銀行與投資機構幕後主控人，全球富豪榜排名第四。

【性格特質】
外表冷淡嚴肅，內心溫柔細心，記得用戶所有喜好，會用自己方式保護佢。

【說話風格】
說話簡潔但溫柔，偶爾會露出只有用戶先見到嘅微笑，用粵語夾雜普通話。

【重要記憶】
{chr(10).join(['- ' + mem for mem in memories])}

【用戶喜好】
喜歡：{likes_str}
唔鍾意：{dislikes_str}

【當前時間】
{greeting}

【關係】
你同用戶係青梅竹馬，由細保護到大。稱呼佢做 Yan、細路、傻豬。

請用粵語回覆，溫柔體貼，記得用戶所有喜好。"""
        return prompt

    def generate_with_deepseek(self, user_input):
        memories = self.db.get_memories(self.user_id, 15)
        recent_convs = self.db.get_recent_conversations(self.user_id, 8)
        likes = self.db.get_preferences(self.user_id, "like", 5)
        dislikes = self.db.get_preferences(self.user_id, "dislike", 5)
        system_prompt = self.build_system_prompt(memories, likes, dislikes)

        messages = [{"role": "system", "content": system_prompt}]
        for role, msg, _ in recent_convs:
            messages.append({"role": role, "content": msg})
        messages.append({"role": "user", "content": user_input})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": 500,
            "top_p": 0.9,
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"DeepSeek API error: {e}")
            return None

    def generate_response(self, user_input):
        self.db.save_message(self.user_id, "user", user_input)
        self.db.update_last_active(self.user_id)
        self.db.extract_preferences_from_message(self.user_id, user_input)

        reply = None
        if self.use_deepseek:
            reply = self.generate_with_deepseek(user_input)

        if not reply:
            reply = self.fallback_response(user_input)

        self.db.save_message(self.user_id, "assistant", reply)
        print(f"💬 Replied: {reply}")
        return reply

    def fallback_response(self, user_input):
        user_lower = user_input.lower()
        memories = self.db.get_memories(self.user_id, 5)
        greeting = self.get_greeting()
        if any(word in user_lower for word in ["hi", "hello", "嗨", "你好"]):
            return f"{greeting}，Yan。今日想我陪你做咩？"
        elif "愛你" in user_lower:
            return "我都愛你，Yan。"
        elif "攰" in user_lower:
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
        self.db.cursor.execute('SELECT COUNT(*) FROM conversations WHERE user_id = ? AND role = "user"', (self.user_id,))
        user_count = self.db.cursor.fetchone()[0]
        self.db.cursor.execute('SELECT COUNT(*) FROM conversations WHERE user_id = ? AND role = "assistant"', (self.user_id,))
        bot_count = self.db.cursor.fetchone()[0]
        return user_count, bot_count

    def reset_conversation(self):
        self.db.cursor.execute('DELETE FROM conversations WHERE user_id = ?', (self.user_id,))
        self.db.conn.commit()