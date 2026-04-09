# Import Flask application
from flask import Flask, render_template, request, redirect, url_for, make_response, Response
from game import *
from flask_socketio import SocketIO, emit
import csv, secrets, json, sqlite3
from blueprints.PitScout.pitScout import pitScout_bp
# from pitScout_bp import my_blueprint 
from datetime import datetime
from io import BytesIO
import os
from zeroconf import Zeroconf, ServiceInfo
import socket
import updateSheet
import psutil

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import xlwings as xw
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
    if tInfo is not None and tInfo != "":
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

        with open('data/matchList.csv', 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                if str(matchNum) == row[1]:
                    if len(row) < 8:
                        # Skip malformed match entries that don't include full team slots.
                        continue
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


def load_all_teams_sheet():
    candidate_names = [
        'ManorOfficialScouting.xlsx',
        'ManorOfficialScouting2026.xlsx'
    ]
    for name in candidate_names:
        excel_path = os.path.join(app.root_path, name)
        if os.path.exists(excel_path):
            xw_app = None
            try:
                # Use xlwings to evaluate formulas
                xw_app = xw.App(visible=False)
                wb = xw_app.books.open(excel_path)
                sheet = wb.sheets['allTeams']
                df = sheet.used_range.options(pd.DataFrame, header=1, index=False).value
                wb.close()
                
                # Clean up the dataframe: remove columns that are all None
                df = df.dropna(axis=1, how='all')
                return df
            except Exception as e:
                print(f"Error loading with xlwings: {e}")
                # Fallback to pandas if xlwings fails
                try:
                    return pd.read_excel(excel_path, sheet_name='allTeams')
                except Exception as e2:
                    print(f"Error loading with pandas: {e2}")
                    continue
            finally:
                if xw_app is not None:
                    try:
                        xw_app.quit()
                    except:
                        pass

    # fallback: scan for matching files in the app root
    for filename in os.listdir(app.root_path):
        if filename.lower().startswith('manorofficialscouting') and filename.lower().endswith('.xlsx'):
            xw_app = None
            try:
                xw_app = xw.App(visible=False)
                wb = xw_app.books.open(os.path.join(app.root_path, filename))
                sheet = wb.sheets['allTeams']
                df = sheet.used_range.options(pd.DataFrame, header=1, index=False).value
                wb.close()
                
                # Clean up the dataframe: remove columns that are all None
                df = df.dropna(axis=1, how='all')
                return df
            except Exception as e:
                print(f"Error loading {filename} with xlwings: {e}")
                continue
            finally:
                if xw_app is not None:
                    try:
                        xw_app.quit()
                    except:
                        pass

    available = [f for f in os.listdir(app.root_path) if f.lower().endswith('.xlsx')]
    raise FileNotFoundError(
        f"Excel file not found. Expected ManorOfficialScouting.xlsx or a matching ManorOfficialScouting*.xlsx in {app.root_path}. "
        f"Found: {available}"
    )

def load_raw_match_data():
    candidate_names = [
        'ManorOfficialScouting.xlsx',
        'ManorOfficialScouting2026.xlsx'
    ]
    for name in candidate_names:
        excel_path = os.path.join(app.root_path, name)
        if os.path.exists(excel_path):
            xw_app = None
            try:
                xw_app = xw.App(visible=False)
                wb = xw_app.books.open(excel_path)
                sheet = wb.sheets['raw match data']
                df = sheet.used_range.options(pd.DataFrame, header=1, index=False).value
                wb.close()
                
                # Clean up the dataframe
                df = df.dropna(axis=1, how='all')
                
                # Rename key columns by position
                if len(df.columns) >= 3:
                    df.columns = ['timestamp' if i == 0 else 
                                 'matchNum' if i == 1 else 
                                 'teamNum' if i == 2 else 
                                 col for i, col in enumerate(df.columns)]
                
                return df
            except Exception as e:
                print(f"Error loading raw match data with xlwings: {e}")
                continue
            finally:
                if xw_app is not None:
                    try:
                        xw_app.quit()
                    except:
                        pass

    available = [f for f in os.listdir(app.root_path) if f.lower().endswith('.xlsx')]
    raise FileNotFoundError(f"Excel file not found for raw match data. Found: {available}")

@app.route('/visualize.html')
def visualize():
    error = None
    try:
        df = load_all_teams_sheet()
        column_counts = df.count()
        visible_columns = [c for c in df.columns if column_counts[c] > 0]
        numeric_cols = [c for c in visible_columns if pd.api.types.is_numeric_dtype(df[c]) and column_counts[c] > 0]

        if len(numeric_cols) == 0:
            error = "No numeric columns with data found in sheet 'allTeams'."
            x_col = y_col = None
        else:
            x_col = request.args.get('x') or numeric_cols[0]
            if x_col not in numeric_cols:
                x_col = numeric_cols[0]
            y_col = request.args.get('y') or (numeric_cols[1] if len(numeric_cols) > 1 else '')
            if y_col and y_col not in numeric_cols:
                y_col = ''

        preview_columns = visible_columns
        preview = df[preview_columns].head(15).fillna('').to_dict(orient='records')
        return render_template('visualize.html',
                               file_name='ManorOfficialScouting2026.xlsx',
                               sheet_name='allTeams',
                               numeric_cols=numeric_cols,
                               x_col=x_col,
                               y_col=y_col,
                               preview=preview,
                               preview_columns=preview_columns,
                               column_counts=column_counts.to_dict(),
                               error=error)
    except Exception as e:
        return render_template('visualize.html',
                               file_name='ManorOfficialScouting2026.xlsx',
                               sheet_name='allTeams',
                               numeric_cols=[],
                               x_col=None,
                               y_col=None,
                               preview=[],
                               preview_columns=[],
                               column_counts={},
                               error=str(e))

@app.route('/visualize_plot.png')
def visualize_plot():
    try:
        df = load_all_teams_sheet()
        column_counts = df.count()
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and column_counts[c] > 0]
        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns with data available for plotting.")

        x_col = request.args.get('x') or numeric_cols[0]
        y_col = request.args.get('y')
        show_labels = request.args.get('labels', 'false').lower() == 'true'
        
        if x_col not in numeric_cols:
            x_col = numeric_cols[0]
        if y_col and y_col not in numeric_cols:
            y_col = ''

        plot_x = df[x_col].dropna()
        if plot_x.empty:
            raise ValueError(f"Selected x-axis column '{x_col}' contains no data.")

        fig, ax = plt.subplots(figsize=(12, 8))
        
        if y_col:
            plot_y = df[y_col].dropna()
            if plot_y.empty:
                raise ValueError(f"Selected y-axis column '{y_col}' contains no data.")
            
            # Create scatter plot with team identification
            scatter = ax.scatter(df[x_col], df[y_col], alpha=0.7, s=50)
            
            if show_labels:
                # Add team name labels to points
                team_names = df['Team Name'].fillna('')
                for i, (x, y, name) in enumerate(zip(df[x_col], df[y_col], team_names)):
                    if pd.notna(x) and pd.notna(y) and name:
                        ax.annotate(name, (x, y), xytext=(5, 5), textcoords='offset points', 
                                  fontsize=8, alpha=0.8, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
            
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"{y_col} vs. {x_col} ({len(df)} teams)")
        else:
            # Histogram
            ax.hist(plot_x, bins=20, color='#4b3f72', edgecolor='black', alpha=0.7)
            ax.set_xlabel(x_col)
            ax.set_title(f"Distribution of {x_col} ({len(df)} teams)")

        ax.grid(True, linestyle='--', alpha=0.35)
        fig.tight_layout()

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        return Response(buf.getvalue(), mimetype='image/png')
    except Exception as e:
        return Response(str(e), status=500, mimetype='text/plain')

@app.route('/trends.html')
def trends():
    error = None
    try:
        df = load_raw_match_data()
        
        # Clean and convert team numbers
        df['teamNum'] = pd.to_numeric(df['teamNum'], errors='coerce')
        df = df.dropna(subset=['teamNum'])
        df['teamNum'] = df['teamNum'].astype(int)
        
        # Get unique teams and matches
        teams = sorted(df['teamNum'].unique())
        matches = sorted(df['matchNum'].dropna().unique())
        
        selected_team = request.args.get('team')
        selected_metric = request.args.get('metric', 'Auto (5-6)')  # Default to auto score
        
        if selected_team:
            try:
                selected_team = int(selected_team)
            except:
                selected_team = None
        
        # Get available metrics (all columns except timestamp, matchNum, teamNum)
        # Filter out None columns and system columns
        all_columns = [col for col in df.columns if col not in ['timestamp', 'matchNum', 'teamNum'] and col is not None]

        # Use all available metrics instead of filtering to specific ones
        potential_metrics = all_columns
        
        return render_template('trends.html',
                               teams=teams,
                               matches=matches,
                               metrics=potential_metrics,
                               selected_team=selected_team,
                               selected_metric=selected_metric,
                               error=error)
    except Exception as e:
        return render_template('trends.html',
                               teams=[],
                               matches=[],
                               metrics=[],
                               selected_team=None,
                               selected_metric='Auto (5-6)',
                               error=str(e))

@app.route('/trends_plot.png')
def trends_plot():
    try:
        df = load_raw_match_data()
        
        # Clean and convert team numbers
        df['teamNum'] = pd.to_numeric(df['teamNum'], errors='coerce')
        df = df.dropna(subset=['teamNum'])
        df['teamNum'] = df['teamNum'].astype(int)
        
        team = request.args.get('team')
        metric = request.args.get('metric', 'Auto (5-6)')
        
        if not team:
            raise ValueError("Please select a team")
        
        try:
            team = int(team)
        except:
            raise ValueError("Invalid team number")
        
        # Filter data for the selected team
        team_data = df[df['teamNum'] == team].copy()
        team_data = team_data.sort_values('matchNum')
        
        if team_data.empty:
            raise ValueError(f"No data found for team {team}")
        
        # Try to extract numeric values from the metric column
        metric_values = []
        match_nums = []
        
        for idx, row in team_data.iterrows():
            match_num = row['matchNum']
            metric_val = row.get(metric)
            
            # Try to parse the metric value as a number
            try:
                if isinstance(metric_val, str):
                    # Look for numbers in the string
                    import re
                    numbers = re.findall(r'\d+\.?\d*', metric_val)
                    if numbers:
                        val = float(numbers[0])
                    else:
                        val = 0
                elif pd.isna(metric_val):
                    val = 0
                else:
                    val = float(metric_val)
                
                metric_values.append(val)
                match_nums.append(match_num)
            except:
                continue
        
        if not metric_values:
            raise ValueError(f"No numeric data found for metric '{metric}' and team {team}")
        
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#222')
        ax.set_facecolor('#333')
        
        # Plot the data
        ax.plot(match_nums, metric_values, 'o-', linewidth=2, markersize=8, color='#663399', markerfacecolor='#4b3f72', markeredgecolor='white')
        
        # Style the axes and labels
        ax.set_xlabel('Match Number', color='white', fontsize=12, fontweight='bold')
        ax.set_ylabel(str(metric), color='white', fontsize=12, fontweight='bold')
        ax.set_title(f'Team {team} - {metric} Over Matches', color='white', fontsize=14, fontweight='bold', pad=20)
        
        # Style the grid
        ax.grid(True, linestyle='--', alpha=0.3, color='#666')
        
        # Style the ticks
        ax.tick_params(colors='white', labelsize=10)
        for spine in ax.spines.values():
            spine.set_edgecolor('#666')
        
        # Add value labels on points with better styling
        for x, y in zip(match_nums, metric_values):
            ax.annotate(f'{y}', (x, y), xytext=(0, 10), textcoords='offset points', 
                       ha='center', fontsize=9, color='white',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='#444', alpha=0.8, edgecolor='#666'))
        
        fig.tight_layout()
        
        fig.tight_layout()
        
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        return Response(buf.getvalue(), mimetype='image/png')
    except Exception as e:
        return Response(str(e), status=500, mimetype='text/plain')

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
            socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False, ssl_context=context, allow_unsafe_werkzeug=True)
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
        socketio.run(app, host='0.0.0.0', debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
