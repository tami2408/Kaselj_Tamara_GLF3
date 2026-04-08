import sqlite3
from pathlib import Path

DB_NAME = 'Nachname_Vorname_fitnessstudio.db'


def create_schema(cur: sqlite3.Cursor) -> None:
    cur.execute('PRAGMA foreign_keys = ON;')

    cur.execute('DROP TABLE IF EXISTS anmelden;')
    cur.execute('DROP TABLE IF EXISTS Kurse;')
    cur.execute('DROP TABLE IF EXISTS Mitglieder;')
    cur.execute('DROP TABLE IF EXISTS Trainer;')
    cur.execute('DROP TABLE IF EXISTS Fitnessstudio;')

    cur.execute('''
        CREATE TABLE Fitnessstudio (
            FID INTEGER PRIMARY KEY,
            Bezeichnung TEXT NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE Trainer (
            TID INTEGER PRIMARY KEY,
            Spezialgebiet TEXT NOT NULL,
            Vorname TEXT NOT NULL,
            Nachname TEXT NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE Mitglieder (
            MID INTEGER PRIMARY KEY,
            Vorname TEXT NOT NULL,
            Nachname TEXT NOT NULL,
            Email TEXT NOT NULL UNIQUE,
            Beitrittsdatum TEXT NOT NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE Kurse (
            KID INTEGER PRIMARY KEY,
            Wochentag TEXT NOT NULL,
            Uhrzeit TEXT NOT NULL,
            MaxTeilnehmer INTEGER NOT NULL,
            Bezeichnung TEXT NOT NULL,
            FID INTEGER NOT NULL,
            TID INTEGER NOT NULL,
            FOREIGN KEY (FID) REFERENCES Fitnessstudio(FID),
            FOREIGN KEY (TID) REFERENCES Trainer(TID)
        );
    ''')

    cur.execute('''
        CREATE TABLE anmelden (
            MID INTEGER NOT NULL,
            KID INTEGER NOT NULL,
            Anmeldedatum TEXT NOT NULL,
            PRIMARY KEY (MID, KID),
            FOREIGN KEY (MID) REFERENCES Mitglieder(MID),
            FOREIGN KEY (KID) REFERENCES Kurse(KID)
        );
    ''')


def insert_sample_data(cur: sqlite3.Cursor) -> None:
    fitnessstudios = [
        (1, 'Fitness First Mitte'),
    ]

    trainer = [
        (1, 'Yoga & Entspannung', 'Laura', 'Becker'),
        (2, 'Kraftausdauer & Spinning', 'Tobias', 'Schneider'),
        (3, 'Dance Fitness & Zumba', 'Miriam', 'Kaya'),
    ]

    mitglieder = [
        (1, 'Anna', 'Meyer', 'anna.meyer@example.com', '2025-01-15'),
        (2, 'Ben', 'Fischer', 'ben.fischer@example.com', '2025-02-03'),
        (3, 'Clara', 'Wolf', 'clara.wolf@example.com', '2024-11-20'),
        (4, 'David', 'Nguyen', 'david.nguyen@example.com', '2025-03-01'),
        (5, 'Elif', 'Yilmaz', 'elif.yilmaz@example.com', '2024-12-10'),
        (6, 'Finn', 'Schulz', 'finn.schulz@example.com', '2025-01-28'),
    ]

    kurse = [
        (1, 'Montag', '08:00', 15, 'Yoga', 1, 1),
        (2, 'Dienstag', '18:00', 12, 'Pilates', 1, 1),
        (3, 'Mittwoch', '19:00', 20, 'Spinning', 1, 2),
        (4, 'Donnerstag', '17:30', 18, 'Zumba', 1, 3),
        (5, 'Freitag', '10:00', 14, 'Rückenfit', 1, 2),
    ]

    anmeldungen = [
        (1, 1, '2025-04-01'),
        (2, 1, '2025-04-02'),
        (3, 2, '2025-04-02'),
        (4, 3, '2025-04-03'),
        (5, 4, '2025-04-03'),
        (6, 5, '2025-04-04'),
        (1, 3, '2025-04-04'),
        (2, 4, '2025-04-05'),
    ]

    cur.executemany('INSERT INTO Fitnessstudio (FID, Bezeichnung) VALUES (?, ?);', fitnessstudios)
    cur.executemany('INSERT INTO Trainer (TID, Spezialgebiet, Vorname, Nachname) VALUES (?, ?, ?, ?);', trainer)
    cur.executemany(
        'INSERT INTO Mitglieder (MID, Vorname, Nachname, Email, Beitrittsdatum) VALUES (?, ?, ?, ?, ?);',
        mitglieder,
    )
    cur.executemany(
        '''
        INSERT INTO Kurse (KID, Wochentag, Uhrzeit, MaxTeilnehmer, Bezeichnung, FID, TID)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        ''',
        kurse,
    )
    cur.executemany(
        'INSERT INTO anmelden (MID, KID, Anmeldedatum) VALUES (?, ?, ?);',
        anmeldungen,
    )


def main() -> None:
    db_path = Path(DB_NAME)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        create_schema(cur)
        insert_sample_data(cur)
        conn.commit()

    print(f'Datenbank erfolgreich erstellt: {db_path.resolve()}')
    print('Enthaltene Tabellen: Fitnessstudio, Trainer, Mitglieder, Kurse, anmelden')


if __name__ == '__main__':
    main()
