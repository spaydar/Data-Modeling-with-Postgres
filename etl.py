import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    '''
    Reads in a song-data file into a pandas dataframe, extracts required fields, and inserts data into the `songs` and `artists` tables in the database.
    
        Parameters:
            cur: A cursor used to execute SQL commands over an open connection to a PostgreSQL database
            filepath: The path of the song data file on the local filesystem
    '''
    
    df = pd.read_json(filepath, lines=True)

    song_data = list(df[['song_id', 'title', 'artist_id', 'year', 'duration']].values[0])
    cur.execute(song_table_insert, song_data)
    
    artist_data = list(df[['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']].values[0])
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    '''
    Reads in a user-activity log file into a pandas dataframe, filters for songplay records, converts the timestamp format from millisecond to datetime, 
        then loads several datetime attributes into the `time` table in the database. 
    Then reads in same log file to extract user-related fields to insert into the `users` table in the database.
    Finally joins `songs` and `artists` tables on song title, artist name, and song duration to select song_id and artist_id for each row in the first
        songplays dataframe to insert records into the `songplays` table in the database.
        
        Parameters:
            cur: A cursor used to execute SQL commands over an open connection to a PostgreSQL database
            filepath: The path of the user-activity data file on the local filesystem
    '''
    
    df = pd.read_json(filepath, lines=True)

    df = df[df['page']=="NextSong"]

    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    
    t = pd.DataFrame({"start_time": df['ts']})
    
    time_data = [[row[0], row.dt.hour[0], row.dt.day[0], row.dt.weekofyear[0], row.dt.month[0], row.dt.year[0], row.dt.weekday[0]] for i, row in t.iterrows()]
    column_labels = ['start_time','hour','day','week','month','year','weekday']
    time_df = pd.DataFrame(time_data, columns=column_labels)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    user_df = pd.read_json(filepath, lines=True)[['userId', 'firstName', 'lastName', 'gender', 'level']]

    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    for index, row in df.iterrows():
        
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        songplay_data = [row.ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent]
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    '''
    Retrieves all JSON files in the specified directory, prints the number of files found, then applies the provided `func` function to each file.
    
        Parameters:
            cur: A cursor used to execute SQL commands over an open connection to a PostgreSQL database. Passed to `func` function
            conn: An active connection to a PostgreSQL database used to commit changes made by `cur`
            filepath: The directory to search for JSON files to apply `func` to
            func: A function that accepts a cursor to a database connection and a file path
    '''

    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    '''
    Opens a connection to the Sparkify database and gets a cursor to it, performs an ETL on the song and user-activity log files, then closes the connection.
    '''
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()