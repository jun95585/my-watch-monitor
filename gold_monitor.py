import requests
import os

def get_data():
    """获取伦敦金价格和美元兑人民币汇率"""
    gold_usd = None
    usd_cny = 7.23  # 预设一个保底汇率，防止接口失效
    
    # 1. 获取伦敦金 (美元/盎司)
    try:
        res_g = requests.get("https://api.gold-api.com/price/XAU", timeout=15)
        if res_g.status_code == 200:
            gold_usd = res_g.json().get('price')
    except Exception as e:
        print(f"金价获取失败: {e}")

    # 2. 获取实时汇率 (USD/CNY)
    try:
        # 使用专为开发者提供的汇率接口
        res_e = requests.get("https://open.er-api.com/v6/latest/USD", timeout=15)
        if res_e.status_code == 200:
            usd_cny = res_e.json().get('rates', {}).get('CNY', 7.23)
            print(f"当前实时汇率: {usd_cny}")
    except Exception as e:
        print(f"汇率获取失败，使用保底值: {e}")
        
    return gold_usd, usd_cny

def send_to_slack(gold_usd, rate):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url: return

    # 计算人民币金价 (1盎司 = 31.1034768克)
    # 公式：美元金价 * 汇率 / 31.1035
    gold_cny = (gold_usd * rate) / 31.1034768
    
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🔔 国际金价换算提醒"}
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn", 
                        "text": f"*伦敦金 (国际盘)*\n`${gold_usd:,.2f}` USD/oz"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"*折算人民币 (参考)*\n`¥{gold_cny:,.2f}` 元/克"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn", 
                        "text": f"今日参考汇率: {rate} | 计算公式: (USD * 汇率) / 31.1035"
                    }
                ]
            }
        ]
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    usd_price, cny_rate = get_data()
    
    if usd_price:
        send_to_slack(usd_price, cny_rate)
        print(f"✅ 执行成功: ${usd_price} -> ¥{round((usd_price * cny_rate)/31.1035, 2)}")
    else:
        print("❌ 未能获取核心金价数据")
