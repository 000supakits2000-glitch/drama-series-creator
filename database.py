import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# ดึง Connection String จาก Environment Variable
DB_URL = os.getenv("DATABASE_URL")

# สร้าง Connection Pool แบบ Thread-safe (เก็บสำรองไว้ 1-20 connections)
try:
    db_pool = psycopg2.pool.ThreadedConnectionPool(1, 20, DB_URL)
except Exception as e:
    print(f"Error initializing connection pool: {e}")
    db_pool = None

def get_db_connection():
    """ดึง Connection ที่ว่างอยู่จาก Pool"""
    try:
        if db_pool:
            return db_pool.getconn()
        return None
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

def release_db_connection(conn):
    """คืน Connection กลับสู่ Pool เพื่อให้คิวรีอื่นนำไปใช้ต่อ"""
    try:
        if db_pool and conn:
            db_pool.putconn(conn)
    except Exception as e:
        print(f"Error releasing connection: {e}")

def init_db():
    """สร้างตาราง users และ drama_history หากยังไม่มี"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
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
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
    finally:
        release_db_connection(conn)

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
        release_db_connection(conn)

def verify_user(username, password):
    """ตรวจสอบการล็อกอิน (รองรับ GodAdmin bypass)"""
    if username == "GodAdmin" and password == "godpass123":
        return True, 999
        
    conn = get_db_connection()
    if not conn:
        return False, 0
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT credits FROM users WHERE username = %s AND password = %s", (username, password))
            row = cur.fetchone()
        
        if row:
            return True, row['credits']
        return False, 0
    except Exception as e:
        print(f"Login error: {e}")
        return False, 0
    finally:
        release_db_connection(conn)

def get_or_create_admin():
    """สร้างหรือรีเซ็ตบัญชี GodAdmin"""
    admin_name = "GodAdmin"
    conn = get_db_connection()
    if not conn:
        return admin_name, 999
    
    try:
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
        return admin_name, 999
    finally:
        release_db_connection(conn)

def check_and_deduct_credit(username, cost=1):
    """ตรวจสอบและหักเครดิตผู้ใช้"""
    conn = get_db_connection()
    if not conn:
        return False, "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"
        
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT credits FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            
            if not result:
                return False, "ไม่พบข้อมูลผู้ใช้"
                
            current_credits = result[0]
            
            if current_credits < cost:
                return False, "เครดิตของคุณหมดแล้ว! กรุณาเติมเครดิตก่อนสร้างซีรีส์"
                
            new_credits = current_credits - cost
            cur.execute("UPDATE users SET credits = %s WHERE username = %s", (new_credits, username))
            conn.commit()
            
            return True, f"หักเครดิตสำเร็จ เหลือ {new_credits} เครดิต"
            
    except Exception as e:
        return False, str(e)
    finally:
        release_db_connection(conn)

def save_drama_history(user_id, title, content):
    """บันทึกประวัติบทละครแยกตามรายชื่อผู้ใช้ (จำกัดไม่เกิน 10 เรื่องล่าสุด)"""
    conn = get_db_connection()
    if not conn:
        return False
        
    try:
        with conn.cursor() as cur:
            # 1. บันทึกข้อมูลบทละครใหม่
            cur.execute(
                "INSERT INTO drama_history (user_id, title, content) VALUES (%s, %s, %s)",
                (user_id, title, content)
            )
            
            # 2. ลบประวัติเก่าออก ให้เหลือแค่ 10 เรื่องล่าสุดของยูสเซอร์นี้
            cur.execute("""
                DELETE FROM drama_history
                WHERE user_id = %s
                AND id NOT IN (
                    SELECT id FROM drama_history
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 10
                )
            """, (user_id, user_id))
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False
    finally:
        release_db_connection(conn)

def get_user_history_by_username(username):
    """ดึงประวัติบทละครเฉพาะของผู้ใช้คนปัจจุบัน 10 เรื่องล่าสุด"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT title, content 
                FROM drama_history 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 10
            """, (username,))
            rows = cur.fetchall()
            return rows
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []
    finally:
        release_db_connection(conn)

def refund_credit(username, amount=1):
    """คืนเครดิตให้ผู้ใช้กรณีเกิดข้อผิดพลาดในการรัน AI"""
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET credits = credits + %s WHERE username = %s", (amount, username))
            conn.commit()
    except Exception as e:
        print(f"Refund error: {e}")
    finally:
        release_db_connection(conn)
