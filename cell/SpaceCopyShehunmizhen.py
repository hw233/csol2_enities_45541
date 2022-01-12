# -*- coding: gb18030 -*-
from SpaceCopyMaps import SpaceCopyMaps
import BigWorld
import Const

class SpaceCopyShehunmizhen( SpaceCopyMaps ):
	
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopyMaps.__init__( self )

	def onLeaveCommon( self, baseMailbox, params ):
		"""
		退出
		"""
		SpaceCopyMaps.onLeaveCommon( self, baseMailbox, params )

	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			15: 剩余Boss/Boss总数
		]
		"""
		# 显示剩余小怪，蒙蒙，剩余BOSS，剩余时间。 
		return [ 0, 17 ]

	def onPlayerReqEnter( self, actType, playerMB, playerDBID, pos, direction ):
		"""
		define method
		有玩家请求进入副本
		"""
		if self.checkSpaceIsFull():
			playerMB.client.onStatusMessage( csstatus.SPACE_COOY_YE_WAI_ENTER_FULL, "" )
		else:
			spaceMapsInfos = self.getScript().getSpaceBirth( 0 )	# 进入出生平台
			className, pos, direction = spaceMapsInfos[0], spaceMapsInfos[1], spaceMapsInfos[2]
			playerMB.cell.onSpaceCopyTeleport( actType, className, pos, direction, not( playerDBID in self._enterRecord ) )