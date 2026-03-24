
import os
import requests
from datetime import datetime

def generate_and_send_final_card(summary_text, d_day_str="D-81"):
    """
    실제 데이터를 한글 유리 카드 디자인에 주입하여 렌더링하고 텔레그램으로 전송합니다.
    """
    # 1. 디자인에 넣을 한글 데이터 가공
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 일정이 없을 때와 있을 때의 처리
    if "없습니다" in summary_text:
        content_html = f"""
        <div class="flex-1 space-y-8 px-4 flex flex-col justify-center">
            <p class="text-[#94a3b8] text-3xl text-center italic leading-relaxed">
                "오늘 예정된 주요 일정 및<br>작업 계획은 없습니다."
            </p>
        </div>
        """
    else:
        # 실제 일정이 있을 경우 상위 4개 정도만 아이콘과 함께 표시 (예시 구현)
        # 나중에 summary_text를 파싱하여 동적으로 생성 가능
        content_html = f"""
        <div class="flex-1 space-y-6 px-2 overflow-hidden">
            <p class="text-[#f8fafc] text-2xl font-bold mb-4">오늘의 주요 일정:</p>
            {summary_text.replace('### 오늘의 주요 일정 및 작업 계획', '').strip()}
        </div>
        """

    # 2. HTML 템플릿 (함장님 최종 승인본 - 한글+베젤 최소화)
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');
            body {{ font-family: 'Pretendard', sans-serif; margin: 0; padding: 0; background: #0f172a; display: flex; align-items: center; justify-content: center; width: 650px; height: 650px; }}
            .glass-card {{ width: 600px; height: 600px; background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(40px); border-radius: 60px; border: 2px solid rgba(255, 255, 255, 0.1); box-shadow: 0 40px 80px rgba(0, 0, 0, 0.5); padding: 50px; display: flex; flex-direction: column; position: relative; overflow: hidden; }}
            .glass-card::after {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, transparent, #38bdf8, transparent); }}
        </style>
    </head>
    <body>
        <div class="glass-card">
            <div class="text-center mb-10">
                <h1 class="text-[#f8fafc] text-4xl font-black mb-3 tracking-tight">정보자원 Daily 알림</h1>
                <p class="text-[#38bdf8] text-2xl font-bold tracking-[0.2em]">{date_str}</p>
            </div>
            {content_html}
            <div class="mt-6 py-8 border-t border-white/10 text-center">
                <p class="text-[34px] font-black text-[#f8fafc] opacity-95 tracking-tight">
                    사업 완료일까지 <span class="text-[#f43f5e] ml-2">{d_day_str}</span>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('final_report.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # Node.js 렌더링
    render_js = """
    const nodeHtmlToImage = require('node-html-to-image')
    const fs = require('fs')
    const html = fs.readFileSync('final_report.html', 'utf8')
    nodeHtmlToImage({
      output: './final_report_card.png',
      html: html,
      puppeteerArgs: { args: ['--no-sandbox', '--disable-setuid-sandbox'] }
    }).then(() => console.log('Final Report Card created!'))
    """
    with open('render_final_report.js', 'w', encoding='utf-8') as f:
        f.write(render_js)
    
    os.system("node render_final_report.js")
    
    # 텔레그램 발송
    token = "8612770185:AAEchYNNBNfxHLOZ8FQ6JvZJuFI4G92nt4E"
    chat_id = "-1002916386908"
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    if os.path.exists('final_report_card.png'):
        with open('final_report_card.png', 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': f'💎 {date_str} 정보자원 AI 지휘 보고 (실전 데이터 적용)'}
            requests.post(url, files=files, data=data)
            print("Final Report Card sent to Telegram.")

if __name__ == "__main__":
    # 오늘 데이터 샘플링 (일정 없음 케이스)
    sample_summary = "### 정보자원사업단 AI 알림이\\n- 제목 : 2026년 03월 23일 일정 요약\\n\\n오늘 예정된 주요 일정 및 작업은 없습니다.\\n\\n"
    generate_and_send_final_card(sample_summary, "D-81")
