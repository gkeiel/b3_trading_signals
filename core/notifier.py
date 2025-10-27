import os, requests
from dotenv import load_dotenv


# =====================================================
#  Notifier
# =====================================================
class Notifier:
    def __init__(self):
        load_dotenv()
        self.TOKEN    = os.getenv("TOKEN")      # bot TOKEN
        self.CHAT_ID  = os.getenv("CHAT_ID")    # channel ID

    def send_telegram(self, payload):
        url = f"https://api.telegram.org/bot{self.TOKEN}/sendMessage"
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        msg_id = r.json()["result"]["message_id"]
        print("Telegram sent.")
        return msg_id
    
    def pin_telegram(self, payload):
        url = f"https://api.telegram.org/bot{self.TOKEN}/pinChatMessage"
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("Telegram pinned.")