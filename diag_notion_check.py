import os
import requests
import json
from dotenv import load_dotenv

# d:/park-ai/app/day_noti/.env 또는 환경 변수 사용
load_dotenv()

def diag_notion():
    token = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_DATABASE_ID")
    
    print(f"Token: {token[:10]}...")
    print(f"DB ID: {db_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 1. DB 정보 조회
    url_db = f"https://api.notion.com/v1/databases/{db_id}"
    res_db = requests.get(url_db, headers=headers)
    print("\n--- DB Schema ---")
    print(res_db.status_code)
    if res_db.status_code == 200:
        props = res_db.json().get("properties", {})
        for name, p in props.items():
            print(f"Property: {name}, Type: {p.get('type')}")
            if p.get('type') == 'status':
                options = [o.get('name') for o in p.get('status', {}).get('options', [])]
                print(f"  Options: {options}")
    else:
        print(res_db.text)
        return

    # 2. 데이터 조회 (필터 없이)
    url_query = f"https://api.notion.com/v1/databases/{db_id}/query"
    res_query = requests.post(url_query, headers=headers, json={})
    print("\n--- DB Data (All) ---")
    if res_query.status_code == 200:
        results = res_query.json().get("results", [])
        print(f"Total entries found: {len(results)}")
        for page in results:
            props = page.get("properties", {})
            name = props.get("이름", {}).get("title", [{}])[0].get("plain_text", "Unknown")
            status = ""
            st_prop = props.get("상태", {})
            if st_prop.get("type") == "status":
                status = st_prop.get("status", {}).get("name")
            print(f"- {name}: Status={status}")
    else:
        print(res_query.text)

if __name__ == "__main__":
    diag_notion()
