import sqlite3, requests, json

### Update this link every time a new version of the Sheets script is created ###
SCRIPT = "https://script.google.com/macros/s/AKfycbz4C0ChdzdRIwL7sRBIPcbrgepH5bzXI2ctxmpQhzfCJoqACx73gEAMTkEPbpDToMCq/exec"
#################################################################################

def get_data(min, max):
    # return the rows whose matchNum is within the range

    conn = sqlite3.connect('data/scoutState.db')
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


print("Sending... ", end="")
req = requests.post(SCRIPT, data=json.dumps(to_send).encode())
print(to_send)
print("Done!")
#print(req.content)