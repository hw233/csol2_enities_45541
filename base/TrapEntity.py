# -*- coding: gb18030 -*-
#
# $Id: TrapEntity.py



import BigWorld
from bwdebug import *
from NPCObject import NPCObject

class TrapEntity( NPCObject ):
	"""
	QuestBox基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPCObject.__init__( self )

# TrapEntity.py