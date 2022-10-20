import streamlit as st
import pandas as pd
import numpy as np
import requests
import PlayerObject

###################################
# Variables
###################################
import variables as v
players = []


###################################
# Functions
###################################
# Find teams in the picks_df which match the input string and add to the teams dictionary
def find_matching_users(in_row: str):
	team_mask = v.picks_df['Team'] == in_row
	team_names = v.picks_df.loc[team_mask]
	name_array = team_names['Name'].to_numpy()
	v.teams_dict[in_row] = name_array


# Input: Name of the player
# Output: A PlayerObject populated with Name, Team, previous picks
# Assumptions: v.picks_df is populated from Google Sheet, but not yet translated (from get_sheets_info)
def populate_player_object(in_player_name: str):
	pass


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

	# Create teams dictionary
	team_names = v.picks_df['Team'].unique()
	vector_function = np.vectorize(find_matching_users)
	vector_function(team_names)
	# Create Player Objects
	player_names = v.picks_df['Name'].unique()
	player_vector_function = np.vectorize(populate_player_object)
	player_vector_function(player_names)

	v.picks_df.drop(columns=['Team'], inplace=True)
	return v.picks_df.set_index('Name').T.to_dict('list')


# Lookup the current week number through API
def get_week_num() -> int:
	response = requests.get(v.season_url)
	season = response.json()
	week_num = season['type']['week']['number']
	return week_num


###################################
# Execution
###################################
st.title('Player Information')

# Find the current week of games
curr_week = get_week_num()
player_form = st.form('Pick a Player')
player = player_form.selectbox('Player:', options=['Bob', 'Sue'])
go_button = player_form.form_submit_button(label='Get info')

if go_button:
	st.header('Info')
	v.picks_dict = get_sheets_info(v.tracker_sheet_team_info_tab_name)
	st.write('Table with name, team, total points, longest streak, current streak')
	st.header('This week')
	st.write('Table with previous picks and win/loss')
	st.write('Matchups for this week and who are the favorites')
