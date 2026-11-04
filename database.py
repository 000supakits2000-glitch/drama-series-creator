import sqlite3

def init_db():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            credits INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    # เพิ่มความเข้มงวด: ตรวจสอบความยาวและรูปแบบข้อมูล
    if not username or len(username.strip()) < 3:
        return "❌ ชื่อผู้ใช้ (Username) ต้องมีความยาวอย่างน้อย 3 ตัวอักษรขึ้นไปครับ"
    if not password or len(password.strip()) < 6:
        return "❌ รหัสผ่าน (Password) ต้องมีความยาวอย่างน้อย 6 ตัวอักษรขึ้นไปครับ"
    
    try:
        conn = sqlite3.connect("users.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, credits) VALUES (?, ?, 0)", (username.strip(), password))
        conn.commit()
        conn.close()
        return "✓ สมัครสมาชิกสำเร็จ! สามารถเข้าสู่ระบบ 'เข้าสู่ระบบ' ได้เลยครับ"
    except sqlite3.IntegrityError:
        return "❌ ชื่อผู้ใช้ถูกใช้งานไปแล้ว กรุณาใช้ชื่ออื่น"

def verify_user(username, password):
    if not username or not password:
        return False, 0
    conn = sqlite3.connect("users.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT credits FROM users WHERE username = ? AND password = ?", (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return True, row[0]
    return False, 0

def get_or_create_admin():
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
    return admin_name, 999

def check_and_deduct_credit(username, cost=1):
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
