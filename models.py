from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'
    # columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    _genres = db.Column(db.String, name="genres", nullable=False)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    # relationships
    shows = db.relationship('Show', backref="venue", lazy=True)

    # genres property
    @property
    def genres(self):
        return self._genres.split(',')

    # genres property setter
    @genres.setter
    def genres(self, value):
        self._genres = ','.join(value)

    # get columns names in list
    def get_data_keys(self, include_id=True):
        keys = self.__table__.columns.keys()
        if not include_id:
            keys.remove('id')
        return keys

    # get get data dict with columns names and values
    def get_data(self, include_id=True):
        keys = self.get_data_keys(include_id)
        data = {}
        for key in keys:
            data[key] = getattr(self, key)
        return data

    # set data from form data
    def set_data(self, form_data):
        keys = self.get_data_keys(False)
        for key in keys:
            if key == 'genres':
                setattr(self, key, form_data.getlist('genres'))
            elif key == 'seeking_talent':
                setattr(self, key, form_data.get(
                    'seeking_talent', '') == 'y')
            else:
                setattr(self, key, form_data.get(key))

    def get_past_shows(self):
        return list(filter(lambda show: show.start_time <= datetime.now(), self.shows))

    def get_upcoming_shows(self):
        return list(filter(lambda show: show.start_time > datetime.now(), self.shows))

    def __repr__(self):
        return f'<Venue id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}>'


class Artist(db.Model):
    __tablename__ = 'Artist'
    # columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    _genres = db.Column(db.String, name="genres", nullable=False)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    # relationships
    shows = db.relationship('Show', backref="artist", lazy=True)

    # genres property
    @property
    def genres(self):
        return self._genres.split(',')

    # genres property setter
    @genres.setter
    def genres(self, value):
        self._genres = ','.join(value)

    # get columns names in list
    def get_data_keys(self, include_id=True):
        keys = self.__table__.columns.keys()
        if not include_id:
            keys.remove('id')
        return keys

    # get get data dict with columns names and values
    def get_data(self, include_id=True):
        keys = self.get_data_keys(include_id)
        data = {}
        for key in keys:
            data[key] = getattr(self, key)
        return data

    # set data from form data
    def set_data(self, form_data):
        keys = self.get_data_keys(False)
        for key in keys:
            if key == 'genres':
                setattr(self, key, form_data.getlist('genres'))
            elif key == 'seeking_venue':
                setattr(self, key, form_data.get(
                    'seeking_venue', '') == 'y')
            else:
                setattr(self, key, form_data.get(key))

    def get_past_shows(self):
        return list(filter(lambda show: show.start_time <= datetime.now(), self.shows))

    def get_upcoming_shows(self):
        return list(filter(lambda show: show.start_time > datetime.now(), self.shows))

    def __repr__(self):
        return f'<Artist id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}>'


class Show(db.Model):
    __tablename__ = 'Show'
    # columns
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f'<Show id: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}, start_time: {self.start_time}>'
