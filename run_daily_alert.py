import requests
import os
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
    
    # 3. AI 고도화 요약 (Gemini 활용)
    print("Generating AI summary...")
    from ai_agent import generate_ai_summary
    final_summary = generate_ai_summary(raw_summary)
    print(f"AI summary generated (length: {len(final_summary)})")

    # 4. 카카오톡 전송
    print("Sending to recipients...")
    from kakao_utils import send_to_all_recipients
    result = send_to_all_recipients(final_summary)
    
    # 서버리스 환경에서는 일반 파일 쓰기가 제한될 수 있으므로 분기 처리
    if not is_vercel:
        base_path = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_path, 'execution_log.txt')
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                from datetime import datetime
                f.write(f"{datetime.now()}: Execution result - {result}\n")
        except:
            pass
    
    print(f"Finished. Final result: {result}")

if __name__ == "__main__":
    run()
