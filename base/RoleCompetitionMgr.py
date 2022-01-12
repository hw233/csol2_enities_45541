# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs
import Love3
import time
import csstatus
import csconst
import random
import items
import Function
import cPickle
import ECBExtend
import RoleMatchRecorder
from CrondDatas import CrondDatas
g_items = items.instance()
g_CrondDatas = CrondDatas.instance()


ROLECOMPETITION_STATE_FREE			= 0		#������
ROLECOMPETITION_STATE_SIANUP		= 1		#������
ROLECOMPETITION_STATE_READY			= 2		#׼����
ROLECOMPETITION_STATE_ADMISSION		= 3		#�볡��
ROLECOMPETITION_STATE_END			= 4		#������
ROLECOMPETITION_ADMISSION1			= 5		#���˾�����ʼ�볡֪ͨ
ROLECOMPETITION_ADMISSION2			= 6		#���˾�����ʼ�볡֪ͨ
ROLECOMPETITION_ADMISSION3			= 7		#���˾�����ʼ�볡֪ͨ
ROLECOMPETITION_READY				= 8		#���˾�����ҳ�ȡ֪ͨ
ROLE_COMPETITION_SELECT				= 9		#�����ȡ���ʱ��
ROLECOMPETITION_TEST				= 10	#��GMָ��ɾ��������
ROLECOMPETITION_BEGIN_SINGUP		= [ 1, 2, 3, 4]
ROLECOMPETITION_BEGIN_SINGUP_TIME	= [ 55, 40, 25, 10, 5]	#���˾�������֪ͨʱ���
ROLECOMPETITION_ADMISSION1_TIME		= [ 5, 4, 3, 2, 1]		#���˾����볡֪ͨʱ���
NOTICE_TIMES2			= [ ( 4, 30), ( 3, 30), ( 2, 30), ( 1, 30)]
NOTICE_TIMES3			= [ 30]
REWARD_EXP_ITEM_ID = 60101248


class RoleCompetitionMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.hasSignUpNames = []		# ��һ�α����У��Ѿ��������������
		self.hasEnterNameDict = {}		#���������ֵ� such as {playerName��level}
		self.roleCompetitionNameDict = {}		# �����μӸ��˾�����ɫname�ֵ�(���ݽ�ɫ�ȼ�����) such as { level/10 : [playerName,...],... }
		self.hasSelectedNameDict = {}			# ѡ�вμӸ��˾�����ɫname�ֵ�(���ݽ�ɫ�ȼ�����) such as { level/10 : [playerName,...],... }
		self.DBIDToBaseMailbox = {}				# ���ݽ�ɫname�ҵ����˾�����ɫ��baseMailbox
		self.hasSelectedBaseMailbox = {}		# ��һ�α����б�ѡ�еĽ�ɫbaseMailbox�ֵ� such as { name:baseMailbox,...}
		self.nameToDBIDDict = {}				#���ݽ�ɫname�ҵ����˾�����ɫ��DBID
		self.currentStage = ROLECOMPETITION_STATE_FREE
		self.levelList = []
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "RoleCompetitionMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register RoleCompetitionMgr Fail!" )
			# again
			self.registerGlobally( "RoleCompetitionMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["RoleCompetitionMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("RoleCompetitionMgr Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"roleCompetition_start_notice" : "onStartNotice",
					  	"roleCompetition_Start" : "onStart",
						"roleCompetition_End" :	"onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		crond.addAutoStartScheme( "roleCompetition_Start", self, "onStart" )

	def onStart( self ):
		"""
		define method.
		�������ʼ
		"""
		if BigWorld.globalData.has_key( "AS_RoleCompetition" ) and BigWorld.globalData[ "AS_RoleCompetition" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "���˾�����������ڽ��У�%i��%i����ͼ�ٴο�ʼ���˾���������"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY, [] )
		BigWorld.globalData[ "AS_RoleCompetition" ] = True
		if BigWorld.globalData.has_key( "AS_RoleCompetitionAdmission" ):
			del BigWorld.globalData[ "AS_RoleCompetitionAdmission" ]
		if BigWorld.globalData.has_key( "RoleCompetitionStopSignUpTime" ):
			del BigWorld.globalData[ "RoleCompetitionStopSignUpTime" ]
		for playerMB in self.hasSelectedBaseMailbox.itervalues():
			playerMB.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_ROLE_COMPETITION )
		
		INFO_MSG( "RoleCompetitionMgr", "start", "" )
			

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_0 %ROLECOMPETITION_BEGIN_SINGUP_TIME[0]
		Love3.g_baseApp.anonymityBroadcast( temp, [] )
		BigWorld.globalData[ "AS_RoleCompetitionSignUp" ] = True
		self.addTimer( 15*60, 0, ROLECOMPETITION_BEGIN_SINGUP[0] )
		INFO_MSG( "RoleCompetitionMgr", "notice", "" )

	def onEnd( self ):
		"""
		define method.
		���������
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ROLECOMPETITION_END_NOTIFY, [] )
		if BigWorld.globalData.has_key( "AS_RoleCompetition" ):
			del BigWorld.globalData[ "AS_RoleCompetition" ]
		self.end_roleCompetition()
		INFO_MSG( "RoleCompetitionMgr", "end", "" )

	def onGMStartNotice( self ):
		"""
		define method.
		GM������֪ͨ
		"""
		if self.currentStage != ROLECOMPETITION_STATE_FREE:
			curTime = time.localtime()
			ERROR_MSG( "���˾�����������ڽ��У�%i��%i����ͼ�ٴο�ʼ���˾���������"%(curTime[3],curTime[4] ) )
			return
		self.hasSignUpNames = []
		self.roleCompetitionNameDict = {}
		self.hasSelectedNameDict = {}
		self.DBIDToBaseMailbox = {}
		self.hasSelectedBaseMailbox = {}
		self.hasEnterNameDict = {}
		temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_0 %ROLECOMPETITION_BEGIN_SINGUP_TIME[0]
		Love3.g_baseApp.anonymityBroadcast( temp, [] )
		BigWorld.globalData[ "AS_RoleCompetitionSignUp" ] = True
		self.currentStage = ROLECOMPETITION_STATE_SIANUP
	
	def onEndNotice( self ):
		"""
		��GMָ�����ʹ��
		"""
		if self.currentStage == ROLECOMPETITION_STATE_FREE:
			return
		
		if self.currentStage == ROLECOMPETITION_STATE_SIANUP:
			temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_2 
			Love3.g_baseApp.anonymityBroadcast( temp, [] )
			if BigWorld.globalData.has_key( "AS_RoleCompetitionSignUp" ):
				del BigWorld.globalData[ "AS_RoleCompetitionSignUp" ]
			BigWorld.globalData[ "AS_RoleCompetitionReady" ] = True
			self.addTimer( 2*60, 0, ROLECOMPETITION_ADMISSION1 )
			self.levelList = self.hasSelectedNameDict.keys()
			self.addTimer( 0, 0, ROLE_COMPETITION_SELECT)
			self.currentStage = ROLECOMPETITION_STATE_READY
			return
		
		if self.currentStage == ROLECOMPETITION_STATE_READY:
			return
			
		if self.currentStage == ROLECOMPETITION_STATE_ADMISSION:
			return
			
		if self.currentStage == ROLECOMPETITION_STATE_END:
			if BigWorld.globalData.has_key( "AS_RoleCompetitionAdmission" ):
				del BigWorld.globalData[ "AS_RoleCompetitionAdmission" ]
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ROLECOMPETITION_END_NOTIFY, [] )
			if BigWorld.globalData.has_key( "AS_RoleCompetition" ):
				del BigWorld.globalData[ "AS_RoleCompetition" ]
			self.end_roleCompetition()
			self.currentStage = ROLECOMPETITION_STATE_FREE
			return
		
		INFO_MSG( "RoleCompetitionMgr", "end notice", "" )

	def onTimer( self, timerID, userArg ):
		"""
		ִ�и��˾�����ز���
		"""
		if userArg in ROLECOMPETITION_BEGIN_SINGUP:
			temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_0 %ROLECOMPETITION_BEGIN_SINGUP_TIME[userArg]
			Love3.g_baseApp.anonymityBroadcast( temp, [] )
			if userArg < ROLECOMPETITION_BEGIN_SINGUP[2]:
				self.addTimer( 15*60, 0, userArg + 1 )
			elif userArg == ROLECOMPETITION_BEGIN_SINGUP[2]:
				self.addTimer( 5*60, 0, userArg + 1 )
			else:
				self.addTimer( 5*60, 0, ROLECOMPETITION_READY )

		elif userArg == ROLECOMPETITION_READY:
			temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_2 
			Love3.g_baseApp.anonymityBroadcast( temp, [] )
			if BigWorld.globalData.has_key( "AS_RoleCompetitionSignUp" ):
				del BigWorld.globalData[ "AS_RoleCompetitionSignUp" ]
			BigWorld.globalData[ "AS_RoleCompetitionReady" ] = True
			self.addTimer( 2*60, 0, ROLECOMPETITION_ADMISSION1 )
			self.levelList = self.hasSelectedNameDict.keys()
			self.addTimer( 0, 0, ROLE_COMPETITION_SELECT)			#�����ȡ�������
			
		elif userArg == ROLECOMPETITION_ADMISSION1:
			BigWorld.globalData[ "RoleCompetitionStopSignUpTime" ] = time.time()
			self.noticePlayer()
			temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_1 %ROLECOMPETITION_ADMISSION1_TIME[0]
			Love3.g_baseApp.anonymityBroadcast( temp, [] )
			self.sendMessageEnterRoleCompetition()
			self.addTimer( 60, 0, ROLECOMPETITION_ADMISSION2 )
			if BigWorld.globalData.has_key( "AS_RoleCompetitionReady" ):
				del BigWorld.globalData[ "AS_RoleCompetitionReady" ]
			BigWorld.globalData[ "AS_RoleCompetitionAdmission" ] = True 
			if self.currentStage == ROLECOMPETITION_STATE_READY:
				self.currentStage = ROLECOMPETITION_STATE_ADMISSION
			
		elif userArg == ROLECOMPETITION_ADMISSION2:
			t =  int (( time.time() - BigWorld.globalData[ "RoleCompetitionStopSignUpTime" ] )/60 + 0.5)
			temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_1 %ROLECOMPETITION_ADMISSION1_TIME[t]
			Love3.g_baseApp.anonymityBroadcast( temp, [] )
			if t < 4:
				self.addTimer( 60, 0, ROLECOMPETITION_ADMISSION2 )
			elif self.currentStage == ROLECOMPETITION_STATE_ADMISSION:
				self.addTimer( 60, 0, ROLECOMPETITION_TEST )
		
		elif userArg == ROLE_COMPETITION_SELECT:
			self.onTimer_roleCompetitionSelect()
			
		elif userArg == ROLECOMPETITION_TEST:
			for playerMB in self.hasSelectedBaseMailbox.itervalues():
				playerMB.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_ROLE_COMPETITION )
			if BigWorld.globalData.has_key( "AS_RoleCompetitionAdmission" ):
				del BigWorld.globalData[ "AS_RoleCompetitionAdmission" ]
			if BigWorld.globalData.has_key( "RoleCompetitionStopSignUpTime" ):
				del BigWorld.globalData[ "RoleCompetitionStopSignUpTime" ]
	
	def isSignUp( self, level, playerName):
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			step = (csconst.ROLE_LEVEL_UPPER_LIMIT - 1)/10
		else:
			step = level/10		# ÿ10��Ϊһ������
		if self.roleCompetitionNameDict.has_key(step) and playerName in self.roleCompetitionNameDict[step]:
			return True
		else:
			return False
	
	def requestSignUp( self, level, playerBaseMailBox, playerName ):
		"""
		define method
		������
		"""
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			step = (csconst.ROLE_LEVEL_UPPER_LIMIT - 1)/10
		else:
			step = level/10		# ÿ10��Ϊһ������
		if BigWorld.globalData.has_key("AS_RoleCompetitionSignUp"):
			if self.isSignUp( level, playerName):
				self.onReceiveSignUpFlag( playerBaseMailBox, True, True )
				return
			if self.addToRoleCompetition( step, playerBaseMailBox, playerName):
				self.onReceiveSignUpFlag( playerBaseMailBox, True, False )
		else:
			self.onReceiveSignUpFlag( playerBaseMailBox, False, False )
	
	def onReceiveSignUpFlag( self, playerBaseMailBox, allowToSignUp, hasSignUp ):
		"""
		�õ���������ظ�
		@param:		playerFull	(�����Ƿ���Ա)
		@type��		BOOL
		"""
		if allowToSignUp:
			if hasSignUp:
				playerBaseMailBox.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_1, "")
			else:
				playerBaseMailBox.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_2, "")
			return
		else:
			playerBaseMailBox.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_3, "")
				
	def addToRoleCompetition( self, step, playerBaseMailBox, playerName):
		"""
		���������˾���
		"""
		if self.roleCompetitionNameDict.has_key( step ):
			if not playerName in self.roleCompetitionNameDict[step]:
				self.roleCompetitionNameDict[step].append( playerName)
				self.hasSelectedNameDict[step].append(playerName)
		else:
			self.roleCompetitionNameDict[step] = [playerName]
			self.hasSelectedNameDict[step] = [playerName]
		self.DBIDToBaseMailbox[playerName] = playerBaseMailBox
		playerBaseMailBox.client.roleCompetition_SignUp( step )
		return True
		
	def callbackRandomSelect( self, name, step, baseMailbox):
		"""
		��ȡ��ҵ�MAILBOX�Ļص�
		"""
		if baseMailbox:
			self.hasSelectedBaseMailbox[name] = baseMailbox
		else:
			if self.hasSelectedNameDict[step] == []:
				return
			index = random.randint( 0, len(self.hasSelectedNameDict[step])-1 )
			name = self.hasSelectedNameDict[step][index]
			self.hasSelectedNameDict[step].remove(name)
			Love3.g_baseApp.lookupRoleBaseByName( name, Function.Functor( self.callbackRandomSelect, name, step ) )
			
	
	def randomSelect( self, level ):
		"""
		�����ȡ���
		"""
		if len(self.hasSelectedNameDict[level]) <= csconst.ROLECOMPETITION_MAX_NUM:
			for j in self.hasSelectedNameDict[level]:
				self.hasSelectedBaseMailbox[j] = self.DBIDToBaseMailbox[j]
		else:
			for j in xrange(csconst.ROLECOMPETITION_MAX_NUM):
				if self.hasSelectedNameDict[level] == []:
					break
				index = random.randint( 0, len(self.hasSelectedNameDict[level])-1 )
				name = self.hasSelectedNameDict[level][index]
				self.hasSelectedNameDict[level].remove(name)
				Love3.g_baseApp.lookupRoleBaseByName( name, Function.Functor( self.callbackRandomSelect, name, level ) )
	
	def onTimer_roleCompetitionSelect( self ):
		"""
		��ʱ���������������
		"""
		if self.levelList == []:
			return
		else:
			level = self.levelList.pop(0)
			self.randomSelect( level )
			self.addTimer( 3, 0, ROLE_COMPETITION_SELECT)
		

	def noticePlayer( self ):
		"""
		֪ͨ����ȡ�����
		"""
		for i in self.roleCompetitionNameDict.iterkeys():
			for j in self.roleCompetitionNameDict[i]:
				playerBaseMB = self.DBIDToBaseMailbox[j]
				if self.hasSelectedBaseMailbox.has_key(j):
					playerBaseMB.client.onStatusMessage( csstatus.ROLE_COMPETITION_BESELECTED, "")
					playerBaseMB.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_ROLE_COMPETITION )
				else:
					playerBaseMB.client.onStatusMessage( csstatus.ROLE_COMPETITION_NOT_BESELECTED, "")
		
	def end_roleCompetition( self ):
		"""
		����ʱ�Ĳ���
		"""
		self.hasSignUpNames = []
		for i in self.roleCompetitionNameDict.iterkeys():
			for j in self.roleCompetitionNameDict[i]:
				playerBaseMB = self.DBIDToBaseMailbox[j]
				playerBaseMB.client.onRoleCompetitionEnd()
		self.roleCompetitionNameDict = {}		
		self.hasSelectedNameDict = {}			
		self.DBIDToBaseMailbox = {}				
		self.hasSelectedBaseMailbox = {}		
		for i,j in self.hasEnterNameDict.items():
			self.addRoleCompetitionReward( i, j )
		temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_3
		Love3.g_baseApp.anonymityBroadcast( temp, [] )
		self.hasEnterNameDict = {}
	
	def onEnterRoleCompetitionSpace( self, playerBaseMB, playerName, mapName, position, direction , level, roleDBID ):
		"""
		��ҽ��븱��֮ǰ�Ĳ�������������������븱��
		"""
		if BigWorld.globalData.has_key("AS_RoleCompetitionAdmission"):
			if self.hasSelectedBaseMailbox.has_key(playerName):
				playerBaseMB.cell.gotoSpace( mapName, position, direction )
				self.hasEnterNameDict[playerName] = level
			else:
				playerBaseMB.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_5, "")

	def addRoleCompetitionReward( self, playerName, level):
		"""
		ͨ���ʼ���ʽ����ҷ��Ͳ��뽱��
			���뽱������ֵ=1404*��25+5*��ɫ�ȼ�^1.2��
		"""

		itemDatas = []
		item = g_items.createDynamicItem( REWARD_EXP_ITEM_ID )
		#�ı���Ʒ�ľ���ֵ
		#pass
		if item:
			item.setLevel( level )
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )

		# ���ż������ʼ�������
		BigWorld.globalData["MailMgr"].send(None, playerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", cschannel_msgs.FCWR_MAIL_ROLECOMPETITION_REWARD_TITLE, "", 0, itemDatas)
		
	def roleCompetition_Record( self, playerDBID, matchType, scoreOrRound, playerBase ):
		"""
		��¼һ�α�����Ϣ
		"""
		RoleMatchRecorder.update( playerDBID, matchType, scoreOrRound, playerBase )
		
	def roleCompetition_end( self, notice):
		"""
		��GMָ�����������
		"""
		if notice != "":
			Love3.g_baseApp.anonymityBroadcast( notice, [] )
		for playerMB in self.hasSelectedBaseMailbox.itervalues():
			playerMB.client.roleCompetitionOver()
		if self.currentStage == ROLECOMPETITION_STATE_ADMISSION:
			self.currentStage = ROLECOMPETITION_STATE_END
			
	def sendMessageEnterRoleCompetition( self ):
		for playerMB in self.hasSelectedBaseMailbox.itervalues():
			playerMB.client.roleCompetitionGather()