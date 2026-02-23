
import requests
import json
import os

def get_access_token(auth_code, client_id):
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": "https://localhost",
        "code": auth_code
    }
    response = requests.post(url, data=data)
    tokens = response.json()
    
    if "access_token" in tokens:
        # Vercel 환경이 아닐 때만 파일로 저장 (로컬 테스트용)
        if not os.getenv("VERCEL"):
            try:
                token_path = os.path.join(os.path.dirname(__file__), "kakao_token.json")
                with open(token_path, "w") as fp:
                    json.dump(tokens, fp)
            except Exception as e:
                print(f"[Kakao] Token save failed (expected on Vercel): {e}")
        return tokens
    else:
        return tokens

def load_tokens():
    # 1. 환경 변수에서 토큰 정보를 먼저 시도 (Vercel 등 클라우드 환경용)
    env_token = os.getenv("KAKAO_TOKEN_JSON")
    if env_token:
        try:
            return json.loads(env_token)
        except Exception:
            pass

    # 2. 파일 시스템에서 토큰 정보 시도
    token_path = os.path.join(os.path.dirname(__file__), "kakao_token.json")
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token file not found. Set KAKAO_TOKEN_JSON env or run auth.")
    with open(token_path, "r") as fp:
        return json.load(fp)

def send_message(access_token, text):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": "Bearer " + access_token
    }
    template = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://localhost",
            "mobile_web_url": "https://localhost"
        },
        "button_title": "일정 확인"
    }
    data = {
        "template_object": json.dumps(template)
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def send_to_all_recipients(text):
    from notion_utils import get_recipients
    recipients = get_recipients()
    
    # 노션 등록자가 없으면 기본 환경변수 토큰으로 본인에게 전송 시도
    if not recipients:
        print("[Kakao] No Notion recipients. Falling back to single token.")
        try:
            tokens = load_tokens()
            return [send_message(tokens["access_token"], text)]
        except:
            return [{"error": "No recipients found"}]

    results = []
    for r in recipients:
        print(f"[Kakao] Sending to {r['name']}...")
        res = send_message(r['access_token'], text)
        results.append({"name": r['name'], "result": res})
        
    return results

def send_message_to_me(text):
    """기존 코드 호환성을 위해 유지: 첫 번째 등록자 혹은 기본 토큰으로 전송"""
    results = send_to_all_recipients(text)
    return results[0] if results else {"error": "Failed"}

if __name__ == "__main__":
    # 이 부분은 테스트용입니다.
    # client_id = "4f7fb9d05e5268a4d420099b16a04dda"
    # auth_code = "CcEdVplxCT0EJn2xdqzx1e6bOGWPs3TD-szFUJxbJUIJT5CcRF_MRwAAAAQKFyIgAAABnH8-AHZtZc76WqiBKA"
    # print(get_access_token(auth_code, client_id))
    pass
