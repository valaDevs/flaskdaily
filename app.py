import os
from flask import Flask,render_template , request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
import urllib.request

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
app.secret_key = 'kaboos123aha'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)


# ...

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    bio = db.Column(db.Text)

    def __repr__(self):
        return f'<Student {self.firstname}>'


class Car(db.Model):
    id = db.Column(db.Integer ,primary_key = True)
    carname = db.Column(db.String(100),nullable=False)
    carcolor = db.Column(db.String(100),nullable=False)
    carmadeat = db.Column(db.String(100),nullable=False)
    cartype = db.Column(db.String(100),nullable=False)

    def __repr__(self):
        return f'<Car {self.carname}>'


class Upload(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)

@app.route('/')
def index():
    students = Student.query.all()

    return render_template('index.html',students=students)

# ...

@app.route('/<int:student_id>/')
def student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('student.html', student=student)

# ...


@app.route('/create/', methods=('GET', 'POST'))
def create():

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        age = int(request.form['age'])
        bio = request.form['bio']
        student = Student(firstname=firstname,
                          lastname=lastname,
                          email=email,
                          age=age,
                          bio=bio)
        db.session.add(student)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')

# ...


@app.route('/<int:student_id>/edit/', methods=('GET', 'POST'))
def edit(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        age = int(request.form['age'])
        bio = request.form['bio']

        student.firstname = firstname
        student.lastname = lastname
        student.email = email
        student.age = age
        student.bio = bio

        db.session.add(student)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', student=student)

# ...

@app.post('/<int:student_id>/delete/')
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))


#============= Cars ==================

@app.route('/cars')
def cars():
    cars = Car.query.all()
    return render_template('cars.html',cars=cars)

@app.route('/car/<int:id>')
def car(id):
    car = Car.query.filter_by(id=id).first_or_404()
   
    return render_template('car.html',car=car   )

@app.route('/spy')
def spy():
    return render_template('spy.html')

@app.route('/spy/play')
def spyPlay():
    return render_template('spyPlay.html')

@app.route('/form',methods=['GET','POST'])
def form():
    return render_template('form.html')

@app.route('/hello',methods=['GET','POST','PATCH'])
def hello():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        if fname == 'admin':
            return redirect(url_for('index'))

    return render_template('hello.html',name=fname,lName=lname)


def allowed_file(filename):
    	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload')
def upload_form():
	return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
	if 'files[]' not in request.files:
		flash('No file part')
		return redirect(request.url)
	files = request.files.getlist('files[]')
	file_names = []
	for file in files:
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file_names.append(filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))



		#else:
		#	flash('Allowed image types are -> png, jpg, jpeg, gif')
		#	return redirect(request.url)

	return render_template('upload.html', filenames=file_names)


@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/avatar',methods=['GET','POST'])
def avatar():
    if request.method=='POST':
        file = request.files['file']

        upload = Upload(filename=file.filename,data=file.read())
        db.session.add(upload)
        db.session.commit()


        return f'Uploaded : {file.filename}'

    return render_template('avatar.html')

@app.route('/blob',methods=['GET','POST'])
def blob():

    upload = Upload.query.all()

    return render_template('blob.html',upload=upload)




if __name__ == "__main__":
    app.run()


