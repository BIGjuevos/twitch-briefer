import json
import os

import requests

from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
    'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cache-Control': 'max-age=0',
    'Cookie': ''
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
    return {
        "flight_levels": [],
        "route": "TBD",
        "distance": 0,
    }


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
