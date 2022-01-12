# -*- coding: gb18030 -*-
#
# $Id: QuestBox.py,v 1.1 2007-12-13 01:51:17 zhangyuxing Exp $



import BigWorld
from bwdebug import *
from NPCObject import NPCObject

class QuestBox( NPCObject ):
	"""
	QuestBox基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPCObject.__init__( self )

# QuestBox.py