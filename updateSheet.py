import sqlite3, requests, json
import pandas as pd


url="https://script.google.com/macros/s/AKfycbyyvkI3fcBH9Q5VVAPhF5zbthbpmBgdOu9TDyeMHdBrxBxJWoH_SHfob3yGSuM6NMwX/exec"
def get_data(min, max):
    # return the rows whose matchNum is within the range [min, max] inclusive

    conn = sqlite3.connect('data/scouting_dat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows = c.fetchall()
    print(rows)
    conn.close()

    # Format data
    to_send = []
    scout_rows = []  # Keep track of original scout rows
    for row in rows:
        print(row, "row beta")
        to_send.append(json.loads(row[4])) # Extract information in the 'data' column
        to_send[-1]["timestamp"] = row[0] # Append metadata
        to_send[-1]["matchNum"] = row[1]
        to_send[-1]["teamNum"] = row[2]
        to_send[-1]["scoutID"] = row[3]
        to_send[-1]["type"] = "scout"
        scout_rows.append(row)  # Store original row
    print(to_send)
    return to_send, scout_rows

def move_to_old(scout_rows):
    if not scout_rows:
        return  # No scout data to move

    # Connect to old database
    conn_old = sqlite3.connect('data/scouting_dat_old.db')
    c_old = conn_old.cursor()
    
    # Create table if not exists (assuming same schema as scoutData)
    c_old.execute('''CREATE TABLE IF NOT EXISTS scoutData (
        timestamp TEXT,
        matchNum INTEGER,
        teamNum INTEGER,
        scoutID TEXT,
        data TEXT
    )''')
    
    # Insert rows into old database
    c_old.executemany('INSERT INTO scoutData VALUES (?, ?, ?, ?, ?)', scout_rows)
    conn_old.commit()
    conn_old.close()
    
    # Delete from original database
    conn = sqlite3.connect('data/scouting_dat.db')
    c = conn.cursor()
    # Delete the specific rows that were sent
    for row in scout_rows:
        c.execute('DELETE FROM scoutData WHERE timestamp = ? AND matchNum = ? AND teamNum = ? AND scoutID = ? AND data = ?',
                  (row[0], row[1], row[2], row[3], row[4]))
    conn.commit()
    conn.close()

def send_match(matchNum):
    # send_match: fetches data from one match and 

    print(f"Uploading data from match {matchNum}... ", end="")

    data, scout_rows = get_data(matchNum, matchNum)
    print(data)

    if len(data) == 0:
        print("Failed")
        return f"Error: No data found for match {matchNum}"

    for i in data:
        try: 
            response = requests.post(url, json=i, allow_redirects=True)
        except:
            print("Failed")
            return "Error: POST request failed"

    status = response.json()
    if status['status'] != 'success':
        print(f"App script returned failing status: {status}")
        return "Error: App script returned failing status"
    

    print("Success")
    # Move data from scouting_dat to scouting_dat_old after successful send

    move_to_old(scout_rows)
    return f"Sent {len(data)} lines. Server response: {response.status_code} {response.reason}"
