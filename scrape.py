# scrape.py: example usage of the python TBA API, unused for now
import tbapy
import csv

tba = tbapy.TBA('rZxJQVjP40eTtskoUbT3OWTKEnKNxk8McjB9QqRdU8mT78o8EN3OuzuMppJTADtV')

team = tba.team(418)

# Current event
EVENT = '2024txbel'

# Get the teams at the event
#teams = tba.event_teams(EVENT)

#print("There are {} teams at {}".format(len(teams), EVENT))
#for team in teams:
    #print(f"Team {team.team_number} ({team.nickname}) is from {team.city}, {team.state_prov}")

# Get the matches at the event
#matches = tba.event_matches(EVENT)

#print("There are {} matches at {}".format(len(matches), EVENT))
#for match in matches:
    #print(f"Match {match.key} is between {match.alliances['red']['team_keys']} and {match.alliances['blue']['team_keys']}")

# example_match = tba.match('2023cmptx_f1m2')
# pprint.pprint(example_match.score_breakdown)

# # Data we can use:
# """
# match.score_breakdown.[red/blue]


# """
matchList = []

matches = tba.event_matches(EVENT)
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
print(matchList)

# write matchList to data/matchList.csv
with open('data/matchList.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["matchID", "matchNum", "red1", "red2", "red3", "blue1", "blue2", "blue3"])
    writer.writerows(matchList)
    f.close()

teams = tba.event_teams(EVENT)
#print(teams)
print(len(teams))
for team in teams:
    print(str(team.team_number) + "," + team.nickname)