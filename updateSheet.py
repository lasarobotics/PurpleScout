import sqlite3, requests, json

### Update this link every time a new version of the Sheets script is created ###
SCRIPT = "https://script.google.com/macros/s/AKfycbzrncsnBRsMoFHOKqJr1Lv6JjQq8t3ITnWOetCi7RytMxugqBrdkJvPkxIe4BnJxix_/exec"
#################################################################################

def get_data(min, max):
    # return the rows whose matchNum is within the range [min, max] inclusive

    conn = sqlite3.connect('data/scoutWaco2025.db')
    c = conn.cursor()
    c.execute('SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows = c.fetchall()
    c.execute('SELECT * FROM superScoutData2 WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows.extend(c.fetchall())
    conn.close()

    # Format data
    to_send = []
    for row in rows:
        if row[3] == "test": continue
        to_send.append(json.loads(row[4])) # Extract information in the 'data' column
        to_send[-1]["timestamp"] = row[0] # Append metadata
        to_send[-1]["matchNum"] = row[1]
        to_send[-1]["teamNum"] = row[2]
        to_send[-1]["scoutID"] = row[3]
        to_send[-1]["type"] = "scout"
    
    # Super Scout
    conn = sqlite3.connect('data/scoutWaco2025.db')
    c = conn.cursor()
    c.execute('SELECT * FROM superScoutData2 WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows = c.fetchall()
    conn.close()

    for row in rows:
        if row[3] == "test": continue
        to_send.append(json.loads(row[4])) # Extract information in the 'data' column
        to_send[-1]["timestamp"] = row[0] # Append metadata
        to_send[-1]["matchNum"] = row[1]
        to_send[-1]["teamNum"] = row[2]
        to_send[-1]["scoutID"] = row[3]
        to_send[-1]["type"] = "superScout"

    # Return object
    return to_send

def manual_send():

    print("Input the range of matches to send to the sheet")
    print("(same value for min and max to send only one match)")
    min = int(input("first match? "))
    max = int(input("last match? "))

    data = get_data(min, max)

    if input(f"Sending {len(data)} lines (this should be 8). Confirm? (y/n) ") == "y":

        resp = requests.post(SCRIPT, data=json.dumps(data).encode())
        print(data)
        print(f"Done.\nResponse code: {resp.status_code} {resp.reason}")

    else:
        print("Abort")
        exit()

def send_match(matchNum):
    # send_match: fetches data from one match and 

    print(f"Uploading data from match {matchNum}... ", end="")

    data = get_data(matchNum, matchNum)

    if len(data) == 0:
        print("Failed")
        return f"Error: No data found"

    try: 
        resp = requests.post(SCRIPT, data=json.dumps(data).encode())
    except:
        print("Failed")
        return "Error: POST request failed"

    print("Success")
    return f"Sent {len(data)} lines. Server response: {resp.status_code} {resp.reason}"


if __name__ == "__main__":
    manual_send()