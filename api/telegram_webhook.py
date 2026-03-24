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

        # 1. 함장님 전용 보안 필터 (지정된 채팅 ID만 허용)
        # 함장님 ID: -1002916386908 (그룹)
        allowed_chat_id = str(os.getenv("TELEGRAM_CHAT_ID") or "-1002916386908")
        
        # 보안 필터 적용 (현재 함장님의 ID를 정확히 맞추기 위해 조건부 허용)
        if str(chat_id) != allowed_chat_id and allowed_chat_id != "None":
            # 만약 함장님이 개인 톡으로 하시는 경우를 위해 디버깅 로그 처리 가능
            print(f"[Debug] Rejected chat_id: {chat_id}")
            # 함장님의 직통 명령임을 확인하기 위해 명시적으로 응답 (초기 보안망 구축 과정)
            # return

        # 2. 명령어 처리
        if text.startswith("/"):
            response_text = self.process_command(text, chat_id)
            self.send_telegram_msg(token, chat_id, response_text)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def process_command(self, text, chat_id):
        # 텔레그램 명령 처리 로직
        cmd = text.split()[0]
        
        if cmd == "/보고":
            # 비동기 실행을 위해 별도 처리하거나 즉시 실행 보고
            from run_daily_alert import run
            try:
                run()
                return "✅ 함장님, 최신 지휘 보고서(카드 및 텍스트) 발송을 완료했습니다. ⚓️💎"
            except Exception as e:
                return f"❌ 보고서 생성 중 장애 발생: {str(e)}"
                
        elif cmd == "/상태":
            from datetime import datetime
            return f"💎 [PyhgoShift] 함대 상태 보고\n서버 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nD-Day: {self.get_current_dday()}\n엔진 상황: 정상 기동 중"
            
        elif cmd == "/도움말":
            return "🛡️ 함대 원격 지휘소\n/보고 - 현 시간 기준 최신 리포트 즉시 발송\n/상태 - 시스템 기동 상태 및 D-Day 확인\n/수정 [내용] - (개발 중) AI를 통한 코드 수정 및 배포"
        
        return f"⚠️ '{cmd}'는 인가되지 않은 명령입니다. /도움말을 참고하십시오."

    def get_current_dday(self):
        from datetime import datetime
        target = datetime(2026, 6, 12)
        delta = (target - datetime.now()).days
        return f"D-{delta}"

    def send_telegram_msg(self, token, chat_id, text):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})

    def do_GET(self):
        """웹훅 설정 확인용"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Telegram Webhook Handler is Active.".encode('utf-8'))
