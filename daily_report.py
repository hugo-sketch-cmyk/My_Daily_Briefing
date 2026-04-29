import os
import requests
import yfinance as yf
from datetime import datetime

# 1. 获取金融数据（包含核心汇率与股市大盘）
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
            if str(c).lower() == 'nan' or c is None: continue
            ch = ((c-p)/p)*100
            fmt = ".4f" if "币" in n or "比索" in n else ".2f"
            info.append(f"{n}: {c:{fmt}} ({'+' if ch>0 else ''}{ch:.2f}%)")
        except: continue
    return "\n".join(info)

# 2. 核心双层大脑逻辑
def get_llm_summary(market_data):
    # ✅ 修正变量名，确保与 GitHub Secrets 一致
    api_key = os.getenv("LLM_API_KEY")
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # --- 双层身份 & 混合视角 Prompt ---
    prompt = f"""
    【角色设定】
    你是一位拥有“双重视野”的顶级顾问，当前时间是 2026 年 4 月：
    1. 第一层：全球首席投资策略师。关注宏观大环境、中美汇率（CNY）、美股、A股及港股联动。
    2. 第二层：Base 在墨西哥城的拉美战略官。深耕拉美医疗（NGS/IVD/细胞治疗）与拉美数字经济（电商圈，如 MELI, Amazon Mexico）。

    【今日底层数据】
    {market_data}

    【简报输出结构】

    ## 🏛️ 第一层：全球投资专家审计 | {today}
    > 用 Gemini 的宏观深度分析今日资本情绪。
    - **宏观与汇率推演**：针对 {market_data}，剖析中美博弈背景下的汇率传导对全球流动性的影响。
    - **权益市场冷暖**：解读美、中、港三地股市异动背后的资本逻辑。

    ## 🇲🇽 第二层：拉美战略官深度观察 (Mexico & LatAm Focus)
    > 用 Claude 的细腻文风，结合投资视角审视本地基本面。
    - **医疗与生命科学**：扫描全拉美 NGS、IVD、细胞治疗的重大监管、技术或资本变量。
    - **拉美数字经济与电商**：关注拉美电商（Mercado Libre, Amazon, Shopee）动态及物流/支付基建的波动。

    ### 📡 关键实体脉搏 (真迈 GeneMind / GenePlanet / SOPHIA / MSK)
    - **静默规则**：仅在发生足以改变行业地位的重大事件时汇报（如拉美准入突破、核心财报异动）。若无大事，请**完全忽略**。

    ### 💡 综合决策建议 (The "So-What")
    - 结合全球投资环境与拉美实地情况，给出一个针对拉美业务的“可操作性”预判。

    【写作要求】：严禁 AI 废话。语言应如精英密电般冷峻、精准、充满洞察力。
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        res_json = r.json()
        if r.status_code != 200:
            return f"❌ 认证失败或API错误 (状态码 {r.status_code}): {res_json.get('error', {}).get('message', '未知错误')}"
        return res_json['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ 连接异常: {str(e)}"

# 3. 发送飞书卡片（增加视觉美感）
def send_feishu_card(summary, market_data):
    webhook = os.getenv("FEISHU_WEBHOOK_URL")
    if not webhook: return
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": f"💎 全球视野 & 拉美内参 | {datetime.now().strftime('%Y-%m-%d')}"}, "template": "violet"},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**📊 宏观金融监测**\n{market_data}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": summary}}
            ]
        }
    }
    requests.post(webhook, json=card)

# 4. 保存为 Obsidian 笔记（增加 LatAm 标签）
def save_for_obsidian(market_data, summary):
    folder = "Notes"
    if not os.path.exists(folder): os.makedirs(folder)
    date_str = datetime.now().strftime('%Y-%m-%d')
    content = f"---\ntags: #Investment #LatAm #Ecomm #Medical\ndate: {date_str}\n---\n# 📅 每日策略简报 {date_str}\n\n{summary}\n\n---\n**底层数据备查**:\n{market_data}"
    with open(f"{folder}/{date_str}.md", "w", encoding="utf-8") as f: f.write(content)

# 5. 归档到飞书多维表格
def archive_to_bitable(market_data, summary):
    try:
        r_auth = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", 
                               json={"app_id": os.getenv("FEISHU_APP_ID"), "app_secret": os.getenv("FEISHU_APP_SECRET")})
        token = r_auth.json().get("tenant_access_token")
        if not token: return
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {"fields": {"日期": int(datetime.now().timestamp() * 1000), "金融指标": market_data, "深度洞察": summary}}
        requests.post(f"https://open.feishu.cn/open-apis/bitable/v1/apps/{os.getenv('FEISHU_APP_TOKEN')}/tables/tblU9VFCmff9iznw/records", 
                      json=payload, headers=headers)
    except: pass

if __name__ == "__main__":
    m = get_market_data()
    s = get_llm_summary(m)
    send_feishu_card(s, m)
    save_for_obsidian(m, s)
    archive_to_bitable(m, s)
