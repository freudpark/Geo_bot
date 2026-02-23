from dotenv import load_dotenv
import os

def generate_ai_summary(schedule_data):
    """
    다양한 AI 프로바이더를 지원하며, 서버 오류 시 깔끔하게 기본 내용을 반환하는 튼튼한 요약 함수입니다.
    """
    load_dotenv()
    
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    api_key = os.getenv("AI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # AI 설정이 없으면 즉시 요약 없이 원본 반환
    if not api_key:
        return schedule_data + "\n\n(안내: AI 키가 설정되지 않아 기본 일정만 전항합니다.)"

    common_prompt = f"""
다음 일정을 친절한 뉴스 리포트 스타일로 요약해 주세요.

[데이터]
{schedule_data}

[요청사항]
1. 가독성 좋게 요약.
2. 자연스러운 문장 사용.
3. 마지막에 응원 메시지 한 줄.
"""

    try:
        # 1. Gemini (Google Free Tier)
        if provider == "gemini":
            from google import genai
            client = genai.Client(api_key=api_key)
            # 가장 성공 확률이 높은 모델 순서로 배치 (pro 모델은 404가 잦아 제외)
            for model in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-8b"]:
                try:
                    res = client.models.generate_content(model=model, contents=common_prompt)
                    if res and res.text: return res.text
                except: continue

        # 2. OpenAI-Compatible (DeepSeek, Kimi, Qwen...)
        else:
            from openai import OpenAI
            base_url = os.getenv("AI_BASE_URL")
            model_name = os.getenv("AI_MODEL")
            
            if provider == "deepseek":
                base_url = base_url or "https://api.deepseek.com"
                model_name = model_name or "deepseek-chat"
            elif provider == "kimi":
                base_url = base_url or "https://api.moonshot.ai/v1"
                model_name = model_name or "moonshot-v1-8k"
            elif provider == "qwen":
                base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
                model_name = model_name or "qwen-plus"

            client = OpenAI(api_key=api_key, base_url=base_url)
            res = client.chat.completions.create(
                model=model_name or "gpt-4o-mini",
                messages=[{"role": "user", "content": common_prompt}]
            )
            return res.choices[0].message.content

    except Exception as e:
        # 모든 시도가 실패하면 로그만 남기고 조용히 처리
        print(f"[AI Error] {provider} failure: {str(e)}")

    # 최종 폴백: 에러 코드 대신 사용자 친화적인 안내 문구 반환
    return schedule_data + "\n\n💡 (안내: 현재 AI 서버가 매우 혼잡하여 기본 일정을 우선 전송합니다. 잠시 후 새로고침하시면 AI 요약이 활성화될 수 있습니다.)"

if __name__ == "__main__":
    test_data = "## 정보자원 AI 알림이 - 2026년 02월 23일\n- [작업] 서버 점검 (상태: 진행중, 팀: 인프라팀)\n- [일정] 주간 회의 (상태: 예정, 팀: 기획팀)"
    print(generate_ai_summary(test_data))
