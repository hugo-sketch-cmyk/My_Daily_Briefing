import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 采集全维度金融数据
def get_market_data():
    tickers = {
        "美元/人民币": "USDCNY=X",
        "港股恒指": "^HSI",
        "上证指数": "000001.SS",
        "纳指100(AI核心)": "^NDX",
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
        except:
            continue
    return "\n".join(market_info) if market_info else "金融数据获取延迟"

# 2. 调用 LLM 进行深度行业总结
def get_llm_summary(market_data):
    api_key = os.getenv("LLM_API_KEY")
    # 如果您的 API 提供商不同，请修改此 URL
    url = "https://api.openai.com/v1/chat/completions" 
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    prompt = f"""
    你是一名专业顾问。请分析今日数据并提供简报：
    [今日指标]:
    {market_data}
    
    [重点任务]:
    1. 宏观：简评汇率波动的潜在影响。
    2. 科技动态：搜寻并总结一条最新的全球 AI 科技进展。
    3. 医疗动态：搜寻并总结一条关于生物医药或 NGS（二代测序）的前沿突破。
    4. 墨西哥评论：给出一条针对当地安全或经贸的简短顾问建议。
    
    [风格]: 严谨、专业、因果导向。
    """
    payload = {
        "model": "gpt-3.5-turbo", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.json()['choices'][0]['message']['content']
    except:
        return "LLM 摘要生成超时，请检查 API 额度。"

# 3. 发送紫色专业卡片
def send_feishu_card(summary_text, market_data):
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    card_payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"📊 专业顾问 | 每日综合简报 {datetime.now().strftime('%m-%d')}"},
                "template": "purple" # 紫色代表深度与科技
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**📈 全球关键指标**\n{market_data}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**💡 深度洞察与科技动态**\n{summary_text}"}},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "📍 墨西哥城 08:00 | 自动化顾问系统 V3.0"}]}
            ]
        }
    }
    requests.post(webhook_url, json=card_payload)

if __name__ == "__main__":
    m_data = get_market_data()
    summary = get_llm_summary(m_data)
    send_feishu_card(summary, m_data)
