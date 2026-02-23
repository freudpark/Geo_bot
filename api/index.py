from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        message = """
        <html>
        <head><title>Geo_bot Status</title></head>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h1>🤖 Geo_bot is Running!</h1>
            <p>정보자원 AI 일시 알림이 서버가 정상 작동 중입니다.</p>
            <p>자동 알림 설정된 시간에 카카오톡으로 메시지가 발송됩니다.</p>
            <hr style="width: 300px;">
            <p style="color: gray;">Vercel Serverless Function</p>
        </body>
        </html>
        """
        self.wfile.write(message.encode('utf-8'))
        return
