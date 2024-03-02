# scrape.py: example usage of the python TBA API, unused for now
import tbapy
import csv
import sqlite3
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_file
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

tba = tbapy.TBA('rZxJQVjP40eTtskoUbT3OWTKEnKNxk8McjB9QqRdU8mT78o8EN3OuzuMppJTADtV')

team = tba.team(418)

# Current event
EVENT = '2023txbel'
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

# write matchList to data/matchList.csv
with open('data/matchList.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["matchID", "matchNum", "red1", "red2", "red3", "blue1", "blue2", "blue3"])
    for row in matchList:
        writer.writerow(row)
    f.close()

teams = tba.event_teams(EVENT)
data = sqlite3.connect('data/scout.db').cursor().execute(
      "SELECT * FROM scoutData").fetchall()


def UpdateSheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'robotics-scouting-414004-d07cb2963d15.json', [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ])
    client = gspread.authorize(creds)
    spreadsheet = client.open('Belton Scouting TEST')  #Title on google sheet
    worksheet = spreadsheet.get_worksheet(1)

    form_data = data = sqlite3.connect('data/scout.db').cursor().execute("SELECT * FROM scoutData").fetchall()

    # Set start index of all columns as the value in the second row 
    rowIndex = len(worksheet.col_values(1)) + 1

    for single_submission in form_data:
        for entry_index in range(len(single_submission)):
            worksheet.update_cell(rowIndex, entry_index + 1, single_submission[entry_index])  #Update Id's    
        rowIndex += 1

def drive_url(image_bytes, filename=""):
  # Upload the image to Google Drive
  media = MediaIoBaseUpload(io.BytesIO(image_bytes),
                            mimetype="image/*",
                            resumable=True)
  file_metadata = {
      'name': filename,
      'parents': ['1gfLgh6UpAb1azj6ymqagRmYN9pcrmFVj']
  }
  # Authenticate using the service account credentials
  credentials = service_account.Credentials.from_service_account_file(
      'robotics-scouting-414004-d07cb2963d15.json',
      scopes=['https://www.googleapis.com/auth/drive'])

  # Create the Google Drive API service
  drive_service = build('drive', 'v3', credentials=credentials)
  file = drive_service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
  return f'"https://drive.google.com/uc?id={file["id"]}"'

UpdateSheets()
print("data from scoutData table", data)