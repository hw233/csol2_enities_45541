# -*- coding: gb18030 -*-

from SpaceCopyTemplate import SpaceCopyTemplate
from CopyContent import NEXT_CONTENT
from CopyContent import CopyContent
from CopyContent import CCKickPlayersProcess
from ObjectScripts.GameObjectFactory import g_objFactory

import csdefine
import cschannel_msgs
import random
import BigWorld
import ECBExtend
import time
import math
import csconst
import csstatus

from csconst import TEAM_COMPETITION_TIME
from csconst import SAVE_MODEL_TIME
from csconst import END_TIME


NOTICE_TIMER01			= 2				# 活动提示
NOTICE_TIMER02			= 3				# 活动提示
NOTICE_TIMER03			= 4				# 活动提示
NOTICE_TIMER04			= 5				# 活动提示
REVIVE_TIMERR			= 6				# 角色死亡后30秒回城复活

FIRSTBOX_TIME			= 7
SECONDBOX_TIME			= 8
THIRDBOX_TIME			= 9

OUT_SPACE_AS_DIED		= 10

BOX3_MESSAGE_TIMER		= 11

REWARD_POSITION = ( -2.375, 9.01, 16.637)

WUDI_BUFF_ID			= 780030001		# 复活保护BUFF

FISTBOXID				= "10121058"
SECONDBOXID				= "10121059"
THIRDBOXID				= "10121060"

LIMIT_DIED_TIMES		= 1

class CCSaveModelProcess( CopyContent ):
	"""
	#产生5分钟pk保护
	"""
	def __init__( self ):
		"""
		"""
		self.key = "saveProcess"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		if BigWorld.globalData.has_key("teamCompetitionStartEnterTime"):
			restEnterTime =  SAVE_MODEL_TIME - ( time.time() - BigWorld.globalData["teamCompetitionStartEnterTime"] )
			if restEnterTime > 0:
				spaceEntity.addTimer( restEnterTime, 0, NEXT_CONTENT )
			if restEnterTime - 120 > 0:
				spaceEntity.addTimer( restEnterTime - 120, 0, NOTICE_TIMER01 )
			if restEnterTime - 60 > 0:
				spaceEntity.addTimer( restEnterTime - 60, 0, NOTICE_TIMER02 )
			if restEnterTime - 20 > 0:
				spaceEntity.addTimer( restEnterTime - 20, 0, NOTICE_TIMER03 )
			if restEnterTime - 10 > 0:
				spaceEntity.addTimer( restEnterTime - 10, 0, NOTICE_TIMER04 )
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )						# 强制所有玩家进入和平模式
			e.cell.lockPkMode()																# 锁定pk模式，不能设置

	def onEnter( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )					# 强制所有玩家进入和平模式
		baseMailbox.cell.lockPkMode()														# 锁定pk模式，不能设置

	def endContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.cell.unLockPkMode()
			e.cell.setSysPKMode( 0 )
			player = BigWorld.entities[e.id]
			BigWorld.globalData["TeamCompetitionMgr"].savePlayersInfo( player.getName(),e,player.getTeamMailbox().id, player.getLevel() )
		CopyContent.endContent( self, spaceEntity )

	def onTimer( self, spaceEntity, id, userArg ):
		"""
		"""
		if userArg == NOTICE_TIMER01:
			for e in spaceEntity._players:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_2_MINUTE, "" )

		elif userArg == NOTICE_TIMER02:
			for e in spaceEntity._players:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_1_MINUTE, "" )

		elif userArg == NOTICE_TIMER03:
			for e in spaceEntity._players:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_20_SECOND, "" )

		elif userArg == NOTICE_TIMER04:
			for e in spaceEntity._players:
				e.client.onStatusMessage( csstatus.ACTIVITY_BEGIN_IN_10_SECOND, "" )

		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )

	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.unLockPkMode()				# 解锁pk模式
		baseMailbox.cell.setSysPKMode( 0 )
		#baseMailbox.leaveTeamFC( baseMailbox.id )
		CopyContent.onLeave( self, selfEntity, baseMailbox, params )


class CCTeamPKProcess( CopyContent ):
	"""
	组队竞赛开始
	"""
	def __init__( self ):
		"""
		"""
		self.key = "teamPKProcess"
		self.val = 1
		self.createTime = 0
		self.firstBoxFlag = False
		self.secondBoxFlag = False

	def onContent( self, spaceEntity ):
		"""
		"""
		# 需要知道副本是否只有一个队伍
		tempTeamID = 0
		isSingleTeam = True
		self.firstBoxFlag = False
		self.secondBoxFlag = False
		self.createTime = time.time()
		for e in spaceEntity._players:
			if BigWorld.entities.has_key( e.id ):
				# 如果找不到玩家就不储存了
				player = BigWorld.entities[e.id]
				tmb = player.getTeamMailbox()
				if isSingleTeam and not tmb is None:
					if tempTeamID == 0:
						tempTeamID = tmb.id
					else:
						isSingleTeam = (tempTeamID == tmb.id)
				player.setTemp( 'died_times',0)
				player.client.updateRestDiedTimes( LIMIT_DIED_TIMES )
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_TEAMMATE )							# 默认设置为组队模式
			e.cell.lockPkMode()																	# 锁定pk模式，不能设置
			e.cell.onEnterTeamCompetition()
			e.client.chat_onChannelMessage( csdefine.CHAT_CHANNEL_SYSBROADCAST, 0, "", cschannel_msgs.BCT_TEAMCOMPETITION_START, [] )
			
		if BigWorld.globalData.has_key( "AS_TeamCompetition" ):
			del BigWorld.globalData[ "AS_TeamCompetition" ]
			
		# 增加需求 只有一个队伍报名时，直接获得胜利，然后让他们滚蛋。 by 姜毅
		if isSingleTeam:
			ll = spaceEntity.params["copyLevel"] * 10
			if spaceEntity.params["copyLevel"] == (csconst.ROLE_LEVEL_UPPER_LIMIT - 1) / 10:
				lu = ll + 10
			else:
				lu = ll + 9
			for e in spaceEntity._players:
				player =  BigWorld.entities.get( e.id )
				if player is None:
					continue
				player.addTeamCompetitionReward( 1 )
				player.statusMessage( csstatus.TEAM_COMPTION_SINGLE_TEAM, ll, lu )
			if tempTeamID:
				spaceEntity.base.setWinner( tempTeamID )
			spaceEntity.addTimer( 2, 0, NEXT_CONTENT )		#提前结束比赛，马上开始下一个进程
		else:
			spaceEntity.addTimer( TEAM_COMPETITION_TIME, 0, NEXT_CONTENT )
			
			spaceEntity.addTimer( 300, 0, FIRSTBOX_TIME )
			spaceEntity.addTimer( 900, 0, SECONDBOX_TIME )
			spaceEntity.addTimer( 1800, 0, THIRDBOX_TIME )
			
	def endContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.cell.unLockPkMode()													#解锁pk模式
			e.cell.setSysPKMode( 0 )
		CopyContent.endContent( self, spaceEntity )
		
	def onLeave( self, selfEntity, baseMailbox, params ):
		"""
		"""
		# 这个做法，一般考虑副本中，角色都和副本在同一个cell内
		player = BigWorld.entities.get( baseMailbox.id )
		if not player:
			return
		if not player.queryTemp( "role_die",False ):
			self.onPlayerLeaveOrDied( selfEntity )
		for e in selfEntity._players:
			selfEntity.base.queryCompetitionInfo( e )
		BigWorld.globalData["TeamCompetitionMgr"].saveLeavePlayerInfo( baseMailbox.id )
		baseMailbox.client.onStatusMessage( csstatus.TEAM_COMPETITION_SET_JOIN_EXP,"" )
		CopyContent.onLeave( self, selfEntity, baseMailbox, params )
		
	def onPlayerLeaveOrDied( self, selfEntity ):
		"""
		玩家死亡或离开时如果只剩一个队伍，做提前结束处理
		"""
		g = BigWorld.entities.get
		entities = []
		for emb in selfEntity._players:
			entity = g(emb.id)
			if entity is not None:
				if not entity.queryTemp( "role_die",False ):
					entities.append( entity )
		t_entities = filter( lambda e: not e.getTeamMailbox() is None, entities )
		tIDs = [ e.getTeamMailbox().id for e in t_entities ]
		if len( set( tIDs ) ) == 1:			#当副本中只有一个队伍 的时候，提前结束组队竞技
			if self.getPersistTime() < 300:				#第一个刷箱子
				if self.firstBoxFlag == False:
					g_objFactory.getObject( FISTBOXID ).createEntity( selfEntity.spaceID, REWARD_POSITION, (0, 0, 0), {} )
					self.firstBoxFlag = True
					for player in entities:
						player.statusMessage( csstatus.ROLE_GOTO_BOX1 )
			if self.getPersistTime() < 900:
				if self.secondBoxFlag == False:
					g_objFactory.getObject( SECONDBOXID ).createEntity( selfEntity.spaceID, ( -2.375, 20.01, 16.637), (0, 0, 0) , {} )
					self.secondBoxFlag = True
					for player in entities:
						player.statusMessage( csstatus.ROLE_GOTO_BOX2 )
			selfEntity.base.setWinner( tIDs[0] )
			selfEntity.addTimer( 5, 0, NEXT_CONTENT )		#提前结束比赛，马上开始下一个进程
		
	def getPersistTime( self ):
		"""
		计算比赛开始时间
		"""
		return time.time() - self.createTime
		
	def onTimer( self, spaceEntity, id, userArg ):
		
		g = BigWorld.entities.get
		entities = []
		for emb in spaceEntity._players:
			entity = g(emb.id)
			if entity is not None:
				entities.append( entity )
				
		if userArg == FIRSTBOX_TIME:
			if len( spaceEntity._players ) <= 30 and self.firstBoxFlag == False:
				g_objFactory.getObject( FISTBOXID ).createEntity( spaceEntity.spaceID, REWARD_POSITION, (0, 0, 0), {} )
				self.firstBoxFlag = True
				for player in entities:
					player.statusMessage( csstatus.ROLE_GOTO_BOX1 )
		
		if userArg == SECONDBOX_TIME:
			if len( spaceEntity._players ) <= 15 and self.secondBoxFlag == False:
				g_objFactory.getObject( SECONDBOXID ).createEntity( spaceEntity.spaceID, ( -2.375, 20.01, 16.637), (0, 0, 0) , {} )
				self.secondBoxFlag = True
				for player in entities:
					player.statusMessage( csstatus.ROLE_GOTO_BOX2 )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )


class CCEXPSendProcess( CopyContent ):
	"""
	#结束比赛
	"""
	def __init__( self ):
		"""
		"""
		self.key = "expSendProcess"
		self.val = 1

	def onContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			e.cell.setSysPKMode( csdefine.PK_CONTROL_PROTECT_PEACE )	
			e.cell.lockPkMode()
			e.cell.requestReward( spaceEntity.base )
			e.client.onStatusMessage( csstatus.ACTIVITY_IS_OVER, "" )
		spaceEntity.base.notifyWinner()
		g_objFactory.getObject( THIRDBOXID ).createEntity( spaceEntity.spaceID, ( -2.375, 30.01, 16.637), (0, 0, 0), {} )
		
		spaceEntity.addTimer( 2, 0, BOX3_MESSAGE_TIMER )		# 由于base上的标记冠军玩家操作，延迟2秒再提示
		spaceEntity.addTimer( END_TIME, 0, NEXT_CONTENT )

	def endContent( self, spaceEntity ):
		"""
		"""
		for e in spaceEntity._players:
			player = BigWorld.entities[e.id]
			e.cell.unLockPkMode()
			e.cell.setSysPKMode( 0 )
		CopyContent.endContent( self, spaceEntity )

	def onLeave( self, spaceEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.client.onStatusMessage( csstatus.TEAM_COMPETITION_SET_JOIN_EXP,"" )
		baseMailbox.cell.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		
	def onTimer( self, spaceEntity, id, userArg ):
		if userArg == BOX3_MESSAGE_TIMER:
			# 提示冠军玩家第三个箱子已刷出
			for e in spaceEntity._players:
				player = BigWorld.entities.get( e.id )
				if not player:
					continue
				if player.queryRoleRecord( "teamCompetitionWiner" ) != "1":
					continue
				player.statusMessage( csstatus.ROLE_GOTO_BOX3 )
		else:
			CopyContent.onTimer( self, spaceEntity, id, userArg )
			
class SpaceCopyTeamCompetition( SpaceCopyTemplate ):
	"""
	组队竞赛
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyTemplate.__init__( self )
		self.isSpaceCalcPkValue = True
		self.isSpaceDesideDrop = True
		self._updateClientTimeTimer = -1

	def initContent( self ):
		"""
		"""
		self.contents.append( CCSaveModelProcess() )
		self.contents.append( CCTeamPKProcess() )
		self.contents.append( CCEXPSendProcess() )
		self.contents.append( CCKickPlayersProcess() )

	def packedDomainData( self, player ):
		"""
		"""
		level = player.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1
		data = {"copyLevel" 		: 	level/10,
				"dbID" 				: 	player.databaseID,
				"teamID"			:	player.teamMailbox.id,
				"captainDBID"		:	player.id,
				"spaceKey"		: level/10,
				}
		return data

	def packedSpaceDataOnEnter( self, player ):
		"""
		"""
		
		level = player.level
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			level = csconst.ROLE_LEVEL_UPPER_LIMIT - 1
		if player.isTeamCaptain():
			teamLeaderName = player.getName()
		else:
			if BigWorld.entities.has_key( player.captainID ):
				teamLeaderName = BigWorld.entities[player.captainID].getName()
			else:
				teamLeaderName = ""
		
		packDict = SpaceCopyTemplate.packedSpaceDataOnEnter( self, player )
		packDict[ "copyLevel" ] = level/10
		packDict[ "dbID" ] = player.databaseID
		packDict[ "teamID" ] = player.teamMailbox.id
		packDict[ "teamLeaderName" ] = teamLeaderName
		return packDict

	def packedSpaceDataOnLeave( self, player ):
		"""
		"""
		packDict = SpaceCopyTemplate.packedSpaceDataOnLeave( self, player )
		packDict[ "dbID" ] = player.databaseID
		packDict[ "teamID" ] = player.queryTemp( "team_compete_team_id", 0 )
		packDict[ "isWatchState" ] = player.effect_state & csdefine.EFFECT_STATE_DEAD_WATCHER
		return packDict

	def onRoleDie( self, role, killer ):
		"""
		virtual method.

		某role在该副本中死亡
		"""
		if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = killer.getOwner()
			if owner.etype == "MAILBOX" : return
			killer = owner.entity
		if killer.teamMailbox == None:
			return

		role.setTemp('team_compete_revive_spell', WUDI_BUFF_ID )
		role.setTemp( "role_die_to_revive_type",csdefine.REVIVE_ON_SPACECOPY )
		exp = ( 25 + ( pow( killer.level,1.2 ) * 5 )) * 140
		killer.addExp( exp ,csdefine.REWARD_TEAMCOMPETITION_EXP )
		killer.addTeamCompetitionScore( 1, 0 )
		killer.setTemp( "getPoint",killer.queryTemp( "getPoint",0 ) + 1 )
		killer.statusMessage( csstatus.TEAM_COMPETITION_KILL_ROLE )
		for player in killer.entitiesInRangeExt( 100.0, "Role", killer.position ):
			if player.teamMailbox.id == killer.teamMailbox.id:
				player.setTemp( "getPoint",player.queryTemp( "getPoint",0 ) + 1 )
				player.addTeamCompetitionScore( 1, 0 )				# 队员击杀一个玩家，给队员也加上一分
		
		role.setTemp( 'died_times', role.queryTemp('died_times',0)+1 )
		role.statusMessage( csstatus.TEAM_COMPETITION_BE_KILLED )
		if hasattr( killer, "teamMailbox" ) and killer.teamMailbox != None:
			if role.queryTemp( 'died_times',0 ) == 2:
				role.getCurrentSpaceBase().onPlayerDied( killer.teamMailbox.id ,role.teamMailbox.id ,role.databaseID ,True )
			else:
				role.getCurrentSpaceBase().onPlayerDied( killer.teamMailbox.id ,0 ,0, False )
		if role.queryTemp('last_team_compete_die_timer_id', -1 ) != -1:
			if role.isReal():
				role.cancel( role.queryTemp('last_team_compete_die_timer_id') )
		
		died_times = role.queryTemp( 'died_times',0 )
		# 显示剩余复活次数
		rest_died_times = LIMIT_DIED_TIMES - died_times
		if rest_died_times >= 0:
			role.client.updateRestDiedTimes( rest_died_times )
		else:
			role.client.updateRestDiedTimes( 0 )
			
		if died_times < 2:
			role.client.challengeOnDie( 0 )		# 弹出复活对话框
			role.setTemp('last_team_compete_die_timer_id', role.addTimer( 10, 0, ECBExtend.ROLE_REVIVE_TIMER ) )
		else:
			role.client.challengeOnDie( 1 )		# 弹出观战选择对话框
			role.setTemp( "role_die_teleport", True ) #设置临时死亡标记
			role.setTemp( "role_die", True )
			spaceID = role.getCurrentSpaceBase().id
			spaceEntity = BigWorld.entities[ spaceID ]
			currentContent = spaceEntity.getScript().getCurrentContent( spaceEntity )
			if currentContent.key != "teamPKProcess":
				return
			currentContent.onPlayerLeaveOrDied( spaceEntity )

	def onLeaveCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		baseMailbox.cell.unLockPkMode()
		baseMailbox.cell.setSysPKMode( 0 )
		baseMailbox.client.onLeaveTeamCompetitionSpace()
		if BigWorld.entities.has_key( baseMailbox.id ):
			player = BigWorld.entities[baseMailbox.id]
			BigWorld.globalData["TeamCompetitionMgr"].recordPoint( player.databaseID, csdefine.MATCH_TYPE_TEAM_COMPETITION, player.queryTemp( "getPoint",0 ), baseMailbox )
			player.removeTemp( "died_times" )
			if player.isReal():
				player.removeTemp( "team_compete_team_id" )
				player.removeTemp( "last_team_compete_die_timer_id" )
				player.removeTemp( "getPoint" )
				player.removeTemp( "role_die")
		isWatchState = params[ "isWatchState" ]
		if isWatchState:
			baseMailbox.cell.onLeaveWatchMode()
		baseMailbox.cell.onLeaveTeamCompetition()
		SpaceCopyTemplate.onLeaveCommon( self, selfEntity, baseMailbox, params )

	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		
		if not BigWorld.globalData.has_key( 'TeamCompetition_%i'%params["teamID"] ):
			BigWorld.globalData['TeamCompetition_%i'%params["teamID"]] = params["copyLevel"]
		
		if selfEntity.queryTemp( "createTime", 0 ) == 0:
			selfEntity.setTemp("createTime", time.time() )
		endTime = time.time()
		if BigWorld.globalData.has_key("teamCompetitionStartEnterTime"):
			endTime = TEAM_COMPETITION_TIME + SAVE_MODEL_TIME + BigWorld.globalData["teamCompetitionStartEnterTime"]
		baseMailbox.client.onEnterTeamCompetitionSpace( int( endTime ) )
		
		player = BigWorld.entities.get( baseMailbox.id )
		player.setRoleRecord( "teamCompetitionWiner", "0" )
		player.setTemp( "getPoint",0 )
		player.lockPkMode()
		SpaceCopyTemplate.onEnterCommon( self, selfEntity, baseMailbox, params )

	def onLeaveTeam( self, playerEntity ):
		"""
		"""
		SpaceCopyTemplate.onLeaveTeam( self, playerEntity )
		playerEntity.leaveTeamTimer = playerEntity.addTimer( 3, 0, ECBExtend.LEAVE_TEAM_TIMER )

	def onLeaveTeamProcess( self, playerEntity ):
		"""
		队员离开队伍处理
		"""
		if not playerEntity.isInTeam() or playerEntity.query( "team_compete_team_id", 0 ) != playerEntity.getTeamMailbox().id:
			playerEntity.gotoForetime()

	def onSpaceDestroy( self, selfEntity ):
		"""
		"""
		selfEntity.cancel( self._updateClientTimeTimer )
		self._updateClientTimeTimer = -1
		SpaceCopyTemplate.onSpaceDestroy( self, selfEntity )

	def onTeleportReady( self, selfEntity, baseMailbox ):
		"""
		"""
		SpaceCopyTemplate.onTeleportReady( self, selfEntity, baseMailbox )
