import os
import psycopg2
from psycopg2.extras import RealDictCursor

# ดึง Connection String จาก Environment Variable หรือใช้ลิงก์โดยตรง
# แนะนำให้ตั้งค่า DB_URL บน Render หรือใส่ Direct Connection URI ของ Supabase ที่เปลี่ยนรหัสผ่านแล้วตรงนี้
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
    """สร้างตารางที่จำเป็นใน Supabase หากยังไม่มี"""
    conn = get_db_connection()
    if not conn:
        return
    
    with conn.cursor() as cur:
        # ตารางผู้ใช้งาน (Users)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                credits INTEGER DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # ตารางประวัติบทละคร (Drama History - บันทึกย่อ/เนื้อหา)
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

# --- ระบบจัดการสมาชิก & เครดิต ---

def register_user(username, password):
    """ลงทะเบียนผู้ใช้ใหม่ (แจกฟรี 10 เครดิต)"""
    conn = get_db_connection()
    if not conn:
        return False, "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password, credits) VALUES (%s, %s, 10)",
                (username, password)
            )
            conn.commit()
        return True, "ลงทะเบียนสำเร็จ! ได้รับฟรี 10 เครดิต"
    except psycopg2.IntegrityError:
        return False, "ชื่อผู้ใช้นี้มีในระบบแล้ว"
    except Exception as e:
        return False, f"เกิดข้อผิดพลาด: {str(e)}"
    finally:
        conn.close()

def login_user(username, password):
    """ตรวจสอบการล็อกอิน"""
    conn = get_db_connection()
    if not conn:
        return False, "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        user = cur.fetchone()
    conn.close()
    
    if user:
        return True, user
    return False, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"

def get_user_credits(username):
    """ดึงจำนวนเครดิตคงเหลือ"""
    conn = get_db_connection()
    if not conn:
        return 0
    
    with conn.cursor() as cur:
        cur.execute("SELECT credits FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
    conn.close()
    
    return result[0] if result else 0

def deduct_credit(username, amount=1):
    """หักเครดิตผู้ใช้งานเมื่อเจนบทละคร"""
    conn = get_db_connection()
    if not conn:
        return False
    
    with conn.cursor() as cur:
        cur.execute("SELECT credits FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        
        if result and result[0] >= amount:
            cur.execute(
                "UPDATE users SET credits = credits - %s WHERE username = %s",
                (amount, username)
            )
            conn.commit()
            conn.close()
            return True
            
    conn.close()
    return False

# --- ระบบจัดการประวัติบทละคร (จำกัดไม่เกิน 10 เรื่องล่าสุด) ---

def save_drama_history(user_id, title, content):
    """บันทึกบทละครลงประวัติ และลบเรื่องที่เกิน 10 เรื่องให้อัตโนมัติ"""
    conn = get_db_connection()
    if not conn:
        return False
    
    with conn.cursor() as cur:
        # 1. บันทึกบทละครเรื่องใหม่
        cur.execute(
            "INSERT INTO drama_history (user_id, title, content) VALUES (%s, %s, %s)",
            (user_id, title, content)
        )
        
        # 2. ลบเรื่องเก่าที่เกิน 10 เรื่องล่าสุดออกทันทีเพื่อประหยัดพื้นที่ Free Tier
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

def get_user_history(user_id):
    """ดึงรายการประวัติบทละคร 10 เรื่องล่าสุดของผู้ใช้"""
    conn = get_db_connection()
    if not conn:
        return []
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, title, content, created_at 
            FROM drama_history 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 10
        """, (user_id,))
        history = cur.fetchall()
    conn.close()
    return history
