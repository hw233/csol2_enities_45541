# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from ProximityTransducer import ProximityTransducer
from gbref import rds
import csdefine
import Define

class ChallengeTransducer( ProximityTransducer ):
	"""
	"""
	def __init__( self ):
		ProximityTransducer.__init__( self )
		self.setSelectable( True )

