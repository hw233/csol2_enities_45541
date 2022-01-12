# -*- coding: gb18030 -*-
#
# 
#

from bwdebug import *
from NPC import NPC
import random
import csdefine
import BigWorld
import csstatus
import ECBExtend

class ProtectTongNPC( NPC ):
	"""
	��������NPC
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
		self.addTimer( 5.0, 3.0, ECBExtend.HEARTBEAT_TIMER_CBID )

	def onProtectTongOver( self ):
		"""
		define method.
		�������
		"""
		self.destroy()
	
	def onSpaceCopyMonsterDead( self ):
		"""
		define method.
		�����Ĺ��ﶼ������
		"""
		self.destroy()
		
	def onHeartbeat( self, timerID, cbID ):
		"""
		����
		"""
		if not BigWorld.globalData.has_key( "AS_ProtectTong" ):
			self.destroy()
		