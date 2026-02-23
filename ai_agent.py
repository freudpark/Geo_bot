from dotenv import load_dotenv
import google.generativeai as genai
import os

def generate_ai_summary(schedule_data):
    """
    일정 데이터를 바탕으로 Gemini AI를 사용하여 가독성 좋은 뉴스 스타일 요약을 생성합니다.
    """
    load_dotenv() # .env 파일에서 환경변수 로드
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return schedule_data + "\n\n(참고: GEMINI_API_KEY가 설정되지 않아 기본 요약을 전송합니다.)"

    genai.configure(api_key=api_key)
    # 모델명을 더 구체적으로 지정하여 404 오류 방지
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt = f"""
다음은 오늘 예정된 구글 시트 일정 데이터입니다.
이 내용을 바탕으로 사용자가 읽기 쉽고 친절한 '오늘의 미션' 또는 '뉴스 리포트' 스타일로 요약해 주세요.

[일정 데이터]
{schedule_data}

[작성 가이드라인]
1. 친절하고 전문적인 톤을 유지하세요.
2. 중요한 일정이나 마감이 임박한 작업이 있다면 강조해 주세요.
3. 단순 리스트가 아닌 자연스러운 문장으로 구성해 주세요.
4. 마지막에는 힘찬 응원의 메시지를 한 줄 추가해 주세요.
5. 마크다운 형식을 적절히 사용하여 가독성을 높여주세요.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # 에러 메시지를 더 상세히 출력하여 디버깅 지원
        error_msg = f"\n\n(AI 요약 생성 중 오류 발생: {type(e).__name__} - {str(e)})"
        print(f"Gemini API Error: {error_msg}")
        return schedule_data + error_msg

if __name__ == "__main__":
    test_data = "## 정보자원 AI 알림이 - 2026년 02월 23일\n- [작업] 서버 점검 (상태: 진행중, 팀: 인프라팀)\n- [일정] 주간 회의 (상태: 예정, 팀: 기획팀)"
    print(generate_ai_summary(test_data))
