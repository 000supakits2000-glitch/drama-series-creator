import sqlite3

DB_NAME = "users.db"

def init_db():
    with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                credits INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

def register_user(username, password):
    # ตรวจสอบความยาวและรูปแบบข้อมูล
    if not username or len(username.strip()) < 3:
        return "❌ ชื่อผู้ใช้ (Username) ต้องมีความยาวอย่างน้อย 3 ตัวอักษรขึ้นไปครับ"
    if not password or len(password.strip()) < 6:
        return "❌ รหัสผ่าน (Password) ต้องมีความยาวอย่างน้อย 6 ตัวอักษรขึ้นไปครับ"
    
    try:
        with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, credits) VALUES (?, ?, 0)", (username.strip(), password))
            conn.commit()
        return "✓ สมัครสมาชิกสำเร็จ! สามารถเข้าสู่ระบบได้เลยครับ"
    except sqlite3.IntegrityError:
        return "❌ ชื่อผู้ใช้ถูกใช้งานไปแล้ว กรุณาใช้ชื่ออื่น"

def verify_user(username, password):
    if not username or not password:
        return False, 0
    with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT credits FROM users WHERE username = ? AND password = ?", (username, password))
        row = cursor.fetchone()
    
    if row:
        return True, row[0]
    return False, 0

def get_or_create_admin():
    admin_name = "GodAdmin"
    with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT credits FROM users WHERE username = ?", (admin_name,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT OR REPLACE INTO users (username, password, credits) VALUES (?, ?, ?)", (admin_name, "godpass123", 999))
        else:
            cursor.execute("UPDATE users SET password = ?, credits = ? WHERE username = ?", ("godpass123", 999, admin_name))
        conn.commit()
    return admin_name, 999

def check_and_deduct_credit(username):
    if username == "GodAdmin":
        return True, 999
    
    with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT credits FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row and row[0] > 0:
            new_credits = row[0] - 1
            cursor.execute("UPDATE users SET credits = ? WHERE username = ?", (new_credits, username))
            conn.commit()
            return True, new_credits
            
    return False, 0
