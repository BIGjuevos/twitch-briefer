import os
import textwrap
from datetime import datetime

from flask import Flask, request, render_template, jsonify

from .helpers.db import get_data, set_data
from .helpers.flight import get_metar, get_taf, get_fuel, get_route

WRAP_WIDTH = 65

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/status')
def status():
    return jsonify({})


@app.route('/fly')
def fly():
    return render_template('fly.html',
                           twitch_client_id=os.environ['TWITCH_CLIENT_ID'])


@app.route('/forge')
def forge():
    return render_template('forge.html',
                           twitch_client_id=os.environ['TWITCH_CLIENT_ID'])


@app.route('/map')
def map():
    if request.args.get('raw') is not None:
        return render_template('raw_map.html',
                               access_token=os.environ['MAPBOX_TOKEN'],
                               includeJquery=True)
    else:
        return render_template('map.html',
                               access_token=os.environ['MAPBOX_TOKEN'])


@app.route('/data', methods=['GET'])
def data():
    return jsonify(get_data(request.args.get('thing')))


@app.route('/in', methods=['GET'])
def put():
    set_data(request.args.get('nam'), request.args.get('val'))
    return jsonify({})


@app.route('/plan', methods=['POST'])
def plan():
    """fetch the page for the plans we care about"""
    origin = request.form['origin']
    dest = request.form['destination']

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5555)
