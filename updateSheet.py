import sqlite3, requests, json
import pandas as pd

### Update this link every time a new version of the Sheets script is created ###
# SCRIPT = "https://script.google.com/macros/s/AKfycbyFWSAVL4ubii6sGGC8UQV72jN50DIoaAPNiBu6jSZQ05NdOtjyAbUAH9zu4CfAvfVbNQ/exec"
SCRIPT = "https://script.google.com/macros/s/AKfycbwWSZ7ieS9HV65ZprYOtLdsmvK-osftUT5gb4FvQAoPRjK1b9AJ1Pwy7aVs2a12VJaw/exec"
#################################################################################

def get_data(min, max):
    # return the rows whose matchNum is within the range [min, max] inclusive

    conn = sqlite3.connect('data/scouting_dat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM scoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    rows = c.fetchall()
    conn.close()

    # Format data
    to_send = []
    scout_rows = []  # Keep track of original scout rows
    for row in rows:
        print(row)
        if row[3] == "test": continue
        to_send.append(json.loads(row[4])) # Extract information in the 'data' column
        to_send[-1]["timestamp"] = row[0] # Append metadata
        to_send[-1]["matchNum"] = row[1]
        to_send[-1]["teamNum"] = row[2]
        to_send[-1]["scoutID"] = row[3]
        to_send[-1]["type"] = "scout"
        scout_rows.append(row)  # Store original row
    
    # # Super Scout
    # conn = sqlite3.connect('data/scouting_dat.db')
    # c = conn.cursor()
    # c.execute('SELECT * FROM superScoutData WHERE matchNum BETWEEN ? AND ?;', (min, max))
    # rows = c.fetchall()
    # conn.close()

    # for row in rows:
    #     if row[3] == "test": continue
    #     to_send.append(json.loads(row[4])) # Extract information in the 'data' column
    #     to_send[-1]["timestamp"] = row[0] # Append metadata
    #     to_send[-1]["matchNum"] = row[1]
    #     to_send[-1]["teamNum"] = row[2]
    #     to_send[-1]["scoutID"] = row[3]
    #     to_send[-1]["type"] = "superScout"

    # Return object and scout rows
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

def send():

    # Read current match from file set by megaScout
    try:
        with open('data/current_match.txt', 'r') as f:
            matchNum = int(f.read().strip())
    except FileNotFoundError:
        print("Current match not set. Please set it in megaScout.")
        return
    except ValueError:
        print("Invalid match number in file.")
        return

    print(f"Sending data for match {matchNum}")

    data, scout_rows = get_data(matchNum, matchNum)

    if input(f"Sending {len(data)} lines. Confirm? (y/n) ") == "y":

        resp = requests.post(SCRIPT, data=json.dumps(data).encode())
        # print(data)
        print(f"Done.\nResponse code: {resp.status_code} {resp.reason}")

        # Move data
        if resp.status_code == 200:
            move_to_old(scout_rows)

    else:
        print("Abort")
        exit()

def send_match(matchNum):
    # send_match: fetches data from one match and 

    print(f"Uploading data from match {matchNum}... ", end="")

    data, scout_rows = get_data(matchNum, matchNum)
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

    #Goes through and splits all the data into a redteam array and blueteam array

    for i in data:
        tNum = (i.get("teamNum"))
        print("ahahaha", tNum)
        if (tNum == teamsColors[matchNum-1][0] or tNum == teamsColors[matchNum-1][1] or tNum == teamsColors[matchNum-1][2]):
            redDATA.append(i)
        else:
            blueDATA.append(i)


    redCheckTeams = []
    blueCheckTeams = []

    #creates a redTeamCheck for robots that the red team played defense on.

    for i in redDATA:
        if (i.get("defenseExperienced") != " "):
            teams = i.get("defenseExperienced")
            try:
                redCheckTeams = teams.split(",")
            except:
                redCheckTeams = [""]
            teamsQuotes = "\""
            for j in range(0,len(redCheckTeams)):  
                if (j == len(redCheckTeams)-1):
                    teamsQuotes+=redCheckTeams[j]
                else:      
                    teamsQuotes += redCheckTeams[j]+","
            teamsQuotes += "\""
            i["defenseExperiencedQuotes"]=teamsQuotes


    #creates a blueTeamCheck for robots that the blue team played defense on.
     
    for i in blueDATA:
        if (i.get("defenseExperienced") != " "):
            teams = i.get("defenseExperienced")
            try:
                blueCheckTeams = teams.split(",")
            except:
                blueCheckTeams = [""]   
            teamsQuotes = "\""
            for j in range(0,len(blueCheckTeams)):  
                if (j == len(blueCheckTeams)-1):
                    teamsQuotes+=blueCheckTeams[j]
                else:      
                    teamsQuotes += blueCheckTeams[j]+","
            teamsQuotes += "\""
            i["defenseExperiencedQuotes"]=teamsQuotes

    #compares to blueCheckTeams to see if any redteam robots experienced defense.
    

    for i in redDATA:
        if (i.get("type")=="superScout"):
            continue
        for j in blueCheckTeams:
            if (j == "  " or j == "" or j =="N/A" or j=="-" or j=="no" or j==" no"):
                i["defense_Experienced"]="FALSE"
                i["defense_NO"]="TRUE"
                continue
            try:
                if (int(j) == int(i.get('teamNum'))):
                    i["defense_Experienced"]="TRUE"
                    i["defense_NO"]="FALSE"
                    continue
                else:
                    i["defense_Experienced"]="FALSE"
                    i["defense_NO"]="TRUE"
            except:
                i["defense_Experienced"]="FALSE"
                i["defense_NO"]="TRUE"


    #compares to redCheckTeams to see if any blueteam robots experienced defense.

    for i in blueDATA:
        if (i.get("type")=="superScout"):
            continue
        if (len(redCheckTeams)==0):
            i["defense_Experienced"]="FALSE"
            i["defense_NO"]="TRUE"
            continue
        for j in redCheckTeams:
            if (j == "  " or j == "" or j =="N/A" or j=="-" or j=="no" or j==" no"):
                i["defense_Experienced"]="FALSE"
                i["defense_NO"]="TRUE"
                continue
            try:
                if (int(j) == int(i.get('teamNum'))):
                    i["defense_Experienced"]="TRUE"
                    i["defense_NO"]="FALSE"
                    continue
                else:
                    i["defense_Experienced"]="FALSE"
                    i["defense_NO"]="TRUE"
            except:
                i["defense_Experienced"]="FALSE"
                i["defense_NO"]="TRUE"

    #Fully proccessed data entries for each team. Ready to upload!
    
    dataNew = []
    for i in redDATA:
        print(i)
        print("\n")
        dataNew.append(i)
    for i in blueDATA:
        print(i)
        print("\n")
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
    # Move data from scouting_dat to scouting_dat_old after successful send
    move_to_old(scout_rows)
    return f"Sent {len(data)} lines. Server response: {resp.status_code} {resp.reason}"


if __name__ == "__main__":
    send()