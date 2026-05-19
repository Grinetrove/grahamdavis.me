import os
import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from BIS372_Delivery2.db import getDb, basePath

bis372Blueprint = Blueprint(
    "bis372",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/BIS372_Delivery2/static",
    url_prefix="/BIS372_Delivery2"
)

documentsPath = os.path.join(basePath, "Documents")
schemaPath = os.path.join(basePath, "schema.sql")

def allowedFile(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"pdf", "doc", "docx"}

@bis372Blueprint.route("/")
def home():
    return render_template("BIS372_Delivery2/home.html")

@bis372Blueprint.route("/sql", methods=["GET", "POST"])
def sqlRunner():
    columns = []
    rows = []
    error = None
    query = ""
    message = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if not query:
            error = "Please enter a SQL query."
        else:
            try:
                conn = getDb()
                cursor = conn.execute(query)

                if cursor.description:
                    # SELECT or other statement that returns rows
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                else:
                    # INSERT, UPDATE, DELETE, etc.
                    conn.commit()
                    message = f"Query executed successfully. {cursor.rowcount} row(s) affected."

                conn.close()
            except Exception as e:
                error = str(e)

    with open(schemaPath, "r") as f:
        schema = f.read()

    return render_template("BIS372_Delivery2/sql_runner.html", columns=columns, rows=rows, error=error, query=query, message=message, schema=schema)

tableJoinQueries = {
    "Instructor": "SELECT * FROM Instructor",
    "Subject": "SELECT * FROM Subject",
    "Course": """
        SELECT c.courseId, s.subjectCode, c.courseNumber, c.courseTitle
        FROM Course c
        JOIN Subject s ON c.subjectId = s.subjectId
    """,
    "Term": "SELECT * FROM Term",
    "CourseOffering": """
        SELECT co.courseOfferingId,
               s.subjectCode || ' ' || c.courseNumber AS course,
               t.academicTerm || ' ' || t.academicYear AS term,
               i.firstName || ' ' || i.lastName AS instructor,
               co.sectionNumber
        FROM CourseOffering co
        JOIN Course c ON co.courseId = c.courseId
        JOIN Subject s ON c.subjectId = s.subjectId
        JOIN Term t ON co.termId = t.termId
        JOIN Instructor i ON co.instructorId = i.instructorId
    """,
    "Syllabus": """
        SELECT sy.syllabusId,
               s.subjectCode || ' ' || c.courseNumber AS course,
               t.academicTerm || ' ' || t.academicYear AS term,
               i.firstName || ' ' || i.lastName AS instructor,
               sy.fileName,
               sy.filePath,
               sy.uploadDate
        FROM Syllabus sy
        JOIN CourseOffering co ON sy.courseOfferingId = co.courseOfferingId
        JOIN Course c ON co.courseId = c.courseId
        JOIN Subject s ON c.subjectId = s.subjectId
        JOIN Term t ON co.termId = t.termId
        JOIN Instructor i ON co.instructorId = i.instructorId
    """
}

tableNames = list(tableJoinQueries.keys())


@bis372Blueprint.route("/tables", methods=["GET"])
def tableViewer():
    selectedTable = request.args.get("table", "Instructor")
    columns = []
    rows = []

    if selectedTable in tableJoinQueries:
        try:
            conn = getDb()
            cursor = conn.execute(tableJoinQueries[selectedTable])
            columns = [description[0] for description in cursor.description] if cursor.description else []
            rows = [list(row) for row in cursor.fetchall()]
            conn.close()
        except Exception:
            pass

    return render_template(
        "BIS372_Delivery2/table_viewer.html",
        tableNames=tableNames,
        selectedTable=selectedTable,
        columns=columns,
        rows=rows
    )


@bis372Blueprint.route("/documents/<path:filename>")
def downloadDocument(filename):
    return send_from_directory(documentsPath, filename)


@bis372Blueprint.route("/upload", methods=["GET", "POST"])
def uploadSyllabus():
    success = False
    error = None

    if request.method == "POST":
        firstName = request.form.get("firstName", "").strip()
        lastName = request.form.get("lastName", "").strip()
        email = request.form.get("email", "").strip()
        subjectCode = request.form.get("subjectCode", "").strip().upper()
        subjectName = request.form.get("subjectName", "").strip()
        courseNumber = request.form.get("courseNumber", "").strip()
        courseTitle = request.form.get("courseTitle", "").strip()
        academicTerm = request.form.get("academicTerm", "").strip()
        academicYear = request.form.get("academicYear", "").strip()
        sectionNumber = request.form.get("sectionNumber", "").strip() or None
        file = request.files.get("file")

        if not all([firstName, lastName, email, subjectCode, subjectName, courseNumber, courseTitle, academicTerm, academicYear]):
            error = "All fields except section number are required."
        elif not file or file.filename == "":
            error = "A syllabus file is required."
        elif not allowedFile(file.filename):
            error = "Only .pdf, .doc, and .docx files are allowed."
        else:
            try:
                conn = getDb()
                row = conn.execute("SELECT instructorId FROM Instructor WHERE email = ?", (email,)).fetchone()
                if row:
                    instructorId = row["instructorId"]
                else:
                    cursor = conn.execute(
                        "INSERT INTO Instructor (firstName, lastName, email) VALUES (?, ?, ?)",
                        (firstName, lastName, email)
                    )
                    instructorId = cursor.lastrowid

                row = conn.execute("SELECT subjectId FROM Subject WHERE subjectCode = ?", (subjectCode,)).fetchone()
                if row:
                    subjectId = row["subjectId"]
                else:
                    cursor = conn.execute(
                        "INSERT INTO Subject (subjectCode, subjectName) VALUES (?, ?)",
                        (subjectCode, subjectName)
                    )
                    subjectId = cursor.lastrowid

                row = conn.execute(
                    "SELECT courseId FROM Course WHERE subjectId = ? AND courseNumber = ?",
                    (subjectId, courseNumber)
                ).fetchone()
                if row:
                    courseId = row["courseId"]
                else:
                    cursor = conn.execute(
                        "INSERT INTO Course (subjectId, courseNumber, courseTitle) VALUES (?, ?, ?)",
                        (subjectId, courseNumber, courseTitle)
                    )
                    courseId = cursor.lastrowid

                row = conn.execute(
                    "SELECT termId FROM Term WHERE academicTerm = ? AND academicYear = ?",
                    (academicTerm, academicYear)
                ).fetchone()
                if row:
                    termId = row["termId"]
                else:
                    cursor = conn.execute(
                        "INSERT INTO Term (academicTerm, academicYear) VALUES (?, ?)",
                        (academicTerm, academicYear)
                    )
                    termId = cursor.lastrowid

                cursor = conn.execute(
                    "INSERT INTO CourseOffering (courseId, termId, instructorId, sectionNumber) VALUES (?, ?, ?, ?)",
                    (courseId, termId, instructorId, sectionNumber)
                )
                courseOfferingId = cursor.lastrowid

                originalFilename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                savedFilename = f"{subjectCode}_{courseNumber}_{timestamp}_{originalFilename}"
                filePath = os.path.join(documentsPath, savedFilename)
                file.save(filePath)

                conn.execute(
                    "INSERT INTO Syllabus (courseOfferingId, fileName, filePath, uploadDate) VALUES (?, ?, ?, ?)",
                    (courseOfferingId, originalFilename, savedFilename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )

                conn.commit()
                conn.close()
                success = True

            except Exception as e:
                error = str(e)

    return render_template("BIS372_Delivery2/upload_syllabus.html", success=success, error=error)
