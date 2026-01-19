# Import Flask application
from flask import Flask, render_template, request, redirect, url_for, make_response, Response
from game import *
from flask_socketio import SocketIO, emit
import csv, secrets, json, sqlite3
from blueprints.PitScout.pitScout import pitScout_bp
# from pitScout_bp import my_blueprint 
from datetime import datetime
import os
from zeroconf import Zeroconf, ServiceInfo
import socket
import updateSheet

import psutil


# Create app
app = Flask(__name__)
app.register_blueprint(pitScout_bp,url_prefix='/pitScout.html')
socketio = SocketIO(app)

# Configure app -- this is all of the constants used throughout the app
app.config['SCOUT_FORM'] = RebuiltForm  # Change this to the form you want to use
app.config['SUPER_FORM'] = ReefscapeSuperScoutForm 
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['DB_PATH'] = os.path.join(app.root_path, 'data', 'scoutWorlds2025.db') # change to your database path in /data
app.config['SCOUT_TABLE'] = "scoutData"
app.config['SUPER_SCOUT_TABLE'] = "superScoutData"

# Create scoutData and superScoutData tables in sqlite database
conn = sqlite3.connect(app.config['DB_PATH'])
cursor = conn.cursor()
cursor.execute(f'''CREATE TABLE IF NOT EXISTS {app.config['SCOUT_TABLE']} (
    timestamp STRING PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    matchNum INTEGER,
    teamNum INTEGER,
    scoutID STRING, 
    data TEXT
)
''')
cursor.execute(f'''CREATE TABLE IF NOT EXISTS {app.config['SUPER_SCOUT_TABLE']} (
    timestamp STRING PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    matchNum INTEGER,
    alliance STRING,
    scoutID STRING,
    data TEXT
)
''')
conn.commit()
conn.close()

# Index
@app.route('/')
def index():
    return render_template('home.html', name=app.config['SCOUT_FORM'].name) # creates home page with form name

# Home
@app.route('/home.html')
def home():
    return render_template('home.html', name=app.config['SCOUT_FORM'].name)

# Test
@app.route('/test.html')
def test():
    # Instantiate your SCOUT_FORM
    form = app.config['SCOUT_FORM']()

    # Optionally retrieve cookies
    account_info = request.cookies.get("acc_info")
    cookie_values = account_info if account_info else None

    # Pass 'form' and 'cookie_values' to test.html
    return render_template('test2.html', form=form, cookie_values=cookie_values)

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
    form = app.config['SCOUT_FORM']()
    
    account_info = request.cookies.get("acc_info")
    if account_info is not None:
        cookie_values = account_info
    else:
        cookie_values = None

    return render_template('forms/' + app.config['SCOUT_FORM'].__name__ + '.html',
                           form=form, 
                           cookie_values=cookie_values)

# Super scout
@app.route('/superScout.html')
def superScout():
    form = app.config['SUPER_FORM']()
    # Tell the scouts that the super scout is ready 
    socketio.emit('superScoutConnect')
    print(vars(CrescendoSuperScoutForm()))
    
    return render_template('superForms/' + app.config['SUPER_FORM'].__name__ + '.html', form=form)

# Admin
@app.route('/megaScout.html')
def megaScout():
    conn = sqlite3.connect(app.config['DB_PATH'])
    cursor = conn.cursor()
    data = cursor.execute(f"select data from {app.config['SCOUT_TABLE']}")
    vals = cursor.fetchall()
    newArr = []
    for i in range(len(vals)):
        newArr.append(json.loads(vals[i][0]))
    print(newArr)
    return render_template('megaScout.html', dat=newArr, len=len(newArr))

# Normal scout submit
@app.route('/scoutSubmit.html', methods=['POST', 'GET'])
def scoutSubmit():
    print(f"got request via {request.method}")
    site = make_response(render_template("scoutSubmit.html"))
    if request.method == 'POST':
        print("working")
        data = request.form.to_dict()
        print("DATA: " + str(data))
        print("hasn't failed yet")

        # append data to data/scout.csv
        with open('data/scout.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(data.keys()))
            data['info'] = data.get('info').encode("utf-8")
            writer.writerow(data)
            f.close()
        print("hasn't failed yet")
        data['info'] = data.get('info').decode("utf-8")
        print(data)

        # append data to sqlite3 database
        conn = sqlite3.connect(app.config['DB_PATH'])
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

        # Ensure checkbox and optional fields always exist and are normalized
        bool_fields = ['autoMobility', 'teleopPassed', 'teleopDefense', 'climbFailed', 'failure']

        for k in bool_fields:
            if k not in data:
                data[k] = False
            else:
                v = str(data[k]).lower()
                data[k] = (v in ['y', 'on', 'true', '1'])

        # Field-map clicks (CSV string
        if 'teleopScoreLocation' not in data or not str(data['teleopScoreLocation']).strip():
            data['teleopScoreLocation'] = 'none'


        current_time = str(datetime.now())

        print("still working")
            
        cursor.execute(f"INSERT INTO {app.config['SCOUT_TABLE']} (timestamp, matchNum, teamNum, scoutID, data) VALUES (?, ?, ?, ?, ?)", 
                       (current_time, matchNum, teamNum, scoutID, json.dumps(data)))
        print("failed now")
        conn.commit()
        conn.close()

        print(data)

    return site


# Pit Scout
@app.route('/pitScout.html', methods=['POST', 'GET'])
def pitScout():
    return render_template('/pitScout.html')

@app.route('/pitScoutSubmit.html', methods=['POST', 'GET'])
def pitScoutSubmit():
    return render_template('/pitScoutSubmit.html')

# Super scout submit
@app.route('/superScoutSubmit.html', methods=['GET', 'POST'])
def superScoutSubmit():
    print(f"Received Super Scout {request.method} request:")
    if request.method == 'POST':
        for key, value in request.form.items():
            print(f"{key}: {value}")

        print(request.form.to_dict())
        data = request.form.to_dict()

        # define fields to keep
        matchNum = data['matchNum']
        alliance = data['alliance']
        scoutID = data['scoutID']

        socketio.emit('scoutSubmit', data)

        # remove unneeded data
        del data['matchNum']
        del data['alliance']
        del data['scoutID']

       

        # append data to sql database
        conn = sqlite3.connect(app.config['DB_PATH'])
        cursor = conn.cursor()
            
        cursor.execute(f"INSERT INTO {app.config['SUPER_SCOUT_TABLE']} (timestamp, matchNum, alliance, scoutID, data) VALUES (?, ?, ?, ?, ?)",
                       (str(datetime.now()), matchNum, alliance, scoutID, json.dumps(data)))
        conn.commit()
        conn.close()

        print(data)

        # return redirect(url_for('superScoutSubmit'))

    return render_template('superScoutSubmit.html')

# Favicon
@app.route('/favicon.ico')
def favicon():
    with open('static/favicon.ico', 'rb') as f:
        r = Response(f.read())
        r.content_type = "image/png"
        return r
    
# Teapot
@app.route('/teapot')
def teapot():
    return "<img src='static/teapot.jpg'/>", 418

#### Socket routes ####
@socketio.on('echo')  # test route
def handle_echo(data):
    print(f"received echo: {data}")
    # plugged = battery.power_plugged
    # percent = str(battery.percent)
    # plugged = "Plugged In" if plugged else "Not Plugged In"
    # print(percent+'% | '+plugged)
    emit('echo', data)

@socketio.on('getTeams')  # activated when the super scout clicks the button to fetch teams
def handle_fetchTeams(data):
    print('getTeams')
    matchNum = data['matchNum']
    with open('data/matchList.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['matchNum'] == matchNum:
                emit('sendTeams', row)
                return
    # if no matchNum found, send error
    emit('sendTeams', {
        'red1': 'error', 'red2': 'error', 'red3': 'error',
        'blue1': 'error', 'blue2': 'error', 'blue3': 'error'
    })

@socketio.on('batteryInfo')
def handle_battery_info(data):
    print(f"Received battery info: {data}")
    # You can process the battery info here or store it in a database
    emit('battery_response', data)


# Broadcast routes
@socketio.on('scoutSelect')  # activated when a scout chooses their team
def handle_scoutSelect(data):
    print(f"received scoutSelect: {data}")
    # battery = psutil.sensors_battery()
    # emit('battery',battery)
    emit('scoutSelect', data, broadcast=True)

@socketio.on('scoutAssign')  # activated when the mega scout assigns the team#
def handle_scoutAssign(data):
    print(f"received scoutAssign: {data}")
    emit('scoutAssign', data, broadcast=True)

@socketio.on('postData')
def handle_postData(data):
    status = updateSheet.send_match(int(data['matchNum']))
    print(status)
    emit('postDataStatus', {'status': status})


@socketio.on('matchReset')
def handle_matchReset():
    print('received matchReset')
    emit('matchReset', broadcast=True)

@socketio.on('message')
def handle_message(data):
    print('message: ' + data['msg'])
    emit('message', data, broadcast=True)

# Run app 

if __name__ == '__main__':
    # Get the local IP address of your server
    ip_address = socket.gethostbyname(socket.gethostname())

    # Create the service info
    info = ServiceInfo(
        "_http._tcp.local.",
        "purplescout._http._tcp.local.",
        addresses=[socket.inet_aton(ip_address)],
        port=5000,
        properties={},
        server="purplescout.local."
    )

    # Register the service with Zeroconf
    zeroconf = Zeroconf()
    try:
        zeroconf.register_service(info)
        print(f"Service registered successfully at {ip_address}:5000")
    except Exception as e:
        print(f"Warning: Could not register zeroconf service: {e}")
        print("The app will continue running without mDNS discovery")

    # Start the Flask app
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)

    # After Flask app stops, unregister the service
    try:
        zeroconf.unregister_service(info)
    except:
        pass
    zeroconf.close()
