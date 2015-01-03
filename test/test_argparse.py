'''Tests that args provided by user are correctly parsed and processed'''
import unittest

from src.argv_input import arg_parser
from src.mg_proxy_creator import createMgInstance, getFileNamePath
import src.constants as CON


class TestArgs(unittest.TestCase):
    '''Test that argparse is correctly implemented and passed on'''

    def test_default_args(self):
        '''Test that empty args results in correct default values'''
        parsed_input = vars(arg_parser.parse_args(
            ['name_of_program'])
        )
        creator = createMgInstance(parsed_input)

        self.assertEqual(creator.dpi, CON.DPI)
        self.assertEqual(creator.wh, [CON.WIDTH, CON.HIGHT])
        self.assertEqual(creator.xy, [CON.PAGE_X, CON.PAGE_Y])

    def test_opt_file_name(self):
        '''Test that the user can provide optional file name'''
        parsed_input = vars(arg_parser.parse_args(
            ['name_of_program', '--'+CON.ARG_CONST['alt_name'], 'yay_santa']
        ))

        results = getFileNamePath(
            'does/not/matter',
            parsed_input
        )

        self.assertEqual(results[1], 'yay_santa')


if __name__ == '__main__':
    unittest.main()
