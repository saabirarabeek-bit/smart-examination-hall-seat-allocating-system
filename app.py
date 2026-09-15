
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS halls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hall_name TEXT NOT NULL,
                    rows INTEGER NOT NULL,
                    cols INTEGER NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reg_no TEXT NOT NULL,
                    name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    hall_id INTEGER,
                    seat_row INTEGER,
                    seat_col INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_hall', methods=['POST'])
def add_hall():
    hall_name = request.form['hall_name']
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO halls (hall_name, rows, cols) VALUES (?, ?, ?)",
              (hall_name, rows, cols))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_student', methods=['POST'])
def add_student():
    reg_no = request.form['reg_no']
    name = request.form['name']
    subject = request.form['subject']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO students (reg_no, name, subject) VALUES (?, ?, ?)",
              (reg_no, name, subject))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/allocate', methods=['POST'])
def allocate():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM halls")
    halls = c.fetchall()

    c.execute("SELECT * FROM students ORDER BY subject")
    students = c.fetchall()

    student_index = 0
    for hall in halls:
        hall_id, hall_name, rows, cols = hall
        last_subject = None
        for r in range(1, rows + 1):
            for col in range(1, cols + 1):
                if student_index >= len(students):
                    break
                student = students[student_index]
                # avoid same subject in adjacent seat (same row)
                if student[3] == last_subject and student_index + 1 < len(students):
                    students[student_index], students[student_index + 1] = \
                        students[student_index + 1], students[student_index]
                    student = students[student_index]

                c.execute('''UPDATE students SET hall_id=?, seat_row=?, seat_col=?
                             WHERE id=?''', (hall_id, r, col, student[0]))
                last_subject = student[3]
                student_index += 1
    conn.commit()
    conn.close()
    return redirect(url_for('view_seats'))

@app.route('/view_seats')
def view_seats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT students.reg_no, students.name, students.subject,
                        halls.hall_name, students.seat_row, students.seat_col
                 FROM students JOIN halls ON students.hall_id = halls.id
                 ORDER BY halls.hall_name, students.seat_row, students.seat_col''')
    data = c.fetchall()
    conn.close()
    return render_template('view_seats.html', data=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
