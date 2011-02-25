# -*- coding: utf-8 -*-
import time
from flask import (Module, request, session, url_for, redirect,
    render_template, abort, g, flash)
from werkzeug import check_password_hash, generate_password_hash  # XXX
from models import User, Message, Follower
from syrinx import app
from syrinx.models import db
from syrinx.forms import FollowForm

# app = Module(__name__, 'views')


@app.before_request
def before_request():
    """Make sure we are connected to the database each request and look
    up the current user so that we know he's there.
    """
    g.user = None
    if 'username' in session:
        g.user = User.query.get((session['username'], ''))


@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    # import pdb; pdb.set_trace()
    if not g.user:
        return redirect(url_for('public_timeline'))
    return render_template('timeline.html',
        messages=Message.query.filter_by(author=session['username']),
        users=User.query.all())

    # ============================================================= #
    #                                                               #
    # return render_template('timeline.html', messages=query_db(''' #
    #     select message.*, user.* from message, user               #
    #     where message.author_id = user.user_id and (              #
    #         user.user_id = ? or                                   #
    #         user.user_id in (select whom_id from follower         #
    #                                 where who_id = ?))            #
    #     order by message.pub_date desc limit ?''',                #
    #     [session['user_id'], session['user_id'], PER_PAGE]))      #
    #                                                               #
    # ============================================================= #


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=Message.query.all(),
        users=User.query.all())


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = User.query.get_or_404((username, ''))
    followed = False
    if g.user:
        followed = Follower.query.get((session['username'],
            profile_user.username,)) is not None
    return render_template('timeline.html',
        messages=Message.query.filter_by(
            author=profile_user.username).order_by(
                'date_publish')[:app.config['PER_PAGE']],
        followed=followed, profile_user=profile_user)
        # ======================================================== #
        #                                                          #
        # select message.*, user.* from message, user where        #
        # user.user_id = message.author_id and user.user_id = ?    #
        # order by message.pub_date desc limit ?''',               #
        # [profile_user['user_id'], PER_PAGE]), followed=followed, #
        # profile_user=profile_user)                               #
        #                                                          #
        # ======================================================== #


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        redirect(url_for('follow_remote', username=username))
    user = User.query.get_or_404((g.user.username, ''))
    whom = User.query.get_or_404((username, ''))
    follower = Follower(who=user, whom=whom)
    db.session.add(follower)
    db.session.commit()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/follow/remote', methods=['GET', 'POST'])
def follow_remote(username):
    """Asks for the user's credentials to notify his/her service provider of
    the subscription."""
    user = User.query.get_or_404((username, ''))
    form = FollowForm()
    if form.validate_on_submit():
        print('valid!')  # DEBUG
        import logging  # DEBUG
        logging.debug('valid!')  # DEBUG
        username, server = form.account.split('@')
        remote_user = User(username=username, server=server)
        db.session.add(remote_user)
        db.session.commit()
        # FIXME: Mandarlo a confirmar a su servidor.
    return render_template('follow_remote.html', form=form, user=user)


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    user = User.query.get_or_404((username, ''))
    whom = user.username
    follower = Follower.query.get((session['username'], whom,))
    db.session.delete(follower)
    db.session.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add-message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'username' not in session:
        abort(401)
    if request.form['text']:
        message = Message(author=session['username'],
            text=request.form['text'])
        db.session.add(message)
        db.session.commit()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = User.query.get((request.form['username'], ''))
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user._password, request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['username'] = user.username
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif not User.query.filter_by(username=request.form['username']):
            error = 'The username is already taken'
        else:
            user = User(
                username=request.form['username'],
                password=request.form['password'],
                email=request.form['email'])
            db.session.add(user)
            db.session.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('username', None)
    return redirect(url_for('public_timeline'))
