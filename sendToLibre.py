import sqlite3
import json
from openpyxl import load_workbook
import os


def get_data(min_match, max_match):
    conn = sqlite3.connect('data/scouting_dat.db')
    c = conn.cursor()

    c.execute(
        'SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;',
        (min_match, max_match)
    )
    rows = c.fetchall()
    conn.close()

    to_send = []
    scout_rows = []

    for row in rows:
        try:
            data = json.loads(row[4])
        except:
            continue  # skip bad rows

        data["timestamp"] = row[0]
        data["matchNum"] = row[1]
        data["teamNum"] = row[2]
        data["scoutID"] = row[3]
        data["type"] = "scout"

        to_send.append(data)
        scout_rows.append(row)

    return to_send, scout_rows


def move_to_old(scout_rows):
    if not scout_rows:
        return

    conn_old = sqlite3.connect('data/scouting_dat_old.db')
    c_old = conn_old.cursor()

    c_old.execute('''CREATE TABLE IF NOT EXISTS scoutData (
        timestamp TEXT,
        matchNum INTEGER,
        teamNum INTEGER,
        scoutID TEXT,
        data TEXT
    )''')

    c_old.executemany(
        'INSERT INTO scoutData VALUES (?, ?, ?, ?, ?)',
        scout_rows
    )

    conn_old.commit()
    conn_old.close()

    conn = sqlite3.connect('data/scouting_dat.db')
    c = conn.cursor()

    for row in scout_rows:
        c.execute('''
            DELETE FROM scoutData
            WHERE timestamp=? AND matchNum=? AND teamNum=? AND scoutID=? AND data=?
        ''', row)

    conn.commit()
    conn.close()


def send_match(matchNum):
    print(f"Uploading data from match {matchNum}...")

    data, scout_rows = get_data(matchNum, matchNum)

    print("DATA FOUND:", len(data))

    if len(data) == 0:
        print("No data found.")
        return

    # Check file exists
    file_path = 'scoutingDataRAW.xlsx'

    if not os.path.exists(file_path):
        print("Excel file not found!")
        return

    # LOAD WORKBOOK ONCE
    wb = load_workbook(file_path)
    ws = wb.active

    for entry in data:
        try:
            failure = "y" if entry.get("failureCheck") == "y" else ""

            ws.append([
                entry.get("timestamp", ""),
                entry.get("scoutID", ""),
                entry.get("matchNum", ""),
                entry.get("teamNum", ""),
                entry.get("autoShots", ""),
                entry.get("totalPositions", ""),
                entry.get("heatmap_frequencies", ""),
                entry.get("teleopShots", ""),
                entry.get("passes", ""),
                entry.get("climbLocation", ""),
                entry.get("fouls", ""),
                entry.get("failureDetails", ""),
                failure,
                entry.get("climbTime", ""),
                entry.get("info", "")
            ])

        except Exception as e:
            print("Error writing row:", e)

    wb.save(file_path)
    print("Excel updated successfully.")

    # OPTIONAL: move data after success
    # move_to_old(scout_rows)

    return "Sent"


# Example run
if __name__ == "__main__":
    send_match(1)