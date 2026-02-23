import requests
from kakao_utils import send_message_to_me
from daily_schedule_summary import get_daily_schedule

def run():
    # 1. 최신 구글 시트 다운로드
    csv_url = 'https://docs.google.com/spreadsheets/d/1hS38RfKBaq13MOWutb4CteswgIIc5Weos0Np-4faRGk/export?format=csv&gid=0'
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, 'GEO_JobList.csv')
    
    print(f"Downloading CSV to {csv_path}...")
    response = requests.get(csv_url)
    response.raise_for_status()
    with open(csv_path, 'wb') as f:
        f.write(response.content)

    # 2. 일정 요약 생성
    raw_summary = get_daily_schedule(csv_path)
    
    # 3. AI 고도화 요약 (Gemini 활용)
    from ai_agent import generate_ai_summary
    final_summary = generate_ai_summary(raw_summary)

    # 4. 카카오톡 전송
    result = send_message_to_me(final_summary)
    
    log_path = os.path.join(base_path, 'execution_log.txt')
    with open(log_path, 'a', encoding='utf-8') as f:
        from datetime import datetime
        f.write(f"{datetime.now()}: Execution result - {result}\n")
    print(f"Finished. Result: {result}")

if __name__ == "__main__":
    run()
