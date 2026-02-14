# game.py: define the form for the scout page

# Below is an example from Charged Up 2023.
import wtforms
from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, TextAreaField, BooleanField, SelectField, StringField, FormField
from wtforms.validators import *

class ScoutForm(FlaskForm):
    def fields(self):
        return [key for key in self.__dict__.keys() if not key.startswith('_')]

class ChargedUpScoutForm(ScoutForm):
    name = "Charged Up 2023"

    matchNum = IntegerField('matchNumber', validators=[DataRequired()])
    teamNum = IntegerField('teamNumber', validators=[DataRequired()])
    

    autoHighCones = IntegerField('autoHighCones', validators=[DataRequired()], default=0)
    autoHighCubes = IntegerField('autoHighCubes', validators=[DataRequired()], default=0)
    autoMidCones = IntegerField('autoMidCones', validators=[DataRequired()], default=0)
    autoMidCubes = IntegerField('autoMidCubes', validators=[DataRequired()], default=0)
    autoLowCones = IntegerField('autoLowCones', validators=[DataRequired()], default=0)
    autoLowCubes = IntegerField('autoLowCubes', validators=[DataRequired()], default=0)
    teleopHighCones = IntegerField('teleopHighCones', validators=[DataRequired()], default=0)
    teleopHighCubes = IntegerField('teleopHighCubes', validators=[DataRequired()], default=0)
    teleopMidCones = IntegerField('teleopMidCones', validators=[DataRequired()], default=0)
    teleopMidCubes = IntegerField('teleopMidCubes', validators=[DataRequired()], default=0)
    teleopLowCones = IntegerField('teleopLowCones', validators=[DataRequired()], default=0)
    teleopLowCubes = IntegerField('teleopLowCubes', validators=[DataRequired()], default=0)

    defense = RadioField('defense', validators=[DataRequired()], choices=[
        ('none', 'Did not play defense'),
        ('poor', 'Poor defense'),
        ('average', 'Average defense'),
        ('excellent', 'Excellent defense!')
    ])

    sub = RadioField('sub', validators=[DataRequired()], choices=[
        ('single', 'Single substation'),
        ('double', 'Double substation'),
        ('both', 'Used both substations'),
    ])

    droppedPieces = IntegerField('Dropped Pieces', validators=[DataRequired()])

    info = TextAreaField('info', validators=[DataRequired()])

class UltimateAscentScoutForm(ScoutForm):
    name = "Ultimate Ascent 2013"

    matchNum = IntegerField('matchNumber', validators=[DataRequired()])
    teamNum = IntegerField('teamNumber', validators=[DataRequired()])

    discsScored = IntegerField('discsScored', validators=[DataRequired()])
    discsMissed = IntegerField('discsMissed', validators=[DataRequired()])

    climb = RadioField('climb', validators=[DataRequired()], choices=[
        (0, 'No climb'),
        (1, 'First level'),
        (2, 'Second level'),
        (3, 'Third level'),
    ])

    info = TextAreaField('info', validators=[DataRequired()])

class CrescendoForm(FlaskForm):

    name = "Crescendo 2024"

    # Basic match and team information
    matchNum = IntegerField('matchNumber', validators=[DataRequired()])
    teamNum = IntegerField('teamNumber', validators=[DataRequired()])
    scoutID = StringField('scoutID', validators=[DataRequired()])

    # Autonomous (15 seconds)
    autoMobility = BooleanField('autoMobility', default=False)
    autoAmp = IntegerField('autoAmp', validators=[DataRequired()], default=0)
    autoSpeaker = IntegerField('autoSpeaker', validators=[DataRequired()], default=0)

    # Teleoperated (135 seconds)
    teleopAmp = IntegerField('teleopAmp', validators=[DataRequired()], default=0)
    teleopSpeaker = IntegerField('teleopSpeaker', validators=[DataRequired()], default=0)
    teleopAmplified = IntegerField('teleopAmplified', validators=[DataRequired()], default=0)

    # Endgame
    trap = IntegerField('trap', validators=[DataRequired()], default=0)
    climb = SelectField('climb', validators=[DataRequired()], choices=[
        ('none', 'None'),
        ('park', 'Park'),
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
    ])

    spotlight = BooleanField('spotlight', default=False)

    droppedPieces = IntegerField('Dropped Pieces / Missed Shots', validators=[DataRequired()], default=0)

    passedNotes = IntegerField('Passed notes', validators=[DataRequired()], default=0)
    
    # Other info
    intake = RadioField('intake', validators=[DataRequired()], choices=[
        ('none', 'Intake failed/was not used'),
        ('human', 'Human Player Only'),
        ('ground', 'Ground Only'),
        ('both', 'Both'),
    ])

    # defense = RadioField('defense', validators=[DataRequired()], choices=[
    #     #('null', 'Unsure'),
    #     ('none', 'Did not play defense'),
    #     ('poor', 'Poor defense'),
    #     ('average', 'Average defense'),
    #     ('excellent', 'Excellent defense')
    # ])
    # driving = RadioField('driving', validators=[DataRequired()], choices=[
    #     #('null', 'Unsure'),
    #     ('none', 'Immobile'),
    #     ('poor', 'Clunky/Awkward'),
    #     ('average', 'Average'),
    #     ('excellent', 'Smooth/Skilled')
    # ])
    fouls = RadioField('fouls (list in notes)', validators=[DataRequired()], choices=[
        ('none', 'No fouls'),
        ('some', '1-2 fouls'),
        ('many', '3+ fouls')
    ])

    freeze = RadioField('Did the robot freeze/disconnect at any time?', validators=[DataRequired()], choices=[
        (False, 'No'),
        (True, 'Yes')
    ])

    # info = TextAreaField('info', validators=[DataRequired(), Length(min=10)])

class SubjectiveRobotData(FlaskForm):
    role = RadioField('role', validators=[DataRequired()], choices=[
        ('offense', 'Offense'),
        ('defense', 'Defense'),
        ('passing', 'Passing')
    ])
    defense = RadioField('defense', validators=[DataRequired()], choices=[
        ('none', 'Did not play defense'),
        ('poor', 'Poor defense'),
        ('average', 'Average defense'),
        ('excellent', 'Excellent defense')
    ])
    driving = RadioField('driving', validators=[DataRequired()], choices=[
        ('none', 'Immobile'),
        ('poor', 'Clunky/Awkward'),
        ('average', 'Average'),
        ('excellent', 'Smooth/Skilled')
    ])
    
    info = TextAreaField('info', validators=[DataRequired(), Length(min=10)])

class CrescendoSuperScoutForm(FlaskForm):
    # Basic match and team information
    matchNum = IntegerField('matchNumber', validators=[DataRequired()])
    teamNum = IntegerField('teamNumber', validators=[DataRequired()])
    scoutID = StringField('scoutID', validators=[DataRequired()])

    robot1 = FormField(SubjectiveRobotData)
    robot2 = FormField(SubjectiveRobotData)
    robot3 = FormField(SubjectiveRobotData)

    redAmps = IntegerField('redAmps', validators=[DataRequired()], default=0)
    blueAmps = IntegerField('blueAmps', validators=[DataRequired()], default=0)

class ReefscapeForm(FlaskForm):
    name = "Reefscape 2025"

    matchNum = IntegerField('matchNumber', validators=[DataRequired()])
    teamNum = IntegerField('teamNumber', validators=[DataRequired()])
    scoutID = StringField('scoutID', validators=[DataRequired()])

    # Autonomous fields
    autoMobility = BooleanField('autoMobility', default=False)
    autoL1 = IntegerField('autoL1', validators=[DataRequired()], default=0)
    autoL2 = IntegerField('autoL2', validators=[DataRequired()], default=0)
    autoL3 = IntegerField('autoL3', validators=[DataRequired()], default=0)
    autoL4 = IntegerField('autoL4', validators=[DataRequired()], default=0)

    autoAlgaeRemoved = IntegerField('autoAlgaeRemoved', validators=[DataRequired()], default=0)
    autoProcessor = IntegerField('autoProcessor', validators=[DataRequired()], default=0)
    autoNet = IntegerField('autoNet', validators=[DataRequired()], default=0)

    # Teleoperated fields
    teleopL1 = IntegerField('teleopL1', validators=[DataRequired()], default=0)
    teleopL2 = IntegerField('teleopL2', validators=[DataRequired()], default=0)
    teleopL3 = IntegerField('teleopL3', validators=[DataRequired()], default=0)
    teleopL4 = IntegerField('teleopL4', validators=[DataRequired()], default=0)

    teleopAlgaeRemoved = IntegerField('teleopAlgaeRemoved', validators=[DataRequired()], default=0)
    teleopProcessor = IntegerField('teleopProcessor', validators=[DataRequired()], default=0)
    teleopNet = IntegerField('teleopNet', validators=[DataRequired()], default=0)
    
    # Endgame fields
    climb = SelectField('climb', validators=[DataRequired()], choices=[
        ('none', 'None'),
        ('park', 'Park'),
        ('shallow', 'Shallow'),
        ('deep', 'Deep')
    ])

    climbSpeed = SelectField('climbSpeed', validators=[DataRequired()], choices=[
        (0, '0-5s'),
        (1, '5-10s'),
        (2, '10-15s'),
        (3, '15-20s'),
        (4, '20+ seconds')
    ])

    # Other fields
    defense = BooleanField('defense', default=False)
    defenseExperienced = StringField('defenseExperienced')
    droppedPieces = IntegerField('droppedPieces', validators=[DataRequired()], default=0)
    fouls = IntegerField('fouls', validators=[DataRequired()], default=0)
    failure = BooleanField('failure', default=False)

    info = TextAreaField('info', validators=[DataRequired()])

class ReefscapeSuperScoutForm(FlaskForm):
    # Basic match and team information
    matchNum = IntegerField('matchNumber', validators=[DataRequired()])
    scoutID = StringField('scoutID', validators=[DataRequired()])

    # Team numbers for each robot
    robot1Num = IntegerField('robot1Num', validators=[DataRequired()])
    robot2Num = IntegerField('robot2Num', validators=[DataRequired()])
    robot3Num = IntegerField('robot3Num', validators=[DataRequired()])

    # Textarea boxes for each robot
    robot1Info = TextAreaField('robot1Info', validators=[DataRequired(), Length(min=10)])
    robot2Info = TextAreaField('robot2Info', validators=[DataRequired(), Length(min=10)])
    robot3Info = TextAreaField('robot3Info', validators=[DataRequired(), Length(min=10)])


class RebuiltForm(FlaskForm):
    name = "Rebuilt 2026"

    matchNum = IntegerField('matchNumber', validators=[DataRequired()])
    teamNum = IntegerField('teamNumber', validators=[DataRequired()])
    scoutID = StringField('scoutID', validators=[DataRequired()])

    # Autonomous fields
    autoMobility = BooleanField('autoMobility', default=False)
    autoL1 = BooleanField('autoL1', default=False) # Climb checkbox
    

    autoShots = IntegerField('autoShots', validators=[DataRequired()], default=0)

    autoShotAccuracy = IntegerField('autoShotAccuracy', validators=[DataRequired()], default=0) #needs to be a slider

    # Teleoperated fields


    teleopShots = IntegerField('teleopShots', validators=[DataRequired()], default=0)

    teleopShotAccuracy = IntegerField('teleopShotAccuracy', validators=[DataRequired()], default=0) #needs to be a slider
    teleopPassed = BooleanField('teleopPassed', default=False) #did they pass?
    teleopDefense = BooleanField('teleopDefense', default=False)  # did they play defense?
    climbLocation = StringField('climbLocation', default='none')  # CSV list from field map
    # Endgame fields
    climb = SelectField('climb', validators=[DataRequired()], choices=[
        ('none', 'None'),
        ('level1', 'L1'),
        ('level2', 'L2'),
        ('level3', 'L3')
    ])
    
    climbFailed = BooleanField('climbFailed', default=False)
    climbTime = StringField('climbTime', default='0.0s')

    # Other fields
    defenseExperienced = StringField('defenseExperienced')
    passes = IntegerField('passes', validators=[DataRequired()], default=0)
    successfulStops = IntegerField('successfulStops', validators=[DataRequired()], default=0)
    fouls = IntegerField('fouls', validators=[DataRequired()], default=0)
    failure = BooleanField('failure', default=False)
    failureDetails = StringField('failureDetails', default='')

    info = TextAreaField('info', default='')
