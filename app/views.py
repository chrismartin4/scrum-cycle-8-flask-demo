from flask import Flask, render_template, jsonify, request, redirect, url_for, flash,g,send_from_directory,session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app import app, db,login_manager
from .forms import ContactForm
from .models import User
import datetime

@app.route('/hello')
def hello_world():
    # example without a template
    return 'Hello, World!'

@app.route("/register", methods=["GET", "POST"])
def register():
    form = ContactForm()
    if request.method == "POST" and form.validate_on_submit():
            name=form.name.data
            email=form.email.data
            password=form.password.data
            pic=form.profile_photo.data
            role=form.role.data
            date=datetime.datetime.now()
            user = User(full_name=name, email=email,password=password,profile_photo=pic,role=role,date=date)
            if user is not None :
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("login"))
            else:
                flash('User already exists ', 'danger')
    return render_template("register.html", form=form)

@app.route("/", methods=["GET", "POST"])
def login():
    form = ContactForm()
    if request.method == "POST" and form.validate_on_submit():
        if form.email.data:
            email=form.email.data
            password=form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and check_password_hash(user.password,password):
                login_user(user)
                if user.role =="Admin":
                    session['is_admin'] = True
                else:
                    session['is_regular'] = True
                return redirect(url_for("about"))
            else:
                flash('Email or Password is incorrect.', 'danger')
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    # Logout the user and end the session
    logout_user()
    flash('You have been logged out.', 'danger')
    return redirect(url_for('login'))

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