CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700;800&display=swap');

footer {visibility: hidden}

/* ดึงภาพผ่าน GitHub Raw URL ชัวร์ 100% ไม่ติดบล็อกของ Gradio */
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

/* จัดรูปแบบข้อความแจ้งเตือนสถานะให้เป็นฟอนต์และสีเดียวกับหัวข้อล็อกอิน */
.auth-status, .auth-status * {
    color: #38bdf8 !important;
    font-family: 'Prompt', sans-serif !important;
    font-weight: 600 !important;
}

/* จัดรูปแบบข้อความต้อนรับและเครดิตผู้ใช้ให้เป็นสีฟ้าและฟอนต์ Prompt เดียวกัน */
.welcome-text, .welcome-text * {
    color: #38bdf8 !important;
    font-family: 'Prompt', sans-serif !important;
    font-weight: 600 !important;
}

/* ตกแต่งหัวข้อ Tab ให้ตัวหนังสือชัดเจนบนพื้นหลังมืด */
.tab-nav button {
    color: #cbd5e1 !important;
    font-family: 'Prompt', sans-serif !important;
    font-weight: 600 !important;
}

/* สีของแท็บที่กำลังถูกเลือก (Active Tab) */
.tab-nav button.selected {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}

/* ตกแต่งหัวข้อ Tab ให้ตัวหนังสือชัดเจนบนพื้นหลังมืด */
.tab-nav button {
    color: #cbd5e1 !important;
    font-family: 'Prompt', sans-serif !important;
    font-weight: 600 !important;
}

/* สีของแท็บที่กำลังถูกเลือก (Active Tab) */
.tab-nav button.selected {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}

/* บังคับให้แถบเลื่อน Slider สามารถคลิกและลากได้ปกติ */
input[type="range"] {
    pointer-events: auto !important;
    cursor: pointer !important;
}

.gr-slider {
    pointer-events: auto !important;
}

/* ปลดล็อกให้กล่องการ์ดและฟอร์มแสดงผลเนื้อหาที่ลอยออกมาได้เต็มที่ ไม่โดนตัดขอบ */
.unified-card, .unified-card div {
    overflow: visible !important;
}

/* ล็อกตำแหน่งช่องดรอปดาวน์ */
.gr-dropdown {
    position: relative !important;
    z-index: 50 !important;
}

/* ให้รายการดรอปดาวน์กางออกมาเต็มๆ ไม่โดนตัด และอยู่บนสุด */
.gr-dropdown ul, .gr-dropdown-options, .options {
    position: absolute !important;
    top: 100% !important;
    left: 0 !important;
    width: 100% !important;
    max-height: 250px !important;
    overflow-y: auto !important;
    z-index: 99999 !important;
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.8) !important;
}

/* บังคับให้ช่องกรอกตัวเลขทุกช่องแสดงปุ่มลูกศรขึ้น-ลงตลอดเวลาอย่างถาวร */
.gr-number input[type="number"]::-webkit-inner-spin-button,
.gr-number input[type="number"]::-webkit-outer-spin-button {
    opacity: 1 !important;
    display: block !important;
    cursor: pointer !important;
}

/* บังคับให้ปุ่มเพิ่ม/ลด และไอคอนลูกศรด้านในของช่องตัวเลขทุกช่องแสดงผลครบถ้วน */
.gr-number button, 
.gr-number .wrap button,
.gr-input-row button {
    display: flex !important;
    opacity: 1 !important;
    visibility: visible !important;
}

.gr-number button svg,
.gr-number .wrap button svg {
    display: block !important;
    opacity: 1 !important;
    visibility: visible !important;
}

/* ปรับแต่งกล่องเมนู Dropdown ให้พื้นหลังสีขาว ตัวหนังสือสีดำ ชัดเจน */
.gr-dropdown-list, ul.options, .options {
    background-color: #ffffff !important;
    color: #000000 !important;
}
.gr-dropdown-list li, ul.options li, .options li {
    background-color: #ffffff !important;
    color: #000000 !important;
}
.gr-dropdown-list li:hover, ul.options li:hover, .options li:hover {
    background-color: #f1f5f9 !important;
    color: #000000 !important;
}

package_input = gr.Dropdown(
    choices=[
        "🚀 แพ็กเกจเริ่มต้น: 1 เครดิต (2 ตอน / 8 ฉาก) - คลิปสั้น/วิว (TikTok / Reels / Shopee Video)",
        "🌟 แพ็กเกจยอดฮิต: 3 เครดิต (6 ตอน / 24 ฉาก) - ซีรีส์ดราม่าเนื้อหาเข้มข้น",
        "🔥 แพ็กเกจพรีเมียม: 5 เครดิต (10 ตอน / 40 ฉาก) - ซีรีส์ดราม่าเนื้อหาจัดเต็ม 99 บาท/คลิป"
    ],
    value="🌟 แพ็กเกจยอดฮิต: 3 เครดิต (6 ตอน / 24 ฉาก) - ซีรีส์ดราม่าเนื้อหาเข้มข้น",
    label="เลือกแพ็กเกจซีรีส์"
)
"""
