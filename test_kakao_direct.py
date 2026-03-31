import requests
import json
import os

token_path = r'd:\park-ai\app\day_noti\kakao_token.json'
with open(token_path, 'r') as f:
    tokens = json.load(f)

url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
headers = {
    'Authorization': 'Bearer ' + tokens['access_token']
}
template = {
    'object_type': 'text',
    'text': '함장님, 로컬 기지에서 정밀 타격한 카카오톡 테스트 메시지입니다. 수신 성공 시 즉시 응답 바랍니다! ⚓️🎯',
    'link': {'web_url': 'https://localhost', 'mobile_web_url': 'https://localhost'}
}
data = {
    'template_object': json.dumps(template)
}
res = requests.post(url, headers=headers, data=data)
print(res.json())
