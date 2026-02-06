import os
import time
import requests
import threading
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse

# 从环境变量读取 Token (稍后在 Zeabur 后台设置)
BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
# 预警消息发送到的频道 ID
CHANNEL_ID = os.environ.get("CHANNEL_ID") 

client = WebClient(token=BOT_TOKEN)

high_target = None
low_target = None

def get_realtime_gold():
    try:
        res_g = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        res_e = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10).json()
        usd = res_g.get('price')
        rate = res_e.get('rates', {}).get('CNY', 7.25)
        cny = round((usd * rate) / 31.1035, 2)
        return cny, usd
    except:
        return None, None

def handle_message(client: SocketModeClient, req):
    global high_target, low_target
    if req.type == "events_api":
        event = req.payload["event"]
        if event.get("bot_id"): return
        text = event.get("text", "").strip()
        channel = event["channel"]

        if text == "查" or text.lower() == "now":
            cny, usd = get_realtime_gold()
            client.web_client.chat_postMessage(channel=channel, text=f"📊 *实时报价*\n人民币：`¥{cny}/克`\n国际盘：`${usd}/oz`")
        elif text.startswith("高"):
            try:
                high_target = float(text[1:].strip())
                client.web_client.chat_postMessage(channel=channel, text=f"🚀 已设*高价预警*：>{high_target}")
            except: pass
        elif text.startswith("低"):
            try:
                low_target = float(text[1:].strip())
                client.web_client.chat_postMessage(channel=channel, text=f"📉 已设*低价预警*：<{low_target}")
            except: pass
        elif text == "清除":
            high_target, low_target = None, None
            client.web_client.chat_postMessage(channel=channel, text="🧹 预警已清除")
    return SocketModeResponse(envelope_id=req.envelope_id)

def auto_monitor():
    global high_target, low_target
    while True:
        if high_target or low_target:
            cny, _ = get_realtime_gold()
            if cny:
                if high_target and cny >= high_target:
                    client.chat_postMessage(channel=CHANNEL_ID, text=f"🚨 *高价触达！*\n当前 `¥{cny}` 已突破目标 `¥{high_target}`！")
                    high_target = None
                if low_target and cny <= low_target:
                    client.chat_postMessage(channel=CHANNEL_ID, text=f"✅ *低价触达 (抄底)！*\n当前 `¥{cny}` 已跌破目标 `¥{low_target}`！")
                    low_target = None
        time.sleep(180) # 3分钟

if __name__ == "__main__":
    threading.Thread(target=auto_monitor, daemon=True).start()
    socket_client = SocketModeClient(app_token=APP_TOKEN, web_client=client)
    socket_client.socket_mode_request_listeners.append(handle_message)
    socket_client.connect()
    from threading import Event
    Event().wait()
