# -*- coding: gb18030 -*-
#
# $Id: Exp $


import time
import random
import math
import cPickle
import copy

import BigWorld
from bwdebug import *
from MsgLogger import g_logger
import csdefine
import csconst
import cschannel_msgs
import csstatus
import Love3
import RoleMatchRecorder
from Function import Functor
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from items import ItemDataList
g_items = ItemDataList.instance()

# ������״̬
WUDAO_STAGE_FREE		= 0			# ������
WUDAO_STAGE_NOTICE		= 1			# �㲥��
WUDAO_STAGE_SIGNUP		= 2			# ������
WUDAO_STAGE_UNDERWAY	= 3			# ������

# ʱ�� ( �Է���Ϊ��λ )
WUDAO_TIME_DISTANCE_NOTICE 		= 15	# �´ι㲥ʱ��
WUDAO_TIME_DISTANCE_SIGNUP		= 5		# �´α����㲥ʱ��

WUDAO_TIME_NOTICE = WUDAO_TIME_DISTANCE_NOTICE * 4	# �㲥ʱ��
WUDAO_TIME_SIGNUP = WUDAO_TIME_DISTANCE_SIGNUP * 3 	# ����ʱ��

# time userArg
WUDAO_USER_ARG_NOTICE		= 1 # �㲥׼������
WUDAO_USER_ARG_SIGNUP		= 2 # �㲥����
WUDAO_USER_ARG_CLOSE_ENTER	= 3 # �ر��볡��־
WUDAO_USER_ARG_OPEN_NEXT		= 4 # ��ʼ���ֱ���
WUDAO_USER_ARG_END			= 5 # �������
WUDAO_USER_ARG_Will_START    = 6	# ���1min��֪ͨ����������

WU_DAO_LAST_ROUND = int( math.ceil( math.log( csconst.WUDAO_MAX_NUM, 2 ) ) ) # ����������һ��

WU_DAO_JOIN_REWARD = 60101258

class WuDaoMgr( BigWorld.Base ):
	"""
	���������ģ��
	"""

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )

		self.currentStage = WUDAO_STAGE_FREE	 # ��ǰ������״̬
		self.currentRound = 0					 # ��ǰ�����ڼ���
		
		self.noticeWillSignUpNum = WUDAO_TIME_NOTICE / WUDAO_TIME_DISTANCE_NOTICE
		self.noticeSignUpNum = WUDAO_TIME_SIGNUP / WUDAO_TIME_DISTANCE_SIGNUP
		
		self.noticeWillSignUpTimeID = 0
		self.noticeSignUpTimeID = 0
		
		self.isCanEnter = False
		self.activityStartTime = 0
		
		self.joinActivityPlayers = []

		self.wuDaoDBIDDict = {}       # �����μ��������ɫdbid�ֵ�(���ݽ�ɫ�ȼ�����) such as { level/10 : [dbid,...],... }
		self.wuDaoWinnerDBIDDict = {} # ������ʤ��һ�� such as { level/10 : [dbid,...],... }
		self.playerToSpaceDict = {}   # ��ǰ�ִβμӱ������� such as { level/10 : {dbid : spaceKey,...},... }
		self.wuDaoNextRound = {}      # ��������һ�ִ� such as { level/10 : step }
		self.currentRoundStartTime = 0	  # ��ǰ�ִα�����ʼʱ��
		self.DBIDToBaseMailbox = {}	  # ���ݽ�ɫdbid�ҵ��������ɫ��baseMailbox

		self.hasEnterDBIDs = []		  # ��һ�ֱ����� ���Ѿ�����������

		self.sendMessageEnterWuDaoDBIDList = []	# ��Ҫ֪ͨ�����������ɫ��databaseID��list
		self.sendMessageEnterWuDaoTime = 0		# ֪ͨ������������ִ�
		
		self.currentEnterDict = {} # ��ǰ�ֿ��Խ������ң���Ҫ��Ϊ�˹رռ���ʹ��
		
		self.championList = []

		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.registerGlobally( "WuDaoMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register WuDaoMgr Fail!" )
			# again
			self.registerGlobally( "WuDaoMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["WuDaoMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("WuDaoMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"WuDaoMgr_start_notice" : "onStartNotice",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		if self.currentStage != WUDAO_STAGE_FREE:		# ����������ڽ����У��޷��ٴο���
			ERROR_MSG( "WuDaoMgr is progressing,cannot start again.GM Wait until last time end!" )
			return
		
		self.joinActivityPlayers = []
		self.currentStage = WUDAO_STAGE_NOTICE
		self.noticeWillStartSignUp()
		self.activityStartTime = time.time()
		INFO_MSG( "WuDaoMgr", "notice", "" )
	
	def onEndNotice( self ):
		"""
		define method.
		�����֪ͨ
		"""
		if self.currentStage == WUDAO_STAGE_FREE:
			return
		
		if self.currentStage == WUDAO_STAGE_UNDERWAY:
			self.end_wudao()
			return
		
		if self.currentStage == WUDAO_STAGE_NOTICE:
			self.delTimer( self.noticeWillSignUpTimeID )
			self.currentStage = WUDAO_STAGE_SIGNUP
			self.noticeSignUp()
			return
		
		if self.currentStage == WUDAO_STAGE_SIGNUP:
			self.delTimer( self.noticeSignUpTimeID )
		
		self.startNewRound()
		self.currentStage = WUDAO_STAGE_UNDERWAY
		INFO_MSG( "WuDaoMgr", "notice end", "" )
		
	def noticeWillStartSignUp( self ):
		# �㲥��ÿ��Կ�ʼ����
		if self.currentStage != WUDAO_STAGE_NOTICE:
			return
			
		if not self.noticeWillSignUpTimeID:
			self.noticeWillSignUpTimeID = self.addTimer( WUDAO_TIME_DISTANCE_NOTICE * 60, WUDAO_TIME_DISTANCE_NOTICE * 60, WUDAO_USER_ARG_NOTICE )
			
		if self.noticeWillSignUpNum > 0:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_WILL_SIGNUP_NOTIFY%( self.noticeWillSignUpNum * WUDAO_TIME_DISTANCE_NOTICE, ), [] )
			self.noticeWillSignUpNum -= 1
		else:
			self.delTimer( self.noticeWillSignUpTimeID )
			self.currentStage = WUDAO_STAGE_SIGNUP
			self.noticeSignUp()
	
	def noticeSignUp( self ):
		# �㲥����ʱ�仹�ж��
		if self.currentStage != WUDAO_STAGE_SIGNUP:
			return
			
		if not self.noticeSignUpTimeID:
			self.noticeSignUpTimeID = self.addTimer( WUDAO_TIME_DISTANCE_SIGNUP * 60, WUDAO_TIME_DISTANCE_SIGNUP * 60, WUDAO_USER_ARG_SIGNUP )
			
		if self.noticeSignUpNum > 0: 
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_START_SIGNUP_NOTIFY, [] )
			if self.noticeSignUpNum == 1:
				self.addTimer( ( WUDAO_TIME_DISTANCE_SIGNUP - 1 ) * 60, 0, WUDAO_USER_ARG_SIGNUP )
				
			self.noticeSignUpNum -= 1
		elif self.noticeSignUpNum == 0:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_START_SIGNUP_NOTIFY, [] )
			self.noticeSignUpNum -= 1
			self.addTimer( 60, 0, WUDAO_USER_ARG_SIGNUP )
		else:
			self.delTimer( self.noticeSignUpTimeID )
			if self.currentStage == WUDAO_STAGE_UNDERWAY:
				return
				
			if self.currentStage != WUDAO_STAGE_UNDERWAY:
				self.startNewRound()

	def startNewRound( self ):
		# �����µ�һ��
		if self.currentStage < WUDAO_STAGE_SIGNUP:
			# ��ֹʹ��GMָ�����
			return
		
		if self.currentRound < 0:
			return
			
		if self.currentRound == 0:
			self.currentStage = WUDAO_STAGE_UNDERWAY
			self.initWuDaoWar( copy.deepcopy( self.wuDaoDBIDDict ), self.currentRound + 1 )
			self.currentEnterDict = copy.deepcopy( self.wuDaoDBIDDict )
		else:
			self.currentEnterDict = copy.deepcopy( self.wuDaoWinnerDBIDDict )
			self.initWuDaoWar( self.wuDaoWinnerDBIDDict, self.currentRound + 1 )
		
		if self.currentRound == 0:
			return
		
		INFO_MSG( "WuDaoMgr", "round", str( self.currentRound ) )
		
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_WILL_BEGIN_NOTIFY%( self.currentRound, csconst.WUDAO_TIME_PREPARE ), [] )
		self.currentRoundStartTime = time.time()
		self.addTimer( csconst.WUDAO_TIME_PREPARE * 60, 0, WUDAO_USER_ARG_CLOSE_ENTER ) # ���׼����ʱ��
		if self.currentRound < math.log( csconst.WUDAO_MAX_NUM, 2 ):
			self.addTimer( csconst.WUDAO_TIME_ROUND * 60, 0, WUDAO_USER_ARG_OPEN_NEXT ) # ÿ�ֱ�����ʱ��
		else:
			self.addTimer( csconst.WUDAO_TIME_ROUND * 60, 0, WUDAO_USER_ARG_END ) # ÿ�ֱ�����ʱ��

	def closeEnterFlags( self ):
		# �رս�����־
		self.isCanEnter = False
		for dbids in self.currentEnterDict.values():
			for dbid in dbids:
				baseMailbox = self.DBIDToBaseMailbox.get( dbid )
				if baseMailbox:
					baseMailbox.cell.challengeRemoveFlagGather( csconst.TRANSMIT_TYPE_WUDAO )
					
				winnerList = []
				for ids in self.wuDaoWinnerDBIDDict.values():
					winnerList.extend( ids )
					
				if dbid not in self.hasEnterDBIDs and dbid not in winnerList and dbid not in self.championList: # ��������Ѿ�������б��ڣ��Ǿͱ�ʾ��û�н��볡��
					baseMailbox.client.onStatusMessage( csstatus.WU_DAO_NOT_IN_SPACE, "" )
		
	
	def updateDBIDToBaseMailbox( self, databaseID, baseMailbox ):
		"""
		����������DBIDToBaseMailbox
		"""
		if self.DBIDToBaseMailbox.has_key( databaseID ):
			self.DBIDToBaseMailbox[databaseID] = baseMailbox

	def delDBIDToBaseMailbox( self, databaseID ):
		"""
		��ɫ���ߺ�ɾ��DBIDToBaseMailbox
		"""
		if self.DBIDToBaseMailbox.has_key( databaseID ):
			self.DBIDToBaseMailbox[databaseID] = 0

	def onTimer( self, timerID, userArg ):
		"""
		ִ����������ز���
		"""
		if userArg == WUDAO_USER_ARG_NOTICE:
			self.noticeWillStartSignUp()
		elif userArg == WUDAO_USER_ARG_SIGNUP:
			self.noticeSignUp()
		elif userArg == WUDAO_USER_ARG_CLOSE_ENTER:
			self.closeEnterFlags()
		elif userArg == WUDAO_USER_ARG_OPEN_NEXT:
			self.startNewRound()
		elif userArg == WUDAO_USER_ARG_END:
			self.end_wudao()
		elif userArg == WUDAO_USER_ARG_Will_START:
			# ֪ͨ����������
			for e in self.sendMessageEnterWuDaoDBIDList:
				self.sendMessageEnterWuDao( e )
					
	def isSingUpFull( self, step ):
		"""
		�ж�������ĳ������������Ƿ���Ա
		"""
		return self.wuDaoDBIDDict.has_key( step ) and len( self.wuDaoDBIDDict[step] ) >= csconst.WUDAO_MAX_NUM

	def requestSignUp( self, level, playerBaseMailBox, playerDBID ):
		"""
		define method
		������
		"""
		step = level / 10 # ÿ10��Ϊһ������

		if self.currentStage == WUDAO_STAGE_SIGNUP:
			if self.wuDaoDBIDDict.has_key( step ) and playerDBID in self.wuDaoDBIDDict[step]:	# ����Ѿ�����
				playerBaseMailBox.client.onStatusMessage( csstatus.WU_DAO_SIGN_UP_ALREADY, "" )
				return
				
			if self.addToWuDao( step, playerBaseMailBox, playerDBID):
				playerBaseMailBox.client.onStatusMessage( csstatus.WU_DAO_SIGN_UP_SUCCE, "" )
				
				minLevel = step * 10
				maxLevel = minLevel + 9
				playerBaseMailBox.client.wuDaoUpLevel( maxLevel, minLevel )
			else:
				playerBaseMailBox.client.onStatusMessage( csstatus.WU_DAO_SIGN_UP_FULL, "" )
		else:
			playerBaseMailBox.client.onStatusMessage( csstatus.WU_DAO_SIGN_UP_TIME_ERR, "" )

	def addToWuDao( self, step, playerBaseMailBox, dbid ):
		"""
		�������������
		"""
		if self.isSingUpFull( step ):
			return False

		if self.wuDaoDBIDDict.has_key( step ):
			if not dbid in self.wuDaoDBIDDict[step]:
				index = random.randint( 0, len( self.wuDaoDBIDDict[step] ) )
				self.wuDaoDBIDDict[step].insert( index, dbid ) # �Ա���ѡ�ֽ����������
		else:
			self.wuDaoDBIDDict[step] = [dbid]

		self.DBIDToBaseMailbox[dbid] = playerBaseMailBox	# ���ݽ�ɫdbid��Ųμ��赸����ɫbaseMailbox
		return True

	def initWuDaoWar( self, dbidDict, time ):
		"""
		��ʼ���������������,timeΪ�ִΡ�
		"""
		self.isCanEnter  = True  # ����������������
		self.currentRound += 1 # ��ǰ�ִμ�1
		self.playerToSpaceDict.clear() # ����ǰ�ִβμӱ����������
		self.sendMessageEnterWuDaoDBIDList = []	# ��Ҫ֪ͨ�����������DBIDList���
		enterNextRound = {}		# ��ʤֱ�ӽ�����һ�ֵ�

		keys = dbidDict.keys()
		for key in keys:
			for dbid in dbidDict[key]:
				baseMailbox = self.DBIDToBaseMailbox.get( dbid )
				if baseMailbox:
					baseMailbox.client.wuDaoUpInfo( self.currentRound - 1 )
				
			length = len( dbidDict[key] )		# һ�������ж��ٸ�������
			if length == 2 :		# ���ֻ��2������
				self.wuDaoNextRound[key] = WU_DAO_LAST_ROUND 	# ������һ��Ϊ���һ��

			if length > 1 and length % 2 == 1:	# �������������ȡ���һ����ֱ�ӻ��ʤ��
				dbid = dbidDict[key][-1]
				del dbidDict[key][-1]
				length -= 1
				baseMailbox = self.DBIDToBaseMailbox.get( dbid )
				if baseMailbox :
					self.addWuDaoAward( self.currentRound, key, baseMailbox, 1 )
					baseMailbox.client.onStatusMessage( csstatus.WU_DAO_WITHOUT_ENEMY, "" )
				enterNextRound[key] = [dbid]

			teamCount = int( length / 2.0 + 0.5 )
			self.playerToSpaceDict[key] = {}
			for x in xrange( teamCount ):
				self.playerToSpaceDict[key][dbidDict[key][x*2]] = "WUDAO" + str(key*10000 + x)
				try:
					self.playerToSpaceDict[key][dbidDict[key][x*2 + 1]] = "WUDAO" + str(key*10000 + x)
				except:
					if length == 1:	# ���ֻ��һ����������ֱ�ӻ�ùھ�
						playerBaseMB = self.DBIDToBaseMailbox.get( dbidDict[key][0] )
						if playerBaseMB:
							playerBaseMB.cell.wuDaoNoticeChampion( key, self.activityStartTime + csconst.CHALLENGE_CHAMPION_REWARD_LIVING )
							self.championList.append( dbid )
						del dbidDict[key]

		# �����Ҫ֪ͨ�����������DBIDList
		for dbidList in dbidDict.itervalues():
			self.sendMessageEnterWuDaoDBIDList += dbidList

		# ֪ͨ����������
		if len( self.sendMessageEnterWuDaoDBIDList ) == 0:
			self.end_wudao()
			return
			
		for e in self.sendMessageEnterWuDaoDBIDList:
			self.sendMessageEnterWuDao( e, time )

		# ���1min���ٴ�֪ͨ����������
		self.addTimer( 60, 0, WUDAO_USER_ARG_Will_START )

		dbidDict.clear() # �������������
		self.wuDaoWinnerDBIDDict = enterNextRound	# ֱ�ӻ��ʤ����

	def end_wudao( self ):
		"""
		����������
		"""
		for dbid in  self.wuDaoDBIDDict:
			if self.DBIDToBaseMailbox.has_key( dbid ):
				self.DBIDToBaseMailbox[ dbid ].client.wuDaoClose()
				
		self.wuDaoDBIDDict = {}
		self.wuDaoWinnerDBIDDict = {}
		self.playerToSpaceDict = {}
		self.hasEnterDBIDs = []
		self.wuDaoNextRound = {}
		self.currentRoundStartTime = 0
		self.DBIDToBaseMailbox = {}

		self.currentStage = WUDAO_STAGE_FREE	 # ��ǰ������״̬
		self.currentRound = 0					 # ��ǰ�����ڼ���
		self.isCanEnter = False
		
		self.noticeWillSignUpNum = WUDAO_TIME_NOTICE / WUDAO_TIME_DISTANCE_NOTICE
		self.noticeSignUpNum = WUDAO_TIME_SIGNUP / WUDAO_TIME_DISTANCE_SIGNUP
		
		self.noticeWillSignUpTimeID = 0
		self.noticeSignUpTimeID = 0
		self.championList = []
		self.rewardJoin()
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.WU_DAO_DA_HUI_CLOSE_NOTIFY, [] )
		INFO_MSG( "WuDaoMgr", "end", "" )
	
	def rewardJoin( self ):
		# �����в�����Ҳ��뽱��
		mailMgr = BigWorld.globalData[ "MailMgr" ]
		item = g_items.createDynamicItem( WU_DAO_JOIN_REWARD )
		tempDict = item.addToDict()
		del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
		itemData = cPickle.dumps( tempDict, 0 )
		for inf in self.joinActivityPlayers:
			baseMailbox = inf[ 0 ]
			mailMgr.sendWithMailbox( 
				None, \
				baseMailbox, \
				inf[ 1 ], \
				csdefine.MAIL_TYPE_QUICK, \
				csdefine.MAIL_SENDER_TYPE_NPC, \
				cschannel_msgs.WU_DAO_DA_HUI_MAIL_SEND_NAME, \
				cschannel_msgs.WU_DAO_DA_HUI_MAIL_TITILE, \
				"", \
				0, \
				[ itemData,]\
			)

	def isWuDaoWinner( self, roleDBID ):
		"""
		�Ƿ��Ѿ���ʤ����
		"""
		for iList in self.wuDaoWinnerDBIDDict.itervalues():
			if roleDBID in iList:
				return True
			
		return False

	def isJoinWuDao( self, roleDBID ):
		"""
		��ɫ�Ƿ��ڵ�ǰ�ִβ����б���
		"""
		for iDict in self.playerToSpaceDict.itervalues():
			if roleDBID in iDict:
				return True
		return False

	def onEnterWuDaoSpace( self, domainBase, position, direction, playerBaseMB, params ):
		"""
		Define method.
		������������ḱ��

		@param domainBase : �ռ��Ӧ��domain��base mailbox
		@type domainBase : MAILBOX
		@param position : ����ռ�ĳ�ʼλ��
		@type position : VECTOR3
		@param direction : ����ռ�ĳ�ʼ����
		@type direction : VECTOR3
		@param playerBaseMB : ���base mailbox
		@type playerBaseMB : MAILBOX
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT
		"""
		roleDBID = params[ "roleDBID" ]			# ������븱����ҵ�dbid
		level = params['level']
		playerName = params['playerName']
		
		currentInList = self.currentEnterDict[ level/10 ] if self.currentEnterDict.has_key( level/10 ) else []
		if not self.isCanEnter or roleDBID not in currentInList:
			playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_NOT_OPEN_ENTER, "" )
			return
		
		if roleDBID in self.championList: # �Ѿ��ǹھ���
			playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_ALREADY_CHAMPION, "" )
			return

		if self.isWuDaoWinner( roleDBID ):					# ����Ѿ���ʤ�������
			playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_ALREADY_WIN, "" )
			return

		if not self.isJoinWuDao( roleDBID ):
			playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_NOT_JOIN, "" )
			return

		if roleDBID not in self.hasEnterDBIDs:
			self.hasEnterDBIDs.append( roleDBID ) # ���뵽�Ѿ����������б���

		if playerName not in [ inf[1] for inf in self.joinActivityPlayers ]:
			self.joinActivityPlayers.append( ( playerBaseMB, playerName ) )
			
		enterKeyDict = {'spaceKey': self.playerToSpaceDict[level/10][roleDBID] }
		domainBase.onEnterWuDaoSpace( position, direction, True, playerBaseMB, enterKeyDict )

	def onWuDaoOverFromSpace( self, playerBaseMB, databaseID, level, result ):
		"""
		Define method.
		����֪ͨһ������������

		@param databaseID : ��ɫ��dbid
		@type databaseID : DATABASE_ID
		"""
		for key in self.playerToSpaceDict:
			if self.playerToSpaceDict[key].has_key( databaseID ):
				del self.playerToSpaceDict[key][databaseID]

		self.hasEnterDBIDs.remove( databaseID ) # �����Ӹ����г���
		step = level/10
		if result: # ���Ϊ��ʤ��
			round = self.currentRound
			if self.wuDaoNextRound.has_key(step):
				round = WU_DAO_LAST_ROUND

			if round < WU_DAO_LAST_ROUND:
				if self.wuDaoWinnerDBIDDict.has_key( step ):
					index = random.randint( 0, len( self.wuDaoWinnerDBIDDict[step] ) )
					self.wuDaoWinnerDBIDDict[step].insert( index, databaseID ) # ��ѡ�ֽ����������
				else:
					self.wuDaoWinnerDBIDDict[step] = [databaseID]
				nextRoundTime = int( (csconst.WUDAO_TIME_ROUND * 60 + self.currentRoundStartTime - time.time())/60 )	# ֪ͨ��ʤ���μ���һ�ֱ���
				playerBaseMB.client.onStatusMessage( csstatus.WU_DAO_NEXT_ROUND_TIME, "(\'%s\',)" % nextRoundTime )
			
			self.addWuDaoAward( round, step, playerBaseMB, True )
			if round == WU_DAO_LAST_ROUND:
				playerBaseMB.cell.wuDaoNoticeChampion( step, self.activityStartTime + csconst.CHALLENGE_CHAMPION_REWARD_LIVING )
				self.championList.append( databaseID )
				RoleMatchRecorder.update( databaseID, csdefine.MATCH_TYPE_PERSON_ABA, 0, playerBaseMB ) #���û��Ϣ

		else: # ���Ϊʧ�ܷ�
			self.addWuDaoAward( self.currentRound, step, playerBaseMB, False )
			re = self.currentRound
			memNums = len( self.wuDaoDBIDDict[ step ] )
			re = int( math.ceil( math.log( memNums, 2 ) ) ) - self.currentRound
			RoleMatchRecorder.update( databaseID, csdefine.MATCH_TYPE_PERSON_ABA, re, playerBaseMB )#���û��Ϣ

	def addWuDaoAward( self, round, step, playerBaseMB, isWinner ):
		"""
		������Ӧ����

		@param round : �����ִ�
		@param playerBaseMB : ��ý�����ɫmail_box
		@param isWinner : �Ƿ�ʤ����
		@type isWinner : BOOL
		"""
		playerBaseMB.cell.wuDaoReward( round, step, isWinner )

# ����databaseIDѰ����Ӧ�Ľ�ɫ��֪ͨ��μ�������
	def sendMessageEnterWuDao( self, databaseID, time = 0 ):
		"""
		֪ͨ�ͻ��ˣ�Ҫ������������
		"""
		if time != 0:
			self.sendMessageEnterWuDaoTime = time

		playerBaseMB = self.DBIDToBaseMailbox.get( databaseID )
		if playerBaseMB:
			playerBaseMB.client.wuDaoGather( self.sendMessageEnterWuDaoTime )
			playerBaseMB.cell.challengeSetFlagGather( csconst.TRANSMIT_TYPE_WUDAO )
		#BigWorld.lookUpBaseByDBID( "Role", databaseID, Functor( self.sendMessageEnterWuDaoCB, self.sendMessageEnterWuDaoTime ) )

#	def sendMessageEnterWuDaoCB( self, time, callResult ):
		"""
		��ѯ�ص�����
		"""
#		if callResult != True and callResult != False:
#			callResult.client.receiveMessageEnterWuDao( time )

	def selectEnterWuDao( self, databaseID ):
		"""
		��ɫѡ����������ᣬ����Ҫ��֪ͨ��
		"""
		if databaseID in self.sendMessageEnterWuDaoDBIDList:
			self.sendMessageEnterWuDaoDBIDList.remove( databaseID )

#$Log:$
#
