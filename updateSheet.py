import sqlite3, requests, json

### Update this link every time a new version of the Sheets script is created ###
SCRIPT = "https://script.google.com/macros/s/AKfycby0uHoCYTMCzLsIqpeXVZJx7w7aiZaD9oi3wJQLwDbgqJhv0ZUr1Cg2pwgStIpEnWTc/exec"
#################################################################################

def get_data(min, max):
    # return the rows whose matchNum is within the range

    conn = sqlite3.connect('data/scoutWaco2025.db')
    c = conn.cursor()
    c.execute('SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows = c.fetchall()
    conn.close()

    # do we need to merge two sql databases? ####################
    # conn = sqlite3.connect('data/scoutFortWorth.db')
    # c = conn.cursor()
    # # select from scoutData where matchNum is within the range
    # c.execute('SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    # rows.extend(c.fetchall())
    # conn.close()

    return rows

def manual_send():

    print("Input the range of matches to send to the sheet")
    print("(same value for min and max to send only one match)")
    min = int(input("first match? "))
    max = int(input("last match? "))

    data = get_data(min,max)

    to_send = []
    for d in data:
        if d[3] == "test": continue
        to_send.append(json.loads(d[4]))
        # timestamp
        # match
        # team
        # scoutID
        to_send[-1]["timestamp"] = d[0]
        to_send[-1]["matchNum"] = d[1]
        to_send[-1]["teamNum"] = d[2]
        to_send[-1]["scoutID"] = d[3]
        # print(to_send)

    if input(f"Sending {len(to_send)} lines. Confirm? (y/n) ") == "y":

        resp = requests.post(SCRIPT, data=json.dumps(to_send).encode())

        #print(to_send)
        print(f"Done.\nResponse code: {resp.status_code} {resp.reason}")

    else:
        print("Abort")
        exit()

if __name__ == "__main__":
    manual_send()