import requests
import os
import re

def get_london_gold():
    print("--- 尝试获取伦敦金 ---")
    url = "https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"Yahoo 状态码: {res.status_code}")
        if res.status_code != 200:
            print(f"Yahoo 错误返回预览: {res.text[:200]}") # 打印前200个字符
        
        data = res.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        return price
    except Exception as e:
        print(f"伦敦金解析异常: {e}")
        return None

def get_shanghai_gold():
    print("\n--- 尝试获取上海金 ---")
    # 换一个更宽松的新浪接口
    url = "http://hq.sinajs.cn/list=s_au9999"
    headers = {
        'Referer': 'http://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"新浪状态码: {res.status_code}")
        # 新浪返回的是 GBK 编码，需特殊处理
        res.encoding = 'gbk'
        content = res.text
        print(f"新浪返回原始内容: {content}")
        
        match = re.search(r'"([^"]+)"', content)
        if match:
            fields = match.group(1).split(',')
            if len(fields) > 1:
                return fields[1]
        return None
    except Exception as e:
        print(f"上海金解析异常: {e}")
        return None

if __name__ == "__main__":
    l_price = get_london_gold()
    s_price = get_shanghai_gold()
    
    print("\n--- 最终结果 ---")
    print(f"伦敦金: {l_price}")
    print(f"上海金: {s_price}")
    
    # 只有成功获取到至少一个价格时才尝试推送
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if (l_price or s_price) and webhook_url:
        payload = {"text": f"📢 监控测试\n伦敦金: {l_price}\n上海金: {s_price}"}
        requests.post(webhook_url, json=payload)
