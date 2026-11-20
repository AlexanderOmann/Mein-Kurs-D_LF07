import sqlite3

# Verbindung zur Datenbank herstellen
datenbank = sqlite3.connect("codes.db")

cursor = datenbank.cursor()

# Tabelle erstellen
cursor.execute("""
CREATE TABLE IF NOT EXISTS zugang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL
)
""")

# Benutzer mit Zugangscode eintragen
cursor.execute(
    "INSERT INTO zugang (name, code) VALUES (?, ?)",
    ("Benutzer1", "1234")
)

# Änderungen speichern
datenbank.commit()

# Verbindung schließen
datenbank.close()

print("Datenbank wurde erfolgreich erstellt!")