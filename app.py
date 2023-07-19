#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show
from flask_migrate import Migrate
from babel import dates


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Models was moved to models.py
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(datetime, format='medium'):
    date = dateutil.parser.parse(datetime)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    formatted_date = dates.format_datetime(date, format=format, locale='en')
    return formatted_date

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
    # Query all venues from the database
    venues = Venue.query.all()

    # Create a dictionary to store the venue data grouped by city and state
    data = []
    
    # Iterate over the venues and group them by city and state
    for venue in venues:
        found = False
        for item in data:
            if item['city'] == venue.city and item['state'] == venue.state:
                item['venues'].append({
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': 0  # Placeholder for now, update as needed
                })
                found = True
                break
        if not found:
            data.append({
                'city': venue.city,
                'state': venue.state,
                'venues': [{
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_shows': 0  # Placeholder for now, update as needed
                }]
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Get the search term from the form data
    search_term = request.form.get('search_term', '')

    # Perform case-insensitive search for venues matching the search term
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    # Create the response data
    response = {
        "count": len(venues),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0  # Placeholder for now, update as needed
        } for venue in venues]
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # Retrieve the venue data based on the venue_id from the database or any other data source
    venue = Venue.query.get(venue_id)

    # Check if the venue exists
    if not venue:
        return render_template('errors/404.html')

    # Create the response data
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(',') if venue.genres else [],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "image_link": venue.image_link,
        "past_shows": [],  # Placeholder for now, update as needed
        "upcoming_shows": [],  # Placeholder for now, update as needed
        "past_shows_count": 0,  # Placeholder for now, update as needed
        "upcoming_shows_count": 0  # Placeholder for now, update as needed
    }
    
    if hasattr(venue, 'seeking_description'):
        data['seeking_description'] = venue.seeking_description
    else:
        data['seeking_description'] = None

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Get the form data
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')

    try:
        # Create a new Venue object
        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link
        )

        # Add the venue to the database session
        db.session.add(venue)

        # Commit the session to persist the changes
        db.session.commit()

        # Flash success message
        flash('Venue ' + str(name) + ' was successfully listed!')


        # Redirect to the homepage
        return redirect(url_for('index'))

    except Exception as e:
        print(e)
        # Rollback the session in case of any error
        db.session.rollback()

        # Flash error message
        flash('An error occurred. Venue ' +str(name) + ' could not be listed.')

        # Redirect to the homepage or an error page
        return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        # Find the venue with the given venue_id
        venue = Venue.query.get(venue_id)

        # Check if the venue exists
        if not venue:
            return jsonify({'message': 'Venue not found.'}), 404

        # Delete the venue from the database
        db.session.delete(venue)

        # Commit the session to persist the changes
        db.session.commit()

        # Return a success response
        return jsonify({'message': 'Venue deleted successfully.'}), 200

    except:
        # Rollback the session in case of any error
        db.session.rollback()

        # Return an error response
        return jsonify({'message': 'An error occurred. Venue could not be deleted.'}), 500


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # Retrieve artists from the database
    artists = Artist.query.all()

    # Create a list to store the artist data
    data = []

    # Iterate over the artists and populate the data list
    for artist in artists:
        artist_data = {
            "id": artist.id,
            "name": artist.name,
        }
        data.append(artist_data)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Get the search term from the form
    search_term = request.form.get('search_term', '')

    # Perform case-insensitive search on artists' names
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

    # Create a list to store the search results
    data = []

    # Iterate over the artists and populate the data list
    for artist in artists:
        artist_data = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": 0,  
        }
        data.append(artist_data)

    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Query the artist from the database using the artist_id
    artist = Artist.query.get(artist_id)

    # Check if the artist exists
    if artist:
        # Retrieve the artist's past shows
        past_shows = db.session.query(Show).join(Venue).filter(
            Show.artist_id == artist_id,
            Show.start_time < datetime.now()
        ).all()

        # Retrieve the artist's upcoming shows
        upcoming_shows = db.session.query(Show).join(Venue).filter(
            Show.artist_id == artist_id,
            Show.start_time >= datetime.now()
        ).all()

        # Convert the artist data to a dictionary
        data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.split(',') if artist.genres else [],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [],  # Placeholder for now, update as needed
        "upcoming_shows": [],  # Placeholder for now, update as needed
        "past_shows_count": 0,  # Placeholder for now, update as needed
        "upcoming_shows_count": 0,  # Placeholder for now, update as needed
        }

        # Populate the past shows data
        for show in past_shows:
            venue = show.venue
            past_show = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            }
            data["past_shows"].append(past_show)

        # Populate the upcoming shows data
        for show in upcoming_shows:
            venue = show.venue
            upcoming_show = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            }
            data["upcoming_shows"].append(upcoming_show)

        return render_template('pages/show_artist.html', artist=data)
    else:
        flash('Artist not found')
        return redirect(url_for('artists'))


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # Query the artist from the database using the artist_id
    artist = Artist.query.get(artist_id)

    # Check if the artist exists
    if artist:
        # Populate the form with artist data
        form.name.data = artist.name
        form.genres.data = artist.genres
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website_link.data = artist.website
        form.facebook_link.data = artist.facebook_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
        form.image_link.data = artist.image_link

        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
        flash('Artist not found')
        return redirect(url_for('artists'))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Retrieve the artist from the database
    artist = Artist.query.get(artist_id)

    # Check if the artist exists
    if artist:
        # Update the artist attributes with the form values
        artist.name = request.form['name']
        artist.genres = request.form.getlist('genres')
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.website = request.form['website_link']
        artist.facebook_link = request.form['facebook_link']
        artist.seeking_venue = 'seeking_venue' in request.form
        artist.seeking_description = request.form['seeking_description']
        artist.image_link = request.form['image_link']

        try:
            # Commit the changes to the database
            db.session.commit()
            flash('Artist ' + artist.name + ' was successfully updated!')
        except:
            # Handle any exceptions that occur during the database update
            db.session.rollback()
            flash('An error occurred. Artist ' + artist.name + ' could not be updated.')

        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        flash('Artist not found')
        return redirect(url_for('artists'))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # Retrieve the venue from the database
    venue = Venue.query.get(venue_id)

    # Check if the venue exists
    if venue:
        # Populate the form with the venue's attributes
        form.name.data = venue.name
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website_link.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
        form.image_link.data = venue.image_link

        return render_template('forms/edit_venue.html', form=form, venue=venue)
    else:
        flash('Venue not found')
        return redirect(url_for('venues'))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Retrieve the venue from the database
    venue = Venue.query.get(venue_id)

    # Check if the venue exists
    if venue:
        # Update the venue's attributes with the form values
        venue.name = request.form['name']
        venue.genres = request.form.getlist('genres')
        venue.address = request.form['address']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.phone = request.form['phone']
        venue.website = request.form['website_link']
        venue.facebook_link = request.form['facebook_link']
        venue.seeking_talent = 'seeking_talent' in request.form
        venue.seeking_description = request.form['seeking_description']
        venue.image_link = request.form['image_link']

        # Commit the changes to the database
        db.session.commit()

        flash('Venue successfully updated!')
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        flash('Venue not found')
        return redirect(url_for('venues'))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # Retrieve form data
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    website = request.form.get('website', '')  # Use get() with a default value
    facebook_link = request.form['facebook_link']
    seeking_venue = 'seeking_venue' in request.form
    seeking_description = request.form['seeking_description']
    image_link = request.form['image_link']

    # Create a new Artist instance with the form data
    new_artist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        genres=genres,
        website=website,
        facebook_link=facebook_link,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description,
        image_link=image_link
    )

    try:
        # Add the new artist to the database
        db.session.add(new_artist)
        db.session.commit()

        # Flash success message
        flash('Artist ' + new_artist.name + ' was successfully listed!')
        return render_template('pages/home.html')
    except:
        # Rollback the changes if an error occurs
        db.session.rollback()

        # Flash error message
        flash('An error occurred. Artist ' + name + ' could not be listed.')
        return render_template('pages/home.html')




#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # Retrieve the list of shows from the database
    shows = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()

    # Create a list to store the show data
    data = []

    # Iterate over each show and extract the required information
    for show in shows:
        show_data = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)  # Convert datetime object to string
        }
        data.append(show_data)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

from datetime import datetime
from forms import ShowForm  # Import the ShowForm

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # Create an instance of the ShowForm and populate it with the form data
    form = ShowForm(request.form)

    if form.validate():
        try:
            # Create a new Show object using the form data
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )

            # Add the show to the session and commit the changes to the database
            db.session.add(show)
            db.session.commit()

            # on successful db insert, flash success
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
        except Exception as e:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            flash('An error occurred. Show could not be listed: {}'.format(str(e)))
            db.session.rollback()
            return render_template('pages/home.html')
        finally:
            db.session.close()
    else:
        # Handle form validation errors
        flash(form.errors)
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
