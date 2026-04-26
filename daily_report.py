import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 采集金融数据 (保持不变，已验证稳定)
def get_market_data():
    tickers = {
        "美元/人民币": "USDCNY=X",
        "港股恒指": "^HSI",
        "上证指数": "000001.SS",
        "纳指100": "^NDX",
        "现货黄金": "GC=F",
        "布伦特原油": "BZ=F"
    }
    market_info = []
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="3d")
            if not data.empty:
                current = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                arrow = "🔺" if change > 0 else "🔻"
                fmt = ".4f" if "人民币" in name else ".2f"
                market_info.append(f"{name}: {current:{fmt}} ({arrow}{change:.2f}%)")
        except: continue
    return "\n".join(market_info) if market_info else "金融数据获取延迟"

# 2. 调用 DeepSeek 进行深度总结
def get_llm_summary(market_data):
    api_key = os.getenv("LLM_API_KEY")
    
    # ✅ DeepSeek 标准 API 地址
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"你是一名专业顾问。请分析今日数据并撰写简报，重点关注汇率、AI、生物医疗（NGS）前沿。要求：逻辑严密，风格严谨，使用中文。\n[今日数据]:\n{market_data}"
    
    payload = {
        "model": "deepseek-chat", # 或者使用 deepseek-reasoner 获得更强的逻辑推理
        "messages": [
            {"role": "system", "content": "你是一名顶尖的专业决策支持助手。"},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"【DeepSeek 报错】状态码：{response.status_code}\n详情：{response.text[:100]}"
    except Exception as e:
        return f"【系统提示】连接 DeepSeek 失败: {str(e)[:50]}"

# 3. 发送飞书卡片 (保持紫色高感设计)
def send_feishu_card(summary_text, market_data):
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    card_payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"📊 专业顾问 | 综合决策简报 {datetime.now().strftime('%m-%d')}"},
                "template": "purple"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**📈 全球关键指标**\n{market_data}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**💡 深度洞察与行业动态**\n{summary_text}"}},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "📍 墨西哥城 08:00 | 由 DeepSeek AI 提供智能驱动"}]}
            ]
        }
    }
    requests.post(webhook_url, json=card_payload)

if __name__ == "__main__":
    m_data = get_market_data()
    summary = get_llm_summary(m_data)
    send_feishu_card(summary, m_data)
