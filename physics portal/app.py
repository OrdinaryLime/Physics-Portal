from flask import Flask, render_template, redirect, request, url_for
import csv
import sqlite3

app = Flask(__name__)
ad_details = ('lemon@admin', 'iamadmin')

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        details = (email, password)
        # connection closes after with block
        with sqlite3.connect("student.db") as conn:
            cursor = conn.cursor()

        cursor.execute("""
            SELECT email, password FROM Student;
        """)

        stored = cursor.fetchall()
        if details == ad_details:
            return redirect(url_for("admin"))
        elif details not in stored:
            message = "Username or password is wrong"
            return render_template("login.html", message=message)
        else:
            return redirect(url_for("student", email=stored[0]))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = str(request.form["name"])
        cg = str(request.form["cg"])
        email = str(request.form["email"])
        password = str(request.form["password"])
        details = (email, password)
        # connection closes after with block
        with sqlite3.connect("student.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT email, password FROM Student;
            """)
            stored = cursor.fetchall()
            if details in stored:
                message = "Username or password already exists"
            else:
                message = "Successfully registered"
                cursor.execute("""
                    INSERT INTO Student(name, cg, email, password)
                    VALUES (?, ?, ?, ?)
                    """,(name, cg, email, password))
                conn.commit() # make changes to db
            
    
        return render_template("register.html", message=message)
    
    return render_template("register.html")

@app.route("/admin/student", methods=["GET","POST"])
def admin():
    stored = ()
    if request.method == "POST":
        stu_name = request.form["stu_name"]
        status = request.form["status"]
        with sqlite3.connect("student.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Submission.name, Submission.due_date, StudentSubmission.status
                FROM Student
                INNER JOIN StudentSubmission
                ON Student.stu_id = StudentSubmission.stu_id
                INNER JOIN Submission
                ON StudentSubmission.assg_id = Submission.assg_id
                WHERE StudentSubmission.status = (?) AND Student.name = (?);
            """,(status, stu_name))
            stored = cursor.fetchall()
        if stored == ():
            name = 'No student found'
        else:
            name = stu_name
        return render_template("admin.html", stored=stored, name=name)
    return render_template("admin.html")

@app.route("/admin/assg", methods=["GET","POST"])
def assg():
    stored = ()
    if request.method == "POST":
        assg_name = request.form["assg_name"]
        status = request.form["status"]
        if status == 'all':
            status = ['completed', 'incomplete', 'overdue']
            placeholders = ', '.join(['?'] * len(status))
            query = f"""
                SELECT Student.name, StudentSubmission.status
                FROM Student
                INNER JOIN StudentSubmission
                ON Student.stu_id = StudentSubmission.stu_id
                INNER JOIN Submission
                ON StudentSubmission.assg_id = Submission.assg_id
                WHERE StudentSubmission.status IN ({placeholders}) AND Submission.name = ?;
            """
            params = (*status, assg_name)
        else:
            query = """
                SELECT Student.name, StudentSubmission.status
                FROM Student
                INNER JOIN StudentSubmission
                ON Student.stu_id = StudentSubmission.stu_id
                INNER JOIN Submission
                ON StudentSubmission.assg_id = Submission.assg_id
                WHERE StudentSubmission.status = ? AND Submission.name =?;
            """
            params = (status, assg_name)
        with sqlite3.connect("student.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            stored = cursor.fetchall()
        if stored == ():
            name = 'No assignment found'
        else:
            name = assg_name
        return render_template("assignment.html", stored=stored, name=name)
    return render_template("assignment.html")

@app.route("/admin/new", methods=["GET","POST"])
def new():
    if request.method == "POST":
        assg_name = request.form["assg_name"]
        due_date = request.form["due_date"]
        with sqlite3.connect("student.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Submission(name, due_date)
                VALUES (?, ?);
            """,(assg_name, due_date))
            cursor.execute("""
                SELECT COUNT(stu_id)
                FROM Student;
            """)
            stu_total = cursor.fetchone()[0]
            cursor.execute("""
                SELECT assg_id
                FROM Submission
                WHERE name = ?;
                """,(assg_name,))
            assg_id = cursor.fetchone()[0]
            for stu_id in range(1, stu_total + 1):
                cursor.execute("""
                    INSERT INTO StudentSubmission (stu_id, assg_id, status)
                    VALUES (?, ?, 'incomplete'); 
                    """,(stu_id, assg_id))
            conn.commit()
    return render_template("new.html")

@app.route("/admin/update", methods=["GET", "POST"])
def update():
    message = ""
    if request.method == "POST":
        assg_name = request.form["assg_name"]
        status = request.form["status"]
        stu_list = request.form["stu_list"]
        if ',' in stu_list:
            stu_list = stu_list.split(',')
        else:
            stu_list = [stu_list]
        with sqlite3.connect("student.db") as conn:
            cursor = conn.cursor()
            for student in stu_list:
                cursor.execute("""
                    SELECT stu_id
                    FROM Student
                    WHERE name = ?;
                """,(student,))
                stu_id = cursor.fetchone()
                if stu_id is None:
                    message = f"Student {student} not found."
                    return render_template("update.html", message=message)
                else:
                    stu_id = stu_id[0]
                    cursor.execute("""
                        UPDATE StudentSubmission
                        SET status = ?
                        WHERE stu_id = ? AND assg_id = (
                            SELECT assg_id FROM Submission WHERE name = ?
                        );
                    """,(status, stu_id, assg_name))
                    message = "Update successful"
                    conn.commit()    
    return render_template("update.html", message=message)

@app.route("/admin/notes", methods=["GET","POST"])
def notes():
    return render_template("notes.html")

@app.route("/admin/notes1", methods=["GET","POST"])
def notes1():
    if request.method == "POST":
        name = request.form["name"]
        remarks = f"Student {name} not found"
        # file closes after with block
        with open("student.csv", 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == name:
                    remarks = row[2]
                next(file)
        return render_template("notes.html", remarks=remarks, name=name)
    return render_template("notes.html")

@app.route("/admin/notes2", methods=["GET","POST"])
def notes2():
    if request.method == "POST":
        name = request.form['name']
        remarks = request.form["remarks"]
        message = f"Student {name} not found"
        # file closes after with block
        with open("student.csv", 'r') as file:
            reader = csv.reader(file)
            row_list = []
            for row in reader:
                if row[0] == name:
                    message = 'Updated'
                    if remarks == 'clear':
                        row[2] = ""
                        message = 'cleared'
                    else:
                        row[2] = row[2] + f'\n{remarks}'
                row_list.append(row)
                next(file)
        # file closes after with block
        with open("student.csv", "w") as file:
            writer = csv.writer(file)
            writer.writerows(row_list)
    
    return render_template("notes.html", message=message, remarks=None)


@app.route("/student")
def student():
    email = request.args.get('email')
    # connection closes after with block
    with sqlite3.connect("student.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name
            FROM Student
            WHERE email = ?;
        """,(email,))
        name = cursor.fetchone()[0]
        cursor.execute("""
            SELECT Submission.name, Submission.due_date, StudentSubmission.status
            FROM Submission
            INNER JOIN StudentSubmission
            ON Submission.assg_id = StudentSubmission.assg_id
            INNER JOIN Student
            ON StudentSubmission.stu_id = Student.stu_id
            WHERE Student.name = ?;
        """,(name,))
        details = cursor.fetchall()
        # file closes after with block
        with open("student.csv", 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row == []:
                    continue
                elif row[0] == name:
                    remarks = row[2]
    return render_template('student.html', name=name, details=details, remarks=remarks)

if __name__ == "__main__":
    app.run(debug=True, port=3294)




