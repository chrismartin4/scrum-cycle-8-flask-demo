from flask import Flask, render_template, jsonify, make_response, request, redirect, url_for, flash,g,send_from_directory,session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app import app, db,login_manager
from .forms import RegisterForm, LoginForm, EventForm
from .models import User,Events
import datetime
import os
import jwt
from functools import wraps

# Create a JWT @requires_auth decorator
# This decorator can be used to denote that a specific route should check
# for a valid JWT token before displaying the contents of that route.
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None) # or request.cookies.get('token', None)
        if not auth:
            return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401
        parts = auth.split()
        if parts[0].lower() != 'bearer':
            return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
        elif len(parts) == 1:
            return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
        elif len(parts) > 2:
            return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401
        token = parts[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 'token_expired', 'description': 'token is expired'}), 401
        except jwt.DecodeError:
            return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401
        g.current_user = user = payload
        return f(*args, **kwargs)

    return decorated
@app.route('/hello')
@requires_auth
def hello_world():
    # example without a template
    # return 'Hello, World!'
    return jsonify(msg="jwt test")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    #if request.method == "POST" and form.validate_on_submit():
    if request.method == "POST":
            name=form.full_name.data
            email=form.email.data
            password=form.password.data
            pic=form.profile_photo.data
            photo=secure_filename(pic.filename)
            role=form.role.data
            dt=datetime.datetime.now()
            usercheck= User.query.filter_by(email=email).first()
            if usercheck is None :
                user = User(full_name=name, email=email,password=password,profile_photo=photo,role=role,date=dt)
                db.session.add(user)
                db.session.commit()
                pic.save(os.path.join(app.config['UPLOAD_FOLDER'],photo))
                #return redirect(url_for("login"))
                return make_response(jsonify(message='Successfully registered. Please Log in.'), 202)
            else:
        # returns 202 if user already exists
                return make_response(jsonify(message='User already exists. Please Log in.'), 202)
    err=[]
    for error in form.errors:
        app.logger.error(error)
        flash(error)
        err.append(error)
    return jsonify(msg="register errors",err=err)
    #return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" :
        if form.email.data:
            email=form.email.data
            password=form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and check_password_hash(user.password,password):
                payload = { 'email': user.email,'userid': user.id}
                token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
                jsonmsg=jsonify(message=" Login Successful and Token was Generated",data={"token":token})
                session['uid']=user.id
                if user.role =="Admin":
                    session['is_admin'] = True
                elif user.role =="Regular":
                    session['is_admin'] = False
                return jsonmsg
                #return redirect(url_for("about"))
            else:
                flash('Email or Password is incorrect.', 'danger')
    for error in form.errors:
        app.logger.error(error)
        flash(error)
    return render_template("login.html", form=form)

@app.route("/logout")
@requires_auth
def logout():
    # Logout the user and end the session
    session.pop('uid', None)
    session.pop('is_admin', None)
    session.pop('is_regular', None)
    flash('You were logged out', 'success')
    return redirect(url_for('login'))

@app.route('/about')
@requires_auth
def about():
    return render_template('about.html')
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/api/events', methods=["GET", "POST"])
@requires_auth
def addevent():
    form = EventForm()
    if request.method == "POST" :
        title=form.title.data
        start_date=form.start_date.data
        end_date=form.end_date.data
        desc=form.desc.data
        venue=form.venue.data
        flyer=form.flyer.data
        website_url=form.website_url.data
        dt=datetime.datetime.now()
        event=Events(title=title, start_date=start_date, end_date=end_date, desc=desc, venue=venue, flyer=flyer, website_url=website_url, status="Pending", uid=session['uid'], created_at=dt)
        if event is not None:
            db.session.add(event)
            db.session.commit()
            return make_response('Event Successfully registered.', 201)
        else:
            return make_response('Event already exists. Please Log in.', 202)

    if request.method=="GET":
        allev=[]
        if session['is_admin']== True:
            evlist=Events.query.order_by(Events.id).all()
            for e in evlist:
                ev={}
                ev['title']=e.title
                ev["start_date"]=e.start_date
                ev["end_date"]=e.end_date        
                ev["desc"]=e.desc
                ev["venue"]=e.venue
                ev["flyer"]=e.flyer
                ev["website_url"]=e.website_url
                ev["status"]=e.status
                ev["uid"]=e.uid
                ev["created_at"]=e.created_at
                allev.append(ev)

        elif session['is_admin']== False:
            evlist=Events.query.filter_by(status="Published").all()
            for e in evlist:
                ev={}
                ev['title']=e.title
                ev["start_date"]=e.start_date
                ev["end_date"]=e.end_date        
                ev["desc"]=e.desc
                ev["venue"]=e.venue
                ev["flyer"]=e.flyer
                ev["website_url"]=e.website_url
                ev["status"]=e.status
                ev["uid"]=e.uid
                ev["created_at"]=e.created_at
                allev.append(ev)
        return jsonify(allev=allev)  
    for error in form.errors:
        app.logger.error(error)
        flash(error)
    return jsonify(msg="event test")

@app.route('/api/events/<event_id>', methods=['GET'])
@requires_auth
def event_details(event_id):       
    if request.method == 'GET':
        e=Events.query.filter_by(id=event_id).first()
        return jsonify(title=e.title, start_date=e.start_date, end_date=e.end_date, desc=e.desc, 
        venue=e.venue, flyer=e.flyer, website_url=e.website_url,
        status=e.status, uid=e.uid, created_at=e.created_at)

@app.route('/api/events/user/<user_id>', methods=["GET"])
@requires_auth
def user_events(user_id):
    if request.method=="GET":
        allev=[]
        evlist=Events.query.filter_by(uid=user_id).all()
        for e in evlist:
            ev={}
            ev['title']=e.title
            ev["start_date"]=e.start_date
            ev["end_date"]=e.end_date        
            ev["desc"]=e.desc
            ev["venue"]=e.venue
            ev["flyer"]=e.flyer
            ev["website_url"]=e.website_url
            ev["status"]=e.status
            ev["uid"]=e.uid
            ev["created_at"]=e.created_at
            allev.append(ev)
        return jsonify(allev=allev)
        #return render_template('addevent.html')

@app.route('/api/tasks')
def tasks():
    tasks = [{'id': 1, 'title': 'Teach Class'}, {'id': 2, 'title': 'Go have lunch'}]
    return jsonify(tasks=tasks)