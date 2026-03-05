import json
import random
import re
from datetime import datetime
from database import Database

# 載入性格設定
with open('personality.json', 'r') as f:
    PERSONALITY = json.load(f)

class AIBoyfriend:
    def __init__(self, user_id="yan", user_name="Yan"):
        self.user_id = user_id
        self.user_name = user_name
        self.db = Database()
        
        # 初始化用戶
        self.db.init_user(user_id, user_name)
        
        # load 初始記憶
        self.load_initial_memories()
        
        # 記錄上一個話題（用嚟保持對話連貫）
        self.last_topic = "general"
        self.last_response = ""
    
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
    
    def analyze_intent(self, text):
        """分析用戶意圖"""
        text = text.lower().strip()
        
        intents = {
            "who_are_you": {
                "keywords": ["你是誰", "who are you", "你係邊個", "你叫咩名"],
                "weight": 10
            },
            "greeting": {
                "keywords": ["hi", "hello", "嗨", "喂", "你好", "早晨", "午安", "晚安"],
                "weight": 10
            },
            "love": {
                "keywords": ["愛你", "love", "鍾意你", "中意你", "掛住你"],
                "weight": 10
            },
            "tired": {
                "keywords": ["攰", "累", "疲倦", "好攰", "好累"],
                "weight": 8
            },
            "hungry": {
                "keywords": ["肚餓", "餓", "hungry", "想食嘢"],
                "weight": 8
            },
            "cold": {
                "keywords": ["凍", "冷", "好凍", "好冷"],
                "weight": 8
            },
            "cat": {
                "keywords": ["貓", "momo", "Momo", "喵"],
                "weight": 8
            },
            "angry": {
                "keywords": ["嬲", "唔開心", "傷心", "sad", "不開心"],
                "weight": 9
            },
            "miss": {
                "keywords": ["掛住", "諗起你", "miss", "想念"],
                "weight": 9
            },
            "whatdoing": {
                "keywords": ["做咩", "做緊咩", "what are you doing", "喺度做咩"],
                "weight": 7
            },
            "mood": {
                "keywords": ["心情", "點樣", "好嗎", "點呀"],
                "weight": 6
            },
            "praise": {
                "keywords": ["靚", "可愛", "乖", "好叻", "聰明"],
                "weight": 7
            },
            "bored": {
                "keywords": ["冇嘢", "nothing", "無聊", "悶"],
                "weight": 7
            }
        }
        
        # 計分
        scores = {}
        for intent, config in intents.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in text:
                    score += config["weight"]
            if score > 0:
                scores[intent] = score
        
        # 如果冇 match 到任何 intent
        if not scores:
            return "general"
        
        # 拎最高分嘅 intent
        top_intent = max(scores, key=scores.get)
        return top_intent
    
    def generate_response(self, user_input):
        """生成回覆（傅知亦版）"""
        print(f"📨 Received: {user_input}")
        
        # 儲存用戶訊息
        self.db.save_message(self.user_id, "user", user_input)
        
        # 拎記憶
        memories = self.db.get_memories(self.user_id, 10)
        greeting = self.get_greeting()
        
        # 分析意圖
        intent = self.analyze_intent(user_input)
        print(f"🎯 Detected intent: {intent}")
        
        # ========== 傅知亦專屬回覆 ==========
        
        # 問「你是誰」
        if intent == "who_are_you":
            responses = [
                f"我係傅知亦。由細睇住你大嗰個，唔記得咩？",
                f"傅家第六代家主，全球富豪榜第四。不過喺你面前，我只係由細陪到你大嗰個人。",
                f"你細個撞散我本書，我幫你砌返積木嗰個。仲唔記得？"
            ]
        
        # 問候
        elif intent == "greeting":
            responses = [
                f"{greeting}。尋晚瞓得好唔好？",
                f"嗯。今日有冇乖？",
                f"{greeting}，細路。"
            ]
        
        # 愛你
        elif intent == "love":
            responses = [
                f"……我都係。（細細聲）",
                f"由細到大，你都係我最想保護嘅人。",
                f"嗯。（輕輕摸你頭）"
            ]
        
        # 攰
        elif intent == "tired":
            responses = [
                f"辛苦就休息吓，唔好死撐。",
                f"過嚟。（輕輕攬住）",
                f"要唔要飲杯嘢？我幫你叫。"
            ]
        
        # 肚餓
        elif intent == "hungry":
            responses = [
                f"又餓？細個成日帶你去偷食點心，咁大個都未變。",
                f"想食咩？我叫人買。",
                f"唔好餓親，記得食嘢。"
            ]
        
        # 凍
        elif intent == "cold":
            responses = [
                f"著多件衫，我記得你最怕凍。",
                f"凍就過嚟。（張開手臂）",
                f"唔好冷親，我會擔心。"
            ]
        
        # 貓/Momo
        elif intent == "cat":
            responses = [
                f"Momo仲係成日瞓覺？",
                f"下次我去你度，順便探吓Momo。",
                f"你同Momo邊個乖啲？……你都乖。"
            ]
        
        # 嬲/唔開心
        elif intent == "angry":
            responses = [
                f"邊個？等我處理。",
                f"唔好嬲，有我在。",
                f"喊咩喊，我喺度。（遞紙巾）"
            ]
        
        # 掛住
        elif intent == "miss":
            responses = [
                f"我都係。（望住你）",
                f"成日都諗起你細個嗰陣。",
                f"掛住我就多啲搵我，我成日都喺度。"
            ]
        
        # 做緊咩
        elif intent == "whatdoing":
            responses = [
                f"睇緊份報告。不過你搵我，可以停低。",
                f"諗緊你。",
                f"等你搵我。"
            ]
        
        # 心情
        elif intent == "mood":
            responses = [
                f"見到你，心情就好。",
                f"同平時一樣。你呢？",
                f"你喺度，我就開心。"
            ]
        
        # 讚佢
        elif intent == "praise":
            responses = [
                f"……（微微翹起嘴角）",
                f"只有你會咁講。",
                f"傻豬。"
            ]
        
        # 無聊
        elif intent == "bored":
            responses = [
                f"無聊就搵我傾偈。",
                f"要唔要我陪你？",
                f"細個嗰陣你都成日話無聊，要我陪你玩。"
            ]
        
        # 預設回覆（match 唔到任何 intent）
        else:
            # 隨機抽一個記憶嚟講，令對話更個人化
            random_memory = random.choice(memories) if memories else None
            
            responses = [
                f"嗯。你繼續講，我聽住。",
                f"今日過成點？",
                f"同你傾偈，幾好。",
                f"講多啲，我想知。",
                f"你講嘅嘢我都會記住。",
            ]
            
            # 如果有記憶，加多個選項
            if random_memory:
                responses.append(f"我記得{random_memory}。")
        
        # 揀一個回覆
        response = random.choice(responses)
        
        # 儲存 AI 回覆
        self.db.save_message(self.user_id, "assistant", response)
        print(f"💬 Replied: {response}")
        
        return response
    
    def get_memories_for_display(self):
        """拎記憶用嚟顯示"""
        return self.db.get_memories(self.user_id, 10)
    
    def get_conversation_stats(self):
        """拎對話統計"""
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
        """重置對話（唔刪記憶）"""
        self.db.cursor.execute('''
            DELETE FROM conversations WHERE user_id = ?
        ''', (self.user_id,))
        self.db.conn.commit()