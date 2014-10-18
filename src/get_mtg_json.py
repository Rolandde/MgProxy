'''Download and parse JSON files from mtgjson.com'''

import urllib
from urlparse import urljoin
import json

from .constants import MgException, BASE_URL_JSON, JSON_EXT


def createSetAddress(set_name):
    '''Crate a valid URL address to the JSON file for a given set'''
    file_name = urllib.quote(set_name + JSON_EXT)
    json_url = urljoin(BASE_URL_JSON, 'json/')
    return urljoin(json_url, file_name)


def getSetJson(set_name):
    '''Downloads the JSON data for the given set and returns it as a dict'''
    address = createSetAddress(set_name)
    response = urllib.urlopen(address)

    if response.getcode() != 200:
        raise MgException(
            'Set URL does not exist. Error code: ' + str(response.getcode()) +
            ': ' + address)

    if response.info()['Content-Type'] != 'application/json':
        raise MgException(
            'Expected json file, instead received: ' +
            response.info()['Content-Type'] +
            ': ' +
            address)

    json_size = int(response.info()['Content-Length'])
    json_stream = response.read(json_size)

    return json.loads(json_stream)


def parseSetForRarity(set_dict):
    '''Returns a dictionary with rarity (key) and list of card names (value)'''
    all_cards = set_dict['cards']
    result_dict = {}

    for card in all_cards:
        card_name = card['name']
        card_rarity = card['rarity']

        # If first card with given rarity found, start an empty list
        if card_rarity not in result_dict:
            result_dict[card_rarity] = []

        result_dict[card_rarity].append(card_name)

    return result_dict
