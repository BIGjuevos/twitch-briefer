import json
import os

import requests

from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
}


def get_metar(station):
    token = os.environ['AVWX_API_KEY']
    url = f'https://avwx.rest/api/metar/{station}?options=&format=json&onfail=cache&token={token}'
    response = requests.get(url, headers=headers)

    obj = json.loads(response.text)

    return obj['sanitized']


def get_taf(station):
    token = os.environ['AVWX_API_KEY']
    url = f'https://avwx.rest/api/taf/{station}?options=summary&format=json&onfail=cache&token={token}'
    response = requests.get(url, headers=headers)

    obj = json.loads(response.text)

    return obj['raw']


def get_route(origin, dest):
    url = f"https://flightaware.com/analysis/route.rvt?origin={origin}&destination={dest}"
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, features="html.parser")
    table = soup.findAll('table')[3]

    flight_levels = table.findAll('td')[3].contents[0]
    route = table.findAll('td')[4].findAll('a')[0].contents[0]
    distance = table.findAll('td')[5].contents[0]

    return {
        "flight_levels": flight_levels,
        "route": route,
        "distance": distance,
    }
    # with open("static/test.html") as f:
    #     return f.read()


def get_fuel(origin, dest):
    params = {
        "okstart": 1,
        "EQPT": "B738",
        "ORIG": origin,
        "DEST": dest,
        "submit": "PLANNER",
    }

    url = "http://www.fuelplanner.com/index.php"
    response = requests.post(url, data=params, headers=headers)

    soup = BeautifulSoup(response.text, features="html.parser")
    points = soup.findAll('td')

    return [points[2].text, points[3].text, points[5].text, points[6].text, points[8].text, points[9].text]
