# tbaScrape.py: Scrapes matchlist from The Blue Alliance API
import tbapy
import csv
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
tba = tbapy.TBA(os.getenv('TBA'))

# team = tba.team(418)

# Current event
EVENT = '2024txcmp1'

# Get the teams at the event
teams = sorted([team.team_number for team in tba.event_teams(EVENT)])

print("There are {} teams at {}. Writing to file teamList.txt...".format(len(teams), EVENT), end='')
#for team in teams:
    #print(f"Team {team.team_number} ({team.nickname}) is from {team.city}, {team.state_prov}")

# Write teams to data/teamList.txt
with open('data/teamList.txt', 'w') as f:
    for team in teams:
        f.write(f"{team}\n")
    f.close()

print("done.")

matchList = []

matches = tba.event_matches(EVENT)
print(f"There are {len(matches)} matches at {EVENT}. Writing to file matchList.txt...", end='')
for match in matches:
    # Get only qualifying matches
    if 'qm' in match.key:

        matchID = match.key
        matchNum = int(match.key.split('_')[1][2:])
        red1 = int(match.alliances['red']['team_keys'][0][3:])
        red2 = int(match.alliances['red']['team_keys'][1][3:])
        red3 = int(match.alliances['red']['team_keys'][2][3:])
        blue1 = int(match.alliances['blue']['team_keys'][0][3:])
        blue2 = int(match.alliances['blue']['team_keys'][1][3:])
        blue3 = int(match.alliances['blue']['team_keys'][2][3:])
        matchList.append([matchID, matchNum, red1, red2, red3, blue1, blue2, blue3])

# sort matchList by matchNum
matchList.sort(key=lambda x: x[1])

# write matchList to data/matchList.csv
with open('data/matchList.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["matchID", "matchNum", "red1", "red2", "red3", "blue1", "blue2", "blue3"])
    for row in matchList:
        writer.writerow(row)
    f.close()

print("done.")