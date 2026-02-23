from dotenv import load_dotenv
import os

def generate_ai_summary(schedule_data):
    """
    다양한 AI 프로바이더(Gemini, DeepSeek, Kimi, Qwen 등)를 지원하는 통합 요약 생성 함수입니다.
    """
    load_dotenv()
    
    # 환경 변수 로드
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    api_key = os.getenv("AI_API_KEY") or os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("AI_BASE_URL")
    model_name = os.getenv("AI_MODEL")
    
    if not api_key:
        return schedule_data + "\n\n(참고: AI_API_KEY가 설정되지 않아 기본 요약을 전송합니다.)"

    # 작성 가이드라인 (프롬프트 공통)
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
        # 1. Gemini 프로바이더 (google-genai)
        if provider == "gemini":
            from google import genai
            client = genai.Client(api_key=api_key)
            model_target = model_name or "gemini-2.0-flash"
            print(f"Using Gemini Provider: {model_target}")
            response = client.models.generate_content(model=model_target, contents=prompt)
            return response.text

        # 2. OpenAI 호환 프로바이더 (openai SDK 사용: DeepSeek, Kimi, Qwen 등)
        else:
            from openai import OpenAI
            
            # 프로바이더별 기본 설정
            if provider == "deepseek":
                base_url = base_url or "https://api.deepseek.com"
                model_target = model_name or "deepseek-chat"
            elif provider == "kimi":
                base_url = base_url or "https://api.moonshot.ai/v1"
                model_target = model_name or "moonshot-v1-8k"
            elif provider == "qwen":
                base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
                model_target = model_name or "qwen-plus"
            else: # general openai
                model_target = model_name or "gpt-4o-mini"

            print(f"Using OpenAI-compatible Provider ({provider}): {model_target} at {base_url}")
            client = OpenAI(api_key=api_key, base_url=base_url)
            response = client.chat.completions.create(
                model=model_target,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

    except Exception as e:
        error_msg = f"\n\n(AI 요약 생성 중 오류 발생 [{provider}]: {type(e).__name__} - {str(e)})"
        print(f"AI Provider Error: {error_msg}")
        return schedule_data + error_msg

if __name__ == "__main__":
    test_data = "## 정보자원 AI 알림이 - 2026년 02월 23일\n- [작업] 서버 점검 (상태: 진행중, 팀: 인프라팀)\n- [일정] 주간 회의 (상태: 예정, 팀: 기획팀)"
    # 로컬 테스트용 (환경변수 설정 시 작동)
    print(generate_ai_summary(test_data))
