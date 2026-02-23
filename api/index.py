from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # UI HTML Content
        html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyhgoShift Info Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Pretendard', sans-serif; background: #0f172a; color: #f8fafc; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .gradient-text { background: linear-gradient(45deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .btn-primary { background: linear-gradient(45deg, #0ea5e9, #6366f1); transition: all 0.3s ease; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }
        .pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">
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
                    <span class="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded-full px-3">Status: Active</span>
                </div>
                <p class="text-slate-400 text-sm">지금 바로 구글 시트 정보를 읽어와서 카카오톡으로 전송합니다.</p>
                <button id="runBtn" class="w-full py-4 rounded-2xl btn-primary font-bold text-lg flex items-center justify-center gap-2">
                    지금 바로 알림 보내기
                </button>
                <div id="result" class="hidden p-4 rounded-xl bg-slate-800/50 text-sm border border-slate-700"></div>
            </div>

            <div class="h-px bg-slate-700/50"></div>

            <!-- Schedule Section -->
            <div class="space-y-4">
                <h2 class="text-xl font-semibold flex items-center gap-2">
                    <span class="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">⏰</span>
                    자동 알림 시간 설정
                </h2>
                <p class="text-slate-400 text-sm">매일 정해진 시간에 자동으로 알림을 보냅니다. (한국 시간 기준)</p>
                
                <div class="flex gap-4 items-center">
                    <input type="time" id="shTime" value="09:00" class="flex-1 bg-slate-900 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-sky-500 outline-none">
                    <button onclick="updateCron()" class="bg-slate-700 hover:bg-slate-600 px-6 py-3 rounded-xl font-semibold transition-colors">설정 적용</button>
                </div>

                <div id="cronGuide" class="hidden space-y-3 mt-4">
                    <div class="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-200 text-sm">
                        <p class="font-bold mb-1">⚠️ 주의사항</p>
                        Vercel 시스템 특성상 화면에서 즉시 변경은 불가능합니다. 아래 코드를 <strong>vercel.json</strong>의 schedule 부분에 붙여넣고 Push해 주세요.
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
        document.getElementById('runBtn').onclick = async () => {
            const btn = document.getElementById('runBtn');
            const resDiv = document.getElementById('result');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="pulse">🚀 발송 중...</span>';
            resDiv.classList.add('hidden');

            try {
                const res = await fetch('/api/cron');
                const text = await res.text();
                resDiv.innerHTML = '✅ ' + text;
                resDiv.classList.remove('hidden', 'bg-red-500/10', 'border-red-500/30');
                resDiv.classList.add('bg-emerald-500/10', 'border-emerald-500/30', 'text-emerald-200');
            } catch (e) {
                resDiv.innerHTML = '❌ 오류: ' + e.message;
                resDiv.classList.remove('hidden', 'bg-emerald-500/10', 'border-emerald-500/30');
                resDiv.classList.add('bg-red-500/10', 'border-red-500/30', 'text-red-200');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '지금 바로 알림 보내기';
            }
        };

        function updateCron() {
            const time = document.getElementById('shTime').value;
            const guide = document.getElementById('cronGuide');
            const [h, m] = time.split(':');
            
            // UTC 변환 (-9시간)
            let utc_h = parseInt(h) - 9;
            if (utc_h < 0) utc_h += 24;
            
            document.getElementById('cronResult').innerText = `${m} ${utc_h} * * *`;
            guide.classList.remove('hidden');
        }
    </script>
</body>
</html>
        """
        self.wfile.write(html.encode('utf-8'))
        return
