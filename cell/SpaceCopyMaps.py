# -*- coding: gb18030 -*-
from SpaceCopy import SpaceCopy
import csstatus
import Const

class SpaceCopyMaps( SpaceCopy ):
	"""
	多地图副本
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
	
	def onCloseMapsCopy( self ):
		"""
		define method.
		关闭副本
		"""
		if not self.waitDestroy:
			self.waitDestroy = True
			self.getScript().onCloseMapsCopy( self )
	
	def setCopyKillBoss( self, bossNum ):
		"""
		define method
		设置副本BOSS数量
		"""
		self.copyStatBoss = bossNum
		self.getScript().setCopyKillBoss( self, bossNum )
	
	def setCopyKillMonster( self, monsterNum ):
		"""
		define method
		设置副本小怪数量
		"""
		self.copyStatMonster = monsterNum
		self.getScript().setCopyKillMonster( self, monsterNum )
	
	def getSpaceGlobalKey( self ):
		"""
		获取队伍进入global key
		"""
		spaceType = self.getScript().getSpaceType()
		teamId = self.params['teamID'] if self.params.has_key( "teamID" ) else 0
		if Const.SPACE_COPY_GLOBAL_KEY.has_key( spaceType ):
			return Const.GET_SPACE_COPY_GLOBAL_KEY( spaceType, teamId, self.getScript().difficulty )
		else:
			return ""

	def onAllCopyMonsterkilled( self, spaceName ):
		"""
		define method
		副本中小怪全部被击杀
		"""
		self.getScript().onAllCopyMonsterkilled( self, spaceName )

	def onPlayerReqEnter( self, actType, playerMB, playerDBID, pos, direction ):
		"""
		define method
		有玩家请求进入副本
		"""
		if self.checkSpaceIsFull():
			playerMB.client.onStatusMessage( csstatus.SPACE_COOY_YE_WAI_ENTER_FULL, "" )
		else:
			copyNo = self.getScript().getCopyNo()
			spaceMapsInfos = self.getScript().getSpaceBirth( copyNo )
			pos, direction = spaceMapsInfos[1], spaceMapsInfos[2]
			playerMB.cell.onSpaceCopyTeleport( actType, self.className, pos, direction, not( playerDBID in self._enterRecord ) )