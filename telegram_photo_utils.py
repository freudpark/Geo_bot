
import requests
import os

def send_telegram_photo(photo_path, caption=""):
    """
    고정된 채팅방(-1002916386908)으로 이미지를 전송합니다.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN", "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "-1002916386908")
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            params = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(url, files=files, params=params)
            
            if response.status_code == 200:
                print(f"[Telegram] Photo sent successfully.")
                return True
            else:
                print(f"[Telegram] Failed to send photo: {response.text}")
                return False
    except Exception as e:
        print(f"[Telegram] Error sending photo: {e}")
        return False

if __name__ == "__main__":
    # 샘플 이미지 전송 테스트
    sample_path = 'alert_card_sample.png'
    if os.path.exists(sample_path):
        send_telegram_photo(sample_path, "🚀 정보자원 Daily 알림 (디자인 컨셉 테스트)")
    else:
        print("Sample image not found. Please run test_render.py first.")
