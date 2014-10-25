'''Tests downloading and parsin of JSON files downloaded from mtgjson.com'''
from src import get_mtg_json
import unittest
import json


class GetAndParseMTGJson(unittest.TestCase):

    '''Main TestCase testing validyt of JSON download and parsing'''

    def setUp(self):
        '''Loads the local json file to test against.'''
        f = open('test/files/M10.json', 'r')
        self.mtg_file = json.loads(f.read())

    def test_get_json(self):
        '''Test if json file is correctly downloaded and returned'''
        self.assertDictEqual(self.mtg_file, get_mtg_json.getSetJson('M10'))

    def test_parse_json(self):
        '''Test if json file has been corretly parsed'''
        expected_rarity = [
            'Common', 'Uncommon', 'Rare', 'Mythic Rare', 'Basic Land'
        ]

        mtg_json = get_mtg_json.getSetJson('M10')
        mtg_parsed = get_mtg_json.parseLocalSetForRarity(mtg_json)

        self.assertItemsEqual(
            mtg_parsed.keys(), expected_rarity,
            'Not all expected rarities have been parsed'
        )

        cards_json = mtg_json['cards']
        for card in cards_json:
            card_name = card['name']
            card_rarity = card['rarity']

            self.assertIn(
                card_name, mtg_parsed[card_rarity],
                card_name + 'not in the expected rarity of ' + card_rarity
            )

        web_parsed = get_mtg_json.parseSetForRarity('M10')
        self.assertDictEqual(
            mtg_parsed, web_parsed,
            'Wrapper function does not equal individual functions'
        )

if __name__ == '__main__':
    unittest.main()
