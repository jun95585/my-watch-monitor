import requests
import os

def get_gold_price():
    # 获取现货黄金价格 (Yahoo Finance)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        return price
    except Exception as e:
        print(f"获取金价失败: {e}")
        return None

def send_to_slack(price):
    # 从 GitHub Secrets 中读取你的 Slack 链接
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("未配置 SLACK_WEBHOOK_URL")
        return

    # 构造 Slack 消息格式
    payload = {
        "text": f"🏆 *实时金价提醒*\n> 当前国际现货黄金价格：*${price}* USD/oz\n> 状态：监测中"
    }
    
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    current_price = get_gold_price()
    if current_price:
        send_to_slack(current_price)
