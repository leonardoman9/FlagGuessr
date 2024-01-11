import sqlite3
from datetime import datetime


def create_scores_table(db_filename):
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    cursor.execute('''  CREATE TABLE IF NOT EXISTS scores
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        score INTEGER,
                        timestamp TEXT,
                        gamemode TEXT,
                        game_sequence LONGTEXT,
                        mistakes TEXT)''')
    connection.commit()
    connection.close()

def insert_score(db_filename, score, countries_list, wrong_countries, gamemode):
    try:
        connection = sqlite3.connect(db_filename)
        cursor = connection.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        countries = ""
        for i in countries_list:
            countries += i+ ", "
        mistakes = ""
        for i in wrong_countries:
            if len(mistakes)!=0 and len(mistakes)!=3:
                mistakes += ","
            mistakes += i
        cursor.execute('''  INSERT INTO 
                            scores (score, timestamp, gamemode ,game_sequence, mistakes) 
                            VALUES (?, ?, ?, ?, ?)''', (score, timestamp, gamemode, countries, mistakes))
        connection.commit()
        connection.close()
    except Exception:
        print("Error while inserting score!")
        print(Exception)

def get_top_scores(db_filename, gamemode,limit=10):
    try:
        connection = sqlite3.connect(db_filename)
        cursor = connection.cursor()
        cursor.execute('''  SELECT score, timestamp, gamemode, game_sequence, mistakes 
                            FROM scores    
                            WHERE gamemode = ?
                            ORDER BY score 
                            DESC LIMIT ?''', (gamemode, limit))
        top_scores = cursor.fetchall()
        connection.close()
        return top_scores
    except Exception:
        print("Error while retrieving top scores!")
        print(Exception)
