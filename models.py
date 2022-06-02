from datetime import datetime #Import datetime to use datatime.utcnow()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate #Import flask migrate to use migration


app = Flask(__name__)

# TODO: connect to a local postgresql database
app.config.from_object('config')

# Initiate instance of database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venue' # change tablename to small letter to fixed issues

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column("genres", db.ARRAY(db.String()))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(120))
    seeking_description = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} name: {self.name}>'

    # TODO DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist' # change tablename to small letter 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column("genres", db.ARRAY(db.String()))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(120))
    seeking_description = db.Column(db.String(250))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} name: {self.name}>'

    
    # TODO DONE: implement any missing fields, as a database migration using Flask-Migrate

# TODO DONE: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __repr__(self):
      return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'
