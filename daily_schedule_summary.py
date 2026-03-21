
import pandas as pd
from datetime import datetime

def get_daily_schedule(file_path):
    # CSV 파일을 먼저 읽어서 헤더 구조를 파악합니다.
    df_raw = pd.read_csv(file_path, encoding='utf-8', header=None)

    # 실제 헤더가 있는 행을 찾습니다. (예: '상태' 및 '작업명' 컬럼이 같이 있는 행)
    header_row_index = -1
    for i, row in df_raw.iterrows():
        row_str = row.astype(str).tolist()
        if '상태' in row_str and '작업명' in row_str:
            header_row_index = i
            break

    # 새로운 방식으로 헤더 인덱스를 1로 고정하여 읽고, (1번행이 '상태', '일자' 등이 있는 메인 헤더)
    # 2번행에 서브헤더('시작', '종료')가 있으므로 이를 조합하거나 인덱스 기반으로 강제 매핑합니다.
    df = pd.read_csv(file_path, encoding='utf-8', skiprows=1)
    
    # 데이터 행은 2번 인덱스부터 시작하므로 (원래 CSV 기준 3번째 줄부터 데이터), 
    # skiprows=1로 읽었으니 0번 인덱스 행('시작', '종료' 등의 서브헤더)을 제거합니다.
    if len(df) > 0:
        df = df.drop(0).reset_index(drop=True)

    # 컬럼 이름이 복잡하므로 위치(index) 및 키워드를 병합하여 매핑합니다.
    cols = df.columns.tolist()
    col_mapping = {}
    
    # 1. 위치 기반 기본 매핑 (현재 시트 구조 보장)
    if len(cols) >= 11:
        col_mapping[cols[0]] = '상태'
        col_mapping[cols[1]] = '일자 (시작)'
        col_mapping[cols[2]] = '일자 (종료)'
        col_mapping[cols[3]] = '구분'
        col_mapping[cols[7]] = '팀구분'
        col_mapping[cols[8]] = '작업명'
        col_mapping[cols[9]] = '작업시간 (시작)'
        col_mapping[cols[10]] = '작업시간 (소요시간)'
    
    # 2. 키워드 기반 보정 (위치가 틀어졌을 경우 대비)
    for i, col in enumerate(cols):
        c_name = str(col).strip()
        if '상태' in c_name and '상태' not in col_mapping.values(): col_mapping[col] = '상태'
        elif '작업명' in c_name: col_mapping[col] = '작업명'
        elif '팀구분' in c_name: col_mapping[col] = '팀구분'
        elif '일자' in c_name: 
            col_mapping[col] = '일자 (시작)'
            if i+1 < len(cols): col_mapping[cols[i+1]] = '일자 (종료)'
        elif '작업시간' in c_name:
            col_mapping[col] = '작업시간 (시작)'
            if i+1 < len(cols): col_mapping[cols[i+1]] = '작업시간 (소요시간)'
        
    df.rename(columns=col_mapping, inplace=True)
    print(f"Debug - Final columns: {df.columns.tolist()}")

    # 필수 컬럼 정의
    target_cols = ['상태', '일자 (시작)', '일자 (종료)', '구분', '팀구분', '작업명', '작업시간 (시작)', '작업시간 (소요시간)']
    # 존재하는 컬럼만 선택하고 없는 컬럼은 빈 값으로 생성
    for tc in target_cols:
        if tc not in df.columns:
            df[tc] = None

    # '일자 (시작)'과 '일자 (종료)' 컬럼을 datetime 객체로 변환
    # 한국에서 흔히 사용하는 형식들 시도
    for col in ['일자 (시작)', '일자 (종료)']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 종료일이 없거나 파싱 실패 시 시작일로 대체
    df['일자 (종료)'] = df['일자 (종료)'].fillna(df['일자 (시작)'])
    print(f"Debug - Date parsing completed. Valid rows: {df['일자 (시작)'].notna().sum()}")

    # 오늘 날짜 가져오기 (UTC 기준 Vercel 환경 고려)
    # 한국 시간(KST)으로 보정해서 필터링할 수도 있으나, 0시에 실행된다면 UTC/KST 일자가 같을 가능성이 큼
    # 비교를 위해 datetime 타입 원본을 유지하거나 pd.Timestamp 사용
    today_ts = pd.Timestamp(datetime.now().date())
    print(f"Debug - Today's date TS: {today_ts}")

    # 오늘 날짜에 해당하는 일정 필터링
    # 시작일 <= 오늘 <= 종료일 인 경우를 찾습니다.
    try:
        # 시간 부분이 들어간 경우를 대비하여 normalize() 처리
        mask = (df['일자 (시작)'].dt.normalize() <= today_ts) & (df['일자 (종료)'].dt.normalize() >= today_ts)
        today_schedule = df[mask.fillna(False)]
        print(f"Debug - Filtered schedule count: {len(today_schedule)}")
    except Exception as e:
        print(f"Debug - Filtering failed: {e}")
        today_schedule = pd.DataFrame()

    summary = f"### 정보자원사업단 AI 알림이\n- 제목 : {datetime.now().strftime('%Y년 %m월 %d일')} 일정 요약\n\n"

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
