# Import Flask application
from flask import Flask, render_template, request, redirect, url_for, make_response, Response
from game import *
from flask_socketio import SocketIO, emit
import csv, secrets, json, sqlite3
from blueprints.PitScout.pitScout import pitScout_bp
from datetime import datetime

# Create app
app = Flask(__name__)
app.register_blueprint(pitScout_bp)
socketio = SocketIO(app)

# Configure app
app.config['FORM'] = CrescendoForm # Change this to the form you want to use
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['DB_PATH'] = 'data/scoutState.db'

# Create scoutData and superScoutData tables in sqlite database
conn = sqlite3.connect(app.config['DB_PATH'])
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS scoutData (
    timestamp STRING PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    matchNum INTEGER,
    teamNum INTEGER,
    scoutID STRING, 
    data TEXT
)
''')
cursor.execute('''CREATE TABLE IF NOT EXISTS superScoutData (
    timestamp STRING PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    matchNum INTEGER,
    red1Ranking INTEGER,
    red2Ranking INTEGER,
    red3Ranking INTEGER,
    blue1Ranking INTEGER,
    blue2Ranking INTEGER,
    blue3Ranking INTEGER,
    redAmps INTEGER,
    blueAmps INTEGER,
    info TEXT
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

def changeValue(inputString="", val=""):
    print("input: " + inputString + " | val: " + val)

    val_index = inputString.find('value="') + len('value="')
    print("val index: " + str(val_index) + " | length: " + str(len(inputString)))

    print("left: " + str(inputString[:val_index]))
    print("right: " + str(inputString[val_index:]))
    inputString = inputString[:val_index] + val + inputString[val_index:]

    
    print("input: " + inputString)
    return inputString

# Scout
@app.route('/scout.html')
def scout():
    form = app.config['FORM']()
    
    account_info = request.cookies.get("acc_info")
    if account_info is not None:
        cookie_values = account_info
        # scoutID = account_info[
        #     account_info.find(":") + 1:
        #     account_info.find(",")
        # ]
        # matchNum_startIndex = account_info.find("matchNum:")
        # matchNum = account_info[
        #     account_info.find(":", matchNum_startIndex) + 1:
        #     account_info.find(",", matchNum_startIndex)
        # ]
        # allianceNum_startIndex = account_info.find("allianceNum:", 2)
        # allianceNum = account_info[
        #     account_info.find(":", allianceNum_startIndex) + 1:
        #     #End of string
        # ]
        # cookie_values = (scoutID, matchNum, allianceNum)
        # print("account_info: " + str(cookie_values))
    else:
        cookie_values = None

    return render_template('forms/' + app.config['FORM'].__name__ + '.html', form=form, cookie_values=cookie_values)

# Super scout
@app.route('/superScout.html')
def superScout():
    # Tell the scouts that the super scout is ready 
    socketio.emit('superScoutConnect')
    return render_template('superScout.html')

# Normal scout submit
@app.route('/scoutSubmit.html', methods=['POST', 'GET'])
def scoutSubmit():
    print(f"got request via {request.method}")
    site = make_response(render_template("scoutSubmit.html"))
    if request.method == 'POST':
        print("working")
        data = request.form.to_dict()
        print("DATA: " + str(data))

        if 'autoMobility' not in data.keys():
            data['autoMobility'] = 'n'

        if 'spotlight' not in data.keys():
            data['spotlight'] = 'n'

        # append data to data/scout.csv
        with open('data/scout.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(data.keys()))
            writer.writerow(data)

            f.close()

        # append data to sqlite3 database
        conn = sqlite3.connect('data/scoutState.db')
        cursor = conn.cursor()
        
        scoutID = data['scoutID']
        matchNum = data['matchNum']
        teamNum = data['teamNum']

        site.set_cookie("acc_info", str(scoutID))
        print(f"scout: {scoutID}")

        socketio.emit('scoutSubmit', data)

        del data['matchNum']
        del data['teamNum']
        del data['scoutID']

        # make sure checkboxes appear
        if 'autoMobility' not in data:
            data['autoMobility'] = 'n'
        if 'spotlight' not in data:
            data['spotlight'] = 'n'

        current_time = str(datetime.now())
            
        cursor.execute('INSERT INTO scoutData (timestamp, matchNum, teamNum, scoutID, data) VALUES (?, ?, ?, ?, ?)', 
                       (current_time, matchNum, teamNum, scoutID, json.dumps(data)))
        conn.commit()
        conn.close()

        print(data)

    return site

# Super scout submit
@app.route('/superScoutSubmit.html', methods=['GET', 'POST'])
def superScoutSubmit():
    print(f"got request via {request.method}")
    if request.method == 'POST':
        # print the data recieved from the form
        for key, value in request.form.items():
            print(f"{key}: {value}")

        print(request.form.to_dict())
        data = request.form.to_dict()


        # append data to sql database
        conn = sqlite3.connect('data/scoutState.db')
        cursor = conn.cursor()
            
        cursor.execute('INSERT INTO superScoutData (timestamp, matchNum, red1Ranking, red2Ranking, red3Ranking, blue1Ranking, blue2Ranking, blue3Ranking, redAmps, blueAmps, info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (str(datetime.now()), data['matchNum'], data['red1Ranking'], data['red2Ranking'], data['red3Ranking'], data['blue1Ranking'], data['blue2Ranking'], data['blue3Ranking'], data['redAmps'], data['blueAmps'], data['info']))
        conn.commit()
        conn.close()

        print(data)


        return redirect(url_for('superScoutSubmit'))

    return render_template('superScoutSubmit.html')

# Favicon
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
    print('getTeams')
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

@socketio.on('message')
def handle_message(data):
    print('message: ' + data['msg'])
    emit('message', data, broadcast=True)



# Run app  
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
