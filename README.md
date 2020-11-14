# Data Modeling with Postgres

## Purpose

This project seeks to create a Postgres database with tables optimized for queries on song-play analysis for a fictitious music streaming startup called Sparkify. Furthermore, it implements an ETL pipeline using Python to load logs on user activity as well as song metadata into the schema. Sparkify is interested in understanding what songs users are listening to.

## Database Design and ETL Pipeline

The relations in the database are implemented as fact and dimension tables for a star schema as follows:  

###### Fact Table
1. **songplays** - records in log data associated with song plays i.e. records with page `NextSong`
    - songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent
    
###### Dimension Tables
2. **users** - users in the app
    - user_id, first_name, last_name, gender, level
    
3. **songs** - songs in music database
    - song_id, title, artist_id, year, duration
    
4. **artists** - artists in music database
    - artist_id, name, location, latitude, longitude
    
5. **time** - timestamps of records in **songplays** broken down into specific units
    - start_time, hour, day, week, month, year, weekday  
    
The first column in each table is a primary key. The `songplays` table has foreign keys referencing name-matched primary key columns in each dimension table.



The ETL pipeline traverses the data directory for all JSON files contained, reads files in as pandas dataframes individually, extracts required columns, transforms data types if necessary (e.g. millisecond timestamp to datetime object), and in one case performs a join to synthesize data from different log types (i.e. songplay record vs. song metadata). Then, data is inserted in its designated table via the psycopg2 Postgres library.

## File and Code Structure

All SQL queries for the entire project are centralized in the `sql_queries.py` file for purposes of modularity and ease of maintenance. This file includes queries to drop tables, create tables, insert records into tables, and join two tables to retrieve a song ID and artist ID.

Before executing the ETL, the `create_tables.py` script must be run (use the `python3 create_tables.py` terminal command to run the script). This script drops the Sparkify database (if it exists) then creates the database, drops all tables (if they exist), then finally creates all the tables in the star schema. Once the tables have been created, the `etl.py` script can be run (with the `python3 etl.py` terminal command), which extracts, transforms, then loads all the data from the `data` directory into the tables as required by the schema design described above. The `data` directory contains JSON files describing song metadata as well as JSON logs of simulated user listening activity. The results of the ETL can be seen by querying the tables using the `test.ipynb` notebook, which selects all columns for 5 rows from each table. The `etl.ipynb` notebook contains a more detailed walkthrough of the steps taken in `etl.py` and applies them to single data files to extract, transform, and load a limited amount of data into the tables.

## Sample SQL Commands

Drop Table:

    DROP TABLE IF EXISTS songplays;
    
Create Table:

    CREATE TABLE IF NOT EXISTS songplays (songplay_id serial PRIMARY KEY, start_time timestamp NOT NULL, user_id varchar NOT NULL, level varchar, song_id varchar, artist_id varchar, session_id int, location varchar, user_agent varchar);
    
Insert Record into Table:

    INSERT INTO users (user_id, first_name, last_name, gender, level) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (user_id) DO UPDATE SET level=EXCLUDED.level;
    
Find song ID and artist ID with join:
        
    SELECT song_id, artists.artist_id FROM songs JOIN artists on songs.artist_id = artists.artist_id WHERE title = %s AND name = %s AND duration = %s;
    
## Datasets

### Song Dataset

The files found in the `/data/song_data/` directory are a subset of real data from the [Million Song Dataset](http://millionsongdataset.com/). Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are filepaths to two files in this dataset:

    song_data/A/B/C/TRABCEI128F424C983.json
    song_data/A/A/B/TRAABJL12903CDCF1A.json
    
Below is an example of what a single song file, TRAABJL12903CDCF1A.json, looks like:

    {"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}

### Log Dataset

The second dataset found in the `/data/log_data/` directory consists of log files in JSON format generated by this [event simulator](https://github.com/Interana/eventsim) based on the songs in the dataset above. These simulate activity logs from a music streaming app based on specified configurations.

The log files in this dataset are partitioned by year and month. For example, here are filepaths to two files in this dataset:

    log_data/2018/11/2018-11-12-events.json
    log_data/2018/11/2018-11-13-events.json

Below is an example of what the data in a log file, 2018-11-12-events.json, looks like:

![event log](https://video.udacity-data.com/topher/2019/February/5c6c15e9_log-data/log-data.png)

## Screenshots of Tables with Sample Data

`songs` Table:

![songs table](/images/songs_table.png "songs table")

`time` Table:

![time table](/images/time_table.png "time table")