import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_file, Blueprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload  
import time

pitScout_bp = Blueprint('pitScout', __name__, template_folder="templates", url_prefix='/pitScout.html')

worksheet = None
openedSheets = False

#File directory to SQL Table
#db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/Pit Scouting/RobotInfo.db')
db_path = "data/pitScoutData2.db"

#Only needs to be called when remaking SQL Table NOT every time you reload the page
def InitSQL():
  # Connect to the SQLite database (or create it if it doesn't exist)
  conn = sqlite3.connect(db_path)

  # Create a cursor object to execute SQL queries
  cursor = conn.cursor()

  # Define a SQL statement to create a table
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS Robots (
      Team INT PRIMARY KEY,
      Intake TEXT NOT NULL,
      Archetype TEXT NOT NULL,
      Drive TEXT NOT NULL,      
      Auto TEXT NOT NULL,
      Can_Shallow BOOLEAN,
      Can_Deep BOOLEAN,
      Weight TEXT NOT NULL,
      DriveT TEXT NOT NULL,
      Image_FileType TEXT NOT NULL,
      Image LONGBLOB,
      Additional_Info TEXT
    );'''
  )

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS Robots_Posted(
      Team INT PRIMARY KEY
    );'''
  )

  conn.commit()
  conn.close()

#Is called every time you are publishing to Google Sheets. Requires Internet
def initSheets():
  global worksheet, openedSheets

  # Google Sheets API credentials
  creds = ServiceAccountCredentials.from_json_keyfile_name(
    'PitScouting_GoogleSheetsKey.json', 
    [ 'https://spreadsheets.google.com/feeds',
      'https://www.googleapis.com/auth/drive' ]
  )
  client = gspread.authorize(creds)

  # Open the Google Sheets spreadsheet
  spreadsheet = client.open('Manor Scouting 2025')  #Title on google sheet
  worksheet = spreadsheet.get_worksheet_by_id(1991768468)  # Assuming you want to use the first worksheet
  openedSheets = True 

@pitScout_bp.route('/initSQL')
def init():
  InitSQL()
  return redirect(url_for("base"))

@pitScout_bp.route('/')
def base():
  InitSQL()
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()
  return render_template(
    'pitScout.html',
    unposted_robots = cursor.execute('''
      SELECT Robots.*
      FROM Robots
      LEFT JOIN Robots_Posted ON Robots.Team = Robots_Posted.Team
      WHERE Robots_Posted.Team IS NULL; '''
    ).fetchall(),
    posted_robots = cursor.execute('''
      SELECT Robots.*
      FROM Robots
      LEFT JOIN Robots_Posted ON Robots.Team = Robots_Posted.Team
      WHERE Robots_Posted.Team IS NOT NULL; '''
    ).fetchall()
  )


@pitScout_bp.route('/ClearAll', methods=['GET', 'POST'])
def ClearAll():
  conn = sqlite3.connect(db_path)
  conn.cursor().execute('DELETE FROM Robots;')
  conn.cursor().execute('DELETE FROM Robots_Posted;')
  conn.commit()
  conn.close()
  
  return redirect(url_for('pitScout.base'))


@pitScout_bp.route('//ClearUnposted', methods=['GET', 'POST'])
def ClearUnposted():
  conn = sqlite3.connect(db_path)
  conn.cursor().execute('''
    DELETE FROM Robots WHERE Team IN (
      SELECT Robots.Team
      FROM Robots
      LEFT JOIN Robots_Posted ON Robots.Team = Robots_Posted.Team
      WHERE Robots_Posted.Team IS NULL
    );'''
  )
  conn.commit()
  conn.close()

  return redirect(url_for('pitScout.base'))

@pitScout_bp.route('/ClearPosted', methods=['GET', 'POST'])
def ClearPosted():
  conn = sqlite3.connect(db_path)
  conn.cursor().execute('''
    DELETE FROM Robots WHERE Team IN (
      SELECT Robots.Team
      FROM Robots
      LEFT JOIN Robots_Posted ON Robots.Team = Robots_Posted.Team
      WHERE Robots_Posted.Team IS NOT NULL
    );'''
  )
  conn.commit()
  conn.close()

  return redirect(url_for('pitScout.base'))

@pitScout_bp.route('/ClearPostedIds', methods=['GET', 'POST'])
def ClearPostedIds():
  conn = sqlite3.connect(db_path)
  conn.cursor().execute('DELETE FROM Robots_Posted;')
  conn.commit()
  conn.close()

  return redirect(url_for('pitScout.base'))


#Adds current HTML inputs into SQL table
@pitScout_bp.route('/pitScoutSubmit', methods=['GET','POST'])
def UpdateSQL():
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  can_deep = request.form.get("climb")
  can_deep = 'True' if can_deep == 'on' else 'False'

  can_shallow = request.form.get("shallow")
  can_shallow = 'True' if can_shallow == 'on' else 'False'
  
  
  img = request.files["image"]

  
  cursor.execute(
    '''INSERT INTO Robots (
      Team,
      Intake,
      Archetype,
      Drive,      
      Auto,
      Can_Shallow,
      Can_Deep,
      Weight,
      DriveT,
      Image_FileType,
      Image,
      Additional_Info
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
    (
      request.form["team"],
      request.form["intake"],
      request.form["scoring"],
      request.form["drive"],
      request.form["auto"],
      can_shallow,
      can_deep,
      request.form["weight"],
      request.form["driver"],
      os.path.splitext(str(img.filename))[1].lower()[1:],
      sqlite3.Binary(img.read()),
      request.form["info"]
      # ^ Takes the file directory, and splits at the . (inclusive), then converts to lowercase and then removes dot
    )
  )

  # Close database connection
  conn.commit()
  cursor.close()
  conn.close()

  return redirect(url_for('pitScout.base'))


#Downloads all images in SQL table to local machine. Does not require internet
@pitScout_bp.route('/Download', methods=['Get', 'POST'])
def DownloadImages():
  data = sqlite3.connect(db_path).cursor().execute("SELECT Team, Image, Image_FileType FROM Robots").fetchall()
  
  for datum in data:
    # Datum values:
    # 0 = Team
    # 1 = Image
    # 2 = Type

    image_stream = io.BytesIO(datum[1])

    with open_file_with_suffix(f"Team_{datum[0]}.{datum[2]}", "wb") as f:
      f.write(image_stream.read())

  return redirect(url_for('pitScout.base'))


#Returns newly opened file with given name and mode. If file name already exists, will add a number after it.
# e.g if you already had a file named "test.txt", it will return "test (2).txt"
def open_file_with_suffix(filename, mode):
  base, ext = os.path.splitext(filename)
  counter = 1
  while os.path.exists(filename):
    counter += 1
    filename = f"{base} ({counter}){ext}"
  return open(filename, mode)


#Takes all current SQL Values and adds them to Google Sheet. Does not skip duplicates in table or already in Sheet. Requires internet.
@pitScout_bp.route('/UpdateSheets')
def UpdateSheets():
  print("starting post")
  global worksheet, openedSheets
  if (not openedSheets):
    initSheets()

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()
  form_data = cursor.execute('''
    SELECT Robots.*
    FROM Robots
    LEFT JOIN Robots_Posted ON Robots.Team = Robots_Posted.Team
    WHERE Robots_Posted.Team IS NULL; '''
  ).fetchall()
  # print(str(form_data[0][-1:0]))

  row_index = len(worksheet.col_values(1))  #Column A
  for datum in form_data:
    team = datum[0]
    image = io.BytesIO(datum[10])
    print("datum",datum)
    url = drive_url(image, filename=f"Team_{team}")
    image = f'=IMAGE({url}, 1)'

    column_index = 1
    for i in range(len(datum)):
      if (i == 9): continue #Odd case: skipping image type
      
      worksheet.update_cell(
        row_index + 1, 
        column_index, 
        datum[i] if i != 10 else image
      )
      column_index += 1
    print("works?")

    cursor.execute(
      '''INSERT INTO Robots_Posted (Team) VALUES (?);''',
      (team,)
    )
    print("works?")
    row_index += 1
    conn.commit()
    time.sleep(10)
  
  conn.commit()
  cursor.close()
  conn.close()
  
  return redirect(url_for('pitScout.base'))


#Takes in image bytes and intended file name. Returns google drive link of image. Requires Internet
def drive_url(image_bytes, filename=""):
  print("in this function")
  # Upload the image to Google Drive
  media = MediaIoBaseUpload((image_bytes),
                            mimetype="image/*",
                            resumable=True)
  print(media)
  
  file_metadata = {
      'name': filename,
      'parents': ['1gfLgh6UpAb1azj6ymqagRmYN9pcrmFVj']
  }
  # Authenticate using the service account credentials
  credentials = service_account.Credentials.from_service_account_file(
      'PitScouting_GoogleSheetsKey.json',
      scopes=['https://www.googleapis.com/auth/drive']
  )

  # Create the Google Drive API service
  drive_service = build('drive', 'v3', credentials=credentials)
  file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
  print("failed")

  return f'"https://drive.google.com/uc?id={file["id"]}"'

InitSQL()