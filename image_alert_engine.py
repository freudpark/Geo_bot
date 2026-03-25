import os
import requests
import json
from datetime import datetime
import asyncio

class ImageAlertEngine:
    def __init__(self):
        self.is_vercel = os.getenv('VERCEL') == '1'
        self.output_image = '/tmp/alert_card_final.png' if self.is_vercel else 'alert_card_final.png'
        self.html_file = '/tmp/alert_card.html' if self.is_vercel else 'alert_card.html'

    def generate_image(self, summary_text, d_day_str="D-80"):
        """
        안티그래비티 기지(로컬)와 Vercel 환경 모두에서 작동하는 하이브리드 이미지 엔진.
        Vercel에서는 리소스 제한으로 인해 실패할 확률이 높으므로, 
        실패 시 AI 텍스트 리포트로 자동 전환되는 Fail-safe 구조를 갖춥니다.
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 1. 디자인 데이터 가공
        forbidden_words = ["정보자원사업단", "작업계획", "주요일정", "일정 요약", "알리미", "제목 :", "#", "사업 완료일까지", "D-"]
        lines = [line.strip() for line in summary_text.split('\n') if line.strip()]
        clean_lines = []
        for line in lines:
            if any(word in line for word in forbidden_words): continue
            text = line.replace('●', '').replace('- ', '').replace('**', '').replace('🔹', '').replace('📍', '').strip()
            if text: clean_lines.append(text)

        # 2. 메트릭 계산
        line_count = len(clean_lines)
        total_chars = sum(len(l) for l in clean_lines)
        estimated_rows = line_count + (total_chars // 22) 
        dynamic_height = 75 + (estimated_rows * 22)
        card_height = max(130, min(500, dynamic_height))
        canvas_height = card_height + 20

        content_html = ""
        if not clean_lines:
            content_html = '<p class="text-[#94a3b8] text-[11px] italic opacity-60 text-center py-2">No tasks today.</p>'
        else:
            list_items = ""
            for line in clean_lines[:12]: 
                list_items += f"""
                <div class="flex items-start text-[12px] font-bold text-[#f8fafc] mb-1 leading-tight border-l-2 border-[#38bdf8]/50 pl-2.5">
                    <div class="flex-1 whitespace-normal break-words">{line}</div>
                </div>
                """
            content_html = f'<div class="flex-1 overflow-visible">{list_items}</div>'

        # 3. HTML 템플릿 (함장님의 '노란색' 헤더 반영)
        html_template = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@700;900&display=swap');
                body {{ font-family: 'Pretendard', sans-serif; margin: 0; padding: 0; background: #0f172a; display: flex; align-items: center; justify-content: center; width: 320px; height: {canvas_height}px; }}
                .glass-card {{ width: 290px; height: {card_height}px; background: linear-gradient(135deg, rgba(30, 41, 59, 1.0), rgba(15, 23, 42, 1.0)); border-radius: 20px; border: 1.2px solid rgba(255, 255, 255, 0.1); box-shadow: 0 40px 80px rgba(0, 0, 0, 0.95); padding: 15px; display: flex; flex-direction: column; position: relative; overflow: hidden; }}
                .glass-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1.5px; background: linear-gradient(90deg, transparent, #fbbf24, transparent); }}
            </style>
        </head>
        <body>
            <div class="glass-card">
                <div class="mb-1.5 border-b border-white/10 pb-1 flex justify-between items-baseline">
                    <div class="text-[#fbbf24] text-[16px] font-black tracking-tighter">정보자원 AI 일일 알리미</div>
                    <div class="text-[#38bdf8] text-[9px] font-bold tracking-widest opacity-80">{date_str}</div>
                </div>
                {content_html}
                <div class="pt-0.5 border-t border-white/5 flex flex-col items-center justify-center opacity-80">
                    <p class="text-[9px] font-bold text-[#64748b] leading-none mb-0.5">사업 완료일까지</p>
                    <p class="text-[15px] font-black text-[#f43f5e] tracking-tight leading-none italic">{d_day_str}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_template)

        # 4. 고성능 렌더링 시도 (Playwright/Node 하이브리드)
        try:
            # 로컬에서는 Node.js Puppeteer가 빠르므로 먼저 시도 (패키지가 있다면)
            if not self.is_vercel:
                render_js = 'render_card.js'
                node_code = f"""
                const nodeHtmlToImage = require('node-html-to-image');
                const fs = require('fs');
                nodeHtmlToImage({{
                  output: '{self.output_image}',
                  html: fs.readFileSync('{self.html_file}', 'utf8'),
                  puppeteerArgs: {{ args: ['--no-sandbox'] }}
                }}).then(() => console.log('Done'));
                """
                with open(render_js, 'w', encoding='utf-8') as f: f.write(node_code)
                os.system(f"node {render_js}")
            
            # 실패했거나 Vercel인 경우, 혹은 다른 방법 시도 (수동 검증)
            if os.path.exists(self.output_image):
                return self.output_image
        except:
            pass

        return None

    def send_telegram(self, image_path, caption):
        token = os.getenv("TELEGRAM_BOT_TOKEN", "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "-1002916386908")
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        try:
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': chat_id, 'caption': caption}
                requests.post(url, files=files, data=data)
        except Exception as e:
            print(f"Telegram send failed: {e}")

    def upload_to_kakao(self, image_path, access_token):
        url = "https://kapi.kakao.com/v2/api/talk/storage/image"
        headers = { "Authorization": f"Bearer {access_token}" }
        try:
            with open(image_path, 'rb') as f:
                res = requests.post(url, headers=headers, files={ "file": f })
            return res.json().get('infos', {}).get('original', {}).get('url') if res.status_code == 200 else None
        except: return None
