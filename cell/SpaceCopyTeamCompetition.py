# -*- coding: gb18030 -*-
from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import random

class SpaceCopyTeamCompetition( SpaceCopy ):
	
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.client.onTeamCompetitionEnd()
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )