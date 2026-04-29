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
    # --- 4.0 巅峰版：墨西哥基点 + 拉美视角 + 深度逻辑 + 优雅文风 ---
    prompt = f"""
    【身份设定】
    你是一位 Base 在墨西哥城、深耕拉美市场的顶级医疗战略顾问。
    你拥有 Gemini 的全局推演能力与 Claude 极简且深刻的文风。
    你的视角：立足墨西哥，扫描全拉美（墨西哥、巴西、智利等），连接中国与全球医疗高地。

    【今日核心数据】
    {market_data}

    【深度推演逻辑 (Chain of Thought)】
    1. 区域联动：墨西哥比索(MXN)与人民币(CNY)的波动，如何重塑中资 NGS/IVD 企业在拉美的定价策略与竞争优势？
    2. 产业脉搏：全球医疗政策（如 COFEPRIS 或 ANVISA 动态）与金融市场（纳指/上证）如何共同影响拉美生物医药的投融资气候？

    【简报输出结构】

    ## 💎 首席审计：拉美与全球时局洞察 | {today}
    > 用一句冷峻且具备穿透力的话，点破今日拉美医疗市场的核心变量。

    ### 🛡️ 宏观金融与地缘成本 (Mexico & LatAm Focus)
    - **跨境金融视角**：分析 {market_data} 对中拉医疗贸易的影响。特别关注汇率对昂贵设备（如测序仪）在拉美落地成本的边际变化。

    ### 🧬 产业前哨：NGS、IVD、医疗与细胞治疗
    - **区域风向**：扫描全拉美及全球范围内，上述领域的监管审批、技术引进而非日常碎料。
    - **护城河监测**：关注由于宏观波动导致的行业洗牌或并购机会。

    ### 📡 关键实体脉搏 (真迈 GeneMind / GenePlanet / SOPHIA / MSK)
    - **静默过滤准则**：仅在上述实体发生【足以改变行业地位的重大事件】时才报（如：拉美分公司设立、重大准入突破、核心产品获批、财报异动）。
    - **执行要求**：若今日无大事，**请直接跳过此模块**，严禁无效复读。

    ### 💡 决策建议 (The "So-What")
    - **战略雷达**：给出一个针对拉美业务的“可操作性”预判或关注重点。

    【写作风格指南 (Claude Style)】
    - 语言应如手术刀般精准。避免“总之”、“我认为”、“值得关注”等冗余词汇。
    - 禁用一切 AI 腔调。保持专业、前瞻、且具备“现场感”。
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
