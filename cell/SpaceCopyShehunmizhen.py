# -*- coding: gb18030 -*-
from SpaceCopyMaps import SpaceCopyMaps
import BigWorld
import Const

class SpaceCopyShehunmizhen( SpaceCopyMaps ):
	
	def __init__(self):
		"""
		���캯����
		"""
		SpaceCopyMaps.__init__( self )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		�˳�
		"""
		SpaceCopyMaps.onLeaveCommon( self, baseMailbox, params )

	def shownDetails( self ):
		"""
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			15: ʣ��Boss/Boss����
		]
		"""
		# ��ʾʣ��С�֣����ɣ�ʣ��BOSS��ʣ��ʱ�䡣 
		return [ 0, 17 ]

	def onPlayerReqEnter( self, actType, playerMB, playerDBID, pos, direction ):
		"""
		define method
		�����������븱��
		"""
		if self.checkSpaceIsFull():
			playerMB.client.onStatusMessage( csstatus.SPACE_COOY_YE_WAI_ENTER_FULL, "" )
		else:
			spaceMapsInfos = self.getScript().getSpaceBirth( 0 )	# �������ƽ̨
			className, pos, direction = spaceMapsInfos[0], spaceMapsInfos[1], spaceMapsInfos[2]
			playerMB.cell.onSpaceCopyTeleport( actType, className, pos, direction, not( playerDBID in self._enterRecord ) )