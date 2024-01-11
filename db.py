import sqlite3
from datetime import datetime


def create_scores_table(db_filename):
    try:
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
        print(f"Succesfully created scores table in {db_filename}")
    except Exception as e:
        print(f"Error while creating database {db_filename}: {e}")

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
        print(f"Score inserted into {db_filename}")
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error while inserting score in {db_filename}:\n {e}")

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
        print(f"Top scores loaded from {db_filename}")
        return top_scores
    except Exception as e:
        print(f"Error while retrieving top scores:\n {e}")