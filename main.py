import numpy as np
import requests
from datetime import datetime
import pandas as pd
import streamlit as st

# scoreboard_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
team_list_url = 'https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2022/teams'
season_url = 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2022?lang=en&region=us'
week_events_url_start = 'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2022/types/2/weeks/'
tracker_sheet_url = 'https://docs.google.com/spreadsheets/d/1XLPDd43v4ASAIDB_IVI0TU6IQmdqiPuueII3Xp9rOFQ/gviz/tq?tqx=out:csv&sheet='
tracker_sheet_team_info_tab_name = 'TeamInfo'
tracker_sheet_weekly_picks_tab_name = 'WeeklyPicks'
football_teams_dict = dict()
picks_dict = dict()
teams_dict = dict()
weekly_results_dict = dict()
picks_df = pd.DataFrame()
today_date = datetime.today()


###################################
# Functions
###################################
def find_matching_users(in_row: str):
	team_mask = picks_df['Team'] == in_row
	team_names = picks_df.loc[team_mask]
	name_array = team_names['Name'].to_numpy()
	teams_dict[in_row] = name_array


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
	st.write('Generated Teams...')
	picks_df.drop(columns=['Team'], inplace=True)
	return picks_df.set_index('Name').T.to_dict('list')


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


def get_week_num() -> int:
	response = requests.get(season_url)
	season = response.json()
	curr_week = season['type']['week']['number']
	return curr_week


def get_week_games(in_week_num: int) -> dict:
	results_dict = dict()
	week_num = str(in_week_num)
	week_events_url_end = '/events?lang=en&region=us'
	week_events_url = week_events_url_start + week_num + week_events_url_end
	week_response = requests.get(week_events_url)
	all_weeks = week_response.json()
	for week in all_weeks['items']:
		event_link = week['$ref']
		event_response = requests.get(event_link)
		event_object = event_response.json()['competitions'][0]
		event_datetime = datetime.strptime(event_object['date'], '%Y-%m-%dT%H:%MZ')
		if event_datetime < today_date:
			results_dict[event_object['competitors'][0]['uid']] = event_object['competitors'][0]['winner']
			results_dict[event_object['competitors'][1]['uid']] = event_object['competitors'][1]['winner']
	return results_dict


def calculate_player_totals():
	for player in picks_dict:
		for week_num in weekly_results_dict:
			week_results = weekly_results_dict[week_num]
			week_pick = picks_dict[player][week_num-1]
			if week_results[week_pick] is True:
				st.write(f'{player} got a point for {week_pick} in week {week_num}')
		st.write(picks_dict[player])


###################################
# Execution
###################################
# Get all teams uid and name and store in to team dictionary
load_form = st.form('Show Calculations')
go_button = load_form.form_submit_button(label='Get info')

if go_button:
	st.write('Getting Google Sheet...')
	picks_dict = get_sheets_info()
	st.write('Picks Info...')
	st.write(picks_dict)
	st.write('Generated Player Picks...')

	# st.write('Getting team info...')
	# get_teams_info()

	st.write('Getting current week...')
	curr_week = get_week_num()

	st.write('Getting weekly info...')
	# Cycle through each week and find the winners from each game
	for week in range(1, curr_week+1):
		weekly_results = get_week_games(week)
		weekly_results_dict[week] = weekly_results
	st.write(weekly_results_dict)

	st.write('Gathered all info...')
	st.write('Calculating player totals...')
	calculate_player_totals()
