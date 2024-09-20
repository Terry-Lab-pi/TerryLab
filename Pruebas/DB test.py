import sqlite3

conn = sqlite3.connect('terry.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS mediciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        FechaHora DateTime,
        Humedad DECIMAL,
        Temperatura DECIMAL,
        Conductividad NUMERIC,
        PH DECIMAL,
        Nitrogeno NUMERIC,
        Fosforo NUMERIC,
        Potasio NUMERIC)
''')

cursor.execute('''
    INSERT INTO mediciones (FechaHora, Humedad, Temperatura, Conductividad, PH, Nitrogeno, Fosforo, Potasio)
    VALUES (datetime('now', 'localtime'), ?, ?, ?, ?, ?, ?, ?)
''', (10, 20, 30, 40, 50, 60, 70))
conn.commit()

conn.close()
