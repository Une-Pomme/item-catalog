#!/usr/bin/env python
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Category, Base, Item, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import requests
import httplib2
import json
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response


app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

engine = create_engine('sqlite:///catalogwithusers.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def createUser(login_session):
    """ Adds a user's info to the user table in the database

    Args:
        login_session: session object with user data

    Returns:
        user.id: a unique integer value that identifies the user
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """ Get's a user's info from the database

    Args:
        user_id: an integer value associated with the user

    Returns:
        An object with the user's database info
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """ Gets a user's ID from the database

    Args:
        email: a string value that is associated with a user

    Returns:
        on NoResultFound exception: None
        a user id if the email is in the database
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


# Displays the front page of the catalog web app
@app.route('/')
@app.route('/catalog/')
def catalogDisplay():
    categories = session.query(Category).order_by(Category.name).all()
    items = session.query(Item).join(Category).order_by(desc(Item.id)).limit(5)
    return render_template('catalog.html',
                           categories=categories,
                           lastestItems=items)


# Displays all the catalog items as a JSON object
@app.route('/catalog.json')
def getJSONEndpointAll():
    categories = session.query(Category).all()
    return jsonify(category=[c.serialize for c in categories])


# Displays a specific catalog item as a JSON object
@app.route('/item_<item_id>.json')
def getJSONEndpointSpecificItem(item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
        return jsonify(item=item.serialize)
    except NoResultFound:
        return "{'error': 'No item with that id exists in the catalog'}"


# Adds a new item to the catalog if logged in
@app.route('/catalog/new-item', methods=['GET', 'POST'])
def addNewItem():
    """ Creates a new item and adds it to the catalog

    Returns:
        on GET: the web form to create a new object
        on POST: add the new item to catalog and then redirect to main page
        Redirect to login page when user is not signed in
    """
    if 'username' not in login_session:
        flash("You need to be logged in to create an item")
        return redirect(url_for('showLogin'))
    if request.method == 'POST':
        if request.form['item-name']:
            newItem = Item(name=request.form['item-name'],
                           description=request.form['item-description'],
                           category_id=request.form['categories-list'],
                           user_id=login_session['user_id'])
            session.add(newItem)
            flash('%s has been added to the catalog!' % newItem.name)
            session.commit()
            return redirect(url_for('catalogDisplay'))
    else:
        categories = session.query(Category).order_by(Category.name).all()
        return render_template('new-item-form.html', categories=categories)


# Deletes an item from the catalog if logged in
@app.route('/catalog/delete/<item_id>', methods=['GET', 'POST'])
def deleteItem(item_id):
    """ Deletes an item from the database (if the user created it)

    Args:
        item_id: an integer value that identifies the item

    Returns:
        on GET: a deletion confirmation page
        on POST: delete the item from the database and then
        redirect to main page
        Redirect to login page when user is not signed in
        Alert user if they did not create item
    """
    if 'username' not in login_session:
        flash("You need to be logged in to delete an item")
        return redirect(url_for('showLogin'))
    item = session.query(Item).filter_by(id=item_id).one()
    if item.user_id != login_session['user_id']:
        alert = "<script>function myFunction(){"
        alert += "alert('You are not authorized to delete this item!');}"
        alert += "</script><body onload='myFunction()'>"
        return alert
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('%s has been removed!' % item.name)
        return redirect(url_for('catalogDisplay'))
    else:
        referer = request.headers.get("Referer")
        return render_template(
                               'delete-item.html',
                               item=item,
                               referer=referer)


# Edits an item in the catalog if logged in
@app.route('/catalog/edit/<item_id>', methods=['GET', 'POST'])
def editItem(item_id):
    """ Edits an item in the database (if the user created it)

    Args:
        item_id: an integer value that identifies the item

    Returns:
        on GET: a web form to edit the item
        on POST: update item in the database and then redirect to the item page
        Redirect to login page when user is not signed in
        Alert user if they did not create item
    """
    if 'username' not in login_session:
        flash("You need to be logged in to edit an item")
        return redirect(url_for('showLogin'))

    item = session.query(Item).filter_by(id=item_id).one()
    if item.user_id != login_session['user_id']:
        alert = "<script>function myFunction(){"
        alert += "alert('You are not authorized to delete this item!');}"
        alert += "</script><body onload='myFunction()'>"
        return alert
    if request.method == 'POST':
        if request.form['item-name']:
            item.name = request.form['item-name']
        if request.form['item-description']:
            item.description = request.form['item-description']
        if request.form['categories-list']:
            item.category_id = request.form['categories-list']
        category_name = session.query(Category).filter_by(
                                        id=item.category_id).one().name
        session.add(item)
        session.commit()
        flash('Item has been edited!')
        return redirect(url_for(
                                'displaySpecificItem',
                                category_name=category_name,
                                item_name=item.name,
                                item_id=item_id))
    else:
        categories = session.query(Category).order_by(Category.name).all()
        return render_template('edit-item-form.html',
                               item=item,
                               categories=categories)


# Display a login page
@app.route('/login')
@app.route('/catalog/login')
def showLogin():
    """ Login page for user

    Returns:
        The login page
    """
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Logs in via Google Accounts
# Taken from project.py in Full-Stack Foundations Udacity Course
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200
            )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Log a user out
@app.route('/disconnect')
def disconnect():
    """ Log out a user and delete their login session info

    Returns:
        Redirect user to the main page
    """
    if 'provider' in login_session:
        gdisconnect()
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('catalogDisplay'))
    else:
        flash("You were not logged in")
        return redirect(url_for('catalogDisplay'))


# Log out a user via Google
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400)
            )
        response.headers['Content-Type'] = 'application/json'
        return response


# Displays the items in a category
@app.route('/catalog/<category_name>/')
@app.route('/catalog/<category_name>/Items/')
def displayCategoryItems(category_name):
    """ Display all the items in a category

    Args:
        category_name: the name of the category

    Returns:
        A category page that contains all the items
        associated with that category
    """
    categories = session.query(Category).order_by(Category.name).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template(
        'category.html',
        category_name=category_name,
        items=items,
        categories=categories)


# Displays the name and description of an item
@app.route('/catalog/<category_name>/<item_name>/<item_id>')
def displaySpecificItem(category_name, item_name, item_id):
    """ Display info and operations associated with the item

    Args:
        category_name: the string value containing
        the category the item belongs to
        item_name: the string value of the item's name
        item_id: the integer value that identifies the item in the database

    Returns:
        A page with the name, category and description of that item
        If user is logged in and created the item,
        the options to edit and delete the item with be available
    """
    ownsItem = False
    item = session.query(Item).filter_by(id=item_id).one()
    if 'username' in login_session and item.user_id == login_session['user_id']:
        ownsItem = True
    return render_template(
            'specific-item.html',
            category_name=category_name,
            item_name=item_name,
            item=item,
            ownsItem=ownsItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
