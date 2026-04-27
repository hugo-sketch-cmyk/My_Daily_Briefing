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
# --- 升级版获取摘要函数 ---
def get_llm_summary(market_data):
    api_key = os.getenv("LLM_API_KEY")
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    today = datetime.now().strftime('%Y-%m-%d')
    # 💡 换成“资深顾问”口吻，避免触发 AI 的防御机制
    prompt = f"""
    作为一名深耕医疗与金融领域的资深顾问，请基于以下 2026 年的实时市场观测数据，
    结合 NGS 行业（重点关注真迈生物、GenePlanet、SOPHIA GENETICS、MSK 等动态）
    撰写一份专业的深度分析简报。
    
    【今日数据节点】: {today}
    【市场观测指标】:
    {market_data}
    
    请直接进入深度解读，从宏观趋势和企业动态两个维度展开，无需开场白或免责声明。
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        res_json = r.json()
        
        # ✅ 新增：如果 API 返回错误，直接显示错误详情
        if r.status_code != 200:
            error_msg = res_json.get('error', {}).get('message', '未知 API 错误')
            return f"❌ DeepSeek API 报错 (状态码 {r.status_code}): {error_msg}"
        
        return res_json['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ 系统连接异常: {str(e)}"

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
