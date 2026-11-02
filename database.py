import sqlite3

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

def register_user(username, password):
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

def check_and_deduct_credit(username):
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
