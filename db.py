import sqlite3
import os
from scripts import resource_path

# --- Database Initialization ---

def create_connection(db_file):
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

# --- Scores Database Management ---

def create_scores_table(db_path):
    """Create the scores table if it doesn't exist."""
    sql_create_scores_table = """ CREATE TABLE IF NOT EXISTS scores (
                                        id integer PRIMARY KEY,
                                        score integer NOT NULL,
                                        timestamp text NOT NULL,
                                        gamemode text NOT NULL,
                                        game_sequence text,
                                        mistakes text,
                                        game_mode text,
                                        time_taken real,
                                        flags_shown integer,
                                        mode_data text
                                    ); """
    conn = create_connection(db_path)
    if conn:
        create_table(conn, sql_create_scores_table)
        print(f"Successfully created/updated scores table in {db_path}")
        conn.close()

def insert_score(db_path, score, game_sequence, wrong_countries, gamemode, game_mode, time_taken, flags_shown, mode_data):
    """Insert a new score into the scores table."""
    from datetime import datetime
    import json
    
    conn = create_connection(db_path)
    if conn:
        sql = ''' INSERT INTO scores(score, timestamp, gamemode, game_sequence, mistakes, game_mode, time_taken, flags_shown, mode_data)
                  VALUES(?,?,?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sequence_str = ",".join(game_sequence)
        mistakes_str = ",".join(wrong_countries)
        mode_data_str = json.dumps(mode_data)
        
        cur.execute(sql, (score, now, gamemode, sequence_str, mistakes_str, game_mode, time_taken, flags_shown, mode_data_str))
        conn.commit()
        conn.close()

def get_top_scores(db_path, gamemode, filter_mode="all", limit=10):
    """Query top scores from the scores table based on gamemode and filter."""
    conn = create_connection(db_path)
    if not conn:
        return []

    try:
        cur = conn.cursor()
        # Base query
        query = "SELECT score, timestamp, gamemode, game_sequence, mistakes, game_mode, time_taken, flags_shown, mode_data FROM scores WHERE gamemode = ?"
        params = [gamemode]

        # Apply filter for specific game modes (normal, endless, blitz)
        if filter_mode != "all":
            query += " AND game_mode = ?"
            params.append(filter_mode)

        # Order by score and select top N
        query += " ORDER BY score DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in get_top_scores: {e}")
        return []
    finally:
        if conn:
            conn.close()


# --- Flags Database Management ---

def populate_flags_database(db_path):
    """
    Populates the flags database from the data folder.
    This should only be run if the database is missing or needs an update.
    """
    conn = create_connection(db_path)
    if not conn:
        return

    sql_create_flags_table = """CREATE TABLE IF NOT EXISTS flags (
                                id INTEGER PRIMARY KEY,
                                country TEXT NOT NULL UNIQUE,
                                continent TEXT NOT NULL
                            );"""
    create_table(conn, sql_create_flags_table)

    cursor = conn.cursor()
    print("Syncing flags database with asset files...")
    base_flags_path = resource_path("data/flags")
    continents = ['africa', 'america', 'asia', 'europe', 'oceania']

    discovered = {}
    for continent in continents:
        continent_path = os.path.join(base_flags_path, continent)
        try:
            for filename in os.listdir(continent_path):
                if filename.endswith(".png"):
                    country_name = os.path.splitext(filename)[0]
                    discovered[country_name] = continent
        except FileNotFoundError:
            print(f"Warning: Directory not found for continent: {continent}")
            continue

    cursor.execute("SELECT country, continent FROM flags")
    existing = {country: continent for country, continent in cursor.fetchall()}

    inserted = 0
    updated = 0
    removed = 0

    for country, continent in discovered.items():
        if country not in existing:
            cursor.execute("INSERT INTO flags(country, continent) VALUES(?, ?)", (country, continent))
            inserted += 1
        elif existing[country] != continent:
            cursor.execute("UPDATE flags SET continent = ? WHERE country = ?", (continent, country))
            updated += 1

    stale_countries = set(existing.keys()) - set(discovered.keys())
    for country in stale_countries:
        cursor.execute("DELETE FROM flags WHERE country = ?", (country,))
        removed += 1

    conn.commit()
    conn.close()
    print(f"Flags database synced. Inserted: {inserted}, Updated: {updated}, Removed: {removed}")
