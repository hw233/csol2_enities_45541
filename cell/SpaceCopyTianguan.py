# -*- coding: gb18030 -*-
#
# $Id: SpaceCopyTianguan.py,v 1.3 2008-08-20 01:21:11 zhangyuxing Exp $




from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import Const
import time

LEASE_MEMBER_AMOUNT = 3				#���ٶ����Ա
MAX_MEMBER_AMOUNT = 5				#�������Ա

class SpaceCopyTianguan( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopy.__init__( self )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopy.onLeaveCommon( self, baseMailbox, params )
		
		if len( self._players ) == 0:
			self.addTimer( 10.0, 0, Const.SPACE_COPY_CLOSE_CBID )
			del BigWorld.globalData[self.queryTemp('globalkey')]
			
	def setLeaveTeamPlayerMB( self, baseMailbox ):
		"""
		define method
		"""
		self.setTemp( 'leavePMB', baseMailbox )

