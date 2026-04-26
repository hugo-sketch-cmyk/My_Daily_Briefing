import os
import requests
import yfinance as yf
from datetime import datetime

def send_feishu_card(summary_text, market_data):
    # 【自检环节】
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    
    if not webhook_url or "https" not in webhook_url:
        print("❌ 错误：找不到飞书地址！请检查 GitHub Secrets 是否配置了 FEISHU_WEBHOOK_URL")
        return

    card_payload = {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": "📅 专业顾问简报"}, "template": "blue"},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": f"**指标数据**\n{market_data}"}},
                {"tag": "hr"},
                {"tag": "div", "text": {"tag": "lark_md", "content": summary_text}}
            ]
        }
    }
    r = requests.post(webhook_url, json=card_payload)
    print(f"发送状态: {r.status_code}, 响应: {r.text}")

# 获取数据的逻辑（保持不变）
def get_market_data():
    try:
        # 简单抓取汇率做测试
        data = yf.Ticker("USDCNY=X").history(period="1d")
        price = data['Close'].iloc[-1]
        return f"美元/人民币汇率: {price:.4f}"
    except:
        return "数据抓取暂不可用"

if __name__ == "__main__":
    # 执行
    m_data = get_market_data()
    # 模拟总结，先测试通道是否畅通
    summary = "这是一条自动化测试简报。如果您看到这条信息，说明飞书连接成功！"
    send_feishu_card(summary, m_data)
