import requests
import json
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
teams_dict = dict()
weeks_dict = dict()
today_date = datetime.today()


###################################
# Functions
###################################
def get_sheets_info():
	teams_dict = pd.read_csv(tracker_sheet_url + tracker_sheet_team_info_tab_name)
	st.write(teams_dict)


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
		if team_object['isActive'] == True and team_object['isAllStar'] == False:
			team_uid = team_object['uid']
			team_name = team_object['displayName']
			teams_dict[team_uid] = team_name
			# print(f'COUNT:{team_counter}, UID="{team_uid}", NAME="{team_name}"')
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
		event_uid = event_object['uid']
		event_datetime = datetime.strptime(event_object['date'], '%Y-%m-%dT%H:%MZ')
		if event_datetime < today_date:
			print(f'Gathering event:{event_uid} for week {in_week_num}')
			results_dict[event_object['competitors'][0]['uid']] = event_object['competitors'][0]['winner']
			results_dict[event_object['competitors'][1]['uid']] = event_object['competitors'][1]['winner']
	return results_dict


###################################
# Execution
###################################

# Get all teams uid and name and store in to team dictionary
load_form = st.form('Start Calcs')
go_button = load_form.form_submit_button(label='Get info')

if go_button:
	st.write('Getting Google Sheet...')
	get_sheets_info()

	# st.write('Getting team info...')
	# get_teams_info()

	st.write('Getting current week...')
	# curr_week = get_week_num()

	st.write('Getting weekly info...')
	# Cycle through each week and find the winners from each game
	# for week in range(1, curr_week+1):
	#	weekly_results = get_week_games(week)
	#	weeks_dict[week] = weekly_results
	#print(weeks_dict)
	st.write('Gathered all info...')