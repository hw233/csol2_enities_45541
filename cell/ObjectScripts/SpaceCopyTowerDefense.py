# -*- coding: gb18030 -*-

from SpaceCopyTeam import SpaceCopyTeam
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import time
from GameObject import GameObject
from CopyContent import CopyContent
from CopyContent import CCWait
from CopyContent import CCKickPlayersProcess
from CopyContent import NEXT_CONTENT
from CopyContent import CCEndWait
import csdefine
import ECBExtend
import csconst
import Const

CLOSE_COPY_WIN_USERARG = 1
CLOSE_COPY_LOSE_USERARG = 2
SPAWN_MONSTER_USERARG = 3

CLOSE_COPY_TIME = 60.0



class SpaceCopyTowerDefense( SpaceCopyTeam ):
	"""
	塔防副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )
		self.recordKey = "tower_defense_record"
		self.spawnMonsterBatchNum = 0
		self.spawnMonsterIntervels = 0.0
		self.lieZhenMonstersIDList = []
		self.lieZhenMonstersNum = []
		self.aiCommandIDList = []
		self.emergeList = []
		self.bossClassName = ""
	
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTeam.load( self, section )
		if section[ "Space" ].has_key( "spawnMonsterBatchNum" ):
			self.spawnMonsterBatchNum = section[ "Space" ][ "spawnMonsterBatchNum" ].asInt
		if section[ "Space" ].has_key( "spawnMonsterIntervels" ):
			self.spawnMonsterIntervels = section[ "Space" ][ "spawnMonsterIntervels" ].asFloat
		if section[ "Space" ].has_key( "lieZhenMonstersID" ):
			self.lieZhenMonstersIDList = section[ "Space" ][ "lieZhenMonstersID" ].asString.split( ";" )
		if section[ "Space" ].has_key( "lieZhenMonstersNum" ):
			self.lieZhenMonstersNum = section[ "Space" ][ "lieZhenMonstersNum" ].asInt
		if section[ "Space" ].has_key( "aiCommandIDs" ):
			self.aiCommandIDList = section[ "Space" ][ "aiCommandIDs" ].asString.split( ";" )
		if section[ "Space" ].has_key( "energy" ):
			self.energyList = section[ "Space" ][ "energy" ].asString.split( ";" )
		if section[ "Space" ].has_key( "bossClassName" ):
			self.bossClassName = section[ "Space" ][ "bossClassName" ].asString
		

	def packedDomainData( self, entity ):
		"""
		创建domain时，传递参数
		"""
		d = { 'dbID' : entity.databaseID, "spaceKey":entity.databaseID }
		if entity.teamMailbox:
			# 已加入队伍，取队伍数据
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			d["mailbox"] = entity.base
			# 取得所有队员basemailboxs
			teamMemberMailboxsList = entity.getTeamMemberMailboxs()
			if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
				teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
			d["membersMailboxs"] = teamMemberMailboxsList

			# 设置队伍平均等级、最高等级（队伍等级为队长等级，最高等级为队长等级加3）
			if entity.isTeamCaptain():
				d["teamLevel"] = entity.level
				d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )

				if entity.queryTemp( "onEnterShenGuiMiJing" ) == entity.teamMailbox.id:	# 如果队长进入过副本
					d["isCallTeamMember"] = False
				else:
					d["isCallTeamMember"] = True

			d[ "difficulty" ] = entity.popTemp( "ShenGuiMiJingType" )
			d["spaceKey"] = entity.teamMailbox.id

		return d

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyTeam.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id

		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		进入
		"""
		if baseMailbox is not None and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_TOWER_DEFENSE, self.recordKey )
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		self.spawnOneBatchMonster( selfEntity )
		if baseMailbox:
			baseMailbox.client.enterTowerDefenceSpace()

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		if baseMailbox:
			baseMailbox.client.endTowerDefenseSpaceSkill()
		
	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == CLOSE_COPY_WIN_USERARG:		# 关闭副本，获胜
			self.kickAllPlayer( selfEntity )
			self.closeCopy( selfEntity, 1 )

		elif userArg == CLOSE_COPY_LOSE_USERARG:		# 关闭副本，失败
			self.closeCopy( selfEntity, 0 )

		elif userArg == SPAWN_MONSTER_USERARG:
			self.spawnOneBatchMonster( spaceEntity )
			
		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		DEBUG_MSG( "Role %i kill a enemy." % role.id )
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		role.addTimer( 7.0, 0, ECBExtend.ROLE_REVIVE_TIMER )

	def spawnMonster( self, spaceEntity, BatchNum ):
		spawnPointMBList = spaceEntity.queryTemp( "towerDefenseSpawnPoint" )
		if spawnPointMBList:
			for spawnPointMB in spawnPointMBList:
				self.noticePlayerInfo( spaceEntity, cschannel_msgs.TOWER_DEFENSE_SPAWN_MONSTER_NOTICE % BatchNum )
				if BatchNum == self.spawnMonsterBatchNum:
					self.noticePlayerInfo( spaceEntity, cschannel_msgs.TOWER_DEFENSE_SPAWN_MONSTER_NOTICE_1 )
				
				params = {}
				params[ "level" ] = spaceEntity.teamMaxLevel
				params[ "batchNum" ] = BatchNum
				spawnPointMB.cell.createEntity( spaceEntity, spaceEntity.teamMaxLevel, BatchNum )

	def spawnOneBatchMonster( self, spaceEntity ):
		currentBatch = spaceEntity.queryTemp( "currentBatch", 1 )
		if currentBatch <= self.spawnMonsterBatchNum:
			self.spawnMonster( spaceEntity, currentBatch )
			spaceEntity.setTemp( "currentBatch", currentBatch + 1 )
			if currentBatch <= self.spawnMonsterBatchNum:
				spaceEntity.addTimer( self.spawnMonsterIntervels, 0, SPAWN_MONSTER_USERARG )
				
	
	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""
		if monsterClassName in self.lieZhenMonstersIDList:
			tempCount = selfEntity.queryTemp( "lieZhenMonstersNum", 0 )
			tempCount = tempCount + 1
			selfEntity.setTemp( "lieZhenMonstersNum", tempCount )
			if tempCount == self.lieZhenMonstersNum:
				BOSSID = selfEntity.queryTemp( "BOSSID", 0 )
				boss = BigWorld.entities.get( BOSSID, None )
				if boss:
					energy = boss.queryTemp( "energy", 0 )
					if energy == self.energyList[ 0 ]:
						boss.sendAICommand( BOSSID, self.aiCommandIDList[ 0 ] )
					elif energy < self.energyList[ 1 ]:
						boss.sendAICommand( BOSSID, self.aiCommandIDList[ 1 ] )
					else:
						boss.sendAICommand( BOSSID, self.aiCommandIDList[ 2 ] )
		else:
			if monsterClassName == self.bossClassName:
				for e in selfEntity._players:
					player = BigWorld.entities.get( e.id )
					if player:
						player.client.onStatusMessage( csstatus.SPACE_WILL_BE_CLOSED, "" )
				selfEntity.addTimer( CLOSE_COPY_TIME, 0, CLOSE_COPY_WIN_USERARG )
		pass
		
	def noticePlayerInfo( self, selfEntity, msg ):
		"""
		给玩家一些提示信息
		"""
		for e in selfEntity._players:
			player = BigWorld.entities.get( e.id )
			if player:
				player.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SC_HINT, 0, "", msg, [])
		
	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		if playerEntity.queryTemp( 'leaveSpaceTime', 0 ) == 0:
			playerEntity.leaveTeamTimer = playerEntity.addTimer( 5, 0, ECBExtend.LEAVE_TEAM_TIMER )
		playerEntity.setTemp( "leaveSpaceTime", 5 )
		playerEntity.client.onLeaveTeamInSpecialSpace( 5 )

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		队员离开队伍处理
		"""
		if not playerEntity.isInTeam():
			playerEntity.gotoForetime()
		