import requests
import os
import datetime
import pytz
import yfinance as ticker
import feedparser # 新增：解析行业情报
import sys

def get_market_summary():
    """获取金融指标 (同上个版本，具备鲁棒性)"""
    symbols = {"Gold": "GC=F", "Oil": "CL=F", "USD/MXN": "MXN=X"}
    results = {}
    for name, sym in symbols.items():
        try:
            data = ticker.Ticker(sym).history(period="5d")
            if not data.empty:
                last_p, prev_p = data['Close'].iloc[-1], data['Close'].iloc[-2]
                change = ((last_p - prev_p) / prev_p) * 100
                results[name] = f"{last_p:.2f} ({'🔺' if change>0 else '🔻'}{change:.2f}%)"
            else: results[name] = "Market Closed"
        except: results[name] = "Error"
    return results

def get_real_ngs_news():
    """逻辑审计：抓取真实的 NGS & 医疗前沿动态"""
    # 订阅源列表：Nature 生物医学、BioRxiv 基因组学
    feeds = [
        "https://www.nature.com/subjects/biotechnology.rss",
        "https://biorxiv.org/collections/genetics.rss"
    ]
    news_items = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            # 每个源只取最新 2 条，避免简报过长
            for entry in feed.entries[:2]:
                news_items.append(f"• **{entry.title}**\n  [点击查看]({entry.link})")
        except:
            continue
    
    if not news_items:
        return "暂无实时学术更新，建议检查网络连接。"
    return "\n\n".join(news_items)

def send_to_feishu():
    webhook_url = os.environ.get("LARK_WEBHOOK")
    market = get_market_summary()
    ngs_news = get_real_ngs_news()
    cdmx_now = datetime.datetime.now(pytz.timezone('America/Mexico_City'))

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"🚀 决策情报汇总 | {cdmx_now.strftime('%Y-%m-%d')}"},
                "template": "orange" 
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**🏦 实时宏观指标**\n- 黄金：`{market.get('Gold')}`\n- 原油：`{market.get('Oil')}`\n- **美元/比索**：`{market.get('USD/MXN')}`"}
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**🧬 学术与行业前沿 (RSS 实时)**\n{ngs_news}"}
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": "**💡 顾问提示 (Consultant Advice):**\n1. 请检查上述论文标题，如有感兴趣的，请直接下载 PDF 丢入 **NotebookLM**。\n2. 比索汇率若持续波动，请更新您的 Obsidian [[汇率对冲]] 笔记。"}
                },
                {
                    "tag": "note",
                    "elements": [{"tag": "plain_text", "content": "数据源: Yahoo Finance & Nature RSS Feed"}]
                }
            ]
        }
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    send_to_feishu()
