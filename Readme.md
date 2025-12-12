## so what i expect from the SQL is 
    1. name: Name of the table
    2. summary: short summary about the table
    3. purpose: purpose of the table
    4. dependencies: relation with the other rables of the database that are mentioned in description 
    5. keys: list of columns that are keys that are used for connections with other tables in datbase
    6. connected_tables: names of table that are connected with this one concerning the previously detected keys


https://github.com/user-attachments/assets/808db055-c49b-4379-ab79-7276bddc54c0


## example
   CREATE TABLE playlist_track (
	playlist_id INTEGER NOT NULL, 
	track_id INTEGER NOT NULL, 
	CONSTRAINT playlist_track_pkey PRIMARY KEY (playlist_id, track_id), 
	CONSTRAINT playlist_track_playlist_id_fkey FOREIGN KEY(playlist_id) REFERENCES playlist (playlist_id), 
	CONSTRAINT playlist_track_track_id_fkey FOREIGN KEY(track_id) REFERENCES track (track_id)
)


### what i would want is
{
  "name": "playlist_track",

  "summary": "A junction table linking music tracks to playlists.",

  "purpose": "To bridge the many-to-many relationship between playlists and tracks. It allows a single playlist to contain multiple tracks and a single track to be listed in multiple different playlists without duplicating data.",

  "dependencies_thoughts": "Relates to the `playlist` table (playlist_id to playlist_id) and the `track` table (track_id to track_id). Records here depend on the existence of IDs in both parent tables.",

  "keys": [
    "playlist_id",
    "track_id"
  ],

  "connected_tables": [
    "playlist",
    "track"
  ],
  
  "columns": [
    {
      "column": "playlist_id",
      "description": "The numerical identifier of the playlist. This is part of the composite primary key and a foreign key referencing the 'playlist' table."
    },
    {
      "column": "track_id",
      "description": "The numerical identifier of the music track. This is part of the composite primary key and a foreign key referencing the 'track' table."
    }
  ]
}
