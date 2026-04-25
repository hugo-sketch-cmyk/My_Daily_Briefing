import requests
import os
import datetime
import pytz

def get_financial_data():
    """
    逻辑审计：获取宏观政经数据
    此处使用示例数据，建议后续接入具体的 API (如 yfinance)
    """
    # 模拟抓取到的实时数据
    data = {
        "gold": "2,385.10 USD/oz",
        "oil_wti": "82.45 USD/bbl",
        "usd_mxn": "17.12",
        "nasdaq": "16,274.95"
    }
    return data

def get_ngs_briefing():
    """
    垂直领域：NGS/生物医疗简讯
    """
    return "1. Illumina 发布新型高通量测序平台架构；\n2. 墨西哥卫健委更新二代测序临床准入指南（草案）。"

def send_to_feishu():
    webhook_url = os.environ.get("LARK_WEBHOOK")
    if not webhook_url:
        print("错误：未找到 LARK_WEBHOOK 环境变量")
        return

    # 锚定墨西哥城时间
    cdmx_tz = pytz.timezone('America/Mexico_City')
    now = datetime.datetime.now(cdmx_tz)
    
    finance = get_financial_data()
    ngs = get_ngs_briefing()

    # 构造飞书卡片消息
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"📊 每日深度决策简报 | {now.strftime('%Y-%m-%d')}"},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**📍 宏观政经指标 (CDMX 08:00)**\n- 黄金现货: `{finance['gold']}`\n- WTI 原油: `{finance['oil_wti']}`\n- 美元/比索 (USD/MXN): `{finance['usd_mxn']}`\n- 纳斯达克指数: `{finance['nasdaq']}`"}
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**🧬 NGS & 医疗检测动态**\n{ngs}"}
                },
                {
                    "tag": "note",
                    "elements": [{"tag": "plain_text", "content": "数据来源：自动化监测系统 | 决策建议：保持观察"}]
                }
            ]
        }
    }

    response = requests.post(webhook_url, json=payload)
    print(f"发送状态: {response.status_code}, 响应: {response.text}")

if __name__ == "__main__":
    send_to_feishu()
