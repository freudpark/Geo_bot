import requests
import json
import os
import time

def check_telegram_updates(bot_token, offset=None):
    """최신 메시지를 확인합니다."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    params = {"timeout": 10, "offset": offset}
    try:
        res = requests.get(url, params=params, timeout=12)
        if res.status_code == 200:
            return res.json().get("result", [])
    except:
        pass
    return []

def handle_command(command, chat_id):
    """명령어를 처리하고 결과를 반환합니다."""
    # 함장님 전용 명령 체계
    if command == "/보고":
        return "🚀 함장님, 현재 지휘 보고서를 생성하여 전송합니다. (10초 소요)"
    elif command == "/상태" or command == "/status":
        from datetime import datetime
        return f"💎 함대 상태 보고\n서버 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n엔진 상황: 정상 작동 중 (PyhgoShift 2.0)"
    elif command == "/help" or command == "/도움말":
        return "🛡️ 함대 지휘소 명령어\n/보고 - 현재 지휘 보고서 즉시 발송\n/상태 - 엔진 및 서버 상태 확인\n/안내 - 시스템 사용 가이드"
    else:
        return f"⚠️ '{command}'는 인가되지 않은 명령입니다. /help 를 참고하십시오."

def run_remote_control():
    """텔레그램 원격 제어 루프 (로컬 테스트용)"""
    token = "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E"
    offset = None
    print("🛰️ 텔레그램 원격 지휘소 가동 중... (Ctrl+C로 종료)")
    
    while True:
        try:
            updates = check_telegram_updates(token, offset)
            for upd in updates:
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                
                if text.startswith("/"):
                    print(f"Command received: {text} from {chat_id}")
                    response = handle_command(text, chat_id)
                    
                    # 텍스트 응답
                    res_url = f"https://api.telegram.org/bot{token}/sendMessage"
                    requests.post(res_url, data={"chat_id": chat_id, "text": response})
                    
                    # 특수 명령: /보고 인 경우 실제 run_daily_alert 실행
                    if text == "/보고":
                        from run_daily_alert import run
                        run()
            
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_remote_control()
