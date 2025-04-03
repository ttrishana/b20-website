from flask import Flask, render_template, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask import jsonify 
from flask_migrate import Migrate


app = Flask(__name__)    

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///assignment3.db'
app.config['SECRET_KEY'] = 'key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 10)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

@app.route('/')
def test():
    return redirect('register.html')

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else:
        username = request.form["Username"]
        email = request.form["Email"]
        password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
        accType = request.form["AccountType"]
        registration = (username, email, password, accType)
        print(registration)
        addUser(registration)
        return redirect("login.html")
    
@app.route('/login.html', methods=['GET', 'POST'])
def login():
        if request.method=='GET':
        #    if 'name' in session:
        #            return redirect('index.html')
            return render_template('login.html')
        else:
            username = request.form["Username"]
            password = request.form["Password"]
            user = Users.query.filter_by(username = username).first()
            if not user or not bcrypt.check_password_hash(user.password, password):
                flash('Please check your login details and try again.', 'Error')
                return render_template('login.html')
            
            session['user_id'] = user.u_id
            session.permanent = True
            return redirect('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'Success')
    return redirect('login.html')

def addUser(details):
    user = Users(username=details[0], email=details[1], password=details[2], accType=details[3])
    db.session.add(user)
    db.session.commit()

@app.route('/index.html')
def index():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect(('login.html'))

    user = Users.query.get(session['user_id'])
    return render_template('index.html', user=user)

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
'''
@app.route('/feedback.html')
def feedback():
    return render_template('feedback.html')
'''
@app.route('/team.html')
def team():
    return render_template('team.html')

@app.route('/grades')
def view_grades():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect('login.html')

    user = Users.query.get(session['user_id'])

    if user.accType != 'Student':
        flash('Only students can view grades.', 'error')
        return redirect('index.html')

    grades = db.session.query(Grades, Remark.status).outerjoin(Remark, 
              (Grades.u_id == Remark.u_id) & (Grades.a_name == Remark.a_name)
          ).filter(Grades.u_id == user.u_id).all()

    return render_template('grades.html', user=user, grades=grades)

@app.route('/submit_remark', methods=['POST'])
def submit_remark():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 403

    data = request.get_json()
    a_name = data.get('a_name')
    reason = data.get('reason')

    user_id = session['user_id']

    # Check if a remark already exists for this assignment
    remark_exists = Remark.query.filter_by(u_id=user_id, a_name=a_name).first()
    if remark_exists:
        return jsonify({'success': False, 'message': 'Remark already requested'}), 400

    # Insert new remark request
    new_remark = Remark(u_id=user_id, a_name=a_name, status='Pending', reason=reason)
    db.session.add(new_remark)
    db.session.commit()

    return jsonify({"success": "Remark request submitted successfully!"})

@app.route('/instructor_grades', methods=['GET', 'POST'])
def instructor_grades():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect('login.html')

    user = Users.query.get(session['user_id'])

    if user.accType != 'Instructor':
        flash('Only instructors can access this page.', 'error')
        return redirect('index.html')

    students = Users.query.filter_by(accType='Student').all()
    grades = Grades.query.all()

    return render_template('grades_instructor.html', user=user, students=students, grades=grades)

@app.route('/update_grade', methods=['POST'])
def update_grade():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 403

    user = Users.query.get(session['user_id'])
    if user.accType != 'Instructor':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = request.get_json()
    student_id = data.get('student_id')
    assignment = data.get('assignment')
    new_grade = data.get('new_grade')

    grade_entry = Grades.query.filter_by(u_id=student_id, a_name=assignment).first()
    
    if grade_entry:
        grade_entry.percent = new_grade  # Update existing grade
    else:
        new_grade_entry = Grades(u_id=student_id, a_name=assignment, percent=new_grade)
        db.session.add(new_grade_entry)  # Insert new grade

    db.session.commit()

    return jsonify({'success': True, 'message': 'Marks updated successfully!'})

@app.route('/remark_requests', methods=['GET'])
def remark_requests():
    if 'user_id' not in session:
        flash('You must be logged in to view this page.', 'error')
        return redirect('login.html')

    user = Users.query.get(session['user_id'])
    if user.accType != 'Instructor':
        flash('Only instructors can access this page.', 'error')
        return redirect('index.html')

    remarks = Remark.query.all()

    return render_template('remark_requests.html', user=user, remarks=remarks)

@app.route('/update_remark_status', methods=['POST'])
def update_remark_status():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 403

    user = Users.query.get(session['user_id'])
    if user.accType != 'Instructor':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = request.get_json()
    remark_id = data.get('remark_id')
    new_status = data.get('new_status')

    remark = Remark.query.get(remark_id)
    if remark:
        remark.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'message': 'Remark status updated!'})
    
    return jsonify({'success': False, 'message': 'Remark not found'})

@app.route('/feedback.html', methods=['GET'])
def feedback_form():
    if 'user_id' not in session:
        flash('You must be logged in to access this page.', 'error')
        return redirect('login.html')

    user = Users.query.get(session['user_id'])
    if user.accType != 'Student':
        flash('Only students can submit feedback.', 'error')
        return redirect('index.html')

    instructors = Users.query.filter_by(accType='Instructor').all()
    return render_template('feedback.html', instructors=instructors, success=False)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return jsonify(success=False, message='You must be logged in to submit feedback.')

    user = Users.query.get(session['user_id'])
    if user.accType != 'Student':
        return jsonify(success=False, message='Only students can submit feedback.')

    instructor_id = request.form['instructor']
    teaching_feedback = request.form['teaching_feedback']
    teaching_recommendations = request.form['teaching_recommendations']
    lab_feedback = request.form['lab_feedback']
    lab_recommendations = request.form['lab_recommendations']

    feedback = Feedback(
        u_id=instructor_id,
        teaching_feedback=teaching_feedback,
        teaching_recommendations=teaching_recommendations,
        lab_feedback=lab_feedback,
        lab_recommendations=lab_recommendations
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify(success=True, message='Feedback submitted successfully.')

@app.route('/view_feedback', methods=['GET'])
def view_feedback():
    if 'user_id' not in session:
        flash('You must be logged in to view feedback.', 'error')
        return redirect('login.html')

    user = Users.query.get(session['user_id'])

    if user.accType != 'Instructor':
        flash('Only instructors can view feedback.', 'error')
        return redirect('index.html')

    feedbacks = Feedback.query.filter_by(u_id=user.u_id).all()

    return render_template('instructor_feedback.html', user=user, feedbacks=feedbacks)

@app.route('/mark_feedback_reviewed', methods=['POST'])
def mark_feedback_reviewed():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 403

    user = Users.query.get(session['user_id'])
    if user.accType != 'Instructor':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    data = request.get_json()
    feedback_id = data.get('feedback_id')

    feedback = Feedback.query.get(feedback_id)

    if not feedback or feedback.u_id != user.u_id:
        return jsonify({'success': False, 'message': 'Feedback not found or unauthorized'}), 403

    feedback.reviewed = True
    db.session.commit()

    return jsonify({'success': True, 'message': 'Feedback marked as reviewed'})


class Users(db.Model):
    __tablename__ = 'Users'
    u_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    accType = db.Column(Enum('Student', 'Instructor', name='accTypeEnum'), nullable = False)
    
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
    reviewed = db.Column(db.Boolean, default=False)

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
        db.session.close()
    app.run(debug=True)
