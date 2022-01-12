# -*- coding: gb18030 -*-
#
# $Id: TeamEntity.py,v 1.27 2008-03-14 00:49:43 yangkai Exp $

import BigWorld
import time
import csdefine
import csconst
import csstatus
import cschannel_msgs
import Love3
from bwdebug import *
import RoleMatchRecorder
from interface.TeamMatcherInterface import TeamMatcherInterface
from interface.TeamMatchedInterface import TeamMatchedInterface
from interface.DomainTeamInterface import UseTeamForDomainInter
from interface.TeamTurnWarInterface import TeamTurnWarInterface
from interface.TeamCampTurnWarInterface import TeamCampTurnWarInterface

DESTORY_TEAM_TIMER 	= 1 	# 组队没回应销毁队伍延ID
OFFLINE_LEAVE_TIMER = 2 	# 玩家下线，离线处理检测TIMER

class TeamEntity( BigWorld.Base, TeamMatcherInterface, TeamMatchedInterface, UseTeamForDomainInter, TeamTurnWarInterface, TeamCampTurnWarInterface ):
	def __init__( self ):
		BigWorld.Base.__init__( self )
		TeamMatcherInterface.__init__( self )				# 处理作为普通队伍的功能
		TeamMatchedInterface.__init__( self )				# 处理作为匹配队伍的功能
		UseTeamForDomainInter.__init__( self )
		TeamTurnWarInterface.__init__( self )
		TeamCampTurnWarInterface.__init__( self )
		self.member = []	# [(entityID, { ... }),  ], see also join()
		self.captainID = self.teamArg["captainBase"].id		# 记录队长entityID
		self.pickUpState = self.teamArg["pickUpState"]
		self.pickUpVal2	 = 2

		self.followList = []	# 跟随成员列表

		# 关于队伍竞技信息
		self.teamChallengeInfo = csdefine.MATCH_LEVEL_NONE
		self.teamChallengeLevel = None
		self.teamChallengeIsGather = False
		self.teamChallengeRecruit = False

		self.teamCompetitionLevel = None
		self.teamCompetitionGatherFlag = False
		
		# 宝藏PVP
		self.baoZangPVPreqTime = 0
		
		self.yingXiongCampReqTime = 0
		
		# 添加队长数据
		self.join( self.teamArg["captainDBID"], self.teamArg["captainName"],\
				self.teamArg["captainBase"], self.teamArg["captainRaceclass"], self.teamArg["captainHeadTextureID"] )

		# 启动计时器
		self.addTimer( csconst.TEAM_FEEDBACK_WAIT_TIME, 0, DESTORY_TEAM_TIMER )

		# 离线记时ID
		self.leaveTimerID = 0
		self.leaveDBIDs = {}		# { playerDBID : ( id, logout time ) } #加入id，主要是为了处理离队

		del self.teamArg	# 删除初始化数据

		# 取队伍管理器
		try:
			self.teamManager = BigWorld.globalBases["TeamManager"]
		except:
			self.teamManager = None
			ERROR_MSG( "get team manager entity error!" )
			return

		# 注册管理器
		self.teamManager.register( self.id, self )
	
	def _getMemberInfoByDBID( self, playerDBID ):
		"""
		获取entity的mailbox
		@return: 队伍成员的entityID及信息字典
		"""
		for entityID, info in self.member:
			if info["playerDBID"] == playerDBID:
				return entityID, info
		return None, None

	def _notifyPlayerTeamMemberInfo( self, playerBase ):
		"""
		向玩家发送所有队伍成员的信息，包括离线了的

		@param playerBase: 玩家BASE
		@type  playerBase: mailbox
		"""
		playerBase.teamInfoNotify( self.captainID, self )
		if playerBase.id != self.captainID :	# 创建队伍时给队长发送拾取方式消息已经移动到了join中
			playerBase.changePickUpStateNotify( self.pickUpState )
			playerBase.cell.changePickUpQualityNotify( self.pickUpVal2 )
		for entityID, info in self.member:
			playerBase.addTeamMember( info["playerDBID"], entityID, info["playerName"], info["playerBase"], info["playerRaceclass"], info["headTextureID"] )

	def onTimer( self, id, userArg ):
		"""
		时间计数器
		时间达到
		"""
		# 如果被邀请玩家无回复，队伍销毁
		if DESTORY_TEAM_TIMER == userArg:
			if self.isDestroyed:
				return
			self.delTimer( id )
			# 队伍小于2人，队伍销毁
			#if len(self.member) < 2:
			#	self.disband()

		if OFFLINE_LEAVE_TIMER == userArg:
			# 玩家离队，必须用dict.items()，不能用iteritems()，因为在这里需要删除
			for dbid, t in self.leaveDBIDs.items():
				if time.time() - t >= csconst.TEAM_OFFLINE_DURATION:
					# 没有下线成员
					id,info = self._getMemberInfoByDBID( dbid )
					self.leave( id, id )

	def isfull( self ):
		return len( self.member ) >= csconst.TEAM_MEMBER_MAX


	#-----------------------------------------------------------
	def join( self, playerDBID, playerName, playerBase, playerRaceclass, headTextureID ):
		"""
		<define>
		玩家添加到队伍中

		@param playerID: 玩家的EntityID
		@type playerID: OBJECT_ID
		@param playerDBID: 玩家DBID
		@type playerDBID: DATABASE_ID
		@param playerBase: 玩家BASE
		@type playerBase: mailbox
		@param playerName: 玩家名称
		@type playerName: string
		@param playerRaceclass: 玩家职业
		@type playerRaceclass: INT32
		"""
		# 异步情况下什么都有可能发生，因此需要判断队伍人数是否已满
		if self.isfull():
			# 队伍已满，需要通知加入队伍失败
			playerBase.client.onStatusMessage( csstatus.TEAM_FULL, "" )
			playerBase.clearTeamInfo()	# 清除队伍相关数据
			return

		# 通知所有人有队伍成员，有新玩家加入队伍
		# 以下代码已与_notifyPlayerTeamMemberInfo中的处理重复
		for entityID, info in self.member:
			if info["playerBase"]:
				info["playerBase"].addTeamMember( playerDBID, playerBase.id, playerName, playerBase, playerRaceclass, headTextureID )

		# 加入新成员到队伍中
		info = {	"playerDBID" : playerDBID,
					"playerName" : playerName,
					"playerBase" : playerBase,
					"playerRaceclass" : playerRaceclass,
					"headTextureID": headTextureID,
					"time" : time.time(), }				# 加入时间
		self.member.append( ( playerBase.id, info ) )

		# 玩家接受邀请后，向客户端发送消息  2009-3-25 gjx
		if self.captainID != playerBase.id:
			# 向加入者发送加入队伍消息
			captainInfo = self._getPlayerInfoByID( self.captainID )
			captainName = captainInfo["playerName"]
			playerBase.client.onStatusMessage( csstatus.TEAM_JOIN_TEAM_SUCCESS, "(\'%s\',)" % captainName )
			# 向队长发送玩家接受邀请消息
			captain = captainInfo["playerBase"]
			captain.client.onStatusMessage( csstatus.TEAM_ACCEPT_JOIN_TEAM, "(\'%s\',)" % playerName )
			# 创建队伍后第二个队员加入时给队长发送队伍拾取方式的消息
			# 放在这里是为了先出现组队成功消息，再提示拾取方式
			if len( self.member ) == 2 :
				captain.changePickUpStateNotify( self.pickUpState )

		# 通知新成员队伍成员
		self._notifyPlayerTeamMemberInfo( playerBase )
		# 进行副本组队系统的相关处理
		self.tmi_onMemberJoin( playerDBID, playerBase.id )

		# 更新竞技类信息
		if self.teamChallengeLevel:
			playerBase.client.teamChallengeUpInfo( self.teamChallengeInfo )
			playerBase.client.teamChallengeUpLevel( self.teamChallengeLevel[0], self.teamChallengeLevel[1] )

		if self.teamChallengeIsGather:
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

		if self.teamChallengeRecruit:
			if len( self.member ) >= csconst.TEAM_MEMBER_MAX: # 当队伍满员的时候自动退出招募
				BigWorld.globalData[ "TeamChallengeMgr" ].cancelRecruitTeam( self )

			playerBase.client.teamChallengeOnRecruit()

		if self.teamCompetitionLevel:
			playerBase.client.teamCompetitionNotify( self.teamCompetitionLevel )

		if self.teamCompetitionGatherFlag:
			playerBase.client.teamCompetitionGather()
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

	def leave( self, srcID, dstID ):
		"""
		define method.
		开除指定玩家/玩家离队
		1、如果srcID == dstID则表示自己是离队；
		2、如果srcID != dstID 则 srcID是队长则表示队长开除玩家出队伍

		@param srcID: 使dstID离开队伍的ID
		@type  srcID: OBJECT_ID
		@param dstID: 离开队伍的玩家ID
		@type  dstID: OBJECT_ID
		"""
		# 匹配的副本不允许队长踢人，只能投票踢人
		if self.isMatchedTeam and srcID != dstID :
			return
		# dstID有可能是客户端过来的参数，需判断其合法性；
		# 或者远程调用leave时，dstID已经被踢出队伍，进行下面的操作前需检查dstID是否还合法。11:07 2009-11-4，wsf
		dstInfo = self._getPlayerInfoByID( dstID )
		if dstInfo is None:
			return
		if srcID == dstID or srcID == self.captainID:
			# 自己离队或队长开除
			for entityID, info in self.member:
				# 通知每一个在线的玩家，谁离开了队伍
				if info["playerBase"]:
					info["playerBase"].leaveTeamNotify( srcID, dstID )

			# 如果玩家在离线列表中，则cancel离线处理
			dbid = dstInfo["playerDBID"]
			if dbid in self.leaveDBIDs:
				self.leaveDBIDs.pop( dbid )
				# 如果没有了离线队员，则停掉timer
				if len( self.leaveDBIDs ) == 0:
					self.delTimer( self.leaveTimerID )
					self.leaveTimerID = 0
			self.member.remove( ( dstID, dstInfo ) )	# 删除离队的人员
		else:
			# 既不是自己离队，也不是队长开除，直接忽略
			return

		# 队伍小于2人，队伍销毁
		#if len(self.member) < 2:
		#	self.disband()
		#	return
		if not dstInfo[ "playerBase" ]:# 被踢的不在线
			self.kcikNotOnline( dstInfo["playerDBID"] )
			
		self.leaveFollow( dstID )
		# 进行副本组队系统的相关处理
		self.tmi_onMemberLeave( dstInfo["playerDBID"], dstID )

		# 恢复组队竞技集合状态
		if self.teamCompetitionGatherFlag:
			dstInfo[ "playerBase" ].cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

		# 恢复组队竞技当前参赛级别信息
		if self.teamCompetitionLevel:
			dstInfo[ "playerBase" ].client.teamCompetitionNotify( 0 )

		memberNum = len( self.member )	# 检测队伍人数觉定是否解散队伍 modified by姜毅
		if memberNum <= 0 or memberNum == len( self.leaveDBIDs ):	# 统计在线的玩家数量
			dstInfo[ "playerBase" ].cell.turnWar_setJoinFlag( False )
			self.disband()	# 队伍解散
			return

		# 如果离队的是队长则需要:
		if dstID == self.captainID:
			self._autoSelectCaptain()	# 重新选择队长并通知队伍所有成员
			dstInfo[ "playerBase" ].cell.turnWar_setJoinFlag( False )

		# 设置队伍竞技类活动的结果
		if self.teamChallengeLevel:
			RoleMatchRecorder.update( dstInfo[ "playerDBID" ], csdefine.MATCH_TYPE_TEAM_ABA, self.teamChallengeInfo, dstInfo[ "playerBase" ] )

		if self.teamChallengeIsGather and dstInfo[ "playerBase" ]:
			dstInfo[ "playerBase" ].cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )
			
		self.turnWar_onMemberLeave( dstInfo )

	def _autoSelectCaptain( self ):
		"""
		自动选择一个队长，此函数一般用于当队长直接（断）下线时或队长离开队伍
		"""
		maxTime = float( 0x7FFFFFFF )
		captain = 0
		for entityID, info in self.member:
			if info["playerBase"] != None and info["time"] < maxTime:	# 在线时间最长且没有掉线（有base mailbox）
				captain = info["playerBase"].id
				maxTime = info["time"]
		self.changeCaptain( captain )

	def changeCaptain( self, newCaptainID ):
		"""
		define method.
		移交队长权限

		@param newCaptainID: 新队长的entity id
		@type  newCaptainID: OBJECT_ID
		"""
		self.turnWar_onChangeCaptain( newCaptainID )
			
		self.captainID = newCaptainID
		# 通知所有成员
		for ( entityID, info ) in self.member:
			if info["playerBase"]:
				info["playerBase"].changeCaptainNotify( newCaptainID )

		self.onChangeCaptain( newCaptainID )
		self.tmi_onChangeCaptain( newCaptainID )

	def onChangePickUpQuality( self, val ):
		"""
		define method.
		"""
		# 通知所有成员
		self.pickUpVal2 = val
		for ( entityID, info ) in self.member:
			if info["playerBase"]:
				info["playerBase"].cell.changePickUpQualityNotify( val )


	def onChangeRollQuality( self, val ):
		"""
		define method.
		"""
		# 通知所有成员
		self.pickUpVal2 = val
		for ( entityID, info ) in self.member:
			if info["playerBase"]:
				info["playerBase"].cell.changeRollQualityNotify( val )


	def onChangePickUpState( self, state ):
		"""
		define method.
		重设拾取状态

		@param state: 新队长的entity id
		@type  state: OBJECT_ID
		"""
		self.pickUpState = state
		# 通知所有成员
		for ( entityID, info ) in self.member:
			if info["playerBase"]:
				info["playerBase"].changePickUpStateNotify( state )



	#-----------------------------------------------------------
	def logon( self, playerDBID, playerBase ):
		"""
		define method.
		通知队伍玩家上线

		@param playerDBID: 玩家DBID
		@type playerDBID: DATABASE_ID
		@param playerBase: 玩家BASE
		@type playerBase: mailbox
		"""
		oldEntityID, info = self._getMemberInfoByDBID( playerDBID )
		if info is None:
			# 找不到则表示该玩家已经被清除出队伍
			playerBase.clearTeamInfo()
			return

		dic = dict( self.member )
		self.member.remove( ( oldEntityID, dic[oldEntityID] ) )	# 先删除旧的玩家信息

		# 通知所有的在线成员
		for entityID, tempinfo in self.member:
			if tempinfo["playerBase"]:
				tempinfo["playerBase"].rejoinTeam( oldEntityID, playerDBID, playerBase )

		info["playerBase"] = playerBase			# 更新playerBase
		self.member.append( ( playerBase.id, info ) )		# 以新的entityID重新关联玩家信息

		# 队伍向上线玩家发送成员列表
		self._notifyPlayerTeamMemberInfo( playerBase )

		# 检查有没有下线成员，没有则关掉timer
		if self.leaveTimerID:
			self.leaveDBIDs.pop( playerDBID )

			# 没有下线成员，关掉timer
			if len(self.leaveDBIDs) == 0:
				self.delTimer( self.leaveTimerID )
				self.leaveTimerID = 0

		# 进行副本组队系统的相关处理
		self.tmi_onMemberLogon( oldEntityID, playerBase.id, playerDBID )

		# 更新组队竞技类活动的信息
		if self.teamChallengeLevel:
			playerBase.client.teamChallengeUpInfo( self.teamChallengeInfo )
			playerBase.client.teamChallengeUpLevel( self.teamChallengeLevel[0], self.teamChallengeLevel[1] )

		if self.teamChallengeIsGather:
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

		if self.teamChallengeRecruit:
			playerBase.client.teamChallengeOnRecruit()

		if self.teamCompetitionLevel:
			playerBase.client.teamCompetitionNotify( self.teamCompetitionLevel )

		if self.teamCompetitionGatherFlag:
			playerBase.client.teamCompetitionGather()
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )
		
		if self.baoZangPVPreqTime:
			playerBase.client.baoZangPVPonReq( self.baoZangPVPreqTime )
		
		if self.yingXiongCampReqTime:
			playerBase.client.yingXiongCampOnReq( self.yingXiongCampReqTime )
		
	#-----------------------------------------------------------

	def logout( self, playerDBID ):
		"""
		define method.
		玩家下线

		过程：
		在成员列表里设置玩家为下线状态
		队伍通知其它成员，玩家离线

		@param playerDBID: 玩家DBID
		@type  playerDBID: DATABASE_ID
		"""
		entityID, info = self._getMemberInfoByDBID( playerDBID )
		if info is None:
			return

		# 清除离队成员BASE
		info["playerBase"] = None

		# 添加离队信息
		self.leaveDBIDs[playerDBID] =  time.time()

		if not self.leaveTimerID:
			self.leaveTimerID = self.addTimer( csconst.TEAM_OFFLINE_DURATION, csconst.TEAM_OFFLINE_DETECT_INTERVAL, OFFLINE_LEAVE_TIMER )

		# 统计在线的玩家数量
		if len( self.member ) - len( self.leaveDBIDs ) == 0:
			# 队伍解散
			self.disband()
		else:
			# 通知队伍成员，有玩家离线
			for playerID, info in self.member:
				if info["playerBase"]:
					info["playerBase"].logoutNotify( playerDBID )

			if entityID == self.captainID:
				self._autoSelectCaptain()
		# 进行副本组队系统的相关处理
		self.tmi_onMemberLogout( playerDBID )
		
		self.turnWar_onMemLogout()

	#-----------------------------------------------------------
	def disband( self ):
		"""
		define method
		请求解散队伍
		通知所有成员，队伍解散
		"""
		# 进行副本组队系统的相关处理
		self.tmi_onDisband()
		
		# 通知成员队伍销毁
		for entityID, info in self.member:
			if info["playerBase"]:
				info["playerBase"].disbandTeamNotify()

		# 队伍销毁
		self.teamManager.deregister( self.id )
		if self.teamChallengeLevel:
			BigWorld.globalData[ "TeamChallengeMgr" ].teamDismiss( self.id )
		
		if self.baoZangPVPreqTime:
			BigWorld.globalData[ "BaoZangCopyMgr" ].cancel( self.id, False )
			
		self.turnWar_onDisband()
		
		# 通知副本队伍解散
		self.desSpaceCopyNotify()

		# 销毁自身
		self.destroy()


	def getCaptainDBID( self ):
		"""
		获得组长的DBID
		"""
		for entityID, info in self.member:
			if entityID == self.captainID:
				return info['playerDBID']

		
	# -----------------------------------------------------------------------------------------
	# 组队跟随，13:50 2009-3-13，wsf
	# -----------------------------------------------------------------------------------------
	def startFollow( self ):
		"""
		Define method.
		队长发起组队跟随。
		"""
		self.followList.append( self.captainID )
		#DEBUG_MSG( "------>>>self.followList.", self.followList )

	def stopFollow( self ):
		"""
		Define method.
		队长停止组队跟随
		"""
		#DEBUG_MSG( "------>>>self.followList.", self.followList )
		for entityID in self.followList:
			playerInfo = self._getPlayerInfoByID( entityID )
			if playerInfo is None:
				continue
			playerBase = playerInfo[ "playerBase" ]
			if playerBase and hasattr( playerBase, "cell" ):
				playerBase.cell.cancelTeamFollow()
				playerBase.client.onStatusMessage( csstatus.TEAM_FOLLOW_CAPTAIN_STOP, "" )
		self.followList = []

	def isFollowState( self ):
		"""
		队伍是否在组队跟随中。
		"""
		return len( self.followList ) > 0

	def followCaptain( self, entityID ):
		"""
		Define method.
		玩家同意跟随队长，进入跟随列表

		@param playerDBID : 玩家的dbid
		@type playerDBID : databaseID
		"""
		if not self.isFollowState():
			return
		if entityID in self.followList:
			return
		info = self._getPlayerInfoByID( entityID )
		if info is None:
			return
		info[ "playerBase" ].client.team_followPlayer( self.followList[ -1 ] )	# 告诉玩家他应该跟随谁
		self.followList.append( entityID )

	def _getPlayerInfoByID( self, entityID ):
		"""
		通过玩家的id获得玩家的信息

		@param entityID : OBJECT_ID
		"""
		for playerID, info in self.member:
			if playerID == entityID:
				return info
		return None

	def cancelFollow( self, entityID ):
		"""
		Define method.
		退出队伍跟随

		@param entityID : 玩家的entity id
		@type entityID : OBJECT_ID
		"""
		if entityID not in self.followList:
			return

		if len( self.followList ) == 2:	# 一共2人，一人退出，跟随解散
			self.stopFollow()
			return

		#DEBUG_MSG( "-------->>>followList,entityID", self.followList, entityID )
		index = self.followList.index( entityID )
		if index + 1 == len( self.followList ):	# 如果是队尾队员退出跟随
			self.followList.pop()
		else:								# 调整后面一个玩家的跟随目标
			playerBase = self._getPlayerInfoByID( self.followList[ index + 1 ] )[ "playerBase" ]
			if playerBase:
				playerBase.client.team_followPlayer( self.followList[ index - 1 ] )
			self.followList.remove( entityID )

	def onChangeCaptain( self, newCaptainID ):
		"""
		队长改变了

		@param newCaptainID : 新队长id,OBJECT_ID
		"""
		#DEBUG_MSG( "------->>>111newCaptainID,followList", newCaptainID, self.followList )
		if not self.isFollowState():
			return

		if newCaptainID not in self.followList:
			self.stopFollow()
			return

		index = self.followList.index( newCaptainID )
		if index + 1 != len( self.followList ):	# 如果不是跟随最末一位队员当队长
			playerBase = None
			playerInfo = self._getPlayerInfoByID( self.followList[ index + 1 ] )
			if playerInfo is not None:
				playerBase = playerInfo[ "playerBase" ]
			if playerBase is not None:
				playerBase.client.team_followPlayer( self.followList[ index - 1 ] )
		self.followList.remove( newCaptainID )
		self.followList.insert( 0, newCaptainID )
		#DEBUG_MSG( "-------->>>222self.followList", self.followList )
		playerBase = self._getPlayerInfoByID( self.followList[ 1 ] )[ "playerBase" ]
		if playerBase:
			playerBase.client.team_followPlayer( newCaptainID )

	def leaveFollow( self, playerID ):
		"""
		有队员离线

		@param playerID : 离线队员的id
		@type playerID : OBJECT_ID
		"""
		#DEBUG_MSG( "-------->>>,playerID", playerID )
		if not self.isFollowState():
			return

		if not playerID in self.followList:
			return

		if playerID == self.captainID:
			self.stopFollow()
		else:
			index = self.followList.index( playerID )
			if index + 1 == len( self.followList ):
				self.followList.pop( index )
				return
			playerBase = self._getPlayerInfoByID( self.followList[ index + 1 ] )[ "playerBase" ]
			if playerBase:
				playerBase.client.team_followPlayer( self.followList[ index - 1 ] )
			self.followList.pop( index )

	def setMessage( self ,statuID ):
		"""
		defined method.
		"""
		for playerID, info in self.member:
				if info["playerBase"]:
					info["playerBase"].client.onStatusMessage( statuID,"" )

	# ---------------------------------------------------------
	# 组队擂台
	# ---------------------------------------------------------
	def teamChallengeRequestJoin( self, playerDBID, playerName, playerLevel, playerBase, playerRaceclass, headTextureID ):
		# define method
		# 组队擂台往队伍里加队员
		if len( self.member ) >= csconst.TEAM_MEMBER_MAX:
			BigWorld.globalData[ "TeamChallengeMgr" ].recruitRresult( playerBase, playerLevel, self.id, False )
		else:
			if playerDBID not in [ info[ 1 ][ "playerDBID" ] for info in self.member ]:
				self.join( playerDBID, playerName, playerBase, playerRaceclass, headTextureID )
				playerBase.cell.challengeActivityTransmit( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

			BigWorld.globalData[ "TeamChallengeMgr" ].recruitRresult( playerBase, playerLevel, self.id, True )

	def teamChallengeChampion( self, entityDBIDs, minL, maxL, rewardTime):
		# define method
		# 通知队伍为组队擂台冠军
		championNameStr  = ""

		for playerID, info in self.member:
			if len( entityDBIDs ) != 0 and info[ "playerDBID" ] not in entityDBIDs:
				continue

			if championNameStr:
				championNameStr += "," + info[ "playerName" ]
			else:
				championNameStr = info[ "playerName" ]

			playerBase = info[ "playerBase" ]

			if playerBase:
				playerBase.cell.teamChallengeSetChampion( rewardTime )
				playerBase.client.onStatusMessage( csstatus.TEAM_CHALLENGE_WIN_LAST,  str( ( minL, maxL, ) )  )

		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TEAM_CHALLENGE_WIN_ALL_ROLE%( championNameStr, minL, maxL ), [] )

	def teamChallengeGather( self, round ):
		# define method
		# 组队擂台集合
		self.teamChallengeIsGather = True
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.challengeTeamGather( round )
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

	def teamChallengeCloseGather( self ):
		# define method
		# 关闭组队擂台的集合
		self.teamChallengeIsGather = False
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TEAM_CHALLENGE )

	def teamChallengeSetResult( self, result ):
		# define method
		# 设置比赛结果
		for playerID, info in self.member:
			RoleMatchRecorder.update( info[ "playerDBID" ], csdefine.MATCH_TYPE_TEAM_ABA, result, info[ "playerBase" ] )

	def teamChallengeUpLevel( self, maxLevel, minLevel ):
		# define method
		# 更新比赛等级
		self.teamChallengeLevel = ( maxLevel, minLevel )
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.teamChallengeUpLevel( maxLevel, minLevel )

	def teamChallengeUpInfo( self, result ):
		# define method
		# 更新当前队伍的排行
		self.teamChallengeInfo = result
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.teamChallengeUpInfo( result )

	def teamChallengeClose( self ):
		# define method
		# 组队擂台活动结束
		self.teamChallengeInfo = csdefine.MATCH_LEVEL_NONE
		self.teamChallengeLevel = None

	def teamChallengeOnRecruit( self ):
		# define method
		# 队伍正在招募
		self.teamChallengeRecruit = True
		for playerID, info in self.member:
			info[ "playerBase" ].client.teamChallengeOnRecruit()

	def teamChallengeCancelRecruit( self ):
		# define method
		# 队伍取消招募
		self.teamChallengeRecruit = False
		for playerID, info in self.member:
			info[ "playerBase" ].client.teamChallengeOnCRecruit()

	def teamChallengeRecruitComplete( self ):
		self.teamChallengeRecruit = False
		for playerID, info in self.member:
			info[ "playerBase" ].client.teamChallengeRecruitComplete()

	# ---------------------------------------------------------
	# 组队竞技
	# ---------------------------------------------------------
	def teamCompetitionNotify( self,level ):
		"""
		defined method

		组队竞技活动开始时调用此函数，更新参赛信息到每个队员的客户端
		@param :level  参与等级
		@type :level   UNIT16
		"""
		self.teamCompetitionLevel = level
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.teamCompetitionNotify( self.teamCompetitionLevel )

	def teamCompetitionGather( self ):
		# define method
		# 组队竞技集合开始
		self.teamCompetitionGatherFlag = True
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.teamCompetitionGather()
			playerBase.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

	def teamCompetitionCloseGather( self ):
		# define method

		# 关闭组队竞技的集合
		self.teamCompetitionGatherFlag = False
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_TEAM_COMPETITION )

	# ----------------------------------------------------------------
	# extensions of copy matcher.
	# ----------------------------------------------------------------
	def memberDBIDOfID( self, playerID ) :
		"""
		根据玩家ID返回
		"""
		info = self._getPlayerInfoByID( playerID )
		if info :
			return info["playerDBID"]
		else :
			return None

	def memberInfoOfDBID( self, playerDBID ) :
		"""
		"""
		return self._getMemberInfoByDBID( playerDBID )[1]

	def memberNames( self ) :
		"""
		获取成员的名字
		"""
		return tuple( [m[1]["playerName"] for m in self.member] )

	def memberNameOfDBID( self, playerDBID ) :
		"""
		获取与DBID对应的成员名字
		"""
		info = self.memberInfoOfDBID( playerDBID )
		if info :
			return info["playerName"]
		else :
			return ""

	def membersOnline( self ) :
		"""
		获取在线成员的mailbox
		"""
		return tuple( [m[1]["playerBase"] for m in self.member if m[1]["playerBase"]] )

	def memberMailboxOfDBID( self, playerDBID ) :
		"""
		获取与DBID对应的成员mailbox
		"""
		info = self.memberInfoOfDBID( playerDBID )
		if info :
			return info["playerBase"]
		else :
			return None

	def memberMailboxOfID( self, playerID ) :
		"""
		获取与id对应的成员mailbox
		"""
		info = self._getPlayerInfoByID( playerID )
		if info :
			return info["playerBase"]
		else :
			return None

	def allMembersAreOnline( self ) :
		"""
		所否所有成员都在线
		"""
		return len( self.leaveDBIDs ) == 0

	def contain( self, playerDBID ) :
		"""
		检查playerDBID是不是队员
		"""
		return self.memberInfoOfDBID( playerDBID ) is not None

	def containID( self, playerID ) :
		"""
		检查playerID是不是队员
		"""
		return self._getPlayerInfoByID( playerID ) is not None

	# ----------------------------------------------------------------
	# 英雄联盟PVP
	# ----------------------------------------------------------------
	def baoZangReqSucceed( self, teamMB ):
		"""
		define method
		英雄联盟副本PVP匹配成功
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.baoZangReqSucceed( teamMB )

	def baoZangSetRivalTeamIDs( self, rTeamIDs, t ):
		"""
		define method.
		接收对手队伍人员ID
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.baoZangSetRivalTeamIDs( rTeamIDs, t )
	
	def baoZangPVPonReq( self ):
		"""
		define method.
		队伍申请宝藏PVP
		"""
		self.baoZangPVPreqTime = time.time()
			
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.baoZangPVPonReq( self.baoZangPVPreqTime )
	
	def baoZangPVPonCancel( self, isMatch ):
		"""
		define method.
		队伍退出宝藏PVP的排队
		"""
		self.baoZangPVPreqTime  = 0
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.baoZangPVPonCancel( isMatch )
	
	# 阵营英雄联盟
	def yingXiongCampReqSucceed( self, teamMB ):
		"""
		define method
		英雄联盟副本PVP匹配成功
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.yingXiongCampReqSucceed( teamMB )

	def yingXiongCampSetRivalTeamIDs( self, rTeamIDs, t ):
		"""
		define method.
		接收对手队伍人员ID
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.cell.yingXiongCampSetRivalTeamIDs( rTeamIDs, t )
	
	def yingXiongCampOnReq( self ):
		"""
		define method.
		队伍申请宝藏PVP
		"""
		self.yingXiongCampReqTime = time.time()
			
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.yingXiongCampOnReq( self.yingXiongCampReqTime )
	
	def yingXiongCampOnCancel( self, isMatch ):
		"""
		define method.
		队伍退出宝藏PVP的排队
		"""
		self.yingXiongCampReqTime  = 0
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.yingXiongCampOnCancel( isMatch )
#
# $Log: not supported by cvs2svn $
# Revision 1.26  2008/03/01 00:59:43  zhangyuxing
# 重新处理 onTimer的 leave调用。 通过DBID 直接获得ID 去处理
#
# Revision 1.25  2008/02/29 07:00:44  zhangyuxing
# 在leave函数里面， 处理自动选择队长的条件有问题，已修改。
#
# Revision 1.24  2008/02/29 06:39:16  zhangyuxing
# 修改了 leaveDBIDs 里面的数据， 多加入一个 玩家ID， 主要是处理离对
#
# Revision 1.23  2008/02/28 01:06:21  zhangyuxing
# 修改在onTimer 中对 self.leave的错误调用
#
# Revision 1.22  2008/02/27 09:21:33  zhangyuxing
# 修改logout函数内部一处 引起 队长自动设置 出问题的 BUG。
#
# Revision 1.21  2007/12/08 07:54:19  yangkai
# self.member 类型由{entityID ： info,...}改成 [(entityID,Info),...]
# 通过dict([]) he {}.items() 自由转换，按顺序添加队伍，方便cell处理轮流拾取物品
#
# Revision 1.20  2007/11/16 03:41:55  zhangyuxing
# 调整：依据Team的接口addMember的变化，而在调用该接口时，多加入
# 玩家ID变量。
# 修改BUG：在logon接口中， info变量被外部使用了，而在循环中又用到
# 它，以至修改了他的信息。现在在循环中使用tempinfo替代。
#
# Revision 1.19  2007/11/15 07:05:55  phw
# method modified: _notifyPlayerTeamMemberInfo(), 修正了给在线玩家发送已下线队员时无法找到已下线队员的entityID的bug
#
# Revision 1.18  2007/10/09 07:51:41  phw
# 队伍代码调整，方法改名，优化实现方式，修正隐含的bug
#
# Revision 1.17  2007/06/19 09:26:27  kebiao
# captainID -->
# DATABASE_ID
# to:
# OBJECT_ID
#
# Revision 1.16  2007/06/14 09:25:01  huangyongwei
# 一些可调整值的宏定义被移动到 Const 中
#
# Revision 1.15  2007/06/14 03:06:48  panguankong
# 修改队伍client只使用objectID
#
# Revision 1.14  2007/04/04 09:15:36  panguankong
# 修改了下线离队时间
#
# Revision 1.13  2007/04/04 01:00:06  panguankong
# 添加了玩家离线后离队的处理，加了timer
#
# Revision 1.12  2007/03/01 08:14:58  panguankong
# 添加了处理开除玩家时，找不到下线玩家BASE的情况
#
# Revision 1.11  2007/01/31 04:22:57  panguankong
# 去掉了一个提前通知队伍信息的代码
#
# Revision 1.10  2007/01/29 01:37:48  panguankong
# 将队长通知放到队员信息发送以后
#
# Revision 1.9  2007/01/03 07:41:30  panguankong
# 修改了多玩家组队　先组的人看不到后进来的人的信息的BUG
#
# Revision 1.8  2007/01/03 01:49:19  panguankong
# 修改了队伍部分BUG
#
# Revision 1.7  2006/12/29 08:32:08  huangyongwei
# 修改了通知上线成员人位置
#
# Revision 1.6  2006/12/20 08:20:54  panguankong
# 修改　队长ID
#
# Revision 1.5  2006/12/20 06:56:29  panguankong
# 添加上线　队伍信息通知
#
# Revision 1.4  2006/11/29 10:25:42  panguankong
# no message
#
# Revision 1.3  2006/11/29 09:26:01  panguankong
# no message
#
# Revision 1.2  2006/11/29 09:02:06  panguankong
# no message
#
# Revision 1.1  2006/11/29 02:05:51  panguankong
# 添加了队伍系统
#