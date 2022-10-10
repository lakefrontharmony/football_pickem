import numpy as np
import requests
from datetime import datetime
import pandas as pd
import streamlit as st

###################################
# Variables
###################################
# Scoreboard link shows the real-time status of this week's games.
# scoreboard_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
team_list_url = 'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2022/teams'
season_url = 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2022?lang=en&region=us'
week_events_url_start = 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2022/types/2/weeks/'
week_events_url_end = '/events?lang=en&region=us'
tracker_sheet_url = 'https://docs.google.com/spreadsheets/d/1XLPDd43v4ASAIDB_IVI0TU6IQmdqiPuueII3Xp9rOFQ/gviz/tq?tqx=out:csv&sheet='
tracker_sheet_team_info_tab_name = 'TeamInfo'
tracker_sheet_weekly_picks_tab_name = 'WeeklyPicks'
football_teams_dict = dict()
picks_dict = dict()
teams_dict = dict()
weekly_results_dict = dict()
picks_df = pd.DataFrame()
scores_df = pd.DataFrame()
display_df = pd.DataFrame()
ranking_df = pd.DataFrame()
today_date = datetime.today()


###################################
# Functions
###################################
# Find teams in the picks_df which match the input string and add to the teams dictionary
def find_matching_users(in_row: str):
	team_mask = picks_df['Team'] == in_row
	team_names = picks_df.loc[team_mask]
	name_array = team_names['Name'].to_numpy()
	teams_dict[in_row] = name_array


# Get team info and player pick info from Google Sheets.
def get_sheets_info() -> dict:
	# Get football teams and create dictionary
	football_teams_df = pd.read_csv(tracker_sheet_url + tracker_sheet_team_info_tab_name)
	teams_temp_dict = football_teams_df.set_index('TeamUID').T.to_dict('list')
	for uid in teams_temp_dict:
		football_teams_dict[uid] = teams_temp_dict[uid][0]

	# Get player weekly picks info
	picks_sheet = pd.read_csv(tracker_sheet_url + tracker_sheet_weekly_picks_tab_name)
	# Had a random problem with the picks_sheet, so I brute-force converted it to picks_df
	picks_df['Name'] = picks_sheet['Name']
	picks_df['Team'] = picks_sheet['Team']
	picks_df['Week 1'] = picks_sheet['Week 1']
	picks_df['Week 2'] = picks_sheet['Week 2']
	picks_df['Week 3'] = picks_sheet['Week 3']
	picks_df['Week 4'] = picks_sheet['Week 4']
	picks_df['Week 5'] = picks_sheet['Week 5']
	picks_df['Week 6'] = picks_sheet['Week 6']
	picks_df['Week 7'] = picks_sheet['Week 7']
	picks_df['Week 8'] = picks_sheet['Week 8']
	picks_df['Week 9'] = picks_sheet['Week 9']
	picks_df['Week 10'] = picks_sheet['Week 10']
	picks_df['Week 11'] = picks_sheet['Week 11']
	picks_df['Week 12'] = picks_sheet['Week 12']
	picks_df['Week 13'] = picks_sheet['Week 13']
	picks_df['Week 14'] = picks_sheet['Week 14']
	picks_df['Week 15'] = picks_sheet['Week 15']
	picks_df['Week 16'] = picks_sheet['Week 16']
	picks_df['Week 17'] = picks_sheet['Week 17']
	picks_df['Week 18'] = picks_sheet['Week 18']

	# Create teams dictionary
	team_names = picks_df['Team'].unique()
	vector_function = np.vectorize(find_matching_users)
	vector_function(team_names)
	picks_df.drop(columns=['Team'], inplace=True)
	return picks_df.set_index('Name').T.to_dict('list')


# Retrieve Football team info from API
def get_teams_info():
	response = requests.get(team_list_url)
	all_teams = response.json()
	teams_count = all_teams['count']
	team_counter = 1
	link_counter = 1
	while team_counter <= teams_count:
		team_link = team_list_url + '/' + str(link_counter)
		team_response = requests.get(team_link)
		team_object = team_response.json()
		if team_object['isActive'] is True and team_object['isAllStar'] is False:
			team_uid = team_object['uid']
			team_name = team_object['displayName']
			football_teams_dict[team_uid] = team_name
			team_counter += 1
		link_counter += 1


# Lookup the current week number through API
def get_week_num() -> int:
	response = requests.get(season_url)
	season = response.json()
	week_num = season['type']['week']['number']
	return week_num


# Cycle through the games in a given week to store the winners/losers information.
def get_week_games(in_week_num: int) -> dict:
	results_dict = dict()
	week_num = str(in_week_num)
	week_events_url = week_events_url_start + week_num + week_events_url_end
	week_response = requests.get(week_events_url)
	all_weeks = week_response.json()
	for week in all_weeks['items']:
		event_link = week['$ref']
		event_response = requests.get(event_link)
		event_object = event_response.json()['competitions'][0]
		event_datetime = datetime.strptime(event_object['date'], '%Y-%m-%dT%H:%MZ')
		if event_datetime < today_date:
			if 'winner' in event_object['competitors'][0].keys():
				results_dict[event_object['competitors'][0]['uid']] = event_object['competitors'][0]['winner']
				results_dict[event_object['competitors'][1]['uid']] = event_object['competitors'][1]['winner']
	return results_dict


# Cycle through each player, getting the score for each week. Return a dictionary of names and arrays of scores.
def calculate_player_results() -> pd.DataFrame:
	return_df = pd.DataFrame()
	return_df['Week'] = range(1, 19)
	display_df['Week'] = range(1, 19)
	for player in picks_dict:
		return_df[player] = 0
		display_df[player] = " "
		for week_num in weekly_results_dict:
			week_results = weekly_results_dict[week_num]
			week_pick = picks_dict[player][week_num-1]
			# Verify that the pick has been entered for this week
			if type(week_pick) == str:
				# Verify that the results of the game for that week exist
				if week_pick in week_results.keys():
					if week_results[week_pick] is True:
						return_df.at[week_num-1, player] = 1
						display_df.at[week_num-1, player] = f'{football_teams_dict[week_pick]} - WIN'
					else:
						return_df.at[week_num-1, player] = 0
						display_df[player] = display_df[player].astype(str)
						display_df.at[week_num - 1, player] = f'{football_teams_dict[week_pick]} - LOSS'
				else:
					display_df.at[week_num - 1, player] = f'{football_teams_dict[week_pick]}'
	return return_df


# Sum the totals for each player from all weeks.
def calc_player_totals() -> pd.DataFrame:
	return_df = pd.DataFrame()
	# This is a dummy column to force the shape of the Dataframe (brute force)
	return_df['Totals'] = range(0, 1)
	for player in picks_dict:
		return_df[player] = scores_df[player].sum()
	# Drop the dummy column
	return_df.drop(columns=['Totals'], inplace=True)
	return return_df


# Sum the totals for each team of players (not Football teams).
def calc_team_totals() -> pd.DataFrame:
	return_df = pd.DataFrame()
	# This is a dummy column to force the shape of the Dataframe (brute force)
	return_df['Totals'] = range(0, 1)
	for team in teams_dict:
		team_total = 0
		for team_player in teams_dict[team]:
			team_total += scores_df[team_player].sum()
		return_df.at[0, team] = team_total
		return_df[team] = return_df[team].astype(int)
	# Drop the dummy column
	return_df.drop(columns=['Totals'], inplace=True)
	return return_df


def rank_players():
	working_rank_df = pd.DataFrame(columns=['Player', 'Longest Streak', 'Curr Win Streak'])
	for player in picks_df['Name']:
		player_df = calculate_streak_lengths(scores_df[player].iloc[0:int(curr_week)], player)
		max_streak = max(player_df['streak_counter'].loc[player_df[player] == 1])
		print(max_streak)


def calculate_streak_lengths(in_results: pd.Series, column_name: str) -> pd.DataFrame:
	streaks = in_results.to_frame()
	streaks['start_of_streak'] = streaks[column_name].ne(streaks[column_name].shift())
	streaks['streak_id'] = streaks['start_of_streak'].cumsum()
	streaks['streak_counter'] = streaks.groupby('streak_id').cumcount() + 1
	st.write(streaks)
	return pd.concat([in_results, streaks['streak_counter']], axis=1)


# TODO: Create ranking of players
# Criteria:
# 1. Longest winning streak
# 2. if still tied after #1, longest CURRENT winning streak
# 3. If still tied after #2, rock/paper/scissors.
# Create a new dataframe with score, longest streak, and current streak columns
# (see https://joshdevlin.com/blog/calculate-streaks-in-pandas/ for calculating streaks.
# Find the biggest number for the longest streak, and find the last number for the current streak.
# Make sure streaks are for wins and not losses.)
# Order the dataframe by score, then longest streak, then current streak.
###################################
# Execution
###################################
st.title("Football Pick'em Tracker")

# Get all teams uid and name and store in to team dictionary
load_form = st.form('Show Calculations')
load_form.write('Click the button below to see picks and weekly results')
go_button = load_form.form_submit_button(label='Get info')

if go_button:
	with st.expander('DATA BUILD', expanded=True):
		st.header('Prepping Calcs...')
		st.write('Retrieving Player Picks...')
		picks_dict = get_sheets_info()
		# Retrieve team info from API's (commented as this is less efficient than getting from Google Sheet)
		# st.write('Getting team info...')
		# get_teams_info()
		st.write('Getting current week...')
		curr_week = get_week_num()
		st.write('Getting weekly info...')
		# Cycle through each week and find the winners from each game
		for week in range(1, curr_week+1):
			weekly_results = get_week_games(week)
			weekly_results_dict[week] = weekly_results
		st.write('Prep completed...')

		st.header('Starting Calculations...')
		st.write('Calculating results from each game...')
		scores_df = calculate_player_results()
		st.write('Calculating player totals...')
		player_totals = calc_player_totals()
		rank_players()
		st.write('Calculating team totals...')
		teams_totals = calc_team_totals()
		st.write('Calculations completed...')

	st.subheader(f'Results as of Week {curr_week}')
	st.write('Use the "View Fullscreen" buttons to the right of each table to expand your view')
	st.subheader('Weekly Picks')
	st.write(display_df.astype(str).T)
	st.subheader('Weekly Points')
	st.write(scores_df.T)
	st.subheader('Player Totals')
	st.write(player_totals.T)
	st.subheader('Team Totals')
	st.write(teams_totals.T)
