from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = json.loads(post_data)
        
        action = params.get("action")
        
        if action == "register":
            name = params.get("name")
            code = params.get("code")
            client_id = os.getenv("KAKAO_CLIENT_ID") or params.get("client_id")
            
            if not name or not code or not client_id:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing parameters"}).encode())
                return

            from kakao_utils import get_access_token
            from notion_utils import add_recipient
            
            # 1. 카카오 토큰 발급
            redirect_uri = params.get("redirect_uri", "https://localhost")
            tokens = get_access_token(code, client_id, redirect_uri)
            if "access_token" not in tokens:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Kakao Auth Failed: {tokens.get('error_description', 'unknown')}"}).encode())
                return
            
            # 2. 노션에 저장
            success, error_msg = add_recipient(name, tokens)
            
            if success:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Registration successful"}).encode())
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": error_msg}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        client_id_placeholder = os.getenv("KAKAO_CLIENT_ID", "")
        
        # UI HTML Content
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyhgoShift Info Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Pretendard', sans-serif; background: #0f172a; color: #f8fafc; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }}
        .gradient-text {{ background: linear-gradient(45deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .btn-primary {{ background: linear-gradient(45deg, #0ea5e9, #6366f1); transition: all 0.3s ease; }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }}
        .pulse {{ animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .5; }} }}
    </style>
</head>
<body class="min-h-screen py-12 px-4 flex flex-col items-center">
    <div class="max-w-2xl w-full space-y-8">
        <!-- Header -->
        <div class="text-center">
            <h1 class="text-5xl font-extrabold mb-2 gradient-text">PyhgoShift Info</h1>
            <p class="text-slate-400">지능형 자동화 일정 관리 시스템</p>
        </div>

        <!-- Main Card -->
        <div class="glass rounded-3xl p-8 shadow-2xl space-y-8">
            <!-- Alert Section -->
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <h2 class="text-xl font-semibold flex items-center gap-2">
                        <span class="p-2 bg-sky-500/20 rounded-lg text-sky-400">🚀</span>
                        수동 알림 발송
                    </h2>
                    <span class="text-xs text-slate-500 bg-slate-800 px-3 py-1 rounded-full">Status: Active</span>
                </div>
                <p class="text-slate-400 text-sm">등록된 모든 수신자에게 구글 시트 정보를 즉시 전송합니다.</p>
                <button id="runBtn" class="w-full py-4 rounded-2xl btn-primary font-bold text-lg flex items-center justify-center gap-2">
                    지금 바로 알림 보내기
                </button>
                <div id="result" class="hidden p-4 rounded-xl text-sm border"></div>
            </div>

            <div class="h-px bg-slate-700/50"></div>

            <!-- Recipient Management Section -->
            <div class="space-y-4">
                <h2 class="text-xl font-semibold flex items-center gap-2">
                    <span class="p-2 bg-emerald-500/20 rounded-lg text-emerald-400">👥</span>
                    수신자 추가 (Notion DB)
                </h2>
                <p class="text-slate-400 text-sm">카카오 인증을 통해 알림을 받을 사람을 추가합니다.</p>
                
                <div class="space-y-3 bg-slate-800/30 p-4 rounded-2xl border border-slate-700/50">
                    <div class="grid grid-cols-2 gap-3">
                        <input type="text" id="regName" placeholder="수신자 이름" class="bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none">
                        <input type="password" id="regClientId" value="{client_id_placeholder}" placeholder="REST API 키" class="bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none">
                    </div>
                    <div class="flex gap-3">
                        <button type="button" onclick="startKakaoAuth()" class="flex-1 bg-amber-400 hover:bg-amber-300 text-amber-900 py-3 rounded-xl font-bold text-sm transition-colors flex items-center justify-center gap-2">
                            1. 카카오 인증 창 열기
                        </button>
                    </div>
                    <p class="text-[10px] text-amber-500/80 text-center font-mono break-all" id="redirectHint">
                        카카오 설정용: <span id="hintUrl"></span>
                        <script>document.getElementById('hintUrl').innerText = window.location.origin;</script>
                    </p>
                    <div class="space-y-2">
                        <input type="text" id="regCode" placeholder="인증 완료 후 나타나는 code 입력" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm focus:ring-2 focus:ring-emerald-500 outline-none">
                        <button type="button" id="regBtn" onclick="registerRecipient()" class="w-full bg-slate-700 hover:bg-slate-600 py-3 rounded-xl font-bold text-sm transition-all border border-slate-600">
                            2. 수신자 등록 완료
                        </button>
                    </div>
                    <div id="regResult" class="hidden p-3 rounded-lg text-xs border text-center"></div>
                </div>
                <p class="text-[10px] text-slate-500 text-center">※ 등록된 명단은 Notion DB에서 직접 관리하실 수 있습니다.</p>
            </div>

            <div class="h-px bg-slate-700/50"></div>

            <!-- Schedule Section -->
            <div class="space-y-4">
                <h2 class="text-xl font-semibold flex items-center gap-2">
                    <span class="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">⏰</span>
                    자동 알림 시간 설정
                </h2>
                <div class="flex gap-4 items-center">
                    <input type="time" id="shTime" value="09:00" class="flex-1 bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-sky-500 outline-none">
                    <button onclick="updateCron()" class="bg-slate-700 hover:bg-slate-600 px-6 py-3 rounded-xl font-semibold transition-colors">변경</button>
                </div>

                <div id="cronGuide" class="hidden space-y-3 mt-4">
                    <div class="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-200 text-sm">
                        <p class="font-bold mb-1">⚠️ 주의사항</p>
                        <strong>vercel.json</strong>의 schedule 부분을 아래로 수정하고 Push해 주세요.
                    </div>
                    <div class="bg-black/50 p-4 rounded-xl font-mono text-emerald-400 text-sm break-all">
                        "schedule": "<span id="cronResult">0 0 * * *</span>"
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <p class="text-center text-slate-500 text-xs">
            Powered by PyhgoShift & The 7 Parks Group Intelligence
        </p>
    </div>

    <script>
        document.getElementById('runBtn').onclick = async () => {{
            const btn = document.getElementById('runBtn');
            const resDiv = document.getElementById('result');
            btn.disabled = true;
            btn.innerHTML = '<span class="pulse">🚀 발송 중...</span>';
            resDiv.classList.add('hidden');

            try {{
                const res = await fetch('/api/cron');
                const text = await res.text();
                resDiv.innerHTML = '✅ ' + text;
                resDiv.className = 'p-4 rounded-xl text-sm border bg-emerald-500/10 border-emerald-500/30 text-emerald-200';
            }} catch (e) {{
                resDiv.innerHTML = '❌ 오류: ' + e.message;
                resDiv.className = 'p-4 rounded-xl text-sm border bg-red-500/10 border-red-500/30 text-red-200';
            }} finally {{
                btn.disabled = false;
                btn.innerHTML = '지금 바로 알림 보내기';
            }};
        }};

        function startKakaoAuth() {{
            const clientId = document.getElementById('regClientId').value;
            if(!clientId) {{ alert('REST API 키를 입력해 주세요.'); return; }}
            const redirectUri = window.location.origin; 
            // 함장님께 정확한 주소를 한번 더 알림으로 보여드립니다.
            console.log('Using Redirect URI:', redirectUri);
            const url = `https://kauth.kakao.com/oauth/authorize?client_id=${{clientId}}&redirect_uri=${{encodeURIComponent(redirectUri)}}&response_type=code&scope=talk_message&prompt=login`;
            window.open(url, '_blank');
        }}

        async function registerRecipient() {{
            const name = document.getElementById('regName').value;
            const code = document.getElementById('regCode').value;
            const clientId = document.getElementById('regClientId').value;
            const resDiv = document.getElementById('regResult');
            const btn = document.getElementById('regBtn');

            if(!name || !code || !clientId) {{ alert('모든 필드를 입력해 주세요.'); return; }}

            btn.disabled = true;
            btn.innerText = '등록 중...';
            resDiv.classList.add('hidden');

            const redirectUri = window.location.origin;
            try {{
                const res = await fetch('/', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ action: 'register', name, code, client_id: clientId, redirect_uri: redirectUri }})
                }});
                const data = await res.json();
                if(res.ok) {{
                    resDiv.innerHTML = '✅ 등록 성공! 정해진 시간에 알림이 발송됩니다.';
                    resDiv.className = 'p-3 rounded-lg text-xs border text-center bg-emerald-500/10 border-emerald-500/30 text-emerald-200';
                    // 등록 성공 시 입력 필드 초기화
                    document.getElementById('regName').value = '';
                    document.getElementById('regCode').value = '';
                }} else {{
                    throw new Error(data.error);
                }}
            }} catch (e) {{
                resDiv.innerHTML = '❌ 실패: ' + e.message;
                resDiv.className = 'p-3 rounded-lg text-xs border text-center bg-red-500/10 border-red-500/30 text-red-200';
            }} finally {{
                resDiv.classList.remove('hidden');
                btn.disabled = false;
                btn.innerText = '2. 수신자 등록 완료';
            }}
        }}

        function updateCron() {{
            const time = document.getElementById('shTime').value;
            const guide = document.getElementById('cronGuide');
            const [h, m] = time.split(':');
            let utc_h = parseInt(h) - 9;
            if (utc_h < 0) utc_h += 24;
            document.getElementById('cronResult').innerText = `${{m}} ${{utc_h}} * * *`;
            guide.classList.remove('hidden');
        }}
    </script>
</body>
</html>
        """
        self.wfile.write(html.encode('utf-8'))
        return
