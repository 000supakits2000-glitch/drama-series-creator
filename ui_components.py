CUSTOM_CSS = """
/* บังคับภาพพื้นหลัง bg-drama.png ให้แสดงผลเต็มจอและตรึงไว้ตลอด */
html, body, .gradio-container {
    background-image: url('file/bg-drama.png') !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

/* ล็อกรูปแบบกล่องการ์ดฟอร์ม Login/Register ให้สวยงามคงที่ */
.unified-card {
    background: rgba(15, 23, 42, 0.80) !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    padding: 24px;
    margin: 0 auto;
}

.auth-title {
    text-align: center;
    margin-bottom: 15px;
}

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
