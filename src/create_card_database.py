import sqlite3
import json

def getCardInfo(card_dict):
	card_info = {}
	card_info['name'] = card_dict['name']
	card_info['imageName'] = card_dict['imageName']
	card_info['rarity'] = card_dict['rarity']
	
	return card_info
	
def getSetCards(set_dict):
	set_code = set_dict['code']
	card_list = []

	for card in set_dict['cards']:
		simple_card = getCardInfo(card)
		simple_card['setCode'] = set_code
		card_list.append(simple_card)
		
	return card_list

def getAllCards(json_obj):
	all_cards = []
	
	for set in json_obj:
		set_cards = getSetCards(json_obj[set])
		all_cards = all_cards + set_cards
		
	return all_cards

def getAllCardsFromJSONFile(file_path):
	f = open(file_path, 'r')
	return getAllCards(json.loads(f.read()))

all_cards = getAllCardsFromJSONFile('/cygdrive/c/Users/Savo/Desktop/mg/AllSets.json')	
	
database = sqlite3.connect('mg_cards.sqlite3')
conn = database.cursor()

conn.execute("DROP TABLE IF EXISTS cards")
conn.execute("CREATE TABLE cards (id INTEGER PRIMARY KEY AUTOINCREMENT, set_code text, name text, image text, rarity text)")

for card in all_cards:
	conn.execute('INSERT INTO cards VALUES(NULL, :setCode, :name, :imageName, :rarity)', card)
	
database.commit()
database.close()