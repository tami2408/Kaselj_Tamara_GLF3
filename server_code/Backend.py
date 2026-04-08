import anvil.server
from anvil.files import data_files
import sqlite3
import datetime

DB_NAME = "Seeberger_Jakob_fitnessstudio.db"


def db_lesen():
  return sqlite3.connect(data_files[DB_NAME])


@anvil.server.callable
def get_kurse():
  conn = db_lesen()
  conn.row_factory = sqlite3.Row
  cur = conn.cursor()

  cur.execute("""
    SELECT
      k.kurs_id,
      k.bezeichnung,
      k.wochentag,
      k.uhrzeit,
      t.vorname || ' ' || t.nachname AS trainer_name,
      COUNT(a.anmeldung_id) AS teilnehmerzahl
    FROM kurse k
    JOIN trainer t ON k.trainer_id = t.trainer_id
    LEFT JOIN anmeldung a ON a.kurs_id = k.kurs_id
    GROUP BY k.kurs_id, k.bezeichnung, k.wochentag, k.uhrzeit, trainer_name
    ORDER BY k.wochentag, k.uhrzeit, k.bezeichnung
  """)

  daten = []
  for row in cur.fetchall():
    daten.append({
      "Kurse": row["bezeichnung"],
      "Wochentag": row["wochentag"],
      "Uhrzeit": row["uhrzeit"],
      "Trainer": row["trainer_name"],
      "Teilnehmer": str(row["teilnehmerzahl"]),
      "kurs_id": row["kurs_id"]
    })

  conn.close()
  return daten


@anvil.server.callable
def get_mitglieder():
  conn = db_lesen()
  conn.row_factory = sqlite3.Row
  cur = conn.cursor()

  cur.execute("""
    SELECT mitglied_id, vorname, nachname
    FROM mitglieder
    ORDER BY nachname, vorname
  """)

  daten = [
    (f"{row['vorname']} {row['nachname']}", row["mitglied_id"])
    for row in cur.fetchall()
  ]

  conn.close()
  return daten


@anvil.server.callable
def anmelden(mitglied_id, kurs_id):
  if mitglied_id is None:
    raise Exception("Bitte ein Mitglied auswählen.")
  if kurs_id is None:
    raise Exception("Kein Kurs ausgewählt.")

  with data_files.editing(DB_NAME) as db_path:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
      SELECT COUNT(*) AS anzahl
      FROM anmeldung
      WHERE mitglied_id = ? AND kurs_id = ?
    """, (mitglied_id, kurs_id))
    schon_da = cur.fetchone()["anzahl"]

    if schon_da > 0:
      conn.close()
      raise Exception("Dieses Mitglied ist bereits angemeldet.")

    cur.execute("""
      SELECT max_teilnehmer
      FROM kurse
      WHERE kurs_id = ?
    """, (kurs_id,))
    kurs = cur.fetchone()

    if kurs is None:
      conn.close()
      raise Exception("Kurs nicht gefunden.")

    max_teilnehmer = kurs["max_teilnehmer"]

    cur.execute("""
      SELECT COUNT(*) AS anzahl
      FROM anmeldung
      WHERE kurs_id = ?
    """, (kurs_id,))
    aktuelle_anzahl = cur.fetchone()["anzahl"]

    if aktuelle_anzahl >= max_teilnehmer:
      conn.close()
      raise Exception("Dieser Kurs ist bereits voll.")

    cur.execute("""
      INSERT INTO anmeldung (mitglied_id, kurs_id, anmeldedatum)
      VALUES (?, ?, ?)
    """, (
      mitglied_id,
      kurs_id,
      datetime.date.today().isoformat()
    ))

    conn.commit()
    conn.close()

  return True


# optional: Mitglieder eines Kurses anzeigen
@anvil.server.callable
def get_mitglieder_im_kurs(kurs_id):
  conn = db_lesen()
  conn.row_factory = sqlite3.Row
  cur = conn.cursor()

  cur.execute("""
    SELECT m.vorname, m.nachname
    FROM anmeldung a
    JOIN mitglieder m ON a.mitglied_id = m.mitglied_id
    WHERE a.kurs_id = ?
    ORDER BY m.nachname, m.vorname
  """, (kurs_id,))

  daten = [f"{row['vorname']} {row['nachname']}" for row in cur.fetchall()]
  conn.close()
  return daten