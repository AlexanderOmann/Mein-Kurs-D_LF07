import sqlite3

datenbank = sqlite3.connect("codes.db")
cursor = datenbank.cursor()

cursor.execute("SELECT * FROM zugang")

daten = cursor.fetchall()

for eintrag in daten:
    print(eintrag)

datenbank.close()
