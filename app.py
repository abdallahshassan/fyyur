#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
import sys
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort,
    jsonify
)
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import VenueForm, ArtistForm, ShowForm
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

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

    # venue data
    data = venue.get_data()

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

    showForm = ShowForm()
    return render_template('pages/show_venue.html', venue=data, showForm=showForm)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # validate form
    form = VenueForm(request.form)
    if not form.validate():
        return render_template('forms/new_venue.html', form=form)

    # create venue
    error = False
    try:
        venue = Venue()
        venue.set_data(form_data=request.form)
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
              request.form.get('name', '') + ' could not be listed.')
    else:
        flash('Venue ' + request.form.get('name', '') +
              ' was successfully listed!')

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
    result_format = request.form.get('result_format', '')

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

    if result_format == 'json':
        return jsonify(response)

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # get by id
    artist = Artist.query.get(artist_id)

    # artist data
    data = artist.get_data()

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
    data = artist.get_data(include_id=False)
    form = ArtistForm(data=data)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # validate form
    form = ArtistForm(request.form)
    if not form.validate():
        artist = Artist.query.get(artist_id)
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    # edit artist
    try:
        artist = Artist.query.get(artist_id)
        artist.set_data(form_data=request.form)
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
    data = venue.get_data(include_id=False)
    form = VenueForm(data=data)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # validate form
    form = VenueForm(request.form)
    if not form.validate():
        venue = Venue.query.get(venue_id)
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    # edit venue
    try:
        venue = Venue.query.get(venue_id)
        venue.set_data(form_data=request.form)
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
    # validate form
    form = ArtistForm(request.form)
    if not form.validate():
        return render_template('forms/new_artist.html', form=form)

    # create artist
    error = False
    try:
        artist = Artist()
        artist.set_data(form_data=request.form)
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
              request.form.get('name', '') + ' could not be listed.')
    else:
        flash('Artist ' + request.form.get('name', '') +
              ' was successfully listed!')

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
    data = {
        'venue_id': request.args.get('venue_id', ''),
        'artist_id': request.args.get('artist_id', '')
    }
    form = ShowForm(data=data)
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # validate form
    form = ShowForm(request.form)
    if not form.validate():
        return render_template('forms/new_show.html', form=form)

    # create show
    error = False
    try:
        show = Show()
        show.venue_id = request.form.get('venue_id', '')
        show.artist_id = request.form.get('artist_id', '')
        show.start_time = request.form.get('start_time', '')
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
