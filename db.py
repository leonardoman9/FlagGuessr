import sqlite3
from datetime import datetime
import json


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
                            mistakes TEXT,
                            game_mode TEXT DEFAULT 'normal',
                            time_taken INTEGER DEFAULT 0,
                            flags_shown INTEGER DEFAULT 0,
                            mode_specific_data TEXT DEFAULT '{}')''')
        connection.commit()
        
        # Check if we need to add new columns to existing table
        cursor.execute("PRAGMA table_info(scores)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns for backward compatibility
        if 'game_mode' not in columns:
            cursor.execute('ALTER TABLE scores ADD COLUMN game_mode TEXT DEFAULT "normal"')
            print("Added game_mode column")
        
        if 'time_taken' not in columns:
            cursor.execute('ALTER TABLE scores ADD COLUMN time_taken INTEGER DEFAULT 0')
            print("Added time_taken column")
            
        if 'flags_shown' not in columns:
            cursor.execute('ALTER TABLE scores ADD COLUMN flags_shown INTEGER DEFAULT 0')
            print("Added flags_shown column")
            
        if 'mode_specific_data' not in columns:
            cursor.execute('ALTER TABLE scores ADD COLUMN mode_specific_data TEXT DEFAULT "{}"')
            print("Added mode_specific_data column")
        
        connection.commit()
        connection.close()
        print(f"Successfully created/updated scores table in {db_filename}")
    except Exception as e:
        print(f"Error while creating/updating database {db_filename}: {e}")

def insert_score(db_filename, score, countries_list, wrong_countries, gamemode, 
                game_mode="normal", time_taken=0, flags_shown=0, mode_data=None):
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
        
        # Handle mode-specific data
        if mode_data is None:
            mode_data = {}
        mode_data_json = json.dumps(mode_data)
        
        cursor.execute('''  INSERT INTO 
                            scores (score, timestamp, gamemode, game_sequence, mistakes, 
                                   game_mode, time_taken, flags_shown, mode_specific_data) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (score, timestamp, gamemode, countries, mistakes, 
                        game_mode, time_taken, flags_shown, mode_data_json))
        print(f"Score inserted into {db_filename} (mode: {game_mode})") 
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Error while inserting score in {db_filename}:\n {e}")

def get_top_scores(db_filename, gamemode, game_mode="all", limit=10):
    try:
        connection = sqlite3.connect(db_filename)
        cursor = connection.cursor()
        
        # Build query based on filters
        base_query = '''SELECT score, timestamp, gamemode, game_sequence, mistakes,
                              game_mode, time_taken, flags_shown, mode_specific_data 
                        FROM scores WHERE gamemode = ?'''
        params = [gamemode]
        
        if game_mode != "all":
            base_query += ' AND game_mode = ?'
            params.append(game_mode)
        
        # Order by score for most modes, but by time for blitz mode
        if game_mode == "blitz":
            base_query += ' ORDER BY score DESC, time_taken ASC LIMIT ?'
        else:
            base_query += ' ORDER BY score DESC LIMIT ?'
        
        params.append(limit)
        
        cursor.execute(base_query, params)
        top_scores = cursor.fetchall()
        connection.close()
        print(f"Top scores loaded from {db_filename} for gamemode '{gamemode}' mode '{game_mode}': {len(top_scores)} records found")
        return top_scores
    except Exception as e:
        print(f"Error while retrieving top scores from {db_filename} for gamemode '{gamemode}' mode '{game_mode}':\n {e}")
        return []  # Return empty list instead of None