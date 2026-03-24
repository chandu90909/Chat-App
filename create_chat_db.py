import sqlite3

conn = sqlite3.connect('chat.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    room TEXT,
    message TEXT
)
''')

print("✅ Chat DB created!")

conn.close()