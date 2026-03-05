import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_path="ai_boyfriend.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # 長期記憶表（重要嘅嘢）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                memory TEXT,
                category TEXT DEFAULT 'general',
                importance INTEGER DEFAULT 5,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP
            )
        ''')
        
        # 對話記錄表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                role TEXT,
                message TEXT,
                sentiment REAL DEFAULT 0,
                created_at TIMESTAMP
            )
        ''')
        
        # 用戶喜好表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                preference_type TEXT,
                preference_value TEXT,
                count INTEGER DEFAULT 1,
                last_updated TIMESTAMP,
                UNIQUE(user_id, preference_type, preference_value)
            )
        ''')
        
        # 用戶資料表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                birthday DATE,
                relationship_start DATE,
                created_at TIMESTAMP,
                last_active TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✅ Database tables created successfully")
    
    # ========== 長期記憶操作 ==========
    def add_memory(self, user_id, memory, category="general", importance=5):
        self.cursor.execute('''
            INSERT INTO long_term_memory (user_id, memory, category, importance, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, memory, category, importance, datetime.now(), datetime.now()))
        self.conn.commit()
        print(f"✅ Added memory: {memory}")
    
    def get_memories(self, user_id, limit=20):
        self.cursor.execute('''
            SELECT memory FROM long_term_memory 
            WHERE user_id = ? 
            ORDER BY importance DESC, last_accessed DESC 
            LIMIT ?
        ''', (user_id, limit))
        return [row[0] for row in self.cursor.fetchall()]
    
    def update_memory_access(self, user_id, memory):
        self.cursor.execute('''
            UPDATE long_term_memory 
            SET last_accessed = ? 
            WHERE user_id = ? AND memory = ?
        ''', (datetime.now(), user_id, memory))
        self.conn.commit()
    
    # ========== 對話操作 ==========
    def save_message(self, user_id, role, message, sentiment=0):
        self.cursor.execute('''
            INSERT INTO conversations (user_id, role, message, sentiment, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, role, message, sentiment, datetime.now()))
        self.conn.commit()
    
    def get_recent_conversations(self, user_id, limit=10):
        self.cursor.execute('''
            SELECT role, message, created_at FROM conversations 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        return list(reversed(self.cursor.fetchall()))
    
    # ========== 用戶喜好操作 ==========
    def add_preference(self, user_id, pref_type, value):
        try:
            self.cursor.execute('''
                INSERT INTO user_preferences (user_id, preference_type, preference_value, count, last_updated)
                VALUES (?, ?, ?, 1, ?)
            ''', (user_id, pref_type, value, datetime.now()))
        except sqlite3.IntegrityError:
            self.cursor.execute('''
                UPDATE user_preferences 
                SET count = count + 1, last_updated = ?
                WHERE user_id = ? AND preference_type = ? AND preference_value = ?
            ''', (datetime.now(), user_id, pref_type, value))
        self.conn.commit()
    
    def get_preferences(self, user_id, pref_type=None, limit=10):
        if pref_type:
            self.cursor.execute('''
                SELECT preference_value, count FROM user_preferences 
                WHERE user_id = ? AND preference_type = ?
                ORDER BY count DESC LIMIT ?
            ''', (user_id, pref_type, limit))
        else:
            self.cursor.execute('''
                SELECT preference_type, preference_value, count FROM user_preferences 
                WHERE user_id = ? 
                ORDER BY count DESC LIMIT ?
            ''', (user_id, limit))
        return self.cursor.fetchall()
    
    # ========== 用戶資料操作 ==========
    def init_user(self, user_id, name):
        self.cursor.execute('''
            INSERT OR IGNORE INTO user_profile (user_id, name, created_at, last_active)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, datetime.now(), datetime.now()))
        self.conn.commit()
        print(f"✅ Initialized user: {name}")
    
    def update_last_active(self, user_id):
        self.cursor.execute('''
            UPDATE user_profile SET last_active = ? WHERE user_id = ?
        ''', (datetime.now(), user_id))
        self.conn.commit()
    
    # ========== 工具函數 ==========
    def extract_preferences_from_message(self, user_id, message):
        """從訊息中抽出喜好"""
        indicators_like = ["我鍾意", "我最鍾意", "我好中意", "我中意", "我like"]
        indicators_dislike = ["我唔鍾意", "我唔中意", "我最憎", "我討厭"]
        
        for ind in indicators_like:
            if ind in message:
                try:
                    # 簡單抽出喜好詞
                    parts = message.split(ind)
                    if len(parts) > 1:
                        like = parts[1].strip().split()[0][:20]
                        if like and len(like) > 0:
                            self.add_preference(user_id, "like", like)
                            self.add_memory(user_id, f"你鍾意{like}", "preference", 8)
                except Exception as e:
                    print(f"Error extracting like: {e}")
        
        for ind in indicators_dislike:
            if ind in message:
                try:
                    parts = message.split(ind)
                    if len(parts) > 1:
                        dislike = parts[1].strip().split()[0][:20]
                        if dislike and len(dislike) > 0:
                            self.add_preference(user_id, "dislike", dislike)
                            self.add_memory(user_id, f"你唔鍾意{dislike}", "preference", 8)
                except Exception as e:
                    print(f"Error extracting dislike: {e}")
    
    def close(self):
        self.conn.close()