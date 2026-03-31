import requests
import os
from datetime import datetime
from daily_schedule_summary import get_daily_schedule

def run_with_result():
    """핵심 데이터 요약만을 수행하는 엔진"""
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
        
        # 3. D-Day 계산 (Target: 2026-06-12)
        target_dt = datetime(2026, 6, 12)
        today_dt = datetime.now()
        delta_days = (target_dt - today_dt).days
        d_day_str = f"D-{delta_days}" if delta_days >= 0 else f"D+{abs(delta_days)}"

        # 4. AI 요약 생성 (가장 가벼운 텍스트 리포트)
        from ai_agent import generate_ai_summary
        final_summary = generate_ai_summary(raw_summary, d_day_str=d_day_str)
        
        return True, final_summary
            
    except Exception as e:
        print(f"[Run] Error: {e}")
        return False, f"데이터 처리 중 에러 발생: {str(e)}"

def run():
    """통합 실행 시퀀스: 이미지 제거, 텍스트 전송 최우화 전략"""
    print(f"[{datetime.now()}] !!! LIGHTWEIGHT TEXT-ONLY ALERT START !!!")
    
    # 0. 데이터 및 AI 요약 확보 (이미지 생성 로직 완전 제거)
    success, final_summary = run_with_result()
    
    # 1. 카카오톡 발송 (최우선)
    from kakao_utils import send_to_all_recipients
    print("[Kakao] Sending text alert to all recipients...")
    try:
        # 이미지는 None으로 처리하여 텍스트 템플릿 강제 사용
        kakao_res = send_to_all_recipients(final_summary, image_url=None)
        print(f"[Kakao] Results: {kakao_res}")
    except Exception as e:
        print(f"[Kakao] Failed to send: {e}")
        
    # 2. 텔레그램 발송
    from telegram_utils import send_telegram_message
    print("[Telegram] Sending text alert...")
    try:
        send_telegram_message(f"💎 정보자원 Daily 알림\n{datetime.now().strftime('%Y-%m-%d')}\n\n{final_summary}")
    except Exception as e:
        print(f"[Telegram] Failed to send: {e}")
            
    print("!!! TEXT-ONLY ALERT COMPLETED !!!")

if __name__ == "__main__":
    run()
