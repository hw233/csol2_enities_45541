# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from Monster import Monster

class CallMonster( Monster ):
	"""
	招唤类怪物
	"""
	def __init__( self ):
		Monster.__init__( self )
