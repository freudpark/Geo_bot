from http.server import BaseHTTPRequestHandler
import json
import os
import requests
import sys
from datetime import datetime
import re

# 프로젝트 루트 임포트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """텔레그램 웹훅(Webhook)으로부터 명령을 수신합니다."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_ok()
                return

            post_data = self.rfile.read(content_length).decode('utf-8')
            update = json.loads(post_data)
            
            token = os.getenv("TELEGRAM_BOT_TOKEN") or "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E"
            message = update.get("message", {})
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")

            # 1. 함장님 전용 보안 필터
            allowed_chat_id = str(os.getenv("TELEGRAM_CHAT_ID") or "-1002916386908")
            if str(chat_id) != allowed_chat_id and allowed_chat_id != "None":
                self._send_ok()
                return

            if not text:
                self._send_ok()
                return

            # 2. 명령어 처리
            if text.startswith("/"):
                if text == "/보고":
                    self.send_telegram_msg(token, chat_id, "🚀 함장님, 통합 리포트(카톡+텔그) 생성을 즉시 시작합니다...")
                    try:
                        # run_daily_alert.run()을 직접 호출하여 카톡과 텔레그램 동시 사격
                        from run_daily_alert import run
                        run()
                        # run() 내부에서 이미 텔레그램과 카톡 전송이 끝났을 것이지만, 명시적 완료 보고
                        self.send_telegram_msg(token, chat_id, "✅ 통합 리포트 사격 완료. 카톡을 확인해 주십시오!")
                    except Exception as e:
                        self.send_telegram_msg(token, chat_id, f"❌ 통합 보고 중 통신 장애: {str(e)}")
                
                elif text.startswith("/수정"):
                    # 날짜 검색 패턴 매칭 (예: /수정 3월 11일 일정을 보여줘)
                    date_match = re.search(r'(\d+)월\s*(\d+)일', text)
                    if date_match:
                        month, day = date_match.groups()
                        target_date = f"2026-{month.zfill(2)}-{day.zfill(2)}"
                        self.send_telegram_msg(token, chat_id, f"🔍 함장님, {month}월 {day}일({target_date})의 과거 기록을 조회합니다...")
                        self.handle_date_search(token, chat_id, target_date)
                    else:
                        request_text = text.replace("/수정", "").strip()
                        self.send_telegram_msg(token, chat_id, f"🛠️ '{request_text}' 명령 수신. 안티그래비티 기지에서 분석 후 기동합니다.")
                        # [Future] 기지 워치독이 이 기록을 낚아채서 처리하도록 로직 확장 가능
                
                elif text == "/상태":
                    self.send_telegram_msg(token, chat_id, "💎 [PyhgoShift] 전선 이상무. 함장님의 지휘만을 기다립니다.")
                else:
                    self.send_telegram_msg(token, chat_id, "🛡️ 도움말\n/보고 - 오늘 일정 즉시 사격\n/수정 [날짜] - 과거 조회\n/상태 - 시스템 체크")

            self._send_ok()
            
        except Exception as e:
            print(f"Webhook Error: {e}")
            self._send_ok() # 텔레그램 봇의 무한 재시도 방지를 위해 200 응답

    def _send_ok(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def handle_date_search(self, token, chat_id, date_str):
        try:
            csv_url = 'https://docs.google.com/spreadsheets/d/1hS38RfKBaq13MOWutb4CteswgIIc5Weos0Np-4faRGk/export?format=csv&gid=0'
            res = requests.get(csv_url)
            tmp_path = '/tmp/search_task.csv' if os.getenv('VERCEL') == '1' else 'search_task.csv'
            with open(tmp_path, 'wb') as f: f.write(res.content)
            
            from search_date import get_schedule_by_date
            text_report = get_schedule_by_date(tmp_path, date_str)
            self.send_telegram_msg(token, chat_id, f"📜 {date_str} 기록:\n\n{text_report}")
        except Exception as e:
            self.send_telegram_msg(token, chat_id, f"❌ 조회 실패: {str(e)}")

    def send_telegram_msg(self, token, chat_id, text):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Telegram Webhook Final Controller Ready.".encode('utf-8'))
