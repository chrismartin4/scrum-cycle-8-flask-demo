from app import db

#eventCreator = db.Table("eventCreator",
#    db.Column('creatorid', db.Integer, db.ForeignKey('user.id')),
#    db.Column('eventid', db.Integer, db.ForeignKey('events.id'))
#)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name= db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    profile_photo= db.Column(db.String(200)) #refers to the location of the image
    role=db.Column(db.String(1))  # ROLE = ["USER","ADMIN"] 
    created_at = db.Column(db.DateTime())

    def __init__(self, full_name, email, password, profile_photo,role,date):
        self.full_name = full_name
        self.email = email
        self.password = password
        self.profile_photo=profile_photo
        self.role=role
        self.created_at = date

class Events(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(128))
    start_date= db.Column(db.DateTime())
    end_date= db.Column(db.DateTime())
    desc= db.Column(db.String(500))
    venue= db.Column(db.String(250))
    flyer= db.Column(db.String(200))
    website_url= db.Column(db.String(128))
    status= db.Column(db.String(128)) # STATUS = ["PENDING","PUBLISHED"] 
    uid= db.Column(db.Integer) # id of the user who created the event
    created_at= db.Column(db.DateTime())


    def __init__(self, title, start_date, end_date, desc, venue, flyer, website_url, status, uid, created_at):
        self.title= title
        self.start_date= start_date
        self.end_date= end_date
        self.desc= desc
        self.venue= venue
        self.flyer= flyer
        self.website_url= website_url
        self.status= status
        self.uid= uid
        self.created_at= created_at
