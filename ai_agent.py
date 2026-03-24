from dotenv import load_dotenv
import os

def generate_ai_summary(schedule_data, d_day_str):
    """
    다양한 AI 프로바이더를 지원하며, 서버 오류 시 깔끔하게 기본 내용을 반환하는 튼튼한 요약 함수입니다.
    """
    load_dotenv()
    
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    api_key = os.getenv("AI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    # 디버깅용 로그 (Vercel 로그에서 확인 가능)
    print(f"[Debug] Provider detected: {provider}")
    print(f"[Debug] API Key set: {'Yes' if api_key else 'No'}")

    # AI 설정이 없으면 즉시 요약 없이 원본+D-Day 반환
    if not api_key:
        footer = f"\n\n[사업완료일까지 {d_day_str}]"
        return schedule_data + footer

    common_prompt = f"""
다음 일정을 핵심만 뽑아 아주 간결한 불렛포인트로 요약해 주세요. 

[데이터]
{schedule_data}

[작성 규칙 - 반드시 지킬 것]
1. 최상단에 "정보자원사업단 AI 알림이" 문구를 넣으세요.
2. 그 바로 아래에 "제목 : [요약된 제목]" 형식을 넣으세요.
3. 중간에는 핵심 내용만 3~5줄 내외로 간결하게 요약하세요.
4. 마지막 줄에 "[사업완료일까지 {d_day_str}]" 문구를 넣으며 마무리하세요.
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
    footer = f"\n\n[사업완료일까지 {d_day_str}]"
    return schedule_data + footer

if __name__ == "__main__":
    test_data = "## 정보자원 AI 알림이 - 2026년 02월 23일\n- [작업] 서버 점검 (상태: 진행중, 팀: 인프라팀)\n- [일정] 주간 회의 (상태: 예정, 팀: 기획팀)"
    print(generate_ai_summary(test_data))
