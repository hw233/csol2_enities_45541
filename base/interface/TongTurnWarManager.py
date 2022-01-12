# -*- coding: gb18030 -*-

import BigWorld
import time
import random
import Love3
import csconst
import csstatus
import csdefine
import cschannel_msgs
from bwdebug import *
from MsgLogger import g_logger

from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

class teamInfos( object ):
	def __init__( self, teamMailbox, memberMaxLevel, tongDBID, camp, cityName, captainName ):
		object.__init__( self )
		self.camp = camp
		self.tongDBID = tongDBID
		self.teamMailbox = teamMailbox
		self.teamLevel =  memberMaxLevel/10 * 10
		self.preparedMember = []		# 已准备好了的队友[( dabaseID, playerName )]
		self.chooseCityName = cityName
		self.captainName =  captainName
	
	def getID( self ):
		return self.teamMailbox.id
	
	def onPreparedMember( self, memberDBID, playerName ):
		self.preparedMember.append( ( memberDBID, playerName ) )
	
	def getPreparedMembers( self ):
		return [ mem[0] for mem in self.preparedMember ]
	
	def isPrepared( self ):
		return len( self.preparedMember ) >= csconst.TONG_TURN_MEMBER_NUM

class TrunWarControl( object ):
	def __init__( self ):
		object.__init__( self )
		self._teamDict = {}
		self._preparedTeam = []
		self._matchedTeamData = []
		self._recordWarData = {}
	
	def addTeam( self, teamMailbox, memberMaxLevel, tongDBID, camp, cityName, captainName ):
		self._teamDict[ teamMailbox.id ] = teamInfos( teamMailbox, memberMaxLevel, tongDBID, camp, cityName, captainName )
	
	def resert( self ):
		self._teamDict = {}
		self._preparedTeam = []
		self._matchedTeamData = []
		self._recordWarData = {}
	
	def getTeam( self, teamID ):
		return self._teamDict.get( teamID, None )
	
	def getPreparedTeam( self, camp, tongDBID, city ):
		preparedTeams = []
		for teamID in self._preparedTeam:
			team = self._teamDict[ teamID ]
			if team.isPrepared() and team.camp == camp and team.tongDBID != tongDBID and team.chooseCityName == city:
				preparedTeams.append( team )
		
		if len( preparedTeams ):
			return random.choice( preparedTeams )
		else:
			return None
	
	def preparedMember( self, teamID, memberDBID, playerName ):
		if self._teamDict.has_key( teamID ):
			teamInfo = self._teamDict[ teamID ]
			teamInfo.onPreparedMember( memberDBID, playerName )
			if teamInfo.isPrepared():
				self.matchWar( teamInfo )
	
	def matchWar( self, teamInfo ):
		"""
		匹配
		"""
		matchTeam = self.getPreparedTeam( teamInfo.camp, teamInfo.tongDBID, teamInfo.chooseCityName )
		if matchTeam:
			self._matchedTeamData.append( ( teamInfo.getID(), matchTeam.getID() ) )
			teamInfo.teamMailbox.turnWar_onTeamMatched( matchTeam.teamMailbox, teamInfo.getPreparedMembers() )
			matchTeam.teamMailbox.turnWar_onTeamMatched( teamInfo.teamMailbox, matchTeam.getPreparedMembers() )
			self._preparedTeam.remove( matchTeam.getID() )
		else:
			self._preparedTeam.append( teamInfo.getID() )
	
	def getMatch( self, teamID ):
		for info in self._matchedTeamData:
			if teamID in info:
				return info
		
		return []
	
	def onOneSpaceWarOver( self, mgr, loseTeamID, winTeamID, hasWinner ):
		"""
		一场比赛结束
		"""
		if not hasWinner:		# 没有获胜者
			INFO_MSG("turn war space has no winner.teamIDs( %s, %s )" % ( loseTeamID, winTeamID ) )
			pass
		else:
			winTeam = self.getTeam( winTeamID )
			if winTeam:
				mgr.addTongTurnWarPoint( winTeam.tongDBID, winTeam.chooseCityName, csconst.TONG_TURN_WIN_POINT )
				
				loseTeam = self.getTeam( loseTeamID )
				if loseTeam:
					g_logger.actResultLog( csdefine.SPACE_TYPE_TONG_TURN_WAR, winTeam.chooseCityName, winTeam.tongDBID, winTeam.preparedMember, loseTeam.tongDBID, loseTeam.preparedMember )
				else:
					g_logger.actResultLog( csdefine.SPACE_TYPE_TONG_TURN_WAR,  winTeam.chooseCityName, winTeam.tongDBID, winTeam.preparedMember, 0, 0 )
		
		# 清除两个队伍的相关数据
		for teamID in [ winTeamID, loseTeamID ]:
			BigWorld.globalData["TeamManager"].teamRemoteCall( teamID, "turnWar_onWarOver", () )
			self._teamDict.pop( teamID, 0 )
			if teamID in self._preparedTeam:
				self._preparedTeam.remove( teamID )
			
			self._recordWarData[ teamID ] = time.time()		# 记录参赛时间
		
		for matchInfos in self._matchedTeamData:				# 删除匹配数据
			if loseTeamID in matchInfos or winTeamID in matchInfos:
				self._matchedTeamData.remove( matchInfos )
	
	def onPlayerLeaveTeam( self, teamID ):
		if teamID in self._preparedTeam:
			self._preparedTeam.remove( teamID )
		
		self._teamDict.pop( teamID, 0 )

class TongTurnWarManager:
	"""
	帮会车轮战管理器
	"""
	def __init__( self ):
		self.spaceBases = []
		self.turnWarControl = TrunWarControl()
		
		self.turnWarPointTopTable = {}
		BigWorld.globalData[ "TongTurnWarStep" ] = csconst.TONG_TURN_STEP_END
		BigWorld.globalData["TurnWarHasSpaceTeam"] = []
	
	def onManagerInitOver( self ):
		"""
		virtual method.
		管理器初始化完毕
		"""
		taskEvents = {
					  	"TongTurnWar_start_notify"	: "onStartNotify",						# 开始通知
					  	"TongTurnWar_sign_up_start" : "onSignUpStart",						# 开启报名
					  	"TongTurnWar_activity_end"	: "allWarOver",							# 活动结束
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		
	def registerSpaceBase( self, spaceBase, teamIDs ):
		"""
		define method
		副本base注册到管理器
		
		@param teamIDs: ARRAY [ teamID1, teamID2 ]
		"""
		self.spaceBases.append( spaceBase )
		
		# 记录已开启副本的队伍的ID
		temp = BigWorld.globalData["TurnWarHasSpaceTeam"]
		temp.extend( teamIDs )
		BigWorld.globalData["TurnWarHasSpaceTeam"] = temp
	
	def unRegisterSpaceBase( self, spaceBase, teamIDs ):
		"""
		define method
		"""
		for i in self.spaceBases:
			if i.id == spaceBase.id:
				self.spaceBases.remove( i )
		
		temp = BigWorld.globalData["TurnWarHasSpaceTeam"]
		for id in teamIDs:
			if id in temp:
				temp.remove( id )
		BigWorld.globalData["TurnWarHasSpaceTeam"] = temp
		
	def onSignUpStart( self ):
		"""
		define method
		报名开启
		"""
		self.turnWarControl.resert()
		BigWorld.globalData[ "TongTurnWarStep" ] = csconst.TONG_TURN_STEP_SIGNUP
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_TURN_WAR_SIGN_UP_START, [] )
		INFO_MSG( "TongTurnWarManager", "signup" )
	
	def onStartNotify( self ):
		"""
		define method
		开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_TURN_WAR_SIGN_UP_NOTIFY, [] )
		INFO_MSG( "TongTurnWarManager", "notify" )
		
	def allWarOver( self ):
		"""
		define method
		关闭所有副本活动
		"""
		BigWorld.globalData[ "TongTurnWarStep" ] = csconst.TONG_TURN_STEP_END
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_TURN_WAR_END, [] )
		for spaceBase in self.spaceBases:
			spaceBase.onActivityOver()
		self.turnWarControl.resert()
		INFO_MSG( "TongTurnWarManager", "end" )
		
	def onOneSpaceWarOver( self, loseTeamID, winTeamID, hasWinner ):
		"""
		define method
		一个副本的战斗结束了
		
		@param loseTeamID: 战败一方的队伍ID
		@param winTeamID: 获胜一方的队伍ID
		"""
		# 加帮会的车轮战积分
		self.turnWarControl.onOneSpaceWarOver( self, loseTeamID, winTeamID, hasWinner )
		
	def signUp( self, teamMailbox, captainBase, memberMaxLevel, tongDBID, camp, cityName, captainName ):
		"""
		define method
		报名
		"""
		teamID = teamMailbox.id
		if cityName not in csconst.TONG_CITYWAR_CITY_MAPS:
			ERROR_MSG("Sign up tong turn war error. No such a city ( %s )." % cityName )
			return
		
		joinInfo = self.turnWarControl.getTeam( teamID )
		if joinInfo:
			joinCityName = joinInfo.chooseCityName
			captainBase.client.onStatusMessage( csstatus.TONG_TURN_REPEAT_SIGNUP, str(( csconst.TONG_CITYWAR_CITY_MAPS[ joinCityName ], )) )
			return
			
		self.turnWarControl.addTeam( teamMailbox, memberMaxLevel, tongDBID, camp, cityName, captainName )
		captainBase.client.onStatusMessage( csstatus.TONG_TURN_WAR_SIGNUP_SIGNUP_SUCCESS,"" )
		teamMailbox.turnWar_onSignUpTong()
		
	def onTeamMemberPrepared( self, teamID, memberDBID, playerName ):
		"""
		define method
		某个玩家准备好了
		"""
		BigWorld.globalBases["TeamManager"].teamRemoteCall( teamID, "turnWar_onTeamMemPrepared", ( playerName, ) )
		self.turnWarControl.preparedMember( teamID, memberDBID, playerName )
		
	def requestEnterSpace( self, teamID, playerBase, playerName ):
		"""
		define method
		请求进副本
		"""
		matchInfo = self.turnWarControl.getMatch( teamID )
		if teamID in matchInfo:
			playerBase.cell.gotoSpace( "fu_ben_bang_hui_che_lun_zhan",  ( 0, 0, 0 ), ( 0, 0, 0 ) )
			BigWorld.globalBases["TeamManager"].teamRemoteCall( matchInfo[0], "turnWar_onPlayerEnter", ( playerName, ) )
			BigWorld.globalBases["TeamManager"].teamRemoteCall( matchInfo[1], "turnWar_onPlayerEnter", ( playerName, ) )
		
	def onEnterTongTurnWarSpace( self, domainBase, position, direction, playerBase, params ):
		"""
		Define method.
		请求进入车轮赛副本

		@param domainBase : 空间对应的domain的base mailbox
		@type domainBase : MAILBOX
		@param position : 进入空间的初始位置
		@type position : VECTOR3
		@param direction : 进入空间的初始面向
		@type direction : VECTOR3
		@param playerBase : 玩家base mailbox
		@type playerBase : MAILBOX
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT
		"""
		teamID = params["teamID"]
		databaseID = params["databaseID"]
		warInfo = self.turnWarControl.getMatch( teamID )
		isLogin = params.pop( "login", False )
		if not warInfo:#没有权利参与比赛
			if isLogin:
				playerBase.logonSpaceInSpaceCopy()
			else:
				playerBase.client.onStatusMessage( csstatus.TONG_TURN_WAR_CANNOT_ENTER, "" )
			return
			
		team_left = self.turnWarControl.getTeam( warInfo[ 0 ] )
		team_right = self.turnWarControl.getTeam( warInfo[ 1 ] )
		team_left_pick =  { "teamID": team_left.getID(), "orderedPlayer": team_left.preparedMember, "captainName": team_left.captainName }
		team_right_pick =  { "teamID": team_right.getID(), "orderedPlayer": team_right.preparedMember, "captainName": team_right.captainName }
		params[ "team_left" ] = team_left_pick
		params[ "team_right" ] = team_right_pick
		params[ "isFirstOrder" ] = False
		if databaseID in [ i[0] for i in team_left.preparedMember[ 0 : csconst.TONG_TURN_FIGHT_MEM_NUM ] ] or databaseID in [ i[0] for i in team_right.preparedMember[ 0 : csconst.TONG_TURN_FIGHT_MEM_NUM ] ]:	# 第一个准备的玩家第一个出场
			params["isFirstOrder"] = True
			
		if isLogin:
			domainBase.onLoginTurnWarSpace( playerBase, params, False )
		else:
			domainBase.onEnterTongTurnWarSpace( playerBase, direction, params )
		
	def onPlayerLeaveTeam( self, teamID ):
		"""
		define method
		
		玩家离队处理
		"""
		self.turnWarControl.onPlayerLeaveTeam( teamID )
			
	def addTongTurnWarPoint( self, tongDBID, cityName, amount ):
		"""
		给帮会加车轮战积分
		
		@param cityName: 哪个城市的积分
		@param amount: 分值
		"""
		tongEntity = self.findTong( tongDBID )
		if not tongEntity:
			return
			
		tongEntity.addTongTurnWarPoint( cityName, amount )
		
	def updateTongTurnWarPoint( self, tongDBID, cityName, newAmount ):
		"""
		define method
		更新某帮会的车轮战积分基础数据
		"""
		for i in self._tongBaseDatas[ tongDBID ][ "tongTurnWarPoint" ]:
			if i["cityName"] == cityName:
				i["point"] = newAmount
				self.updateTurnWarTopTable( tongDBID, cityName, newAmount )
				return
				
		info = { "cityName": cityName, "point": newAmount }
		self._tongBaseDatas[ tongDBID ][ "tongTurnWarPoint" ].append(info)
		self.updateTurnWarTopTable( tongDBID, cityName, newAmount )
	
	def updateTurnWarTopTable( self, tongDBID, cityName, newAmount ):
		"""
		更新车轮战积分排名
		"""
		# 将tongDBID插入到列表的相应位置,实现按积分排序
		if self.turnWarPointTopTable.has_key( cityName ):	# turnWarPointTopTable{ cityName1: [tongDBID1, tongDBID2, ...], ... }
			cityPointTable = self.turnWarPointTopTable[ cityName ]
			
			if tongDBID in cityPointTable:
				cityPointTable.remove( tongDBID )			# 先从列表中移掉此帮会的DBID
			
			for index, dbid in enumerate( cityPointTable ):
				for i in self._tongBaseDatas[ dbid ][ "tongTurnWarPoint" ]:
					if i["cityName"] == cityName and i["point"] < newAmount:
						cityPointTable.insert( index, tongDBID )
						self.writeToDB()
						return
			cityPointTable.append( tongDBID )		# 积分最少的情况
		else:
			self.turnWarPointTopTable[ cityName ] = [ tongDBID ]	# 帮会是第一个获得此城市的积分的情况
		
		self.writeToDB()
		
	def onTongDismiss( self, tongDBID ):
		"""
		某个帮会解散了
		"""
		for list in self.turnWarPointTopTable.values():		# 从帮会车轮战积分排行榜中移除记录
			if tongDBID in list:
				list.remove( tongDBID )
				
	def getTurnWarPointTopTable( self, camp ):
		"""
		获取turnWarPointTopTable,也就是帮会车轮战排名
		"""
		result = {}
		for k, tongList in self.turnWarPointTopTable.iteritems():
			result[ k ] = []
			for tid in tongList:
				tongCamp = self.getTongCampByDBID( tid )
				if camp == tongCamp:
					result[ k ].append( tid )
			
		return result
		