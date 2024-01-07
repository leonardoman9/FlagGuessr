import os
import sqlite3

class countries:
    def __init__(self):
        self.result = {}
        self.create_database()
        self.load_countries()

    def create_database(self):
        # Connect to the database (or create it if it doesn't exist)
        with sqlite3.connect("flags.db") as conn:
            cursor = conn.cursor()

            # Create a table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS countries (
                    country TEXT PRIMARY KEY,
                    continent TEXT
                )
            ''')

    def load_countries(self):
        with sqlite3.connect("flags.db") as conn:
            cursor = conn.cursor()

            # Check if the database is empty
            cursor.execute("SELECT COUNT(*) FROM countries")
            if cursor.fetchone()[0] == 0:
                # If the database is empty, populate it with data
                self.populate_database(cursor)
            else:
                # Otherwise, load data from the database
                cursor.execute("SELECT country, continent FROM countries")
                self.result = dict(cursor.fetchall())

    def populate_database(self, cursor):
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

    def load_countries_data(self, folder):
        countries_data = []
        for filename in os.listdir(folder):
            country_name = os.path.splitext(filename)[0].title()  # Extract country name from filename
            countries_data.append((country_name, os.path.basename(os.path.normpath(folder))))
        return countries_data
    def getResult(self):
        return self.result
    def connect_db():
        return sqlite3.connect('flags.db')