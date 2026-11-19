import sqlite3

# Connect to database (creates database.db automatically)
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create sys_command table for native Windows desktop applications[cite: 1, 2, 3]
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sys_command (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100),
        path VARCHAR(255)
    )
""")

# Create web_command table for website/web shortcut routing[cite: 1, 2, 3]
cursor.execute("""
    CREATE TABLE IF NOT EXISTS web_command (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100),
        url VARCHAR(255)
    )
""")

# Default Windows system application paths
sys_commands = [
    ("notepad", "C:\\Windows\\notepad.exe"),
    ("calculator", "C:\\Windows\\System32\\calc.exe"),
    ("paint", "C:\\Windows\\System32\\mspaint.exe"),
    ("command prompt", "C:\\Windows\\System32\\cmd.exe"),
]

cursor.executemany(
    "INSERT OR IGNORE INTO sys_command (name, path) VALUES (?, ?)",
    sys_commands,
)

# Default web commands / shortcuts
web_commands = [
    ("youtube", "https://www.youtube.com"),
    ("google", "https://www.google.com"),
    ("chatgpt", "https://chatgpt.com"),
    ("github", "https://github.com"),
]

cursor.executemany(
    "INSERT OR IGNORE INTO web_command (name, url) VALUES (?, ?)",
    web_commands,
)

conn.commit()
conn.close()

print("Database 'database.db' initialized successfully with Windows configurations!")