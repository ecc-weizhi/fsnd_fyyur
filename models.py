from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

show = db.Table('shows',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
    db.Column('start_time', db.DateTime),
)


def shorten(text):
    if text and len(text) > 5:
        return text[:5] + "..."
    return text


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    website_link = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500), nullable=True)
    show_list = db.relationship('Artist',
        secondary=show,
        collection_class=list
    )

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
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    website_link = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean)
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
               f"seeking_talent:{self.seeking_talent}, " \
               f"seeking_description:{shorten(self.seeking_description)}>"
