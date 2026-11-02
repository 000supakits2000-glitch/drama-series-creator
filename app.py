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

# ฟังก์ชันหลักสร้างซีรีส์
def generate_dynamic_series(current_user, api_key, genre_choice, ep_count, custom_detail, avoided_topics):
    if not current_user:
        yield """<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ กรุณาเข้าสู่ระบบก่อนใช้งาน</div>""", None
        return
        
    if not api_key or api_key.strip() == "":
        yield """<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ กรุณากรอก Gemini API Key ในช่องด้านซ้าย</div>""", None
        return
        
    has_credit, remaining = check_and_deduct_credit(current_user)
    if not has_credit:
        yield f"""<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ เครดิตของคุณหมดแล้ว! กรุณาเติมเครดิต</div>""", None
        return

    try:
        num_episodes = int(ep_count)
        yield f"""<div style="background-color: #0f172a; color: #38bdf8; padding: 25px; border-radius: 12px; border: 1px solid #334155; text-align: center; font-size: 1.1rem; font-family: 'Prompt', sans-serif;">⏳ กำลังประมวลผลบทซีรีส์ {num_episodes} ตอน พร้อมสร้างคลังตัวละคร... กรุณารอสักครู่ครับ</div>""", None

        client = genai.Client(api_key=api_key.strip())
        
        genre_map = {
            "ดราม่าโรแมนติก / ซึ้งกินใจ": "Romance Drama",
            "สยองขวัญ / ระทึกขวัญ / ลึกลับ": "Horror / Thriller",
            "คอมเมดี้ / ตลก / ฮาๆ": "Comedy",
            "สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ": "Inspirational / Plot Twist",
            "แฟนตาซี / ย้อนยุค / ไซไฟ": "Fantasy / Sci-Fi"
        }
        selected_genre = genre_map.get(genre_choice, "Romance Drama")
        
        prompt = f"""
        Create a {num_episodes}-Episode Drama Mini-Series Script for TikTok / YouTube Shorts.
        Genre: {selected_genre}
        Total Episodes Required: EXACTLY {num_episodes} EPISODES.
        Each episode MUST contain EXACTLY 4 to 5 detailed scenes.
        Additional Details: {custom_detail if custom_detail else 'Create a unique storyline.'}
        Avoided topics: {avoided_topics if avoided_topics else 'None'}
        
        Provide response strictly in JSON format:
        {{
          "series_title": "Title (Thai / English)",
          "genre": "{selected_genre}",
          "total_episodes": {num_episodes},
          "logline_th": "Logline in Thai",
          "main_characters": [
            {{
              "name_th": "ชื่อตัวละคร", "role_th": "บทบาท", "personality_th": "นิสัย",
              "visual_prompt_en": "Detailed English visual prompt"
            }}
          ],
          "episodes": [
            {{
              "ep_number": 1, "ep_title_th": "ชื่อตอน", "ep_synopsis_th": "เรื่องย่อ",
              "scenes": [
                {{
                  "scene_number": 1, "camera_and_action_th": "มุมกล้อง",
                  "voiceover_th": "บทพากย์", "video_prompt_en": "Video prompt in English"
                }}
              ]
            }}
          ]
        }}
        """

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.85)
        )
        
        data = json.loads(response.text)
        main_char = data.get('main_characters', [{}])[0]
        char_prompt = main_char.get('visual_prompt_en', 'Cinematic portrait, 8k')
        encoded_prompt = urllib.parse.quote(f"cinematic character portrait, {char_prompt}, 8k resolution")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true"

        html_out = f"""
        <div style="background-color: #0f172a; color: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif; line-height: 1.6; max-height: 650px; overflow-y: auto;">
            <h2 style="color: #38bdf8; margin-top: 0;">🎬 ซีรีส์: {data.get('series_title', '')}</h2>
            <p><b>📌 แนวเรื่อง:</b> {data.get('genre', '')} | <b>เครดิตคงเหลือ:</b> {remaining} ครั้ง</p>
            <p><b>💡 Logline:</b> {data.get('logline_th', '')}</p>
            <hr style="border-color: #334155; margin: 20px 0;">
            <h3 style="color: #a855f7;">👥 คลังตัวละครหลัก</h3>
        """
        for char in data.get('main_characters', []):
            html_out += f"""<div style="background: #1e293b; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #6366f1;">
                <b>🎭 {char.get('name_th', '')} ({char.get('role_th', '')}):</b> {char.get('personality_th', '')}<br>
                <span style="color: #94a3b8; font-size: 0.9rem;">Prompt: <code>{char.get('visual_prompt_en', '')}</code></span></div>"""
                
        html_out += "<hr style='border-color: #334155; margin: 20px 0;'>"
        for ep in data.get('episodes', []):
            html_out += f"<h3 style='color: #38bdf8;'>📺 EP {ep.get('ep_number', 1)}: {ep.get('ep_title_th', '')}</h3>"
            html_out += f"<p><b>📖 เรื่องย่อ:</b> {ep.get('ep_synopsis_th', '')}</p>"
            for scene in ep.get('scenes', []):
                html_out += f"""<div style="background: #1e293b; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #334155;">
                    <b style="color: #fbbf24;">🎥 Scene {scene.get('scene_number', 1)}</b><br>
                    🎬 <b>มุมกล้อง:</b> {scene.get('camera_and_action_th', '')}<br>
                    🗣️ <b>บทพากย์:</b> {scene.get('voiceover_th', '')}<br>
                    ✨ <b>Google Flow Prompt:</b><br>
                    <pre style="background: #090d16; color: #4ade80; padding: 8px; border-radius: 6px; white-space: pre-wrap;">{scene.get('video_prompt_en', '')}</pre></div>"""
        html_out += "</div>"
        
        yield html_out, image_url
        
    except Exception as e:
        yield f"""<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ เกิดข้อผิดพลาด: {str(e)}</div>""", None
        # เพิ่ม JavaScript สำหรับฟังก์ชัน toggle ดูรหัสผ่าน
show_pass_js = """
<script>
function togglePasswordVisibility(inputId) {
    const input = document.querySelector('#' + inputId + ' input');
    if (input) {
        if (input.type === "password") {
            input.type = "text";
        } else {
            input.type = "password";
        }
    }
}
</script>
"""


# --- โครงสร้างหน้าเว็บ Gradio ---
with gr.Blocks(theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=CUSTOM_CSS) as app:
    
    logged_in_user = gr.State("")
    user_credits = gr.State(0)

    with gr.Column(elem_classes="main-container"):
        gr.HTML("""
        <div class="header-box">
            <h1 class="header-title">🎬 AI Drama Series Creator</h1>
            <p class="header-subtitle">ระบบสมาชิกและเจเนอเรตบทซีรีส์มินิละครสั้นระดับโปรสำหรับ Google Flow</p>
        </div>
        """)
        
# --- หน้าที่ 1: หน้า Login / Register ---
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

# --- หน้าที่ 2: หน้าแอปหลัก ---
with gr.Column(visible=False, elem_classes="unified-card") as app_section:
    with gr.Row(elem_classes="welcome-text"):
        user_welcome_label = gr.Markdown("### ยินดีต้อนรับ")
            
            with gr.Row():
                with gr.Column(scale=4):
                    with gr.Group():
                        api_key_input = gr.Textbox(type="password", placeholder="วาง Gemini API Key ที่นี่...", label="🔑 Gemini API Key")
                        genre_input = gr.Dropdown(
                            choices=[
                                "ดราม่าโรแมนติก / ซึ้งกินใจ", "สยองขวัญ / ระทึกขวัญ / ลึกลับ",
                                "คอมเมดี้ / ตลก / ฮาๆ", "สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ", "แฟนตาซี / ย้อนยุค / ไซไฟ"
                            ],
                            value="สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ", label="🎭 เลือกแนวซีรีส์"
                        )
                        ep_count_input = gr.Dropdown(choices=["3", "5", "8", "10"], value="5", label="📺 จำนวนตอน")
                        detail_input = gr.Textbox(lines=3, placeholder="ไอเดียหรือพล็อตหลัก...", label="💡 พล็อตหลัก (Optional)")
                        avoid_input = gr.Textbox(lines=2, placeholder="พล็อตที่ห้ามซ้ำ...", label="🚫 พล็อตที่เคยทำแล้ว")
                    
                    with gr.Row():
                        logout_btn = gr.Button("🚪 ออกจากระบบ", variant="secondary")
                        submit_btn = gr.Button("🚀 Submit (สร้างซีรีส์)", elem_classes="primary-btn")
                        
                with gr.Column(scale=5):
                    image_output = gr.Image(label="🖼️ ภาพตัวละครหลัก (Master Reference)", height=280)
                    output_html = gr.HTML(label="📄 ผลลัพธ์บทซีรีส์", value='<div style="background-color: #0f172a; color: #94a3b8; padding: 25px; border-radius: 12px; border: 1px solid #334155; min-height: 350px; display: flex; align-items: center; justify-content: center; font-family: Prompt, sans-serif;">กรุณากดสร้างซีรีส์เพื่อดูผลลัพธ์ที่นี่</div>')

    # เชื่อมโยงระบบล็อกอิน
    reg_btn.click(fn=register_user, inputs=[reg_user_input, reg_pass_input], outputs=[auth_status])
    
    def handle_login(u, p):
        success, credits = verify_user(u, p)
        if success:
            return gr.update(visible=False), gr.update(visible=True), f"🎉 ยินดีต้อนรับคุณ {u} (เครดิตคงเหลือ: {credits} ครั้ง)", u, credits
        else:
            return gr.update(visible=True), gr.update(visible=False), "❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "", 0

    login_btn.click(
        fn=handle_login,
        inputs=[login_user_input, login_pass_input],
        outputs=[auth_section, app_section, auth_status, logged_in_user, user_credits]
    ).then(
        fn=lambda u, c: f"### 👤 ผู้ใช้งาน: **{u}** | 💳 เครดิตคงเหลือ: **{c}** ครั้ง",
        inputs=[logged_in_user, user_credits],
        outputs=[user_welcome_label]
    )

    def handle_admin():
        u, c = get_or_create_admin()
        return gr.update(visible=False), gr.update(visible=True), f"👑 เข้าสู่ระบบในฐานะผู้สร้าง (Admin) สำเร็จ!", u, c

    admin_btn.click(
        fn=handle_admin,
        outputs=[auth_section, app_section, auth_status, logged_in_user, user_credits]
    ).then(
        fn=lambda u, c: f"### 👑 ผู้ใช้งาน: **{u} (ผู้สร้างระบบ)** | 💳 เครดิต: **ไม่จำกัด (999)** ครั้ง",
        inputs=[logged_in_user, user_credits],
        outputs=[user_welcome_label]
    )

    logout_btn.click(
        fn=lambda: (gr.update(visible=True), gr.update(visible=False), "", 0),
        outputs=[auth_section, app_section, logged_in_user, user_credits]
    )

    submit_btn.click(
        fn=generate_dynamic_series,
        inputs=[logged_in_user, api_key_input, genre_input, ep_count_input, detail_input, avoid_input],
        outputs=[output_html, image_output]
    )

port = int(os.environ.get("PORT", 7860)) if "PORT" in os.environ else 7860
app.launch(server_name="0.0.0.0", server_port=port)
