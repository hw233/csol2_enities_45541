# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
import csdefine
from NPC import NPC

class TongBuilding( NPC ):
	"""
	帮会建筑物基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		self.utype = csdefine.ENTITY_TYPE_MISC

	def setModelNumber( self, modelNumber ):
		"""
		define method.
		设置模型编号
		"""
		self.modelNumber = modelNumber
	
# NPC.py
