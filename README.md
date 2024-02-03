```txt
                                    dP                                                   dP   
                                    88                                                   88   
88d888b. dP    dP 88d888b. 88d888b. 88 .d8888b.    .d8888b. .d8888b. .d8888b. dP    dP d8888P 
88'  `88 88    88 88'  `88 88'  `88 88 88ooood8    Y8ooooo. 88'  `"" 88'  `88 88    88   88   
88.  .88 88.  .88 88       88.  .88 88 88.  ...          88 88.  ... 88.  .88 88.  .88   88   
88Y888P' `88888P' dP       88Y888P' dP `88888P'    `88888P' `88888P' `88888P' `88888P'   dP   
88                         88                                                                 
dP                         dP

```

## Description
PurpleScout is an app that simplifies the scouting process for FRC teams. 
Data pipeline (from scouting to analysis) is as follows:

1. A Windows laptop runs a Python/Flask app that hosts a web form
2. Scouters collect data and input into the app
3. After each match, an HTML form is submitted that contains the data
4. Laptop recieves POST request
5. Data from scouts is combined and organized into a CSV file
6. CSV file is periodically synced to Google Drive
7. Google Sheets runs analytics on the data and creates suggestions for the team
8?? Web dashboard accessible to admins to see data at-a-glance and make decisions

## Game definition
PurpleScout can be configured for any game. 

### 1. Define fields in `game.py`
This app uses [Flask-WTF](https://flask-wtf.readthedocs.io/en/1.2.x/quickstart/#creating-forms) for form gerenation. In `game.py`, make a subclass of `FlaskForm` with the name of your game.

Add instance variables in each class to represent fields, or pieces of data you want to collect. Example:

```python
class ChargedUpScoutForm(FlaskForm):
    matchNum = IntegerField('Match Number', validators=[DataRequired()])
    teamNum = IntegerField('Team Number', validators=[DataRequired()])

    cubesScored = IntegerField('Cubes Scored', validators=[DataRequired()])
    conesScored = IntegerField('Cones Scored', validators=[DataRequired()])

    defenseQuality = RadioField('Defense Quality', choices=[
      (0,'No defense'),
      (1, 'Average defense'),
      (2,'Good defense')
    ], validators=[DataRequired()])

    comment = TextAreaField('Comment', validators=[DataRequired()])
```

Most fields you need will be of type `IntegerField`, `RadioField`, or `TextAreaField`. Refer to WTForms and Flask-WTF documentation for more information.

### 2. Create template in `templates/forms`

Create a new HTML file in `templates/forms` with the same filename as your class. Example:

```html
<!-- ChargedUpScoutForm.html -->
{% extends "scout.html" %}
{% block form %}

{{ form.matchNum }}
{{ form.teamNum }}
<table class="my custom html">
  {{ form.cubesScored }}
  {{ form.conesScored }}
</table>
{{ form.defenseQuality }}
{{ form.comment }}

{% endblock %}
```
Each `{{ form.field }}` will be replaced by an `<input>` element of the corresponding type. You can add classes like this: `form.field(class_="custom classes")` and style them in `scout.css`.

You don't need to include a `<form>` wrapper or a submit button. If you want minus and plus buttons next to your integer inputs, add `<button class='subtractButton'>-</button>` and `<button class='addButton'>+</button>` before and after the `{{ form.field }}` line. The app will automatically add event listeners.

### 3. Configure main.py

Change this line to the name of your class:
```
app.config["GAME"] = ChargedUpScoutForm
```
