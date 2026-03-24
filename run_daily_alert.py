import requests
import os
from datetime import datetime
from kakao_utils import send_message_to_me
from daily_schedule_summary import get_daily_schedule

def run_with_result():
    """웹훅 등에서 결과를 리턴받기 위한 함수 버전"""
    try:
        # 1. 최신 구글 시트 다운로드
        csv_url = 'https://docs.google.com/spreadsheets/d/1hS38RfKBaq13MOWutb4CteswgIIc5Weos0Np-4faRGk/export?format=csv&gid=0'
        is_vercel = os.getenv('VERCEL') == '1'
        csv_path = '/tmp/pyhgoshift_info.csv' if is_vercel else os.path.join(os.path.dirname(__file__), 'pyhgoshift_info.csv')
        
        response = requests.get(csv_url)
        response.raise_for_status()
        with open(csv_path, 'wb') as f:
            f.write(response.content)

        # 2. 일정 요약 생성
        raw_summary = get_daily_schedule(csv_path)
        
        # 3. D-Day 정밀 계산
        target_dt = datetime(2026, 6, 12)
        today_dt = datetime.now()
        delta_days = (target_dt - today_dt).days
        d_day_str = f"D-{delta_days}" if delta_days >= 0 else f"D+{abs(delta_days)}"

        # AI 요약 생성
        from ai_agent import generate_ai_summary
        final_summary = generate_ai_summary(raw_summary, d_day_str=d_day_str)
        
        # 4. 이미지 생성 시도
        from image_alert_engine import ImageAlertEngine
        engine = ImageAlertEngine()
        image_path = engine.generate_image(final_summary, d_day_str=d_day_str)
        
        if image_path and os.path.exists(image_path):
            return True, final_summary, image_path
        else:
            return False, final_summary, None
            
    except Exception as e:
        print(f"[Run] Error: {e}")
        return False, "에러 발생으로 리포트 생성 불가", None

def run():
    """기존의 통합 실행 시퀀스"""
    success, final_summary, image_path = run_with_result()
    
    # 텔레그램 전송
    from telegram_photo_utils import send_telegram_photo
    from telegram_utils import send_telegram_message
    
    if success and image_path:
        # 이미지 전송
        send_telegram_photo(image_path, caption=f"💎 정보자원 Daily 알림\n{datetime.now().strftime('%Y-%m-%d')}")
    else:
        # 텍스트 백업 전송
        send_telegram_message(f"⚠️ [시스템 알림] 이미지 생성 불가.\n텍스트 리포트:\n\n{final_summary}")
        
    print("Run completed.")

if __name__ == "__main__":
    run()
