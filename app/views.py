from turtle import title
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash,g,send_from_directory,session,make_response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from app import app, db,login_manager
from .forms import RegisterForm, LoginForm, EventForm,searchForm
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


###########################################################     WEB  ######################################################
@app.route("/web/register", methods=["GET", "POST"])
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
            usercheck= User.query.filter_by(email=email).first()
            if usercheck is None :
                user = User(full_name=name, email=email,password=password,profile_photo=picfilename,role=role,date=dt)
                db.session.add(user)
                db.session.commit()
                pic.save(os.path.join(app.config['UPLOAD_FOLDER'],picfilename))
                flash("User "+name+' Successfully registered. Please Log in.')
                return redirect(url_for("login"))
            else:
                return flash('User already exists. Please Log in.')
    for error in form.errors:
        app.logger.error(error)
        flash(error)
    return render_template("register.html", form=form)

@app.route("/web/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        if form.email.data:
            email=form.email.data
            password=form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and check_password_hash(user.password,password):
                login_user(user)
                session['uid']=user.id
                if user.role =="Admin":
                    session['is_admin'] = True
                elif user.role =="Regular":
                    session['is_admin'] = False
                return redirect(url_for("addevent"))
            else:
                flash('Email or Password is incorrect.', 'danger')
    for error in form.errors:
        app.logger.error(error)
        flash(error)
    return render_template("login.html", form=form)

@app.route("/web/logout")
@login_required
def web_logout():
    # Logout the user and end the session
    logout_user()
    session.pop('uid', None)
    session.pop('is_admin', None)
    session.pop('is_regular', None)
    flash('You were logged out', 'success')
    return redirect(url_for('login'))

@app.route('/web/events/add', methods=["GET", "POST"])
@login_required
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
        dt=datetime.datetime.now()
        event=Events(title=title, start_date=start_date, end_date=end_date, desc=desc, venue=venue, flyer=flyerfilename, website_url=website_url, status="Pending", uid=session['uid'], created_at=dt)
        if event is not None:
            db.session.add(event)
            db.session.commit()
            flyer.save(os.path.join(app.config['UPLOAD_FOLDER'],flyerfilename))
            flash('Event Successfully registered.','success')
        else:
            flash('Event already exists')
    for error in form.errors:
        app.logger.error(error)
        flash(error)
    return render_template("addevent.html", form=form)

@app.route('/web/events', methods=["GET", "POST"])
@login_required
def viewevent():
    evlist=[]
    if request.method=="GET":
        if session['is_admin']== True:
            evlist=Events.query.order_by(Events.id).all()
        elif session['is_admin']== False:
            evlist=Events.query.filter_by(status="Published").all()
    return render_template("viewevents.html",evlist=evlist)

@app.route("/web/events/pending", methods=["GET"])
@login_required
def web_pendingEvents():
    if session['is_admin']== True:
        events=Events.query.filter_by(status="Pending").all()
    else:
        flash('User is not an Admin', 'danger')
    return render_template("addevent.html",events=events)

@app.route('/web/events/myevents', methods=["GET"])
@login_required
def web_user_events(user_id):
    if request.method=="GET":
        evlist=Events.query.filter_by(uid=session['uid']).all()
        return render_template("addevent.html",evlist=evlist)

@app.route("/outputs/<filename>")
def get_image(filename):
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir, app.config['UPLOAD_FOLDER']), filename)

@app.route('/web/events/<event_id>/', methods=['GET','PATCH','PUT','DELETE'])
@requires_auth
def web_event_details(event_id):
    form = EventForm()
    e=Events.query.filter_by(id=event_id).first()      
    if request.method == 'GET':
        return jsonify(title=e.title, start_date=e.start_date, end_date=e.end_date, desc=e.desc, 
        venue=e.venue, flyer=e.flyer, website_url=e.website_url,
        status=e.status, uid=e.uid, created_at=e.created_at)
    if request.method == 'PATCH':
        if session['is_admin']== True:
            e.status='Published'
            db.session.commit()
            return jsonify(msg='Event '+e.title+' Successfully Published.',Event=e),201
        else:
            return jsonify(msg='User is not an Admin. Please Log in as Admin to Publish events.'),401
    if request.method == 'PUT':
        if session['is_admin']== True or session['uid']==e.uid:
            e.title=form.title.data
            e.start_date=form.start_date.data
            e.end_date=form.end_date.data
            e.desc=form.desc.data
            e.venue=form.venue.data
            flyer=form.flyer.data
            e.flyer=secure_filename(flyer.filename)
            e.website_url=form.website_url.data
            db.session.commit()
            return jsonify(msg='Event '+e.title+' Successfully updated.',updatedEvent=e),201
        else:
            return jsonify(msg='User is not an Admin nor the creator of this event. Only admins and the creator may update this event.'),401
    if request.method == 'DELETE':
        if session['is_admin']== True or session['uid']==e.uid:
            e=Events.query.filter_by(id=event_id).first()
            db.session.delete(e)
            db.session.commit()
            return jsonify(msg='Event '+e.title+' Successfully deleted.')
        else:
            return jsonify(msg='User is not an Admin nor the creator of this event. Only admins and the creator may delete this event.'),401


@app.route('/web/about')
@login_required
def about():
    return render_template('about.html')
# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))





####################################################     API  ##############################################################################
@app.route("/api/v1/register", methods=["POST"])

def api_register():
    form = RegisterForm()
    #if request.method == "POST" and form.validate_on_submit():
    if request.method == "POST":
            name=form.full_name.data
            email=form.email.data
            password=form.password.data
            pic=form.profile_photo.data
            picfilename=secure_filename(pic.filename)
            role=form.role.data
            dt=datetime.datetime.now()
            usercheck= User.query.filter_by(email=email).first()
            if usercheck is None :
                user = User(full_name=name, email=email,password=password,profile_photo=picfilename,role=role,date=dt)
                db.session.add(user)
                db.session.commit()
                pic.save(os.path.join(app.config['UPLOAD_FOLDER'],picfilename))
                #return redirect(url_for("login"))
                return jsonify(message="User "+name+' Successfully registered. Please Log in.'), 201
            else:
                return jsonify(message='User already exists. Please Log in.'), 409
    err=[]
    for error in form.errors:
        app.logger.error(error)
        flash(error)
        err.append(error)
    return jsonify(msg="register errors",err=err)
    #return render_template("register.html", form=form)

@app.route("/api/v1/login", methods=["GET", "POST"])
def api_login():
    form = LoginForm()
    if request.method == "POST" :
        if form.email.data:
            email=form.email.data
            password=form.password.data
            user = User.query.filter_by(email=email).first()
            if user is not None and check_password_hash(user.password,password):
                payload = { 'email': user.email,'userid': user.id,'role':user.role}
                token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
                #token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
                jsonmsg=jsonify(message=" Login Successful and Token was Generated",token=token)
                return jsonmsg,200
            else:
                flash('Email or Password is incorrect.', 'danger')
    err=[]
    for error in form.errors:
        app.logger.error(error)
        flash(error)
        err.append(error)
    return jsonify(errors=err)

@app.route("/api/v1/logout")
@requires_auth
def logout():
    # Logout the user and end the session
    return jsonify('You were logged out succesfully.'),200



@app.route('/api/v1/events', methods=["GET", "POST"])
@requires_auth
def event():
    form = EventForm()
    if request.method == "POST" :
        title=form.title.data
        start_date=form.start_date.data
        end_date=form.end_date.data
        desc=form.desc.data
        venue=form.venue.data
        flyer=form.flyer.data
        flyerfilename=secure_filename(flyer.filename)
        website_url=form.website_url.data
        dt=datetime.datetime.now()
        event=Events(title=title, start_date=start_date, end_date=end_date, desc=desc, venue=venue, flyer=flyerfilename, website_url=website_url, status="Pending", uid=g.current_user['userid'], created_at=dt)
        if event is not None:
            db.session.add(event)
            db.session.commit()
            flyer.save(os.path.join(app.config['UPLOAD_FOLDER'],flyerfilename))
            return jsonify('Event Successfully registered.'),201
        else:
            return jsonify('Event already exists.'),409
    if request.method=="GET":
        allev=[]
        evlist=Events.query.filter_by(status="Published").all()
        for e in evlist:
            ev={}
            ev['Event_id']=e.id
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
        return jsonify(allev=allev),200  
    

@app.route('/api/v1/events/<event_id>', methods=['GET','PATCH','PUT','DELETE'])
@requires_auth
def event_details(event_id):
    form = EventForm()
    e=Events.query.filter_by(id=event_id).first()      
    if request.method == 'GET':
        return jsonify(eventid=e.id,title=e.title, start_date=e.start_date, end_date=e.end_date, desc=e.desc, 
        venue=e.venue, flyer=e.flyer, website_url=e.website_url,
        status=e.status, uid=e.uid, created_at=e.created_at)
    if request.method == 'PATCH':
        if g.current_user['role']=='Admin':
            e.status='Published'
            db.session.commit()
            return jsonify(msg='Event ID: '+str(e.id) +" Title: "+e.title+' Successfully Published.'),200
        else:
            return jsonify(msg='User is not an Admin. Please Log in as Admin to Publish events.'),401
    if request.method == 'PUT':
        if g.current_user['role']=='Admin' or g.current_user['userid']==e.uid:
            e.title=form.title.data
            e.desc=form.desc.data
            e.venue=form.venue.data
            flyer=form.flyer.data
            e.flyer=secure_filename(flyer.filename)
            e.website_url=form.website_url.data
            e.status=e.status
            e.created_at=e.created_at
            db.session.commit()
            return jsonify(msg='Event ID: '+str(e.id) +" Title: "+e.title+' Successfully updated.'),200
        else:
            return jsonify(msg='User is not an Admin nor the creator of this event. Only admins and the creator may update this event.'),401
    if request.method == 'DELETE':
        if g.current_user['role']=='Admin' or g.current_user['userid']==e.uid:
            e=Events.query.filter_by(id=event_id).first()
            if e is not None:
                db.session.delete(e)
                db.session.commit()
                return jsonify(msg='Event ID: '+str(e.id) +" Title: "+e.title+' Successfully deleted.')
            else:
                return jsonify(msg='This Event does not exist or has aleady been deleted'),409
        else:
            return jsonify(msg='User is not an Admin nor the creator of this event. Only admins and the creator may delete this event.'),401




@app.route('/api/v1/events/user/<user_id>', methods=["GET"])
@requires_auth
def user_events(user_id):
    if request.method=="GET":
        allev=[]
        evlist=Events.query.filter_by(uid=user_id).all()
        for e in evlist:
            ev={}
            ev['Event_id']=e.id
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

@app.route('/api/v1/profile', methods=["GET"])
@requires_auth
def user_details():
    if request.method=="GET":
        u = User.query.filter_by(id=g.current_user['userid']).first()
        usp={}
        usp['user_id']=u.id
        usp['full_name']=u.full_name
        usp["email"]=u.email
        usp["profile_photo"]=u.profile_photo        
        usp["role"]=u.role
        return jsonify(profile=usp)

@app.route('/api/v1/events/search', methods=["GET","POST"])
@requires_auth
def events_search():
    form=searchForm()
    searchEvents=[]
    if request.method=="POST":  
        start_date=form.start_date.data
        end_date=form.start_date.data
        title="%{}%".format(form.title.data)
        search_results= Events.query.filter((Events.title.like(title)|Events.start_date.is_(start_date)|Events.end_date.is_(end_date)))
        for e in search_results:
            ev={}
            ev['Event_id']=e.id
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
            searchEvents.append(ev)
        return jsonify(searchEvents=searchEvents)


@app.route("/api/v1/events/pending", methods=["GET"])
@requires_auth
def pendingEvents():
    if g.current_user['role']=='Admin':
            events=[]
            evlist=Events.query.filter_by(status="Pending").all()
            for e in evlist:
                ev={}
                ev['Event_id']=e.id
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
                events.append(ev)
            return jsonify(events=events), 200
    else:
        return jsonify(msg='User is not an Admin. Please Log in as Admin to view pending events.'),401



@app.route("/api/v1/test", methods=["GET"])
@requires_auth
def test():
    return g.current_user['role']
