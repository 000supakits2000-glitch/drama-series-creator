CUSTOM_CSS = """
body {
    background-image: url('bg-drama-v2.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

.unified-card {
    background-color: rgba(15, 23, 42, 0.85) !important; /* ปรับความโปร่งใสของกล่องการ์ดให้กลืนกับพื้นหลัง */
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    border-radius: 12px;
    backdrop-filter: blur(8px); /* เพิ่มลูกเล่นเบลอฉากหลังนิดหน่อยเพื่อให้ตัวหนังสือเด่นขึ้น */
}

.auth-title {
    text-align: center;
    margin-bottom: 15px;
}

.primary-btn {
    background-color: #2563eb !important;
    color: white !important;
}

.admin-btn {
    background-color: #4b5563 !important;
    color: white !important;
}
"""
