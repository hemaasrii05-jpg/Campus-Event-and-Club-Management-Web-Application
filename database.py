import sqlite3

# connect to a sqlite database file
conn = sqlite3.connect("students.db")

# create cursor
cursor = conn.cursor()

# create table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        password TEXT
    )
    """
)

# insert sample data
cursor.execute(
    "INSERT INTO students (name, email, password) VALUES (?, ?, ?)",
    ("Mahavarshani", "mahavarshani@example.com", "30003")
)

# save changes
conn.commit()

# read data
cursor.execute("SELECT * FROM students")
rows = cursor.fetchall()

for row in rows:
    print(row)

# close connection
conn.close()