import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 采集全维度金融数据
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
        except:
            continue
    return "\n".join(market_info) if market_info else "金融数据获取延迟"

# 2. 调用 Google Gemini 进行深度总结
def get_llm_summary(market_data):
    api_key = os.getenv("LLM_API_KEY")
    # ✅ 这是 Gemini 的专用接口地址
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
    你是一名专业顾问。请分析今日数据并撰写简报：
    [今日指标]:
    {market_data}
    
    [重点任务]:
    1. 宏观：简评汇率波动对中资企业的潜在影响。
    2. AI 科技：总结一条今日全球 AI 领域的重大进展。
    3. 生物医疗：总结一条关于 NGS 或生物制药的前沿突破。
    4. 墨西哥视角：给出一个针对当地经贸安全或近岸外包的建议。
    
    [要求]: 逻辑严密，每条动态需体现“事实+影响”。语言：中文。
    """
    
    # ✅ 这是 Gemini 专用的数据格式（和 OpenAI 完全不同）
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            # ✅ 解析 Gemini 特有的返回结构
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"【Gemini 错误】状态码：{response.status_code}，请检查 API Key 是否有效。"
    except Exception as e:
        return f"【系统提示】连接 Gemini 失败。错误详情: {str(e)[:50]}"

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
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "📍 墨西哥城 08:00 | 由 Google Gemini 提供智能驱动"}]}
            ]
        }
    }
    requests.post(webhook_url, json=card_payload)

if __name__ == "__main__":
    m_data = get_market_data()
    summary = get_llm_summary(m_data)
    send_feishu_card(summary, m_data)
