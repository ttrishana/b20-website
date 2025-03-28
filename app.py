from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)    

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///assignment3.db'
db = SQLAlchemy(app)

@app.route('/')
def test():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/syllabus.html')
def syllabus():
    return render_template('syllabus.html')

@app.route('/calendar.html')
def calendar():
    return render_template('calendar.html')

@app.route('/assignments.html')
def assignments():
    return render_template('assignments.html')

@app.route('/labs.html')
def labs():
    return render_template('labs.html')

@app.route('/lecture_notes.html')
def lecture_notes():
    return render_template('lecture_notes.html')

@app.route('/feedback.html')
def feedback():
    return render_template('feedback.html')

@app.route('/team.html')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(debug=True)
