import io
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import math
import numpy as np


def load_codes():
    ## `load_codes` is a function used to load the stats.ncaa.org team codes 

    ##   Input: load_codes takes no arguments

    ##   Output:
    ##        team_codes : a dataframe of team codes

    #Scrape codes table
    page = requests.get('http://stats.ncaa.org/game_upload/team_codes')
    team_codes = pd.read_html(page.text)[0]

    #Make column names descriptive, drop unnecessary rows, and reset row indices
    team_codes.rename(columns = {0: 'Code', 1: 'School'}, inplace = True)
    team_codes.drop(index = [0, 1], inplace=True)
    team_codes.reset_index(drop=True, inplace=True)

    #Convert `Code` column from str to int
    team_codes['Code'] = team_codes['Code'].astype(int)
    
    return(team_codes)


def load_roster(code, year_ID):
    '''used to scrape an entire roster from stats.ncaa.org

    Input:
        code : the code for the desired team
        year_ID : the stats.ncaa ID for the desired year

    Output:
        roster : pandas object of roster of entire team
    '''

    # Scrape roster table
    URL = f"http://stats.ncaa.org/team/{code}/roster/{year_ID}"
    page = requests.get(URL)
    roster = pd.read_html(page.text)[0]

    # Fix MultiIndex column names, which makes indexing inconvenient
    roster.columns = roster.columns.droplevel()

    # Split the 'Player' column on the first comma to separate players' first and last names.
    # Setting the `expand` parameter to True tells `Series.str.split()` to output a dataframe
    # with each column containing a component of the split string.
    split_name = roster['Player'].str.split(", ", n=1, expand=True)

    # Drop unnecessary columns and add each column of `split_name` to `roster`
    roster.drop(columns=["Player", "GP", "GS"], inplace=True)
    roster["Last_Name"] = split_name[0]
    roster["First_Name"] = split_name[1]

    # Reorder `roster` columns
    cols = roster.columns.to_list()
    cols = [cols[0]] + cols[3:] + cols[1:3]
    roster = roster[cols]

    # Add 'Team' column
    # roster['Team'] = team_codes[team_codes['Code'] == 755].values[0][1]

    ## In the original sprays script, there was a function called quickStats that scraped offensive
    ## stats from stats.ncaa.  For the purposes of sprays, this function only ended up adding each player's 
    ## number of at bats to the roster dataframe, so I decided to include that functionality in load_roster.

    #Scrape offensive stats table
    URL = f'http://stats.ncaa.org/team/{code}/stats/{year_ID}'
    page = requests.get(URL)
    stats = pd.read_html(page.text)[2]

    # Split the player column just like we did for `roster`
    split_name = stats['Player'].str.split(', ', n=1, expand=True)
    stats['Last_Name'] = split_name[0]
    stats['First_Name'] = split_name[1]

    # Merge `roster` and 'AB' column in `stats` on first and last names
    roster = roster.merge(stats[['Last_Name', 'First_Name', 'AB']], on = ['Last_Name', 'First_Name'])

    # Players with no at bats will have 'NaN' in the 'AB' column. We want to change this to 0
    # and change all values in this column to type int.
    roster.fillna(value = {'AB': 0}, inplace=True)
    roster['AB'] = roster['AB'].astype(int)

    return(roster)


def links_helper(URL, match):
    '''helper function for `get_links` that scrapes links matching a given regex (`match`) from a given URL.

    Input:
        URL : the URL that we want to scrape
        match : the regex specifying which links we want to scrap
        links : a list of links matching the regex
    '''

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = soup.find_all('a', href=match)

    return(links)


def get_links(code, year_ID):
    '''## `get_links` is a function used to scrape links to play-by-play data for all of a given
     team's games in a given year.

    Input:
        code : the code for the desired team
        year_ID : the stats.ncaa ID for the desired year

    Output:
        pbp_links : list of URLs for play-by-play data

    Note: Originally this function returned play-by-play links for the supplied year and the year before. This
    version only returns links from the supplied year so that the user can specify the number of years they want
    included in the sprays and run this function an appropriate number of times.
    '''

    # Scrape HTML elements with the desired href
    URL = f"https://stats.ncaa.org/team/{code}/roster/{year_ID}"
    match = re.compile(r'\/teams\/\d{6}')
    link = links_helper(URL, match)[0]

    team_URL = f"https://stats.ncaa.org/{link['href']}"    
    ## There was a change in the URL scheme after the 2018 season that necessitates
    ## different possible regex at this step.
    if year_ID >= 14781:
        match = re.compile(r'\/contests\/1\d+')
    else:
        match = re.compile(r'\/game\/index')
    links = links_helper(team_URL, match)
    contests_links = [link['href'] for link in links]

    def concat_link(link):
        href = links_helper(f'https://stats.ncaa.org/{link}', 
                           re.compile(r"\/play_by_play"))[0]['href']
        full_link = f"https://stats.ncaa.org/{href}"
        return(full_link)

    pbp_links = [concat_link(link) for link in contests_links]

    return(pbp_links)


def play_scrape(code, pbp_links):
    ''' `play_scrape` is a function used to scrape play by play data off the stats.ncaa website.

    Input:
        code : the code for the desired team
        pbp_links : a list of URLs linking to play-by-play pages

     Output:
        plays : a one column dataframe with all of the team's events/plays on offense
    '''

    # Find the team's name so we don't include opponents' events on offense
    team_name = team_codes[team_codes['Code'] == code].values[0][1]

    plays = []
    for URL in pbp_links:
        page = requests.get(URL)
        game = pd.read_html(page.text)
        # The object at index 5 of `game` is the first inning of that game. The first object of that inning is 
        # a column representing the away team's events on offense. The first string of that column is the team name.
        # If our desired team's name doesn't match this string, then they must be the home team, whose events are in
        # the column at index 2.
        if game[5][0][0] == team_name:
            idx = 0
        else:
            idx = 2
        # After index 5, even numbered indices contain a table with an updated score. We want to iterate over odd indices.
        for i in range(5, len(game), 2):
            # Each team's column for each inning contains NaN values (which have type float) for the part of that inning
            # where they were on defense. We check the type of `event` to make sure we don't add these to `plays`.
            game_plays = [event for event in game[i][idx][1:-1] if type(event) == str]
            plays = plays + game_plays
    plays = pd.DataFrame(data={'Description': plays})
    return(plays)


def load_points(file):
    '''
    `load_points` is a function used to read in a csv file with the graphing instructions for the
    `make_spray` function

    Input:
        file : the file you want to read in

    Output:
        points : a dataframe of the information in the csv file
    '''

    ## Graphical Point is the suggested file to use
    points = pd.read_csv(file).dropna().reset_index(drop=True)
    points.rename(columns={'line.type': 'line_type', 'Total': 'Event', 'type': 'face_color', 'color': 'edge_color'},
                  inplace=True)
    points['face_color'] = np.where(points['face_color']==1, 'none', points['edge_color'])
    return(points)


def spray_info(plays, First_Name, Last_Name):

    # Create a Series subset of `plays` for each play with the player's last name
    player_plays = plays[plays['Description'].str.contains(Last_Name, regex=False)]

    # The batter of a play always appears before any semi-colons, so we remove everything after any semi-colons
    player_plays = player_plays['Description'].str.replace(";.*", "", regex=True)
    player = pd.DataFrame(data={'Description': player_plays})

    # Extract the name of the batter (first or last), which is always the first word in the play
    player['Name'] = player['Description'].str.extract('^([A-Za-z]+)')

    # Outcomes, locations, and unwanted plays that we want to extract
    outcomes = "grounded|muffed throw|error|line|lined|lined|flied|force|single|pop|double|triple|home|choice|out at|foul|bunt"
    locations = "1b|2b|3b| ss| p | p\\.| p\\,| c | c\\.| c\\,|catcher|pitcher|lf|rf|cf|shortstop|center|left|right|left center|right field line|lf line|rf line|left field line|right center|through the left side|through the right side|middle|1B line|3B line|third base|first base|second base"
    unwanted = "picked off|caught stealing|struck"

    # Following three lines create three columns of lists
    player['Outcome_List'] = player['Description'].str.findall(outcomes)
    player['Location_List'] = player['Description'].str.findall(locations)
    player['Unwanted'] = player['Description'].str.findall(unwanted)

    # Drop rows where `Unwanted` list is not empty and where `Outcome` or `Location` list is empty
    player = player[(player['Unwanted'].str.len() == 0) & (player['Outcome_List'].str.len() != 0) 
                & (player['Location_List'].str.len() != 0)]
    player.drop(columns='Unwanted', inplace=True)

    # Drop rows where batter is not the player of interest
    player = player[(player['Name'] == First_Name) | (player['Name'] == Last_Name)]

    # Extract the first elements of `Outcome_List` and `Location_List` from each row
    player.loc[:, 'Outcome'] = player['Outcome_List'].apply(lambda x: x[0])
    player.loc[:, 'Location'] = player['Location_List'].apply(lambda x: x[0])

    player.drop(columns=['Outcome_List', 'Location_List'], inplace=True)

    # Create a new column for merging `player` with `points`
    player['Event'] = player['Outcome'] + ' ' + player['Location']

    player = player[player['Event'].isin(points['Event'])]

    return(player)


if __name__ == "__main__":
    # team_codes = load_codes()
    # print(team_codes.to_csv())
    roster = load_roster(755, 15204)
    print(roster.to_csv())
    # ##This takes a while to run
    # year_codes = [15204, 14781, 12973]
    # pbp_links = []

    # for year in year_codes:
    #     links = get_links(755, year)
    #     pbp_links = pbp_links + links

    # plays = play_scrape(755, pbp_links)
    # points = load_points('Graphical Point.csv')
    # player = spray_info(plays, 'Caleb', 'Durbin')
    # print(player)