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
	
	def setModelNumber( self, modelNumber ):
		"""
		define method.
		设置模型编号
		"""
		if not hasattr( self, "cell" ):
			self.cellData[ "modelNumber" ] = modelNumber
		else:
			self.cell.setModelNumber( modelNumber )

	def onRemoveBuilding( self ):
		"""
		define method.
		建筑物被删除		
		"""
		if hasattr( self, "cell" ):
			self.destroyCellEntity()
		else:
			self.destroy()

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		pass
				
# NPC.py
