from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin, current_user, login_user, logout_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import email_validator
import os
from datetime import datetime

app = Flask(__name__)
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(32)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    lists = relationship('Lists', back_populates="user")


class Lists(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="lists")
    things = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=True)

# db.create_all()

class Register(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(email_validator)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')


class Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(email_validator)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


to_do_lists = {}


@app.route('/', methods=['post', 'get'])
def home():
    id = 0
    user = User.query.get(id)
    if current_user.is_authenticated:
        user = current_user
        lists = user.lists
        if request.method == "POST":
            data = Lists(user_id=user.id,
                         things=request.form.get('userinput'),
                         date=datetime.strptime(request.form.get('duedate'), '%Y-%m-%d'), )
            print(user.lists)
            db.session.add(data)
            db.session.commit()
            lists = user.lists
        return render_template('index.html', user=user, login=True, to_do_lists=lists)
    if request.method == "POST":
        user_input = request.form.get('userinput')
        due = request.form.get('duedate')
        to_do_lists.update({user_input: due})
        print(to_do_lists)
        return render_template('index.html', user_input=user_input, to_do_lists=to_do_lists)
    return render_template('index.html', user=user)


@app.route('/register', methods=['post', 'get'])
def register():
    form = Register()
    if form.validate_on_submit():
        data = User(username=form.name.data,
                    email=form.email.data,
                    password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8))
        try:
            db.session.add(data)
            db.session.commit()
        except IntegrityError:
            flash("Register Failed: This email address has already registered")
            return redirect(url_for('register'))
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['post', 'get'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                print(current_user)
                print(current_user.is_authenticated)
                return redirect(url_for('home'))
            else:
                flash('Password does not match')
                redirect(url_for('login'))
        else:
            flash('Email does not exist in the database')
            redirect(url_for('login'))
    return render_template("login.html", form=form, login=current_user.is_authenticated, user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='localhost', debug=True)
