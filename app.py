from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

app = Flask(__name__)    

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///assignment3.db'
app.config['SECRET_KEY'] = 'key'
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

class Users(db.Model):
    __tablename__ = 'Users'
    u_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    accType = db.Column(Enum('Student', 'Teacher', name='accTypeEnum'), nullable = False)
    
    grades = db.relationship('Grades', backref='student', lazy=True)
    remarks = db.relationship('Remark', backref='student', lazy=True)
    feedbacks = db.relationship('Feedback', backref='instructor', lazy=True)
    

class Grades(db.Model):
    __tablename__ = 'Grades'
    u_id = db.Column(db.Integer, db.ForeignKey("Users.u_id"), primary_key=True)
    a_name = db.Column(db.Text, primary_key=True)
    percent = db.Column(db.Float, nullable=False)

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    f_id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey("Users.u_id"), nullable=False)
    teaching_feedback = db.Column(db.Text, nullable=False)
    teaching_recommendations = db.Column(db.Text, nullable=False)
    lab_feedback = db.Column(db.Text, nullable=False)
    lab_recommendations = db.Column(db.Text, nullable=False)

class Remark(db.Model):
    __tablename__ = 'Remark'
    r_id = db.Column(db.Integer, primary_key=True)
    u_id = db.Column(db.Integer, db.ForeignKey("Users.u_id"), nullable=False)
    status = db.Column(db.Text, nullable=False)
    a_name = db.Column(db.Text, nullable=False)
    reason = db.Column(db.Text, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Users.query.first():
            person1 = Users(username='student1', email='student@test.com', password='pass', accType='Student')
            person2 = Users(username='teacher1', email='teacher@test.com', password='passer', accType='Teacher')
            db.session.add_all([person1, person2])
            db.session.commit()

        if not Grades.query.first():
            grade1 = Grades(u_id=1, a_name="test1", percent=94.0)  # Ensure `percent` is a float
            db.session.add(grade1)
            db.session.commit()

        if not Feedback.query.first():
            feedback1 = Feedback(u_id=2, teaching_feedback='good', teaching_recommendations='better', lab_feedback='easy', lab_recommendations='worth more') 
            db.session.add(feedback1)
            db.session.commit()    

        if not Remark.query.first():
            remark1 = Remark(u_id=1, status='rejected', a_name='final', reason='sick') 
            db.session.add(remark1)
            db.session.commit()    
        db.session.close()
    app.run(debug=True)
