# creating initital database and csv file
import csv
import sqlite3

conn = sqlite3.connect('student.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE Student(
    stu_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cg TEXT NOT NULL,
    email TEXT NOT NULL,
    password NOT NULL,
    w_letter INTEGER,
);
""")
cursor.execute("""
CREATE TABLE Submission (
    assg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    due_date TEXT,
);
""")
cursor.execute("""
CREATE TABLE StudentSubmission (
    stu_id INTEGER,
    assg_id TEXT,
    status TEXT,
    

    FOREIGN KEY (stu_id) REFERENCES Student(stu_id),
    FOREIGN KEY (assg_id) REFERENCES Submission(assg_id)
);
""")

conn.commit() # make changes to db
conn.close() # close the connection

# file closes after with block
with open("student.csv", 'w') as file:
    writer = csv.writer(file)
    writer.writerow(['Student', 'cg', 'Remarks'])
                    
