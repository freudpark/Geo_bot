import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# d:/park-ai/app/day_noti/.env 또는 환경 변수 사용
load_dotenv()

def diagnostic_test():
    token = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_DATABASE_ID")
    kakao_client_id = os.getenv("KAKAO_CLIENT_ID")
    
    print("=== [1] Environment Variables Check ===")
    print(f"NOTION_API_KEY: {'Set' if token else 'NOT SET'}")
    print(f"NOTION_DATABASE_ID: {'Set' if db_id else 'NOT SET'}")
    print(f"KAKAO_CLIENT_ID: {'Set' if kakao_client_id else 'NOT SET'}")
    
    if not token or not db_id:
        print("\n[Error] Notion API Key or Database ID is missing. Please check your environment variables.")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 1. DB 정보 조회
    print("\n=== [2] Notion Database Schema Check ===")
    url_db = f"https://api.notion.com/v1/databases/{db_id}"
    res_db = requests.get(url_db, headers=headers)
    
    if res_db.status_code == 200:
        props = res_db.json().get("properties", {})
        print(f"DB Title: {res_db.json().get('title', [{}])[0].get('plain_text', 'No Title')}")
        print("Properties found:")
        for name, p in props.items():
            st_info = ""
            if p.get('type') == 'status':
                options = [o.get('name') for o in p.get('status', {}).get('options', [])]
                st_info = f" (Options: {options})"
            elif p.get('type') == 'select':
                options = [o.get('name') for o in p.get('select', {}).get('options', [])]
                st_info = f" (Options: {options})"
            print(f"- {name} ({p.get('type')}){st_info}")
    else:
        print(f"Error fetching DB: {res_db.status_code} - {res_db.text}")
        return

    # 2. 수신자 명단 조회
    print("\n=== [3] Recipient Data Check ===")
    url_query = f"https://api.notion.com/v1/databases/{db_id}/query"
    # 필터 없이 전체 조회
    res_query = requests.post(url_query, headers=headers, json={})
    
    if res_query.status_code == 200:
        results = res_query.json().get("results", [])
        print(f"Found {len(results)} entries in DB.")
        for page in results:
            props = page.get("properties", {})
            name = props.get("이름", {}).get("title", [{}])[0].get("plain_text", "Unknown")
            
            # 상태 추출
            status = "N/A"
            st_prop = props.get("상태", {})
            if st_prop.get("type") == "status":
                status = st_prop.get("status", {}).get("name")
            elif st_prop.get("type") == "select":
                status = st_prop.get("select", {}).get("name")
            
            # 토큰 존재 여부
            access_tok = props.get("텍스트", {}).get("rich_text", [{}])[0].get("plain_text", "")
            has_token = "Yes" if access_tok else "No"
            
            print(f"- Name: {name}, Status: {status}, Token Set: {has_token}")
            
            # 토큰 유효성 테스트 (첫 번째 유효한 토큰인 경우)
            if access_tok:
                print(f"  Testing Kakao token for {name}...")
                k_url = "https://kapi.kakao.com/v1/user/ids"
                k_headers = {"Authorization": f"Bearer {access_tok}"}
                k_res = requests.get(k_url, headers=k_headers)
                if k_res.status_code == 200:
                    print(f"  ✅ Token is valid. ID: {k_res.json().get('id')}")
                else:
                    print(f"  ❌ Token invalid/expired: {k_res.status_code} - {k_res.text}")
    else:
        print(f"Error querying data: {res_query.status_code} - {res_query.text}")

if __name__ == "__main__":
    diagnostic_test()
