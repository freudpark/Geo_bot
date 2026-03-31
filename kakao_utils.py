import requests
import json
import os

def load_tokens():
    env_token = os.getenv("KAKAO_TOKEN_JSON")
    if env_token:
        try: return json.loads(env_token)
        except: pass
    token_path = os.path.join(os.path.dirname(__file__), "kakao_token.json")
    if not os.path.exists(token_path):
        raise FileNotFoundError("Token file missing.")
    with open(token_path, "r") as fp: return json.load(fp)

def refresh_kakao_token(refresh_token, client_id):
    url = "https://kauth.kakao.com/oauth/token"
    data = {"grant_type": "refresh_token", "client_id": client_id, "refresh_token": refresh_token}
    res = requests.post(url, data=data).json()
    if "access_token" in res:
        if "refresh_token" not in res: res["refresh_token"] = refresh_token
        return res
    return None

def send_kakao_text(access_token, text):
    """이미지 전송 실패 시 텍스트 리스트 템플릿으로 전송"""
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    template = {
        "object_type": "text",
        "text": f"💎 [PyhgoShift] 정보자원 알림\n\n{text[:180]}...",
        "link": {"web_url": "https://localhost", "mobile_web_url": "https://localhost"},
        "button_title": "상세 확인"
    }
    res = requests.post(url, headers=headers, data={"template_object": json.dumps(template)})
    return res.json()

def send_image_message(access_token, image_url, text):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    template = {
        "object_type": "feed",
        "content": {
            "title": "정보자원 Daily 알림",
            "description": text[:40] + "...",
            "image_url": image_url,
            "link": {"web_url": "https://localhost", "mobile_web_url": "https://localhost"}
        }
    }
    res = requests.post(url, headers=headers, data={"template_object": json.dumps(template)})
    return res.json()

def send_to_all_recipients(text, image_url=None):
    from notion_utils import get_recipients
    recipients = get_recipients()
    client_id = os.getenv("KAKAO_CLIENT_ID")
    
    if not recipients:
        try:
            tokens = load_tokens()
            recipients = [{"name": "함장님", "access_token": tokens["access_token"], "refresh_token": tokens.get("refresh_token"), "page_id": None}]
        except: return [{"error": "No recipients"}]

    results = []
    for r in recipients:
        print(f"[Kakao] Sending to {r['name']}...")
        if image_url:
            res = send_image_message(r['access_token'], image_url, text)
        else:
            # 이미지 없으면 텍스트로 발송
            res = send_kakao_text(r['access_token'], text)
        
        # 만료 시 리프레시
        if isinstance(res, dict) and res.get("code") == -401 and r.get("refresh_token") and client_id:
            new_tokens = refresh_kakao_token(r['refresh_token'], client_id)
            if new_tokens:
                if r['page_id']:
                    from notion_utils import update_recipient_tokens
                    update_recipient_tokens(r['page_id'], new_tokens)
                res = send_image_message(new_tokens["access_token"], image_url, text) if image_url else send_kakao_text(new_tokens["access_token"], text)
        results.append({"name": r['name'], "result": res})
    return results
