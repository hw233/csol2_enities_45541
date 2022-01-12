# -*- coding: gb18030 -*-
import time
import BigWorld

from SpaceCopyTeam import SpaceCopyTeam
from GameObject import GameObject

import csdefine
import ECBExtend
import csconst
import Const
import cschannel_msgs
import ShareTexts as ST


CLOSE_COPY_WIN_USERARG      = 1					# 关闭副本获胜timer标记
CLOSE_COPY_LOSE_USERARG		= 2					# 关闭副本失败timer标记

ENTERN_SGMJ_MENBER_DISTANCE = 5					# 队伍距离

WU_YAO_WANG						= [ "20742059", "20742060", "20742061" ]		# 巫妖王的className
QUEST_WU_YAO_WANG_BAO_ZANG_ID 	= 40301003		# 巫妖前哨副本任务id

ALL_MONSTERS_COUNT = 50							# 刷怪数量
SPACE_LAST_TIME = 1800							# 副本持续时间

class SpaceCopyWuYaoWang( SpaceCopyTeam ):
	"""
	巫妖王宝藏脚本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTeam.__init__( self )
		self.isSpaceCalcPkValue = True
		self.recordKey = "wuyaowangbaozang_record"

	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopyTeam.load( self, section )

	def packedDomainData( self, entity ):
		"""
		创建SpaceDomainShenGuiMiJing时，传递参数
		"""
		d = { 'dbID' : entity.databaseID, 'spaceKey' : entity.databaseID }
		if entity.teamMailbox:
			# 已加入队伍，取队伍数据
			d["spaceKey"] = entity.teamMailbox.id
			d["teamID"] = entity.teamMailbox.id
			d["captainDBID"] = entity.getTeamCaptainDBID()
			d["membersDBID"] = entity.getTeamMemberDBIDs()
			d["mailbox"] = entity.base
			# 取得所有队员basemailboxs
			teamMemberMailboxsList = entity.getTeamMemberMailboxs()
			if entity.getTeamCaptainMailBox() in teamMemberMailboxsList:
				teamMemberMailboxsList.remove( entity.getTeamCaptainMailBox() )
			d["membersMailboxs"] = teamMemberMailboxsList

			# 设置队伍平均等级、最高等级
			if entity.isTeamCaptain():
				d["teamLevel"] = entity.level
				d["teamMaxLevel"] = min( entity.level + 3, csconst.ROLE_LEVEL_UPPER_LIMIT )

				if entity.queryTemp( "onEnterWuYaoWangBaoZang" ) == entity.teamMailbox.id:	# 如果队长进入过副本
					d["isCallTeamMember"] = False
				else:
					d["isCallTeamMember"] = True

		d[ "difficulty" ] = entity.popTemp( "WuYaoWangEnterType" )
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
		进入巫妖王宝藏
		"""
		if baseMailbox and params[ "databaseID" ] not in selfEntity._enterRecord:
			baseMailbox.cell.remoteAddActivityCount( selfEntity.id, csdefine.ACTIVITY_SHI_LUO_BAO_ZHANG, self.recordKey )
			
		SpaceCopyTeam.onEnterCommon( self, selfEntity, baseMailbox, params )
		# 进入之后，设置相应任务的任务标记teamID，与相应的队伍绑定
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]
			if player.isInTeam():
				player.setTemp( "onEnterWuYaoWangBaoZang", params['teamID'] )
				if player.has_quest( QUEST_WU_YAO_WANG_BAO_ZANG_ID ):
					player.setQuestVal( QUEST_WU_YAO_WANG_BAO_ZANG_ID, "teamID", player.getTeamMailbox().id )

		if not selfEntity.queryTemp( "tempHaveCome", False ):	# 只设置一次
			selfEntity.setTemp( "tempHaveCome", True )

		# 如果副本没有开始计时
		if not selfEntity.queryTemp( "copyStartTime", 0 ):
			selfEntity.setTemp( "copyStartTime", time.time() )
			selfEntity.addTimer( SPACE_LAST_TIME, 0, CLOSE_COPY_LOSE_USERARG )	# 30min后关闭副本

		#副本界面使用
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEVEL, 		"" )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_COPY_TITLE, cschannel_msgs.ACTIVITY_WU_YAO_WANG )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_START_TIME, selfEntity.queryTemp( "copyStartTime" ) )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LAST_TIME, SPACE_LAST_TIME )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, selfEntity.monsterCount )
		BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, selfEntity.bossCount )

		baseMailbox.client.startCopyTime( SPACE_LAST_TIME - int( time.time() - selfEntity.queryTemp( "copyStartTime" ) ) )	# 通知客户端副本倒计时

		baseMailbox.cell.checkTeamInCopySpace( selfEntity.base )	# 检查进入副本的时候是否有队伍，防止：副本中下线再上线没在队伍中

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		一个entity准备离开space时的通知；
		"""
		SpaceCopyTeam.onLeaveCommon( self, selfEntity, baseMailbox, params )
		baseMailbox.client.endCopyTime()

	def onOneTypeMonsterDie( self, selfEntity, monsterID, monsterClassName ):
		"""
		怪物通知其所在副本自己挂了，根据怪物的className处理不同怪物死亡
		"""
		if monsterClassName in WU_YAO_WANG:			# 如果杀死了boss巫妖王之影
			uskCount = None
			monster = BigWorld.entities.get( monsterID )
			if monster and monster.isReal():
				uskCount = monster.queryTemp( "uskCount" )		# 特殊任务需求，如果巫妖王の影挂掉而且每次癫狂都是图腾清除
			if uskCount is not None and uskCount <= 0:
				selfEntity.onGodWeaponWuYao()
			self.broadcastInCopy( selfEntity, cschannel_msgs.BCT_FUBEN_WU_YAO_WANG_BAO_ZANG_OVER )
			for e in selfEntity._players:
				player = BigWorld.entities[e.id]
				if player.has_quest( QUEST_WU_YAO_WANG_BAO_ZANG_ID ):
					e.cell.questTaskIncreaseState( QUEST_WU_YAO_WANG_BAO_ZANG_ID, 1 )	# 完成任务
					e.cell.spellTarget( 122169002, e.id )		# 任务完成后，加一个90s buff(防止新接的任务，进入久的副本)
			selfEntity.addTimer( 60.0, 0.0, CLOSE_COPY_WIN_USERARG )				# 30秒后，关闭副本获胜
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_BOSS, 0 )
			selfEntity.setTemp( "bossCount", 0 )
		else:
			tempCount = selfEntity.queryTemp( "allMonsterCount" )
			tempCount -= 1
			selfEntity.setTemp( "allMonsterCount", tempCount )
			BigWorld.setSpaceData( selfEntity.spaceID, csconst.SPACE_SPACEDATA_LEAVE_MONSTER, tempCount )

	def onTimer( self, selfEntity, id, userArg ):
		"""
		"""
		if userArg == CLOSE_COPY_WIN_USERARG:		# 关闭副本，获胜
			self.closeCopy( selfEntity, 1 )

		elif userArg == CLOSE_COPY_LOSE_USERARG:		# 关闭副本，失败
			self.closeCopy( selfEntity, 0 )

		else:
			SpaceCopyTeam.onTimer( self, selfEntity, id, userArg )

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
				if player.has_quest( QUEST_WU_YAO_WANG_BAO_ZANG_ID ):
					e.cell.setQuestVal( QUEST_WU_YAO_WANG_BAO_ZANG_ID, "questHasLose", True )	# 设置此任务失败
					e.cell.questTaskFailed( QUEST_WU_YAO_WANG_BAO_ZANG_ID, 1 )					# 通知任务失败

		for e in selfEntity._players:
			if BigWorld.entities.has_key( e.id ):
				player = BigWorld.entities[ e.id ]
				if player.isInTeam():
					player.removeTemp( "onEnterWuYaoWangBaoZang" )
				BigWorld.entities[ e.id ].gotoForetime()
			else:
				e.cell.removeTemp( "onEnterWuYaoWangBaoZang" )
				e.cell.gotoForetime()

		SpaceCopyTeam.closeCopy( self, selfEntity, isWin )

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		pass