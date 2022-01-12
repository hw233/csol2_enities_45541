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
		self.preparedMember = []		# ��׼�����˵Ķ���[( dabaseID, playerName )]
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
		ƥ��
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
		һ����������
		"""
		if not hasWinner:		# û�л�ʤ��
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
		
		# �������������������
		for teamID in [ winTeamID, loseTeamID ]:
			BigWorld.globalData["TeamManager"].teamRemoteCall( teamID, "turnWar_onWarOver", () )
			self._teamDict.pop( teamID, 0 )
			if teamID in self._preparedTeam:
				self._preparedTeam.remove( teamID )
			
			self._recordWarData[ teamID ] = time.time()		# ��¼����ʱ��
		
		for matchInfos in self._matchedTeamData:				# ɾ��ƥ������
			if loseTeamID in matchInfos or winTeamID in matchInfos:
				self._matchedTeamData.remove( matchInfos )
	
	def onPlayerLeaveTeam( self, teamID ):
		if teamID in self._preparedTeam:
			self._preparedTeam.remove( teamID )
		
		self._teamDict.pop( teamID, 0 )

class TongTurnWarManager:
	"""
	��ᳵ��ս������
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
		��������ʼ�����
		"""
		taskEvents = {
					  	"TongTurnWar_start_notify"	: "onStartNotify",						# ��ʼ֪ͨ
					  	"TongTurnWar_sign_up_start" : "onSignUpStart",						# ��������
					  	"TongTurnWar_activity_end"	: "allWarOver",							# �����
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		
	def registerSpaceBase( self, spaceBase, teamIDs ):
		"""
		define method
		����baseע�ᵽ������
		
		@param teamIDs: ARRAY [ teamID1, teamID2 ]
		"""
		self.spaceBases.append( spaceBase )
		
		# ��¼�ѿ��������Ķ����ID
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
		��������
		"""
		self.turnWarControl.resert()
		BigWorld.globalData[ "TongTurnWarStep" ] = csconst.TONG_TURN_STEP_SIGNUP
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_TURN_WAR_SIGN_UP_START, [] )
		INFO_MSG( "TongTurnWarManager", "signup" )
	
	def onStartNotify( self ):
		"""
		define method
		��ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_TURN_WAR_SIGN_UP_NOTIFY, [] )
		INFO_MSG( "TongTurnWarManager", "notify" )
		
	def allWarOver( self ):
		"""
		define method
		�ر����и����
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
		һ��������ս��������
		
		@param loseTeamID: ս��һ���Ķ���ID
		@param winTeamID: ��ʤһ���Ķ���ID
		"""
		# �Ӱ��ĳ���ս����
		self.turnWarControl.onOneSpaceWarOver( self, loseTeamID, winTeamID, hasWinner )
		
	def signUp( self, teamMailbox, captainBase, memberMaxLevel, tongDBID, camp, cityName, captainName ):
		"""
		define method
		����
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
		ĳ�����׼������
		"""
		BigWorld.globalBases["TeamManager"].teamRemoteCall( teamID, "turnWar_onTeamMemPrepared", ( playerName, ) )
		self.turnWarControl.preparedMember( teamID, memberDBID, playerName )
		
	def requestEnterSpace( self, teamID, playerBase, playerName ):
		"""
		define method
		���������
		"""
		matchInfo = self.turnWarControl.getMatch( teamID )
		if teamID in matchInfo:
			playerBase.cell.gotoSpace( "fu_ben_bang_hui_che_lun_zhan",  ( 0, 0, 0 ), ( 0, 0, 0 ) )
			BigWorld.globalBases["TeamManager"].teamRemoteCall( matchInfo[0], "turnWar_onPlayerEnter", ( playerName, ) )
			BigWorld.globalBases["TeamManager"].teamRemoteCall( matchInfo[1], "turnWar_onPlayerEnter", ( playerName, ) )
		
	def onEnterTongTurnWarSpace( self, domainBase, position, direction, playerBase, params ):
		"""
		Define method.
		������복��������

		@param domainBase : �ռ��Ӧ��domain��base mailbox
		@type domainBase : MAILBOX
		@param position : ����ռ�ĳ�ʼλ��
		@type position : VECTOR3
		@param direction : ����ռ�ĳ�ʼ����
		@type direction : VECTOR3
		@param playerBase : ���base mailbox
		@type playerBase : MAILBOX
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT
		"""
		teamID = params["teamID"]
		databaseID = params["databaseID"]
		warInfo = self.turnWarControl.getMatch( teamID )
		isLogin = params.pop( "login", False )
		if not warInfo:#û��Ȩ���������
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
		if databaseID in [ i[0] for i in team_left.preparedMember[ 0 : csconst.TONG_TURN_FIGHT_MEM_NUM ] ] or databaseID in [ i[0] for i in team_right.preparedMember[ 0 : csconst.TONG_TURN_FIGHT_MEM_NUM ] ]:	# ��һ��׼������ҵ�һ������
			params["isFirstOrder"] = True
			
		if isLogin:
			domainBase.onLoginTurnWarSpace( playerBase, params, False )
		else:
			domainBase.onEnterTongTurnWarSpace( playerBase, direction, params )
		
	def onPlayerLeaveTeam( self, teamID ):
		"""
		define method
		
		�����Ӵ���
		"""
		self.turnWarControl.onPlayerLeaveTeam( teamID )
			
	def addTongTurnWarPoint( self, tongDBID, cityName, amount ):
		"""
		�����ӳ���ս����
		
		@param cityName: �ĸ����еĻ���
		@param amount: ��ֵ
		"""
		tongEntity = self.findTong( tongDBID )
		if not tongEntity:
			return
			
		tongEntity.addTongTurnWarPoint( cityName, amount )
		
	def updateTongTurnWarPoint( self, tongDBID, cityName, newAmount ):
		"""
		define method
		����ĳ���ĳ���ս���ֻ�������
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
		���³���ս��������
		"""
		# ��tongDBID���뵽�б����Ӧλ��,ʵ�ְ���������
		if self.turnWarPointTopTable.has_key( cityName ):	# turnWarPointTopTable{ cityName1: [tongDBID1, tongDBID2, ...], ... }
			cityPointTable = self.turnWarPointTopTable[ cityName ]
			
			if tongDBID in cityPointTable:
				cityPointTable.remove( tongDBID )			# �ȴ��б����Ƶ��˰���DBID
			
			for index, dbid in enumerate( cityPointTable ):
				for i in self._tongBaseDatas[ dbid ][ "tongTurnWarPoint" ]:
					if i["cityName"] == cityName and i["point"] < newAmount:
						cityPointTable.insert( index, tongDBID )
						self.writeToDB()
						return
			cityPointTable.append( tongDBID )		# �������ٵ����
		else:
			self.turnWarPointTopTable[ cityName ] = [ tongDBID ]	# ����ǵ�һ����ô˳��еĻ��ֵ����
		
		self.writeToDB()
		
	def onTongDismiss( self, tongDBID ):
		"""
		ĳ������ɢ��
		"""
		for list in self.turnWarPointTopTable.values():		# �Ӱ�ᳵ��ս�������а����Ƴ���¼
			if tongDBID in list:
				list.remove( tongDBID )
				
	def getTurnWarPointTopTable( self, camp ):
		"""
		��ȡturnWarPointTopTable,Ҳ���ǰ�ᳵ��ս����
		"""
		result = {}
		for k, tongList in self.turnWarPointTopTable.iteritems():
			result[ k ] = []
			for tid in tongList:
				tongCamp = self.getTongCampByDBID( tid )
				if camp == tongCamp:
					result[ k ].append( tid )
			
		return result
		