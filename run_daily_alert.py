import requests
import os
from datetime import datetime
from kakao_utils import send_message_to_me
from daily_schedule_summary import get_daily_schedule

def run():
    # 1. 최신 구글 시트 다운로드
    csv_url = 'https://docs.google.com/spreadsheets/d/1hS38RfKBaq13MOWutb4CteswgIIc5Weos0Np-4faRGk/export?format=csv&gid=0'
    
    # Vercel과 같은 서버리스 환경에서는 /tmp 폴더를 사용해야 합니다.
    is_vercel = os.getenv('VERCEL') == '1'
    if is_vercel:
        csv_path = '/tmp/pyhgoshift_info.csv'
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_path, 'pyhgoshift_info.csv')
    
    print(f"Downloading CSV to {csv_path}...")
    response = requests.get(csv_url)
    response.raise_for_status()
    with open(csv_path, 'wb') as f:
        f.write(response.content)

    # 2. 일정 요약 생성
    print("Generating raw summary...")
    raw_summary = get_daily_schedule(csv_path)
    print(f"Raw summary generated (length: {len(raw_summary)})")
    
    # 3. D-Day 정밀 계산 (Target: 2026-06-12 00:00:00)
    # 데이터 불일치 박멸을 위해 메인 센터에서 1회만 계산
    target_dt = datetime(2026, 6, 12)
    today_dt = datetime.now()
    delta_days = (target_dt - today_dt).days
    d_day_str = f"D-{delta_days}" if delta_days >= 0 else f"D+{abs(delta_days)}"

    # AI 요약 생성 (중앙에서 계산된 D-Day 전달)
    print("Generating AI summary...")
    from ai_agent import generate_ai_summary
    final_summary = generate_ai_summary(raw_summary, d_day_str=d_day_str)
    print(f"AI summary generated (length: {len(final_summary)})")
    
    # 4. 통합 이미지 알림 엔진 가동
    print("Initializing Image Alert Engine...")
    from image_alert_engine import ImageAlertEngine
    engine = ImageAlertEngine()
    
    # 이미지 생성 (전달받은 d_day_str 공유)
    print("Generating Glass Card image...")
    image_path = engine.generate_image(final_summary, d_day_str=d_day_str)
    
    if image_path:
        # 5. 카카오톡 전송 (이미지 피드)
        print("Sending to Kakao recipients (Image Feed)...")
        from kakao_utils import send_to_all_recipients, load_tokens
        
        # 카카오 이미지 업로드를 위해 토큰 로드 (첫 번째 수신자 기준 혹은 기본 토큰)
        try:
            tokens = load_tokens()
            image_url = engine.upload_to_kakao(image_path, tokens["access_token"])
            if image_url:
                kakao_result = send_to_all_recipients(final_summary, image_url=image_url)
                print(f"[Kakao] Image feed sent to all recipients.")
            else:
                print("[Kakao] Image upload failed. Falling back to text (not implemented).")
                kakao_result = {"error": "Image upload failed"}
        except Exception as e:
            print(f"[Kakao] Error during image flow: {e}")
            kakao_result = {"error": str(e)}

        # 6. 텔레그램 전송 (이미지 포토)
        print("Sending to Telegram group (Image Photo)...")
        try:
            engine.send_telegram(image_path, f"💎 정보자원 Daily 알림\n{datetime.now().strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"[Telegram] Error: {e}")
    else:
        print("[Engine] Image generation failed. No alerts sent.")
        kakao_result = {"error": "Image gen failed"}

    # 서버리스 환경에서는 일반 파일 쓰기가 제한될 수 있으므로 분기 처리
    if not is_vercel:
        base_path = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_path, 'execution_log.txt')
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()}: Execution result - {kakao_result}\n")
        except:
            pass
    
    print(f"Finished. Final result: {kakao_result}")

if __name__ == "__main__":
    run()
