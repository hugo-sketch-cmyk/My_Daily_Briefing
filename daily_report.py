import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 自动抓取金融与汇率数据
def get_market_data():
    # 监控清单：美元/人民币、恒生指数、上证指数、纳斯达克100、黄金、原油
    tickers = {
        "美元/人民币": "USDCNY=X",
        "港股恒指": "^HSI",
        "上证指数": "000001.SS",
        "纳指100(AI相关)": "^NDX",
        "现货黄金": "GC=F",
        "布伦特原油": "BZ=F"
    }
    market_info = []
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="2d")
            if len(data) >= 2:
                current = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                arrow = "🔺" if change > 0 else "🔻"
                # 汇率保留4位，指数保留2位
                fmt = ".4f" if "人民币" in name else ".2f"
                market_info.append(f"{name}: {current:{fmt}} ({arrow}{change:.2f}%)")
        except:
            continue
    return "\n".join(market_info) if market_info else "暂无实时市场数据"

# 2. 调用 LLM 进行深度总结（针对生物医疗与 AI）
def get_llm_summary(market_data):
    api_key = os.getenv("LLM_API_KEY")
    # 提示：如果您使用国内 API，请修改此处的 URL
    url = "https://api.openai.com/v1/chat/completions" 
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 增强版顾问指令
    prompt = f"""
    你是一名顶尖专业顾问。请基于以下数据撰写简报：
    
    [今日数据]: 
    {market_data}
    
    [重点关注领域]:
    1. 宏观：分析美元汇率对中国市场的潜在影响。
    2. 科技-AI：简述全球 AI 算力或大模型的一项最新进展（需体现顾问洞察）。
    3. 科技-生物医疗：简述 NGS（二代测序）或生物制药的一项前沿动态。
    4. 墨西哥视角：一句话评论对当地中资企业或安全形势的影响。
    
    [要求]: 语气严谨、客观，使用“因为...所以...”逻辑。
    """
    
    payload = {
        "model": "gpt-3.5-turbo", 
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.json()['choices'][0]['message']['content']
    except:
        return "LLM 系统繁忙，请检查 API 配置。"

# 3. 发送飞书互动卡片
def send_feishu_card(summary_text, market_data):
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    card_payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"📊 专业顾问 | 财资与科技简报 {datetime.now().strftime('%m-%d')}"},
                "template": "violet" # 紫色代表科技与深度
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**📈 关键指标 (汇率/指数)**\n{market_data}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**💡 顾问深度洞察**\n{summary_text}"}},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "数据源：Yahoo Finance & AI 分析 | 墨西哥城 08:00"}]}
            ]
        }
    }
    requests.post(webhook_url, json=card_payload)

if __name__ == "__main__":
    m_data = get_market_data()
    summary = get_llm_summary(m_data)
    send_feishu_card(summary, m_data)
