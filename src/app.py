import json
import textwrap
from datetime import datetime
from functools import lru_cache

from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

WRAP_WIDTH = 65

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/plan', methods=['POST'])
def plan():
    "fetch the page for the plans we care about"
    origin = request.form['origin']
    dest = request.form['destination']

    soup = BeautifulSoup(get_route(origin, dest))
    table = soup.findAll('table')[3]

    flight_levels = table.findAll('td')[3].contents[0]
    route = table.findAll('td')[4].findAll('a')[0].contents[0]
    route = "\n".join(textwrap.wrap(route, WRAP_WIDTH))
    distance = table.findAll('td')[5].contents[0]

    origin_weather = get_metar(origin)
    origin_weather = "\n".join(textwrap.wrap(origin_weather, WRAP_WIDTH))

    dest_weather = get_metar(dest)
    dest_weather = "\n".join(textwrap.wrap(dest_weather, WRAP_WIDTH))
    
    origin_taf = get_taf(origin)
    origin_taf = "\n".join(textwrap.wrap(origin_taf, WRAP_WIDTH))

    dest_taf = get_taf(dest)
    dest_taf = "\n".join(textwrap.wrap(dest_taf, WRAP_WIDTH))

    fuel = get_fuel(origin, dest)

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


@lru_cache()
def get_metar(station):
    response = requests.get(f'https://avwx.rest/api/metar/{station}?options=&format=json&onfail=cache')

    obj = json.loads(response.text)

    return obj['sanitized']


@lru_cache()
def get_taf(station):
    response = requests.get(f'https://avwx.rest/api/taf/{station}?options=summary&format=json&onfail=cache')

    obj = json.loads(response.text)

    return obj['raw']


@lru_cache()
def get_route(origin, dest):
    url = f"https://flightaware.com/analysis/route.rvt?origin={origin}&destination={dest}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    response = requests.get(url, headers=headers)

    return response.text
    # with open("static/test.html") as f:
    #     return f.read()


@lru_cache()
def get_fuel(origin, dest):
    params = {
        "okstart": 1,
        "EQPT": "B738",
        "ORIG": origin,
        "DEST": dest,
        "submit": "PLANNER",
    }

    url = "http://www.fuelplanner.com/index.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    response = requests.post(url, data=params)

    soup = BeautifulSoup(response.text)
    points = soup.findAll('td')

    return [points[2].text, points[3].text, points[5].text, points[6].text, points[8].text, points[9].text]


if __name__ == '__main__':
    app.run()
