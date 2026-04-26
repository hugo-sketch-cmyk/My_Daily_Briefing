import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 采集金融数据 (保持不变)
def get_market_data():
    tickers = {
        "美元/离岸人民币": "USDCNH=X",
        "港股恒生指数": "^HSI",
        "上证指数": "000001.SS",
        "纳指100 (AI核心)": "^NDX",
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

# 2. 修复后的 Gemini 调用逻辑
def get_llm_summary(market_data):
    api_key = os.getenv("LLM_API_KEY")
    
    # ✅ 尝试使用最标准的 v1 接口和 gemini-1.5-flash 模型
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    prompt = f"你是一名专业顾问。分析以下数据并提供简报，重点关注汇率、AI、生物医疗动态：\n{market_data}\n请用中文回答。"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        # 如果 v1 接口报 404，尝试使用 v1beta 备用接口
        if response.status_code == 404:
            url_beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            response = requests.post(url_beta, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            # ✅ 如果还是报错，打印出具体的错误信息到飞书，方便我们排查
            return f"【Gemini 报错】状态码：{response.status_code}\n详情：{response.text[:100]}"
    except Exception as e:
        return f"【系统提示】连接失败: {str(e)[:50]}"

# 3. 发送紫色高级感互动卡片
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
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "📍 墨西哥城 08:00 | 由 Google Gemini 驱动"}]}
            ]
        }
    }
    requests.post(webhook_url, json=card_payload)

if __name__ == "__main__":
    m_data = get_market_data()
    summary = get_llm_summary(m_data)
    send_feishu_card(summary, m_data)
