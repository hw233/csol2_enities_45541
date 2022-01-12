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
	def __init__( self, teamMailbox, memberMaxLevel, camp, cityName, captainName ):
		object.__init__( self )
		self.camp = camp
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
		return len( self.preparedMember ) >= csconst.CAMP_TURN_MEMBER_NUM

class TrunWarControl( object ):
	def __init__( self ):
		object.__init__( self )
		self._teamDict = {}
		self._preparedTeam = []
		self._matchedTeamData = []
		self._recordWarData = {}
	
	def addTeam( self, teamMailbox, memberMaxLevel, camp, cityName, captainName ):
		self._teamDict[ teamMailbox.id ] = teamInfos( teamMailbox, memberMaxLevel, camp, cityName, captainName )
	
	def resert( self ):
		self._teamDict = {}
		self._preparedTeam = []
		self._matchedTeamData = []
		self._recordWarData = {}
	
	def getTeam( self, teamID ):
		return self._teamDict.get( teamID, None )
	
	def getPreparedTeam( self, camp, city ):
		preparedTeams = []
		for teamID in self._preparedTeam:
			team = self._teamDict[ teamID ]
			if team.isPrepared() and team.camp != camp and team.chooseCityName == city:
				preparedTeams.append( team )
		
		if len( preparedTeams ):
			return random.choice( preparedTeams )
		else:
			return None
	
	def onPreparedMember( self, teamID, memberDBID, playerName ):
		if self._teamDict.has_key( teamID ):
			teamInfo = self._teamDict[ teamID ]
			teamInfo.onPreparedMember( memberDBID, playerName )
			if teamInfo.isPrepared():
				self.matchWar( teamInfo )
	
	def matchWar( self, teamInfo ):
		"""
		ƥ��
		"""
		matchTeam = self.getPreparedTeam( teamInfo.camp, teamInfo.chooseCityName )
		if matchTeam:
			self._matchedTeamData.append( ( teamInfo.getID(), matchTeam.getID() ) )
			teamInfo.teamMailbox.campTurnWar_onTeamMatched( matchTeam.teamMailbox, teamInfo.getPreparedMembers() )
			matchTeam.teamMailbox.campTurnWar_onTeamMatched( teamInfo.teamMailbox, matchTeam.getPreparedMembers() )
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
				mgr.turnWar_reward( winTeamID, winTeam.chooseCityName, csconst.CAMP_TURN_WIN_POINT )
				
				loseTeam = self.getTeam( loseTeamID )
				if loseTeam:
					g_logger.actResultLog( csdefine.SPACE_TYPE_CAMP_TURN_WAR, winTeam.chooseCityName, winTeam.preparedMember, loseTeam.preparedMember )
				else:
					g_logger.actResultLog( csdefine.SPACE_TYPE_CAMP_TURN_WAR,  winTeam.chooseCityName, winTeam.preparedMember, 0, 0 )
		
		# �������������������
		for teamID in [ winTeamID, loseTeamID ]:
			BigWorld.globalData["TeamManager"].teamRemoteCall( teamID, "campTurnWar_onWarOver", () )
			self._teamDict.remove( teamID )
			self._preparedTeam.remove( teamID )
			
			self._recordWarData[ teamID ] = time.time()		# ��¼����ʱ��
		
		for matchInfos in self._matchedTeamData:				# ɾ��ƥ������
			if loseTeamID in matchInfos or winTeamID in matchInfos:
				self._matchedTeamData.remove( matchInfos )
	
	def onPlayerLeaveTeam( self, teamID ):
		if teamID in self._preparedTeam:
			self._preparedTeam.remove( teamID )
		
		self._teamDict.pop( teamID, 0 )

class CampTurnWarManager:
	"""
	��Ӫ����ս������
	"""
	def __init__( self ):
		self.spaceBases = []
		self.turnWarControl = TrunWarControl()
		
		self.turnWarPointTopTable = {}
		BigWorld.globalData[ "CampTurnWarStep" ] = csconst.CAMP_TURN_STEP_END
		BigWorld.globalData["CampTurnWarHasSpaceTeam"] = []
	
	def registerCrond( self ):
		"""
		virtual method.
		��������ʼ�����
		"""
		taskEvents = {
					  	"CampTurnWar_start_notify"	: "turnWar_onStartNotify",						# ��ʼ֪ͨ
					  	"CampTurnWar_sign_up_start" : "turnWar_onSignUpStart",						# ��������
					  	"CampTurnWar_activity_end"	: "turnWar_allWarOver",							# �����
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		
	def turnWar_registerSpaceBase( self, spaceBase, teamIDs ):
		"""
		define method
		����baseע�ᵽ������
		
		@param teamIDs: ARRAY [ teamID1, teamID2 ]
		"""
		self.spaceBases.append( spaceBase )
		
		# ��¼�ѿ��������Ķ����ID
		temp = BigWorld.globalData["CampTurnWarHasSpaceTeam"]
		temp.extend( teamIDs )
		BigWorld.globalData["CampTurnWarHasSpaceTeam"] = temp
	
	def turnWar_unRegisterSpaceBase( self, spaceBase, teamIDs ):
		"""
		define method
		"""
		for i in self.spaceBases:
			if i.id == spaceBase.id:
				self.spaceBases.remove( i )
		
		temp = BigWorld.globalData["CampTurnWarHasSpaceTeam"]
		for id in teamIDs:
			if id in temp:
				temp.remove( id )
		BigWorld.globalData["CampTurnWarHasSpaceTeam"] = temp
		
	def turnWar_onSignUpStart( self ):
		"""
		define method
		��������
		"""
		self.turnWarControl.resert()
		BigWorld.globalData[ "CampTurnWarStep" ] = csconst.CAMP_TURN_STEP_SIGNUP
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_TURN_WAR_SIGN_UP_START, [] )
		INFO_MSG( "CampTurnWarManager", "signup" )
	
	def turnWar_onStartNotify( self ):
		"""
		define method
		��ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_TURN_WAR_SIGN_UP_NOTIFY, [] )
		INFO_MSG( "CampTurnWarManager", "notify" )
		
	def turnWar_allWarOver( self ):
		"""
		define method
		�ر����и����
		"""
		BigWorld.globalData[ "CampTurnWarStep" ] = csconst.CAMP_TURN_STEP_END
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_TURN_WAR_END, [] )
		for spaceBase in self.spaceBases:
			spaceBase.onActivityOver()
		self.turnWarControl.resert()
		INFO_MSG( "CampTurnWarManager", "end" )
		
	def turnWar_onOneSpaceWarOver( self, loseTeamID, winTeamID, hasWinner ):
		"""
		define method
		һ��������ս��������
		
		@param loseTeamID: ս��һ���Ķ���ID
		@param winTeamID: ��ʤһ���Ķ���ID
		"""
		# ����Ӫ�ĳ���ս����
		self.turnWarControl.onOneSpaceWarOver( self, loseTeamID, winTeamID, hasWinner )
		
	def turnWar_signUp( self, teamMailbox, captainBase, memberMaxLevel, camp, cityName, captainName ):
		"""
		define method
		����
		"""
		teamID = teamMailbox.id
		if cityName not in csconst.CAMP_CITYWAR_CITY_MAPS:
			ERROR_MSG("Sign up Camp turn war error. No such a city ( %s )." % cityName )
			return
		
		joinInfo = self.turnWarControl.getTeam( teamID )
		if joinInfo:
			joinCityName = joinInfo.chooseCityName
			captainBase.client.onStatusMessage( csstatus.CAMP_TURN_REPEAT_SIGNUP, str(( csconst.CAMP_CITYWAR_CITY_MAPS[ joinCityName ], )) )
			return
			
		self.turnWarControl.addTeam( teamMailbox, memberMaxLevel, camp, cityName, captainName )
		captainBase.client.onStatusMessage( csstatus.CAMP_TURN_WAR_SIGNUP_SIGNUP_SUCCESS,"" )
		teamMailbox.campTurnWar_onSignUp()
		
	def turnWar_onTeamMemberPrepared( self, teamID, memberDBID, playerName ):
		"""
		define method
		ĳ�����׼������
		"""
		BigWorld.globalBases["TeamManager"].teamRemoteCall( teamID, "campTurnWar_onTeamMemPrepared", ( playerName, ) )
		self.turnWarControl.onPreparedMember( teamID, memberDBID, playerName )
		
	def turnWar_requestEnterSpace( self, teamID, playerBase, playerName ):
		"""
		define method
		���������
		"""
		matchInfo = self.turnWarControl.getMatch( teamID )
		if teamID in matchInfo:
			playerBase.cell.gotoSpace( "fu_ben_camp_che_lun_zhan", ( 0, 0, 0 ), ( 0, 0, 0 ) )
			BigWorld.globalBases["TeamManager"].teamRemoteCall( matchInfo[0], "campTurnWar_onPlayerEnter", ( playerName, ) )
			BigWorld.globalBases["TeamManager"].teamRemoteCall( matchInfo[1], "campTurnWar_onPlayerEnter", ( playerName, ) )
		
	def turnWar_onEnterCampTurnWarSpace( self, domainBase, position, direction, playerBase, params ):
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
				playerBase.client.onStatusMessage( csstatus.CAMP_TURN_WAR_CANNOT_ENTER, "" )
			return
			
		team_left = self.turnWarControl.getTeam( warInfo[ 0 ] )
		team_right = self.turnWarControl.getTeam( warInfo[ 1 ] )
		team_left_pick =  { "teamID": team_left.getID(), "orderedPlayer": team_left.preparedMember, "captainName": team_left.captainName }
		team_right_pick =  { "teamID": team_right.getID(), "orderedPlayer": team_right.preparedMember, "captainName": team_right.captainName }
		params[ "team_left" ] = team_left_pick
		params[ "team_right" ] = team_right_pick
		params[ "isFirstOrder" ] = False
		if databaseID == team_left.preparedMember[0][0] or databaseID == team_right.preparedMember[0][0]:	# ��һ��׼������ҵ�һ������
			params["isFirstOrder"] = True
			
		if isLogin:
			domainBase.onLoginTurnWarSpace( playerBase, params, False )
		else:
			domainBase.onEnterCampTurnWarSpace( playerBase, direction, params )
		
	def turnWar_onPlayerLeaveTeam( self, teamID ):
		"""
		define method
		
		�����Ӵ���
		"""
		self.turnWarControl.onPlayerLeaveTeam( teamID )
			
	def turnWar_reward( self, winTeamID, cityName, amount ):
		"""
		���ӳ���ս����
		@param winTeamID: ʤ���İ��
		@param cityName: �ĸ����еĻ���
		@param amount: ��ֵ
		"""
		pass