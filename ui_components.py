# ui_components.py

CUSTOM_CSS = """
/* ตั้งค่าภาพพื้นหลังหลัก bg-drama.png */
body, .gradio-container {
    background-image: url('file/bg-drama.png') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

/* ปรับแต่งกล่องการ์ดให้มีความโปร่งใสและเบลอฉากหลังนิดๆ เพื่อให้อ่านตัวหนังสือชัดเจน */
.unified-card {
    background: rgba(15, 23, 42, 0.75) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    padding: 24px;
    margin: 0 auto;
}

/* จัดสไตล์หัวข้อ */
.auth-title {
    text-align: center;
    margin-bottom: 15px;
}

/* ปรับแต่งปุ่มกด */
.primary-btn {
    background-color: #6366f1 !important;
    color: white !important;
    border-radius: 8px !important;
}

.admin-btn {
    background-color: #f97316 !important;
    color: white !important;
    border-radius: 8px !important;
}
"""
