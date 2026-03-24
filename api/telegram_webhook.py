from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import sys

# 프로젝트 루트 임포트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """텔레그램 웹훅(Webhook)으로부터 명령을 수신합니다."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        update = json.loads(post_data)
        
        # 환경 변수 및 하드코딩 폴백 (Vercel 설정 미비 대비)
        token = os.getenv("TELEGRAM_BOT_TOKEN") or "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E"
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        # 1. 함장님 전용 보안 필터
        allowed_chat_id = str(os.getenv("TELEGRAM_CHAT_ID") or "-1002916386908")
        
        if str(chat_id) != allowed_chat_id and allowed_chat_id != "None":
            # 개인 톡이나 다른 방은 무시 (보안)
            self.send_response(200)
            self.end_headers()
            return

        # 2. 명령어 처리
        if text and text.startswith("/"):
            if text == "/보고":
                # 함장님께 대기 명령 즉시 전송
                self.send_telegram_msg(token, chat_id, "🚀 함장님, 리포트를 생성 중입니다. (이미지 생성 시도 중...)")
                
                # 리포트 생성 프로세스 기동
                try:
                    from run_daily_alert import run_with_result
                    success, final_summary, image_path = run_with_result()
                    
                    if success and image_path and os.path.exists(image_path):
                        from telegram_photo_utils import send_telegram_photo
                        send_telegram_photo(image_path, caption=f"💎 [PyhgoShift] 최신 지휘 보고서")
                    else:
                        # 이미지 실패 시 즉시 텍스트로 전환하여 보고
                        error_msg = f"⚠️ [시스템 알림] 이미지 엔진 기동 불가(Vercel 리소스 제한).\n텍스트 리포트로 대체 보고합니다.\n\n{final_summary}"
                        self.send_telegram_msg(token, chat_id, error_msg)
                except Exception as e:
                    self.send_telegram_msg(token, chat_id, f"❌ 보고서 생성 중 장애 발생: {str(e)}")
            else:
                response_text = self.process_command(text, chat_id)
                self.send_telegram_msg(token, chat_id, response_text)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def process_command(self, text, chat_id):
        cmd = text.split()[0]
        if cmd == "/상태":
            from datetime import datetime
            target = datetime(2026, 6, 12)
            delta = (target - datetime.now()).days
            return f"💎 [PyhgoShift] 함대 상태 보고\n서버 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nD-Day: D-{delta}\n엔진 상황: 정상 기동 중"
        elif cmd == "/도움말":
            return "🛡️ 함대 원격 지휘소\n/보고 - 최신 리포트 즉시 발송\n/상태 - 시스템 상태 확인\n/수정 [내용] - AI 코드 수정 (준비 중)"
        return f"⚠️ '{cmd}'는 인가되지 않은 명령입니다. /도움말을 참고하십시오."

    def send_telegram_msg(self, token, chat_id, text):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Telegram Webhook Handler is Active.".encode('utf-8'))
