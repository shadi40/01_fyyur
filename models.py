"""
Artist, Venue and Show models
"""
# Imports

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, CheckConstraint
import re
from datetime import datetime
from sqlalchemy import func

db = SQLAlchemy()

# Models.

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))  # Adding a new field 'website'
    genres = db.Column(db.String(120), nullable=False) # Add the venue_genres field
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    past_shows_count = db.Column(db.Integer, default=0)
    upcoming_shows_count = db.Column(db.Integer, default=0)
   # Add more fields as needed
    def update_shows_count(self):
        now = datetime.now()
        past_shows_count = db.session.query(func.count(Show.id)).filter(Show.artist_id == self.id, Show.start_time < now).scalar()
        upcoming_shows_count = db.session.query(func.count(Show.id)).filter(Show.artist_id == self.id, Show.start_time >= now).scalar()
        self.past_shows_count = past_shows_count
        self.upcoming_shows_count = upcoming_shows_count
        db.session.commit()
   # Add additional constraints
    __table_args__ = (
        UniqueConstraint('name', 'city', 'state', name='uq_Venue_name_city_state'),
        CheckConstraint("phone <> ''", name='chk_Venue_phone_not_empty')
    )
    @staticmethod
    def validate_phone_number(key, value):
        # Modify the regular expression pattern to allow different phone number formats
        phone_pattern = re.compile(r'^\+?\d{1,3}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')
        if not phone_pattern.match(value):
            raise ValueError(f"Invalid phone number format: {value}")
        return value

    @db.validates('phone')
    def validate_phone(self, key, value):
        return self.validate_phone_number(key, value)



class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String)  # Add the genres column here
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String)
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    past_shows_count = db.Column(db.Integer, default=0)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    # Add more fields as needed
    def update_shows_count(self):
        now = datetime.now()
        past_shows_count = db.session.query(func.count(Show.id)).filter(Show.artist_id == self.id, Show.start_time < now).scalar()
        upcoming_shows_count = db.session.query(func.count(Show.id)).filter(Show.artist_id == self.id, Show.start_time >= now).scalar()
        self.past_shows_count = past_shows_count
        self.upcoming_shows_count = upcoming_shows_count
        db.session.commit()

     # Add additional constraints
    __table_args__ = (
        UniqueConstraint('name', 'city', 'state', name='uq_artist_name_city_state'),
        CheckConstraint("phone <> ''", name='chk_artist_phone_not_empty')
    )
    @staticmethod
    def validate_phone_number(key, value):
        # Modify the regular expression pattern to allow different phone number formats
        phone_pattern = re.compile(r'^\+?\d{1,3}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')
        if not phone_pattern.match(value):
            raise ValueError(f"Invalid phone number format: {value}")
        return value

    @db.validates('phone')
    def validate_phone(self, key, value):
        return self.validate_phone_number(key, value)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))