# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
import Love3
import BigWorld
from bwdebug import *


class SpaceCopyTeamChallenge( SpaceCopy ):
	# 组队擂台
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		