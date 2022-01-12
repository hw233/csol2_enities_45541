# -*- coding: gb18030 -*-
#
# $Id: Exp $



import BigWorld
from bwdebug import *
import csdefine
from NPC import NPC

class NPCRacehorse( NPC ):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		
