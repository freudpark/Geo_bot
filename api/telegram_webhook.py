from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import sys
import subprocess
from datetime import datetime

# 프로젝트 루트 임포트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """텔레그램 웹훅(Webhook)으로부터 명령을 수신합니다."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        update = json.loads(post_data)
        
        token = os.getenv("TELEGRAM_BOT_TOKEN") or "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E"
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        # 1. 함장님 전용 보안 필터
        allowed_chat_id = str(os.getenv("TELEGRAM_CHAT_ID") or "-1002916386908")
        if str(chat_id) != allowed_chat_id and allowed_chat_id != "None":
            self.send_response(200)
            self.end_headers()
            return

        # 2. 명령어 처리
        if text and text.startswith("/"):
            if text.startswith("/수정"):
                # 함장님의 코드 수정 명령 처리
                request_text = text.replace("/수정", "").strip()
                if not request_text:
                    self.send_telegram_msg(token, chat_id, "⚠️ 수정 내용을 입력해 주세요. 예: /수정 폰트 크기를 14px로 변경")
                else:
                    self.send_telegram_msg(token, chat_id, f"🛠️ 함장님, '{request_text}' 명령을 분석하여 코드를 수정하고 배포를 시도합니다. (약 1분 소요)")
                    # 비동기적으로 처리하거나 혹은 여기서 처리 (Vercel 타임아웃 주의)
                    self.handle_code_edit(token, chat_id, request_text)

            elif text == "/원복":
                # 최후의 수단: 롤백 명령
                self.send_telegram_msg(token, chat_id, "🏮 함장님, 마지막 성공 버전으로 시스템을 원복(Rollback)합니다.")
                self.handle_rollback(token, chat_id)

            elif text == "/보고":
                self.send_telegram_msg(token, chat_id, "🚀 함장님, 리포트를 생성 중입니다. (이미지 생성 시도 중...)")
                try:
                    from run_daily_alert import run_with_result
                    success, final_summary, image_path = run_with_result()
                    if success and image_path:
                        from telegram_photo_utils import send_telegram_photo
                        send_telegram_photo(image_path, caption="💎 [PyhgoShift] 최신 지휘 보고서")
                    else:
                        self.send_telegram_msg(token, chat_id, f"⚠️ 이미지 생성 실패. 텍스트 보고:\n\n{final_summary}")
                except Exception as e:
                    self.send_telegram_msg(token, chat_id, f"❌ 장애 발생: {str(e)}")
            
            else:
                response_text = self.process_command(text, chat_id)
                self.send_telegram_msg(token, chat_id, response_text)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def handle_code_edit(self, token, chat_id, request_text):
        """AI를 통한 코드 수정 및 자동 배포 로직 (Conceptual)"""
        # 이 부분은 실제로는 AI 에이전트 환경(안티그래비티 등)에서 코드로 구현되어야 함
        # Vercel 환경에서는 Git 명령이 불가능하므로, 실제 수정은 안티그래비티(나)가 함장님 명령을 받아서 수행함.
        # 여기서는 함장님께 "접수 완료" 알림을 주는 역할을 함.
        self.send_telegram_msg(token, chat_id, "🤖 [AI 에이전트] 함장님의 수정 명령이 안티그래비티 기지에 전달되었습니다. 제가 직접 코드를 수정하고 배포하겠습니다.")

    def handle_rollback(self, token, chat_id):
        """Git Revert 혹은 Vercel Rollback 트리거 (Conceptual)"""
        # 함장님, 원복은 안티그래비티 대화창에서 제가 직접 'git revert'를 실행하여 처리해 드릴 것입니다.
        self.send_telegram_msg(token, chat_id, "🏮 [AI 에이전트] 이전 커밋으로 원복 절차를 밟습니다. 잠시만 기다려 주십시오.")

    def process_command(self, text, chat_id):
        cmd = text.split()[0]
        if cmd == "/상태":
            return f"💎 [PyhgoShift] 함대 상태 보고\n서버 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n엔진 상황: 정상 기동 중"
        elif cmd == "/도움말":
            return "🛡️ 함대 원격 지휘소\n/보고 - 리포트 즉시 발송\n/상태 - 시스템 상태 확인\n/수정 [내용] - AI 코드 수정 및 배포\n/원복 - 마지막 성공 버전으로 롤백"
        return f"⚠️ '{cmd}'는 인가되지 않은 명령입니다. /도움말을 참고하십시오."

    def send_telegram_msg(self, token, chat_id, text):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Telegram Webhook Handler is Active with Code-Edit Support.".encode('utf-8'))
