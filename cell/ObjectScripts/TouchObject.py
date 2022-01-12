# -*- coding: gb18030 -*-
#
# $Id:$

from NPCObject import NPCObject
import csconst

class TouchObject( NPCObject ):
	"""
	NPC基类，点击后触发某事件
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPCObject.__init__( self )

	def touch( self, selfEntity ):
		"""
		被触摸
		"""
		if selfEntity.queryTemp( "touch", False ):
			return

		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( {} )
			selfEntity.setTemp( "touch", True )
			selfEntity.modelNumber += csconst.TOUCH_OBJECT_MODELNUM
