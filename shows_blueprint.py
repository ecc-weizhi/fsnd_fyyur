from flask import Blueprint, render_template, flash
from sqlalchemy.exc import SQLAlchemyError

from forms import ShowForm
from models import db, Venue, VenueArtistShow, Artist

shows_blueprint = Blueprint('shows', __name__, url_prefix='')


@shows_blueprint.route('/shows')
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


@shows_blueprint.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@shows_blueprint.route('/shows/create', methods=['POST'])
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
    except SQLAlchemyError:
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')
