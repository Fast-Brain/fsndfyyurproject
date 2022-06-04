'''
  The entire project was inspired by https://github.com/cmdlinebeep/fyyur, and my Udacity Programming for Data Science Python for enterprises project https://github.com/Fast-Brain/pdsnd_github.
'''
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Show, Artist, app, db
import sys
#  FIXED: AttributeError: module 'collections' has no attribute 'Callable'
#  with Collections.Callable and Python 3.10
#  Source: https://github.com/udacity/FSND/issues/167
import collections
import collections.abc
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)

# TODO DONE: connect to a local postgresql database. SEE Models.py

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value) 
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

# Define datetime now to avoid get this over and over in a loop!
now = datetime.now()

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
  # TODO DONE: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues_in_database = Venue.query.all()

  data = []

  cities_states = set()
  for venue in venues_in_database:
      cities_states.add( (venue.city, venue.state) )
  
  cities_states = list(cities_states)

  for location in cities_states:
    city = location[0]
    state = location[1]
    for venue in venues_in_database:
        if (venue.city == city) and (venue.state == state):

            shows_in_database = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > now).all()

            num_upcoming = len(shows_in_database)

            venue_data = [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming
            }]
    data.append({
        "city": city,
        "state": state,
        "venues": venue_data
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  '''This is the same as search_artist()'''
  
  search_term = request.form['search_term'].strip()

  venues_in_database = Venue.query.filter(Venue.name.ilike('%'+ search_term +'%')).all()

  data = list()
  num_upcoming_shows = 0
  
  for venue in venues_in_database:
    venue_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > now).all()

    num_upcoming_shows = len(venue_shows)

    data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
    })

  response = {
      "count": len(venues_in_database),
      "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO DONE: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    venue_show = {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    }

    if show.start_time < now:
      past_shows.append(venue_show)
    else:
      upcoming_shows.append(venue_show)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
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
  # TODO DONE: insert form data as a new Venue record in the db, instead
  # TODO DONE: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  form = VenueForm()

  venue = Venue(
    name = form.name.data,
    genres = form.genres.data,
    address = form.address.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data
  )

  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue '+ request.form['name'] +' was successfully listed!')

  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
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
  # TODO DONE: replace with real data returned from querying the database
  artists_in_database = Artist.query.all()

  data = list()

  for artist in artists_in_database:
    data.append({
      "id": artist.id,
      "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term'].strip() # added strip() to trim spaces

  artists_in_database = Artist.query.filter(Artist.name.ilike('%'+ search_term +'%')).all()

  artist_list = []
  
  for artist in artists_in_database:
    artist_shows = Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > now).all()

    artist_list.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(artist_shows)
    })

  response = {
      "count": len(artists_in_database),
      "data": artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO DONE: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)

  past_shows = list()
  upcoming_shows = list()

  for show in artist.shows:
    artist_show = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    }

    if show.start_time < now:
      past_shows.append(artist_show)
    else:
      upcoming_shows.append(artist_show)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
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
  # TODO DONE: populate form with fields from artist with ID <artist_id>

  artist = Artist.query.filter_by(id=artist_id).all()[0]

  # Passing existing data to form for update
  form.name.default = artist.name
  form.city.default = artist.city
  form.state.default = artist.state
  form.phone.default = artist.phone
  form.genres.default = artist.genres
  form.seeking_venue.default = artist.seeking_venue
  form.seeking_description.default = artist.seeking_description
  form.facebook_link.default = artist.facebook_link
  form.image_link.default = artist.image_link
  form.website_link.default = artist.website
  form.process() 

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:
    form = ArtistForm()

    artist = Artist.query.filter_by(id=artist_id).all()[0]
    artist.name=form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.genres=form.genres.data
    artist.seeking_description=form.seeking_description.data
    artist.seeking_venue=form.seeking_venue.data
    artist.facebook_link=form.facebook_link.data
    artist.image_link=form.image_link.data
    artist.website=form.website_link.data

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO DONE: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.name.default = venue.name
  form.genres.default = venue.genres
  form.address.default = venue.address
  form.city.default = venue.city
  form.state.default = venue.state
  form.phone.default = venue.phone
  form.website_link.default = venue.website
  form.facebook_link.default = venue.facebook_link
  form.seeking_talent.default = venue.seeking_talent
  form.seeking_description.default = venue.seeking_description
  form.image_link.default = venue.image_link
  form.process()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm()

    venue = Venue.query.get(venue_id)
    venue.name=form.name.data
    venue.genres=form.genres.data
    venue.address=form.address.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.phone=form.phone.data
    venue.website=form.website_link.data
    venue.facebook_link=form.facebook_link.data
    venue.seeking_talent=form.seeking_talent.data
    venue.seeking_description=form.seeking_description.data
    venue.image_link=form.image_link.data

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  except:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())
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
  # TODO DONE: insert form data as a new Venue record in the db, instead
  # TODO DONE: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  form = ArtistForm()

  artist = Artist(
    name = form.name.data,
    genres = form.genres.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    website = form.website_link.data,
    seeking_venue = form.seeking_venue.data,
    seeking_description = form.seeking_description.data,
    facebook_link = form.facebook_link.data,
    image_link = form.image_link.data
  )

  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist '+ request.form['name'] +' was successfully listed!')

  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO DONE: replace with real venues data.
  shows_in_database = Show.query.all()

  data = list()
  
  for show in shows_in_database:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO DONE: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = ShowForm()

  try:
    show = Show(
      artist_id = form.artist_id.data.strip(),
      venue_id = form.venue_id.data.strip(),
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  except Exception as e:
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
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
