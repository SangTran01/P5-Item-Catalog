from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
# import request to get data from form
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string

from database_setup import Base, User, Collection, ArtWork

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Artwork Collection Application"


engine = create_engine('sqlite:///artcollections.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# LOGIN ROUTE


@app.route('/login')
def showLogin():
    print "STARTING LOGIN"
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# GPLUS login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # STEP3.1 FLOW Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # STEP 3.2 FLOW exchange code for token
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is'
                                            ' already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    # login_session['credentials'] = credentials
    # login_session['gplus_id'] = gplus_id
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Add provider to Login session
    login_session['provider'] = 'google'

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # SEE if user exists, if not make a new one
    user_id = getUserID(data['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius: 150px;"'
               '"-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Facebook LOGIN


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&'
           'client_secret=%s&fb_exchange_token=%s') % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.6/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.6/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = ('https://graph.facebook.com/v2.6/me/picture?%s&'
           'redirect=0&height=200&width=200') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;"'
               '"border-radius: 150px;-webkit-border-radius: 150px;"'
               '"-moz-border-radius: 150px;"> ')

    flash("Now logged in as %s" % login_session['username'])
    return output

# Handle Google logout
# DISCONNECT - Revoke a current user's token and reset their login_session.


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Handle Facebook Logout
# DISCONNECT


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect based on provider and redirect to main page


@app.route('/disconnect')
def disconnect():
    """
    disconnect : Disconnect user based on provider
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCollections'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCollections'))

# JSON APIs to view Artwork Collection information


@app.route('/collections/JSON')
def collectionsJSON():
    collections = session.query(Collection).order_by(
        desc(Collection.name)).all()
    return jsonify(collections=[c.serialize for c in collections])


@app.route('/collections/<int:collection_id>/JSON')
def artInCollectionsJSON(collection_id):
    collection = session.query(Collection).filter_by(id=collection_id).one()
    artworks = session.query(ArtWork).filter_by(
        collection_id=collection_id).all()
    return jsonify(artworks=[a.serialize for a in artworks])


@app.route('/collections/<int:collection_id>/artwork/<int:artwork_id>/JSON')
def artworkJSON(collection_id, artwork_id):
    artwork = session.query(ArtWork).filter_by(id=artwork_id).one()
    return jsonify(artwork=artwork.serialize)


# MAIN ROUTE
@app.route('/')
@app.route('/collections/')
def showCollections():
    collections = session.query(Collection).order_by(
        desc(Collection.name)).all()
    artworks = session.query(ArtWork).all()
    return render_template('collections.html', collections=collections,
                           artworks=artworks, login_session=login_session)


# individual collections
@app.route('/collections/<int:collection_id>/')
@app.route('/collections/<int:collection_id>/artwork/')
def showArtWorks(collection_id):
    collection = session.query(Collection).filter_by(id=collection_id).one()
    artworks = session.query(ArtWork).filter_by(
        collection_id=collection_id).all()
    creator = session.query(User).filter_by(id=collection.user_id).one()
    return render_template("artworks.html", collection=collection,
                           artworks=artworks, creator=creator,
                           login_session=login_session)


# new collection
@app.route('/collections/new/', methods=['GET', 'POST'])
def newCollection():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        collection = Collection(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(collection)
        session.commit()
        flash("You just created collection %s." % collection.name)
        return redirect(url_for('showCollections',
                                login_session=login_session))
    else:
        return render_template('newcollection.html',
                               login_session=login_session)

# Edit Collection


@app.route('/collections/<int:collection_id>/edit/', methods=['GET', 'POST'])
def editCollection(collection_id):
    if 'username' not in login_session:
        return redirect('/login')
    collection = session.query(Collection).filter_by(id=collection_id).one()
    creator = session.query(User).filter_by(id=collection.user_id).one()
    if creator.id != login_session['user_id']:
        flash("HOLD UP!! You can only edit your own collection")
        return redirect('/collections/')
    if request.method == 'POST':
        if request.form['name']:
            collection.name = request.form['name']
            session.add(collection)
            session.commit()
            flash("Successfully Edited %s." % collection.name)
            return redirect(url_for('showCollections',
                                    login_session=login_session))
    else:
        return render_template('editcollection.html',
                               collection=collection,
                               login_session=login_session)


# Delete Collection
@app.route('/collections/<int:collection_id>/delete/', methods=['GET', 'POST'])
def deleteCollection(collection_id):
    if 'username' not in login_session:
        return redirect('/login')
    collection = session.query(Collection).filter_by(id=collection_id).one()
    creator = session.query(User).filter_by(id=collection.user_id).one()
    if creator.id != login_session['user_id']:
        flash("HOLD UP!! You can only delete your own collection")
        return redirect('/collections/')
    if request.method == 'POST':
        session.delete(collection)
        session.commit()
        flash("Successfully Deleted %s." % collection.name)
        return redirect(url_for('showCollections',
                                login_session=login_session))
    else:
        return render_template('deletecollection.html',
                               collection=collection,
                               login_session=login_session)


# new artwork
@app.route('/collections/<int:collection_id>/new/', methods=['GET', 'POST'])
def newArtWork(collection_id):
    if 'username' not in login_session:
        return redirect('/login')
    collection = session.query(Collection).filter_by(id=collection_id).one()
    creator = session.query(User).filter_by(id=collection.user_id).one()
    if creator.id != login_session['user_id']:
        flash("HOLD UP!! You can't do that!!")
        return redirect('/collections/%s/' % collection.id)
    if request.method == 'POST':
        artwork = ArtWork(name=request.form['name'],
                          description=request.form['description'],
                          price=request.form['price'],
                          picture=request.form['picture'],
                          collection_id=collection_id,
                          user_id=collection.user_id)
        session.add(artwork)
        session.commit()
        flash('Artwork %s Successfully Created' % (artwork.name))
        return redirect(url_for('showArtWorks', collection_id=collection_id,
                                login_session=login_session))
    else:
        return render_template('newartwork.html', collection_id=collection_id,
                               login_session=login_session)


# edit artwork
@app.route('/collections/<int:collection_id>/artwork/<int:artwork_id>/edit',
           methods=['GET', 'POST'])
def editArtWork(collection_id, artwork_id):
    if 'username' not in login_session:
        return redirect('/login')
    collection = session.query(Collection).filter_by(id=collection_id).one()
    editedArtwork = session.query(ArtWork).filter_by(id=artwork_id).one()
    creator = session.query(User).filter_by(id=collection.user_id).one()
    if creator.id != login_session['user_id']:
        flash("HOLD UP!! You can only edit your own artworks")
        return redirect('/collections/%s/' % collection.id)
    if request.method == "POST":
        if request.form['name']:
            editedArtwork.name = request.form['name']
        if request.form['description']:
            editedArtwork.description = request.form['description']
        if request.form['picture']:
            editedArtwork.picture = request.form['picture']
        if request.form['price']:
            editedArtwork.price = request.form['price']
        session.add(editedArtwork)
        session.commit()
        flash('Artwork %s Successfully Edited' % editedArtwork.name)
        return redirect(url_for('showArtWorks',
                                collection_id=collection_id,
                                login_session=login_session))
    else:
        return render_template('editartwork.html',
                               collection_id=collection_id,
                               artwork_id=artwork_id,
                               editedArtwork=editedArtwork,
                               login_session=login_session)


# delete artwork
@app.route('/collections/<int:collection_id>/artwork/<int:artwork_id>/delete',
           methods=['GET', 'POST'])
def deleteArtWork(collection_id, artwork_id):
    if 'username' not in login_session:
        return redirect('/login')
    collection = session.query(Collection).filter_by(id=collection_id).one()
    deletedArtwork = session.query(ArtWork).filter_by(id=artwork_id).one()
    creator = session.query(User).filter_by(id=collection.user_id).one()
    if creator.id != login_session['user_id']:
        flash("HOLD UP!! You can only delete your own artworks")
        return redirect('/collections/%s/' % collection.id)
    if request.method == 'POST':
        session.delete(deletedArtwork)
        session.commit()
        flash('Artwork Successfully Deleted')
        return redirect(url_for('showArtWorks',
                                collection_id=collection_id,
                                login_session=login_session))
    else:
        return render_template('deleteartwork.html',
                               collection_id=collection_id,
                               artwork_id=artwork_id,
                               deletedArtwork=deletedArtwork,
                               login_session=login_session)


# Create a new user
def createUser(login_session):
    """
    createUser : Create a new user from session
    Args:
      login_session (dict): session dictionary
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Get a user from user_id


def getUserInfo(user_id):
    """
    getUserInfo : Get user info for a user id
    Args:
      user_id (int): user id
    """
    user = session.query(User).get(user_id)
    return user


# get a user from email address
def getUserID(email):
    """
    getUserID : Get user info from an email address
    Args:
      email (string): user's email address
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
