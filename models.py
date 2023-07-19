"""
Artist, Venue and Show models
"""
# Imports

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, CheckConstraint
import re

db = SQLAlchemy()

# Models.

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String, unique=True, nullable=False)  # Add unique and nullable constraints
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))  # Adding a new field 'website'
    genres = db.Column(db.String(120), nullable=False) # Add the venue_genres field
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
   # Add more fields as needed
    # Add additional constraints
    __table_args__ = (
        UniqueConstraint('name', 'city', 'state', name='uq_Venue_name_city_state'),
        CheckConstraint("phone <> ''", name='chk_Venue_phone_not_empty')
    )
    # Add a regular expression pattern for phone number validation
    phone_pattern = re.compile(r'^\d{10}$')  # Example pattern for 10-digit phone numbers

    def validate_phone(self, key, value):
        if not Venue.phone_pattern.match(value):
            raise ValueError(f"Invalid phone number format: {value}")
        return value

    @db.validates('phone')
    def validate_phone_number(self, key, value):
        return self.validate_phone(key, value)



class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    phone = db.Column(db.String, unique=True, nullable=False)  # Add unique and nullable constraints
    genres = db.Column(db.String)  # Add the genres column here
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String)
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

     # Add additional constraints
    __table_args__ = (
        UniqueConstraint('name', 'city', 'state', name='uq_artist_name_city_state'),
        CheckConstraint("phone <> ''", name='chk_artist_phone_not_empty')
    )
    # Add a regular expression pattern for phone number validation
    phone_pattern = re.compile(r'^\d{10}$')  # Example pattern for 10-digit phone numbers

    def validate_phone(self, key, value):
        if not Artist.phone_pattern.match(value):
            raise ValueError(f"Invalid phone number format: {value}")
        return value

    @db.validates('phone')
    def validate_phone_number(self, key, value):
        return self.validate_phone(key, value)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))