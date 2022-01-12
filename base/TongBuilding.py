# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC����
"""

import BigWorld
from bwdebug import *
import csdefine
from NPC import NPC

class TongBuilding( NPC ):
	"""
	��Ὠ�������
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
	
	def setModelNumber( self, modelNumber ):
		"""
		define method.
		����ģ�ͱ��
		"""
		if not hasattr( self, "cell" ):
			self.cellData[ "modelNumber" ] = modelNumber
		else:
			self.cell.setModelNumber( modelNumber )

	def onRemoveBuilding( self ):
		"""
		define method.
		�����ﱻɾ��		
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
