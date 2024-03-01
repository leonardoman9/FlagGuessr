import os
import sqlite3
import pygame

class countries:
    def __init__(self):
        self.db_filename = "flags.db"

        # Destroy the database if it exists
        self.destroy_db(self.db_filename)

        # Create the database
        self.create_database(self.db_filename)

        # Populate the database
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            self.populate_database(cursor)

       
    def create_database(self, db_filename):
        try:
        # Connect to the database (or create it if it doesn't exist)
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()

                # Create a table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS countries (
                        country TEXT PRIMARY KEY,
                        continent TEXT
                    )
                ''')
            print(f"Database '{db_filename}' has been created.")
        except Exception:
            print(f"Error creating {db_filename}")
            print(Exception)




    def load_countries(self, db_filename, gamemode):
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()

                # Check if the database is empty
                cursor.execute("SELECT COUNT(*) FROM countries")
                if cursor.fetchone()[0] == 0:
                    # If the database is empty, populate it with data
                    self.populate_database(cursor)
                    if type(gamemode) == str:
                        cursor.execute("SELECT country, continent FROM countries WHERE continent = ?", (gamemode,))
                    elif type(gamemode) == list:
                        raise Exception("List passed as parameter for gamemode")
                    self.result = dict(cursor.fetchall())
                else:
                    # Otherwise, load data from the database
                    if type(gamemode) == str:
                        if gamemode == "global":
                            cursor.execute("SELECT country, continent FROM countries")
                        else:
                            cursor.execute("SELECT country, continent FROM countries WHERE continent = ?", (gamemode,))
                    elif type(gamemode) == list:
                        raise Exception("List passed as parameter for gamemode")  
                    self.result = dict(cursor.fetchall())    
                    return self.result               
        except Exception:
            print("Error while loading countries")
            print(Exception)

    def populate_database(self, cursor):
        try:
            # You should replace this with your actual data loading logic
            # For demonstration purposes, I'm assuming a simplified structure
            europe_countries = self.load_countries_data("data/flags/europe")
            america_countries = self.load_countries_data("data/flags/america")
            asia_countries = self.load_countries_data("data/flags/asia")
            oceania_countries = self.load_countries_data("data/flags/oceania")
            africa_countries = self.load_countries_data("data/flags/africa")

            # Insert data into the database
            cursor.executemany("INSERT INTO countries VALUES (?, ?)", europe_countries)
            cursor.executemany("INSERT INTO countries VALUES (?, ?)", america_countries)
            cursor.executemany("INSERT INTO countries VALUES (?, ?)", asia_countries)
            cursor.executemany("INSERT INTO countries VALUES (?, ?)", oceania_countries)
            cursor.executemany("INSERT INTO countries VALUES (?, ?)", africa_countries)

            # Commit the changes
            cursor.connection.commit()
            print(f"Database '{self.db_filename}' has been populated.")
        except Exception:
            print("Error while populating database '{db_filename}'")
            print(Exception)

    def destroy_db(self, db_filename):
        try:
            if os.path.exists(db_filename):
                os.remove(db_filename)
                print(f"Database '{db_filename}' has been deleted.")
        except Exception:
            print("Error while destroying database '{db_filename}'")
            print(Exception)

    def load_countries_data(self, folder):
        try:
            countries_data = []
            for filename in os.listdir(folder):
                country_name = os.path.splitext(filename)[0].title()  # Extract country name from filename
                countries_data.append((country_name, os.path.basename(os.path.normpath(folder))))
            return countries_data
        except Exception:
            print("Error while loading countries data from database '{db_filename}'")

    def connect_db(self):
        return sqlite3.connect(self.db_filename)

    def load_flags_images(self, game_countries, flag_size):
        flags = {}
        flags_directory = "data/flags"  # Adjust the directory path as needed

        for country, continent in game_countries.items():
            # Assuming the country names are in lowercase in the flags directory
            country_lowercase = country.lower()
            flag_path = os.path.join(flags_directory, continent.lower(), f"{country_lowercase}.png")
            
            # Check if the file exists before adding to the dictionary
            if os.path.isfile(flag_path):
                # Load the image using pygame
                flag_image = pygame.image.load(flag_path)
                resized_flag = pygame.transform.scale(flag_image, flag_size)
                flags[country] = resized_flag
            else:
                print(f"Flag not found for {country} in {flag_path}")

        return flags
     