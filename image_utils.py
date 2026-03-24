
import os
import imgkit
from datetime import datetime

def generate_alert_image(summary_text, d_day_str):
    """
    텍스트 요약본을 받아 프리미엄 디자인의 이미지로 변환합니다.
    """
    # HTML 템플릿 (함장님이 승인한 다크모드 + 글래스모피즘 스타일)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Pretendard', sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                width: 800px;
                height: 500px;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #f8fafc;
            }}
            .card {{
                width: 720px;
                height: 420px;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 30px;
                position: relative;
                display: flex;
                flex-direction: column;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }}
            .logo {{
                position: absolute;
                top: 25px;
                left: 30px;
                font-size: 18px;
                font-weight: 800;
                color: #38bdf8;
                letter-spacing: -0.5px;
            }}
            .header {{
                text-align: center;
                margin-top: 10px;
                margin-bottom: 30px;
            }}
            .title {{
                font-size: 32px;
                font-weight: 700;
                margin: 0;
                background: linear-gradient(90deg, #38bdf8, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .date {{
                font-size: 14px;
                color: #94a3b8;
                margin-top: 5px;
            }}
            .content {{
                flex: 1;
                font-size: 18px;
                line-height: 1.6;
                overflow: hidden;
                white-space: pre-wrap;
            }}
            .bullet {{
                color: #38bdf8;
                margin-right: 10px;
            }}
            .footer {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .d-day {{
                font-size: 20px;
                font-weight: 700;
                color: #f43f5e;
            }}
            .status {{
                font-size: 14px;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">PyhgoShift</div>
            <div class="header">
                <div class="title">정보자원 Daily 알림</div>
                <div class="date">{datetime.now().strftime('%Y년 %m월 %d일')}</div>
            </div>
            <div class="content">
                {summary_text.replace('### 오늘의 주요 일정 및 작업 계획', '').replace('### 정보자원사업단 AI 알림이', '').strip()}
            </div>
            <div class="footer">
                <div class="status">System Status: Online</div>
                <div class="d-day">{d_day_str}</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 임시 이미지 경로
    is_vercel = os.getenv('VERCEL') == '1'
    output_path = '/tmp/alert_card.png' if is_vercel else 'alert_card.png'
    
    options = {
        'format': 'png',
        'encoding': "UTF-8",
        'quiet': '',
        'width': 800,
        'height': 500,
        'enable-local-file-access': None
    }
    
    # wkhtmltoimage 설치 경로 (윈도우/리눅스 환경에 따라 다를 수 있음)
    # Vercel에서는 별도의 빌드 스텝이 필요할 수 있으나, 로컬 테스트용으로 먼저 작동 확인
    try:
        imgkit.from_string(html_content, output_path, options=options)
        return output_path
    except Exception as e:
        print(f"[ImageGen] Failed: {e}")
        return None

if __name__ == "__main__":
    test_text = "오늘 예정된 주요 일정 및 작업은 없습니다.\n\n- [인프라] 서버 점검 예정\n- [네트워크] 방화벽 정책 변경"
    path = generate_alert_image(test_text, "D-81")
    if path: print(f"Image saved at: {os.path.abspath(path)}")
