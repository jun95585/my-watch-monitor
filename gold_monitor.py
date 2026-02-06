import requests
import os

def get_london_gold():
    """获取伦敦金 (美元/盎司)"""
    url = "https://api.gold-api.com/price/XAU"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            return res.json().get('price')
    except Exception as e:
        print(f"伦敦金解析异常: {e}")
    return None

def get_shanghai_gold():
    """获取上海金 Au9999 (人民币/克) - 双接口容错"""
    # 方案 A: 东方财富
    try:
        url_east = "https://push2.eastmoney.com/api/qt/stock/get?secid=10.Au9999&fields=f43"
        res = requests.get(url_east, timeout=10)
        data = res.json()
        if data and data.get('data') and data['data'].get('f43') and data['data']['f43'] != '-':
            return float(data['data']['f43']) / 100
    except Exception as e:
        print(f"东方财富接口尝试失败: {e}")

    # 方案 B: 腾讯财经 (备用)
    try:
        url_tencent = "https://qt.gtimg.cn/q=s_shau9999"
        res = requests.get(url_tencent, timeout=10)
        if res.status_code == 200:
            content = res.text
            # 腾讯返回格式: v_s_shau9999="100~Au9999~620.50~...";
            parts = content.split('~')
            if len(parts) > 2:
                return float(parts[2])
    except Exception as e:
        print(f"上海金所有接口均失败: {e}")
    
    return None

def send_to_slack(lp, sp):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url:
        print("未找到 Webhook URL")
        return

    # 格式化价格显示
    l_str = f"${lp:,.2f}" if lp else "获取失败"
    s_str = f"¥{sp:,.2f}" if sp else "获取失败"

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "💰 黄金双线行情报告"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*伦敦金 (现货)*\n`{l_str}`"},
                    {"type": "mrkdwn", "text": f"*上海金 (Au9999)*\n`{s_str}`"}
                ]
            }
        ]
    }
    
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"发送 Slack 失败: {e}")

if __name__ == "__main__":
    l_price = get_london_gold()
    s_price = get_shanghai_gold()
    
    print(f"运行结果 -> 伦敦: {l_price}, 上海: {s_price}")
    
    if l_price or s_price:
        send_to_slack(l_price, s_price)
        print("✅ 任务执行成功")
    else:
        print("❌ 未获取到任何有效数据")
