import gradio as gr
import json
import urllib.parse
import os
import time
from google import genai
from google.genai import types

from database import init_db, register_user, verify_user, get_or_create_admin, check_and_deduct_credit
from ui_components import CUSTOM_CSS
user_cooldowns = {}
COOLDOWN_SECONDS = 15

# เริ่มต้นฐานข้อมูล
init_db()

# ฟังก์ชันหลักสร้างซีรีส์
def generate_dynamic_series(current_user, api_key, genre_choice, package_choice, custom_detail, avoided_topics):
    user_key = current_user if current_user else "guest"
    current_time = time.time()
    
    if user_key in user_cooldowns:
        elapsed_time = current_time - user_cooldowns[user_key]
        if elapsed_time < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed_time)
            gr.Warning(f"⏳ กรุณารอสักครู่... ระบบจำกัดการใช้งาน 1 ครั้งต่อ {COOLDOWN_SECONDS} วินาที (เหลือเวลาอีก {remaining} วินาที)")
            yield f"""<div style="background-color: #1e293b; color: #fca5a5; padding: 25px; border-radius: 12px; border: 1px solid #ef4444; font-family: 'Prompt', sans-serif;">❌ กรุณารออีก {remaining} วินาทีก่อนกดสร้างซีรีส์ใหม่อีกครั้งครับ</div>"""
            return
    
    user_cooldowns[user_key] = current_time
    # แปลงข้อความแพ็กเกจเป็นตัวเลขจำนวนตอน
    if "1 เครดิต" in package_choice:
        ep_count = 2
        scenes_per_episode = 4
        credit_cost = 1
    elif "3 เครดิต" in package_choice:
        ep_count = 6
        scenes_per_episode = 4
        credit_cost = 3
    elif "5 เครดิต" in package_choice:
        ep_count = 10
        scenes_per_episode = 4
        credit_cost = 5
    else:
        ep_count = 6
        scenes_per_episode = 4
        credit_cost = 1
    try:
        if current_user and current_user != "GodAdmin":
            success, message = check_and_deduct_credit(current_user, credit_cost)
            if not success:
                yield f"""<div style="background: #fee2e2; color: #991b1b; padding: 25px; border-radius: 12px; font-family: 'Prompt', sans-serif;">❌ เครดิตของคุณหมดแล้ว! กรุณาเติมเครดิตก่อนสร้างซีรีส์</div>"""
                return
    except Exception as e:
        yield f"""<div style="background: #fee2e2; color: #991b1b; padding: 25px; border-radius: 12px; font-family: 'Prompt', sans-serif;">❌ เกิดข้อผิดพลาดในการตรวจสอบเครดิต: {str(e)}</div>"""
        return
        
    if not api_key or api_key.strip() == "":
        yield """<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ กรุณากรอก Gemini API Key ในช่องด้านซ้าย</div>""", None
        return

    try:
        num_episodes = ep_count
        yield f"""<div style="background-color: #0f172a; color: #38bdf8; padding: 25px; border-radius: 12px; border: 1px solid #334155; text-align: center; font-size: 1.1rem; font-family: 'Prompt', sans-serif;">⏳ กำลังประมวลผลบทซีรีส์ {num_episodes} ตอน พร้อมสร้างคลังตัวละคร... กรุณารอสักครู่ครับ</div>""", None

        client = genai.Client(api_key=api_key.strip())
        system_prompt = """
        คุณเป็นนักเขียนบทซีรีส์มืออาชีพ กรุณาสร้างบทซีรีส์โดยแบ่งเป็นฉาก ๆ และในแต่ละฉากต้องมีรูปแบบดังนี้เป๊ะ ๆ:
        - ฉากที่ [X]
        - มุมกล้อง: [ระบุรายละเอียดมุมกล้อง/การเคลื่อนกล้อง]
        - บทพากย์: [บทสนทนาของตัวละคร]
        - Google Flow Prompt: [คีย์เวิร์ดภาษาอังกฤษสำหรับเจนภาพ เช่น cinematic lighting, 4k...]
        """
        full_prompt = f"{system_prompt}\n\nแนวเรื่อง: {selected_genre}\nรายละเอียด: {custom_detail}"
        
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
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.85)
        )
        
        data = json.loads(response.text)
        main_char = data.get('main_characters', [{}])[0]
        

        html_out = f"""
        <div style="background-color: #ffffff; color: #111111; padding: 25px; border-radius: 12px; font-family: 'Prompt', sans-serif; line-height: 1.6; max-height: 600px; overflow-y: auto;">
            <h2 style="color: #38bdf8; margin-top: 0;">🎬 ซีรีส์: {data.get('series_title', '')}</h2>
            <p><b>📂 แนวเรื่อง:</b> {data.get('genre', '')} | <b>🔥 ธีมหลัก:</b> {data.get('logline', '')}</p>
            <p><b>💡 Logline:</b> {data.get('logline_th', '')}</p>
            <hr style="border-color: #334155; margin: 20px 0;">
            <h3 style="color: #818cf8;">📌 คลังตัวละครหลัก</h3>
        """
        for char in data.get('main_characters', []):
            html_out += f"""<div style="background: #f8fafc; color: #1e293b; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #6366f1;">
                <b>🎭 {char.get('name_th', '')} ({char.get('role_th', '')}):</b> {char.get('personality_th', '')}<br>
                <span style="color: #94a3b8; font-size: 0.9rem;">Prompt: <code>{char.get('visual_prompt_en', '')}</code></span></div>"""
                
        html_out += "<hr style='border-color: #334155; margin: 20px 0;'>"
        for ep in data.get('episodes', []):
            html_out += f"<h3 style='color: #38bdf8;'>📺 EP {ep.get('ep_number', 1)}: {ep.get('ep_title_th', '')}</h3>"
            html_out += f"<p><b>📖 เรื่องย่อ:</b> {ep.get('ep_synopsis_th', '')}</p>"
        for scene in ep.get('scenes', []):
            scene_num = scene.get('scene_number', 1)
            prompt_text = scene.get('viden_prompt_en', '')
            html_out += f"""<div style="background: #f8fafc; color: #1e293b; padding: 18px; border-radius: 10px; margin-bottom: 18px; border: 1px solid #cbd5e1;">
                <b>Scene {scene_num}</b><br>
                <b>มุมกล้อง:</b> {scene.get('camera_and_action th', '')}<br>
                <b>บทพากย์:</b> {scene.get('voiceover_th', '')}<br>
                <b>Google Flow Prompt:</b>
                <pre id="prompt-{scene_num}" style="background: #f1f5f9; color: #1e293b; padding: 8px; border-radius: 6px; white-space: pre-wrap;">{prompt_text}</pre>
                <button onclick="navigator.clipboard.writeText(document.getElementById('prompt-{scene_num}').innerText); alert('คัดลอก Prompt เรียบร้อย!');" 
                        style="background: #6366f1; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; margin-top: 8px;">
                    📋 Copy Prompt
                </button>
            </div>"""
        
        yield html_out
        
    except Exception as e:
        yield f"""<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ เกิดข้อผิดพลาด: {str(e)}</div>"""


# --- โครงสร้างหน้าเว็บ Gradio ---
extra_css = """
.gr-box, .gr-panel, .markdown-text, div[data-testid="block-markdown"] {
    word-wrap: break-word !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
    max-width: 100% !important;
}
div[data-testid="block-markdown"] p, 
div[data-testid="block-markdown"] span, 
div[data-testid="block-markdown"] li,
div[data-testid="block-markdown"] strong {
    color: #F3F4F6 !important;
}
div[data-testid="block-markdown"] h1, 
div[data-testid="block-markdown"] h2, 
div[data-testid="block-markdown"] h3 {
    color: #60A5FA !important;
}
"""
with gr.Blocks(theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=CUSTOM_CSS ) as app:
    
    logged_in_user = gr.State("")
    user_credits = gr.State(0)

    with gr.Column(elem_classes="main-container"):
        gr.HTML('''
        <div class="header-box">
            <h1 class="header-title">AI Drama Series Creator</h1>
            <p class="header-subtitle">ระบบสมาชิกและเจเนอเรตบทซีรีส์มินิละครสั้นระดับโปรสำหรับ Google Flow</p>
        </div>
        ''')
        
        # --- หน้าที่ 1: หน้า Login / Register ---
        with gr.Column(visible=True, elem_classes="unified-card") as auth_section:
            with gr.Tabs():
            # พาร์ท 1: หน้าเข้าสู่ระบบ
                    with gr.Tab("🔑 เข้าสู่ระบบ"):
                        login_user_input = gr.Textbox(label="ชื่อผู้ใช้ (Username)")
                        login_pass_input = gr.Textbox(label="รหัสผ่าน (Password)", type="password")
                        login_show_pass = gr.Checkbox(label="👁️ แสดงรหัสผ่าน", value=False)
                        login_show_pass.change(
                            fn=lambda show: gr.Textbox(type="text" if show else "password"),
                            inputs=login_show_pass,
                            outputs=login_pass_input
                        )
                        login_btn = gr.Button("🔑 เข้าสู่ระบบ", elem_classes="primary-btn")
            
            # พาร์ท 2: หน้าสมัครสมาชิก
                    with gr.Tab("💖สมัครสมาชิกใหม่"):
                        reg_user_input = gr.Textbox(label="ตั้งชื่อผู้ใช้ (Username)")
                        reg_pass_input = gr.Textbox(label="รหัสผ่าน (Password)", type="password")
                        reg_show_pass = gr.Checkbox(label="👁️ แสดงรหัสผ่าน", value=False)
                        reg_show_pass.change(
                            fn=lambda show: gr.Textbox(type="text" if show else "password"),
                            inputs=reg_show_pass,
                            outputs=reg_pass_input
                        )
                        reg_btn = gr.Button("💖สมัครสมาชิกใหม่", variant="primary")
            
        # ปุ่ม Admin Bypass ทางลัด และกล่องแสดงสถานะ
        admin_btn = gr.Button("🔑 เข้าสู่ระบบในฐานะผู้สร้าง (Admin Bypass)", elem_classes="admin-btn")
        auth_status = gr.Markdown("", elem_classes="auth-status")

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
                            value="ดราม่าโรแมนติก / ซึ้งกินใจ", # ค่าเริ่มต้นที่เลือกไว้ label="🎬 เลือกแนวซีรีส์"
                            label="เลือกแนวละคร"
                        )
                        package_input = gr.Radio(
                            choices=[
                                "1 เครดิต (2 ตอน / 8 ฉาก)",
                                "3 เครดิต (6 ตอน / 24 ฉาก)",
                                "5 เครดิต (10 ตอน / 40 ฉาก)"
                            ],
                            value="3 เครดิต (6 ตอน / 24 ฉาก)",
                            label="เลือกแพ็กเกจซีรีส์"
                        )
                        detail_input = gr.Textbox(lines=3, placeholder="ไอเดียหรือพล็อตหลัก...", label="💡 พล็อตหลัก (Optional)")
                        avoid_input = gr.Textbox(lines=2, placeholder="พล็อตที่ห้ามซ้ำ...", label="🚫 พล็อตที่เคยทำแล้ว")
                    
                    with gr.Row():
                        logout_btn = gr.Button("🚪 ออกจากระบบ", variant="secondary")
                        submit_btn = gr.Button("🚀 Submit (สร้างซีรีส์)", elem_classes="primary-btn")
                        
                with gr.Column(scale=5):
                    
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
        fn=lambda u, c: f"<span style='color: #38bdf8; font-weight: 600;'>👤 ผู้ใช้งาน: {u} | 💳 เครดิตคงเหลือ: {c} ครั้ง</span>",
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
    fn=lambda: gr.Button(value="⏳ กำลังสร้างซีรีส์...", interactive=False),
    outputs=[submit_btn],
    queue=False
).then(
    fn=generate_dynamic_series,
    inputs=[logged_in_user, api_key_input, genre_input, package_input, detail_input, avoid_input],
    outputs=[output_html]
).then(
    fn=lambda: gr.Button(value="🚀 Submit (สร้างซีรีส์)", interactive=True),
    outputs=[submit_btn],
    queue=False
)

port = int(os.environ.get("PORT", 7860)) if "PORT" in os.environ else 7860
app.launch(server_name="0.0.0.0", server_port=port, theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=CUSTOM_CSS)
