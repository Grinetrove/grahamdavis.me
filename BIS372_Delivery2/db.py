import sqlite3
import os

basePath = os.path.dirname(os.path.abspath(__file__))
dbPath = os.path.join(basePath, "BIS372_Delivery2.db")
schemaPath = os.path.join(basePath, "schema.sql")


def getDb():
    conn = sqlite3.connect(dbPath)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initDb():
    if not os.path.exists(dbPath):
        conn = getDb()
        with open(schemaPath, "r") as f:
            conn.executescript(f.read())
        conn.close()
