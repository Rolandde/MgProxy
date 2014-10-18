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

if __name__ == '__main__':
    unittest.main()
