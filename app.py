import gradio as gr
import json
import urllib.parse
import os
from google import genai
from google.genai import types

from database import init_db, register_user, verify_user, get_or_create_admin, check_and_deduct_credit
from ui_components import CUSTOM_CSS

# เริ่มต้นฐานข้อมูล
init_db()

# --- 1. Custom CSS & JavaScript สำหรับฟังก์ชัน Show/Hide Password ---
CUSTOM_JS = """
function togglePasswordVisibility(fieldId) {
    const passwordInput = document.querySelector('#' + fieldId + ' input');
    if (passwordInput) {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
        } else {
            passwordInput.type = 'password';
        }
    }
}
"""

# --- 2. ฟังก์ชันจำลองการทำงานระบบ Login / Register ---
def handle_login(username, password):
    if not username or not password:
        return "กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน", gr.update(visible=True), gr.update(visible=False)
    # ตรวจสอบผ่านฐานข้อมูลจริง
    user = verify_user(username, password)
    if user:
        return f"ยินดีต้อนรับคุณ {username} เข้าสู่ระบบ!", gr.update(visible=False), gr.update(visible=True)
    return "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", gr.update(visible=True), gr.update(visible=False)

def handle_register(username, password):
    if not username or not password:
        return "กรุณากรอกข้อมูลสำหรับสมัครสมาชิกให้ครบถ้วน"
    success = register_user(username, password)
    if success:
        return f"สมัครสมาชิกสำเร็จ! ยินดีต้อนรับ {username} (ได้รับ 18 เครดิตฟรี)"
    return "ชื่อผู้นี้อาจมีผู้ใช้งานแล้ว กรุณาเปลี่ยนชื่อผู้ใช้"

# --- 3. สร้างโครงสร้าง Gradio Interface ---
with gr.Blocks(theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=CUSTOM_CSS, js=CUSTOM_JS) as demo:
    
    # --- พาร์ท 1: หน้า Login / Register ---
    with gr.Column(visible=True, elem_classes="unified-card") as auth_section:
        with gr.Row():
            with gr.Column(elem_classes="auth-title"):
                gr.Markdown("### เข้าสู่ระบบ (Login)")
                login_user_input = gr.Textbox(label="ชื่อผู้ใช้ (Username)")
                login_pass_input = gr.Textbox(label="รหัสผ่าน (Password)", type="password")
                
                toggle_login_btn = gr.Button("👁", elem_id="toggle_login_btn")
                toggle_login_btn.click(None, None, None, js="() => togglePasswordVisibility('login_pass')")
                
                gr.HTML("""
                <div style="text-align: right; margin-top: 6px; margin-bottom: 12px;">
                    <a href="#" style="color: #38bdf8; font-size: 0.85rem; text-decoration: none; font-family: 'Prompt', sans-serif;">Forgot Password?</a>
                </div>
                """)
                
                login_btn = gr.Button("เข้าสู่ระบบ", elem_classes="primary-btn")
                
                gr.Markdown("---")
                admin_btn = gr.Button("เข้าสู่ระบบในฐานะผู้ดูแล (Admin Bypass)", elem_classes="admin-btn")
                gr.Markdown("---")

        with gr.Column(elem_classes="auth-title"):
            gr.Markdown("### สมัครสมาชิก (Register - ฟรี 18 เครดิต)")
            reg_user_input = gr.Textbox(label="ชื่อผู้ใช้ (Username)")
            reg_pass_input = gr.Textbox(label="รหัสผ่าน (Password)", type="password")
            
            toggle_reg_btn = gr.Button("👁", elem_id="toggle_reg_btn")
            toggle_reg_btn.click(None, None, None, js="() => togglePasswordVisibility('reg_pass')")
            
            reg_btn = gr.Button("สมัครสมาชิก", variant="secondary")

        auth_status = gr.Markdown("")

    # --- พาร์ท 2: หน้าหลักหลังจาก Login สำเร็จ ---
    with gr.Column(visible=False, elem_classes="unified-card") as app_section:
        with gr.Row(elem_classes="welcome-text"):
            user_welcome_label = gr.Markdown("### ยินดีต้อนรับเข้าสู่ระบบหลัก")
            logout_btn = gr.Button("ออกจากระบบ", variant="stop")

    # --- เชื่อมโยง Event ปุ่มกด ---
    login_btn.click(
        fn=handle_login,
        inputs=[login_user_input, login_pass_input],
        outputs=[auth_status, auth_section, app_section]
    )
    
    reg_btn.click(
        fn=handle_register,
        inputs=[reg_user_input, reg_pass_input],
        outputs=[auth_status]
    )

# --- รันแอปพลิเคชัน ---
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
