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
get_or_create_admin()

# --- 1. JavaScript สำหรับฟังก์ชัน Show/Hide Password ---
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

# --- 2. ฟังก์ชันหลักของระบบ (Login, Register & Content Generation) ---
def handle_login(username, password):
    if not username or not password:
        return "กรุณากรอกชื่อผู้ใช้และรหัสผ่าน", gr.update(visible=True), gr.update(visible=False), f"👤 ผู้ใช้งาน: -"
    
    user = verify_user(username, password)
    if user:
        return f"เข้าสู่ระบบสำเร็จ!", gr.update(visible=False), gr.update(visible=True), f"👤 ผู้ใช้งาน: {username} | เครดิตคงเหลือ: {user.get('credits', 0)}"
    return "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", gr.update(visible=True), gr.update(visible=False), f"👤 ผู้ใช้งาน: -"

def handle_admin_bypass():
    return "เข้าสู่ระบบในฐานะผู้ดูแลระบบ", gr.update(visible=False), gr.update(visible=True), f"👑 ผู้ดูแลระบบ (Admin Bypass) | เครดิต: ไม่จำกัด"

def handle_register(username, password):
    if not username or not password:
        return "กรุณากรอกข้อมูลให้ครบถ้วน"
    success = register_user(username, password)
    if success:
        return "สมัครสมาชิกสำเร็จ! (รับฟรี 18 เครดิต) สามารถเข้าสู่ระบบได้เลย"
    return "ชื่อผู้ใช้นี้มี ใช้งานแล้ว กรุณาเปลี่ยนชื่ออื่น"

def generate_dynamic_series(current_user, api_key, genre_choice, ep_count, custom_detail, avoided_topics):
    if not current_user or current_user == "👤ผู้ใช้งาน: -":
        yield f"""<div style="background-color: #ff172a; color: #f8f1f1; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ กรุณาเข้าสู่ระบบก่อนใช้งาน</div>""", None
        return
    
    if not api_key or api_key.strip() == "":
        yield f"""<div style="background-color: #ff172a; color: #f8f1f1; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌กรุณาใส่ Gemini API Key ในช่องตั้งค่า</div>""", None
        return

    try:
        client = genai.Client(api_key=api_key.strip())
        prompt = f"สร้างโครงเรื่องซีรีส์ แนว: {genre_choice}, จำนวนตอน: {ep_count}, รายละเอียด: {custom_detail}"
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        yield f"""<div style="background-color: #0f172a; color: #38bdf8; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">{response.text}</div>""", response.text
    except Exception as e:
        yield f"""<div style="background-color: #ff172a; color: #f8f1f1; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ เกิดข้อผิดพลาด: {str(e)}</div>""", None

# --- 3. สร้างโครงสร้าง Gradio Interface ---
with gr.Blocks(theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=CUSTOM_CSS, js=CUSTOM_JS) as demo:
    
    current_user_state = gr.State("👤 ผู้ใช้งาน: -")

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

    # --- พาร์ท 2: หน้าหลักแอปพลิเคชัน (หลัง Login สำเร็จ) ---
    with gr.Column(visible=False, elem_classes="unified-card") as app_section:
        with gr.Row(elem_classes="welcome-text"):
            user_welcome_label = gr.Markdown("### ยินดีต้อนรับสู่ระบบสร้างซีรีส์")
            logout_btn = gr.Button("ออกจากระบบ", variant="stop")

        with gr.Row():
            api_key_input = gr.Textbox(label="Gemini API Key", type="password")
            genre_dropdown = gr.Dropdown(choices=["Drama", "Romance", "Action", "Sci-Fi", "Comedy"], label="แนวซีรีส์", value="Drama")
            ep_slider = gr.Slider(minimum=1, maximum=10, value=3, step=1, label="จำนวนตอน")

        custom_detail_input = gr.Textbox(label="รายละเอียดเพิ่มเติม / พล็อตเรื่องย่อ", lines=3)
        avoided_topics_input = gr.Textbox(label="เนื้อหาที่ต้องการหลีกเลี่ยง", lines=2)

        generate_btn = gr.Button("🚀 เริ่มสร้างซีรีส์", elem_classes="primary-btn")
        
        output_html = gr.HTML()
        output_raw_text = gr.Textbox(label="ผลลัพธ์ (Raw Text)", visible=False)

    # --- เชื่อมโยง Event การทำงาน ---
    login_btn.click(
        fn=handle_login,
        inputs=[login_user_input, login_pass_input],
        outputs=[auth_status, auth_section, app_section, current_user_state]
    )

    admin_btn.click(
        fn=handle_admin_bypass,
        inputs=[],
        outputs=[auth_status, auth_section, app_section, current_user_state]
    )
    
    reg_btn.click(
        fn=handle_register,
        inputs=[reg_user_input, reg_pass_input],
        outputs=[auth_status]
    )

    logout_btn.click(
        fn=lambda: (gr.update(visible=True), gr.update(visible=False), "👤 ผู้ใช้งาน: -"),
        inputs=[],
        outputs=[auth_section, app_section, current_user_state]
    )

    generate_btn.click(
        fn=generate_dynamic_series,
        inputs=[current_user_state, api_key_input, genre_dropdown, ep_slider, custom_detail_input, avoided_topics_input],
        outputs=[output_html, output_raw_text]
    )

# --- รันแอปพลิเคชัน ---
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
