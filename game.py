# game.py: define the form for the scout page

# Below is an example from Charged Up 2023.

from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, TextAreaField, BooleanField, SelectField, StringField
from wtforms.validators import *

class ChargedUpScoutForm(FlaskForm):
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

class UltimateAscentScoutForm(FlaskForm):
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
    defense = RadioField('defense', validators=[DataRequired()], choices=[
        #('null', 'Unsure'),
        ('none', 'Did not play defense'),
        ('poor', 'Poor defense'),
        ('average', 'Average defense'),
        ('excellent', 'Excellent defense')
    ])
    driving = RadioField('driving', validators=[DataRequired()], choices=[
        #('null', 'Unsure'),
        ('none', 'Immobile'),
        ('poor', 'Clunky/Awkward'),
        ('average', 'Average'),
        ('excellent', 'Smooth/Skilled')
    ])
    fouls = RadioField('fouls (list in notes)', validators=[DataRequired()], choices=[
        #('null', 'Unsure'),
        ('none', 'No fouls'),
        ('some', '1-2 fouls'),
        ('many', '3+ fouls')
    ])

    info = TextAreaField('info', validators=[DataRequired(), Length(min=10)])