# -*- coding: utf-8 -*-

import functools
import logging

import flask
import google.oauth2.credentials
import googleapiclient.discovery
from authlib.client import OAuth2Session

from smart_blinds.actions import Actions
from smart_blinds.slack import Slack
from smart_blinds.smart_blinds import SmartBlinds
from smart_blinds.utils import (find_channel_by_user_name, get_room_id_map,
                                get_user_name, logger_message,
                                validate_command)

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE = 'openid email profile'

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'
USER_INFO_KEY = 'user_info'

app = flask.Flask(__name__, instance_relative_config=True)
app.logger.setLevel(logging.INFO)
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.secret_key = app.config['FN_FLASK_SECRET_KEY']

AUTH_REDIRECT_URI = app.config['AUTH_REDIRECT_URI']
BASE_URI = app.config['BASE_URI']
CLIENT_ID = app.config['CLIENT_ID']
CLIENT_SECRET = app.config['CLIENT_SECRET']
CHANNELS = app.config["CHANNELS"]
DATA = app.config["DATA"]
DEBUG = app.config["DEBUG"]
ADMIN_EMAILS = app.config['ADMIN_EMAILS']

app.logger.info('Loading data from file: ' + DATA)
room_id_map = get_room_id_map(DATA)

smart_blinds = SmartBlinds(CHANNELS, DEBUG)

slack = Slack(app, room_id_map, CHANNELS, smart_blinds, DEBUG)
slack.start()

def render_slack_help():
    return 'Slack commands currently support only automatic mode. For more control see <{0}/blinds>'.format(BASE_URI)


def get_param(key):
    result = flask.request.args.get(key)

    print(key)
    print(result)
    if not result:
        result = flask.request.form.get(key)
    return result


def is_logged_in():
    return True if AUTH_TOKEN_KEY in flask.session else False


def build_credentials():
    if not is_logged_in():
        raise AssertionError('User must be logged in')

    oauth2_tokens = flask.session[AUTH_TOKEN_KEY]

    return google.oauth2.credentials.Credentials(
        oauth2_tokens['access_token'],
        refresh_token=oauth2_tokens['refresh_token'],
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri=ACCESS_TOKEN_URI)


def get_user_info():
    if USER_INFO_KEY in flask.session:
        return flask.session[USER_INFO_KEY]

    credentials = build_credentials()

    oauth2_client = googleapiclient.discovery.build(
        'oauth2', 'v2',
        credentials=credentials)

    user_info = oauth2_client.userinfo().get().execute()
    flask.session[USER_INFO_KEY] = user_info

    return user_info


def render_user_card_section(is_allowed_domain, is_admin, email, link):
    text = ''
    text += '<div class="Polaris-Card__Section">\n'
    text += '<div class="Polaris-Stack">\n'
    if is_admin:
        text += '<div class="Polaris-Stack__Item"><span class="Polaris-Badge Polaris-Badge--statusAttention"><span class="Polaris-VisuallyHidden">Attention</span>Admin</span></div>\n'

    email_badge = 'statusSuccess' if is_allowed_domain else 'statusAttention'
    text += '<div class="Polaris-Stack__Item"><span class="Polaris-Badge Polaris-Badge--{0}"><span class="Polaris-VisuallyHidden">Email</span>{1}</span></div>\n'.format(
        email_badge, email)
    text += '<div class="Polaris-Stack__Item"><a class="Polaris-Link" href="{0}">{1}</a></div>\n'.format(
        link[1], link[0])
    text += '<div class="Polaris-Stack__Item"><a class="Polaris-Link" href="/google/logout">Logout</a></div>\n'
    text += '</div>\n'
    text += '</div>\n'

    return text


def render_channel_card_section(key, channel, is_admin, is_allowed_domain):
    label = channel['label']

    text = ''
    text += '<div class="Polaris-Card__Section">\n'
    text += '<div class="Polaris-Card__SectionHeader">\n'
    text += '<h3 class="Polaris-Subheading">{0}</h3>\n'.format(label)
    text += '</div>\n'

    text += '<div class="Polaris-ButtonGroup">\n'

    for action in [Actions.OPEN, Actions.CLOSE, Actions.STOP]:
        url = '/blinds/ajax/' + action + '?channel_name=' + key

        if is_admin or is_allowed_domain:
            text += '<div class="Polaris-ButtonGroup__Item"><button type="button" class="Polaris-Button" onclick="command(\'{0}\')"><span class="Polaris-Button__Content"><span class="Polaris-Button__Text">{1}</span></span></button></div>\n'.format(
                url, action)
        else:
            text += '<div class="Polaris-ButtonGroup__Item"><button type="button" class="Polaris-Button Polaris-Button--disabled" disabled><span class="Polaris-Button__Content"><span class="Polaris-Button__Text">{0}</span></span></button></div>\n'.format(
                action)

    text += '</div>\n'
    text += '</div>\n'

    return text


def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)


@app.route('/', methods=['GET'])
def api_root():
    text = ''
    text += '<div class="Polaris-Card__Header">\n'
    text += '<h2 class="Polaris-Heading">Main</h2>\n'
    text += '</div>\n'

    if is_logged_in():
        user_info = get_user_info()
        is_admin = user_info['email'] in ADMIN_EMAILS
        is_allowed_domain = user_info['email'].endswith(
            app.config['ALLOWED_EMAIL_DOMAIN'])

        channel_name = None
        user_name = get_user_name(user_info['email'])
        user_email = user_info['email']

        try:
            channel_name = find_channel_by_user_name(
                room_id_map, CHANNELS, user_name)
        except AssertionError as exception:
            app.logger.warning(logger_message(user_email, exception))
            text += '<div class="Polaris-Card__Section">\n'
            text += '<p class="error">{0}</p>\n'.format(str(exception))
            text += '</div>\n'

        text += render_user_card_section(is_allowed_domain,
                                         is_admin, user_email, ('Channel list', '/blinds'))

        if not channel_name is None:
            channel = app.config['CHANNELS'][channel_name]
            text += render_channel_card_section(
                channel_name, channel, is_admin, is_allowed_domain)

    else:
        text += '<div class="Polaris-Card__Section">\n'
        text += '<p><a href="/google/login">Login</a></p>'
        text += '</div>\n'

    return flask.render_template("main.html", main=text)


@app.route('/blinds', methods=['GET', 'POST'])
def api_blinds_main():
    if not is_logged_in():
        return flask.redirect(flask.url_for('api_root'), code=302)

    user_info = get_user_info()
    is_admin = user_info['email'] in app.config['ADMIN_EMAILS']
    is_allowed_domain = user_info['email'].endswith(
        app.config['ALLOWED_EMAIL_DOMAIN'])
    user_email = user_info['email']

    text = ''
    text += '<div class="Polaris-Card__Header">\n'
    text += '<h2 class="Polaris-Heading">Channel list</h2>\n'
    text += '</div>\n'

    text += render_user_card_section(is_allowed_domain,
                                     is_admin, user_email, ('Main', '/'))

    for key, channel in sorted(CHANNELS.items()):
        text += render_channel_card_section(key, channel,
                                            is_admin, is_allowed_domain)

    return flask.render_template("blinds.html", channels_html=text)


@app.route('/blinds/ajax/<action>', methods=["GET"])
def api_blinds_ajax_control(action):
    if not is_logged_in():
        return 'Not authorised!', 403

    user_info = get_user_info()
    is_admin = user_info['email'] in ADMIN_EMAILS
    is_allowed_domain = user_info['email'].endswith(
        app.config['ALLOWED_EMAIL_DOMAIN'])

    user_email = user_info['email']
    user_name = get_user_name(user_info['email'])

    if not is_admin and not is_allowed_domain:
        return 'Not authorised!', 403

    channel_name = flask.request.args.get('channel_name')

    if channel_name == '':
        channel_name = None

    try:
        app.logger.info(logger_message(
            user_email, 'action: {0} channel: {1}'.format(action, channel_name)))

        channel_name = find_channel_by_user_name(
            room_id_map, CHANNELS, user_name)

        message = validate_command(CHANNELS, action, channel_name)
        smart_blinds.command(action, channel_name)
    except AssertionError as exception:
        app.logger.warning(logger_message(user_email, exception))
        return str(exception), 400

    return flask.jsonify({'message': message})


@app.route('/blinds/slack/<action>', methods=["GET", "POST"])
def api_blinds_slack_control(action):
    channel_name = get_param('text')
    token = get_param('token')
    user_id = get_param('user_id')
    user_name = get_param('user_name')
    response_url = get_param('response_url')

    if channel_name == '':
        channel_name = None

    try:
        if token != app.config['SLACK_VERIFICATION_TOKEN']:
            raise AssertionError('Invalid slack verification token.')

        if action == 'help':
            return render_slack_help()

        slack.queue.put({
            'action': action, 
            'channel_name': channel_name,
            'user_name': user_name,
            'user_id': user_id,
            'response_url': response_url
        })

        return ''
    except AssertionError as exception:
        app.logger.warning(logger_message(user_name, exception))
        return str(exception), 400


@app.route('/google/login')
@no_cache
def login():
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)

    uri, state = session.authorization_url(AUTHORIZATION_URL)

    flask.session[AUTH_STATE_KEY] = state
    flask.session.permanent = True

    return flask.redirect(uri, code=302)


@app.route('/google/auth')
@no_cache
def google_auth_redirect():
    req_state = flask.request.args.get('state', default=None, type=None)

    if req_state != flask.session[AUTH_STATE_KEY]:
        response = flask.make_response('Invalid state parameter', 401)
        return response

    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            state=flask.session[AUTH_STATE_KEY],
                            redirect_uri=AUTH_REDIRECT_URI)

    oauth2_tokens = session.fetch_access_token(
        ACCESS_TOKEN_URI,
        authorization_response=flask.request.url)

    flask.session[AUTH_TOKEN_KEY] = oauth2_tokens

    get_user_info()

    return flask.redirect(BASE_URI, code=302)


@app.route('/google/logout')
@no_cache
def logout():
    flask.session.pop(AUTH_TOKEN_KEY, None)
    flask.session.pop(AUTH_STATE_KEY, None)
    flask.session.pop(USER_INFO_KEY, None)

    return flask.redirect(BASE_URI, code=302)
