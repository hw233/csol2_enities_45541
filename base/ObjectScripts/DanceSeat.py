# -*- coding: gb18030 -*-
#


"""
NPC的基类
"""
from bwdebug import *
from NPC import NPC
import csdefine

class DanceSeat( NPC ):
	"""
	NPC的基类
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPC.__init__( self )