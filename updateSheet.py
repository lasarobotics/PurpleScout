import sqlite3, requests, json
import pandas as pd

### Update this link every time a new version of the Sheets script is created ###
SCRIPT = "https://script.google.com/macros/s/AKfycbxsabVlBc1M0CoAF0Qcb-vLDa9jOiOSs-gP0DCVVvcIqp08R5RfmhCAbFLOUU99eXaBDg/exec"
#################################################################################

def get_data(min, max):
    # return the rows whose matchNum is within the range [min, max] inclusive

    conn = sqlite3.connect('data/scoutManor2025.db')
    c = conn.cursor()
    c.execute('SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows = c.fetchall()
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
    conn = sqlite3.connect('data/scoutManor2025.db')
    c = conn.cursor()
    c.execute('SELECT * FROM superScoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
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
        # print(data)
        print(f"Done.\nResponse code: {resp.status_code} {resp.reason}")

    else:
        print("Abort")
        exit()

def send_match(matchNum):
    # send_match: fetches data from one match and 

    print(f"Uploading data from match {matchNum}... ", end="")

    data = get_data(matchNum, matchNum)
    dataColor = pd.read_csv('data\\matchList.csv')
    teamsColors = []

    for index, row in dataColor.iterrows():
        teamsColor = []
        rd1 = (index, row['red1'])
        rd2 = (index, row['red2'])
        rd3 = (index, row['red3'])
        bl1 = (index, row['blue1'])
        bl2 = (index, row['blue2'])
        bl3 = (index, row['blue3'])
        teamsColor.append(rd1[1])
        teamsColor.append(rd2[1])
        teamsColor.append(rd3[1])
        teamsColor.append(bl1[1])
        teamsColor.append(bl2[1])
        teamsColor.append(bl3[1])
        teamsColors.append(teamsColor)

    redDATA = []
    blueDATA = []

    for i in data:
        tNum = (i.get("teamNum"))
        if (tNum == teamsColors[matchNum-1][0] or tNum == teamsColors[matchNum-1][1] or tNum == teamsColors[matchNum-1][2]):
        # if (tNum == 1 or tNum ==2 or tNum == 3):
            redDATA.append(i)
        else:
            blueDATA.append(i)

    # print(redDATA)
    # print("\n")
    # print(blueDATA)

    redCheckTeams = []
    blueCheckTeams = []

    for i in redDATA:
        if (i.get("defenseExperienced") != " "):
            teams = i.get("defenseExperienced")
            print(teams)
            try:
                redCheckTeams = teams.split(",")
            except:
                redcheckTeams = []
     
    for i in blueDATA:
        if (i.get("defenseExperienced") != " "):
            teams = i.get("defenseExperienced")
            try:
                blueCheckTeams = teams.split(",")
            except:
                blueCheckTeams = []
    
    print(redCheckTeams)
    print('\n')
    print(blueCheckTeams)

    for i in redDATA:
        print(i)
        for j in blueCheckTeams:
            if (j == ""):
                i["defense_Experienced"]="FALSE"
                i["defense_NO"]="TRUE"
            if (int(j) == int(i.get('teamNum'))):
                print(" lol its TRUE")
                i["defense_Experienced"]="TRUE"
                i["defense_NO"]="FALSE"
                break
            else:
                i["defense_Experienced"]="FALSE"
                i["defense_NO"]="TRUE"

    for i in blueDATA:
        print(i)
        for j in redCheckTeams:
            if (j == ""):
                i["defense_Experienced"]="FALSE"
                i["defense_NO"]="TRUE"
            if (int(j) == int(i.get('teamNum'))):
                print(" lol its TRUE")
                i["defense_Experienced"]="TRUE"
                i["defense_NO"]="FALSE"
                break
            else:
                i["defense_Experienced"]="FALSE"
                i["defense_NO"]="TRUE"
    
    dataNew = []
    for i in redDATA:
        print(i)
        dataNew.append(i)
    for i in blueDATA:
        print(i)
        dataNew.append(i)


    if len(dataNew) == 0:
        print("Failed")
        return f"Error: No data found"

    try: 
        resp = requests.post(SCRIPT, data=json.dumps(dataNew).encode())
    except:
        print("Failed")
        return "Error: POST request failed"

    print("Success")
    return f"Sent {len(data)} lines. Server response: {resp.status_code} {resp.reason}"


if __name__ == "__main__":
    manual_send()