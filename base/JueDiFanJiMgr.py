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
from operator import itemgetter, attrgetter
g_items = items.instance()
g_CrondDatas = CrondDatas.instance()


LEFT_SEAT = 0			#ƥ��ĵ�һ��Ԫ��
RIGHT_SEAT = 1			#ƥ��ĵڶ���Ԫ��
CAN_MATCH_NUM = 2		#�ܹ�ƥ�����С����
MATCH_NUM = 2			#ƥ��ĵ�����Ԫ�أ���ʾƥ������֣�


VICTORY_SCORE_NUM			= 2			#ʤһ��������
DRAW_SCORE_NUM				= 1			#ƽһ��������

MAX_SCORE_NUM				= 10		#��������

LENGTH_OF_PLAYER_1			= 2
LENGTH_OF_PLAYER_2			= 3


REWARD_EXP_ITEM_ID = 60101282	#������ƷID
VICTORY_MONEY		= 3			#ʤ����Ǯ����
DRAW_MONEY			= 2			#ƽ�ֽ�Ǯ����
FAILED_MONEY		= 1			#ʧ�ܽ�Ǯ����
FIRST_THIRD_RANK_NUM = 3		#ǰ����

INTERFACE_CLOSE_TIME = 300.0	#����ر�ʱ�䣨5���ӣ�
INTERFACE_CLOSE_TIMER = 20003	#����ر�timer
JUE_DI_FAN_JI_SPACENAME = "fu_ben_jue_di_fan_ji"

class JueDiFanJiMember:
	"""
	���ط������Ա
	"""
	def __init__( self, level, dbid ):
		self.level = level
		self.dbid = dbid

	def __repr__( self ):
		return repr( ( self.level, self.dbid ) )
		
	def getLevel( self ):
		return self.level
	
	def getDBID( self ):
		return self.dbid

class JueDiFanJiMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# ���Լ�ע��ΪglobalDataȫ��ʵ��
		self.jueDiFanJiQueue = []							#���ط����ŶӶ���
		self.jueDiFanJiScoreDict = {}						#���ط��������ֵ䣬����{dbid1:[playerName1, score1, victoryNum1 ],dbid2:[playerName2, score2, victoryNum2 ],...}(����victoryNum1Ϊ��ʤ����score1Ϊ����)
		self.jueDiFanJiDBIDToPlayerInfo = {}				#���ط���DBID��Ӧ��player��Ϣ�ֵ䣬����{dbid1:[playerMB1,playerName1,level1,playerClass1],dbid2:[playerMB2,playerName2,level2,playerClass2]}
		self.jueDiFanJiVictoryCountDict = {}				#���ط�����ʤ������¼�ֵ�
		self.jueDiFanJiStateDict = {}						#���ط���ÿ�����״̬�ֵ�
		self.jueDiFanJiMatchList = []						#���ط���ƥ���б�����[(dbid1,dbid2,ƥ������),(dbid3,dbid4,ƥ������),...](����dbid1��dbid2�Ƕ�ս˫����ƥ������ָ�������Ƕ��ٴ�ƥ��)
		self.jueDiFanJiMatchedDBIDToIndex = {}				#���ط����Ѿ�ƥ���DBID��Ӧ��Index�ֵ䣬����{dbid1:index1,dbid2:index1,dbid3:index2,dbid4:index2,...}
		self.jueDiFanJiEmptyIndexList = []					#���ط����յ�λ������
		self.curMaxMatchCount = 0							#Ŀǰ�Ѿ�ƥ��ɹ����������
		self.requestCount = 0								#�����������
		self.operateCount = 0								#���ڲ���������
		self.jueDiFanJiDBIDToOnlineDict = {}				#���ط���DBID��Ӧ����Ƿ������ֵ�,����{123:1,234:0,...}������������1��ʾ����������0��ʾ��
		self.jueDiFanJiTimerID = 0							#���ط����Timer
		self.jueDiFanJiFirstThirdRank = []					#���ط���ǰ������Ϣ��������Ҫ����սȺ���б�����ʱ���ܹ�ȡ����������Ҫ���浽��һ�λ����ǰ
		self.jueDiFanJiTempHPDict = {}						#���ط������ʱѪ����¼,����{dbid1:HP1,dbid2:HP2,...}
		self.registerGlobally( "JueDiFanJiMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		ע��ȫ��Base�Ļص�������
		@param complete:	��ɱ�־
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register JueDiFanJiMgr Fail!" )
			# again
			self.registerGlobally( "JueDiFanJiMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["JueDiFanJiMgr"] = self		# ע�ᵽ���еķ�������
			INFO_MSG("JueDiFanJiMgr Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"jueDiFanJi_Start_Notice" : "onStartNotice",
					  	"jueDiFanJi_Start" : "onStart",
						"jueDiFanJi_End" :	"onEnd",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
		crond.addAutoStartScheme( "jueDiFanJi_Start", self, "onStart" )

	def onStart( self ):
		"""
		define method.
		�������ʼ
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "���ط�������ڽ��У�%i��%i����ͼ�ٴο�ʼ���ط������"%(curTime[3],curTime[4] ) )
			return
		for playerInfo in self.jueDiFanJiDBIDToPlayerInfo.itervalues():
				playerMB = playerInfo[ 0 ]
				playerMB.cell.removeBulletin()
		if self.jueDiFanJiTimerID:
			self.delTimer( self.jueDiFanJiTimerID )
			self.jueDiFanJiTimerID = 0
		self.resetJueDiFanJiData()
		self.jueDiFanJiFirstThirdRank = []
		INFO_MSG( "jueDiFanJi onStart: resetJueDiFanJiData!!!" )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JUE_DI_FAN_JI_BEGIN, [] )
		BigWorld.globalData[ "AS_JueDiFanJiStart" ] = True
		Love3.g_baseApp.globalRemoteCallClient( "jueDiFanJiStart" )

	def onStartNotice( self ):
		"""
		define method.
		���ʼ֪ͨ
		"""
		pass

	def onEnd( self ):
		"""
		define method.
		���������
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ):
			del BigWorld.globalData[ "AS_JueDiFanJiStart" ]
		self.calJueDiFanJiRankAndNotice()
		self.jueDiFanJiTimerID = self.addTimer( INTERFACE_CLOSE_TIME, 0, INTERFACE_CLOSE_TIMER)
		
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == INTERFACE_CLOSE_TIMER:
			Love3.g_baseApp.globalRemoteCallClient( "jueDiFanJiEnd" )
			for playerInfo in self.jueDiFanJiDBIDToPlayerInfo.itervalues():
				playerMB = playerInfo[ 0 ]
				playerMB.cell.removeBulletin()
			self.resetJueDiFanJiData()
			self.jueDiFanJiTimerID = 0
			INFO_MSG( "jueDiFanJi onTimer: resetJueDiFanJiData!!!" )
		
	def onJueDiFanJiSignUp( self, playerMB, dbid, playerName, level, playerClass ):
		"""
		���ط�������
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ]:
			self.jueDiFanJiDBIDToPlayerInfo[ dbid ] = [ playerMB, playerName, level, playerClass ]
			self.jueDiFanJiDBIDToOnlineDict[ dbid ] = 1
			#�ı�״̬���������ڵ�״̬���ͻ���
			self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
			self.pushJueDiFanJiQueue( dbid, level )
			
	def assignJueDiFanJiMatcher( self ):
		"""
		������ط�����ƥ�����
		"""
		if len( self.jueDiFanJiQueue ) >= CAN_MATCH_NUM and BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ] == True:
			if self.operateCount != 0:
				return
			else:
				self.operateCount = 1
				self.sortJueDiFanJiQueue()			#�Ծ��ط�������н�������
				playerA = self.jueDiFanJiQueue.pop( 0 ).getDBID()
				playerB = self.jueDiFanJiQueue.pop( 0 ).getDBID()
				self.clearJueDiFanJiMatcher( playerA )
				self.clearJueDiFanJiMatcher( playerB )
				self.curMaxMatchCount += 1
				if self.jueDiFanJiEmptyIndexList:
					indexOfMatch = self.jueDiFanJiEmptyIndexList[ 0 ]
					self.jueDiFanJiMatchList[ indexOfMatch ] = [ playerA, playerB, self.curMaxMatchCount ]
					self.jueDiFanJiMatchedDBIDToIndex[ playerA ] = ( indexOfMatch, LEFT_SEAT )
					self.jueDiFanJiMatchedDBIDToIndex[ playerB ] = ( indexOfMatch, RIGHT_SEAT )
					DEBUG_MSG( "jueDiFanJi : match success, playerA is %s, playerB is %s, indexOfMatch is %s"%( playerA, playerB, indexOfMatch ) )
				else:
					self.jueDiFanJiMatchList.append( [ playerA, playerB, self.curMaxMatchCount ] )
					indexOfMatch = len( self.jueDiFanJiMatchList ) - 1
					self.jueDiFanJiMatchedDBIDToIndex[ playerA ] = ( indexOfMatch, LEFT_SEAT )
					self.jueDiFanJiMatchedDBIDToIndex[ playerB ] = ( indexOfMatch, RIGHT_SEAT )
					DEBUG_MSG( "jueDiFanJi : new match success, playerA is %s, playerB is %s, indexOfMatch is %s"%( playerA, playerB, indexOfMatch ) )
				#�ı�״̬���������ڵ�״̬���ͻ���
				self.changeStateDict( playerA, csdefine.JUE_DI_FAN_JI_HAS_MATCHED )
				self.changeStateDict( playerB, csdefine.JUE_DI_FAN_JI_HAS_MATCHED )
				self.requestCount -= 1
				self.operateCount = 0
				if self.requestCount > 0:
					#��Ϊ���첽������Ӧ��ɾ���ȴ����м���ƥ����飬������Ҫ�ȵ���һ�β�����ɺ��ٽ�����һ�β���
					self.assignJueDiFanJiMatcher()
			
			
	def clearJueDiFanJiMatcher( self, dbid ):
		"""
		������ߡ�û��ȷ�Ͻ��������µ�ƥ���������
		"""
		if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
			outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
			self.jueDiFanJiMatchList[ outerIndex ][ innerIndex ] = 0
			if ( innerIndex == LEFT_SEAT and self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ] == 0 ) or ( innerIndex == RIGHT_SEAT and self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ] == 0 ):
				self.jueDiFanJiEmptyIndexList.append( outerIndex )
			del self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
			
	def sendStateInfo( self, dbid, state ):
		"""
		����״̬��Ϣ
		"""
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
			playerMB = self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 0 ]
			if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
				playerMB.cell.onReceiveStateInfo( state, self.jueDiFanJiVictoryCountDict[ dbid ][ 0 ] )
			else:
				playerMB.cell.onReceiveStateInfo( state, 0 )
			if state == csdefine.JUE_DI_FAN_JI_HAS_MATCHED:
				#ͬʱ����Ӧ����ҵ�cell��һ��timer��25s�Ժ�ص�
				playerMB.cell.noticeAddTimer( csconst.JUE_DI_FAN_JI_WAIT_TIME )
	
	def onJueDiFanJiEnterConfirm( self, playerMB, dbid ):
		"""
		���ط�������ȷ��
		"""
		if BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ]:
			if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
				outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
				if innerIndex == LEFT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
				elif innerIndex == RIGHT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
				DEBUG_MSG( "dbid is %s, matchDBID is %s"%( dbid, matchDBID ) )
				if not matchDBID:
					self.clearJueDiFanJiMatcher( dbid )		#���Ϊ0��˵���Է��Ѿ�ƥ�䣬��ʱ���Լ�ҲӦ�ñ������ƥ���б�
					self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
					if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
						self.pushJueDiFanJiQueue( dbid, self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 2 ] )
				else:
					if self.jueDiFanJiStateDict[ matchDBID ] == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
					#������Ӧ�ĸ���������Ҵ��ͽ�ȥ(�����ʱ����һ����Ҳ������ˣ���ô�Ͳ�����)
					#���ǵ��첽�����⣬�ȸı�״̬�ٴ���
						if self.isOnlineOrNot( matchDBID ) and self.isOnlineOrNot( dbid ) and self.jueDiFanJiDBIDToPlayerInfo.has_key( matchDBID ):
							self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_ENTERED )
							self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_HAS_ENTERED )
							matchPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ matchDBID ][ 0 ]
							playerMB.cell.gotoSpace( JUE_DI_FAN_JI_SPACENAME, ( 0, 0, 0 ), ( 0, 0, 0 ) )
							matchPlayerMB.cell.gotoSpace( JUE_DI_FAN_JI_SPACENAME, ( 0, 0, 0), ( 0, 0, 0 ) )
							#��ҽ���֮��ȡ����ҵ�timer
							playerMB.cell.jueDiFanJiCanCelTimer()
							matchPlayerMB.cell.jueDiFanJiCanCelTimer()
					else:
						self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER )
	
	def onJueDiFanJiCancelEnter( self, playerMB, dbid ):
		"""
		���ط����������ȡ������
		"""
		#��Ҫȡ����Ӧ��ƥ����У����������������Ŷӣ�������ȡ������ҵ�״̬�����Ҫ���±�����״̬
		if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
			outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
			if innerIndex == LEFT_SEAT:
				matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
			elif innerIndex == RIGHT_SEAT:
				matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
			self.clearJueDiFanJiMatcher( dbid )		#���Լ������ƥ�����
			self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
			DEBUG_MSG( "CancelEnter: dbid is %s, matchDBID is %s"%( dbid, matchDBID ) )
			if matchDBID:				#���ƥ���dbid��Ϊ0��˵��û������ƥ�䣩,��ô����Ҫ���Է���������ƥ���¼��������߾����¼����ŶӶ�����
				self.clearJueDiFanJiMatcher( matchDBID )
				if self.isOnlineOrNot( matchDBID ) and self.jueDiFanJiDBIDToPlayerInfo.has_key( matchDBID ):
					self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
					self.pushJueDiFanJiQueue( matchDBID, self.jueDiFanJiDBIDToPlayerInfo[ matchDBID ][ 2 ] )
				else:
					self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
	
	def pushJueDiFanJiQueue( self, dbid, level ):
		"""
		��һ����Ҽ�����е�ͬʱ�ж��Ƿ���������ƥ�䣬�����������Ӧ��ƥ��
		"""
		flag = False
		for member in self.jueDiFanJiQueue:
			if member.getDBID() == dbid:
				flag = True
				break
		if not flag:
			self.jueDiFanJiQueue.append( JueDiFanJiMember( level, dbid ) )
		#if dbid not in self.jueDiFanJiQueue:
			#self.jueDiFanJiQueue.append( dbid )
		if len( self.jueDiFanJiQueue ) >= CAN_MATCH_NUM and BigWorld.globalData.has_key( "AS_JueDiFanJiStart" ) and BigWorld.globalData[ "AS_JueDiFanJiStart" ] == True:
			self.requestJueDiFanJiMatch()
	
	def sortJueDiFanJiQueue( self ):
		"""
		���ط������������
		"""
		self.jueDiFanJiQueue = sorted( self.jueDiFanJiQueue, key = attrgetter('level'), reverse=True )
	
	def requestJueDiFanJiMatch( self ):
		"""
		������ط���ƥ��
		"""
		self.requestCount += 1
		if self.operateCount == 0:
			self.assignJueDiFanJiMatcher()
	
	
	def changeStateDict( self, dbid, state ):
		"""
		�ı�״̬�б�ͬʱ֪ͨ�ͻ���״̬�ı�
		"""
		DEBUG_MSG( "jueDiFanJi : player state change, dbid is %s, state is %s"%( dbid, state ) )
		if state == csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP:
			if self.jueDiFanJiStateDict.has_key( dbid ):
				del self.jueDiFanJiStateDict[ dbid ]
		else:
			self.jueDiFanJiStateDict[ dbid ] = state
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
			self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 0 ].setJueDiFanJiState( state )
			self.sendStateInfo( dbid, state )
	
	def isOnlineOrNot( self, dbid ):
		"""
		����Ƿ����ߵ��жϣ�����ұ���������֮ǰ����Ϊ�������
		"""
		if self.jueDiFanJiDBIDToOnlineDict.has_key( dbid ) and self.jueDiFanJiDBIDToOnlineDict[ dbid ]:
			return True
		else:
			return False
	
	def onJueDiFanJiReachTimeConfirm( self, dbid ):
		"""
		���ط����ȷ��ʱ�䵽��ص�
		"""
		if self.jueDiFanJiStateDict.has_key( dbid ) and self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ) and self.jueDiFanJiStateDict[ dbid ] == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
			if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
				outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
				if innerIndex == LEFT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
				elif innerIndex == RIGHT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
				DEBUG_MSG( "dbid is %s, state is %s, matchDBID is %s"%( dbid, self.jueDiFanJiStateDict[ dbid ], matchDBID ) )
				if  not matchDBID:
					self.clearJueDiFanJiMatcher( dbid )		#���Ϊ0��˵���Է��Ѿ�ƥ�䣬��ʱ���Լ�ҲӦ�ñ������ƥ���б�
					self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
					if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
						self.pushJueDiFanJiQueue( dbid, self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 2 ] )
				else:
					#�����߲�������ƥ���״̬�£����˵����Ҳ������ߺ��ٴα�������������ߺ��ٴα������ٽ���ƥ����У���ômatchDBIDΪ0��������ߺ�����û�н���ƥ����У���ô״̬�Ͳ���Ϊƥ��״̬��
					#��������������߻�����˼�ǻ�û�н���֮ǰ�������ҵ��߾����±�����������븱��֮��״̬Ϊ�Ѿ����룬��ô��ҿ�������Ӧ��ʱ��������
					#�����ߵ�����£���һ����ȵ���onJueDiFanJiEnterConfirm����Ϊֻ�����������˽���ȷ��״̬�����ʱ�䵽���ʱ�����˫��״̬��Ϊ����ȷ��״̬����ô��Ӧ�ø��Դ����Լ������������ᵼ��״̬���ң�
					#�Է����ߵ������û�н��д���Է����������Ϊ�Է���һ��Լ���һ��timer�ص����Լ������Լ���������С�
					if not self.isOnlineOrNot( matchDBID ) and self.jueDiFanJiStateDict[ matchDBID ] == csdefine.JUE_DI_FAN_JI_HAS_MATCHED:
						self.clearJueDiFanJiMatcher( matchDBID )					#Ҫ��һ������Ϊ������ҵ����ˣ�����û���ٴ����ߣ���ô���ƥ���¼��һֱ������������Ҿ���û���ߣ���������£�Ҳ��Ҫ����������±���
						self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
						#del self.jueDiFanJiStateDict[ matchDBID ]
						#�Է������ߣ��Լ�Ӧ�ñ������ƥ���б�,���¼���ƥ�����
						self.clearJueDiFanJiMatcher( dbid )
						self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
						if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
							self.pushJueDiFanJiQueue( dbid, self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 2 ] )
		elif self.jueDiFanJiStateDict.has_key( dbid ) and self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ) and self.jueDiFanJiStateDict[ dbid ] != csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
			if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
				outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
				if innerIndex == LEFT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
				elif innerIndex == RIGHT_SEAT:
					matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
				DEBUG_MSG( "dbid is %s, state is %s, matchDBID is %s"%( dbid, self.jueDiFanJiStateDict[ dbid ], matchDBID ) )
				self.clearJueDiFanJiMatcher( dbid )
				self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
				if matchDBID:
					if not self.isOnlineOrNot( matchDBID ):							#�Է������ߵ�����£����Է������ƥ���б����������Ҫ���±���
						self.clearJueDiFanJiMatcher( matchDBID )
						self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
					elif self.isOnlineOrNot( matchDBID ) and self.jueDiFanJiMatchedDBIDToIndex.has_key( matchDBID ) and self.jueDiFanJiStateDict[ matchDBID ] == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:
						#���ｫ�Ѿ�ƥ�������ٴμ��뱨���б���Ϊ�˷�ֹ�Ѿ�ƥ�䲢��ȷ�Ͻ�������1���ȵ�����onJueDiFanJiReachTimeConfirm������Ȼ����ʱ��
						#����ƥ������2������ƥ�䵫��δȷ�Ͻ���״̬���Ӷ����²������������1��״̬�ı䣬���������1һֱ���ǵȴ��Է�ȷ��״̬����Ҫ����ȡ��
						#���������2����onJueDiFanJiReachTimeConfirm������ʱ�򣬳��˽��Լ���״̬�������⣬ͬʱ����Է�״̬����ȷ�Ͻ���״̬�����Ϊ�ѱ�����״̬
						self.clearJueDiFanJiMatcher( matchDBID )
						self.changeStateDict( matchDBID, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
						if self.jueDiFanJiDBIDToPlayerInfo.has_key( matchDBID ):
							self.pushJueDiFanJiQueue( matchDBID, self.jueDiFanJiDBIDToPlayerInfo[ matchDBID ][ 2 ] )
		
	def onEnterJueDiFanJiSpace( self, domainBase, baseMailbox, params ):
		"""
		���������ط��������
		"""
		isLogin = params.has_key( "login" )
		dbid = params[ "dbID" ]
		if not self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
			if isLogin:
				baseMailbox.logonSpaceInSpaceCopy()
			return
		outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
		if innerIndex == LEFT_SEAT:
			params[ "left" ] = dbid
			params[ "right" ] = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
		elif innerIndex == RIGHT_SEAT:
			params[ "left" ] = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
			params[ "right" ] = dbid
		params[ "spaceKey" ] = "JueDiFanJi_" + str( self.jueDiFanJiMatchList[ outerIndex ][ MATCH_NUM ] )
		if self.jueDiFanJiMatchedDBIDToIndex.has_key( dbid ):
			outerIndex,innerIndex = self.jueDiFanJiMatchedDBIDToIndex[ dbid ]
			if innerIndex == LEFT_SEAT:
				matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ RIGHT_SEAT ]
			elif innerIndex == RIGHT_SEAT:
				matchDBID = self.jueDiFanJiMatchList[ outerIndex ][ LEFT_SEAT ]
		if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
			params[ "playerHP" ] = self.jueDiFanJiVictoryCountDict[ dbid ][ 1 ]
			params[ "playerHPToDBID" ] = dbid
		elif self.jueDiFanJiVictoryCountDict.has_key( matchDBID ):
			params[ "playerHP" ] = self.jueDiFanJiVictoryCountDict[ matchDBID ][ 1 ]
			params[ "playerHPToDBID" ] = matchDBID
		domainBase.onEnterSpace( baseMailbox, params )
		if isLogin:
			self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 0 ] = baseMailbox
			#֪ͨ�ͻ���������ڵ�״̬
			self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_ENTERED )
		
	def onAddJueDiFanJiScore( self, victoryDBID, failedDBID, status, hp ):
		"""
		define method
		���ط�������ӻ���
		"""
		victoryName = ""
		failedName = ""
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( victoryDBID ):
			victoryName = self.jueDiFanJiDBIDToPlayerInfo[ victoryDBID ][ 1 ]
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( failedDBID ):
			failedName = self.jueDiFanJiDBIDToPlayerInfo[ failedDBID ][ 1 ]
		if status == csdefine.JUE_DI_FAN_JI_VICTORY_STATUS:				#ʤ����
			if self.jueDiFanJiVictoryCountDict.has_key( victoryDBID ):
				score = 2 * (self.jueDiFanJiVictoryCountDict[ victoryDBID ][ 0 ] + 1)				#�������ʤ����ô����Ϊ2*�� ��ʤ�� + 1 ��
				if score > MAX_SCORE_NUM:
					score = MAX_SCORE_NUM
			else:
				score = VICTORY_SCORE_NUM
			if not self.jueDiFanJiScoreDict.has_key( victoryDBID ):
					self.jueDiFanJiScoreDict[ victoryDBID ] = [ victoryName, score, 1 ]
			else:
				victoryNum = self.jueDiFanJiScoreDict[ victoryDBID ][ 2 ] + 1
				newScore = self.jueDiFanJiScoreDict[ victoryDBID ][ 1 ] + score
				self.jueDiFanJiScoreDict[ victoryDBID ][ 1 ] = newScore
				self.jueDiFanJiScoreDict[ victoryDBID ][ 2 ] = victoryNum
			self.jueDiFanJiTempHPDict[ victoryDBID ] = hp
			if not self.jueDiFanJiScoreDict.has_key( failedDBID ):
				self.jueDiFanJiScoreDict[ failedDBID ] = [ failedName, 0, 0 ]
			#ʧ����ҵ���ʤ����Ҫ����
			self.clearVictoryCountDict( failedDBID )
			#ʤ���������ʤ�Ͳ�����ʤ�Ļ��ֲ�һ������Ҫ���͵��ͻ��˽�����ʾ
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( victoryDBID ) and self.isOnlineOrNot( victoryDBID ):
				victoryPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ victoryDBID ][ 0 ]
				victoryPlayerMB.client.receiveScoreInfo( score )
				victoryPlayerMB.client.selectLeaveOrNot( csdefine.JUE_DI_FAN_JI_VICTORY_STATUS )
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( failedDBID ) and self.isOnlineOrNot( failedDBID ):
				failedPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ failedDBID ][ 0 ]
				failedPlayerMB.client.selectLeaveOrNot( csdefine.JUE_DI_FAN_JI_FAILED_STATUS )
		elif status == csdefine.JUE_DI_FAN_JI_DRAW_STATUS:					#ƽ��
			score = DRAW_SCORE_NUM
			if not self.jueDiFanJiScoreDict.has_key( victoryDBID ):
				self.jueDiFanJiScoreDict[ victoryDBID ] = [ victoryName, score, 0 ]
			else:
				newScore = self.jueDiFanJiScoreDict[ victoryDBID ][ 1 ] + score
				self.jueDiFanJiScoreDict[ victoryDBID ][ 1 ] = newScore
			if not self.jueDiFanJiScoreDict.has_key( failedDBID ):
				self.jueDiFanJiScoreDict[ failedDBID ] = [ failedName, score, 0 ]
			else:
				newScore = self.jueDiFanJiScoreDict[ failedDBID ][ 1 ] + score
				self.jueDiFanJiScoreDict[ failedDBID ][ 1 ] = newScore
			#������ƽ�֣�˫������ʤ������Ҫ����
			self.clearVictoryCountDict( victoryDBID )
			self.clearVictoryCountDict( failedDBID )
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( victoryDBID ) and self.isOnlineOrNot( victoryDBID ):
				victoryPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ victoryDBID ][ 0 ]
				victoryPlayerMB.client.selectLeaveOrNot( csdefine.JUE_DI_FAN_JI_DRAW_STATUS )
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( failedDBID ) and self.isOnlineOrNot( failedDBID ):
				failedPlayerMB = self.jueDiFanJiDBIDToPlayerInfo[ failedDBID ][ 0 ]
				failedPlayerMB.client.selectLeaveOrNot( csdefine.JUE_DI_FAN_JI_DRAW_STATUS )
		self.clearJueDiFanJiMatcher( victoryDBID )		#��ʤ������������ƥ�����
		self.changeStateDict( victoryDBID, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
		self.clearJueDiFanJiMatcher( failedDBID )		#��ʧ�ܵ���������ƥ�����
		self.changeStateDict( failedDBID, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
		
	def onClearRecord( self, dbid ):
		"""
		��Ҷ����ߵ��������Ҫ�����Ӧ��ƥ���¼
		"""
		self.clearJueDiFanJiMatcher( dbid )
		self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP )
		
	def sendOfflineReward( self, dbid, status ):
		"""
		��ҵ��ߣ��������߽���
		"""
		if self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
			level = self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 2 ]
		else:
			level = 0
		if status == csdefine.JUE_DI_FAN_JI_VICTORY_STATUS:
			#���ط�����1v1��ʤ�߾��顢��Ǯ������ʽΪ�� (nָ���ǵ�ĿǰΪֹ����ʤ�����ܴ�������һ��ʤ����nΪ1 )
			#���飺(175 * Lv ^ 1.5 + 460) * (n ^ 2 / (n ^ 2 + n + 1)) 
			#��Ǯ��18 * Lv * 1.5 ^ (0.1 * Lv - 1) * (n ^ 2 / (n ^ 2 + n + 1)) 
			n = 1
			if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
				n = self.jueDiFanJiVictoryCountDict[ dbid ][ 0 ] + 1
			exp = int( ( 175 * level ** 1.5 + 460 ) * ( n ** 2 / ( n ** 2 + n + 1.0 ) ) )
			moneyNum = int( 18 * level * 1.5 ** ( 0.1 * level - 1 ) * ( n ** 2 / ( n ** 2 + n + 1.0 ) ) )
		elif status == csdefine.JUE_DI_FAN_JI_DRAW_STATUS:
			#���ط�����1v1��ƽ�־��顢��Ǯ������ʽΪ�� 
			#���飺(116 * Lv ^ 1.5 + 307) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			#��Ǯ��12 * Lv * 1.5 ^ (0.1 * Lv - 1) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			exp = int( ( 116 * level ** 1.5 + 307 ) * ( 1/ 3.0 ) )
			moneyNum = int( 12 * level * 1.5 ** ( 0.1 * level - 1 ) * ( 1/3.0 ) )
		elif status == csdefine.JUE_DI_FAN_JI_FAILED_STATUS:
			#���ط�����1v1�����߾��顢��Ǯ������ʽΪ�� 
			#���飺(58 * Lv ^ 1.5 + 153) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			#��Ǯ��6 * Lv * 1.5 ^ (0.1 * Lv - 1) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			exp = int( ( 58 * level ** 1.5 + 153 ) * ( 1/ 3.0 ) )
			moneyNum = int( 6 * level * 1.5 ** ( 0.1 * level - 1 ) * ( 1/3.0 ) )
		itemDatas = []
		item = g_items.createDynamicItem( REWARD_EXP_ITEM_ID )
		if item:
			item.setExp( exp )
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		if len( itemDatas ) != 0 and self.jueDiFanJiDBIDToPlayerInfo.has_key( dbid ):
			playerName = self.jueDiFanJiDBIDToPlayerInfo[ dbid ][ 1 ]
			title = cschannel_msgs.JUE_DI_FAN_JI_REWARD_TITLE
			content = cschannel_msgs.JUE_DI_FAN_JI_REWARD_CONTENT
			BigWorld.globalData["MailMgr"].send( None, playerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", title, content, moneyNum, itemDatas )
			
	def sendOnlineReward( self, playerMB, dbid, status, level ):
		"""
		�������߽���
		"""
		if status == csdefine.JUE_DI_FAN_JI_VICTORY_STATUS:
			#���ط�����1v1��ʤ�߾��顢��Ǯ������ʽΪ�� (nָ���ǵ�ĿǰΪֹ����ʤ�����ܴ�������һ��ʤ����nΪ1 )
			#���飺(175 * Lv ^ 1.5 + 460) * (n ^ 2 / (n ^ 2 + n + 1)) 
			#��Ǯ��18 * Lv * 1.5 ^ (0.1 * Lv - 1) * (n ^ 2 / (n ^ 2 + n + 1)) 
			n = 1
			if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
				n = self.jueDiFanJiVictoryCountDict[ dbid ][ 0 ] + 1
			exp = int( ( 175 * level ** 1.5 + 460 ) * ( n ** 2 / ( n ** 2 + n + 1.0 ) ) )
			money = int( 18 * level * 1.5 ** ( 0.1 * level - 1 ) * ( n ** 2 / ( n ** 2 + n + 1.0 ) ) )
		elif status == csdefine.JUE_DI_FAN_JI_DRAW_STATUS:
			#���ط�����1v1��ƽ�־��顢��Ǯ������ʽΪ�� 
			#���飺(116 * Lv ^ 1.5 + 307) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			#��Ǯ��12 * Lv * 1.5 ^ (0.1 * Lv - 1) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			exp = int( ( 116 * level ** 1.5 + 307 ) * ( 1/ 3.0 ) )
			money = int( 12 * level * 1.5 ** ( 0.1 * level - 1 ) * ( 1/3.0 ) )
		elif status == csdefine.JUE_DI_FAN_JI_FAILED_STATUS:
			#���ط�����1v1�����߾��顢��Ǯ������ʽΪ�� 
			#���飺(58 * Lv ^ 1.5 + 153) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			#��Ǯ��6 * Lv * 1.5 ^ (0.1 * Lv - 1) * (1 ^ 2 / (1 ^ 2 + 1 + 1)) 
			exp = int( ( 58 * level ** 1.5 + 153 ) * ( 1/ 3.0 ) )
			money = int( 6 * level * 1.5 ** ( 0.1 * level - 1 ) * ( 1/3.0 ) )
		playerMB.cell.addExp( exp, csdefine.CHANGE_EXP_JUE_DI_FAN_JI )
		playerMB.cell.activity_gainMoney( money, csdefine.CHANGE_MONEY_JUE_DI_FAN_JI )
			
			
	def onSelectRepeatedVictory( self, baseMailbox, dbid, hp, playerName, level, playerClass ):
		"""
		���ѡ����ʤ
		"""
		if self.jueDiFanJiTempHPDict.has_key( dbid ):
			playerHP = self.jueDiFanJiTempHPDict[ dbid ]
			del self.jueDiFanJiTempHPDict[ dbid ]
		else:
			playerHP = hp
		if playerHP == 0:		#���ղ߻���Ҫ�����������û��Ѫ�ˣ�����1��Ѫ���Ա�֤�´ν��븱����ʱ����1��Ѫ
			playerHP = 1
		if not self.jueDiFanJiVictoryCountDict.has_key( dbid ):
			self.jueDiFanJiVictoryCountDict[ dbid ] = [ 1, playerHP ]
		else:
			victoryCount = self.jueDiFanJiVictoryCountDict[ dbid ][ 0 ] + 1
			self.jueDiFanJiVictoryCountDict[ dbid ] = [ victoryCount, playerHP ]
		self.jueDiFanJiDBIDToPlayerInfo[ dbid ] = [ baseMailbox, playerName, level, playerClass ]
		self.changeStateDict( dbid, csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP )
		self.pushJueDiFanJiQueue( dbid, level )
		
	def clearVictoryCountDict( self, dbid ):
		"""
		��ҵ��߻���ʧ�ܻ�����ƽ�֣���ô�Ὣ��ҵ���ʤ��¼ɾ��
		"""
		if self.jueDiFanJiVictoryCountDict.has_key( dbid ):
			del self.jueDiFanJiVictoryCountDict[ dbid ]
		
	def onJueDiFanJiRoleDestroy( self, dbid ):
		"""
		���ط�����������
		"""
		self.jueDiFanJiDBIDToOnlineDict[ dbid ] = 0
		
	def calJueDiFanJiRankAndNotice( self ):
		"""
		��������������
		"""
		scoreList = self.jueDiFanJiScoreDict.values()
		scoreList = sorted( scoreList, compareScore )
		if len( scoreList ) <= FIRST_THIRD_RANK_NUM:
			firstThirdRankList = scoreList
		else:
			firstThirdRankList = scoreList[:FIRST_THIRD_RANK_NUM]
		playerDBIDList = []
		firstPlayerDBID = 0
		for i,record in self.jueDiFanJiScoreDict.iteritems():
			if record in firstThirdRankList:
				if record == firstThirdRankList[ 0 ]:
					firstPlayerDBID = i
				playerDBIDList.append( i )
		if firstPlayerDBID and self.jueDiFanJiDBIDToPlayerInfo.has_key( firstPlayerDBID ):
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.JUE_DI_FAN_JI_CHAMPION_BROADCAST % self.jueDiFanJiDBIDToPlayerInfo[ firstPlayerDBID ][ 1 ], [] )
		for playerInfo in self.jueDiFanJiDBIDToPlayerInfo.itervalues():
			playerMB = playerInfo[ 0 ]
			playerMB.cell.receiveBulletin( scoreList )
		self.sendFirstThirdRewardInfo( playerDBIDList )
		for playerDBID in playerDBIDList:
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( playerDBID ):
				playerInfo = self.jueDiFanJiDBIDToPlayerInfo[ playerDBID ]
				self.jueDiFanJiFirstThirdRank.append( ( playerInfo[0], playerDBID, playerInfo[1], playerInfo[2], playerInfo[3] ) )
				
	def sendFirstThirdRewardInfo( self, playerDBIDList ):
		"""
		����ǰ������ҽ�����Ϣ
		"""
		msgList = []
		for playerDBID in playerDBIDList:
			if self.jueDiFanJiScoreDict.has_key( playerDBID ):
				scoreInfo = self.jueDiFanJiScoreDict[ playerDBID ]
				msgList.append( scoreInfo[0] )
				msgList.append( scoreInfo[1] )
		title = cschannel_msgs.JUE_DI_FAN_JI_FIRST_THIRD_REWARD_TITLE
		content = ""
		if len( msgList ) == LENGTH_OF_PLAYER_1 * 2:
			content = cschannel_msgs.JUE_DI_FAN_JI_FIRST_THIRD_CONTENT_2 %( msgList[0], msgList[1], msgList[2], msgList[3] )
		elif len( msgList ) == LENGTH_OF_PLAYER_2 * 2:
			content = cschannel_msgs.JUE_DI_FAN_JI_FIRST_THIRD_CONTENT_1 %( msgList[0], msgList[1], msgList[2], msgList[3], msgList[4], msgList[5] )
		for playerDBID in playerDBIDList:
			if self.jueDiFanJiDBIDToPlayerInfo.has_key( playerDBID ):
				playerInfo = self.jueDiFanJiDBIDToPlayerInfo[ playerDBID ]
				BigWorld.globalData["MailMgr"].send( None, playerInfo[1], csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", title, content, 0, "" )

		
	def resetJueDiFanJiData( self ):
		"""
		���þ��ط��������
		"""
		self.jueDiFanJiQueue = []							#���ط����ŶӶ���
		self.jueDiFanJiScoreDict = {}						#���ط��������ֵ䣬����{dbid1:[playerName1, score1, victoryNum1 ],dbid2:[playerName2, score2, victoryNum2 ],...}(����victoryNum1Ϊ��ʤ����score1Ϊ����)
		self.jueDiFanJiDBIDToPlayerInfo = {}				#���ط���DBID��Ӧ��player��Ϣ�ֵ䣬����{dbid1:[playerMB1,playerName1,level1,playerClass1],dbid2:[playerMB2,playerName2,level2,playerClass2]}
		self.jueDiFanJiVictoryCountDict = {}				#���ط�����ʤ������¼�ֵ�
		self.jueDiFanJiStateDict = {}						#���ط���ÿ�����״̬�ֵ�
		self.jueDiFanJiMatchList = []						#���ط���ƥ���б�����[(dbid1,dbid2,ƥ������),(dbid3,dbid4,ƥ������),...](����dbid1��dbid2�Ƕ�ս˫����ƥ������ָ�������Ƕ��ٴ�ƥ��)
		self.jueDiFanJiMatchedDBIDToIndex = {}				#���ط����Ѿ�ƥ���DBID��Ӧ��Index�ֵ䣬����{dbid1:index1,dbid2:index1,dbid3:index2,dbid4:index2,...}
		self.jueDiFanJiEmptyIndexList = []					#���ط����յ�λ������
		self.curMaxMatchCount = 0							#Ŀǰ�Ѿ�ƥ��ɹ����������
		self.requestCount = 0								#�����������
		self.operateCount = 0								#���ڲ���������
		self.jueDiFanJiDBIDToOnlineDict = {}				#���ط���DBID��Ӧ����Ƿ������ֵ�,����{123:1,234:0,...}������������1��ʾ����������0��ʾ��

	def onAoZhanQunXiongRequest( self ):
		"""
		��սȺ�۱�����Ҫȡ��ǰ����������
		"""
		for info in self.jueDiFanJiFirstThirdRank:
			BigWorld.globalData["AoZhanQunXiongMgr"].onSignUp( info[0], info[1], info[2], info[3], info[4] )

		
		
def compareScore( a, b ):
	"""
	���ֱȽϺ���
	"""
	if a[1] < b[1]:
		return 1
	elif a[1] == b[1] and a[2] < b[2]:
		return 1
	elif a[1] == b[1] and a[2] == b[2]:
		return 0
	elif a[1] == b[1] and a[2] > b[2]:
		return -1
	elif a[1] > b[1]:
		return -1
	