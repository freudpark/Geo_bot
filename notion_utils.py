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
            "property": "Status",
            "select": {
                "equals": "Active"
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
                name = props.get("Name", {}).get("title", [{}])[0].get("plain_text", "Unknown")
                access_token = props.get("Access Token", {}).get("rich_text", [{}])[0].get("plain_text", "")
                refresh_token = props.get("Refresh Token", {}).get("rich_text", [{}])[0].get("plain_text", "")
                
                if access_token:
                    recipients.append({
                        "name": name,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "page_id": page.get("id")
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
    
    if not database_id or not headers:
        return False

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {"title": [{"text": {"content": name}}]},
            "Access Token": {"rich_text": [{"text": {"content": tokens.get("access_token", "")}}]},
            "Refresh Token": {"rich_text": [{"text": {"content": tokens.get("refresh_token", "")}}]},
            "Status": {"select": {"name": "Active"}},
            "Updated At": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"[Notion] Error Response: {response.text}")
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[Notion] Add recipient failed: {e}")
        return False

def update_recipient_tokens(page_id, tokens):
    headers = get_notion_headers()
    if not headers:
        return False

    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "Access Token": {"rich_text": [{"text": {"content": tokens.get("access_token", "")}}]},
            "Refresh Token": {"rich_text": [{"text": {"content": tokens.get("refresh_token", "")}}]},
            "Updated At": {"date": {"start": datetime.now().isoformat()}}
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[Notion] Update tokens failed: {e}")
        return False
