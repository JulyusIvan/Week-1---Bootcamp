from flask import Flask, render_template, url_for, request, flash, redirect, session
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date

app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = '1234567890101'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_filename: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    birthday: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()

with app.app_context():
    db.create_all()

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_age(birthday_str):
    birth_date = datetime.strptime(birthday_str, "%Y-%m-%d").date()
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        image = request.files['image']

        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            flash("Invalid image file!")
            return redirect(url_for('register'))

        name = request.form['name']
        birthday = request.form['birthday']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

        new_user = User(
            name=name,
            birthday=birthday,
            address=address,
            username=username,
            password=password,
            image_filename=image_filename
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for('login'))

    return render_template('User/registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(User).filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials!")
    return render_template('User/login.html')

@app.route('/home')
def home():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = db.session.get(User, user_id) 
    if not user:
        flash("User not found!")
        return redirect(url_for('login'))

    age = calculate_age(user.birthday)
    return render_template('User/homepage.html', user=user, age=age)


if __name__ == '__main__':
    app.run(debug=True)
