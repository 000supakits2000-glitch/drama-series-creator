import gradio as gr
import json
import urllib.parse
import os
from google import genai
from google.genai import types

# Custom CSS สำหรับแต่งดีไซน์ภาพรวม
custom_css = """
footer {visibility: hidden}

.main-container {
    max-width: 1250px !important;
    margin: auto !important;
    padding: 20px !important;
}

.header-box {
    text-align: center;
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(49, 46, 129, 0.95) 50%, rgba(67, 56, 202, 0.95) 100%);
    padding: 25px;
    border-radius: 16px;
    margin-bottom: 25px;
    box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.15);
}

.header-title {
    color: #ffffff !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    margin-bottom: 8px !important;
}

.header-subtitle {
    color: #c7d2fe !important;
    font-size: 1.05rem !important;
}

label span, div[data-testid="block-label"] {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}

.primary-btn {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 12px 24px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
}
"""

def generate_dynamic_series(api_key, genre_choice, ep_count, custom_detail, avoided_topics):
    if not api_key or api_key.strip() == "":
        err_html = """
        <div style="background-color: #0f172a; color: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #334155; min-height: 400px; display: flex; align-items: center; justify-content: center;">
            <p style="color: #f87171; font-size: 1.1rem; text-align: center;">❌ <b>กรุณากรอก Gemini API Key ของคุณในช่องด้านซ้ายก่อนเริ่มใช้งานครับ</b></p>
        </div>
        """
        return err_html, None
        
    try:
        num_episodes = int(ep_count)
        loading_html = f"""
        <div style="background-color: #0f172a; color: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #334155; min-height: 400px; display: flex; align-items: center; justify-content: center;">
            <p style="color: #38bdf8; font-size: 1.1rem; text-align: center;">⏳ <b>กำลังประมวลผลบทซีรีส์ {num_episodes} ตอน พร้อมสร้างคลังตัวละครสุดเข้มข้น... กรุณารอสักครู่ครับ</b></p>
        </div>
        """
        yield loading_html, None
        
        client = genai.Client(api_key=api_key.strip())
        
        genre_map = {
            "ดราม่าโรแมนติก / ซึ้งกินใจ": "Romance Drama",
            "สยองขวัญ / ระทึกขวัญ / ลึกลับ": "Horror / Thriller",
            "คอมเมดี้ / ตลก / ฮาๆ": "Comedy",
            "สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ": "Inspirational / Plot Twist",
            "แฟนตาซี / ย้อนยุค / ไซไฟ": "Fantasy / Sci-Fi"
        }
        
        selected_genre = genre_map.get(genre_choice, "Romance Drama")
        
        avoid_instruction = f"""
        STRICT UNIQUENESS RULE:
        The plot MUST BE completely fresh, creative, and original. 
        AVOID these previously used topics or clichés: {avoided_topics if avoided_topics else 'Standard cliché plots'}.
        Ensure the core conflict, twist, and storytelling angle are unique and surprising across all episodes.
        """
        
        prompt = f"""
        Create a {num_episodes}-Episode Drama Mini-Series Script for TikTok / YouTube Shorts.
        Genre: {selected_genre}
        Total Episodes Required: EXACTLY {num_episodes} EPISODES (from Episode 1 to Episode {num_episodes}).
        
        CRITICAL SCENE REQUIREMENT:
        Each episode MUST contain EXACTLY 4 to 5 detailed scenes (Scene 1 to Scene 5) to ensure a rich narrative.

        Additional Details: {custom_detail if custom_detail else 'Create a unique, emotional, and well-paced multi-episode storyline.'}
        
        {avoid_instruction}
        
        CRITICAL CHARACTER REQUIREMENT:
        Create at least 3 distinct characters. Provide Thai names and detailed English visual prompts for each.

        Provide the response strictly in JSON format matching the standard drama structure.
        {{
          "series_title": "Title in Thai (English Title)",
          "genre": "{selected_genre}",
          "total_episodes": {num_episodes},
          "logline_th": "Logline in Thai",
          "main_characters": [
            {{
              "name_th": "ชื่อ-นามสกุล และชื่อเล่นตัวละคร 1",
              "role_th": "บทบาท",
              "personality_th": "นิสัย/จุดเด่น",
              "visual_prompt_en": "Detailed English visual prompt: age, ethnicity, facial expression, hairstyle, unique clothing, cinematic lighting"
            }}
          ],
          "episodes": [
            {{
              "ep_number": 1,
              "ep_title_th": "ชื่อตอนที่ 1",
              "ep_synopsis_th": "เรื่องย่อตอนที่ 1",
              "scenes": [
                {{
                  "scene_number": 1,
                  "camera_and_action_th": "รายละเอียดการแสดงและมุมกล้อง",
                  "voiceover_th": "บทพากย์/บทพูด",
                  "video_prompt_en": "Complete cinematic video prompt in English"
                }}
              ]
            }}
          ]
        }}
        """

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.85
            )
        )
        
        data = json.loads(response.text)
        
        main_char = data.get('main_characters', [{}])[0]
        char_prompt = main_char.get('visual_prompt_en', 'Cinematic portrait of main character, 8k')
        encoded_prompt = urllib.parse.quote(f"cinematic character portrait, {char_prompt}, 8k resolution, photorealistic")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true"

        # สร้าง HTML แสดงผลบทซีรีส์ ตัวหนังสือสีขาวและสีฟ้าชัดเจนบนพื้นหลังดำ
        html_out = f"""
        <div style="background-color: #0f172a; color: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #334155; font-family: sans-serif; line-height: 1.6; max-height: 700px; overflow-y: auto;">
            <h2 style="color: #38bdf8; margin-top: 0;">🎬 ซีรีส์เรื่อง: {data.get('series_title', '')}</h2>
            <p><b>📌 แนวเรื่อง:</b> {data.get('genre', '')} (จำนวน {data.get('total_episodes', num_episodes)} ตอน)</p>
            <p><b>💡 Logline:</b> {data.get('logline_th', '')}</p>
            <hr style="border-color: #334155; margin: 20px 0;">
            
            <h3 style="color: #a855f7;">👥 คลังตัวละครหลัก (Character Bible)</h3>
        """
        
        for char in data.get('main_characters', []):
            html_out += f"""
            <div style="background: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #6366f1; color: #f8fafc;">
                <b>🎭 {char.get('name_th', '')} ({char.get('role_th', '')}):</b> {char.get('personality_th', '')}<br>
                <span style="color: #94a3b8; font-size: 0.9rem;">Visual Prompt: <code>{char.get('visual_prompt_en', '')}</code></span>
            </div>
            """
            
        html_out += "<hr style='border-color: #334155; margin: 20px 0;'>"
        
        for ep in data.get('episodes', []):
            html_out += f"<h3 style='color: #38bdf8;'>📺 EP {ep.get('ep_number', 1)}: {ep.get('ep_title_th', '')}</h3>"
            html_out += f"<p><b>📖 เรื่องย่อ:</b> {ep.get('ep_synopsis_th', '')}</p>"
            
            for scene in ep.get('scenes', []):
                html_out += f"""
                <div style="background: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #334155; color: #f8fafc;">
                    <b style="color: #fbbf24;">🎥 Scene {scene.get('scene_number', 1)}</b><br>
                    🎬 <b>มุมกล้อง/การแสดง:</b> {scene.get('camera_and_action_th', '')}<br>
                    🗣️ <b>บทพากย์ไทย:</b> {scene.get('voiceover_th', '')}<br>
                    ✨ <b>Video Prompt (วางใน Google Flow):</b><br>
                    <pre style="background: #090d16; color: #4ade80; padding: 10px; border-radius: 6px; white-space: pre-wrap; word-break: break-word; margin-top: 5px;">{scene.get('video_prompt_en', '')}</pre>
                </div>
                """
            html_out += "<br>"
            
        html_out += "</div>"
            
        yield html_out, image_url
        
    except Exception as e:
        err_html = f"""
        <div style="background-color: #0f172a; color: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #334155;">
            <p style="color: #f87171;">❌ เกิดข้อผิดพลาด: {str(e)}<br>(โปรดตรวจสอบว่า Gemini API Key ถูกต้องหรือไม่)</p>
        </div>
        """
        yield err_html, None

with gr.Blocks(theme=gr.themes.Default(primary_hue="indigo", neutral_hue="slate"), css=custom_css) as app:
    
    with gr.Column(elem_classes="main-container"):
        gr.HTML("""
        <div class="header-box">
            <h1 class="header-title">🎬 AI Drama Series Creator</h1>
            <p class="header-subtitle">ระบบเจเนอเรตบทซีรีส์มินิละครสั้น คลังตัวละคร และ Video Prompt สำหรับ Google Flow</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=4):
                with gr.Group():
                    api_key_input = gr.Textbox(
                        type="password",
                        placeholder="วาง Gemini API Key ของคุณที่นี่ (เช่น AIzaSy...)",
                        label="🔑 Gemini API Key (จำเป็นต้องใส่)",
                        info="รับ API Key ฟรีได้ที่ Google AI Studio"
                    )
                    genre_input = gr.Dropdown(
                        choices=[
                            "ดราม่าโรแมนติก / ซึ้งกินใจ",
                            "สยองขวัญ / ระทึกขวัญ / ลึกลับ",
                            "คอมเมดี้ / ตลก / ฮาๆ",
                            "สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ",
                            "แฟนตาซี / ย้อนยุค / ไซไฟ"
                        ],
                        value="สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ",
                        label="🎭 เลือกแนวซีรีส์"
                    )
                    ep_count_input = gr.Dropdown(
                        choices=["3", "5", "8", "10"],
                        value="5",
                        label="📺 เลือกจำนวนตอน (Episodes)"
                    )
                    detail_input = gr.Textbox(
                        lines=3,
                        placeholder="ระบุพล็อตหรือไอเดียหลักที่อยากให้เกิดขึ้นในซีรีส์เรื่องนี้...",
                        label="💡 ไอเดียหรือพล็อตหลัก (Optional)"
                    )
                    avoid_input = gr.Textbox(
                        lines=2,
                        placeholder="พิมพ์พล็อตเรื่องที่เคยทำไปแล้ว เพื่อห้ามไม่ให้ AI ซ้ำ...",
                        label="🚫 พล็อตที่เคยทำแล้ว (ห้ามซ้ำเด็ดขาด)"
                    )
                
                with gr.Row():
                    clear_btn = gr.Button("🔄 ล้างข้อมูล", variant="secondary")
                    submit_btn = gr.Button("🚀 Submit (สร้างซีรีส์)", elem_classes="primary-btn")
                    
            with gr.Column(scale=5):
                image_output = gr.Image(label="🖼️ ภาพตัวละครหลัก (Master Reference)", height=320)
                output_html = gr.HTML(label="📄 บทซีรีส์ คลังตัวละคร และ Video Prompts", value='<div style="background-color: #0f172a; color: #94a3b8; padding: 25px; border-radius: 12px; border: 1px solid #334155; min-height: 400px; display: flex; align-items: center; justify-content: center;">ผลลัพธ์บทซีรีส์และ Prompt จะแสดงที่นี่หลังกด Submit</div>')

    submit_btn.click(
        fn=generate_dynamic_series,
        inputs=[api_key_input, genre_input, ep_count_input, detail_input, avoid_input],
        outputs=[output_html, image_output]
    )
    
    clear_btn.click(fn=lambda: ("", "สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ", "5", "", "", '<div style="background-color: #0f172a; color: #94a3b8; padding: 25px; border-radius: 12px; border: 1px solid #334155; min-height: 400px; display: flex; align-items: center; justify-content: center;">ผลลัพธ์บทซีรีส์และ Prompt จะแสดงที่นี่หลังกด Submit</div>', None), 
                    outputs=[api_key_input, genre_input, ep_count_input, detail_input, avoid_input, output_html, image_output])

port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port)
