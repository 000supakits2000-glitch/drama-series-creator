import gradio as gr
import json
import urllib.parse
import os
from google import genai
from google.genai import types

# Custom CSS พร้อมบังคับภาพพื้นหลังให้แสดงผล
custom_css = """
/* บังคับภาพพื้นหลังเว็บแอป */
.gradio-container {
    background-image: linear-gradient(rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.94)), url('https://image.pollinations.ai/prompt/cinematic%20film%20set,%20dramatic%20lighting,%20movie%20production,%20dark%20moody%20atmosphere,8k?width=1920&height=1080&nologo=true') !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}

/* ซ่อน Footer ของ Gradio */
footer {visibility: hidden}

/* ปรับแต่ง Container หลัก */
.main-container {
    max-width: 1200px !important;
    margin: auto !important;
    padding: 20px !important;
}

/* ตกแต่งหัวข้อเว็บให้โปร่งแสงสวยงาม */
.header-box {
    text-align: center;
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(49, 46, 129, 0.85) 50%, rgba(67, 56, 202, 0.85) 100%);
    padding: 25px;
    border-radius: 16px;
    margin-bottom: 25px;
    box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
}

.header-title {
    color: #ffffff !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    margin-bottom: 8px !important;
    letter-spacing: 0.5px;
}

.header-subtitle {
    color: #c7d2fe !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
}

/* ปุ่ม Submit โทนสีนีออน */
.primary-btn {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 12px 24px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
    transition: all 0.3s ease !important;
}

.primary-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6) !important;
}
"""

def generate_dynamic_series(api_key, genre_choice, ep_count, custom_detail, avoided_topics):
    if not api_key or api_key.strip() == "":
        yield "❌ **กรุณากรอก Gemini API Key ของคุณในช่องด้านซ้ายก่อนเริ่มใช้งานครับ**", None
        return
        
    try:
        num_episodes = int(ep_count)
        yield f"⏳ **กำลังประมวลผลบทซีรีส์ {num_episodes} ตอน พร้อมสร้างคลังตัวละครสุดเข้มข้น... กรุณารอสักครู่ครับ**", None
        
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
        
        yield f"⏳ **ดึงข้อมูลสำเร็จ! กำลังเรนเดอร์ภาพ Master Reference ตัวละครหลัก...**, ", None
        
        main_char = data.get('main_characters', [{}])[0]
        char_prompt = main_char.get('visual_prompt_en', 'Cinematic portrait of main character, 8k')
        encoded_prompt = urllib.parse.quote(f"cinematic character portrait, {char_prompt}, 8k resolution, photorealistic")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true"

        output_text = f"# 🎬 **ซีรีส์เรื่อง:** {data.get('series_title', '')}\n"
        output_text += f"📌 **แนวเรื่อง:** {data.get('genre', '')} (จำนวน {data.get('total_episodes', num_episodes)} ตอน | 4-5 ซีนต่อตอน)\n"
        output_text += f"💡 **Logline:** {data.get('logline_th', '')}\n\n"
        output_text += "---\n\n"
        
        output_text += "## 👥 **คลังตัวละครหลัก (Character Bible):**\n"
        for char in data.get('main_characters', []):
            output_text += f"* 🎭 **{char.get('name_th', '')} ({char.get('role_th', '')}):** {char.get('personality_th', '')}\n"
            output_text += f"  - *Visual Prompt:* `{char.get('visual_prompt_en', '')}`\n\n"
        
        output_text += "---\n\n"
        
        for ep in data.get('episodes', []):
            output_text += f"## 📺 **EP {ep.get('ep_number', 1)}: {ep.get('ep_title_th', '')}**\n"
            output_text += f"📖 **เรื่องย่อ:** {ep.get('ep_synopsis_th', '')}\n\n"
            
            for scene in ep.get('scenes', []):
                output_text += f"🎥 **Scene {scene.get('scene_number', 1)}**\n"
                output_text += f"🎬 **มุมกล้อง/การแสดง:** {scene.get('camera_and_action_th', '')}\n"
                output_text += f"🗣️ **บทพากย์ไทย:** {scene.get('voiceover_th', '')}\n"
                output_text += f"✨ **Video Prompt (วางใน Google Flow):**\n`{scene.get('video_prompt_en', '')}`\n\n"
                output_text += "```\n" + scene.get('video_prompt_en', '') + "\n```\n"
                output_text += "–"*30 + "\n"
            output_text += "\n" + "="*40 + "\n\n"
            
        yield output_text, image_url
        
    except Exception as e:
        yield f"❌ เกิดข้อผิดพลาด: {str(e)}\n(โปรดตรวจสอบว่า Gemini API Key ถูกต้องหรือไม่)", None

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
                image_output = gr.Image(label="🖼️ ภาพตัวละครหลัก (Master Reference)", height=350)
                output_text = gr.Markdown(label="📄 บทซีรีส์ คลังตัวละคร และ Video Prompts")

    submit_btn.click(
        fn=generate_dynamic_series,
        inputs=[api_key_input, genre_input, ep_count_input, detail_input, avoid_input],
        outputs=[output_text, image_output]
    )
    
    clear_btn.click(fn=lambda: ("", "สู้ชีวิต / หักมุม / สร้างแรงบันดาลใจ", "5", "", "", None, None), 
                    outputs=[api_key_input, genre_input, ep_count_input, detail_input, avoid_input, output_text, image_output])

port = int(os.environ.get("PORT", 7860))
app.launch(server_name="0.0.0.0", server_port=port)
