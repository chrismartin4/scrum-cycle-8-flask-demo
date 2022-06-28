from turtle import title
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash,g,send_from_directory,session,make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app import app, db,login_manager
from .forms import RegisterForm, LoginForm, EventForm
from .models import User,Events
import datetime
import os



@app.route('/hello')
def hello_world():
    # example without a template
    # return 'Hello, World!'
    return render_template('home.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
            name=form.full_name.data
            email=form.email.data
            password=form.password.data
            pic=form.profile_photo.data
            picfilename=secure_filename(pic.filename)
            role=form.role.data
            dt=datetime.datetime.now()
            user = User(full_name=name, email=email,password=password,profile_photo=picfilename,role=role,date=dt)
            if user is not None :
                db.session.add(user)
                db.session.commit()
                pic.save(os.path.join(app.config['UPLOAD_FOLDER'],picfilename))
                return redirect(url_for("login"))


    for error in form.errors:
        app.logger.error(error)
        flash(error)
    return render_template("register.html", form=form)

@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        if form.email.data:
            email=form.email.data
            password=form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and check_password_hash(user.password,password):
                login_user(user)
                session['uid']=current_user.id
                if user.role =="Admin":
                    session['is_admin'] = True
                elif user.role =="Regular":
                    session['is_regular'] = True
                return redirect(url_for("about"))
            else:
                flash('Email or Password is incorrect.', 'danger')
    for error in form.errors:
        app.logger.error(error)
        flash(error)
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    # Logout the user and end the session
    logout_user()
    flash('You have been logged out.', 'danger')
    return redirect(url_for('login'))
    
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile/<username>')
def profile(username=None):
    return render_template('profile.html', username=username)


@app.route('/addevent', methods=["GET", "POST"])
def addevent():
    form = EventForm()
    if request.method == "POST" and form.validate_on_submit():
        title=form.title.data
        start_date=form.start_date.data
        end_date=form.end_date.data
        desc=form.desc.data
        venue=form.venue.data
        flyer=form.flyer.data
        flyerfilename=secure_filename(flyer.filename)
        website_url=form.website_url.data
        #app.logger.debug(full_name)
        dt=datetime.datetime.now()
        event=Events(title=title, start_date=start_date, end_date=end_date, desc=desc, venue=venue, flyer=flyerfilename, website_url=website_url, status="Pending", uid=session['uid'], created_at=dt)
        if event is not None:
            db.session.add(event)
            db.session.commit()
            flyer.save(os.path.join(app.config['UPLOAD_FOLDER'],flyerfilename))
    for error in form.errors:
        app.logger.error(error)
        flash(error)

    return render_template('addevent.html', form=form)

@app.route("/api/events", methods=["GET"])
# @requires_auth
def allEvents():
    try:
        events = []
        allevents = db.session.query(Events).order_by(Events.id.desc()).all()

        for event in allevents:                                      

            record = {"photo": os.path.join(app.config['GET_FILE'], event.photo), "title": event.title, "Start Date": event.start_date,"End Date": event.end_date, "Description":event.desc, "Venue":event.venue }
            events.append(record)
        return jsonify(events=events), 201
    except Exception as e:
        print(e)

        error = "Internal server error"
        return jsonify(error=error), 401

@app.route('/api/events/<event_title>',methods=["GET"])
@login_required
# @requires_auth
def event_details(event_title):
    if request.method=="GET":
        try:
            details= Events.query.filter_by(title=event_title).first()
            if details is not None:
                return make_response(jsonify(details=details),201)
            else:
                return make_response(jsonify(response="Event not found"))
        except Exception as e:
            print(e)
            error="Internal server error"
            return make_response(jsonify(error=error)),401

@app.route('/api/events/<start_date>',methods=["GET"])
@login_required
# @requires_auth
def event_details(start_date):
    if request.method=="GET":
        try:
            details= Events.query.filter_by(startdate=start_date).first()
            if details is not None:
                return make_response(jsonify(details=details),201)
            else:
                return make_response(jsonify(response="Event not found"))
        except Exception as e:
            print(e)
            error="Internal server error"
            return make_response(jsonify(error=error)),401

@app.route('/api/events/<end_date>',methods=["GET"])
@login_required
# @requires_auth
def event_details(end_date):
    if request.method=="GET":
        try:
            details= Events.query.filter_by(enddate=end_date).first()
            if details is not None:
                return make_response(jsonify(details=details),201)
            else:
                return make_response(jsonify(response="Event not found"))
        except Exception as e:
            print(e)
            error="Internal server error"
            return make_response(jsonify(error=error)),401

@app.route('/api/tasks')
def tasks():
    tasks = [{'id': 1, 'title': 'Teach Class'}, {'id': 2, 'title': 'Go have lunch'}]
    return jsonify(tasks=tasks)