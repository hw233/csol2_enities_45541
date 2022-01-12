# -*- coding: gb18030 -*-
#
# $Id: CollectPoint.py,v 1.1 10:35 2009-11-30 jiangyi Exp $



import BigWorld
from bwdebug import *
from NPCObject import NPCObject

class CollectPoint( NPCObject ):
	"""
	CollectPoint基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPCObject.__init__( self )

# CollectPoint.py