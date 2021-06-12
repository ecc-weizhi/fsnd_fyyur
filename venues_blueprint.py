from datetime import datetime

from flask import Blueprint, render_template, request, flash, url_for
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from forms import VenueForm
from models import db, Venue, VenueArtistShow, Artist

venues_blueprint = Blueprint('venues', __name__, url_prefix='')


@venues_blueprint.route('/venues')
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
    return render_template('pages/venues.html', areas=data)


@venues_blueprint.route('/venues/search', methods=['POST'])
def search_venues():
    now = datetime.utcnow()
    like_search_term = "%{}%".format(request.form.get('search_term', ''))
    venue_list = db.session.query(Venue.id, Venue.name, func.count(VenueArtistShow.id)) \
        .join(VenueArtistShow, VenueArtistShow.venue_id == Venue.id) \
        .filter(VenueArtistShow.start_time > now, Venue.name.ilike(like_search_term)) \
        .group_by(Venue.id, Venue.name) \
        .all()
    response = {
        "count": len(venue_list),
        "data": [{
            "id": venue[0],
            "name": venue[1],
            "num_upcoming_shows": venue[2]
        } for venue in venue_list]
    }
    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', '')
                           )


@venues_blueprint.route('/venues/<int:venue_id>')
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


@venues_blueprint.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@venues_blueprint.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form, meta={'csrf': False})

    if form.validate_on_submit():
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
            return render_template('pages/home.html')
        except SQLAlchemyError:
            flash(f"An error occurred. Venue{f' {name} ' if name else ' '}could not be listed.")
            db.session.rollback()
        finally:
            db.session.close()

    for key, value in form.errors.items():
        flash(f"{key}: {value}\n")
    return render_template('forms/new_venue.html', form=form)


@venues_blueprint.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).first_or_404().delete()
        db.session.commit()
        flash('The venue has been removed together with all of its shows.')
        return render_template('pages/home.html')
    except SQLAlchemyError:
        flash('It was not possible to delete this Venue')
    return redirect(url_for('venues.venues'))


@venues_blueprint.route('/venues/<int:venue_id>/edit', methods=['GET'])
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


@venues_blueprint.route('/venues/<int:venue_id>/edit', methods=['POST'])
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
    except SQLAlchemyError:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('venues.show_venue', venue_id=venue_id))
