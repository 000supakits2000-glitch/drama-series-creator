import os
import json
import urllib.parse
import time
import gradio as gr
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
    
    # [1] สร้างตัวแปรเก็บการอัปเดตหน้า UI เครดิต
    auth_ui_update = gr.update()
    
    if user_key in user_cooldowns:
        elapsed_time = current_time - user_cooldowns[user_key]
        if elapsed_time < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed_time)
            yield f"""<div style="background-color: #1e293b; color: #fca5a5; padding: 25px; border-radius: 12px; border: 1px solid #ef4444; font-family: 'Prompt', sans-serif;">❌ กรุณารออีก {remaining} วินาทีก่อนกดสร้างซีรีส์ใหม่อีกครั้งครับ</div>""", auth_ui_update
            return
    
    user_cooldowns[user_key] = current_time

    # แปลงข้อความแพ็กเกจเป็นตัวเลข
    if "1 เครดิต" in package_choice:
        credit_cost = 1; num_episodes = 2
    elif "3 เครดิต" in package_choice:
        credit_cost = 3; num_episodes = 6
    elif "5 เครดิต" in package_choice:
        credit_cost = 5; num_episodes = 10
    else:
        credit_cost = 1; num_episodes = 2

    # ตรวจสอบและหักเครดิต
    try:
        if current_user and current_user != "GodAdmin":
            from database import check_and_deduct_credit, get_db_connection, release_db_connection
            success, message = check_and_deduct_credit(current_user, credit_cost)
            if not success:
                yield f"""<div style="background: #fee2e2; color: #991b1b; padding: 25px; border-radius: 12px; font-family: 'Prompt', sans-serif;">❌ {message}</div>""", auth_ui_update
                return
            else:
                # [2] เมื่อหักเครดิตสำเร็จ ให้ดึงยอดล่าสุดจาก Database มาเตรียมแสดงผล
                conn = get_db_connection()
                if conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT credits FROM users WHERE username = %s", (current_user,))
                        row = cur.fetchone()
                        if row:
                            auth_ui_update = gr.update(value=f'<div style="text-align: center; color: #58b6fb; font-size: 1.1rem; font-weight: 600;">ยินดีต้อนรับคุณ {current_user} (เครดิตคงเหลือ: {row[0]})</div>')
                    release_db_connection(conn)
    except Exception as e:
        yield f"""<div style="background: #fee2e2; color: #991b1b; padding: 25px; border-radius: 12px; font-family: 'Prompt', sans-serif;">❌ เกิดข้อผิดพลาดในการตรวจสอบเครดิต: {str(e)}</div>""", auth_ui_update
        return
        
    if not api_key or api_key.strip() == "":
        yield """<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: 'Prompt', sans-serif;">❌ กรุณากรอก Gemini API Key ในช่องด้านซ้าย</div>""", auth_ui_update
        return

    try:
        yield f"""<div style="background-color: #0f172a; color: #38bdf8; padding: 25px; border-radius: 12px; border: 1px solid #334155; text-align: center; font-size: 1.1rem; font-family: 'Prompt', sans-serif;">⏳ กำลังประมวลผลบทซีรีส์ {num_episodes} ตอน พร้อมสร้างคลังตัวละคร... กรุณารอสักครู่ครับ</div>""", auth_ui_update

        client = genai.Client(api_key=api_key.strip())
        
        genre_map = {
            "ดราม่าโรแมนติก / ซึ้งกินใจ": "Romance Drama",
            "สยองขวัญ / ระทึกขวัญ / ลึกลับ": "Horror / Thriller",
            "คอมเมดี้ / ตลก / ฮา": "Comedy",
            "สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ": "Inspirational / Plot Twist",
            "แฟนตาซี / ย้อนยุค / ไซไฟ": "Fantasy / Sci-Fi"
        }
    
        selected_genre = genre_map.get(genre_choice, "Romance Drama")
        
        prompt = f"""
    Create a {num_episodes}-Episode Drama Mini-Series Script for TikTok / YouTube Shorts.
    Genre: {selected_genre}
    Total Episodes Required: EXACTLY {num_episodes} EPISODES.
    Each episode MUST contain EXACTLY 4 detailed scenes.
    Additional Details: {custom_detail if custom_detail else "Create a unique storyline."}
    Avoided topics: {avoided_topics if avoided_topics else "None"}

    *** สำคัญมาก! ในแต่ละฉาก (Scene) ต้องมีรูปแบบตามนี้ทุกประการ ห้ามขาดเด็ดขาด: ***
    - ฉากที่ [X]
    - มุมกล้อง: [ระบุรายละเอียดมุมกล้อง เช่น Close-up, Wide shot, Moving shot เป็นต้น]
    - บทพากย์: [บทสนทนาหรือเสียงบรรยาย]
    - Google Flow Prompt: [คีย์เวิร์ดภาษาอังกฤษสำหรับเจนภาพ เช่น cinematic lighting, 4k, hyperrealistic...]

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
            model="gemini-1.5-pro", 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.85)
        )
        
        data = json.loads(response.text)
        
        s_title = data.get('series_title', 'Untitled Series')
        s_genre = data.get('genre', selected_genre)
        s_logline = data.get('logline_th', '')

        html_out = f"""
        <div style="background-color: #ffffff; color: #111111; padding: 25px; border-radius: 12px; font-family: 'Prompt', sans-serif; line-height: 1.6; max-height: 600px; overflow-y: auto;">
            <h2 style="color: #38bdf8; margin-top: 8px;">{s_title}</h2>
            <p><b>แนวเรื่อง:</b> {s_genre}</p>
            <p>{s_logline}</p>
            <hr style="border-color: #334155; margin: 20px 0;">
            <h3 style="color: #818cf8;">ตัวละครหลัก</h3>
        """

        for char in data.get('main_characters', []):
            c_name = char.get('name_th', '')
            c_role = char.get('role_th', '')
            c_prompt = char.get('visual_prompt_en', '')
            html_out += f"""
            <div style="background: #f8fafc; color: #1e293b; padding: 18px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #6366f1;">
                <b>{c_name}</b> ({c_role})<br>
                <span style="color: #94a3b8; font-size: 0.9rem;">Prompt: <code>{c_prompt}</code></span>
            </div>
            """

        for ep in data.get('episodes', []):
            ep_num = ep.get('ep_number', 1)
            ep_title = ep.get('ep_title_th', '')
            ep_syn = ep.get('ep_synopsis_th', '')
        
            html_out += f"""
            <hr style="border-color: #334155; margin: 20px 0;">
            <h3 style="color: #38bdf8;">EP {ep_num}: {ep_title}</h3>
            <p><b>เรื่องย่อ:</b> {ep_syn}</p>
            """
            
            for scene in ep.get('scenes', []):
                s_num = scene.get('scene_number', 1)
                s_cam = scene.get('camera_and_action_th', '')
                s_voice = scene.get('voiceover_th', '')
                s_prompt = scene.get('video_prompt_en', '')
                
                html_out += f"""
                <div style="background: #F8FAFC; color: #1e293b; padding: 18px; border-radius: 10px; margin-bottom: 18px; border: 1px solid #cbd5e1;">
                    <b>ฉากที่ {s_num}</b><br>
                    <b>มุมกล้อง:</b> {s_cam}<br>
                    <b>บทพากย์:</b> {s_voice}<br>
                    <b>Google Flow Prompt:</b><br>
                    <pre style="background: #f1f5f9; color: #1e293b; padding: 8px; border-radius: 6px; white-space: pre-wrap; margin-bottom: 8px;">{s_prompt}</pre>
                    <button onclick="navigator.clipboard.writeText(`{s_prompt}`); alert('คัดลอก Prompt เรียบร้อยแล้ว!');" style="background: #6366f1; color: white; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-family: 'Prompt', sans-serif; font-weight: 600;">📋 คัดลอก Prompt นี้</button>
                </div>
                """
        
        html_out += "</div>"
        
        if current_user:
            from database import save_drama_history
            save_drama_history(current_user, s_title, html_out)

        # [3] ส่งผลลัพธ์บทละคร คืนค่าคู่กับเครดิตที่อัปเดตแล้ว
        yield html_out, auth_ui_update
        
    except Exception as e:
        # ระบบคืนเครดิตให้เมื่อเกิด Error ระหว่างเจน AI
        if current_user and current_user != "GodAdmin":
            from database import refund_credit, get_db_connection, release_db_connection
            refund_credit(current_user, credit_cost)
            
            # อัปเดตตัวเลขเครดิตบนหน้าจอให้กลับมาเท่าเดิม
            conn = get_db_connection()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT credits FROM users WHERE username = %s", (current_user,))
                    row = cur.fetchone()
                    if row:
                        auth_ui_update = gr.update(value=f'<div style="text-align: center; color: #58b6fb; font-size: 1.1rem; font-weight: 600;">ยินดีต้อนรับคุณ {current_user} (เครดิตคงเหลือ: {row[0]})</div>')
                release_db_connection(conn)

        yield f"""<div style="background-color: #0f172a; color: #f87171; padding: 25px; border-radius: 12px; border: 1px solid #334155; text-align: center; font-size: 1.1rem; font-family: 'Prompt', sans-serif;">❌ เกิดข้อผิดพลาดในการสร้างซีรีส์ (ระบบได้คืนเครดิตให้คุณแล้ว): {str(e)}</div>""", auth_ui_update


# --- โครงสร้างหน้าเว็บ Gradio ---
with gr.Blocks(theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=CUSTOM_CSS) as app:
    
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
                    reg_status = gr.HTML("", elem_classes="auth-status")

        # --- หน้าที่ 2: หน้าแอปหลัก ---
        with gr.Column(visible=False, elem_classes="unified-card") as app_section:
            auth_status = gr.Markdown("", elem_classes="auth-status")
            with gr.Row():
                with gr.Column(scale=4):
                    with gr.Group():
                        api_key_input = gr.Textbox(type="password", value="", placeholder="วาง Gemini API Key ที่นี่...", label="🔑 Gemini API Key")
                        genre_input = gr.Dropdown(
                            choices=[
                                "ดราม่าโรแมนติก / ซึ้งกินใจ", "สยองขวัญ / ระทึกขวัญ / ลึกลับ",
                                "คอมเมดี้ / ตลก / ฮาๆ", "สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ", "แฟนตาซี / ย้อนยุค / ไซไฟ"
                            ],
                            value="ดราม่าโรแมนติก / ซึ้งกินใจ", # ค่าเริ่มต้น
                            label="เลือกแนวละคร"
                        )
                        package_input = gr.Radio(
                            choices=[
                                "1 เครดิต (2 ตอน / 8 ฉาก)",
                                "3 เครดิต (6 ตอน / 24 ฉาก)",
                                "5 เครดิต (10 ตอน / 40 ฉาก)"
                            ],
                            value="1 เครดิต (2 ตอน / 8 ฉาก)", # กำหนดค่าเริ่มต้นเป็น 1 เครดิต
                            label="เลือกแพ็กเกจซีรีส์"
                        )
                        detail_input = gr.Textbox(lines=3, value="", placeholder="ไอเดียหรือพล็อตหลัก...", label="💡 พล็อตหลัก (Optional)")
                        avoid_input = gr.Textbox(lines=2, value="", placeholder="พล็อตที่ห้ามซ้ำ...", label="🚫 พล็อตที่เคยทำแล้ว")
                    
                    with gr.Row():
                        logout_btn = gr.Button("🚪 ออกจากระบบ", variant="secondary")
                        submit_btn = gr.Button("🚀 Submit (สร้างซีรีส์)", elem_classes="primary-btn")
                        
                with gr.Column(scale=5):
                    output_html = gr.HTML(label="📄 ผลลัพธ์บทซีรีส์", value='<div style="background-color: #0f172a; color: #94a3b8; padding: 25px; border-radius: 12px; border: 1px solid #334155; min-height: 350px; display: flex; align-items: center; justify-content: center; font-family: Prompt, sans-serif;">กรุณากดสร้างซีรีส์เพื่อดูผลลัพธ์ที่นี่</div>')
                    
                    with gr.Accordion("📜 ประวัติบทละครย้อนหลังของคุณ (10 เรื่องล่าสุด)", open=False, visible=False) as history_container:
                        with gr.Row():
                            history_dropdown = gr.Dropdown(label="เลือกเรื่องที่ต้องการดูย้อนหลัง", choices=[], interactive=True, scale=4)
                            load_hist_btn = gr.Button("🔄 โหลดรายชื่อ", scale=1)
                        history_content_box = gr.HTML(label="เนื้อหาบทละครย้อนหลัง", value='<div style="background-color: #0f172a; padding: 25px; border-radius: 12px; text-align: center; color: #94a3b8; border: 1px solid #334155;">เลือกชื่อเรื่องจาก Dropdown ด้านบนเพื่อดูบทละครครับ</div>')

    # ฟังก์ชันดึงประวัติเข้า Dropdown
    def fetch_user_history(username):
        if not username:
            return gr.update(choices=[])
        try:
            from database import get_user_history_by_username
            histories = get_user_history_by_username(username)
            if not histories:
                return gr.update(choices=[])
            # แก้ไข: ให้แสดงแค่ "ลำดับที่. ชื่อเรื่อง" เท่านั้น
            choices = [f"{i+1}. {h[0]}" for i, h in enumerate(histories)]
            return gr.update(choices=choices)
        except Exception as e:
            print(f"Error fetching history: {e}")
            return gr.update(choices=[])

    # ฟังก์ชันแสดงเนื้อหาเต็มเมื่อเลือกชื่อเรื่อง
    def show_selected_history(selected_choice, username):
        if not selected_choice or not username:
            return "ยังไม่ได้เลือกรายการ"
        from database import get_user_history_by_username
        histories = get_user_history_by_username(username)
        for i, h in enumerate(histories):
            label = f"{i+1}. {h[0]}"
            if label == selected_choice:
                return h[1] # แก้ไข: คืนค่า h[1] (เนื้อหา) แทน h[2] ที่ไม่มีอยู่จริง
        return "ไม่พบเนื้อหา"

    # ผูก Event ปุ่มกดและการเลือกใน Dropdown
    load_hist_btn.click(fn=fetch_user_history, inputs=[logged_in_user], outputs=[history_dropdown])
    history_dropdown.change(fn=show_selected_history, inputs=[history_dropdown, logged_in_user], outputs=[history_content_box])

    # เชื่อมโยงระบบล็อกอิน
    reg_btn.click(
        fn=register_user, 
        inputs=[reg_user_input, reg_pass_input], 
        outputs=[reg_status]
    )
    
    def handle_login(u, p):
        success, credits = verify_user(u, p)
        if success:
            from database import get_user_history_by_username
            histories = get_user_history_by_username(u)
            choices = [f"{i+1}. {h[0]}" for i, h in enumerate(histories)] if histories else []
            return (
                gr.update(visible=False), # ซ่อนหน้า Auth
                gr.update(visible=True),  # แสดงหน้า App
                gr.update(value=f'<div style="text-align: center; color: #58b6fb; font-size: 1.1rem; font-weight: 600;">ยินดีต้อนรับคุณ {u} (เครดิตคงเหลือ: {credits})</div>'),
                u,
                credits,
                gr.update(visible=True),
                gr.update(choices=choices),
                # --- รีเซ็ตค่าเริ่มต้นของอินพุตต่างๆ ---
                gr.update(value=""),                                   # api_key_input
                gr.update(value="ดราม่าโรแมนติก / ซึ้งกินใจ"),            # genre_input
                gr.update(value="1 เครดิต (2 ตอน / 8 ฉาก)"),             # package_input
                gr.update(value=""),                                   # detail_input
                gr.update(value="")                                    # avoid_input
            )
        else:
            return (
                gr.update(visible=True), gr.update(visible=False), "✕ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "", 0, gr.update(visible=False), gr.update(choices=[]),
                gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
            )

    login_btn.click(
        fn=handle_login,
        inputs=[login_user_input, login_pass_input],
        outputs=[
            auth_section, app_section, auth_status, logged_in_user, user_credits, history_container, history_dropdown,
            api_key_input, genre_input, package_input, detail_input, avoid_input # เพิ่มตัวแปรอินพุตสำหรับรีเซ็ต
        ]
    )

    logout_btn.click(
        fn=lambda: (
            gr.update(visible=True),
            gr.update(visible=False),
            "",
            0,
            '<div style="background-color: #0f172a; color: #94a3b8; padding: 25px; border-radius: 12px; border: 1px solid #334155; min-height: 350px; display: flex; align-items: center; justify-content: center; font-family: inherit;">ระบบพร้อมใช้งาน กรุณาสร้างซีรีส์ใหม่</div>',
            "",
            "",
            gr.update(visible=False),
            # --- รีเซ็ตค่าเมื่อออกจากระบบ ---
            gr.update(value=""),                                  # api_key_input
            gr.update(value="ดราม่าโรแมนติก / ซึ้งกินใจ"),           # genre_input
            gr.update(value="1 เครดิต (2 ตอน / 8 ฉาก)"),            # package_input
            gr.update(value=""),                                  # detail_input
            gr.update(value="")                                   # avoid_input
        ),
        outputs=[
            auth_section, 
            app_section, 
            logged_in_user, 
            user_credits, 
            output_html, 
            login_user_input, 
            login_pass_input,
            history_container,
            api_key_input, genre_input, package_input, detail_input, avoid_input
        ]
    )

    # ผูก Event ปุ่มกด พร้อมล็อกอินพุตทั้งหมดขณะกำลังสร้างซีรีส์
    submit_btn.click(
        fn=lambda: (
            gr.Button(value="⏳ กำลังสร้างซีรีส์...", interactive=False),
            gr.update(interactive=False), # api_key_input
            gr.update(interactive=False), # genre_input
            gr.update(interactive=False), # package_input
            gr.update(interactive=False), # detail_input
            gr.update(interactive=False), # avoid_input
        ),
        outputs=[submit_btn, api_key_input, genre_input, package_input, detail_input, avoid_input],
        queue=False
    ).then(
        fn=generate_dynamic_series,
        inputs=[logged_in_user, api_key_input, genre_input, package_input, detail_input, avoid_input],
        outputs=[output_html, auth_status] 
    ).then(
        fn=lambda: (
            gr.Button(value="🚀 Submit (สร้างซีรีส์)", interactive=True),
            gr.update(interactive=True),  # api_key_input
            gr.update(interactive=True),  # genre_input
            gr.update(interactive=True),  # package_input
            gr.update(interactive=True),  # detail_input
            gr.update(interactive=True),  # avoid_input
        ),
        outputs=[submit_btn, api_key_input, genre_input, package_input, detail_input, avoid_input],
        queue=False
    )

port = int(os.environ.get("PORT", 7860)) if "PORT" in os.environ else 7860
app.launch(server_name="0.0.0.0", server_port=port, theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=CUSTOM_CSS)
