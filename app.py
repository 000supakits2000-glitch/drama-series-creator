import gradio as gr
import json
import urllib.parse
import os
import sqlite3
from google import genai
from google.genai import types

# --- 1. ตั้งค่าฐานข้อมูลสมาชิก (SQLite) ---
def init_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            credits INTEGER DEFAULT 10
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ฟังก์ชันสมัครสมาชิก
def register(username, password):
    if not username or not password:
        return "❌ กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน"
    try:
        conn = sqlite3.connect("users.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, credits) VALUES (?, ?, 10)", (username, password))
        conn.commit()
        conn.close()
        return "✅ สมัครสมาชิกสำเร็จ! (ได้รับฟรี 10 เครดิต) สามารถสลับไปแท็บ 'เข้าสู่ระบบ' ได้เลยครับ"
    except sqlite3.IntegrityError:
        return "❌ ชื่อผู้ใช้นี้ถูกใช้งานไปแล้ว กรุณาใช้ชื่ออื่น"

# ฟังก์ชันเข้าสู่ระบบปกติ
def login(username, password):
    if not username or not password:
        return gr.update(visible=False), gr.update(visible=True), "❌ กรุณากรอกข้อมูลให้ครบ", username, 0
    
    conn = sqlite3.connect("users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT credits FROM users WHERE username = ? AND password = ?", (username, password))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        credits = row[0]
        return gr.update(visible=False), gr.update(visible=True), f"🎉 ยินดีต้อนรับคุณ {username} (เครดิตคงเหลือ: {credits} ครั้ง)", username, credits
    else:
        return gr.update(visible=True), gr.update(visible=False), "❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "", 0

# 👑 ฟังก์ชันปุ่มลัดแอดมิน
def admin_login():
    admin_name = "GodAdmin"
    conn = sqlite3.connect("users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT credits FROM users WHERE username = ?", (admin_name,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT OR REPLACE INTO users (username, password, credits) VALUES (?, ?, ?)", (admin_name, "godpass123", 999))
        conn.commit()
    else:
        cursor.execute("UPDATE users SET credits = 999 WHERE username = ?", (admin_name,))
        conn.commit()
    conn.close()
    
    return gr.update(visible=False), gr.update(visible=True), f"👑 เข้าสู่ระบบในฐานะผู้สร้าง (Admin) สำเร็จ!", admin_name, 999

# ฟังก์ชันเช็กและหักเครดิต
def deduct_credit(username):
    if username == "GodAdmin":
        return True, 999
        
    conn = sqlite3.connect("users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT credits FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row and row[0] > 0:
        new_credits = row[0] - 1
        cursor.execute("UPDATE users SET credits = ? WHERE username = ?", (new_credits, username))
        conn.commit()
        conn.close()
        return True, new_credits
    conn.close()
    return False, 0


# --- 2. Custom CSS ตกแต่งเว็บแอป (แก้ไขสีข้อความต้อนรับและ Label ให้แสดงผลชัดเจน) ---
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700;800&display=swap');

footer {visibility: hidden}

body, .gradio-container {
    background: linear-gradient(135deg, #090d16 0%, #0f172a 50%, #111827 100%) !important;
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
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
    padding: 30px 20px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 12px 30px -8px rgba(99, 102, 241, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.18);
    font-family: 'Prompt', sans-serif !important;
}

.header-title {
    color: #ffffff !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    margin-bottom: 8px !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    font-family: 'Prompt', sans-serif !important;
}

.header-subtitle {
    color: #cbd5e1 !important;
    font-size: 1.1rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.2px;
    font-family: 'Prompt', sans-serif !important;
}

/* 🌟 กรอบการ์ดใหญ่ชิ้นเดียว (Unified Card) */
.unified-card {
    background: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(10px);
}

/* 🌟 กำหนดสีเฉพาะ Label ของช่องกรอกข้อมูลให้เป็นสีฟ้าสว่าง */
label span, div[data-testid="block-label"] span { 
    color: #38bdf8 !important; 
    font-weight: 600 !important; 
    font-family: 'Prompt', sans-serif !important; 
}

/* 🌟 กำหนดสีข้อความต้อนรับและสถานะผู้ใช้งานให้สว่างชัดเจน */
.welcome-text h3 {
    color: #f8fafc !important;
    font-family: 'Prompt', sans-serif !important;
    font-weight: 700 !important;
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


# --- 3. ฟังก์ชันหลักสร้างซีรีส์ ---
def generate_dynamic_series(current_user, api_key, genre_choice, ep_count, custom_detail, avoided_topics):
    if not current_user:
        yield """<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ กรุณาเข้าสู่ระบบก่อนใช้งาน</div>""", None
        return
        
    if not api_key or api_key.strip() == "":
        yield """<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ กรุณากรอก Gemini API Key ในช่องด้านซ้าย</div>""", None
        return
        
    has_credit, remaining = deduct_credit(current_user)
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


# --- 4. โครงสร้างหน้าเว็บ Gradio ---
with gr.Blocks(theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=custom_css) as app:
    
    logged_in_user = gr.State("")
    user_credits = gr.State(0)

    with gr.Column(elem_classes="main-container"):
        # Header หลัก
        gr.HTML("""
        <div class="header-box">
            <h1 class="header-title">🎬 AI Drama Series Creator</h1>
            <p class="header-subtitle">ระบบสมาชิกและเจเนอเรตบทซีรีส์มินิละครสั้นระดับโปรสำหรับ Google Flow</p>
        </div>
        """)
        
        # --- หน้าที่ 1: หน้า Login / Register ---
        with gr.Column(visible=True, elem_classes="unified-card") as auth_section:
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🔑 เข้าสู่ระบบ (Login)")
                    login_user_input = gr.Textbox(label="ชื่อผู้ใช้ (Username)")
                    login_pass_input = gr.Textbox(label="รหัสผ่าน (Password)", type="password")
                    login_btn = gr.Button("🚀 เข้าสู่ระบบ", elem_classes="primary-btn")
                    
                    gr.Markdown("---")
                    admin_btn = gr.Button("👑 เข้าสู่ระบบในฐานะผู้สร้าง (Admin Bypass)", elem_classes="admin-btn")
                
                with gr.Column():
                    gr.Markdown("### 📝 สมัครสมาชิกใหม่ (Register - ฟรี 10 เครดิต)")
                    reg_user_input = gr.Textbox(label="ตั้งชื่อผู้ใช้ (Username)")
                    reg_pass_input = gr.Textbox(label="ตั้งรหัสผ่าน (Password)", type="password")
                    reg_btn = gr.Button("✨ สมัครสมาชิก", variant="secondary")
            
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

    # เชื่อมโยงปุ่มกดระบบสมาชิก
    reg_btn.click(fn=register, inputs=[reg_user_input, reg_pass_input], outputs=[auth_status])
    
    login_btn.click(
        fn=login,
        inputs=[login_user_input, login_pass_input],
        outputs=[auth_section, app_section, auth_status, logged_in_user, user_credits]
    ).then(
        fn=lambda u, c: f"### 👤 ผู้ใช้งาน: **{u}** | 💳 เครดิตคงเหลือ: **{c}** ครั้ง",
        inputs=[logged_in_user, user_credits],
        outputs=[user_welcome_label]
    )

    admin_btn.click(
        fn=admin_login,
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
