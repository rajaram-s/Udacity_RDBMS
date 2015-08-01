-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create the database named 'tournament' once
-- CREATE DATABASE tournament;

-- Connect to the 'tournament' database
\c tournament

-- cleanup mess from previous runs`
DROP TABLE matches CASCADE;

DROP TABLE players CASCADE;

-- Create the players table to store registered players information
CREATE TABLE players (id serial PRIMARY KEY,
    name text);

-- Create the matches table to store outcome of matches between two players
CREATE TABLE matches (match_num serial PRIMARY KEY,
    winner integer references players(id),
    loser integer references players(id))
