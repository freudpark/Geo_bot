# 🤖 Geo_bot: 정보자원 AI 일시 알림이

구글 시트의 복잡한 일정을 분석하여, 매일 아침 카카오톡으로 스마트한 AI 요약 리포트를 배달해주는 지능형 헬퍼 시스템입니다.

---

## 🚀 주요 기능

### 1. 자동 데이터 동기화
*   매일 아침 구글 시트(GEO_JobList)에서 최신 일정을 자동으로 다운로드합니다.
*   병합 셀이나 비정형 데이터 구조를 견고하게 분석하는 지능형 파싱 엔진을 탑재했습니다.

### 2. Gemini AI 기반 스마트 요약
*   단순한 일정 나열이 아닌, **Google Gemini 1.5 Flash**를 사용하여 읽기 좋은 뉴스 리포트 스타일로 요약을 생성합니다.
*   일정의 중요도와 맥락을 파악하여 사용자에게 필요한 통찰을 제공합니다.

### 3. 카카오톡 연동 자동 알림
*   요약된 내용을 카카오톡 '나에게 보내기'를 통해 즉시 전송합니다.
*   Vercel Cron Jobs를 활용하여 서버 없이 24시간 자동화 운영이 가능합니다.

---

## 🛠 기술 스택

*   **Language**: Python 3.x
*   **Data Processing**: Pandas
*   **AI Engine**: Google GenAI (Gemini)
*   **Infrastructure**: Vercel (Serverless Functions, Cron Jobs)
*   **Integration**: KakaoTalk Message API, Google Sheets CSV

---

## 📦 설치 및 설정

### 1. 환경 변수 설정
클라우드 배포(Vercel) 시 다음 환경 변수 설정이 필요합니다.

| 변수명 | 설명 | 비고 |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google AI Studio에서 발급받은 API 키 | [발급받기](https://aistudio.google.com/) |
| `KAKAO_TOKEN_JSON` | `kakao_token.json` 파일의 JSON 내용 전체 | 텍스트 형태로 복사 |

### 2. 로컬 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성 및 키 입력
echo "GEMINI_API_KEY=your_key_here" > .env

# 실행
python run_daily_alert.py
```

---

## 🌐 배포 가이드 (Vercel)

1.  이 저장소를 자신의 GitHub로 Fork 또는 Push합니다.
2.  Vercel에서 **New Project**를 생성하고 GitHub 저장소를 연결합니다.
3.  **Environment Variables** 탭에서 위의 필수 변수들을 등록합니다.
4.  배포 완료 후, 매일 한국 시간 오전 9시에 `/api/cron` 엔드포인트가 자동으로 호출되어 알림이 전송됩니다.

---

## 👨‍💻 프로젝트 관리 (The 7 Parks)

이 프로젝트는 **파이고시프트(PyhgoShift)** 프로젝트의 일환으로 구축되었습니다.
*   **Pilot Park**: 전체 설계 및 항로 설정
*   **Innovator Park**: AI 로직 및 데이터 파싱 구현
*   **Synapse Park**: 클라우드 인프라 및 API 연결

---

## 📄 라이선스
MIT License
