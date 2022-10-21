import streamlit as st
import pandas as pd
import numpy as np
import requests
from PlayerObject import PlayerObject

###################################
# Variables
###################################
import variables as v
players = {}


###################################
# Functions
###################################
# Find teams in the picks_df which match the input string and add to the teams dictionary
def find_matching_users(in_row: str):
	team_names = v.picks_df.loc[v.picks_df['Team'] == in_row]
	name_array = team_names['Name'].to_numpy()
	v.teams_dict[in_row] = name_array


# Input: Name of the player.
# Output: Appended a PlayerObject to "players" list (populated with name, team, previous picks).
# Assumptions: v.picks_df is populated from Google Sheet. curr_week variable has been populated.
def populate_player_object(in_player_name: str):
	curr_player = PlayerObject(in_player_name)
	player_row = v.picks_df.loc[v.picks_df['Name'] == in_player_name]
	player_row_index = v.picks_df[v.picks_df['Name'] == in_player_name].index.values[0]
	curr_player.team = player_row.at[player_row_index, 'Team']
	for week_num in range(1, curr_week):
		week_col_name = "Week " + str(week_num)
		weekly_pick = player_row[week_col_name]
		curr_player.add_pick(week_num, weekly_pick)
	players[in_player_name] = curr_player


# Input: Google Sheet tab name
# Output: picks_df populated with weekly picks tab data from Google Sheet.
# Assumptions:
def get_sheets_info(in_sheet_name: str) -> dict:
	# Get football teams and create dictionary
	football_teams_df = pd.read_csv(v.tracker_sheet_url + in_sheet_name)
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

	return_df = v.picks_df.drop(columns=['Team'])
	return return_df.set_index('Name').T.to_dict('list')


# Create teams dictionary
def create_teams_dictionary():
	team_names = v.picks_df['Team'].unique()
	vector_function = np.vectorize(find_matching_users)
	vector_function(team_names)


# Create Player Objects
def create_player_list():
	player_names = v.picks_df['Name'].unique()
	player_vector_function = np.vectorize(populate_player_object)
	player_vector_function(player_names)


# Lookup the current week number through API
def get_week_num() -> int:
	response = requests.get(v.season_url)
	season = response.json()
	week_num = season['type']['week']['number']
	return week_num


def build_player_display(in_name: str) -> pd.DataFrame:
	return_df = pd.DataFrame(columns=['Item', 'Value'])
	player_object: PlayerObject = players[in_name]
	return_df = pd.concat([return_df, pd.Series({'Item': 'Name',
												 'Value': player_object.name}).to_frame().T])
	return_df = pd.concat([return_df, pd.Series({'Item': 'Team',
												 'Value': player_object.team}).to_frame().T])
	return_df = pd.concat([return_df, pd.Series({'Item': 'Total Points',
												 'Value': str(player_object.points)}).to_frame().T])
	return_df = pd.concat([return_df, pd.Series({'Item': 'Longest Streak',
												 'Value': str(player_object.longest_streak)}).to_frame().T])
	return_df = pd.concat([return_df, pd.Series({'Item': 'Current Streak',
												 'Value': str(player_object.current_streak)}).to_frame().T])
	return_df.reset_index(inplace=True, drop=True)
	return return_df


def build_weekly_pick_display(in_player_name: str) -> pd.DataFrame:
	return_df = pd.DataFrame([[in_player_name]], columns=['Name'])
	player_row: pd.Series = v.picks_df.loc[v.picks_df['Name'] == in_player_name]
	player_results = player_row.T.drop(labels=['Name', 'Team'])
	player_results.rename(index={0: 'Picks'}, inplace=True)
	st.write(player_results)
	return_df = v.football_teams_dict[player_results['Picks']]
	# return_series = player_row.drop(labels=['Team'])
	# for week_num in range(1, curr_week):
	#
	return return_df


###################################
# Execution
###################################
st.title('Player Information')

# Find the current week of games
curr_week = get_week_num()
v.picks_dict = get_sheets_info(v.tracker_sheet_team_info_tab_name)
create_teams_dictionary()
create_player_list()
player_form = st.form('Pick a Player')
player = player_form.selectbox('Player:', options=v.picks_df['Name'].unique())
go_button = player_form.form_submit_button(label='Get info')

if go_button:
	st.header('Info')
	st.write(build_player_display(player))
	st.header('This week')
	st.write('Weekly Picks')
	st.write(build_weekly_pick_display(player))
	st.write('Matchups for this week and who are the favorites')
