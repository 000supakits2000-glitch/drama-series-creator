CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');

footer {visibility: hidden}

/* 🌟 ปรับขนาดภาพพื้นหลังให้เล็กลงมาอีกหน่อย (85% width) เพื่อให้เห็นตัวละครครบทุกมุม ไม่ซูมจนล้นจอ */
body, .gradio-container {
    background: linear-gradient(135deg, rgba(9, 13, 22, 0.45) 0%, rgba(15, 23, 42, 0.40) 50%, rgba(17, 24, 39, 0.45) 100%),
                url('https://raw.githubusercontent.com/000supakits2000-glitch/drama-series-creator/main/bg-drama.png') !important;
    background-size: 85% auto !important;
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

/* กรอบการ์ดใหญ่โปร่งแสงโมเดิร์น */
.unified-card {
    background: rgba(15, 23, 42, 0.78) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 20px 30px -5px rgba(0, 0, 0, 0.6), 0 10px 15px -5px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(12px);
}

/* สีหัวข้อและป้าย Label */
.auth-title h3, .auth-title span, .welcome-text h3 {
    color: #38bdf8 !important;
    font-family: 'Prompt', sans-serif !important;
    font-weight: 700 !important;
}

label span, div[data-testid="block-label"] span { 
    color: #38bdf8 !important; 
    font-weight: 600 !important; 
    font-family: 'Prompt', sans-serif !important; 
}

.primary-btn {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important; color: white !important; font-weight: 700 !important;
    font-size: 1.1rem !important; padding: 12px 24px !important; border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    font-family: 'Prompt', sans-serif !important;
}

.admin-btn {
    background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%) !important;
    border: none !important; color: white !important; font-weight: 700 !important;
    font-size: 1.05rem !important; padding: 10px 20px !important; border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
    font-family: 'Prompt', sans-serif !important;
}
"""
