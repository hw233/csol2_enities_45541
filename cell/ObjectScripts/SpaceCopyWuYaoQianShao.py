# -*- coding: gb18030 -*-

"""
巫妖前哨副本
"""

from SpaceCopyMapsTeam import SpaceCopyMapsTeam
import cschannel_msgs
import ShareTexts as ST
import BigWorld
from GameObject import GameObject
from bwdebug import *
import csdefine
import time
import ECBExtend
import csconst
import Const
from Resource.SpaceCopyCountLoader import SpaceCopyCountLoader
g_SpaceCopyCount = SpaceCopyCountLoader.instance()

CLOSE_COPY_WIN_USERARG      = 1				# 关闭副本获胜timer标记
CLOSE_COPY_LOSE_USERARG		= 2				# 关闭副本失败timer标记

ENTERN_SGMJ_MENBER_DISTANCE = 5				# 队伍距离

#GUI_YING_SHI				= [ "20322032","20322043", "20322047" ]	# 鬼影狮的className
#BOSS_SHI_HU_SHOU_WANG		= [ "20314012", "20314013", "20314014" ]	# 狮虎兽王className
SPACE_LAST_TIME				= 1800
QUEST_WU_YAO_QIAN_SHAO_ID 	= 40301002		# 巫妖前哨副本任务id

class SpaceCopyWuYaoQianShao( SpaceCopyMapsTeam ):
	"""
	巫妖前哨脚本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyMapsTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.difficulty = 0
		self._curSpawnBossNeedNum = []
		self.recordKey = "wuyaoqianshao_record"

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyMapsTeam.load( self, section )
		self.difficulty = section[ "Space" ][ "difficulty" ].asInt
		if section[ "Space" ].has_key( "curSpawnBossNeedNum" ):
			tempSpawnBossNeedNumList = section[ "Space" ][ "curSpawnBossNeedNum" ].asString.split(";")
			for num in tempSpawnBossNeedNumList:
				self._curSpawnBossNeedNum.append( int( num ) )

	def packedDomainData( self, entity ):
		"""
		创建SpaceDomainShenGuiMiJing时，传递参数
		"""
		d = SpaceCopyMapsTeam.packedDomainData( self, entity )
		if entity.teamMailbox:
			d["spaceKey"] = entity.getTeamCaptainDBID()	
			d["mailbox"] = entity.base
			# 设置队伍平均等级、最高等级（队伍等级为队长等级，最高等级为队长等级加3）
			if entity.isTeamCaptain():
				d["teamLevel"] = entity.level
				d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				if self._isPickMembers:
					d["membersMailboxs"] = self._pickMemberData( entity )
			else:
				captain = entity.getTeamCaptain()
				if captain:
					d["teamLevel"] = captain.level
					d["teamMaxLevel"] = min( captain.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )
				else:
					d["teamLevel"] = entity.level
					d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )

		return d

	def _pickMemberData( self, entity ):
		# 打包队友数据
		teamMemberMailboxsList = entity.getTeamMemberMailboxs()
		if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
			teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
		
		return teamMemberMailboxsList

	def packedSpaceDataOnEnter( self, entity ):
		"""
		"""
		packDict = SpaceCopyMapsTeam.packedSpaceDataOnEnter( self, entity )
		if entity.teamMailbox:
			packDict[ "teamID" ] =  entity.teamMailbox.id

		return packDict

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		if baseMailbox and self._spaceMapsNo == 0 and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_WU_YAO_QIAN_SHAO, self.recordKey )
			
		SpaceCopyMapsTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		# 进入之后，设置相应任务的任务标记teamID，与相应的队伍绑定
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]
			if player.isInTeam():
				player.setTemp( "onEnterWuYaoQianShao", params['teamID'] )
				if player.has_quest( QUEST_WU_YAO_QIAN_SHAO_ID ):
					player.setQuestVal( QUEST_WU_YAO_QIAN_SHAO_ID, "teamID", player.getTeamMailbox().id )

		if not selfEntity.queryTemp( "tempHaveCome", False ):	# 只设置一次
			selfEntity.base.createSpawnEntities( { "level" : selfEntity.teamLevel })
			selfEntity.setTemp( "teamMaxLevel", selfEntity.teamMaxLevel )
			selfEntity.setTemp( "tempHaveCome", True )


		# 如果副本没有开始计时
		if not selfEntity.queryTemp( "copyStartTime", 0 ):
			selfEntity.setTemp( "copyStartTime", time.time() )
			selfEntity.addTimer( SPACE_LAST_TIME, 0, CLOSE_COPY_LOSE_USERARG )	# 30min后关闭副本

		#副本界面使用
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.ACTIVITY_WU_YAO_QIAN_SHAO )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )

		baseMailbox.client.startCopyTime( SPACE_LAST_TIME - int( time.time() - selfEntity.queryTemp( "copyStartTime" ) ) )	# 通知客户端副本倒计时

		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )	# 检查进入副本的时候是否有队伍，防止：副本中下线再上线没在队伍中

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		"""
		SpaceCopyMapsTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.endCopyTime()

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""
		if self._bossID and monsterClassName in self._bossID:
			# boss死亡后，boss召唤出来的小怪消失
			tempCount = selfEntity.queryTemp( "bossCount" )
			tempCount -= 1
			
			selfEntity.setTemp( "bossCount", tempCount )
			selfEntity.domainMB.killCopyBoss( selfEntity.copyKey )
			if tempCount == 0:
				self.createDoor( selfEntity, False )
				
				for id in selfEntity.queryTemp( "tempCallMonsterIDs", [] ):
					if BigWorld.entities.has_key( id ):
						entity = BigWorld.entities[id]
						entity.destroy()
		else:
			tempCount = selfEntity.queryTemp( "totalMonsterCount", 0 )
			tempCount += 1
			selfEntity.setTemp( "totalMonsterCount", tempCount )
			for index,count in enumerate( self._curSpawnBossNeedNum ):
				if tempCount == count:
					if index > len( self._bossID ) - 1:
						DEBUG_MSG("SpaceCopyShenGuiMiJing:index(%s) more than the length of self._bossID(%s)."%( index, len( self._bossID ) ) )
					else:
						selfEntity.base.createSpawnEntities( { "bossID":self._bossID[ index ], "level" : selfEntity.teamLevel } )
				
			selfEntity.domainMB.killCopyMonster( selfEntity.copyKey )

	def setCopyKillBoss( self, selfEntity, bossNum ):
		"""
		define method
		设置副本BOSS数量
		"""
		SpaceCopyMapsTeam.setCopyKillBoss( self, selfEntity, bossNum )
		if self._copyBossNum ==  bossNum:
			selfEntity.domainMB.closeCopyItem( { "teamID": selfEntity.copyKey } )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == CLOSE_COPY_WIN_USERARG:		# 关闭副本，获胜
			self.closeCopy( selfEntity, 1 )

		elif userArg == CLOSE_COPY_LOSE_USERARG:		# 关闭副本，失败
			self.closeCopy( selfEntity, 0 )

		else:
			SpaceCopyMapsTeam.onTimer( self, selfEntity, id, userArg )

	def broadcastInCopy( self, selfEntity, msg ):
		"""
		副本中广播
		"""
		for baseMailBox in selfEntity._players:
			baseMailBox.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", msg, [] )


	def closeCopy( self, selfEntity, isWin ):
		"""
		副本关闭
		"""
		if not isWin:	# 如果失败
			for e in selfEntity._players:
				player = BigWorld.entities[e.id]
				if player.has_quest( QUEST_WU_YAO_QIAN_SHAO_ID ):
					e.cell.setQuestVal( QUEST_WU_YAO_QIAN_SHAO_ID, "questHasLose", True )	# 设置此任务失败
					e.cell.questTaskFailed( QUEST_WU_YAO_QIAN_SHAO_ID, 1 )					# 通知任务失败

		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				player = BigWorld.entities[ e.id ]
				if player.isInTeam():
					player.removeTemp( "onEnterWuYaoQianShao" )
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.removeTemp( "onEnterWuYaoQianShao" )
				e.cell.gotoForetime()
				
		
		SpaceCopyMapsTeam.closeCopy( self, selfEntity, isWin )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		DEBUG_MSG( "Role %i is killed by a enemy." % role.id )
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		cbid = role.addTimer( 32.0, 0, ECBExtend.ROLE_REVIVE_TIMER )
		role.setTemp( "role_die_to_revive_cbid", cbid )
