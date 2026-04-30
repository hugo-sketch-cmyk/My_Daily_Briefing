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
   # --- 6.0 终极版：全球宏观决策 (剥离特定背景) + 拉美战略与溯源 ---
    prompt = f"""
    【角色审计协议】
    当前时间：2026 年 4 月。你必须以“双层大脑”模块化运行，严禁话题冗余：

    【第一层：全球宏观投资专家 (Global Macro Vision)】
    - **职责**：跳出特定行业与地区，进行纯粹的全球宏观政经、利率决策与地缘政治分析。
    - **宏观与汇率推演**：基于 {market_data} 分析全球主要货币对（重点：中美汇率 CNY 走向）的博弈。分析全球增长逻辑、大宗商品（黄金、原油）与货运指数的共振。
    - **全球股市逻辑**：透视美股、A股、港股核心指数异动背后的流动性真相，不局限于医疗板块。

    【第二层：墨西哥基点·拉美战略顾问 (LatAm & Vertical Strategy)】
    - **职责**：深耕拉美市场（重点：墨西哥、巴西、智利），整合垂直领域（NGS/IVD/细胞治疗/电商）动态。
    - **区域聚焦**：跟踪拉美政经、安全及社会动态。分析 Mercado Libre 等电商巨头与物流基建。
    - **垂直领域溯源（强制）**：
        - 针对医疗、生物、IVD 领域的政策动态，必须标注新闻来源或权威发布机构（如：COFEPRIS, ANVISA, WHO, 或主流财经媒体）。
        - 实体监控：真迈(GeneMind)/GenePlanet/SOPHIA/MSK 仅在发生足以改变行业平衡的重大变量时汇报，否则跳过。

    ### 🛡️ 逻辑审计结论 (Summary of Action Items)
    - **So-What**：结合第一层全球波动与第二层本地执行，给出一个具备“批判性思维”的最优行动建议。

    【语气标准】：严谨、职业、客观。优先使用数据与逻辑连接词，禁止华丽修辞，严禁 AI 式冗余。
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
