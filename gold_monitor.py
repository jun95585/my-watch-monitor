import requests
import os

def get_gold_prices():
    london_price = None
    shanghai_price = None
    
    # --- 尝试获取伦敦金 (使用公共开放 API) ---
    print("--- 正在通过公共 API 获取伦敦金 ---")
    # 使用一个无需 Key 的快速镜像接口
    try:
        url_l = "https://api.gold-api.com/price/XAU"
        res_l = requests.get(url_l, timeout=15)
        if res_l.status_code == 200:
            london_price = res_l.json().get('price')
            print(f"伦敦金获取成功: {london_price}")
    except Exception as e:
        print(f"伦敦金获取失败: {e}")

    # --- 尝试获取上海金 (使用东方财富海外 API 节点) ---
    print("\n--- 正在通过东方财富获取上海金 ---")
    try:
        # 东方财富 Au9999 的代码是 10.Au9999
        url_s = "https://push2.eastmoney.com/api/qt/stock/get?secid=10.Au9999&fields=f43"
        res_s = requests.get(url_s, timeout=15)
        if res_s.status_code == 200:
            # 这里的 f43 对应的是最新价，数值需要除以 100
            raw_price = res_s.json()['data']['f43']
            shanghai_price = raw_price / 100
            print(f"上海金获取成功: {shanghai_price}")
    except Exception as e:
        print(f"上海金获取失败: {e}")
        
    return london_price, shanghai_price

def send_to_slack(lp, sp):
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not webhook_url: return

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "💰 黄金双线行情"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*伦敦金 (USD/oz)*\n`{lp or '获取失败'}`"},
                    {"type": "mrkdwn", "text": f"*上海金 (元/克)*\n`{sp or '获取失败'}`"}
                ]
            }
        ]
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    l, s = get_gold_prices()
    if l or s:
        send_to_slack(l, s)
        print("\n✅ 推送任务完成")
    else:
        print("\n❌ 依然无法获取任何数据，请检查网络节点")
