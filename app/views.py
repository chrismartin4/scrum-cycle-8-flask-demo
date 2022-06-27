from flask import Flask, render_template, jsonify, flash
from app import app, db
from .forms import ContactForm
from .models import User
import datetime

@app.route('/')
def hello_world():
    # example without a template
    return 'Hello, World!'

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile/<username>')
def profile(username=None):
    return render_template('profile.html', username=username)

@app.route('/contact', methods=["GET", "POST"])
def contact():
    form = ContactForm()

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

    return render_template('contact_form.html', form=form)

@app.route('/api/tasks')
def tasks():
    tasks = [{'id': 1, 'title': 'Teach Class'}, {'id': 2, 'title': 'Go have lunch'}]
    return jsonify(tasks=tasks)