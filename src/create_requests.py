import sqlite3

def searchCardName(database, name, set_code=None):
	cursor = database.cursor()
	if (set_code == None):
		cursor.execute('SELECT * FROM cards WHERE name=?', (name,))
	else:
		cursor.execute('SELECT * FROM cards WHERE name=? and set_code=?', (name, set_code))
	return cursor.fetchall()

conn = sqlite3.connect('/cygdrive/c/Users/Savo/Desktop/mg/mg_cards.sqlite3')
print searchCardName(conn, 'Abrupt Decay', 'RTR')

