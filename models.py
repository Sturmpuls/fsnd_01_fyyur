import enum

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# genres = ('Alternative', 'Blues', 'Classical', 'Country', 'Electronic', 'Folk',
#           'Funk', 'Hip-Hop', 'Heavy Metal', 'Instrumental', 'Jazz',
#           'Musical Theatre', 'Pop', 'Punk', 'R&B', 'Reggae', 'Rock n Roll',
#           'Soul', 'Other')
# genres_enum = db.Enum(*genres, name='genres')

class GenreEnum(enum.Enum):
  alternative = 'Alternative'
  blues = 'Blues'
  classical = 'Classical'
  country = 'Country'
  electronic = 'Electronic'
  folk = 'Folk'
  funk = 'Funk'
  hip_hop = 'Hip-Hop'
  heavy_metal = 'Heavy Metal'
  instrumental = 'Instrumental'
  jazz = 'Jazz'
  musical_theatre = 'Musical Theatre'
  pop = 'Pop'
  punk = 'Punk'
  rnb = 'R&B'
  reggae = 'Reggae'
  rocknroll = 'Rock n Roll'
  soul = 'Soul'
  other = 'Other'


GenreEnum_ = db.Enum(GenreEnum, name='genres', values_callable=lambda x: [str(e.value) for e in GenreEnum])


class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  city = db.Column(db.String(120)) # nullable=False
  state = db.Column(db.String(120)) # nullable=False
  address = db.Column(db.String(120)) # nullable=False
  phone = db.Column(db.String(120)) # nullable=False
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  genres = db.relationship('VenueGenres', backref='venue', lazy='select',
                            cascade="all, delete-orphan")
  
  shows = db.relationship('Show', lazy='select', backref='venue')
  artists = association_proxy('shows', 'artist')
  
  @property
  def past_shows(self):
    return Show.query.filter(
      Show.starttime < datetime.now(),
      Show.venue_id == self.id).all()

  @property
  def upcoming_shows(self):
    return Show.query.filter(
      Show.starttime > datetime.now(),
      Show.venue_id == self.id).all()

  @property
  def num_upcoming_shows(self):
    return len(self.upcoming_shows)

  @property
  def num_past_shows(self):
    return len(self.past_shows)
  
  @property
  def summary(self):
    return  {
      'id': self.id,
      'name': self.name,
      'num_upcoming_shows': self.num_upcoming_shows
    }

  # @property
  # def show_count(self):
  #   # return db.object_session(self).query(Show).with_parent(self).count()
  #   return len(self.shows)

  def __repr__(self):
    return f'<Venue: {self.name}>'
  
  def get_areas_with_venue():
    locations = Venue.query.distinct(Venue.city, Venue.state).all()
    return [{'city': l.city, 'state': l.state} for l in locations]
  
  def get_venues_by_area(city, state):
    return Venue.query.filter_by(city=city, state=state).all()

  def get_venues_by_partial_name(name):
    return Venue.query.filter(Venue.name.ilike(f'%{name}%')).all()

  def to_dict(self):
    return {
      'id': self.id,
      'name': self.name,
      'city': self.city,
      'state': self.state,
      'address': self.address,
      'phone': self.phone,
      'image_link': self.image_link,
      'facebook_link': self.facebook_link,
      'website': self.website,
      'seeking_talent': self.seeking_talent,
      'seeking_description': self.seeking_description,
      'genres': [g.genre for g in self.genres],
      "past_shows": [{
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.starttime.isoformat() + 'Z'
      } for show in self.past_shows],
      "upcoming_shows": [{
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.starttime.isoformat() + 'Z'
      } for show in self.upcoming_shows],
      "past_shows_count": self.num_past_shows,
      "upcoming_shows_count": self.num_upcoming_shows
    }


class VenueGenres(db.Model):
  __tablename__ = 'VenueGenres'

  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  genre = db.Column(GenreEnum_, primary_key=True)
  
  def __repr__(self):
    return f'{self.genre}'


class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False, unique=True)
  city = db.Column(db.String(120)) # nullable=False
  state = db.Column(db.String(120)) # nullable=False
  phone = db.Column(db.String(120)) # nullable=False
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String())
  genres = db.relationship('ArtistGenres', backref='artist', lazy='dynamic',
                            cascade="all, delete-orphan")

  def __repr__(self):
    return f'Artist: {self.name}'

  @property
  def past_shows(self):
    return Show.query.filter(
      Show.starttime < datetime.now(),
      Show.artist_id == self.id).all()

  @property
  def upcoming_shows(self):
    return Show.query.filter(
      Show.starttime > datetime.now(),
      Show.artist_id == self.id).all()

  @property
  def num_upcoming_shows(self):
    return len(self.upcoming_shows)

  @property
  def num_past_shows(self):
    return len(self.past_shows)

  @property
  def summary(self):
    return  {
      'id': self.id,
      'name': self.name,
      'num_upcoming_shows': self.num_upcoming_shows
    }

  def get_artists_by_partial_name(name):
    return Artist.query.filter(Artist.name.ilike(f'%{name}%')).all()

  def to_dict(self, with_shows=True):
    data = {
      'id': self.id,
      'name': self.name,
      'city': self.city,
      'state': self.state,
      'phone': self.phone,
      'image_link': self.image_link,
      'facebook_link': self.facebook_link,
      'website': self.website,
      'seeking_venue': self.seeking_venue,
      'seeking_description': self.seeking_description,
      'genres': [g.genre for g in self.genres]
    }
    if with_shows:
      shows = {
        'past_shows': [{
          'venue_id': show.venue.id,
          'venue_name': show.venue.name,
          'venue_image_link': show.venue.image_link,
          'start_time': show.starttime.isoformat() + 'Z'
        } for show in self.past_shows],
        'upcoming_shows': [{
          'venue_id': show.venue.id,
          'venue_name': show.venue.name,
          'venue_image_link': show.venue.image_link,
          'start_time': show.starttime.isoformat() + 'Z'
        } for show in self.upcoming_shows],
        'past_shows_count': self.num_past_shows,
        'upcoming_shows_count': self.num_upcoming_shows
      }
      data = {**data, **shows}
    return data


class ArtistGenres(db.Model):
  __tablename__ = 'ArtistGenres'
  
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  genre = db.Column(GenreEnum_, primary_key=True)

  def __repr__(self):
    return f'{self.genre}'


class Show(db.Model):
  __tablename__ = 'Show'
  
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  starttime = db.Column(db.DateTime, primary_key=True)

  artist = db.relationship('Artist', lazy='joined')
  
  def __init__(self, venue=None, artist=None, starttime=None):
    self.venue = venue
    self.artist = artist
    self.starttime = starttime
        
  def __repr__(self):
      return f'<{self.artist.name} @ {self.venue.name}: {self.starttime}>'