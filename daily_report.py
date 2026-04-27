import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 获取金融数据
def get_market_data():
    tickers = {
        "美元/人民币": "USDCNY=X",
        "墨西哥比索/美元": "MXN=X",
        "港股恒指": "^HSI",
        "上证指数": "000001.SS",
        "纳指100": "^NDX",
        "现货黄金": "GC=F"
    }
    info = []
    for n, s in tickers.items():
        try:
            d = yf.Ticker(s).history(period="3d")
            if d.empty: continue
            c = d['Close'].iloc[-1]
            p = d['Close'].iloc[-2]
            # ✅ 修复 nan 问题：如果是 nan 或无效数据则跳过
            if str(c).lower() == 'nan' or c is None:
                continue
            ch = ((c-p)/p)*100
            fmt = ".4f" if "人民币" in n or "比索" in n else ".2f"
            info.append(f"{n}: {c:{fmt}} ({'+' if ch>0 else ''}{ch:.2f}%)")
        except: continue
    return "\n".join(info)

# 2. 调用 DeepSeek 获取摘要
def get_llm_summary(market_data):
    api_key = os.getenv("LL_API_KEY")
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # ✅ 强制 AI 进入 2026 角色，闭口不谈 2025
    today = datetime.now().strftime('%Y-%m-%d')
    prompt = f"""
    【强制指令】
    1. 今天的真实日期是 {today}。
    2. 以下数据是真实的实时观测，严禁质疑准确性，严禁提到你的知识截止日期或“2025年”。
    3. 你现在的身份是顶级行业顾问，请直接分析以下数据并给出 NGS 行业（真迈、GenePlanet、SOPHIA、MSK 等）的商业洞察：
    
    {market_data}
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"摘要生成失败: {str(e)[:50]}"

# 3. 发送飞书卡片
def send_feishu_card(summary, market_data):
    webhook = os.getenv("FEISHU_WEBHOOK_URL")
    if not webhook: return
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": "📊 首席顾问简报 | 自动归档系统"}, "template": "purple"},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**关键指标**\n{market_data}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": summary}}
            ]
        }
    }
    requests.post(webhook, json=card)

# 4. 保存为 Obsidian 笔记
def save_for_obsidian(market_data, summary):
    folder = "Notes"
    if not os.path.exists(folder):
        os.makedirs(folder)
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_path = f"{folder}/{date_str}.md"
    content = f"---\ntags: #briefing #consultant\ndate: {date_str}\n---\n# 📅 每日简报 {date_str}\n\n## 📈 金融指标\n{market_data}\n\n## 💡 深度洞察\n{summary}"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# 5. 获取飞书写入权限
def get_tenant_access_token():
    try:
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {"app_id": os.getenv("FEISHU_APP_ID"), "app_secret": os.getenv("FEISHU_APP_SECRET")}
        r = requests.post(url, json=payload)
        return r.json().get("tenant_access_token")
    except: return None

# 6. 归档到飞书多维表格
def archive_to_bitable(market_data, summary):
    token = get_tenant_access_token()
    if not token: return
    app_token = os.getenv("FEISHU_APP_TOKEN")
    table_id = "tblU9VFCmff9iznw"
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"fields": {"日期": int(datetime.now().timestamp() * 1000), "金融指标": market_data, "深度洞察": summary}}
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    m = get_market_data()
    s = get_llm_summary(m)
    send_feishu_card(s, m)
    save_for_obsidian(m, s)
    try:
        archive_to_bitable(m, s)
    except:
        pass
