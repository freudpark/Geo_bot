
import sys
import os

# --- 배경을 제거한 '오리지널 유리 사각형' 템플릿 ---
html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700;900&display=swap');
        body {{ 
            font-family: 'Pretendard', sans-serif; 
            margin: 0; 
            padding: 0; 
            background: #0f172a; /* 배경 무늬 없는 깔끔한 다크 딥 블루 */
            display: flex;
            align-items: center;
            justify-content: center;
            width: 800px;
            height: 800px;
        }}
        .glass-card {{
            width: 600px;
            height: 600px;
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(40px);
            border-radius: 60px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 50px 100px rgba(0, 0, 0, 0.6);
            padding: 40px;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        /* 상단 테두리 글로우 효과 */
        .glass-card::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, transparent, #38bdf8, transparent);
        }}
        .icon-box {{
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            margin-right: 12px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="glass-card">
        <!-- Title & Date -->
        <div class="text-center mb-12">
            <h1 class="text-[#f8fafc] text-4xl font-black mb-2 tracking-tight">PyhgoShift Daily Alert</h1>
            <p class="text-[#94a3b8] text-2xl font-bold tracking-widest">2026-03-23</p>
        </div>

        <!-- Content (Original Stats Style) -->
        <div class="flex-1 space-y-8 px-4">
            <div class="flex items-center text-2xl font-bold text-[#f8fafc]">
                <div class="icon-box bg-emerald-500/20 text-emerald-400">✓</div>
                <span>Tasks Completed: <span class="text-emerald-400">12 (80%)</span></span>
            </div>
            <div class="flex items-center text-2xl font-bold text-[#f8fafc]">
                <div class="icon-box bg-amber-500/20 text-amber-400">🕒</div>
                <span>Active Tasks: <span class="text-amber-400">4 (Pending Review)</span></span>
            </div>
            <div class="flex items-center text-2xl font-bold text-[#f8fafc]">
                <div class="icon-box bg-slate-500/20 text-slate-400">●</div>
                <span>High Priority: <span class="text-slate-200">2 (Unassigned)</span></span>
            </div>
            <div class="flex items-center text-2xl font-bold text-[#f8fafc]">
                <div class="icon-box bg-rose-500/20 text-rose-400">⚠️</div>
                <span>Overdue Items: <span class="text-rose-400">0 (No delays)</span></span>
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 py-8 border-t border-white/10 text-center">
            <p class="text-3xl font-black text-[#f8fafc] opacity-90">
                <span class="text-[#38bdf8]">D-81</span> to Project Completion
            </p>
        </div>
    </div>
</body>
</html>
"""

# HTML을 임시 파일로 저장
with open('original_glass.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Node.js 렌더링 스크립트 (깔끔한 사각형 렌더링)
node_script = """
const nodeHtmlToImage = require('node-html-to-image')
const fs = require('fs')

const html = fs.readFileSync('original_glass.html', 'utf8')

nodeHtmlToImage({
  output: './original_glass_card.png',
  html: html,
  puppeteerArgs: {
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  }
}).then(() => console.log('Original Glass Card created!'))
"""

with open('render_original.js', 'w', encoding='utf-8') as f:
    f.write(node_script)

print("Starting Original Glass Card Engine...")
os.system("node render_original.js")
