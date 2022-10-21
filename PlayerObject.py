import pandas as pd
import numpy as np
from datetime import datetime


class PlayerObject:
	def __init__(self, in_player_name):
		self.name = in_player_name
		self.team = ''
		self.points = 0
		self.picks_dict = {}
		self.longest_streak = 0
		self.current_streak = 0

	def add_pick(self, in_week_num: int, in_weekly_pick: str):
		self.picks_dict[in_week_num] = in_weekly_pick
