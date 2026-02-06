import requests
import os
import re

def get_london_gold():
    """获取伦敦金现货价格 (美元/盎司)"""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        return data['chart']['result'][0]['meta']['regularMarketPrice']
    except:
        return None

def get_shanghai_gold():
    """获取上海黄金交易所 Au9999 价格 (人民币/克)"""
    # 使用新浪财经接口
    url = "https://hq.sinajs.cn/list=s_au9999"
    headers = {'Referer': 'https://finance.sina.com.cn'} # 新浪要求有 Referer
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # 返回格式类似: var hq_str_s_au9999="Au9999,620.50,1.20,0.19%,0,0";
        data = res.text
        match = re.search(r'"([^"]+)"', data)
        if match:
            fields = match.group(1).split(',')
            return fields[1] # 第二个字段是当前价
        return None
    except:
        return None

def send_to_slack(london_price, shanghai_price):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        return

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 全球黄金实时行情",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*伦敦金 (现货):*\n`${london_price or '获取失败'}` USD/oz"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*上海金 (Au9999):*\n`￥{shanghai_price or '获取失败'}` CNY/g"
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "💡 *提示：* 1盎司 ≈ 31.1克。内外盘价差可反映汇率波动及溢价。"
                    }
                ]
            }
        ]
    }
    
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    l_price = get_london_gold()
    s_price = get_shanghai_gold()
    
    if l_price or s_price:
        send_to_slack(l_price, s_price)
        print(f"推送成功: 伦敦 {l_price}, 上海 {s_price}")
    else:
        print("所有数据抓取失败")
