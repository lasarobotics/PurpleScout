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

import ssl


# Create app
app = Flask(__name__)
app.register_blueprint(pitScout_bp,url_prefix='/pitScout.html')
socketio = SocketIO(app)

# Configure app
app.config['SCOUT_FORM'] = RebuiltForm  # Change this to the form you want to use
app.config['SUPER_FORM'] = ReefscapeSuperScoutForm
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['DB_PATH'] = os.path.join(app.root_path, 'data', 'scouting_dat.db') # change to your database path in /data
app.config['DB_OLD_PATH'] = os.path.join(app.root_path, 'data', 'scouting_dat_old.db')
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

# Function to change value
def changeValue(inputString="", val=""):
    print("input: " + inputString + " | val: " + val)

    val_index = inputString.find('value="') + len('value="')
    print("val index: " + str(val_index) + " | length: " + str(len(inputString)))

    print("left: " + str(inputString[:val_index]))
    print("right: " + str(inputString[val_index:]))
    inputString = inputString[:val_index] + val + inputString[val_index:]

    print("input: " + inputString)
    return inputString

# Flask Route: Index
@app.route('/')
def index():
    return render_template('home.html', name=app.config['SCOUT_FORM'].name) # creates home page with form name

# Flask Route: Home
@app.route('/home.html')
def home():
    return render_template('home.html', name=app.config['SCOUT_FORM'].name)

# Flask Route: Scout
@app.route('/scout.html')
def scout():
    form = app.config['SCOUT_FORM']()
    
    account_info = request.cookies.get("acc_info")
    tInfo = request.cookies.get("team_info")

    if account_info is not None:
        cookie_values = account_info
    else:
        cookie_values = None


    teamInfoSend = ""
    if tInfo is not None:
        team_info = int(tInfo)
        if team_info < 4:
            teamInfoSend = "red"+str(team_info)
        else:
            teamInfoSend = "blue"+str(int(team_info)-3)
    else:
        teamInfoSend = None

    print(teamInfoSend)

    return render_template('forms/' + app.config['SCOUT_FORM'].__name__ + '.html',
                           form=form, 
                           cookie_values=cookie_values,
                           teamInfo=teamInfoSend)

# Flask Route: Super Scout
@app.route('/superScout.html')
def superScout():
    # form = app.config['SUPER_FORM']()
    # # Tell the scouts that the super scout is ready 
    # socketio.emit('superScoutConnect')
    # print(vars(CrescendoSuperScoutForm()))
    
    # return render_template('superForms/' + app.config['SUPER_FORM'].__name__ + '.html', form=form)
    return render_template('superScout2026.html')

# Flask Route: Mega Scout (Admin)
@app.route('/megaScout.html')
def megaScout():
    conn = sqlite3.connect(app.config['DB_PATH'])
    cursor = conn.cursor()
    data = cursor.execute(f"select data from {app.config['SCOUT_TABLE']}")
    vals = cursor.fetchall()
    newArr = []
    for i in range(len(vals)):
        newArr.append(json.loads(vals[i][0]))
    return render_template('megaScout.html', dat=newArr, len=len(newArr))

# API: Get current scouting data as JSON
@app.route('/api/mega/current')
def api_mega_current():
    
    # Get optional matchNum filter from query parameters
    matchNum = request.args.get('matchNum')
    
    try:
        conn = sqlite3.connect(app.config['DB_PATH'])
        cursor = conn.cursor()
        
        # Build query with optional matchNum filter
        if matchNum:
            cursor.execute(f"SELECT timestamp, matchNum, teamNum, scoutID, data FROM {app.config['SCOUT_TABLE']} WHERE matchNum = ? ORDER BY timestamp DESC", (matchNum,))
        else:
            cursor.execute(f"SELECT timestamp, matchNum, teamNum, scoutID, data FROM {app.config['SCOUT_TABLE']} ORDER BY timestamp DESC")
        
        rows = cursor.fetchall()
        conn.close()
        out = []
        for ts, mn, tn, sid, d in rows:
            try:
                parsed = json.loads(d)
            except:
                parsed = d
            out.append({'timestamp': ts, 'matchNum': mn, 'teamNum': tn, 'scoutID': sid, 'data': parsed})
            # print("Check after: ", {'timestamp': ts, 'matchNum': mn, 'teamNum': tn, 'scoutID': sid, 'data': parsed})
        return json.dumps(out), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        print(f"Error fetching current data: {e}")
        return json.dumps([]), 500, {'Content-Type': 'application/json'}
    

# API: Get old scouting data as JSON
@app.route('/api/mega/old')
def api_mega_old():
    
    # Get optional matchNum filter from query parameters
    matchNum = request.args.get('matchNum')
    
    try:
        if not os.path.exists(app.config['DB_OLD_PATH']):
            return json.dumps([]), 200, {'Content-Type': 'application/json'}
        conn = sqlite3.connect(app.config['DB_OLD_PATH'])
        cursor = conn.cursor()
        
        # Build query with optional matchNum filter
        if matchNum:
            cursor.execute(f"SELECT timestamp, matchNum, teamNum, scoutID, data FROM {app.config['SCOUT_TABLE']} WHERE matchNum = ? ORDER BY timestamp DESC", (matchNum,))
        else:
            cursor.execute(f"SELECT timestamp, matchNum, teamNum, scoutID, data FROM {app.config['SCOUT_TABLE']} ORDER BY timestamp DESC")
        
        rows = cursor.fetchall()
        conn.close()
        out = []
        for ts, mn, tn, sid, d in rows:
            try:
                parsed = json.loads(d)
            except:
                parsed = d
            out.append({'timestamp': ts, 'matchNum': mn, 'teamNum': tn, 'scoutID': sid, 'data': parsed})
            # print("Check after ", {'timestamp': ts, 'matchNum': mn, 'teamNum': tn, 'scoutID': sid, 'data': parsed})
        return json.dumps(out), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        print(f"Error fetching old data: {e}")
        return json.dumps([]), 500, {'Content-Type': 'application/json'}

# Flask Route: Scout Submit
@app.route('/scoutSubmit.html', methods=['POST', 'GET'])
def scoutSubmit():
    # Submit POST request has been received.
    site = make_response(render_template("scoutSubmit.html"))
    if request.method == 'POST':
        data = request.form.to_dict()
        # print("DATAATAAATTATA", data)
        data = {k:v for k, v in data.items() if k!= "heatmap_data"}
        data = {k:v for k, v in data.items() if k!= "climb_map_data"}
        print(data)



        # Store scouting data locally in a CSV file (BACKUP)
        with open('data/scouting_dat.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(data.keys()))
            data['info'] = data.get('info').encode("utf-8")
            writer.writerow(data)
            f.close()
            
        data['info'] = data.get('info').decode("utf-8")

        # Append scouting data to the SQLite Database
        conn = sqlite3.connect(app.config['DB_PATH'])
        cursor = conn.cursor()
        
        scoutID = data['scoutID']
        matchNum = data['matchNum']
        teamNum = data['teamNum']

        teamNumUpdated = ""

        print(list(data.keys()))

        with open('data//matchList.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if str(matchNum) == row[1]:
                    if (str(teamNum) == row[2]):
                        teamNumUpdated = "1"
                    elif (str(teamNum) == row[3]):
                        teamNumUpdated = "2"
                    elif (str(teamNum) == row[4]):
                        teamNumUpdated = "3"
                    elif (str(teamNum) == row[5]):
                        teamNumUpdated = "4"
                    elif (str(teamNum) == row[6]):
                        teamNumUpdated = "5"
                    elif (str(teamNum) == row[7]):
                        teamNumUpdated = "6"

        site.set_cookie("acc_info", str(scoutID))
        site.set_cookie("team_info", str(teamNumUpdated))
        print(teamNumUpdated)
        print(f"scout: {scoutID}")
        print(f"team: {teamNum}")

        
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

            
        cursor.execute(f"INSERT INTO {app.config['SCOUT_TABLE']} (timestamp, matchNum, teamNum, scoutID, data) VALUES (?, ?, ?, ?, ?)", 
                       (current_time, matchNum, teamNum, scoutID, json.dumps(data)))
        conn.commit()
        conn.close()

        # if 'heatmap_data' in data and data['heatmap_data']:
        #     try:
        #         heatmap_svg = data['heatmap_data']
                
        #         # Create directory if it doesn't exist
        #         heatmap_dir = os.path.join(app.root_path, 'data', 'heatmap_captures')
        #         if not os.path.exists(heatmap_dir):
        #             os.makedirs(heatmap_dir)
                
        #         # Generate filename
        #         filename = f"match{matchNum}_team{teamNum}_{scoutID}_{int(datetime.now().timestamp())}.svg"
        #         filepath = os.path.join(heatmap_dir, filename)
                
        #         # Write SVG string to file
        #         with open(filepath, 'w') as f:
        #             f.write(heatmap_svg)
                
        #         print(f"Saved heatmap to {filepath}")
                
        #         # Remove huge SVG string from data before saving to CSV/DB to keep them clean
        #         del data['heatmap_data']
                
        #     except Exception as e:
        #         print(f"Error saving heatmap: {e}")

        # if 'climb_map_data' in data and data['climb_map_data']:
        #     try: 
        #         climb_svg = data['climb_map_data']
        #         heatmap_dir = os.path.join(app.root_path, 'data', 'heatmap_captures')
        #         if not os.path.exists(heatmap_dir):
        #             os.makedirs(heatmap_dir)
                
        #         filename = f"climb_match{matchNum}_team{teamNum}_{scoutID}_{int(datetime.now().timestamp())}.svg"
        #         filepath = os.path.join(heatmap_dir, filename)
                
        #         with open(filepath, 'w') as f:
        #             f.write(climb_svg)
                
        #         print(f"Saved climb map to {filepath}")
        #         del data['climb_map_data']
        #     except Exception as e:
        #         print(f"Error saving climb map: {e}")
        answer = (data["teleopScoreLocation"]).split(",") if "teleopScoreLocation" in data else []
        data['teleopScoreLocation'] = str(answer)


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

    # Check if match is complete (6 scouts submitted)
    conn = sqlite3.connect(app.config['DB_PATH'])
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {app.config['SCOUT_TABLE']} WHERE matchNum = ?", (matchNum,))
    count = cursor.fetchone()[0]
    print(f"Match {matchNum} has {count} scout submissions.")
    conn.close()

    #Send the previous data once resetting for the next match.
    # print(count)
    # if count % 1 == 0:
    #     print(f"Match {int(matchNum) -1} complete, sending data.")
    #     status = updateSheet.send_match(int(matchNum)-1)
    #     print(status)
    
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
    print(status, "aaaahstatus")
    emit('postDataStatus', {'status': status})

@socketio.on('setCurrentMatch')
def handle_setCurrentMatch(data):
    matchNum = data.get('matchNum')
    if matchNum:
        with open('data/current_match.txt', 'w') as f:
            f.write(str(matchNum))
        print(f"Current match set to {matchNum}")

@socketio.on('matchReset')
def handle_matchReset(data):
    print('received matchReset')
    emit('matchReset', broadcast=True)
    matchNum = data['matchNum']
    try:
        # Check if match is complete (6 scouts submitted)
        conn = sqlite3.connect(app.config['DB_PATH'])
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {app.config['SCOUT_TABLE']} WHERE matchNum = ?", (matchNum,))
        count = cursor.fetchone()[0]
        print(f"Match {matchNum} has {count} scout submissions.")
        conn.close()

        print(count)
        if count % 1 == 0:
            print(f"Match {int(matchNum) -1} complete, sending data.")
            status = updateSheet.send_match(int(matchNum))
            print(status)
    except:
        print("No WiFi-- try again later!")
        
    

@socketio.on('message')
def handle_message(data):
    print('message: ' + data['msg'])
    emit('message', data, broadcast=True)

# Run app 

if __name__ == '__main__':
    # Only register Zeroconf in the reloader process (not the main process)
    # This prevents duplicate registration when debug=True
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        zeroconf = None
        try:
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
            zeroconf.register_service(info)
            print(f"✓ Zeroconf service registered: purplescout._http._tcp.local. at {ip_address}:5000")
        
        except Exception as e:
            print(f"⚠ Warning: Could not register Zeroconf service: {e}")
            print("  The app will continue running, but may not be discoverable via mDNS.")

        sslCert = "server.crt"
        sslKey = "server.key"

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=sslCert, keyfile=sslKey)


        
        try:
            # Start the Flask app
            socketio.run(app, host='0.0.0.0', debug=True, ssl_context=context, allow_unsafe_werkzeug=True)
        finally:
            # After Flask app stops, unregister the service
            if zeroconf is not None:
                try:
                    zeroconf.unregister_service(info)
                    zeroconf.close()
                    print("✓ Zeroconf service unregistered")
                except Exception as e:
                    print(f"⚠ Warning: Could not unregister Zeroconf service: {e}")
    else:
        # In the main process, just start the Flask app
        socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
