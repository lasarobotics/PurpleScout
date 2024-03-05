# Import Flask application
from flask import Flask, render_template, request, redirect, url_for, Response
from game import *
from flask_socketio import SocketIO, send, emit
import csv, secrets, json
import sqlite3
import requests

# Create app
app = Flask(__name__)
socketio = SocketIO(app)

# Configure app
app.config['FORM'] = CrescendoForm # Change this to the form you want to use
app.config['SECRET_KEY'] = secrets.token_hex(16)
conn = sqlite3.connect('data/scout.db')
cursor = conn.cursor()

# Create table
cursor.execute('''CREATE TABLE IF NOT EXISTS scoutData (
    timestamp STRING PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    matchNum INTEGER,
    teamNum INTEGER,
    scoutID STRING, 
    data TEXT
)
''')
conn.commit()
conn.close()

# Index
@app.route('/')
def index():
    return render_template('home.html')

# Home
@app.route('/home.html')
def home():
    return render_template('home.html', name=app.config['FORM'].name)

# Scout
@app.route('/scout.html')
def scout():
    form = app.config['FORM']()
    return render_template('forms/' + app.config['FORM'].__name__ + '.html', form=form)

# Super scout
@app.route('/superScout.html')
def superScout():
    return render_template('superScout.html')

# Normal scout submit
@app.route('/scoutSubmit.html', methods=['GET', 'POST'])
def scoutSubmit():
    print(f"got request via {request.method}")
    if request.method == 'POST':

        data = request.form.to_dict()

        # append data to data/scout.csv
        with open('data/scout.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(data.keys()))
            writer.writerow(data)

            f.close()

        # append data to sqlite3 database
        conn = sqlite3.connect('data/scout.db')
        cursor = conn.cursor()
        matchNum = data['matchNum']
        teamNum = data['teamNum']
        scoutID = data['scoutID']
        del data['matchNum']
        del data['teamNum']
        del data['scoutID']

        # make sure checkboxes appear
        if 'autoMobility' not in data:
            data['autoMobility'] = 'n'
        if 'spotlight' not in data:
            data['spotlight'] = 'n'
            
        cursor.execute('INSERT INTO scoutData (matchNum, teamNum, scoutID, data) VALUES (?, ?, ?, ?)', 
                       (matchNum, teamNum, scoutID, json.dumps(data)))
        conn.commit()
        conn.close()

        print(data)

        # tell the super scout that a scout has submitted
        #print(request.form.to_dict()['teamNum'])
        socketio.emit('scoutSubmit', data)

        return redirect(url_for('scoutSubmit'))

    return render_template('scoutSubmit.html')

# Super scout submit
@app.route('/superScoutSubmit.html', methods=['GET', 'POST'])
def superScoutSubmit():
    print(f"got request via {request.method}")
    if request.method == 'POST':
        # print the data recieved from the form
        for key, value in request.form.items():
            print(f"{key}: {value}")

        print(request.form.to_dict())

        # append data to data/scout.csv
        with open('data/superScout.csv', 'a') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "matchNum",
                "num1red",
                "num1blue",
                "num2red",
                "num2blue",
                "num3red",
                "num3blue",
                "info"
            ])
            writer.writerow(request.form.to_dict())

            f.close()

        return redirect(url_for('superScoutSubmit'))

    return render_template('superScoutSubmit.html')

# Pit scout
@app.route('/pitScout.html', methods=['GET', 'POST'])
def pitScout():
    with open("data/robotScouted.csv", "r") as f:
        reader = csv.DictReader(f)
        robots = [row for row in reader]
    count = 0
    for robot in robots:
        if robot['scouted'] == '0':
            count += 1

    print(count)
    return render_template('pitScout.html', robots=robots, remaining=count)

# Pit scout submit
@app.route('/pitScoutSubmit.html', methods=['GET', 'POST'])
def pitScoutSubmit():

    # open csv file and change scouted to 1
    with open("data/robotScouted.csv", "r") as f:
        reader = csv.DictReader(f)
        robots = [row for row in reader]
        print(robots, len(robots))
    
    for robot in robots:
        if str(robot['teamNum']) == str(request.form['tname']):
            robot['scouted'] = '1'
    
    with open("data/robotScouted.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["teamNum", "teamName", "scouted"])
        writer.writeheader()
        writer.writerows(robots)
    
    f.close()

    return render_template('pitScoutSubmit.html')

@app.route('/favicon.ico')
def favicon():
    with open('static/favicon.ico', 'rb') as f:
        r = Response(f.read())
        r.content_type = "image/png"
        return r


#### Socket routes ####
@socketio.on('echo') # test route
def handle_echo(data):
    print(f"received echo: {data}")
    emit('echo', data)

@socketio.on('getTeams') # activated when the super scout clicks the button to fetch teams
def handle_fetchTeams(data):
    # read data from data/teams.csv into a dictionary
    matchNum = data['matchNum']
    # get line of matchNum
    with open('data/matchList.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['matchNum'] == matchNum:
                # send data to super scout
                emit('sendTeams', row)
                return
            
    # if no matchNum found, send error
    emit('sendTeams', {'red1': 'error', 'red2': 'error', 'red3': 'error', 'blue1': 'error', 'blue2': 'error', 'blue3': 'error'})

# Both these routes bounce the data back to all the clients
@socketio.on('scoutSelect') # activated when a scout chooses their team (red/blue and number)
def handle_scoutSelect(data):
    print(f"received scoutSelect: {data}")
    emit('scoutSelect', data, broadcast=True)

@socketio.on('scoutAssign') # activated when the super scout assigns the team# to scouts
def handle_scoutAssign(data):
    print(f"received scoutAssign: {data}")
    emit('scoutAssign', data, broadcast=True)

# Run app  
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
