from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)
DATABASE = "student_clubs.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def setup_database():
    connection = get_db_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            members INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    count = connection.execute("SELECT COUNT(*) FROM clubs").fetchone()[0]

    if count == 0:
        connection.executemany(
            """
            INSERT INTO clubs (name, description, category, members)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    "Coding Club",
                    "Students learn programming, websites, and simple software projects.",
                    "Technology",
                    12,
                ),
                (
                    "Robotics Club",
                    "Students build basic robots and learn about sensors and automation.",
                    "Technology",
                    8,
                ),
                (
                    "Photography Club",
                    "Students practise photography and help capture campus activities.",
                    "Creative",
                    15,
                ),
                (
                    "Debate Club",
                    "Students improve public speaking, confidence, and critical thinking.",
                    "Communication",
                    10,
                ),
            ],
        )

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("student_clubs.html")


@app.route("/student-clubs")
def student_clubs_page():
    return render_template("student_clubs.html")


@app.route("/api/clubs")
def get_clubs():
    connection = get_db_connection()
    clubs = connection.execute("SELECT * FROM clubs ORDER BY name").fetchall()
    connection.close()

    club_list = []
    for club in clubs:
        club_list.append(
            {
                "id": club["id"],
                "name": club["name"],
                "description": club["description"],
                "category": club["category"],
                "members": club["members"],
            }
        )

    return jsonify(club_list)


@app.route("/api/clubs/<int:club_id>/join", methods=["POST"])
def join_club(club_id):
    connection = get_db_connection()
    club = connection.execute("SELECT * FROM clubs WHERE id = ?", (club_id,)).fetchone()

    if club is None:
        connection.close()
        return jsonify({"message": "Club not found."}), 404

    connection.execute(
        "UPDATE clubs SET members = members + 1 WHERE id = ?",
        (club_id,),
    )
    connection.commit()
    connection.close()

    return jsonify({"message": "You joined the club successfully!"})


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)