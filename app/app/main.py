import hashlib
import json
import logging
import os
import signal
import sys
import textwrap
import traceback
import urllib.request
from datetime import datetime
from typing import re

import xmltodict as xmltodict
from flask import Flask, request, render_template, jsonify, make_response
from flask_cors import CORS

from .helpers.db import get_data, set_data, guess, just_end_it_all
from .helpers.flight import get_metar, get_taf, get_fuel, get_route

WRAP_WIDTH = 65

dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=f"/dev/stdout", level=logging.INFO)

logger = logging.getLogger(__name__)


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
    return render_template('index.html',
                           host=request.base_url,)


@app.route('/status')
def status():
    return jsonify({})


@app.route('/data', methods=['GET'])
def data():
    return jsonify(get_data())


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


@app.route('/marquee/info', methods=['GET'])
def marquee_info():
    return render_template('marquee_info.html')


@app.route('/marquee/route', methods=['GET'])
def marquee_route():
    return render_template('marquee_route.html')


@app.route('/planned', methods=['GET'])
def planned():
    args = request.args
    logger.info(f"Planned request: {args}")

    url = 'http://www.simbrief.com/ofp/flightplans/xml/' + args['ofp_id'] + '.xml'
    logger.info(f"Flightplan URL {url}")
    response = urllib.request.urlopen(url)
    flight_plan = xmltodict.parse(response.read())['OFP']

    set_data("rte", flight_plan['general']['route'])
    set_data("dep", flight_plan['origin']['iata_code'])
    set_data("arr", flight_plan['destination']['iata_code'])
    set_data("cruise_alt", flight_plan['general']['initial_altitude'])
    set_data("pass_count", flight_plan['general']['passengers'])

    preflight_url = str(flight_plan['prefile']['vatsim']['link']) + "&rmk=CALLSIGN%3DZERO%20RMK%2FVPC%20RMK%2FSIMBRIEF%20%2FV%2F"

    return render_template('plan.html',
                           url=f"{flight_plan['files']['directory']}{flight_plan['files']['pdf']['link']}",
                           prefile_url=preflight_url,
                           )


@app.route('/simbrief', methods=['GET'])
def simbrief():
    """
    Just pretend to be the PHP file, it was just easier than doing crappy PHP
    """
    args = request.args
    simbrief_api_key = os.environ['SIMBRIEF_API_KEY']

    logger.info(f"Simbrief request: {args}")

    if 'api_req' in args:
        text = 'var api_code = "' + hashlib.md5(simbrief_api_key.encode('utf-8') + args['api_req'].encode('utf-8')).hexdigest() + '";'
        response = make_response(text)
        response.headers['Content-Type'] = "application/javascript"
        return response

    if 'js_url_check' in args:
        varname = args['var'] if args['var'] and args['var'] != '' else 'phpvar'
        logger.info(f"Checking {args['js_url_check']}")
        logger.info(f"varname={varname}")

        url = 'http://www.simbrief.com/ofp/flightplans/xml/' + args['js_url_check'] + '.xml'
        logger.info(f"Checking {url}")
        response = urllib.request.urlopen(url)

        if response.getcode() != 200:
            resp = False
        else:
            resp = True

        text = 'var ' + varname + ' = "' + ('true' if resp else 'false') + '";'
        response = make_response(text)
        response.headers['Content-Type'] = "application/javascript"
        return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8888)
