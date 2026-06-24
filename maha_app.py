from flask import Flask, render_template, redirect, request
import sqlite3

app = Flask(__name__)

DATABASE = "maha_clubs.db"


def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clubs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_name TEXT NOT NULL,
        club_description TEXT NOT NULL,
        category TEXT NOT NULL,
        members INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS joined_clubs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_id INTEGER NOT NULL,
        student_name TEXT NOT NULL
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM clubs")
    total_clubs = cursor.fetchone()[0]

    if total_clubs == 0:
        cursor.execute("""
        INSERT INTO clubs(club_name, club_description, category, members)
        VALUES
        ('Robotics Club', 'Students learn robotics, coding, electronics, and smart technology projects.', 'Technology', 25),
        ('Coding Club', 'Students learn programming, websites, applications, and software development.', 'Technology', 17),
        ('Debate Club', 'Students improve public speaking, confidence, and critical thinking skills.', 'Communication', 13),
        ('Photography Club', 'Students learn photography, photo editing, and creative visual skills.', 'Creative', 21),
        ('Badminton Club', 'Students join badminton training, friendly matches, and competitions.', 'Sports', 30),
        ('Entrepreneurship Club', 'Students learn business, marketing, sales, and event planning.', 'Business', 18)
        """)

    conn.commit()
    conn.close()


create_tables()


@app.route('/')
@app.route('/student-clubs')
def student_clubs():
    conn = connect_db()

    clubs = conn.execute("""
        SELECT clubs.*,
        CASE
            WHEN joined_clubs.id IS NOT NULL THEN 1
            ELSE 0
        END AS joined
        FROM clubs
        LEFT JOIN joined_clubs
        ON clubs.id = joined_clubs.club_id
    """).fetchall()

    conn.close()

    message = request.args.get("message")

    return render_template("student_clubs.html", clubs=clubs, message=message)


@app.route('/join/<int:club_id>', methods=['POST'])
def join_club(club_id):
    student_name = request.form['student_name']

    conn = connect_db()

    existing = conn.execute("""
        SELECT * FROM joined_clubs
        WHERE club_id = ?
    """, (club_id,)).fetchone()

    if existing is None:
        conn.execute("""
            INSERT INTO joined_clubs(club_id, student_name)
            VALUES(?, ?)
        """, (club_id, student_name))

        conn.execute("""
            UPDATE clubs
            SET members = members + 1
            WHERE id = ?
        """, (club_id,))

        conn.commit()
        conn.close()

        return redirect('/student-clubs?message=joined')

    conn.close()

    return redirect('/student-clubs?message=already_joined')


@app.route('/my-clubs')
@app.route('/my_clubs')
def my_clubs():
    conn = connect_db()

    clubs = conn.execute("""
        SELECT clubs.*, joined_clubs.student_name
        FROM clubs
        JOIN joined_clubs
        ON clubs.id = joined_clubs.club_id
    """).fetchall()

    conn.close()

    message = request.args.get("message")

    return render_template("my_clubs.html", clubs=clubs, message=message)


@app.route('/exit/<int:club_id>')
def exit_club(club_id):
    conn = connect_db()

    existing = conn.execute("""
        SELECT * FROM joined_clubs
        WHERE club_id = ?
    """, (club_id,)).fetchone()

    if existing:
        conn.execute("""
            DELETE FROM joined_clubs
            WHERE club_id = ?
        """, (club_id,))

        conn.execute("""
            UPDATE clubs
            SET members = members - 1
            WHERE id = ? AND members > 0
        """, (club_id,))

    conn.commit()
    conn.close()

    return redirect('/my-clubs?message=exited')


if __name__ == '__main__':
    app.run(debug=True, port=5050)