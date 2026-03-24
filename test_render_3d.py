
import sys
import os

# --- 3D 효과 및 빛 반사가 적용된 고도화된 HTML 템플릿 ---
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
            overflow: hidden;
            background: #020617; /* 더 깊은 심연의 블랙 */
        }}
        .scene {{
            width: 800px;
            height: 500px;
            display: flex;
            align-items: center;
            justify-content: center;
            perspective: 1000px; /* 3D 원근감 주입 */
        }}
        .card {{
            width: 560px; /* 30% 축소 (800 * 0.7) */
            height: 350px; /* 30% 축소 (500 * 0.7) */
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(25px);
            border-radius: 24px;
            padding: 24px;
            position: relative;
            transform: rotateY(-15deg) rotateX(10deg); /* 3D 틸트 효과 */
            box-shadow: 
                -20px 20px 50px rgba(0, 0, 0, 0.5),
                inset 1px 1px 0px rgba(255, 255, 255, 0.1);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        /* 빛 반사 효과 (Glossy Specular) */
        .card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                135deg,
                rgba(255, 255, 255, 0) 0%,
                rgba(255, 255, 255, 0) 45%,
                rgba(255, 255, 255, 0.08) 50%,
                rgba(255, 255, 255, 0) 55%,
                rgba(255, 255, 255, 0) 100%
            );
            transform: rotate(30deg);
            pointer-events: none;
        }}
        /* 유리 질감 눈부심 (Glare) */
        .glare {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="scene">
        <div class="card">
            <div class="glare"></div>
            
            <!-- Logo -->
            <div class="flex justify-between items-center mb-6">
                <div class="text-[#38bdf8] font-black text-sm tracking-tighter opacity-80">PyhgoShift</div>
                <div class="text-[#64748b] text-[10px] font-bold tracking-widest uppercase italic">Operational Intel</div>
            </div>
            
            <!-- Header -->
            <div class="text-center mb-6">
                <h1 class="text-2xl font-black bg-gradient-to-r from-[#38bdf8] via-[#818cf8] to-[#c084fc] bg-clip-text text-transparent tracking-tight">
                    정보자원 Daily 알림
                </h1>
                <p class="text-[#475569] text-xs font-bold mt-1 uppercase tracking-widest">2026.03.23 MON</p>
            </div>

            <!-- Content Container -->
            <div class="space-y-4 px-2">
                <div class="bg-white/5 rounded-xl p-4 border border-white/5 shadow-inner">
                    <p class="text-[#94a3b8] text-sm text-center italic mb-3">현재 등록된 일정이 없습니다.</p>
                    <div class="space-y-2 opacity-60">
                        <div class="flex items-center text-xs text-[#f8fafc]">
                            <span class="w-1.5 h-1.5 rounded-full bg-[#38bdf8] mr-2"></span>
                            대기 중인 시스템 작업 점검
                        </div>
                        <div class="flex items-center text-xs text-[#f8fafc]">
                            <span class="w-1.5 h-1.5 rounded-full bg-[#818cf8] mr-2"></span>
                            네트워크 보안 프로토콜 유지
                        </div>
                    </div>
                </div>
            </div>

            <!-- Global Footer -->
            <div class="absolute bottom-6 left-6 right-6 flex justify-between items-end border-t border-white/5 pt-4">
                <div class="flex flex-col space-y-1">
                    <span class="text-[8px] text-[#475569] font-bold uppercase tracking-widest leading-none">Status Report</span>
                    <div class="flex items-center space-x-1.5">
                        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></div>
                        <span class="text-[10px] text-emerald-400 font-black tracking-tighter">SECURED ONLINE</span>
                    </div>
                </div>
                <div class="text-right">
                    <span class="text-[8px] text-[#475569] font-bold uppercase tracking-widest leading-none">Deadline</span>
                    <div class="text-2xl font-black bg-gradient-to-t from-[#f43f5e] to-[#fb7185] bg-clip-text text-transparent tracking-tighter leading-none">D-81</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# HTML을 임시 파일로 저장
with open('temp_3d.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Node.js 렌더링 스크립트 (3D 렌더링 최적화)
node_script = """
const nodeHtmlToImage = require('node-html-to-image')
const fs = require('fs')

const html = fs.readFileSync('temp_3d.html', 'utf8')

nodeHtmlToImage({
  output: './alert_card_3d.png',
  html: html,
  transparent: true,
  puppeteerArgs: {
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--force-device-scale-factor=2'] 
  }
}).then(() => console.log('3D Image created successfully!'))
"""

with open('render_3d.js', 'w', encoding='utf-8') as f:
    f.write(node_script)

print("Starting 3D Glassmorphism Rendering Engine...")
os.system("node render_3d.js")
