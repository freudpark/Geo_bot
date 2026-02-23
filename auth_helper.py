import webbrowser
from kakao_utils import get_access_token

def authenticate():
    print("=== 카카오 인증 도우미 (KOE101 해결 모드) ===")
    print("1. [카카오 개발자 콘솔] > [내 애플리케이션] > [앱 선택] > [앱 키]로 이동하세요.")
    print("2. 'REST API 키'를 복사해서 아래에 입력해 주세요.")
    
    client_id = input("\nREST API 키 입력: ").strip()
    if not client_id:
        print("키가 입력되지 않았습니다.")
        return

    redirect_uri = "https://localhost"
    
    # 1. 인증 코드 발급 URL 생성
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    
    print("\n3. 아래 링크를 브라우저에서 열고 로그인을 진행해 주세요.")
    print(auth_url)
    print("\n4. 로그인이 완료되면 브라우저 주소창이 'https://localhost/?code=...'와 같이 바뀝니다.")
    print("5. 주소창에 있는 'code=' 뒷부분의 긴 문자열을 복사해서 여기에 입력해 주세요.")
    
    # 브라우저 자동 실행 시도
    try:
        import webbrowser
        webbrowser.open(auth_url)
    except:
        pass
        
    auth_code = input("\n인증 코드(code) 입력: ").strip()
    
    if auth_code:
        print("토큰 발급 중...")
        result = get_access_token(auth_code, client_id)
        if "access_token" in result:
            print("\n✅ 인증 성공!")
            print("kakao_token.json 파일이 생성되었습니다.")
            print("이제 이 파일의 내용을 복사해서 Vercel의 KAKAO_TOKEN_JSON 환경변수에 넣으시면 됩니다.")
        else:
            print("\n❌ 인증 실패")
            print(f"에러 내용: {result}")
    else:
        print("인증 코드가 입력되지 않았습니다.")

if __name__ == "__main__":
    authenticate()
