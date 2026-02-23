from http.server import BaseHTTPRequestHandler
import os
import sys

# 프로젝트 루트를 path에 추가하여 로컬 모듈 임포트 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_daily_alert import run

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 주 작업을 실행합니다.
            run()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("Daily alert executed successfully.".encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"Error executing daily alert: {str(e)}".encode('utf-8'))
