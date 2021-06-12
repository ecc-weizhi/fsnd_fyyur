from datetime import datetime

from flask import Blueprint, render_template, request, flash, url_for
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from forms import ArtistForm
from models import db, Venue, VenueArtistShow, Artist

artists_blueprint = Blueprint('artists', __name__, url_prefix='')


@artists_blueprint.route('/artists')
def artists():
    data = list(map(lambda element: {
        "id": element[0],
        "name": element[1]
    }, db.session.query(Artist.id, Artist.name).all()))

    return render_template('pages/artists.html', artists=data)


@artists_blueprint.route('/artists/search', methods=['POST'])
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


@artists_blueprint.route('/artists/<int:artist_id>')
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


@artists_blueprint.route('/artists/<int:artist_id>/edit', methods=['GET'])
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


@artists_blueprint.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form, meta={'csrf': False})
    artist = Artist.query.get(artist_id)

    if form.validate_on_submit():
        try:
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
            flash('Artist ' + artist.name + ' was successfully edited!')
            return redirect(url_for('artists.show_artist', artist_id=artist_id))
        except SQLAlchemyError:
            db.session.rollback()
        finally:
            db.session.close()

    for key, value in form.errors.items():
        flash(f"{key}: {value}\n")
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@artists_blueprint.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@artists_blueprint.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form, meta={'csrf': False})

    if form.validate_on_submit():
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
            return render_template('pages/home.html')
        except SQLAlchemyError:
            flash(f"An error occurred. Artist{f' {name} ' if name else ' '}could not be listed.")
            db.session.rollback()
        finally:
            db.session.close()

    for key, value in form.errors.items():
        flash(f"{key}: {value}\n")
    return render_template('forms/new_artist.html', form=form)
