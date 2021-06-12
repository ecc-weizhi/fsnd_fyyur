# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment

from forms import *
from models import Venue, Artist, VenueArtistShow
from models import db

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    now = datetime.utcnow()
    city_state_list = db.session.query(Venue.city, Venue.state) \
        .group_by(Venue.city, Venue.state) \
        .all()

    data = [
        {
            "city": city_state[0],
            "state": city_state[1],
            "venues": db.session.query(Venue.id, Venue.name)
                .filter(Venue.city == city_state[0], Venue.state == city_state[1])
                .all()
        } for city_state in city_state_list
    ]
    for city_state_group in data:
        city_state_group["venues"] = [
            {
                "id": venue_id_name[0],
                "name": venue_id_name[1],
                "num_upcoming_shows": db.session.query(VenueArtistShow.id)
                    .filter(VenueArtistShow.start_time > now, VenueArtistShow.venue_id == venue_id_name[0])
                    .count()
            } for venue_id_name in city_state_group["venues"]
        ]
    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', '')
                           )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    now = datetime.utcnow()
    venue = Venue.query.get(venue_id)
    upcoming_shows = list(map(lambda element: {
        "artist_id": element[0],
        "artist_name": element[1],
        "artist_image_link": element[2],
        "start_time": str(element[3])
    }, db.session.query(VenueArtistShow.artist_id,
                        Artist.name,
                        Artist.image_link,
                        VenueArtistShow.start_time)
                              .join(Artist, Artist.id == VenueArtistShow.artist_id)
                              .filter(VenueArtistShow.venue_id == venue_id, VenueArtistShow.start_time >= now)
                              .all()))

    past_shows = list(map(lambda element: {
        "artist_id": element[0],
        "artist_name": element[1],
        "artist_image_link": element[2],
        "start_time": str(element[3])
    }, db.session.query(VenueArtistShow.artist_id,
                        Artist.name,
                        Artist.image_link,
                        VenueArtistShow.start_time)
                          .join(Artist, Artist.id == VenueArtistShow.artist_id)
                          .filter(VenueArtistShow.venue_id == venue_id, VenueArtistShow.start_time < now)
                          .all()))

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()

    name = None
    try:
        name = form.name.data
        venue = Venue(
            name=name,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully listed!')
    except:
        flash(f"An error occurred. Venue{f' {name} ' if name else ' '}could not be listed.")
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = list(map(lambda element: {
        "id": element[0],
        "name": element[1]
    }, db.session.query(Artist.id, Artist.name).all()))

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    now = datetime.utcnow()
    like_search_term = "%{}%".format(request.form.get('search_term', ''))
    artist_list = db.session.query(Artist.id, Artist.name, func.count(VenueArtistShow.id)) \
        .join(VenueArtistShow, VenueArtistShow.artist_id == Artist.id) \
        .filter(VenueArtistShow.start_time > now, Artist.name.ilike(like_search_term)) \
        .group_by(Artist.id, Artist.name) \
        .all()
    response = {
        "count": len(artist_list),
        "data": [{
            "id": artist[0],
            "name": artist[1],
            "num_upcoming_shows": artist[2]
        } for artist in artist_list]
    }
    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=request.form.get('search_term', '')
                           )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    now = datetime.utcnow()
    artist = Artist.query.get(artist_id)
    upcoming_shows = list(map(lambda element: {
        "venue_id": element[0],
        "venue_name": element[1],
        "venue_image_link": element[2],
        "start_time": str(element[3])
    }, db.session.query(VenueArtistShow.venue_id,
                        Venue.name,
                        Venue.image_link,
                        VenueArtistShow.start_time)
                              .join(Venue, Venue.id == VenueArtistShow.venue_id)
                              .filter(VenueArtistShow.artist_id == artist_id, VenueArtistShow.start_time >= now)
                              .all()))

    past_shows = list(map(lambda element: {
        "venue_id": element[0],
        "venue_name": element[1],
        "venue_image_link": element[2],
        "start_time": str(element[3])
    }, db.session.query(VenueArtistShow.venue_id,
                        Venue.name,
                        Venue.image_link,
                        VenueArtistShow.start_time)
                          .join(Venue, Venue.id == VenueArtistShow.venue_id)
                          .filter(VenueArtistShow.artist_id == artist_id, VenueArtistShow.start_time < now)
                          .all()))

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()

    try:
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website_link = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()

    try:
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website_link = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        db.session.rollback()
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
    # called upon submitting the new artist listing form
    form = ArtistForm()

    name = None
    try:
        name = form.name.data
        artist = Artist(
            name=name,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + name + ' was successfully listed!')
    except:
        flash(f"An error occurred. Artist{f' {name} ' if name else ' '}could not be listed.")
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    venue_artist_shows = db.session.query(VenueArtistShow).all()

    data = []
    for venue_artist_show in venue_artist_shows:
        data.append({
            "venue_id": venue_artist_show.venue_id,
            "venue_name": Venue.query.filter_by(id=venue_artist_show.venue_id).first().name,
            "artist_id": venue_artist_show.artist_id,
            "artist_name": Artist.query.filter_by(id=venue_artist_show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=venue_artist_show.artist_id).first().image_link,
            "start_time": str(venue_artist_show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()

    show = VenueArtistShow(
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data,
        start_time=form.start_time.data
    )

    try:
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
