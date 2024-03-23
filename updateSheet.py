import sqlite3, requests, json

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

data = get_data(58,61)

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
print(f"Sending {len(to_send)} records")

print(requests.post("https://script.google.com/macros/s/AKfycbw4Yu2gGhH1C6fGABoUeqBhAATC0gWxPxEFro5NEvsO7FMLaa0StxlVSzpnAS6o7cU/exec", data=json.dumps(to_send).encode()).content)

# print(get_data(1, 100))