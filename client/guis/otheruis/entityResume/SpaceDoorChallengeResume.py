# -*- coding: gb18030 -*-
#

from gbref import rds
from bwdebug import *
from LabelGather import labelGather

class SpaceDoorChallengeResume:
	"""
	传送门描述
	"""
	def __init__( self ):
		"""
		"""
		pass

	def doMsg_( self, entity, window ):
		"""
		"""
		return labelGather.getText( "EntityResume:spaceDoor", "challengeNextGate" )


instance = SpaceDoorChallengeResume()