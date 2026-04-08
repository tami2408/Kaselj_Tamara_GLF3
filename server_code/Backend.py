import anvil.server
import sqlite3
import datetime

DB_NAME = "Kaselj_Tamara_fitnessstudio.db"


def get_connection():
  return sqlite3.connect(DB_NAME)


@anvil.server.callable
def get_kurse():
  conn = get_connection()
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  cursor.execute("""
        SELECT 
            k.KID,
            k.Bezeichnung AS kursname,
            k.Wochentag,
            k.Uhrzeit,
            k.MaxTeilnehmer,
            t.Vorname || ' ' || t.Nachname AS trainername,
            COUNT(a.MID) AS teilnehmer_anzahl
        FROM Kurse k
        JOIN Trainer t ON k.TID = t.TID
        LEFT JOIN anmelden a ON k.KID = a.KID
        GROUP BY k.KID, k.Bezeichnung, k.Wochentag, k.Uhrzeit, k.MaxTeilnehmer, trainername
        ORDER BY
            CASE k.Wochentag
                WHEN 'Montag' THEN 1
                WHEN 'Dienstag' THEN 2
                WHEN 'Mittwoch' THEN 3
                WHEN 'Donnerstag' THEN 4
                WHEN 'Freitag' THEN 5
                WHEN 'Samstag' THEN 6
                WHEN 'Sonntag' THEN 7
                ELSE 99
            END,
            k.Uhrzeit
    """)

  daten = []
  for row in cursor.fetchall():
    daten.append({
      "KID": row["KID"],
      "kursname": row["kursname"],
      "wochentag": row["Wochentag"],
      "uhrzeit": row["Uhrzeit"],
      "trainername": row["trainername"],
      "teilnehmer_text": f"{row['teilnehmer_anzahl']}/{row['MaxTeilnehmer']}",
      "teilnehmer_anzahl": row["teilnehmer_anzahl"],
      "max_teilnehmer": row["MaxTeilnehmer"]
    })

  conn.close()
  return daten


@anvil.server.callable
def get_mitglieder():
  conn = get_connection()
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  cursor.execute("""
        SELECT MID, Vorname, Nachname, Email, Beitrittsdatum
        FROM Mitglieder
        ORDER BY Nachname, Vorname
    """)

  daten = []
  for row in cursor.fetchall():
    daten.append({
      "MID": row["MID"],
      "name": f"{row['Nachname']} {row['Vorname']}",
      "vorname": row["Vorname"],
      "nachname": row["Nachname"],
      "email": row["Email"],
      "beitrittsdatum": row["Beitrittsdatum"]
    })

  conn.close()
  return daten


@anvil.server.callable
def kurs_anmelden(mid, kid):
  conn = get_connection()
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  # Prüfen: schon angemeldet?
  cursor.execute("""
        SELECT 1
        FROM anmelden
        WHERE MID = ? AND KID = ?
    """, (mid, kid))
  vorhanden = cursor.fetchone()

  if vorhanden:
    conn.close()
    return "Dieses Mitglied ist bereits für den Kurs angemeldet."

  # max Teilnehmer prüfen
  cursor.execute("""
        SELECT MaxTeilnehmer
        FROM Kurse
        WHERE KID = ?
    """, (kid,))
  kurs = cursor.fetchone()

  cursor.execute("""
        SELECT COUNT(*) AS anzahl
        FROM anmelden
        WHERE KID = ?
    """, (kid,))
  anzahl = cursor.fetchone()["anzahl"]

  if anzahl >= kurs["MaxTeilnehmer"]:
    conn.close()
    return "Der Kurs ist bereits voll."

  heute = datetime.date.today().isoformat()

  cursor.execute("""
        INSERT INTO anmelden (MID, KID, Anmeldedatum)
        VALUES (?, ?, ?)
    """, (mid, kid, heute))

  conn.commit()
  conn.close()

  return "Anmeldung erfolgreich."


@anvil.server.callable
def get_mitglieder_fuer_kurs(kid):
  conn = get_connection()
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()

  cursor.execute("""
        SELECT 
            m.Vorname,
            m.Nachname,
            m.Email,
            a.Anmeldedatum
        FROM anmelden a
        JOIN Mitglieder m ON a.MID = m.MID
        WHERE a.KID = ?
        ORDER BY m.Nachname, m.Vorname
    """, (kid,))

  daten = []
  for row in cursor.fetchall():
    daten.append({
      "name": f"{row['Nachname']} {row['Vorname']}",
      "email": row["Email"],
      "anmeldedatum": row["Anmeldedatum"]
    })

  conn.close()
  return daten