import requests
import os
import json
from datetime import datetime

def get_notion_headers():
    token = os.getenv("NOTION_API_KEY", "").strip()
    db_id = os.getenv("NOTION_DATABASE_ID", "").strip()
    
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
        print(f"[Notion] Missing config - DB_ID: {database_id}, Headers: {'Present' if headers else 'Missing'}")
        # 폴백: 환경변수가 없으면 로컬 파일(있다면) 또는 빈 리스트 반환
        return []

    print(f"[Notion] Querying database: {database_id}")

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
        
        # 만약 필터링된 결과가 없으면 전체 데이터를 가져와서 수동 필터링 시도 (Notion 필터 속성 불일치 대비)
        if not results:
            print("[Notion] No results with group filter. Trying secondary fetch without filter.")
            res_all = requests.post(url, headers=headers, json={})
            if res_all.status_code == 200:
                results = res_all.json().get("results", [])

        recipients = []
        for page in results:
            props = page.get("properties", {})
            try:
                # 상태 확인 (status 또는 select)
                status_prop = props.get("상태", {})
                status_type = status_prop.get("type")
                status_value = ""
                if status_type == "status":
                    status_value = status_prop.get("status", {}).get("name", "")
                elif status_type == "select":
                    status_value = status_prop.get("select", {}).get("name", "")
                
                # '완료' 상태가 아니면 건너뜀 (수동 필터링 시)
                if status_value != "완료":
                    continue

                name = props.get("이름", {}).get("title", [{}])[0].get("plain_text", "Unknown")
                access_token = props.get("텍스트", {}).get("rich_text", [{}])[0].get("plain_text", "")
                refresh_token = props.get("텍스트 1", {}).get("rich_text", [{}])[0].get("plain_text", "")
                
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
        print(f"[Notion] Fetch failed: {msg := getattr(e, 'response', None) and e.response.text or str(e)}")
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
