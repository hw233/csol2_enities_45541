# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC����
"""

import BigWorld
from bwdebug import *
import csdefine
from Monster import Monster

class TongNagual( Monster ):
	"""
	����ػ���
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Monster.__init__( self )
	
	def updateLevel( self, level ):
		"""
		define method.
		�������޵ȼ�
		"""
		if level <= 0:
			if hasattr( self, "cell" ):
				self.destroyCellEntity()
			else:
				self.destroy()
		else:
			if hasattr( self, "cell" ):
				self.cell.updateLevel( level )
			else:
				self.cellData[ "level" ] = level

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		pass
		
# TongNagual.py
