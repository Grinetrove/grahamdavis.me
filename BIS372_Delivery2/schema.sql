CREATE TABLE IF NOT EXISTS Instructor (
    instructorId INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Subject (
    subjectId INTEGER PRIMARY KEY AUTOINCREMENT,
    subjectCode TEXT NOT NULL UNIQUE,
    subjectName TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Course (
    courseId INTEGER PRIMARY KEY AUTOINCREMENT,
    subjectId INTEGER NOT NULL,
    courseNumber TEXT NOT NULL,
    courseTitle TEXT NOT NULL,
    FOREIGN KEY (subjectId) REFERENCES Subject(subjectId) ON DELETE CASCADE,
    UNIQUE(subjectId, courseNumber)
);

CREATE TABLE IF NOT EXISTS Term (
    termId INTEGER PRIMARY KEY AUTOINCREMENT,
    academicTerm TEXT NOT NULL,
    academicYear TEXT NOT NULL,
    UNIQUE(academicTerm, academicYear)
);

CREATE TABLE IF NOT EXISTS CourseOffering (
    courseOfferingId INTEGER PRIMARY KEY AUTOINCREMENT,
    courseId INTEGER NOT NULL,
    termId INTEGER NOT NULL,
    instructorId INTEGER NOT NULL,
    sectionNumber TEXT,
    FOREIGN KEY (courseId) REFERENCES Course(courseId) ON DELETE CASCADE,
    FOREIGN KEY (termId) REFERENCES Term(termId) ON DELETE CASCADE,
    FOREIGN KEY (instructorId) REFERENCES Instructor(instructorId) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Syllabus (
    syllabusId INTEGER PRIMARY KEY AUTOINCREMENT,
    courseOfferingId INTEGER NOT NULL,
    fileName TEXT NOT NULL,
    filePath TEXT NOT NULL,
    uploadDate TEXT NOT NULL,
    FOREIGN KEY (courseOfferingId) REFERENCES CourseOffering(courseOfferingId) ON DELETE CASCADE
);
