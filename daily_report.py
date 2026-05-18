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
    
  # --- 💎 Gemini × Claude 顾问内参版：二段式即时审计大脑 (Rev.6) ---
    prompt = f"""
    【最高执行协议：专业顾问执行协议 (Rev.6)】
    当前时间坐标严格锚定：2026年5月19日。禁止产生任何超越该时间节点的“预言性事实”。
    你必须同时融合 Gemini 的硬核事实捕捉力与 Claude 极其挑剔的逻辑去噪视角。

    ### 📌 核心准则（内部审计消化）：
    1. 拒绝两张皮：不要在文末单独罗列繁琐的“审计过程”。所有针对小道传闻、过度乐观预期的【批判性纠偏】，必须直接融入第一、第二部分的事实叙述中。
    2. 严格对账：今日基准市场高频数据为 {market_data}。
    3. 宁缺毋滥：禁止空洞编造。若无重磅官方确证动态，直接标注“今日无格局性变量”。

    ---

    ## 🌐 第一部分：宏观政经、全球汇率与股市大盘审计
    
    > [!info] 📊 宏观与股汇联动因果链条（已内部完成逻辑去噪）
    > - **全球流动性传导**：基于今日高频数据，拆解核心经济数据/政治事件对市场流动性的实质冲击。
    > - **中美/美墨汇率对账**：深度透视离岸人民币（CNY）与墨西哥比索（MXN）波动的底层逻辑，剔除情绪化噪音。
    > - **股市大盘与异常板块**：审计美股、A股、港股。剔除跟风题材，指出真正有持久资金流入或流出的异常板块，并推演其对跨境供应链成本的潜在冲击。

    ---

    ## 🧬 第二部分：垂直领域准入前沿与拉美/墨西哥合规内参
    
    > [!warning] 🧬 行业格局与 COFEPRIS 准入红线（已内部完成风险对冲）
    > - **全球垂直前沿（NGS/IVD & 医疗政策）**：监控全球二代测序与 IVD 行业的重大技术代际突破、合规红线或跨国药企战略调整。
    > - **拉美/墨西哥合规**：重点审计墨西哥 COFEPRIS、海关等官方机构针对进口医疗器械、实验室耗材的准入、备案、清关新规。
    > - **运营风险对齐（So-What）**：直接指出上述政策变动对 2026 年 6 月技术转移计划及 8 月运营目标的实质性因果冲击，并给出逻辑推演路径。

    ---

    ## 🎯 第三部分：战略决策建议
    
    > [!todo] 🎯 跨界行动路径演导
    > 1. **路径①（即时对冲）**：针对短期流动性波动或突发合规红线的即时防守/避险手段。
    > 2. **路径②（确定性推进）**：针对 6 月技术转移与 8 月实验室落地目标的常态化推进策略。
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
    # 🎯 核心修正：在仓库视角下，直接就是 Notes 文件夹
    folder = "Notes"  
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
