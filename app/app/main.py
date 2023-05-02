import logging
import os
import signal
import sys
import textwrap
import traceback
from datetime import datetime

from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

from .helpers.db import get_data, set_data, guess, just_end_it_all
from .helpers.flight import get_metar, get_taf, get_fuel, get_route

WRAP_WIDTH = 65

dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=f"{dir_path}/logs/app.log", level=logging.INFO)


def sigterm_handler(s, frame):
    just_end_it_all()
    sys.exit(0)


if os.environ.get('FLASK_ENV') != "development":
    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGQUIT, sigterm_handler)

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status')
def status():
    return jsonify({})


@app.route('/data', methods=['GET'])
def data():
    return jsonify(get_data(request.args.get('thing')))


@app.route('/guess', methods=['GET'])
def make_guess():
    guess(request.args.get('username'), request.args.get('speed'))
    return "OK"


@app.route('/choose_winner', methods=['GET'])
def choose_winner():
    # do stuff here
    return "OK"


@app.route('/in', methods=['GET'])
def put():
    set_data(request.args.get('nam'), request.args.get('val'))
    return "OK"


@app.route('/marquee/map', methods=['GET'])
def marquee_map():
    return render_template('marquee_map.html')


@app.route('/plan', methods=['POST'])
def plan():
    """fetch the page for the plans we care about"""
    origin = request.form['origin']
    dest = request.form['destination']

    try:
        flight_plan = get_route(origin, dest)
        route = "\n".join(textwrap.wrap(flight_plan['route'], WRAP_WIDTH))
        flight_levels = flight_plan['flight_levels']
        distance = flight_plan['distance']

        origin_weather = "\n".join(textwrap.wrap(get_metar(origin), WRAP_WIDTH))
        dest_weather = "\n".join(textwrap.wrap(get_metar(dest), WRAP_WIDTH))

        origin_taf = "\n".join(textwrap.wrap(get_taf(origin), WRAP_WIDTH))
        dest_taf = "\n".join(textwrap.wrap(get_taf(dest), WRAP_WIDTH))

        fuel = get_fuel(origin, dest)

        set_data('rte', route)
        set_data('dep', origin)
        set_data('arr', dest)

        return render_template('plan.html',
                               origin=origin,
                               dest=dest,
                               flight_levels=flight_levels,
                               distance=distance,
                               requested_at=str(datetime.now()),
                               origin_weather=origin_weather,
                               dest_weather=dest_weather,
                               origin_taf=origin_taf,
                               dest_taf=dest_taf,
                               fuel=fuel,
                               route=route)

    except Exception as e:
        return render_template('error.html', e=traceback.format_exc())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8888)
