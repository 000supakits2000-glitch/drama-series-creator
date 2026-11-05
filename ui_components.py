CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');

footer {visibility: hidden}

/* พื้นหลังและฟอนต์หลัก */
body, .gradio-container {
    background-image: linear-gradient(135deg, rgba(9, 13, 22, 0.45) 0%, rgba(15, 23, 42, 0.40) 50%, rgba(17, 24, 39, 0.45) 100%),
                        url('https://raw.githubusercontent.com/000supakits2000-glitch/drama-series-creator/main/bg-drama.png') !important;
    background-size: 100% 100% !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    font-family: 'Prompt', sans-serif !important;
    color: #f8fafc !important;
}

.main-container { 
    max-width: 1250px !important; 
    margin: auto !important; 
    padding: 20px !important; 
    font-family: 'Prompt', sans-serif !important; 
}

.header-box {
    text-align: center;
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(49, 46, 129, 0.85) 50%, rgba(67, 56, 202, 0.85) 100%);
    padding: 30px 20px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 12px 30px -8px rgba(99, 102, 241, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(8px);
    font-family: 'Prompt', sans-serif !important;
}

.header-title {
    color: #ffffff !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    margin-bottom: 8px !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    font-family: 'Prompt', sans-serif !important;
}

.header-subtitle {
    color: #cbd5e1 !important;
    font-size: 1.1rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.2px;
    font-family: 'Prompt', sans-serif !important;
}

.unified-card {
    background: rgba(15, 23, 42, 0.78) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 20px 30px -5px rgba(0, 0, 0, 0.6), 0 10px 15px -5px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(12px);
    overflow: visible !important;
}

label span, div[data-testid="block-label"] span { 
    color: #38bdf8 !important; 
    font-weight: 600 !important; 
    font-family: 'Prompt', sans-serif !important; 
}

/* บังคับปุ่มคู่ล่างสุดกว้าง 50/50 และแต่งสีสวยงาม */
.primary-btn, .secondary-btn, 
.primary-btn button, .secondary-btn button {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

.primary-btn button, .secondary-btn button {
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 12px 24px !important;
    border-radius: 12px !important;
    font-family: 'Prompt', sans-serif !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    transition: all 0.3s ease !important;
}

.primary-btn button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
}

.primary-btn button:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%) !important;
    transform: translateY(-1px);
}

.secondary-btn button {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
    border: 1px solid rgba(244, 63, 94, 0.4) !important;
    color: #fca5a5 !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

.secondary-btn button:hover {
    background: linear-gradient(135deg, #334155 0%, #1e293b 100%) !important;
    border-color: rgba(244, 63, 94, 0.8) !important;
    color: #fee2e2 !important;
    transform: translateY(-1px);
}

.admin-btn {
    background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%) !important;
    border: none !important; color: white !important; font-weight: 700 !important;
    font-size: 1.05rem !important; padding: 10px 20px !important; border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
    font-family: 'Prompt', sans-serif !important;
}

.tab-nav button {
    color: #cbd5e1 !important;
    font-family: 'Prompt', sans-serif !important;
    font-weight: 600 !important;
}

.tab-nav button.selected {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}

/* จัดการกล่องดรอปดาวน์ ระยะห่าง และตำแหน่งพอดีเป๊ะ */
.gr-dropdown {
    position: relative !important;
    z-index: 100 !important;
}

.gr-dropdown ul, .gr-dropdown-options, .options, div[role="listbox"] {
    position: absolute !important;
    top: 100% !important;
    left: 0 !important;
    width: 100% !important;
    margin-top: 6px !important;
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #475569 !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.8) !important;
    z-index: 999999 !important;
}

.gr-dropdown ul li, .gr-dropdown-options li, .options li, div[role="option"] {
    background-color: #1e293b !important;
    color: #ffffff !important;
    padding: 10px 14px !important;
}

.gr-dropdown ul li:hover, .gr-dropdown-options li:hover, .options li:hover, div[role="option"]:hover {
    background-color: #334155 !important;
    color: #38bdf8 !important;
}

.gradio-container, .block, .form, .gr-form, .gr-row, .gr-column {
    overflow: visible !important;
}

.auth-status {
    text-align: center !important;
    color: #00ffcc !important; /* สีเขียวมิ้นต์เรืองแสง สดใส เด่นชัด */
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    margin-bottom: 15px !important;
    text-shadow: 0 2px 5px rgba(0, 0, 0, 0.9) !important;
    width: 100% !important;
}

.auth-status:empty {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
}
"""
