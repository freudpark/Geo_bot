import requests
import os
import json
from datetime import datetime

def get_notion_headers():
    token = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_DATABASE_ID")
    
    print(f"[Notion] Auth Check - API_KEY: {'Set' if token else 'NOT SET'}, DB_ID: {'Set' if db_id else 'NOT SET'}")
    if token:
        print(f"[Notion] Token Preview: {token[:7]}...{token[-4:] if len(token) > 10 else ''}")

    if not token:
        return None
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

def get_recipients():
    database_id = os.getenv("NOTION_DATABASE_ID")
    headers = get_notion_headers()
    
    if not database_id or not headers:
        # 폴백: 환경변수가 없으면 로컬 파일(있다면) 또는 빈 리스트 반환
        return []

    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {
        "filter": {
            "property": "상태",
            "status": {
                "equals": "완료"
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        recipients = []
        for page in results:
            props = page.get("properties", {})
            try:
                # 한국어 컬럼명 매핑: 이름, 텍스트(Access), 텍스트 1(Refresh), 상태, 날짜
                name = props.get("이름", {}).get("title", [{}])[0].get("plain_text", "Unknown")
                access_token = props.get("텍스트", {}).get("rich_text", [{}])[0].get("plain_text", "")
                refresh_token = props.get("텍스트 1", {}).get("rich_text", [{}])[0].get("plain_text", "")
                
                # 상태는 '상태' 또는 'Status' 확인 (기본적으로 '상태' 사용)
                status_prop = props.get("상태", {})
                status_type = status_prop.get("type")
                status_value = ""
                if status_type == "status":
                    status_value = status_prop.get("status", {}).get("name", "")
                elif status_type == "select":
                    status_value = status_prop.get("select", {}).get("name", "")

                if access_token:
                    recipients.append({
                        "name": name,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "page_id": page.get("id"),
                        "status": status_value
                    })
            except Exception as e:
                print(f"[Notion] Error parsing page {page.get('id')}: {e}")
                
        return recipients
    except Exception as e:
        print(f"[Notion] Fetch failed: {e}")
        return []

def add_recipient(name, tokens):
    database_id = os.getenv("NOTION_DATABASE_ID")
    headers = get_notion_headers()
    
    if not database_id:
        return False, "NOTION_DATABASE_ID is not set in environment variables."
    if not headers:
        return False, "Notion API Key is missing or invalid."

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "이름": {"title": [{"text": {"content": name}}]},
            "텍스트": {"rich_text": [{"text": {"content": tokens.get("access_token", "")}}]},
            "텍스트 1": {"rich_text": [{"text": {"content": tokens.get("refresh_token", "")}}]},
            "상태": {"status": {"name": "완료"}}, # 사용자 DB의 '완료' 옵션 사용
            "날짜": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get("message", response.text)
            print(f"[Notion] Error Response: {error_msg}")
            return False, f"Notion API Error: {error_msg}"
        
        response.raise_for_status()
        return True, "Success"
    except Exception as e:
        print(f"[Notion] Add recipient failed: {e}")
        return False, str(e)

def update_recipient_tokens(page_id, tokens):
    headers = get_notion_headers()
    if not headers:
        return False

    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "텍스트": {"rich_text": [{"text": {"content": tokens.get("access_token", "")}}]},
            "텍스트 1": {"rich_text": [{"text": {"content": tokens.get("refresh_token", "")}}]},
            "날짜": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[Notion] Update tokens failed: {e}")
        return False
