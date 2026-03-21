import requests
import os
import json

def send_telegram_message(text):
    """
    텔레그램 봇을 통해 단체방에 메시지를 전송합니다.
    기존 카카오톡 로직과는 완전히 독립적으로 작동합니다.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN", "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E")
    # 고정된 채팅방 ID: 사업일정작업 알림
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "-1002916386908") 
    
    if not token:
        print("[Telegram] Token is missing.")
        return None

    # 만약 chat_id가 없으면 마지막 인입된 메시지에서 chat_id를 자동 추출 시도 (임시)
    if not chat_id:
        print("[Telegram] Chat ID is missing. Attempting to find chat_id from updates...")
        try:
            update_url = f"https://api.telegram.org/bot{token}/getUpdates"
            res = requests.get(update_url).json()
            if res.get("ok") and res.get("result"):
                # 가장 최근 메시지가 온 방의 ID를 가져옴
                for update in reversed(res["result"]):
                    if "message" in update:
                        chat_id = update["message"]["chat"]["id"]
                        print(f"[Telegram] Found chat_id: {chat_id}")
                        break
        except Exception as e:
            print(f"[Telegram] Failed to auto-detect chat_id: {e}")

    if not chat_id:
        print("[Telegram] No chat_id found. Please send a message to the bot in the group chat first.")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"[Telegram] Send failed: {e}")
        return None

if __name__ == "__main__":
    # 테스트용
    test_msg = "🚀 파이고시프트 텔레그램 알림 시스템 가동 테스트"
    print(send_telegram_message(test_msg))
