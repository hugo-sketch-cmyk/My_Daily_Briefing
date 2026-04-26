import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 采集金融数据 (保持不变)
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

# 2. 终极兼容版 Gemini 调用逻辑
def get_llm_summary(market_data):
    api_key = os.getenv("LLM_API_KEY")
    
    # 尝试的模型列表，按优先顺序排序
    model_list = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    headers = {"Content-Type": "application/json"}
    prompt = f"你是一名专业顾问。分析以下数据并提供简报，重点关注汇率、AI、生物医疗动态，使用中文：\n{market_data}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    # 循环尝试不同的模型，直到有一个成功
    for model in model_list:
        # 使用 v1beta 接口，这是目前最稳健的路径
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            print(f"正在尝试请求模型: {model}...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {model} 请求成功！")
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"❌ {model} 失败，状态码: {response.status_code}")
                continue # 尝试下一个模型
        except Exception as e:
            print(f"连接 {model} 出错: {str(e)}")
            continue

    return "【系统提示】所有 Gemini 模型均尝试失败，请检查 API Key 权限或区域可用性。"

# 3. 发送飞书卡片 (保持不变)
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
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "📍 墨西哥城 08:00 | 智能顾问系统"}]}
            ]
        }
    }
    requests.post(webhook_url, json=card_payload)

if __name__ == "__main__":
    m_data = get_market_data()
    summary = get_llm_summary(m_data)
    send_feishu_card(summary, m_data)
