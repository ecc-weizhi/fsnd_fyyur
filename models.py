from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()


def shorten(text):
    if text and len(text) > 5:
        return text[:5] + "..."
    return text


class VenueArtistShow(db.Model):
    __tablename__ = 'artist_and_venue_shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.DateTime)
    venue = db.relationship('Venue', backref=db.backref('show_list'))
    artist = db.relationship('Artist', backref=db.backref('show_list'))

    def __repr__(self):
        return f"<VenueArtistShow id:{self.id}, " \
               f"artist_id:{self.artist_id}, " \
               f"venue_id:{self.venue_id}, " \
               f"start_time:{self.start_time}, " \
               f"venue:{self.venue}, " \
               f"artist:{self.artist}>"


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    website_link = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Venue id:{self.id}, " \
               f"name:{self.name}, " \
               f"city:{shorten(self.city)}, " \
               f"state:{self.state}, " \
               f"address:{shorten(self.address)}, " \
               f"phone:{self.phone}, " \
               f"genres:{self.genres}, " \
               f"facebook_link:{shorten(self.facebook_link)}, " \
               f"image_link:{shorten(self.image_link)}, " \
               f"website_link:{shorten(self.website_link)}, " \
               f"seeking_talent:{self.seeking_talent}, " \
               f"seeking_description:{shorten(self.seeking_description)}," \
               f"show_list:{self.show_list}>"


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    website_link = db.Column(db.String(500), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Artist id:{self.id}, " \
               f"name:{self.name}, " \
               f"city:{shorten(self.city)}, " \
               f"state:{self.state}, " \
               f"phone:{self.phone}, " \
               f"genres:{self.genres}, " \
               f"facebook_link:{shorten(self.facebook_link)}, " \
               f"image_link:{shorten(self.image_link)}, " \
               f"website_link:{shorten(self.website_link)}, " \
               f"seeking_venue:{self.seeking_venue}, " \
               f"seeking_description:{shorten(self.seeking_description)}, " \
               f"show_list:{self.show_list}>"
