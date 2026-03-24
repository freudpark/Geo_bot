import pandas as pd
from datetime import datetime
import os
import requests
import json
import sys

# 프로젝트 루트 임포트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_schedule_by_date(file_path, target_date_str):
    """특정 날짜의 일정을 필터링하여 요약 텍스트를 생성합니다."""
    df = pd.read_csv(file_path, encoding='utf-8', skiprows=1)
    if len(df) > 0:
        df = df.drop(0).reset_index(drop=True)

    cols = df.columns.tolist()
    col_mapping = {}
    if len(cols) >= 11:
        col_mapping[cols[0]] = '상태'
        col_mapping[cols[1]] = '일자 (시작)'
        col_mapping[cols[2]] = '일자 (종료)'
        col_mapping[cols[3]] = '구분'
        col_mapping[cols[7]] = '팀구분'
        col_mapping[cols[8]] = '작업명'
        col_mapping[cols[9]] = '작업시간 (시작)'
        col_mapping[cols[10]] = '작업시간 (소요시간)'
    df.rename(columns=col_mapping, inplace=True)

    # 날짜 파싱
    target_date = pd.Timestamp(target_date_str)
    for col in ['일자 (시작)', '일자 (종료)']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    df['일자 (종료)'] = df['일자 (종료)'].fillna(df['일자 (시작)'])

    # 필터링
    mask = (df['일자 (시작)'].dt.normalize() <= target_date) & (df['일자 (종료)'].dt.normalize() >= target_date)
    filtered_df = df[mask.fillna(False)]

    summary = f"### 정보자원사업단 AI 알림이\n- 제목 : {target_date_str} 일정 요약\n\n"
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            summary += f"- **[{row['구분'] or '미정'}] {row['작업명'] or '내용없음'}** (상태: {row['상태']}, 팀: {row['팀구분']})\n"
    else:
        summary = f"### {target_date_str}에는 예정된 일정이 없습니다."
    return summary

def run_for_specific_date(date_str):
    print(f"Targeting date: {date_str}")
    csv_url = 'https://docs.google.com/spreadsheets/d/1hS38RfKBaq13MOWutb4CteswgIIc5Weos0Np-4faRGk/export?format=csv&gid=0'
    csv_path = os.path.join(os.path.dirname(__file__), 'temp_search.csv')
    
    # 다운로드
    res = requests.get(csv_url)
    with open(csv_path, 'wb') as f: f.write(res.content)
    
    # 요약 생성
    summary = get_schedule_by_date(csv_path, date_str)
    
    # D-Day (2026-06-12 기준)
    target_dt = datetime(2026, 6, 12)
    delta_days = (target_dt - datetime.strptime(date_str, "%Y-%m-%d")).days
    d_day_str = f"D-{delta_days}"
    
    # AI 요약
    from ai_agent import generate_ai_summary
    final_summary = generate_ai_summary(summary, d_day_str=d_day_str)
    
    # 파란색에서 노란색으로 헤더 변경 반영 확인 (image_alert_engine.py 수정 필요)
    from image_alert_engine import ImageAlertEngine
    engine = ImageAlertEngine()
    
    # 이미지 생성 및 전송
    image_path = engine.generate_image(final_summary, d_day_str=d_day_str)
    if image_path:
        from telegram_photo_utils import send_telegram_photo
        send_telegram_photo(image_path, caption=f"📅 {date_str} 과거 일정 보고")
    else:
        from telegram_utils import send_telegram_message
        send_telegram_message(f"📅 {date_str} 일정 요약:\n\n{final_summary}")

if __name__ == "__main__":
    run_for_specific_date("2026-03-11")
