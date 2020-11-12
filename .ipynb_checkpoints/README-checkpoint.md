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
    
The first column in each table is a primary key.



The ETL pipeline traverses the data directory for all JSON files contained, reads files in as pandas dataframes individually, extracts required columns, transforms data types if necessary (e.g. millisecond timestamp to datetime object), and in one case performs a join to synthesize data from different log types (i.e. songplay record vs. song metadata). Then, data is inserted in its designated table via the psycopg2 Postgres library.

## File Structure