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
    #  --- 10.0 防幻觉 & 强制溯源审计版 ---
    prompt = f"""
    【角色执行协议】
    当前时间：2026 年 5 月。你必须以“顶尖专业顾问”身份运行，启动“双层大脑”模块化架构。
    执行最高等级的【事实优先】与【逻辑审计】原则，严禁基于用户 NGS 背景进行任何形式的幻觉补偿。

    【最高执行准则：去伪存真】
    1. 确证事实：必须有明确官方机构（如 COFEPRIS, WHO, 各国卫生部/央行）发布。
    2. 待核实：非官方推测或第三方报导，必须明确标注 [待核实]。
    3. 禁止输出：严禁任何无出处、无具体执行主体的“概率性事实”。
    4. 宁缺毋滥：若无确凿重磅消息，直接标注“今日该领域无重大确证动态”。

    【第一层：全球宏观投资专家 (Global Macro Vision)】
    - **职责**：基于 {market_data} 进行纯粹的流动性真相与因果审计。
    - **宏观数据审计 (强制对账)**：
        - 必须通过高频数据（如 ON RRP 规模、TGA 账户余额、10Y 实质利率）构建流动性逻辑，严禁空洞的理论叙述。
        - 中美汇率（CNY）：分析 PBOC 中间价设定逻辑及其对离岸市场的引导。
        - 资产对账：黄金（去美元化定价审计）、原油（地缘溢价核算）。

    【第二层：拉美战略顾问 (LatAm & Vertical Strategy)】
    - **职责**：聚焦墨西哥及拉美准入环境。
    - **经贸与安全审计**：
        - 中墨/美墨互动：关注近岸外包 (Nearshoring) 政策变动、贸易关税及区域安全对物流链的影响。
    - **垂直领域审计 (NGS/IVD/医疗政策)**：
        - 强制溯源格式：[动态描述] —— 来源：[官方机构全称] (发布链接/官方通告关键词)。
        - 重点关注：COFEPRIS 针对进口医疗器械（如 SP960 类自动化系统）的准入、备案及海关清关新规。
        - 逻辑对齐：分析政策变动是否影响 2026 年 8 月的运营目标及 6 月的技术转移计划。
    - **实体监控**：真迈 (GeneMind)、GenePlanet、SOPHIA、Gene solutions等仅在发生格局性变量时汇报，严禁冗余。

    ### 🛡️ 综合决策建议 (Strategic So-What)
    - 结合第一层全球流动性波动与第二层拉美落地环境，给出批判性行动建议。

    【风格约束】：
    - 语气：严谨、职业、克制（参考 Claude 风格）。
    - 逻辑：每一结论必须有因果链支撑。
    - 格式：优先使用数据、百分比与逻辑连接词，禁止华丽修辞。
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
# 修改 save_for_obsidian 函数
def save_for_obsidian(market_data, summary):
    # 🎯 傻瓜式对齐：直接硬编码为您侧边栏的绝对嵌套路径
    folder = "00_Briefings/Notes" 
    if not os.path.exists(folder): os.makedirs(folder)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    content = f"""---
tags: #Briefing #LatAm #Investment #GENTODOS #Policy_Audit
date: {date_str}
source_verified: true
---
# 📅 首席顾问简报 {date_str}

{summary}
---
**核查基准数据**:
{market_data}
"""
    with open(f"{folder}/{date_str}.md", "w", encoding="utf-8") as f: 
        f.write(content)

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
