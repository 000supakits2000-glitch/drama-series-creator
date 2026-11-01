# 1. ติดตั้งไลบรารีที่จำเป็น
!pip install -q gradio google-genai

import gradio as gr
import json
import urllib.parse
import os
from google import genai
from google.genai import types
from google.colab import userdata

# ดึง API Key จาก Secrets (รูปแม่กุญแจด้านซ้าย) อัตโนมัติ
try:
    MY_GEMINI_KEY = userdata.get('GEMINI_API_KEY')
except:
    MY_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

def generate_dynamic_series(genre_choice, ep_count, custom_detail, avoided_topics):
    if not MY_GEMINI_KEY:
        yield "❌ ไม่พบ GEMINI_API_KEY ใน Secrets (รูปแม่กุญแจด้านซ้าย) กรุณาตั้งค่าก่อนครับ", None
        return
        
    try:
        num_episodes = int(ep_count)
        yield f"⏳ **กำลังคิดพล็อตซีรีส์ {num_episodes} ตอน (อัดแน่น 4-5 ซีนต่อตอน) กำลังเขียนบท... กรุณารอสักครู่ครับ**", None
        
        client = genai.Client(api_key=MY_GEMINI_KEY)
        
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
        Each episode MUST contain EXACTLY 4 to 5 detailed scenes (Scene 1, Scene 2, Scene 3, Scene 4, and Scene 5) to ensure a rich, immersive, and well-paced narrative. Avoid short or rushed episodes.

        Additional Details: {custom_detail if custom_detail else 'Create a unique, emotional, and well-paced multi-episode storyline.'}
        
        {avoid_instruction}
        
        CRITICAL CHARACTER & NAME REQUIREMENT:
        Create at least 3 distinct, highly diverse characters. 
        Ensure their Thai full names and nicknames are creative, modern, highly diverse, natural, and non-generic. Provide detailed English visual prompts for each.

        Provide the response strictly in this exact JSON format:
        {{
          "series_title": "Title in Thai (English Title)",
          "genre": "{selected_genre}",
          "total_episodes": {num_episodes},
          "logline_th": "Logline of the whole series in Thai",
          "main_characters": [
            {{
              "name_th": "ชื่อ-นามสกุล และชื่อเล่นตัวละคร 1 (ไทย)",
              "role_th": "บทบาท",
              "personality_th": "นิสัย/จุดเด่น",
              "visual_prompt_en": "Detailed English visual prompt: age, ethnicity, facial expression, hairstyle, unique clothing, cinematic lighting"
            }},
            {{
              "name_th": "ชื่อ-นามสกุล และชื่อเล่นตัวละคร 2 (ไทย)",
              "role_th": "บทบาท",
              "personality_th": "นิสัย/จุดเด่น",
              "visual_prompt_en": "Detailed English visual prompt: age, distinct facial features, outfit, lighting"
            }},
            {{
              "name_th": "ชื่อ-นามสกุล และชื่อเล่นตัวละคร 3 (ไทย)",
              "role_th": "บทบาท",
              "personality_th": "นิสัย/จุดเด่น",
              "visual_prompt_en": "Detailed English visual prompt: age, distinct outfit, expressive look"
            }}
          ],
          "episodes": [
            {{
              "ep_number": 1,
              "ep_title_th": "ชื่อตอนที่ 1 (ภาษาไทย)",
              "ep_synopsis_th": "เรื่องย่อตอนที่ 1",
              "scenes": [
                {{
                  "scene_number": 1,
                  "camera_and_action_th": "รายละเอียดการแสดงและมุมกล้องภาษาไทย",
                  "voiceover_th": "บทพากย์/บทพูดภาษาไทย",
                  "video_prompt_en": "Complete cinematic video prompt in English"
                }},
                {{ "scene_number": 2, "camera_and_action_th": "...", "voiceover_th": "...", "video_prompt_en": "..." }},
                {{ "scene_number": 3, "camera_and_action_th": "...", "voiceover_th": "...", "video_prompt_en": "..." }},
                {{ "scene_number": 4, "camera_and_action_th": "...", "voiceover_th": "...", "video_prompt_en": "..." }}
              ]
            }}
            /* MUST generate all episodes up to ep_number {num_episodes} in sequence, each with 4-5 scenes */
          ]
        }}
        """

        # ใช้โมเดล gemini-3.8-flash ล่าสุด
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.85
            )
        )
        
        data = json.loads(response.text)
        
        yield f"⏳ **บทซีรีส์ {num_episodes} ตอน (ซีนแน่นๆ) พร้อมแล้ว! กำลังเจนรูป Master ตัวละครหลัก...**, ", None
        
        # เจนรูป Master ตัวละครหลักคนแรก
        main_char = data.get('main_characters', [{}])[0]
        char_prompt = main_char.get('visual_prompt_en', 'Cinematic portrait of main character, 8k')
        encoded_prompt = urllib.parse.quote(f"cinematic character portrait, {char_prompt}, 8k resolution, photorealistic")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&nologo=true"

        # จัดฟอร์แมตข้อความ
        output_text = f"# 🎬 **ซีรีส์เรื่อง:** {data.get('series_title', '')}\n"
        output_text += f"📌 **แนวเรื่อง:** {data.get('genre', '')} (จำนวน {data.get('total_episodes', num_episodes)} ตอน | 4-5 ซีนต่อตอน)\n"
        output_text += f"💡 **Logline:** {data.get('logline_th', '')}\n\n"
        
        output_text += "## 👥 **คลังตัวละครและชื่อที่หลากหลาย (Diverse Character Bible):**\n"
        for char in data.get('main_characters', []):
            output_text += f"* 🎭 **{char.get('name_th', '')} ({char.get('role_th', '')}):** {char.get('personality_th', '')}\n"
            output_text += f"  - *Visual Prompt:* `{char.get('visual_prompt_en', '')}`\n\n"
        
        output_text += "\n" + "="*60 + "\n\n"
        
        # แสดงบทละครตามจำนวนตอนและซีนที่แน่นขึ้น
        for ep in data.get('episodes', []):
            output_text += f"## 📺 **EP {ep.get('ep_number', 1)}: {ep.get('ep_title_th', '')}**\n"
            output_text += f"📖 **เรื่องย่อ:** {ep.get('ep_synopsis_th', '')}\n\n"
            
            for scene in ep.get('scenes', []):
                output_text += f"🎥 **Scene {scene.get('scene_number', 1)}**\n"
                output_text += f"🎬 **มุมกล้อง/การแสดง:** {scene.get('camera_and_action_th', '')}\n"
                output_text += f"🗣️ **บทพากย์ไทย:** {scene.get('voiceover_th', '')}\n"
                output_text += f"✨ **Video Prompt (วางใน Google Flow):**\n`{scene.get('video_prompt_en', '')}`\n\n"
                output_text += "-"*40 + "\n"
            output_text += "\n" + "="*60 + "\n\n"
            
        yield output_text, image_url
        
    except Exception as e:
        yield f"❌ เกิดข้อผิดพลาด: {str(e)}", None

# หน้าจอ UI Gradio
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎬 ระบบสร้างซีรีส์ละครยาว (Rich Scenes Edition - 4-5 Scenes/EP)")
    gr.Markdown("เลือกแนวเรื่อง จำนวนตอน (แต่ละตอนจะมี 4-5 ซีนสมบูรณ์) แล้วกด **Submit** ได้เลยครับ!")
    
    with gr.Row():
        with gr.Column(scale=1):
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
                label="💡 ไอเดียหรือพล็อตหลักของเรื่องนี้ (Optional)"
            )
            avoid_input = gr.Textbox(
                lines=2,
                placeholder="พิมพ์พล็อตเรื่องที่เคยทำไปแล้ว เพื่อห้ามไม่ให้ AI ซ้ำ...",
                label="🚫 พล็อตหรือเนื้อหาที่เคยทำแล้ว (ห้ามซ้ำเด็ดขาด)"
            )
            with gr.Row():
                clear_btn = gr.Button("Clear")
                submit_btn = gr.Button("Submit (สร้างซีรีส์ ซีนแน่นๆ)", variant="primary")
                
        with gr.Column(scale=1):
            image_output = gr.Image(label="🖼️ ภาพตัวละครหลัก (Master Reference)")
            output_text = gr.Markdown(label="📄 โครงเรื่อง คลังตัวละคร และบทละครรายตอน")

    submit_btn.click(
        fn=generate_dynamic_series,
        inputs=[genre_input, ep_count_input, detail_input, avoid_input],
        outputs=[output_text, image_output]
    )
    
    clear_btn.click(fn=lambda: ("", "5", "", "", None, None), outputs=[detail_input, ep_count_input, avoid_input, output_text, image_output])

app.launch(share=True, debug=False, inline=False)
