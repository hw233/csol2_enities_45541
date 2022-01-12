# -*- coding: gb18030 -*-
#
# $Id:$

from NPCObject import NPCObject
import csconst

class TouchObject( NPCObject ):
	"""
	NPC���࣬����󴥷�ĳ�¼�
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPCObject.__init__( self )

	def touch( self, selfEntity ):
		"""
		������
		"""
		if selfEntity.queryTemp( "touch", False ):
			return

		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( {} )
			selfEntity.setTemp( "touch", True )
			selfEntity.modelNumber += csconst.TOUCH_OBJECT_MODELNUM
