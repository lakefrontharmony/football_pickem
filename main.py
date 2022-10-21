import numpy as np
import requests
from datetime import datetime
import pandas as pd
import streamlit as st

###################################
# Variables
###################################
import variables as v


###################################
# Functions
###################################
# Find teams in the picks_df which match the input string and add to the teams dictionary
def find_matching_users(in_row: str):
	team_mask = v.picks_df['Team'] == in_row
	team_names = v.picks_df.loc[team_mask]
	name_array = team_names['Name'].to_numpy()
	v.teams_dict[in_row] = name_array


# Get team info and player pick info from Google Sheets.
def get_sheets_info(in_tab_name: str) -> dict:
	# Get football teams and create dictionary
	football_teams_df = pd.read_csv(v.tracker_sheet_url + in_tab_name)
	teams_temp_dict = football_teams_df.set_index('TeamUID').T.to_dict('list')
	for uid in teams_temp_dict:
		v.football_teams_dict[uid] = teams_temp_dict[uid][0]

	# Get player weekly picks info
	picks_sheet = pd.read_csv(v.tracker_sheet_url + v.tracker_sheet_weekly_picks_tab_name)
	# Had a random problem with the picks_sheet, so I brute-force converted it to picks_df
	v.picks_df['Name'] = picks_sheet['Name']
	v.picks_df['Team'] = picks_sheet['Team']
	v.picks_df['Week 1'] = picks_sheet['Week 1']
	v.picks_df['Week 2'] = picks_sheet['Week 2']
	v.picks_df['Week 3'] = picks_sheet['Week 3']
	v.picks_df['Week 4'] = picks_sheet['Week 4']
	v.picks_df['Week 5'] = picks_sheet['Week 5']
	v.picks_df['Week 6'] = picks_sheet['Week 6']
	v.picks_df['Week 7'] = picks_sheet['Week 7']
	v.picks_df['Week 8'] = picks_sheet['Week 8']
	v.picks_df['Week 9'] = picks_sheet['Week 9']
	v.picks_df['Week 10'] = picks_sheet['Week 10']
	v.picks_df['Week 11'] = picks_sheet['Week 11']
	v.picks_df['Week 12'] = picks_sheet['Week 12']
	v.picks_df['Week 13'] = picks_sheet['Week 13']
	v.picks_df['Week 14'] = picks_sheet['Week 14']
	v.picks_df['Week 15'] = picks_sheet['Week 15']
	v.picks_df['Week 16'] = picks_sheet['Week 16']
	v.picks_df['Week 17'] = picks_sheet['Week 17']
	v.picks_df['Week 18'] = picks_sheet['Week 18']

	# Create teams dictionary
	team_names = v.picks_df['Team'].unique()
	vector_function = np.vectorize(find_matching_users)
	vector_function(team_names)
	return_df = v.picks_df.drop(columns=['Team'])
	return return_df.set_index('Name').T.to_dict('list')


# Retrieve Football team info from API
def get_teams_info():
	response = requests.get(v.team_list_url)
	all_teams = response.json()
	teams_count = all_teams['count']
	team_counter = 1
	link_counter = 1
	while team_counter <= teams_count:
		team_link = v.team_list_url + '/' + str(link_counter)
		team_response = requests.get(team_link)
		team_object = team_response.json()
		if team_object['isActive'] is True and team_object['isAllStar'] is False:
			team_uid = team_object['uid']
			team_name = team_object['displayName']
			v.football_teams_dict[team_uid] = team_name
			team_counter += 1
		link_counter += 1


# Lookup the current week number through API
def get_week_num() -> int:
	response = requests.get(v.season_url)
	season = response.json()
	week_num = season['type']['week']['number']
	return week_num


# Cycle through the games in a given week to store the winners/losers information.
def get_week_games(in_week_num: int) -> dict:
	results_dict = dict()
	week_num = str(in_week_num)
	week_events_url = v.week_events_url_start + week_num + v.week_events_url_end
	week_response = requests.get(week_events_url)
	all_weeks = week_response.json()
	for week in all_weeks['items']:
		event_link = week['$ref']
		event_response = requests.get(event_link)
		st.write(f'Response:{event_response}')
		event_object = event_response.json()['competitions'][0]
		event_datetime = datetime.strptime(event_object['date'], '%Y-%m-%dT%H:%MZ')
		if event_datetime < v.today_date:
			if 'winner' in event_object['competitors'][0].keys():
				results_dict[event_object['competitors'][0]['uid']] = event_object['competitors'][0]['winner']
				results_dict[event_object['competitors'][1]['uid']] = event_object['competitors'][1]['winner']
	return results_dict


def calculate_player_results() -> pd.DataFrame:
	return_df = pd.DataFrame()
	v.has_curr_week_game_happened_for_player['Dummy'] = range(0, 1)
	return_df['Week'] = range(1, 19)
	v.display_df['Week'] = range(1, 19)
	for player in v.picks_dict:
		return_df[player] = 0
		v.display_df[player] = " "
		v.has_curr_week_game_happened_for_player[player] = False
		for week_num in v.weekly_results_dict:
			week_results = v.weekly_results_dict[week_num]
			week_pick = v.picks_dict[player][week_num-1]
			# Verify that the pick has been entered for this week
			if type(week_pick) == str:
				# Verify that the results of the game for that week exist
				if week_pick in week_results.keys():
					if week_num == curr_week:
						v.has_curr_week_game_happened_for_player[player] = True
					if week_results[week_pick] is True:
						return_df.at[week_num-1, player] = 1
						v.display_df.at[week_num-1, player] = f'{v.football_teams_dict[week_pick]} - WIN'
					else:
						return_df.at[week_num-1, player] = 0
						v.display_df[player] = v.display_df[player].astype(str)
						v.display_df.at[week_num - 1, player] = f'{v.football_teams_dict[week_pick]} - LOSS'
				else:
					v.display_df.at[week_num - 1, player] = f'{v.football_teams_dict[week_pick]}'
	v.has_curr_week_game_happened_for_player.drop(columns=['Dummy'], inplace=True)
	return return_df


# Sum the totals for each player from all weeks.
def calc_player_totals() -> pd.DataFrame:
	return_df = pd.DataFrame()
	# This is a dummy column to force the shape of the Dataframe (brute force)
	return_df['Totals'] = range(0, 1)
	for player in v.picks_dict:
		return_df[player] = v.scores_df[player].sum()
	# Drop the dummy column
	return_df.drop(columns=['Totals'], inplace=True)
	return return_df


# Sum the totals for each team of players (not Football teams).
def calc_team_totals() -> pd.DataFrame:
	return_df = pd.DataFrame()
	# This is a dummy column to force the shape of the Dataframe (brute force)
	return_df['Dummy'] = range(0, 1)
	for team in v.teams_dict:
		team_total = 0
		for team_player in v.teams_dict[team]:
			team_total += v.scores_df[team_player].sum()
		return_df.at[0, team] = team_total
		return_df[team] = return_df[team].astype(int)
	# Drop the dummy columns
	return_df.drop(columns=['Dummy'], inplace=True)
	# Translate the table and add the entry order and rank columns.
	return_df = return_df.T
	return_df.reset_index(inplace=True)
	return_df.rename(columns={'index': 'Team Name'}, inplace=True)
	return_df.rename(columns={0: 'Points'}, inplace=True)
	return_df['Entry Order'] = range(0, len(return_df.index))
	return_df.sort_values(by=['Points'], ascending=[False], ignore_index=True, inplace=True)

	return_df['Rank'] = range(1, len(return_df.index)+1)
	rank_number = 1
	row_number = 0
	saved_points = 0
	for index, team_entry in return_df.iterrows():
		row_number += 1
		if team_entry['Points'] == saved_points:
			return_df.at[index, 'Rank'] = rank_number
		else:
			return_df.at[index, 'Rank'] = row_number
			rank_number = row_number
			saved_points = team_entry['Points']

	return_df.sort_values(by=['Entry Order'], ascending=[True], ignore_index=True, inplace=True)
	return_df = return_df[['Entry Order', 'Rank', 'Team Name', 'Points']]
	return_df.set_index(['Entry Order'], inplace=True)
	return return_df


def rank_players() -> pd.DataFrame:
	return_rank_df = pd.DataFrame(columns=['Entry Order', 'Player', 'Rank',
										   'Total Points', 'Longest Streak', 'Curr Win Streak'])
	entry_order = 1
	for player in v.picks_df['Name']:
		player_df = calculate_streak_lengths(v.scores_df[player].iloc[0:int(curr_week)], player)
		total_points = player_df[player].sum()
		max_streak = 0
		if len(player_df['streak_counter'].loc[player_df[player] == 1]) > 0:
			max_streak = max(player_df['streak_counter'].loc[player_df[player] == 1])
		curr_win_streak = 0

		if v.has_curr_week_game_happened_for_player[player].values[0]:
			if player_df[player].iloc[-1] == 1:
				curr_win_streak = player_df['streak_counter'].iloc[-1]
		else:
			if curr_week > 1:
				if player_df[player].iloc[-2] == 1:
					curr_win_streak = player_df['streak_counter'].iloc[-2]

		player_dict = {'Entry Order': entry_order, 'Player': player, 'Rank': 1,
					   'Total Points': total_points, 'Longest Streak': max_streak, 'Curr Win Streak': curr_win_streak}
		return_rank_df.loc[len(return_rank_df.index)] = player_dict
		entry_order += 1
	return_rank_df = return_rank_df.sort_values(by=['Total Points', 'Longest Streak', 'Curr Win Streak'],
	  											ascending=[False, False, False], ignore_index=True)
	return_rank_df = calculate_rank_numbers(return_rank_df)
	return_rank_df = return_rank_df.sort_values(by=['Entry Order'],
												ascending=[True], ignore_index=True)
	return_rank_df.set_index(['Player'], inplace=True)
	return return_rank_df


def calculate_streak_lengths(in_results: pd.Series, column_name: str) -> pd.DataFrame:
	streaks = in_results.to_frame()
	streaks['start_of_streak'] = streaks[column_name].ne(streaks[column_name].shift())
	streaks['streak_id'] = streaks['start_of_streak'].cumsum()
	streaks['streak_counter'] = streaks.groupby('streak_id').cumcount() + 1
	return pd.concat([in_results, streaks['streak_counter']], axis=1)


def calculate_rank_numbers(in_df: pd.DataFrame) -> pd.DataFrame:
	rank_number = 1
	row_number = 0
	saved_points = 0
	saved_long_streak = 0
	saved_curr_win_streak = 0
	for index, player_entry in in_df.iterrows():
		row_number += 1
		if (player_entry['Total Points'] == saved_points) & (player_entry['Longest Streak'] == saved_long_streak) & \
				(player_entry['Curr Win Streak'] == saved_curr_win_streak):
			in_df.at[index, 'Rank'] = rank_number
		else:
			in_df.at[index, 'Rank'] = row_number
			rank_number = row_number
			saved_points = player_entry['Total Points']
			saved_long_streak = player_entry['Longest Streak']
			saved_curr_win_streak = player_entry['Curr Win Streak']

	return in_df


###################################
# Execution
###################################
st.title("Football Pick'em Tracker")

# Find the current week of games
curr_week = get_week_num()

load_form = st.form('Show Calculations')
load_form.write('Click the button below to see picks and weekly results')
curr_week = load_form.selectbox('Select A Week to View Results', options=range(1, curr_week+1), index=curr_week-1)
go_button = load_form.form_submit_button(label='Get info')

if go_button:
	with st.expander('DATA BUILD', expanded=True):
		st.header('Prepping Calcs...')
		st.write('Retrieving Player Picks...')
		v.picks_dict = get_sheets_info(v.tracker_sheet_team_info_tab_name)
		st.write('picks_dict:')
		st.write(v.picks_dict)
		# Retrieve team info from API's (commented as this is less efficient than getting from Google Sheet)
		# st.write('Getting team info...')
		# get_teams_info()
		st.write('Getting weekly info...')
		# Cycle through each week and find the winners from each game
		for week in range(1, curr_week+1):
			weekly_results = get_week_games(week)
			v.weekly_results_dict[week] = weekly_results
		st.write('Prep completed...')

		st.header('Starting Calculations...')
		st.write('Calculating results from each game...')
		v.scores_df = calculate_player_results()
		st.write('Calculating player totals...')
		player_totals = calc_player_totals()
		v.ranking_df = rank_players()
		st.write('Calculating team totals...')
		teams_totals = calc_team_totals()
		st.write('Calculations completed...')

	st.subheader(f'Results as of Week {curr_week}')
	st.write('Use the "View Full Screen" buttons to the right of each table to expand your view')
	st.subheader('Team Totals')
	st.write(teams_totals)
	st.subheader('Player Ranking')
	st.write(v.ranking_df)
	st.subheader('Weekly Picks')
	st.write(v.display_df.astype(str).T)
	st.subheader('Weekly Points')
	st.write(v.scores_df.T)
