import sqlite3, requests, json

### Update this link every time a new version of the Sheets script is created ###
SCRIPT = "https://script.google.com/macros/s/AKfycbw4Yu2gGhH1C6fGABoUeqBhAATC0gWxPxEFro5NEvsO7FMLaa0StxlVSzpnAS6o7cU/exec"
#################################################################################

def get_data(min, max):
    # return the rows whose matchNum is within the range

    conn = sqlite3.connect('data/scout_1.db')
    c = conn.cursor()
    c.execute('SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows = c.fetchall()
    conn.close()

    conn = sqlite3.connect('data/scoutFortWorth.db')
    c = conn.cursor()
    # select from scoutData where matchNum is within the range
    c.execute('SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows.extend(c.fetchall())
    conn.close()

    return rows

print("Input the range of matches to send to the sheet")
print("(same value for min and max to send only one match)")
min = input("first match? ")
max = input("last match? ")

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

print(to_send)
if input(f"Sending {len(to_send)} records for {max-min+1} matches. Confirm? (y/n) ") == "y":
    print("Sending... ", end="")
    req = requests.post(SCRIPT, data=json.dumps(to_send).encode())
    print("Done!")
    print(req.content)
else:
    print("Aborted")
    exit(0)