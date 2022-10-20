import pandas as pd
import numpy as np
from datetime import datetime


class PlayerObject:
	def __init__(self):
		self.team = ''
		self.score = 0
		self.picks = []
		self.longest_streak = 0
		self.current_streak = 0
