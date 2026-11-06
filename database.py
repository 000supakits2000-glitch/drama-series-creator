import os
import psycopg2
from psycopg2.extras import RealDictCursor

# ดึง Connection String จาก Environment Variable หรือใส่ลิงก์ตรงนี้ (อย่าลืมเปลี่ยนรหัสผ่านจริง)
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:YOUR_ACTUAL_abdsh893654@db.xxxx.supabase.co:5432/postgres")

def get_db_connection():
    """สร้างและคืนค่าการเชื่อมต่อฐานข้อมูล PostgreSQL (Supabase)"""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

def init_db():
    """สร้างตาราง users และ drama_history หากยังไม่มี"""
    conn = get_db_connection()
    if not conn:
        return
    
    with conn.cursor() as cur:
        # ตารางผู้ใช้งาน
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                credits INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # ตารางประวัติบทละคร (FIFO เก็บ 10 เรื่องล่าสุด)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS drama_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    conn.close()

def register_user(username, password):
    """ลงทะเบียนผู้ใช้ใหม่ พร้อมตรวจสอบความยาว"""
    if not username or len(username.strip()) < 3:
        return "❌ ชื่อผู้ใช้ (Username) ต้องมีความยาวอย่างน้อย 3 ตัวอักษรขึ้นไปครับ"
    if not password or len(password.strip()) < 6:
        return "❌ รหัสผ่าน (Password) ต้องมีความยาวอย่างน้อย 6 ตัวอักษรขึ้นไปครับ"
    
    conn = get_db_connection()
    if not conn:
        return "❌ ไม่สามารถเชื่อมต่อฐานข้อมูลได้"
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password, credits) VALUES (%s, %s, 10)",
                (username.strip(), password)
            )
            conn.commit()
        return "✓ สมัครสมาชิกสำเร็จ! สามารถเข้าสู่ระบบได้เลยครับ"
    except psycopg2.IntegrityError:
        return "❌ ชื่อผู้ใช้ถูกใช้งานไปแล้ว กรุณาใช้ชื่ออื่น"
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {str(e)}"
    finally:
        conn.close()

def verify_user(username, password):
    """ตรวจสอบการล็อกอิน (รองรับ GodAdmin bypass)"""
    if username == "GodAdmin" and password == "godpass123":
        return True, 999
        
    conn = get_db_connection()
    if not conn:
        return False, 0
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT credits FROM users WHERE username = %s AND password = %s", (username, password))
        row = cur.fetchone()
    conn.close()
    
    if row:
        return True, row['credits']
    return False, 0

def get_or_create_admin():
    """สร้างหรือรีเซ็ตบัญชี GodAdmin"""
    admin_name = "GodAdmin"
    conn = get_db_connection()
    if not conn:
        return admin_name, 999
    
    with conn.cursor() as cur:
        cur.execute("SELECT credits FROM users WHERE username = %s", (admin_name,))
        row = cur.fetchone()
        if not row:
            cur.execute(
                "INSERT INTO users (username, password, credits) VALUES (%s, %s, %s) ON CONFLICT (username) DO UPDATE SET credits = 999",
                (admin_name, "godpass123", 999)
            )
        else:
            cur.execute("UPDATE users SET credits = 999 WHERE username = %s", (admin_name,))
        conn.commit()
    conn.close()
    return admin_name, 999

def check_and_deduct_credit(username):
    """ตรวจสอบและหักเครดิตผู้ใช้เมื่อเจนบทละคร"""
    if username == "GodAdmin":
        return True, 999
    
    conn = get_db_connection()
    if not conn:
        return False, 0
    
    with conn.cursor() as cur:
        cur.execute("SELECT credits FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if row and row[0] > 0:
            new_credits = row[0] - 1
            cur.execute("UPDATE users SET credits = %s WHERE username = %s", (new_credits, username))
            conn.commit()
            conn.close()
            return True, new_credits
            
    conn.close()
    return False, 0

def save_drama_history(user_id, title, content):
    """บันทึกประวัติบทละคร (จำกัดไม่เกิน 10 เรื่องล่าสุด)"""
    conn = get_db_connection()
    if not conn:
        return False
    
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO drama_history (user_id, title, content) VALUES (%s, %s, %s)",
            (user_id, title, content)
        )
        cur.execute("""
            DELETE FROM drama_history
            WHERE user_id = %s
              AND id NOT IN (
                SELECT id FROM drama_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 10
              );
        """, (user_id, user_id))
        conn.commit()
    conn.close()
    return True
