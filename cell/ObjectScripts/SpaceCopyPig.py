# -*- coding: gb18030 -*-

import cschannel_msgs
import csstatus
import csconst
import Const
import time
import csdefine
import BigWorld
from SpaceCopyTeam import SpaceCopyTeam

CLOSE_DU_DU_ZHU = 1003
SPACE_LIFE_END_KICK_PLAYER_TIME = 30		# 副本时间到达后，玩家被强制传出的时间（秒）
SPACE_SUCCESS_KICK_PLAYER_TIME = 90		# Boss死亡，玩家被强制传出的时间（秒）

class SpaceCopyPig( SpaceCopyTeam ):
	"""
	嘟嘟猪副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )
		self.recordKey = "duduzhu_record"
		self._spaceLife = 1
		self.bossIDs = []

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTeam.load( self, section )
		self._spaceLife = section[ "Space" ][ "spaceLife" ].asInt 			# 副本时间(分钟)
		self.bossIDs = section[ "Space" ][ "bossID" ].asString.split(";")	# 副本中BossIDs

	def packedDomainData( self, player ):
		"""
		"""
		data = SpaceCopyTeam.packedDomainData( self, player )
		
		captain = BigWorld.entities.get( player.captainID )
		if captain:
			level = captain.level
		else:
			level = player.level
		data["copyLevel"] = level
		data["difficulty"] = player.popTemp( "EnterSpaceDuDuZhu", 0 )
		data["spaceLabel"] = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY )
		data["position"] = 	player.position

		return data

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id

		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		# 进入次数统计
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_DU_DU_ZHU, self.recordKey )
		
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		
		# 第一次进入副本
		if not selfEntity.queryTemp( "tempHaveCome", False ):
			selfEntity.setTemp( "tempHaveCome", True )
			selfEntity.base.spawnMonsters( { "level": selfEntity.params["copyLevel"] } )
			selfEntity.setTemp( "copyStartTime", time.time() )	# 副本开始时间
			selfEntity.setTemp( "SPACE_KICK_PLAYER_TIME", SPACE_LIFE_END_KICK_PLAYER_TIME  )
			selfEntity.addTimer( self._spaceLife * 60 - SPACE_LIFE_END_KICK_PLAYER_TIME, 0, CLOSE_DU_DU_ZHU )

		# 副本界面使用
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, self._spaceLife * 60 )

	def onOneTypeMonsterDie( self, selfEntity, monsterID, className ):
		"""
		根据不同的className处理不同怪物死亡
		"""
		
		if className in self.bossIDs: 
			bossCount = selfEntity.queryTemp( "bossCount" ) - 1
			selfEntity.setTemp( "bossCount", bossCount )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, bossCount )
			if bossCount <= 0: # Boss死亡,副本关闭
				selfEntity.setTemp( "SPACE_KICK_PLAYER_TIME", SPACE_SUCCESS_KICK_PLAYER_TIME )
				self.closeSpace( selfEntity )
		else:
			allMonsterCount = selfEntity.queryTemp( "allMonsterCount" ) - 1 
			selfEntity.setTemp( "allMonsterCount", allMonsterCount )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, allMonsterCount )
			if allMonsterCount == 0: # 小怪全部死亡，刷Boss
				selfEntity.base.spawnMonsters( { "bossIDs": self.bossIDs, "level": selfEntity.params["copyLevel"] } )
				self.broadcastInCopy( selfEntity, cschannel_msgs.BCT_DUDUZHU_BOSS_NOTIFY )

	def broadcastInCopy( self, selfEntity, msg ):
		"""
		副本中广播
		"""
		for baseMailBox in selfEntity._players:
			baseMailBox.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msg, [] )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		时间控制器
		"""
		if userArg == CLOSE_DU_DU_ZHU:
			self.closeSpace( selfEntity )
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )

	def closeSpace( self, selfEntity ):
		"""
		关闭副本
		"""
		closeTime = selfEntity.queryTemp( "SPACE_KICK_PLAYER_TIME", 10 )
		for e in selfEntity._players:
			e.client.onStatusMessage( csstatus.SPACE_CLOSE, str( ( closeTime, ) ) )
		
		selfEntity.addTimer( closeTime, 0.0, Const.SPACE_TIMER_ARG_KICK )
		selfEntity.addTimer( closeTime + 5, 0.0, Const.SPACE_TIMER_ARG_CLOSE )
