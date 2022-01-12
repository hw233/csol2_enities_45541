# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *
import random
import csdefine
import cschannel_msgs 
import csstatus
import cPickle
import Love3
import time
import RoleMatchRecorder
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
import items
g_items = items.instance()


class TeamCompetitionMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "TeamCompetitionMgr", self._onRegisterManager )
		self.teamList = {}		#{ level:{ teamID:{ teamMailbox,captainMailbox } } }
		self.joinPlayerInfo = {}	#{ playerName:[ playerMailbox,teamID,level ] }
		self.leavePlayerIDs = []	#[ playerID ]
		
		self.signUpTimer1 = 0	# ����ͨ��TimerID
		self.signUpTimer2 = 0
		self.signUpTimer3 = 0
		self.signUpTimer4 = 0
		
		self.enterTimer1 = 0	# �볡ͨ��TimerID
		self.enterTimer2 = 0
		self.enterTimer3 = 0
		self.enterTimer4 = 0
		
		self.startEnterTimer = 0		# �볡��ʼTimerID
		self.endEnterTimer = 0			# �����볡TimerID
		self.endTimer = 0				# �����TimerID

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TeamCompetitionMgr Fail!" )
			# again
			self.registerGlobally( "TeamCompetitionMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["TeamCompetitionMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("TeamCompetitionMgr Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"teamCompetition_signup_start" : "onSignupStart",
						"teamCompetition_signup_end" : "onStart",
					  }

		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		BigWorld.globalData["Crond"].addAutoStartScheme( "teamCompetition_signup_start", self, "onSignupStart" )
				
	def onSignupStart( self ):
		"""
		define method.
		������ʼ
		"""
		self.clearData()
		self.onStartNotice()
		BigWorld.globalData[ "teamCompetitionSingUp" ] = True
		BigWorld.globalBases["TeamManager"].addDeregisterListener( self )
		INFO_MSG( "TeamCompetitionMgr", "signup", "" )
		
	def clearData( self ):
		"""
		�������
		"""
		self.teamList = {}
		self.joinPlayerInfo = {}
		self.leavePlayerIDs = []
		if BigWorld.globalData.has_key("teamCompetitionStartEnterTime"):
			del BigWorld.globalData["teamCompetitionStartEnterTime"]
		if BigWorld.globalData.has_key( "AS_TeamCompetition" ):
			del BigWorld.globalData[ "AS_TeamCompetition" ]
		if BigWorld.globalData.has_key( "teamCompetitionEnter" ):
			del BigWorld.globalData[ "teamCompetitionEnter" ]
		if BigWorld.globalData.has_key( "teamCompetitionSingUp" ):
			del BigWorld.globalData[ "teamCompetitionSingUp" ]
		for i in BigWorld.globalData.keys():
			if "TeamCompetitionSelectedTeam_" in i:
				del BigWorld.globalData[i]
		BigWorld.globalBases["TeamManager"].removeDeregisterListener( self )
		if self.signUpTimer1 > 0:
			self.delTimer( self.signUpTimer1 )
			self.signUpTimer1 = 0
		if self.signUpTimer2 > 0:
			self.delTimer( self.signUpTimer2 )
			self.signUpTimer2 = 0
		if self.signUpTimer3 > 0:
			self.delTimer( self.signUpTimer3 )
			self.signUpTimer3 = 0
		if self.signUpTimer4 > 0:
			self.delTimer( self.signUpTimer4 )
			self.signUpTimer4 = 0
		if self.enterTimer1 > 0:
			self.delTimer( self.enterTimer1 )
			self.enterTimer1 = 0
		if self.enterTimer2 > 0:
			self.delTimer( self.enterTimer2 )
			self.enterTimer2 = 0
		if self.enterTimer3 > 0:
			self.delTimer( self.enterTimer3 )
			self.enterTimer3 = 0
		if self.enterTimer4 > 0:
			self.delTimer( self.enterTimer4 )
			self.enterTimer4 = 0
		if self.startEnterTimer > 0:
			self.delTimer( self.startEnterTimer )
			self.startEnterTimer = 0
		if self.endEnterTimer > 0:
			self.delTimer( self.endEnterTimer )
			self.endEnterTimer = 0
		if self.endTimer > 0:
			self.delTimer( self.endTimer )
			self.endTimer = 0
	
	def initCompetitionData( self ):
		"""
		��ʼ����������,�ںϸ�Ķ����������ȡʮ֧����
		"""
		allTeamsID = []
		for i in self.teamList:
			if len(self.teamList[i]) <= 10:			#�����ϸ�Ķ������ʮ��ʱ�����������ȡʮ������μӾ���
				chooseOutList = self.teamList[i].keys()
			else:
				chooseOutList = random.sample( self.teamList[i].keys() ,10 )
			
			for teamID in self.teamList[i].keys():
				if teamID in chooseOutList:
					allTeamsID.append( teamID )
					self.teamList[i][teamID]["teamMailbox"].teamCompetitionNotify( i )
					self.teamList[i][teamID]["teamMailbox"].setMessage( csstatus.TEAM_COMPETITION_CHOOSE_SUCCESS )
					self.teamList[i][teamID]["teamMailbox"].teamCompetitionGather()
					INFO_MSG("Team(%i) has been select to join TeamCompetitionMgr in level %i"%( teamID, i ))
					BigWorld.globalData[ 'TeamCompetitionSelectedTeam_%i'%teamID ] = i
				else:
					self.teamList[i][teamID]["teamMailbox"].setMessage( csstatus.TEAM_COMPETITION_CHOOSE_LOST )
					self.teamList[i][teamID]["teamMailbox"].teamCompetitionNotify( 0 )
					del self.teamList[i][teamID]
			
	def onStart( self ):
		"""
		define method.
		�볡��ʼ
		"""
		BigWorld.globalData["teamCompetitionStartEnterTime"] = time.time()
		self.endTimer = self.addTimer( 37 * 60 )			# �����ʱ�䣨30���ӱ���ʱ��+5�����볡ʱ��+2���ӽ���ʱ�� ��
		if self.signUpTimer1 > 0:
			self.delTimer( self.signUpTimer1 )
			self.signUpTimer1 = 0
		if self.signUpTimer2 > 0:
			self.delTimer( self.signUpTimer2 )
			self.signUpTimer2 = 0
		if self.signUpTimer3 > 0:
			self.delTimer( self.signUpTimer3 )
			self.signUpTimer3 = 0
		if self.signUpTimer4 > 0:
			self.delTimer( self.signUpTimer4 )
			self.signUpTimer4 = 0
			
		self.endEnterTimer = self.addTimer( 5 * 60 )		# 5���Ӻ�����볡
		
		if BigWorld.globalData.has_key( "teamCompetitionSingUp" ):
			del BigWorld.globalData[ "teamCompetitionSingUp" ]
		
		BigWorld.globalData[ "teamCompetitionEnter" ] = True
			
		self.initCompetitionData()
		if BigWorld.globalData.has_key( "AS_TeamCompetition" ) and BigWorld.globalData[ "AS_TeamCompetition" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "��Ӿ�����������ڽ��У�%i��%i����ͼ�ٴο�ʼ��Ӿ���������"%(curTime[3],curTime[4] ) )
			return
		
		self.enterTimer1 = self.addTimer( 60 )
		self.enterTimer2 = self.addTimer( 120 )
		self.enterTimer3 = self.addTimer( 180 )
		self.enterTimer4 = self.addTimer( 240 )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY % str(5), [] )
		BigWorld.globalData[ "AS_TeamCompetition" ] = True
		
		for i in BigWorld.globalData.keys():
			if "TeamCompetition_" in i:
				del BigWorld.globalData[i]
		
		INFO_MSG( "TeamCompetitionMgr", "start", "" )
		
	def onEndEnter( self ):
		"""
		�����볡ʱ�Ĵ���
		"""
		if BigWorld.globalData.has_key( "teamCompetitionEnter" ):
			del BigWorld.globalData[ "teamCompetitionEnter" ]
		for i in self.teamList:
			for teamID in self.teamList[i].keys():
				self.teamList[i][teamID]["teamMailbox"].teamCompetitionCloseGather()
		
	def onStartNotice( self ):
		"""
		define method.
		
		������ʼ
		"""
		self.signUpTimer1 = self.addTimer( 900 )
		self.signUpTimer2 = self.addTimer( 1800 )
		self.signUpTimer3 = self.addTimer( 2700 )
		self.signUpTimer4= self.addTimer( 3000 )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY_0 % str(55), [] )
		INFO_MSG( "TeamCompetitionMgr", "notice", "" )

	def setSignUpTime( self, restTime ):
		"""
		defined method
		
		����ʣ�౨��ʱ��
		"""
		if self.startEnterTimer > 0:
			self.delTimer( self.startEnterTimer )
			self.startEnterTimer = 0
		self.startEnterTimer = self.addTimer( restTime )
		
	def onTimer( self, id, userArg ):
		#������ʾ
		if id == self.signUpTimer1:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY_0 % str(40), [] )
			self.signUpTimer1 = 0
		if id == self.signUpTimer2:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY_0 % str(25), [] )
			self.signUpTimer2 = 0
		if id == self.signUpTimer3:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY_0 % str(10), [] )
			self.signUpTimer3 = 0
		if id == self.signUpTimer4:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY_0 % str(5), [] )
			self.signUpTimer4 = 0
		
		#�볡��ʾ
		if id == self.enterTimer1:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY % str(4), [] )
			self.enterTimer1 = 0
		if id == self.enterTimer2:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY % str(3), [] )
			self.enterTimer2 = 0
		if id == self.enterTimer3:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY % str(2), [] )
			self.enterTimer3 = 0
		if id == self.enterTimer4:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_BEGIN_NOTIFY % str(1), [] )
			self.enterTimer4 = 0
		
		if id == self.startEnterTimer:
			self.onStart()
			self.startEnterTimer = 0
		if id == self.endEnterTimer:
			self.onEndEnter()
			self.endEnterTimer = 0
		if id == self.endTimer:
			self.onEnd()
			self.endTimer = 0
			
	def onEnd( self ):
		"""
		define method.
		
		�����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TEAMCOMPETITION_END_NOTIFY, [] )
		if BigWorld.globalData.has_key( "AS_TeamCompetition" ):
			del BigWorld.globalData[ "AS_TeamCompetition" ]
			
		for i in self.joinPlayerInfo:
			item = g_items.createDynamicItem( 60101249,1 )			#���;��鵤
			itemDatas = []
			if item:
				item.setLevel( self.joinPlayerInfo[i][2] )		# ���þ��鵤�ȼ�Ϊ��ɫ�ȼ�
				tempDict = item.addToDict()
				del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
				itemData = cPickle.dumps( tempDict, 2 )
				itemDatas.append( itemData )
			
			BigWorld.globalData["MailMgr"].send(None, i, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,  cschannel_msgs.SHARE_SYSTEM,cschannel_msgs.TEAMCOMPETITION_MAIL_EXP_TITLE,"", 0, itemDatas)
		
		for i in self.teamList:
			for teamID in self.teamList[i].keys():
				self.teamList[i][teamID]["teamMailbox"].teamCompetitionNotify( 0 )
				
		self.clearData()
		INFO_MSG( "TeamCompetitionMgr", "end", "" )
	
	def requestTeamCompetition( self,playerMailbox,level, teamMailbox ):
		"""
		defined method.
		
		������Ӿ���
		"""
		teamID = teamMailbox.id
		if not self.teamList.has_key( level ):
			self.teamList[level] = {}
		
		if self.teamList[level].has_key( teamID ):
			playerMailbox.client.onStatusMessage( csstatus.TEAM_COMPETITION_FORBID_TEAM_JOIN_AGAIN,"" )
			return
		self.teamList[level][teamID] = {}
		self.teamList[level][teamID]["teamMailbox"] = teamMailbox
		self.teamList[level][teamID]["captainMailbox"] = playerMailbox
		teamMailbox.setMessage( csstatus.TEAM_COMPETITION_REQUEST_SUCCESS )
		teamMailbox.teamCompetitionNotify( level )
			
	def savePlayersInfo( self,playerName,playerMailbox,teamID,level ):
		"""
		defined method.
		
		@param playerName			: �������
		@type playerName			: STRING
		@param playerMailbox			: ���mailbox
		@type playerMailbox			: MAILBOX
		@param teamID			: ������ڶ���ID
		@type teamID			: OBJECT_ID
		
		���������ҵ���Ϣ
		"""
		if playerName not in self.joinPlayerInfo:
			self.joinPlayerInfo[ playerName ] = [ playerMailbox, teamID,level ]
	
	def onTeamDeregister( self,teamID ):
		"""
		defined method.
		
		�����ɢʱ֪ͨ��Ӿ�����������ɾ���Ķ���ļ�¼
		
		@param teamID:	��ɢ�����ID
		@type teamID:	OBJECT_ID
		
		"""
		for levelItem in self.teamList.values():
			if levelItem.has_key( teamID ):
				del levelItem[ teamID ]
		
	def setChampionBox( self,winnerTeamID ):
		"""
		define method.
		
		����ǰ�뿪��������ҷ��Źھ�����
		"""
		item = g_items.createDynamicItem( 60101245,1 )
		itemDatas = []
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		
		championList = []
		for e in self.joinPlayerInfo:
			if self.joinPlayerInfo[e][0].id in self.leavePlayerIDs and self.joinPlayerInfo[e][1] == winnerTeamID:
				championList.append( e )
				BigWorld.globalData["MailMgr"].send(None, e, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.SHARE_SYSTEM,cschannel_msgs.TEAMCOMPETITION_MAIL_CHAMPION_BOX_TITLE, "", 0, itemDatas)
		
		self.leavePlayerIDs = []
			
	def saveLeavePlayerInfo( self,playerID ):
		"""
		defined method.
		
		��¼�������뿪����ҵ�mailbox
		"""
		self.leavePlayerIDs.append( playerID )
	
	def recordPoint( self,playerDBID, matchType, scoreOrRound, playerBase = None):
		"""
		defined method
		
		��¼��һ���
		"""
		RoleMatchRecorder.update( playerDBID, matchType, scoreOrRound, playerBase )
