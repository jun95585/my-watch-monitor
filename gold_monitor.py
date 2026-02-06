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
        if data and data.get('data') and data['data'].get('f43') != '-':
            return float(data['data']['f43']) / 100
    except:
        print("东方财富接口失效，尝试备用接口...")

    # 方案 B: 腾讯财经 (备用)
    try:
        # 腾讯接口对海外 IP 较友好
        url_tencent = "https://qt.gtimg.cn/q=s_shau9999"
        res = requests.get(url_tencent, timeout=10)
        # 返回内容示例: v_s_shau9999="100~Au9999~620.50~...";
        if res.status_code == 200:
            content = res.text
            price = content.split('~')[2]
            return float(price)
    except Exception as e:
        print(f"上海金所有接口均失败: {e}")
    
    return None

def send_to_slack(lp, sp):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url: return

    # 处理价格显示
    l_display = f"${lp:,.2f}" if lp else "获取失败"
    s_display = f"¥{sp:,.2f}" if sp else "获取失败"

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "💰 黄金双线行情报告"}
            },
            {
                "type": "section",
                "fields":
