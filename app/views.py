from flask import Flask, render_template, jsonify, flash
from app import app, db
from .forms import RegisterForm, LoginForm, EventForm
from .models import User
import datetime

@app.route('/')
def hello_world():
    # example without a template
    # return 'Hello, World!'
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile/<username>')
def profile(username=None):
    return render_template('profile.html', username=username)

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        full_name = form.full_name.data # or request.form['full_name']
        email = form.email.data # or request.form['email']
        message = form.message.data # or request.form['message']

        #app.logger.debug(full_name)
        dt=datetime.datetime.now()
        acc=User(full_name=full_name,email=email,password=message,date=dt)
        if acc is not None:
            db.session.add(acc)
            db.session.commit()

    for error in form.email.errors:
        app.logger.error(error)
        flash(error)

    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        full_name = form.full_name.data # or request.form['full_name']
        email = form.email.data # or request.form['email']
        message = form.message.data # or request.form['message']

        #app.logger.debug(full_name)
        dt=datetime.datetime.now()
        acc=User(full_name=full_name,email=email,password=message,date=dt)
        if acc is not None:
            db.session.add(acc)
            db.session.commit()

    for error in form.email.errors:
        app.logger.error(error)
        flash(error)

    return render_template('login.html', form=form)

@app.route('/addevent', methods=["GET", "POST"])
def addevent():
    form = EventForm()

    if form.validate_on_submit():
        full_name = form.full_name.data # or request.form['full_name']
        email = form.email.data # or request.form['email']
        message = form.message.data # or request.form['message']

        #app.logger.debug(full_name)
        dt=datetime.datetime.now()
        acc=User(full_name=full_name,email=email,password=message,date=dt)
        if acc is not None:
            db.session.add(acc)
            db.session.commit()

    for error in form.errors:
        app.logger.error(error)
        flash(error)

    return render_template('addevent.html', form=form)

@app.route('/api/tasks')
def tasks():
    tasks = [{'id': 1, 'title': 'Teach Class'}, {'id': 2, 'title': 'Go have lunch'}]
    return jsonify(tasks=tasks)