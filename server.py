# -*- coding: utf-8 -*-

from flask import jsonify, render_template, request, Flask

from smart_blinds.actions import Actions
from smart_blinds.smart_blinds import SmartBlinds

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

smart_blinds = SmartBlinds(app.config)


@app.route('/', methods=['GET'])
def api_root():
    text = '<a href="{0}blinds">{0}blinds/(open|close|stop)</a>'.format(request.url)

    return render_template("main.html", main=text)

@app.route('/blinds', methods=['GET', 'POST'])
def api_blinds_main():
    text = ''

    for key, channel in sorted(app.config['CHANNELS'].items()):
        label = channel['label']

        text += '<div class="Polaris-Card__Section">\n'
        text += '<div class="Polaris-Card__SectionHeader">\n'
        text += '<h3 class="Polaris-Subheading">{0}</h3>\n'.format(label)
        text += '</div>\n'

        text += '<div class="Polaris-ButtonGroup">\n'

        for action in [Actions.OPEN, Actions.CLOSE, Actions.STOP, 'bad']:
            url = '/blinds/' + action + '?channel_name=' + key

            text += '<div class="Polaris-ButtonGroup__Item"><button type="button" class="Polaris-Button" onclick="command(\'{0}\')"><span class="Polaris-Button__Content"><span class="Polaris-Button__Text">{1}</span></span></button></div>\n'.format(url, action)

        text += '</div>\n'
        text += '</div>\n'
    text += ''

    return render_template("blinds.html", channels_html=text)


@app.route('/blinds/<action>', methods=["GET", "POST"])
def api_blinds_control(action):
    if request.form.get('channel_name'):
        channel_name = request.form.get('channel_name')
    else:
        channel_name = request.args.get('channel_name')

    user_name = request.form.get('user_name')

    try:
        message = smart_blinds.command(action, channel_name, user_name)
    except Exception as exception:
        return str(exception), 400

    return jsonify({'message': message})
