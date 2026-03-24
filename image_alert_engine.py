import os
import requests
import json
from datetime import datetime

class ImageAlertEngine:
    def __init__(self):
        self.is_vercel = os.getenv('VERCEL') == '1'
        self.output_image = '/tmp/alert_card_final.png' if self.is_vercel else 'alert_card_final.png'
        self.html_file = '/tmp/alert_card.html' if self.is_vercel else 'alert_card.html'
        self.render_js = '/tmp/render_card.js' if self.is_vercel else 'render_card.js'

    def generate_image(self, summary_text, d_day_str="D-81"):
        """함장님의 '상하 압착' 명령에 따라 너비와 폰트는 유지하되 수직 공백만 제거한 카드를 생성합니다."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 1. 디자인 데이터 가공
        forbidden_words = ["정보자원사업단", "작업계획", "주요일정", "일정 요약", "알리미", "제목 :", "#", "사업 완료일까지", "D-"]
        lines = [line.strip() for line in summary_text.split('\n') if line.strip()]
        clean_lines = []
        for line in lines:
            if any(word in line for word in forbidden_words): continue
            text = line.replace('●', '').replace('- ', '').replace('**', '').replace('🔹', '').replace('📍', '').strip()
            if text: clean_lines.append(text)

        # 2. '수직 정밀 압착' 높이 계산 (좌우는 원복, 상하는 압착)
        # 기본 헤더(25) + 풋터(20) + 마진(30) = 약 75px 기반 (기존 90에서 하단 10 더 축소)
        line_count = len(clean_lines)
        total_chars = sum(len(l) for l in clean_lines)
        
        # 줄당 22px 계산 (좌우 너비가 넓으므로)
        estimated_rows = line_count + (total_chars // 22) 
        dynamic_height = 75 + (estimated_rows * 22)
        
        # 최소 130px ~ 최대 500px (상하 압착형)
        card_height = max(130, min(500, dynamic_height))
        canvas_height = card_height + 20

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

        # 3. 상하 압착 가변 유리 카드 (320px 너비 원복)
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
                .glass-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1.5px; background: linear-gradient(90deg, transparent, #38bdf8, transparent); }}
            </style>
        </head>
        <body>
            <div class="glass-card">
                <div class="mb-1.5 border-b border-white/10 pb-1 flex justify-between items-baseline">
                    <div class="text-[#fbbf24] text-[16px] font-black tracking-tighter opacity-100">정보자원 AI 일일 알리미</div>
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
        
        # 4. Node.js 렌더링 스크립트
        node_code = f"""
        const nodeHtmlToImage = require('node-html-to-image')
        const fs = require('fs')
        const html = fs.readFileSync('{self.html_file}', 'utf8')
        nodeHtmlToImage({{
          output: '{self.output_image}',
          html: html,
          puppeteerArgs: {{ args: ['--no-sandbox', '--disable-setuid-sandbox'] }}
        }}).then(() => console.log('Report Card Image Generated.'))
        """
        with open(self.render_js, 'w', encoding='utf-8') as f:
            f.write(node_code)
        
        os.system(f"node {self.render_js}")
        return self.output_image if os.path.exists(self.output_image) else None

    def upload_to_kakao(self, image_path, access_token):
        """카카오 서버로 이미지를 업로드하고 URL을 받아옵니다."""
        url = "https://kapi.kakao.com/v2/api/talk/storage/image"
        headers = { "Authorization": f"Bearer {access_token}" }
        # multipart/form-data로 파일을 전송할 때는 requests.post의 files 인자를 사용하며 
        # 이때 headers에 Content-Type을 직접 지정하지 않는 것이 좋습니다.
        try:
            with open(image_path, 'rb') as f:
                files = { "file": f }
                res = requests.post(url, headers=headers, files=files)
            
            if res.status_code == 200:
                return res.json().get('infos', {}).get('original', {}).get('url')
            else:
                print(f"[Kakao Image] Upload failed ({res.status_code}): {res.text}")
                return None
        except Exception as e:
            print(f"[Kakao Image] Error during upload: {e}")
            return None

    def send_telegram(self, image_path, caption):
        """텔레그램으로 이미지를 전송합니다."""
        token = os.getenv("TELEGRAM_BOT_TOKEN", "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "-1002916386908")
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': caption}
            requests.post(url, files=files, data=data)
            print("[Telegram] Card sent.")

if __name__ == "__main__":
    # 통합 엔진 자가 테스트
    engine = ImageAlertEngine()
    img = engine.generate_image("일정 없음")
    if img: print(f"Test image ready: {img}")
