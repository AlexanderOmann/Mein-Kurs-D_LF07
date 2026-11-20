import sqlite3

datenbank = sqlite3.connect("mqtt.db")

cursor = datenbank.cursor()

cursor.execute("""
SELECT id, topic, wert, zeitpunkt
FROM events
ORDER BY id
""")

events = cursor.fetchall()

print()
print("MQTT EVENTS")
print("-" * 50)

for event in events:

    print("ID:", event[0])
    print("Topic:", event[1])
    print("Wert:", event[2])
    print("Zeit:", event[3])

    print("-" * 50)

datenbank.close()