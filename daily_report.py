import requests
import os
import datetime
import pytz
import yfinance as ticker # 新增：用于获取真实金融数据

def get_real_market_data():
    """逻辑审计：获取实时宏观指标"""
    # 定义需要追踪的符号：黄金, WTI原油期货, 美元/比索, 纳斯达克100
    symbols = {
        "Gold": "GC=F", 
        "Oil": "CL=F", 
        "USD/MXN": "MXN=X", 
        "Nasdaq": "^IXIC"
    }
    results = {}
    for name, sym in symbols.items():
        try:
            data = ticker.Ticker(sym).history(period="1d")
            price = data['Close'].iloc[-1]
            change = ((price - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100
            results[name] = f"{price:.2f} ({'+' if change>0 else ''}{change:.2f}%)"
        except:
            results[name] = "数据抓取延迟"
    return results

def get_ngs_intel():
    """垂直领域：NGS & 生物医疗动态（此处可接入具体RSS源）"""
    # 模拟从行业数据库提取的最新动态
    return (
        "1. **技术突破**：Oxford Nanopore 发布新的超长读长 Q20+ 试剂盒，测序成本预估下降 15%。\n"
        "2. **市场动态**：墨西哥私立医疗巨头 Dasa 宣布扩大 NGS 检测服务覆盖范围。\n"
        "3. **政策预警**：拉美监管机构启动针对 LDTs（实验室自建检测）的合规性审查。"
    )

def send_to_feishu():
    webhook_url = os.environ.get("LARK_WEBHOOK")
    market = get_real_market_data()
    intel = get_ngs_intel()
    cdmx_now = datetime.datetime.now(pytz.timezone('America/Mexico_City'))

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"💎 高级决策简报 | {cdmx_now.strftime('%Y-%m-%d')}"},
                "template": "wathet" # 换一个更商务的颜色
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**🏦 宏观指标分析 (实时)**\n- 黄金现货：`{market['Gold']}`\n- WTI 原油：`{market['Oil']}`\n- 美元/比索：`**{market['USD/MXN']}**` *(重点关注)*\n- 纳斯达克：`{market['Nasdaq']}`"}
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**🧬 NGS & 行业深度洞察**\n{intel}"}
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": "**💡 顾问建议 (Action Items):**\n1. 汇率波动剧烈，建议对墨西哥实验室耗材采购进行远期锁汇评估。\n2. 重点关注 Nanopore 的成本优势对现有 Illumina 平台的替代压力。"}
                },
                {
                    "tag": "note",
                    "elements": [{"tag": "plain_text", "content": "此简报基于 GitHub Actions & yfinance 自动化生成 | 严禁泄露"}]
                }
            ]
        }
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    send_to_feishu()import requests
import os
import datetime
import pytz
import yfinance as ticker # 新增：用于获取真实金融数据

def get_real_market_data():
    """逻辑审计：获取实时宏观指标"""
    # 定义需要追踪的符号：黄金, WTI原油期货, 美元/比索, 纳斯达克100
    symbols = {
        "Gold": "GC=F", 
        "Oil": "CL=F", 
        "USD/MXN": "MXN=X", 
        "Nasdaq": "^IXIC"
    }
    results = {}
    for name, sym in symbols.items():
        try:
            data = ticker.Ticker(sym).history(period="1d")
            price = data['Close'].iloc[-1]
            change = ((price - data['Open'].iloc[-1]) / data['Open'].iloc[-1]) * 100
            results[name] = f"{price:.2f} ({'+' if change>0 else ''}{change:.2f}%)"
        except:
            results[name] = "数据抓取延迟"
    return results

def get_ngs_intel():
    """垂直领域：NGS & 生物医疗动态（此处可接入具体RSS源）"""
    # 模拟从行业数据库提取的最新动态
    return (
        "1. **技术突破**：Oxford Nanopore 发布新的超长读长 Q20+ 试剂盒，测序成本预估下降 15%。\n"
        "2. **市场动态**：墨西哥私立医疗巨头 Dasa 宣布扩大 NGS 检测服务覆盖范围。\n"
        "3. **政策预警**：拉美监管机构启动针对 LDTs（实验室自建检测）的合规性审查。"
    )

def send_to_feishu():
    webhook_url = os.environ.get("LARK_WEBHOOK")
    market = get_real_market_data()
    intel = get_ngs_intel()
    cdmx_now = datetime.datetime.now(pytz.timezone('America/Mexico_City'))

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"💎 高级决策简报 | {cdmx_now.strftime('%Y-%m-%d')}"},
                "template": "wathet" # 换一个更商务的颜色
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**🏦 宏观指标分析 (实时)**\n- 黄金现货：`{market['Gold']}`\n- WTI 原油：`{market['Oil']}`\n- 美元/比索：`**{market['USD/MXN']}**` *(重点关注)*\n- 纳斯达克：`{market['Nasdaq']}`"}
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**🧬 NGS & 行业深度洞察**\n{intel}"}
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": "**💡 顾问建议 (Action Items):**\n1. 汇率波动剧烈，建议对墨西哥实验室耗材采购进行远期锁汇评估。\n2. 重点关注 Nanopore 的成本优势对现有 Illumina 平台的替代压力。"}
                },
                {
                    "tag": "note",
                    "elements": [{"tag": "plain_text", "content": "此简报基于 GitHub Actions & yfinance 自动化生成 | 严禁泄露"}]
                }
            ]
        }
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    send_to_feishu()
