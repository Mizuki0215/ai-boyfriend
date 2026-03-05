#!/bin/bash
# AI 男朋友 Telegram Bot 啟動腳本

# 激活虛擬環境
source ai_venv/bin/activate

# 顯示資訊
echo "🚀 啟動 AI 男朋友 Telegram Bot..."
echo "📂 當前目錄: $(pwd)"
echo "🐍 Python: $(which python)"
echo ""

# 行 bot
python telegram_bot.py