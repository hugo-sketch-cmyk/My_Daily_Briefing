import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 采集全维度金融数据 (包含全球主要市场与汇率)
def get_market_data():
    tickers = {
        "美元/离岸人民币": "USDCNH=X",
        "墨西哥比索/美元": "MXN=X",
        "港股恒生指数": "^HSI",
        "上证指数": "000001.SS",
        "纳指100(AI核心)": "^NDX",
        "墨西哥MXX指数": "^MXX",
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
                fmt = ".4f" if "人民币" in name or "比索" in name else ".2f"
                market_info.append(f"{name}: {current:{fmt}} ({arrow}{change:.2f}%)")
        except: continue
    return "\n".join(market_info) if market_info else "金融数据获取延迟"

# 2. 调用 DeepSeek 进行全维度深度总结 (宏观 + 行业)
def get_llm_summary(market_data):
    api_key = os.getenv("LLM_API_KEY")
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # 综合版深度 Prompt
    prompt = f"""
    你是一名顶级专业顾问。请分析以下数据并撰写一份全维度简报：
    
    [今日市场指标]:
    {market_data}
    
    [情报监控要求]:
    1. 宏观政经：分析全球增长、利率决策及重要地缘政治动态（重点关注美、中、墨）。
    2. 上游动态：监控 Illumina, MGI(华大智造), 以及 **真迈生物 (Zhenmai)** 的技术与商业动作。
    3. 中游/生信：分析 **GenePlanet**, **Gene Solutions**, **SOPHIA GENETICS** 的全球布局及 **MSK** 的科研突破。
    4. 行业技术：总结当日 AI 科技（算力/模型）与 NGS（测序技术/临床准入）的核心进展。
    5. 监管预警：关注 FDA, NMPA 及墨西哥 **COFEPRIS** 的政策变动。
    
    [格式要求]:
    - 使用 Markdown 标题区分板块。
    - 每一条信息必须包含“事实+潜在影响分析”。
    - 针对墨西哥城(Mexico City)背景给出一务务实建议。
    - 风格严谨、客观、逻辑严密。
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一名具备全球视野的商业策略与生物技术顾问。"},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"【DeepSeek 报告生成失败】状态码：{response.status_code}"
    except Exception as e:
        return f"【系统告警】LLM 连接中断: {str(e)[:50]}"

# 3. 发送紫色高级互动卡片
def send_feishu_card(summary_text, market_data):
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    card_payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"💎 首席顾问简报 | 全球综述 {datetime.now().strftime('%m-%d')}"},
                "template": "purple"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**📊 全球金融与汇率快报**\n{market_data}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": summary_text}},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "📍 墨西哥城 08:00 | 决策支持系统 3.0 正式版"}]}
            ]
        }
    }
    requests.post(webhook_url, json=card_payload)

if __name__ == "__main__":
    m_data = get_market_data()
    summary = get_llm_summary(m_data)
    send_feishu_card(summary, m_data)
