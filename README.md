# MgProxy
Magic the Gathering Proxy Generator written in Python

## Requirements
Requires Python2.7+ (Py2.7_master branch) or Python3+ (master branch). 
Both version require either the Pillow (preferred) or PIL module with jpeg support enabled.
To recreate the lookup json file (master.json), Requests and lxml modules are required.

## Purpose
Create Magic the Gathering jpg images for easy printing and cutting. 
All the program needs is a text file with card names, how many of each card, and which set they are from.
Input lines follow Magic Workstation (mwDeck file format) rules (see Usage).
Since http://mtgimage.com/ has been shut down, this program works from a master json file that contains card names
and their http://http://magiccards.info/ location. http://mtgjson.com/ is used to get all the sets.

The master.json file can be recreated by running master_lookup.py.

## Usage
Run `python MgProxy -h` for a full list of options.

The input text file takes one card per line. Side Board tag (SB:) and Set Code are optional. Example:

`10 Forest` - Creates 10 Forest cards. Preference is given to the highest resolution card from the most recent set.

`10 [M10] Forest` - Creates 10 Forest cards from the M10 set. For valid set codes see http://mtgjson.com/

`SB: 10 [M10] Forest` - No different than previous line. Useful if you want to remember which cards formed the original side board.
