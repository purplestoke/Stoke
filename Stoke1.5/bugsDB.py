import sqlite3

conn = sqlite3.connect("bugs_DB.sqlite")
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# Drop existing tables and create new ones
cur.executescript(
"""
DROP TABLE IF EXISTS bugs_Profile;
DROP TABLE IF EXISTS Finals_Profile;
DROP TABLE IF EXISTS Apex_Profile;
DROP TABLE IF EXISTS XDefiant_Profile;
DROP TABLE IF EXISTS Stoke_Guilds;
DROP TABLE IF EXISTS Hosted_Comm;
DROP TABLE IF EXISTS Events;

CREATE TABLE Hosted_Comm (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
name TEXT VARCHAR(25)
);

CREATE TABLE Stoke_Guilds (
guild_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
guild_name TEXT VARCHAR(25),
guild INTEGER,
intercom INTEGER,
bugs_channel INTEGER,
sc_submission INTEGER,
apex_role INTEGER,
finals_role INTEGER,
xdefiant_role INTEGER,
competitor_role INTEGER
);

CREATE TABLE bugs_Profile (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
discord INTEGER UNIQUE,
eth_addr TEXT UNIQUE,
hash TEXT VARCHAR(64) UNIQUE,
apex_profile BOOLEAN,
finals_profile BOOLEAN,
xdefiant_profile BOOLEAN
);

CREATE TABLE Finals_Profile ( 
bugs_id INTEGER UNIQUE,
gamertag TEXT VARCHAR(25) UNIQUE,
elligible TEXT VARCHAR(64) UNIQUE,
submission BOOLEAN,
points INTEGER,
guild_id INTEGER,
hosted_id INTEGER,
FOREIGN KEY(bugs_id) REFERENCES bugs_Profile(id) ON DELETE CASCADE,
FOREIGN KEY(guild_id) REFERENCES Stoke_Guilds(guild_id) ON DELETE CASCADE,
FOREIGN KEY(hosted_id) REFERENCES Hosted_Comm(id) ON DELETE CASCADE
);

CREATE TABLE Apex_Profile (
bugs_id INTEGER UNIQUE,
gamertag TEXT VARCHAR(25) UNIQUE,
elligible TEXT VARCHAR(64) UNIQUE,
submission BOOLEAN,
points INTEGER,
guild_id INTEGER,
hosted_id INTEGER,
FOREIGN KEY(bugs_id) REFERENCES bugs_Profile(id) ON DELETE CASCADE,
FOREIGN KEY(guild_id) REFERENCES Stoke_Guilds(guild_id) ON DELETE CASCADE,
FOREIGN KEY(hosted_id) REFERENCES Hosted_Comm(id) ON DELETE CASCADE
);

CREATE TABLE XDefiant_Profile (
bugs_id INTEGER UNIQUE,
gamertag TEXT VARCHAR(25) UNIQUE,
elligible TEXT VARCHAR(64) UNIQUE,
submission BOOLEAN,
points INTEGER,
guild_id INTEGER,
hosted_id INTEGER,
FOREIGN KEY(bugs_id) REFERENCES bugs_Profile(id) ON DELETE CASCADE,
FOREIGN KEY(guild_id) REFERENCES Stoke_Guilds(guild_id) ON DELETE CASCADE,
FOREIGN KEY(hosted_id) REFERENCES Hosted_Comm(id) ON DELETE CASCADE
);

CREATE TABLE Events (
game TEXT VARCHAR(15),
pmnt_flag BOOLEAN,
submission_flag BOOLEAN
);
"""
)

# Commit the changes to create the tables
conn.commit()

# Execute the joins
cur.execute(
    "SELECT * FROM Stoke_Guilds JOIN Apex_Profile ON Stoke_Guilds.guild_id = Apex_Profile.guild_id"
)

cur.execute(
    "SELECT * FROM Stoke_Guilds JOIN Finals_Profile ON Stoke_Guilds.guild_id = Finals_Profile.guild_id"
)

conn.commit()
conn.close()
print("DB Created")
