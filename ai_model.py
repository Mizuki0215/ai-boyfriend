import ollama
import json
from datetime import datetime

class AIModel:
    def __init__(self, model_name="qwen2.5:7b"):
        self.model_name = model_name
        # 檢查 model 是否存在
        try:
            ollama.show(model_name)
        except:
            print(f"Downloading {model_name}...")
            ollama.pull(model_name)
    
    def generate_response(self, system_prompt, user_input, conversation_history=[]):
        """用 Ollama 生成回覆"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 加對話歷史
        for role, msg in conversation_history[-5:]:  # 最近5句
            messages.append({"role": role, "content": msg})
        
        # 加當前輸入
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.8,  # 創意度
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            )
            return response['message']['content']
        except Exception as e:
            print(f"Ollama error: {e}")
            return "對唔住，我而家有啲hang hang地，可唔可以再講多次？"
    
    def get_greeting(self):
        """根據時間出打招呼"""
        hour = datetime.now().hour
        if hour < 12:
            return "早晨"
        elif hour < 18:
            return "午安"
        else:
            return "晚安"