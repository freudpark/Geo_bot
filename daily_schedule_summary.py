
import pandas as pd
from datetime import datetime

def get_daily_schedule(file_path):
    # CSV 파일을 먼저 읽어서 헤더 구조를 파악합니다.
    df_raw = pd.read_csv(file_path, encoding='utf-8', header=None)

    # 실제 헤더가 있는 행을 찾습니다. (예: '순번' 컬럼이 있는 행)
    header_row_index = -1
    for i, row in df_raw.iterrows():
        if '순번' in row.astype(str).values:
            header_row_index = i
            break

    if header_row_index == -1:
        raise ValueError("Could not find header row with '순번' column.")

    # 실제 헤더를 사용하여 다시 CSV 파일을 읽습니다.
    df = pd.read_csv(file_path, encoding='utf-8', skiprows=header_row_index)
    print("Debug - Raw columns:", df.columns.tolist())

    # 컬럼명 유연하게 매핑 (인덱스 및 키워드 기반)
    cols = df.columns.tolist()
    col_mapping = {}
    
    for i, col in enumerate(cols):
        clean_col = str(col).strip()
        if '상태' == clean_col: col_mapping[col] = '상태'
        elif '팀구분' in clean_col: col_mapping[col] = '팀구분'
        elif '구분' == clean_col: col_mapping[col] = '구분'
        elif '작업명' in clean_col: col_mapping[col] = '작업명'
        elif '일자' in clean_col:
            col_mapping[col] = '일자 (시작)'
            if i + 1 < len(cols) and 'Unnamed' in str(cols[i+1]):
                col_mapping[cols[i+1]] = '일자 (종료)'
        elif '작업시간' in clean_col:
            col_mapping[col] = '작업시간 (시작)'
            if i + 1 < len(cols) and 'Unnamed' in str(cols[i+1]):
                col_mapping[cols[i+1]] = '작업시간 (소요시간)'
    
    df.rename(columns=col_mapping, inplace=True)

    # 필수 컬럼 정의
    target_cols = ['상태', '일자 (시작)', '일자 (종료)', '구분', '팀구분', '작업명', '작업시간 (시작)', '작업시간 (소요시간)']
    # 존재하는 컬럼만 선택하고 없는 컬럼은 빈 값으로 생성
    for tc in target_cols:
        if tc not in df.columns:
            df[tc] = None

    # '일자 (시작)'과 '일자 (종료)' 컬럼을 datetime 객체로 변환
    df['일자 (시작)'] = pd.to_datetime(df['일자 (시작)'], errors='coerce')
    df['일자 (종료)'] = pd.to_datetime(df['일자 (종료)'], errors='coerce')
    # 종료일이 없거나 파싱 실패 시 시작일로 대체
    df['일자 (종료)'] = df['일자 (종료)'].fillna(df['일자 (시작)'])

    # 오늘 날짜 가져오기
    today = datetime.now().date()

    # 오늘 날짜에 해당하는 일정 필터링
    # 시작일 <= 오늘 <= 종료일 인 경우를 찾습니다.
    today_schedule = df[(df['일자 (시작)'].dt.date <= today) & (df['일자 (종료)'].dt.date >= today)]

    summary = f"### 정보자원사업단 AI 알림이\n- 제목 : {today.strftime('%Y년 %m월 %d일')} 일정 요약\n\n"

    if not today_schedule.empty:
        summary += "### 오늘의 주요 일정 및 작업 계획\n\n"
        for index, row in today_schedule.iterrows():
            status = row['상태'] if pd.notna(row['상태']) else '미정'
            task_type = row['구분'] if pd.notna(row['구분']) else '미정'
            team = row['팀구분'] if pd.notna(row['팀구분']) else '미정'
            task_name = row['작업명'] if pd.notna(row['작업명']) else '내용 없음'
            start_time = row['작업시간 (시작)'] if pd.notna(row['작업시간 (시작)']) else ''
            duration = row['작업시간 (소요시간)'] if pd.notna(row['작업시간 (소요시간)']) else ''

            summary += f"- **[{task_type}] {task_name}** (상태: {status}, 팀: {team})\n"
            if start_time or duration:
                summary += f"  시작: {start_time}, 소요시간: {duration}\n"
        summary += "\n"
    else:
        summary += "오늘 예정된 주요 일정 및 작업은 없습니다.\n\n"

    return summary

if __name__ == '__main__':
    import os
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(base_path, 'GEO_JobList.csv')
    schedule_summary = get_daily_schedule(csv_file_path)
    print(schedule_summary)
