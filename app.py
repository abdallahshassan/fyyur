#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import VenueForm, ArtistForm, ShowForm
from datetime import datetime
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


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
    genres = db.Column(db.String, nullable=False)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    # relationships
    shows = db.relationship('Show', backref="venue", lazy=True)

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
    genres = db.Column(db.String, nullable=False)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    # relationships
    shows = db.relationship('Show', backref="artist", lazy=True)

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # get areas
    areas = Venue.query.with_entities(
        Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

    # final data for the template
    data = []
    for area in areas:
        # venues data for this area
        area_data = []
        venues = Venue.query.filter(
            Venue.city == area[0], Venue.state == area[1]).all()
        for venue in venues:
            area_data.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(venue.get_upcoming_shows())
            })
        # add area city, state & venues data to final data
        data.append({
            "city": area[0],
            "state": area[1],
            "venues": area_data
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')

    # case insensitive search
    venues = Venue.query.filter(
        Venue.name.ilike('%' + search_term + '%')).all()

    # prepare count and data of response
    count = len(venues)
    data = []
    for venue in venues:
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(venue.get_upcoming_shows())
        })

    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # get by id
    venue = Venue.query.get(venue_id)

    # direct data from columns
    data = {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link
    }

    # genres list
    data['genres'] = venue.genres.split(',')

    # seeking description if seeking_talent is true
    if venue.seeking_talent:
        data['seeking_description'] = venue.seeking_description

    # show to dict
    def get_show_dict(show):
        return {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }

    # past_shows
    past_shows = venue.get_past_shows()
    data['past_shows_count'] = len(past_shows)
    data['past_shows'] = []
    for show in past_shows:
        data['past_shows'].append(get_show_dict(show))

    # upcoming shows
    upcoming_shows = venue.get_upcoming_shows()
    data['upcoming_shows_count'] = len(upcoming_shows)
    data['upcoming_shows'] = []
    for show in upcoming_shows:
        data['upcoming_shows'].append(get_show_dict(show))

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        data = request.form
        venue = Venue()
        venue.name = data.get('name', '')
        venue.city = data.get('city', '')
        venue.state = data.get('state', '')
        venue.address = data.get('address', '')
        venue.phone = data.get('phone', '')
        venue.genres = ','.join(data.getlist('genres'))
        venue.image_link = data.get('image_link', '')
        venue.website = data.get('website', '')
        venue.facebook_link = data.get('facebook_link', '')
        venue.seeking_talent = (data.get('seeking_talent', '') == 'y')
        venue.seeking_description = data.get('seeking_description', '')
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' +
              data.get('name', '') + ' could not be listed.')
    else:
        flash('Venue ' + data.get('name', '') + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return ''

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = Artist.query.all()

    # final data for the template
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')

    # case insensitive search
    artists = Artist.query.filter(
        Artist.name.ilike('%' + search_term + '%')).all()

    # prepare count and data of response
    count = len(artists)
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(artist.get_upcoming_shows())
        })

    response = {
        "count": count,
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # get by id
    artist = Artist.query.get(artist_id)

    # direct data from columns
    data = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link
    }

    # genres list
    data['genres'] = artist.genres.split(',')

    # seeking description if seeking_venue is true
    if artist.seeking_venue:
        data['seeking_description'] = artist.seeking_description

    # show to dict
    def get_show_dict(show):
        return {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }

    # past_shows
    past_shows = artist.get_past_shows()
    data['past_shows_count'] = len(past_shows)
    data['past_shows'] = []
    for show in past_shows:
        data['past_shows'].append(get_show_dict(show))

    # upcoming shows
    upcoming_shows = artist.get_upcoming_shows()
    data['upcoming_shows_count'] = len(upcoming_shows)
    data['upcoming_shows'] = []
    for show in upcoming_shows:
        data['upcoming_shows'].append(get_show_dict(show))

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # get by id
    artist = Artist.query.get(artist_id)

    # form with setting default values
    form = ArtistForm()
    form.name.default = artist.name
    form.city.default = artist.city
    form.state.default = artist.state
    form.phone.default = artist.phone
    form.image_link.default = artist.image_link
    form.genres.default = artist.genres.split(',')
    form.website.default = artist.website
    form.facebook_link.default = artist.facebook_link
    form.seeking_venue.default = artist.seeking_venue
    form.seeking_description.default = artist.seeking_description
    form.process()

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    data = request.form
    try:
        data = request.form
        artist = Artist.query.get(artist_id)
        artist.name = data.get('name', '')
        artist.city = data.get('city', '')
        artist.state = data.get('state', '')
        artist.phone = data.get('phone', '')
        artist.genres = ','.join(data.getlist('genres'))
        artist.image_link = data.get('image_link', '')
        artist.website = data.get('website', '')
        artist.facebook_link = data.get('facebook_link', '')
        artist.seeking_venue = (data.get('seeking_venue', '') == 'y')
        artist.seeking_description = data.get('seeking_description', '')
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # get by id
    venue = Venue.query.get(venue_id)

    # form with setting default values
    form = VenueForm()
    form.name.default = venue.name
    form.city.default = venue.city
    form.state.default = venue.state
    form.address.default = venue.address
    form.phone.default = venue.phone
    form.image_link.default = venue.image_link
    form.genres.default = venue.genres.split(',')
    form.website.default = venue.website
    form.facebook_link.default = venue.facebook_link
    form.seeking_talent.default = venue.seeking_talent
    form.seeking_description.default = venue.seeking_description
    form.process()

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    data = request.form
    try:
        data = request.form
        venue = Venue.query.get(venue_id)
        venue.name = data.get('name', '')
        venue.city = data.get('city', '')
        venue.state = data.get('state', '')
        venue.address = data.get('address', '')
        venue.phone = data.get('phone', '')
        venue.genres = ','.join(data.getlist('genres'))
        venue.image_link = data.get('image_link', '')
        venue.website = data.get('website', '')
        venue.facebook_link = data.get('facebook_link', '')
        venue.seeking_talent = (data.get('seeking_talent', '') == 'y')
        venue.seeking_description = data.get('seeking_description', '')
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        data = request.form
        artist = Artist()
        artist.name = data.get('name', '')
        artist.city = data.get('city', '')
        artist.state = data.get('state', '')
        artist.phone = data.get('phone', '')
        artist.genres = ','.join(data.getlist('genres'))
        artist.image_link = data.get('image_link', '')
        artist.website = data.get('website', '')
        artist.facebook_link = data.get('facebook_link', '')
        artist.seeking_venue = (data.get('seeking_venue', '') == 'y')
        artist.seeking_description = data.get('seeking_description', '')
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' +
              data.get('name', '') + ' could not be listed.')
    else:
        flash('Artist ' + data.get('name', '') + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()

    # final data for the template
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        data = request.form
        show = Show()
        show.venue_id = data.get('venue_id', '')
        show.artist_id = data.get('artist_id', '')
        show.start_time = data.get('start_time', '')
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
