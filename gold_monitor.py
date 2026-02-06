import requests
import os

def get_london_gold():
    """获取伦敦金 (美元/盎司) - 使用公共金融接口"""
    print("--- 尝试获取伦敦金 ---")
    # 这是一个专门为开发者提供的免费镜像接口，不限IP
    url = "https://api.gold-api.com/price/XAU"
    try:
        res = requests.get(url, timeout=15)
        print(f"伦敦金状态码: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            # 接口直接返回价格字段
            return data.get('price')
    except Exception as e:
        print(f"伦敦金解析异常: {e}")
        return None

def get_shanghai_gold():
    """获取上海金 Au9999 (人民币/克) - 使用东方财富接口"""
    print("\n--- 尝试获取上海金 ---")
    # 东方财富的这个接口目前不屏蔽海外IP，且返回标准JSON
    # secid 10.Au9999 是上金所现货代码，f43 是最新价
    url = "https://push2.eastmoney.com/api/qt/stock/get?secid=10.Au9999&fields=f43"
    try:
        res = requests.get(url, timeout=15)
        print(f"上海金状态码: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            # 价格字段 f43 的单位是“分”，需要除以 100
            price_raw = data['data']['f43']
            if price_raw != '-':
                return float(price_raw) / 100
        return None
    except Exception as e:
        print(f"上海金解析异常: {e}")
        return None

def send_to_slack(lp, sp):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url: return

    # 构建精美的 Slack 卡片
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚀 黄金实时双向行情"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*伦敦金 (现货)*\n`${lp or '获取失败'}`"},
                    {"type": "mrkdwn", "text": f"*上海金 (Au9999)*\n`￥{sp or '获取失败'}`"}
                ]
            },
            {
                "type": "divider"
            }
        ]
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    l_price = get_london_gold()
    s_price = get_shanghai_gold()
    
    print(f"\n最终抓取结果 -> 伦敦: {l_price}, 上海: {s_price}")
    
    if l_price or s_price:
        send_to_slack(l_price, s_price)
        print("✅ 推送已完成")
    else:
        print("❌ 两个接口均无法获取数据")
