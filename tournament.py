#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    # Create a database connection
    db_conn = connect()

    # Create a database cursor and execute the delete matches query
    db_cursor = db_conn.cursor()
    delete_matches_query = 'DELETE FROM matches;'
    db_cursor.execute(delete_matches_query)

    # Make the changes to DB persistent
    db_conn.commit()

    # Close communication with the DB
    db_cursor.close()
    db_conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    # Create a database connection
    db_conn = connect()

    # Create a database cursor to interact with the database
    db_cursor = db_conn.cursor()

    # Construct and execute the query to delete registered players
    delete_players_query = 'DELETE FROM players;'
    db_cursor.execute(delete_players_query)

    # Make the changes to DB persistent
    db_conn.commit()

    # Close communication with the DB
    db_cursor.close()
    db_conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    # Create a session to the database
    db_conn = connect()

    # Create a database cursor to interact with the database
    db_cursor = db_conn.cursor()

    # Construct the query to get the count of registered players
    player_count_query = 'SELECT count(*) as player_count FROM players;'
    db_cursor.execute(player_count_query)

    # Get the player count from query output
    total_players = db_cursor.fetchone()[0]

    # Close communication with the DB
    db_cursor.close()
    db_conn.close()

    return total_players


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    # Create a session to the database
    db_conn = connect()

    # Create a database cursor to interact with the database
    db_cursor = db_conn.cursor()

    # Construct the query to add the given player
    add_player_query = 'INSERT INTO players(name) VALUES (%s);'
    player_data = (name,)
    db_cursor.execute(add_player_query, player_data)

    # Make the changes to DB persistent
    db_conn.commit()

    # Close communication with the DB
    db_cursor.close()
    db_conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    # Create a session to the database
    db_conn = connect()

    # Create a database cursor to interact with the database
    db_cursor = db_conn.cursor()

    # Create two views, one for the matches played by each player and
    # other for winning by each player
    players_matches_count_query = """CREATE VIEW players_matches_count as
        SELECT players.id as id, count(matches.winner) as num_matches
        FROM players left join matches on
            players.id = matches.winner or players.id = matches.loser
        GROUP BY players.id;
        """
    db_cursor.execute(players_matches_count_query)

    players_winnings_count_query = """CREATE VIEW players_wins_count as
        SELECT players.id as id, count(matches.winner) as num_wins
        FROM players left join matches on
            players.id = matches.winner
        GROUP BY players.id;
        """
    db_cursor.execute(players_winnings_count_query)

    # Merge the views to create a table with player id, wins and matches
    # Join that with the players table to get players name and sort by wins
    player_standings_query = """SELECT players.id, players.name,
            players_match_data.wins, players_match_data.matches
        FROM players join
            (SELECT players_wins_count.id as id, players_wins_count.num_wins as wins,
                    players_matches_count.num_matches as matches
             FROM players_wins_count join players_matches_count on
                    players_wins_count.id = players_matches_count.id) as players_match_data on
            players.id = players_match_data.id
        ORDER BY players_match_data.wins DESC;
        """
    db_cursor.execute(player_standings_query)
    player_standings = db_cursor.fetchall()

    # Drop the views created
    db_cursor.execute("DROP VIEW players_wins_count;")
    db_cursor.execute("DROP VIEW players_matches_count;")

    # Close communication with the DB
    db_cursor.close()
    db_conn.close()

    # Return the list of tuples with current player standings
    return player_standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    # Create a session to the database
    db_conn = connect()

    # Create a database cursor to interact with the database
    db_cursor = db_conn.cursor()

    # Construct the query to insert data into the matches tables
    add_match_query = "INSERT INTO matches(winner, loser) VALUES (%s, %s);"
    match_results = (winner, loser)
    db_cursor.execute(add_match_query, match_results)

    # Make the transaction permanent
    db_conn.commit()

    # Close communication with the DB
    db_cursor.close()
    db_conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # Get the number of registered players
    total_players = countPlayers()

    # Get the existing player standings
    current_player_standings = playerStandings()

    final_swiss_pairings = []
    player_index = 0
    while player_index < total_players:
        players_considered = current_player_standings[player_index:player_index+2]
        players_pair = tuple([players_considered[0][0], players_considered[0][1],
                              players_considered[1][0], players_considered[1][1]])
        final_swiss_pairings.append(players_pair)
        player_index += 2
    return final_swiss_pairings
