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
            # [추가] 날짜 검색 패턴 매칭 (예: 3월 11일 일정을 보여줘)
            date_match = re.search(r'(\d+)월\s*(\d+)일', text)
            
            if text.startswith("/수정"):
                # 수정 명령 내부에 날짜 검색이 포함된 경우
                if date_match:
                    month, day = date_match.groups()
                    target_date = f"2026-{month.zfill(2)}-{day.zfill(2)}"
                    self.send_telegram_msg(token, chat_id, f"🔍 함장님, {month}월 {day}일({target_date})의 과거 기동 기록을 조회합니다...")
                    self.handle_date_search(token, chat_id, target_date)
                else:
                    request_text = text.replace("/수정", "").strip()
                    self.send_telegram_msg(token, chat_id, f"🛠️ '{request_text}' 명령을 안티그래비티 기지에 전달했습니다. (AI 분석 중)")

            elif text == "/보고":
                self.send_telegram_msg(token, chat_id, "🚀 함장님, 오늘의 리포트 생성을 시도합니다...")
                from run_daily_alert import run_with_result
                success, summary, img = run_with_result()
                if success and img:
                    from telegram_photo_utils import send_telegram_photo
                    send_telegram_photo(img, caption="💎 오늘의 지휘 카드")
                else:
                    self.send_telegram_msg(token, chat_id, f"⚠️ 이미지 생성 불가. 텍스트 보고:\n\n{summary}")
            
            else:
                response_text = self.process_command(text, chat_id)
                self.send_telegram_msg(token, chat_id, response_text)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def handle_date_search(self, token, chat_id, date_str):
        """특정 날짜의 일정을 검색하여 텍스트로 즉각 보고합니다."""
        try:
            # 외부 검색 엔진(search_date.py)의 로직을 활용
            csv_url = 'https://docs.google.com/spreadsheets/d/1hS38RfKBaq13MOWutb4CteswgIIc5Weos0Np-4faRGk/export?format=csv&gid=0'
            res = requests.get(csv_url)
            tmp_path = '/tmp/search_task.csv' if os.getenv('VERCEL') == '1' else 'search_task.csv'
            with open(tmp_path, 'wb') as f: f.write(res.content)
            
            # 검색 및 요약 생성 (기존 search_date.py 로직 내재화 혹은 임포트)
            from search_date import get_schedule_by_date
            text_report = get_schedule_by_date(tmp_path, date_str)
            
            self.send_telegram_msg(token, chat_id, f"📜 함장님, {date_str}의 기록 복원 완료:\n\n{text_report}")
        except Exception as e:
            self.send_telegram_msg(token, chat_id, f"❌ 날짜 검색 중 통신 장애: {str(e)}")

    def process_command(self, text, chat_id):
        cmd = text.split()[0]
        if cmd == "/상태":
            return f"💎 [PyhgoShift] 함대 기동 상태: 정상\nD-Day 전선 이상 없음."
        elif cmd == "/도움말":
            return "🛡️ 지휘 가이드\n/보고 - 오늘 일정 (카드+텍스트)\n/수정 [MM월 DD일 일정] - 과거 기록 조회\n/수정 [내용] - AI 코드 수정"
        return f"⚠️ 미인가 명령: {cmd}"

    def send_telegram_msg(self, token, chat_id, text):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": text})

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Telegram Webhook Handler with Date Search Active.".encode('utf-8'))
