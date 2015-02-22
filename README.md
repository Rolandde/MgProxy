# MgProxy
Magic the Gathering Proxy Generator written in Python

## Requirements
Requires Python2.7+ (Py2.7_master branch) or Python3+ (master branch). 
Both version require either the Pillow (preferred) or PIL module with jpeg support enabled.

## Purpose
Create Magic the Gathering jpg images for easy printing and cutting. 
All the program needs is a text file with card names, how many of each card, and which set they are from.
Input lines follow Magic Workstation (mwDeck file format) rules (see Usage).
Relies on the amazing database found at http://mtgjson.com/ and http://mtgimage.com/.

## Usage
Run `python MgProxy -h` for a full list of options.

The input text file takes one card per line. Side Board tag (SB:) and Set Code are optional. Example:

`10 Forest` - Creates 10 Forest cards. Preference is given to the highest resolution card from the most recent set.

`10 [M10] Forest` - Creates 10 Forest cards from the M10 set. For valid set codes see http://mtgjson.com/

`SB: 10 [M10] Forest` - No different than previous line. Useful if you want to remember which cards formed the original side board.
