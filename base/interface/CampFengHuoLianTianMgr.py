# -*- coding: gb18030 -*-
import time
import random

import BigWorld
import csstatus
import csdefine
import cschannel_msgs
import csconst
import Love3
from bwdebug import *



CAMP_ROLE_NUM = 2				#��Ӫ�������ÿ����Ӫ�������

NOTICE_TIME_1 = 30 * 60			#֪ͨʱ����1
NOTICE_TIME_2 = 15 * 60			#֪ͨʱ����2

MATCH_TIME = 30 * 60			#����ʱ��Ϊ30����
SIGN_UP_TIME = 10 * 60			#����ʱ��Ϊ10����

TIMER_NOTICE_1 = 10
TIMER_NOTICE_2 = 11

REWARD_FIRST_PLAYER_ITEM_ID = 60101282	#��һ����������ID
CAMP_FENG_HUO_LIAN_TIAN_SPACENAME = "fu_ben_zhen_ying_feng_huo_lian_tian"

class CampInfo:
	"""
	������Ӫ��Ա����
	"""
	def __init__( self, camp, dbid, playerMB ):
		self.camp = camp
		self.dbid = dbid
		self.playerMB = playerMB
		
	def getCamp( self ):
		return self.camp
		
	def getDBID( self ):
		return self.dbid
		
	def getMailBox( self ):
		return self.playerMB
		
	def setCamp( self, camp ):
		self.camp = camp
		
	def setDBID( self, dbid ):
		self.dbid = dbid
		
	def setMailBox( self, playerMB ):
		self.playerMB = playerMB
		
class CampItem:
	"""
	һ����������
	"""
	def __init__( self ):
		self.taoismCampInfo = []
		self.demonCampInfo = []
	
	def isCampTotalFull( self ):
		"""
		�ж�ħ���Լ��ɵ���Ӫ�����Ƿ�����
		"""
		if self.isTaosimCampFull() and self.isDemonCampFull():
			return True
		else:
			return False
	
	def isCampFull( self, camp ):
		"""
		ĳ����Ӫ�������Ƿ�����
		"""
		campInfo = []
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			if self.isTaosimCampFull():
				return True
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			if self.isDemonCampFull():
				return True
		return False
	
	def isTaosimCampFull( self ):
		"""
		�ж��ɵ������Ƿ�����
		"""
		if len( self.taoismCampInfo ) >= CAMP_ROLE_NUM:
			return True
	
	def isDemonCampFull( self ):
		"""
		�ж�ħ�������Ƿ�����
		"""
		if len( self.demonCampInfo ) >= CAMP_ROLE_NUM:
			return True
	
	def addCampMember( self, camp, dbid, playerMB ):
		"""
		�����Ӫ��Ա
		"""
		campMember = CampInfo( camp, dbid, playerMB )
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			self.taoismCampInfo.append( campMember )
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			self.demonCampInfo.append( campMember )
			
	def delCampMember( self, camp, dbid ):
		"""
		ɾ����Ӫ��Ա
		"""
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			for campInfo in self.taoismCampInfo:
				if campInfo.getDBID() == dbid:
					#��ʾ�Ѿ��˳������ɹ���֮�󽫶�Աɾ��
					playerMB = campInfo.getMailBox()
					if playerMB:
						playerMB.client.onStatusMessage( csstatus.CAMP_FENG_HUO_EXIT_SUCCESS, "" )
					self.taoismCampInfo.remove( campInfo )
					return
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			for campInfo in self.demonCampInfo:
				if campInfo.getDBID() == dbid:
					#��ʾ�Ѿ��˳������ɹ���֮�󽫶�Աɾ��
					playerMB = campInfo.getMailBox()
					if playerMB:
						playerMB.client.onStatusMessage( csstatus.CAMP_FENG_HUO_EXIT_SUCCESS, "" )
					self.demonCampInfo.remove( campInfo )
					return

	def getTaoismCampInfo( self ):
		"""
		��ȡ��Ӧ���ɵ���Ӫ�����Ϣ
		"""
		return self.taoismCampInfo
		
	def getDemonCampInfo( self ):
		"""
		��ȡ��Ӧ��ħ����Ӫ�����Ϣ
		"""
		return self.demonCampInfo

	def findCampMemberByDBID( self, camp, dbid ):
		"""
		������ҵ���Ӫ�Լ�DBID���Ҷ�Ӧ��CampInfo����
		"""
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			for campInfo in self.taoismCampInfo:
				if campInfo.getDBID() == dbid:
					return campInfo
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			for campInfo in self.demonCampInfo:
				if campInfo.getDBID() == dbid:
					return campInfo
		else:
			return None

	def noticeCampPlayerInfo( self ):
		for info in self.taoismCampInfo:
			playerMB = info.getMailBox()
			if playerMB:
				playerMB.cell.setCampFengHuo_signUpFlag( 1 )
		for info in self.demonCampInfo:
			playerMB = info.getMailBox()
			if playerMB:
				playerMB.cell.setCampFengHuo_signUpFlag( 1 )

	def noticePlayerUpdateMaxBattleNum( self, maxNum ):
		"""
		����
		"""
		for info in self.taoismCampInfo:
			playerMB = info.getMailBox()
			if playerMB:
				playerMB.cell.updateCampFengHuoBattleInfo( maxNum )
		for info in self.demonCampInfo:
			playerMB = info.getMailBox()
			if playerMB:
				playerMB.cell.updateCampFengHuoBattleInfo( maxNum )

class CampItems:
	"""
	�ೡ��������
	"""
	def __init__( self ):
		self.maxBattleNum = 0
		self.lastTaoismNoFullBattleNum = 0
		self.lastDemonNoFullBattleNum = 0
		self.lastNoFullBattleNum = 0
		self.battleItems = {}
		
	def getMaxBattleNum( self ):
		"""
		��ȡĿǰ�Ѿ��������ս������
		"""
		return self.maxBattleNum
		
	def getLastNoFullBattleNum( self ):
		"""
		��ȡĿǰ�Ѿ��������һ��δ����ս����
		"""
		return self.lastNoFullBattleNum
		
	def getLastTaoismNoFullBattleNum( self ):
		"""
		��ȡĿǰ�Ѿ��������һ���ɵ���Ӫδ��ս����
		"""
		return self.lastTaoismNoFullBattleNum
		
	def getLastDemonNoFullBattleNum( self ):
		"""
		��ȡĿǰ�Ѿ��������һ��ħ����Ӫδ��ս����
		"""
		return self.lastDemonNoFullBattleNum
		
	def getLastCampNoFullBattleNum( self, camp ):
		"""
		��ȡĿǰ�Ѿ��������һ��ĳ����Ӫ��δ��ս����
		"""
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			return self.getLastTaoismNoFullBattleNum()
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			return self.getLastDemonNoFullBattleNum()
		return -1
		
	def setMaxBattleNum( self, maxBattleNum ):
		"""
		����Ŀǰ�Ѿ��������ս������
		"""
		self.maxBattleNum = maxBattleNum
		
	def setLastNoFullBattleNum( self, lastNoFullBattleNum ):
		"""
		����Ŀǰ�Ѿ��������һ��δ����ս����
		"""
		self.lastNoFullBattleNum = lastNoFullBattleNum
		
	def setLastTaoismNoFullBattleNum( self, lastTaoismNoFullBattleNum ):
		"""
		����Ŀǰ�Ѿ��������һ���ɵ���Ӫδ��ս����
		"""
		self.lastTaoismNoFullBattleNum = lastTaoismNoFullBattleNum
		
	def setLastDemonNoFullBattleNum( self, lastDemonNoFullBattleNum ):
		"""
		����Ŀǰ�Ѿ��������һ��ħ����Ӫδ��ս����
		"""
		self.lastDemonNoFullBattleNum = lastDemonNoFullBattleNum
		
	def setLastCampNoFullBattleNum( self, camp, num ):
		"""
		����Ŀǰ�Ѿ��������һ��ĳ����Ӫ��δ��ս����
		"""
		DEBUG_MSG( "camp is %s,num is %s"%( camp, num ) )
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			self.setLastTaoismNoFullBattleNum( num )
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			self.setLastDemonNoFullBattleNum( num )
		
	def findCampLastNoFullBattleNum( self, camp, index ):
		"""
		�ӵ�ǰ��ս����������ұ���Ӫ���һ��δ����ս����
		"""
		num = -1
		for i in xrange( index, self.maxBattleNum + 1 ):
			if not self.battleItems[ i ].isCampFull( camp ):
				num = i
				break
		return num
		
	def newBattle( self ):
		"""
		�½�һ��ս��
		"""
		self.maxBattleNum += 1
		newBattleItem = CampItem()
		self.battleItems[ self.maxBattleNum ] = newBattleItem
		if self.lastNoFullBattleNum == 0:
			self.lastNoFullBattleNum += 1
			self.lastTaoismNoFullBattleNum += 1
			self.lastDemonNoFullBattleNum += 1
		self.noticeNoFullBattleUpdateInfo()
	
	def noticeNoFullBattleUpdateInfo( self ):
		"""
		֪ͨδ��ս������ս����Ϣ
		"""
		lastNoFullBattleNum = self.getLastNoFullBattleNum()
		for i in xrange( lastNoFullBattleNum, self.maxBattleNum + 1 ):
			battleItem = self.getBattleByKey( i )
			if battleItem:
				battleItem.noticePlayerUpdateMaxBattleNum( self.maxBattleNum )
	
	def getBattleByKey( self, key ):
		"""
		���ݹؼ��ֻ�ȡ��Ӧ��ս��ʵ��
		"""
		return self.battleItems.get( key, None )


class CampFengHuoLianTianMgr:
	# ��Ӫ�������������
	def __init__( self ):
		self.campBattleItem = CampItems()
		self.fengHuoWaitQueue = []
		self.fengHuoChangeMoraleQueue = []
		self.fengHuoPlayerDBIDToBattleNum = {}
		self.fengHuo_domains = {}
		self.operateNum = 1
		self.rewardOperateNum = 1
		self.fengHuoNotifyTimer = 0
		
	def registerCrond( self ):
		"""
		virtual method.
		��������ʼ�����
		"""
		taskEvents = {
					  	"CampFHLT_start_notify"	: "fengHuo_onStartNotify",						# ��ʼ֪ͨ
					  	"CampFHLT_sign_up_start" : "fengHuo_onSignUpStart",						# ��������
					  	"CampFHLT_start" : "fengHuo_onStart",									# �����
					  	"CampFHLT_activity_end"	: "fengHuo_onEnd",								# �����
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
				
	def fengHuo_onStartNotify( self ):
		"""
		define method
		��Ӫ���������ʼ֪ͨ
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_NOTICE_1, [] )
		#self.campBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_NOTICE_1, cschannel_msgs.CAMP_FENG_HUO_DEMON_NOTICE_1, [] )
		self.resetCampFengHuo()
		self.fengHuoNotifyTimer = self.addTimer( NOTICE_TIME_1, 0, TIMER_NOTICE_1 )
	
	def resetCampFengHuo( self ):
		"""
		������Ӫ����
		"""
		DEBUG_MSG( "reset campFengHuo datas" )
		self.campBattleItem = CampItems()
		self.fengHuoWaitQueue = []
		self.fengHuoChangeMoraleQueue = []
		self.fengHuoPlayerDBIDToBattleNum = {}
		self.fengHuo_domains = {}
		self.operateNum = 1
		self.rewardOperateNum = 1
		self.fengHuoNotifyTimer = 0
	
	def fengHuo_onSignUpStart( self ):
		"""
		��Ӫ�������֪ͨ��������ʼ����
		"""
		if self.fengHuoNotifyTimer:
			self.delTimer( self.fengHuoNotifyTimer )
		if BigWorld.globalData.has_key( "campFengHuo_startSignUp" ):
			curTime = time.localtime()
			ERROR_MSG( "CampFengHuoLianTian has started to sign up, cannot start again. Time is %s hour %s minute"%(curTime[3],curTime[4] ) )
			return
		BigWorld.globalData[ "campFengHuo_startSignUp" ] = True
		BigWorld.globalData[ "campFengHuoSignUpTime" ] = time.time() + SIGN_UP_TIME
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_SIGN_UP, [] )
		#self.campBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_SIGN_UP, cschannel_msgs.CAMP_FENG_HUO_DEMON_SIGN_UP, [] )
	
	def fengHuo_onStart( self ):
		"""
		define method
		��Ӫ���������ʼ
		"""
		#Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_JUE_DI_FAN_JI_BEGIN, [] )
		#self.campBroadcast( cschannel_msgs.BCT_JUE_DI_FAN_JI_BEGIN, cschannel_msgs.BCT_JUE_DI_FAN_JI_BEGIN, [] )
		if BigWorld.globalData.has_key( "campFengHuo_start" ):
			curTime = time.localtime()
			ERROR_MSG( "CampFengHuoLianTian has started, cannot start again. Time is %s hour %s minute"%(curTime[3],curTime[4] ) )
			return
		if BigWorld.globalData.has_key( "campFengHuo_startSignUp" ):
			del BigWorld.globalData[ "campFengHuo_startSignUp" ]
		if BigWorld.globalData.has_key( "campFengHuoSignUpTime" ):
			del BigWorld.globalData[ "campFengHuoSignUpTime" ]
		BigWorld.globalData[ "campFengHuo_start" ] = True
		BigWorld.globalData[ "campFengHuoOverTime" ] = time.time() + MATCH_TIME
		#���ʼ��֪ͨ���ʸ��������ҵ������Ϳ򣬿���ѡ���ͽ��븱��
		self.noticeTransportPlayer()
		
	def fengHuo_onEnd( self ):
		"""
		define method
		��Ӫ�����������
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_FENG_HUO_END, [] )
		#self.campBroadcast( cschannel_msgs.CAMP_FENG_HUO_END, cschannel_msgs.CAMP_FENG_HUO_END, [] )
		if BigWorld.globalData.has_key( "campFengHuo_start" ):
			del BigWorld.globalData[ "campFengHuo_start" ]
		self.closeCampFengHuoRooms()
		
	def onRequestCampFengHuoSignUp( self, camp, dbid, playerMB ):
		"""
		����������μ���Ӫ�������
		"""
		if self.campBattleItem.getMaxBattleNum() == 0:
			self.campBattleItem.newBattle()
		lastCampNoFullBattleNum = self.campBattleItem.getLastCampNoFullBattleNum( camp )
		if lastCampNoFullBattleNum == -1:
			return
		battleItem = self.campBattleItem.getBattleByKey( lastCampNoFullBattleNum )
		if battleItem:
			if not battleItem.isCampFull( camp ) and BigWorld.globalData.has_key( "campFengHuo_startSignUp" ):
				#ģ�²���ϵͳPV����ʵ�ֻ��⣬�Ƚ���P���������ź�����һ�������Ӧ���ź���С��0����ô����ȴ�������
				self.operateNum = self.operateNum - 1
				if self.operateNum < 0:
					self.joinFengHuoWaitQueue( self.onRequestCampFengHuoSignUp, [ camp, dbid, playerMB ] )
					return
				#�ٽ�������
				if self.fengHuoPlayerDBIDToBattleNum.has_key( dbid ):
					battleNum = self.fengHuoPlayerDBIDToBattleNum[ dbid ]
					lastBattleItem = self.campBattleItem.getBattleByKey( battleNum )
					campInfo = lastBattleItem.findCampMemberByDBID( camp, dbid )
					if campInfo:
						#������Ӧ��playerMB��Ϣ
						campInfo.setMailBox( playerMB )
					#lastBattleItem.delCampMember( camp, dbid )
					#lastBattleItem.addCampMember( camp, dbid, playerMB )
				else:
					battleItem.addCampMember( camp, dbid, playerMB )
					#��Ҫ��ʾ����Լ���ǰ������ս�����Լ�Ŀǰ���ս����
					maxNum = self.campBattleItem.getMaxBattleNum()
					if playerMB:
						playerMB.cell.setCampFengHuoBattleInfo( BigWorld.globalData[ "campFengHuoSignUpTime" ] - time.time(), lastCampNoFullBattleNum, maxNum )
					DEBUG_MSG( "camp is %s,dbid is %s, playerMB is %s,maxNum is %s,lastCampNoFullBattleNum is %s"%( camp, dbid, playerMB, maxNum, lastCampNoFullBattleNum ) )
					self.fengHuoPlayerDBIDToBattleNum[ dbid ] = lastCampNoFullBattleNum
					if battleItem.isCampFull( camp ):
						num = self.campBattleItem.findCampLastNoFullBattleNum( camp, lastCampNoFullBattleNum + 1 )
						DEBUG_MSG( "findCampLastNoFullBattleNum: num is %s"%num)
						if num != -1:
							self.campBattleItem.setLastCampNoFullBattleNum( camp, num )
						else:
							self.campBattleItem.newBattle()
							maxNum = self.campBattleItem.getMaxBattleNum()
							self.campBattleItem.setLastCampNoFullBattleNum( camp, maxNum )
						if battleItem.isCampTotalFull():
							self.campBattleItem.setLastNoFullBattleNum( lastCampNoFullBattleNum + 1 )
							DEBUG_MSG( "set setLastNoFullBattleNum to %s"%str( lastCampNoFullBattleNum + 1 ) )
							self.noticePlayerBattleInfo( lastCampNoFullBattleNum )
				#ģ�²���ϵͳPV����ʵ�ֻ��⣬����V���������ź�����һ�������Ӧ���ź���С�ڵ���0����ô�����ͷų�һ���ȴ��ź����Ĳ���
				self.operateNum = self.operateNum + 1
				if self.operateNum <= 0:
					self.releaseFengHuoWaitQueue()
	
	def noticePlayerBattleInfo( self, battleNum ):
		"""
		֪ͨ��������Ӧ��ս����Ϣ
		"""
		battleItem = self.campBattleItem.getBattleByKey( battleNum )
		if battleItem:
			battleItem.noticeCampPlayerInfo()
	
	def onRequestCampFengHuoQuitSignUp( self, camp, dbid, playerMB ):
		"""
		��������˳���������
		"""
		if self.fengHuoPlayerDBIDToBattleNum.has_key( dbid ) and BigWorld.globalData.has_key( "campFengHuo_startSignUp" ):
			battleNum = self.fengHuoPlayerDBIDToBattleNum[ dbid ]
			battleItem = self.campBattleItem.getBattleByKey( battleNum )
			if battleItem.isCampTotalFull():			#�����������൱�ڽ��ж����������ʱ����Ҫ���л���Ĵ���ֻ�е�����δ�������˼����ʱ�򣬲��б�Ҫ���л���Ĵ���
				#ս��˫����������������ʾ�Ѿ������ɹ������ܹ��˳�
				if playerMB:
					playerMB.client.onStatusMessage( csstatus.CAMP_FENG_HUO_CANNOT_EXIT, "" )
			else:
				#ģ�²���ϵͳPV����ʵ�ֻ��⣬�Ƚ���P���������ź�����һ�������Ӧ���ź���С��0����ô����ȴ�������
				self.operateNum = self.operateNum - 1
				if self.operateNum < 0:
					self.joinFengHuoWaitQueue( self.onRequestCampFengHuoQuitSignUp, [ camp, dbid, playerMB ] )
					return
				battleItem.delCampMember( camp, dbid )
				del self.fengHuoPlayerDBIDToBattleNum[ dbid ]
				DEBUG_MSG( "camp is %s, dbid is %s,battleNum is %s"%( camp, dbid, battleNum ) )
				num = self.campBattleItem.getLastCampNoFullBattleNum( camp )
				if num != -1 and battleNum < num:
					self.campBattleItem.setLastCampNoFullBattleNum( camp, battleNum )
				self.operateNum = self.operateNum + 1
				if self.operateNum <= 0:
					self.releaseFengHuoWaitQueue()
	
	def joinFengHuoWaitQueue( self, func, args ):
		"""
		��һЩ��������������ĵȴ�����
		"""
		self.fengHuoWaitQueue.append( ( func, args ) )
		
	def releaseFengHuoWaitQueue( self ):
		"""
		���ȴ����еĲ����ͷţ�ִ�ж�Ӧ�Ĳ���
		"""
		info = self.fengHuoWaitQueue.pop( 0 )
		func = info[ 0 ]
		args = info[ 1 ]
		func( *args )
		
	def onTimer( self, timerID, userArg ):
		"""
		"""
		if userArg == TIMER_NOTICE_1:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_NOTICE_2, [] )
			#self.campBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_NOTICE_2, cschannel_msgs.CAMP_FENG_HUO_DEMON_NOTICE_2, [] )
			self.fengHuoNotifyTimer = self.addTimer( NOTICE_TIME_1, 0, TIMER_NOTICE_2 )
		elif userArg == TIMER_NOTICE_2:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_NOTICE_3, [] )
			#self.campBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_NOTICE_3, cschannel_msgs.CAMP_FENG_HUO_DEMON_NOTICE_3, [] )
			self.fengHuo_onSignUpStart()
	
	def produceCampMsgDict( self, taoismCampMsg, demonCampMsg ):
		"""
		������Ӫ��Ϣ�ֵ�
		"""
		dict = { csdefine.ENTITY_CAMP_TAOISM : taoismCampMsg, csdefine.ENTITY_CAMP_DEMON : demonCampMsg }
		return dict
	
	def campBroadcast( self, taoismCampMsg, demonCampMsg, blobArgs ):
		dict = self.produceCampMsgDict( taoismCampMsg, demonCampMsg )
		Love3.g_baseApp.campActivity_broadcast( dict, blobArgs )
	
	def onRoleRequestEnterCampFHLT( self, camp, dbid, playerMB ):
		"""
		���������������츱��
		"""
		if self.fengHuoPlayerDBIDToBattleNum.has_key( dbid ):
			battleNum = self.fengHuoPlayerDBIDToBattleNum[ dbid ]
			battleItem = self.campBattleItem.getBattleByKey( battleNum )
			DEBUG_MSG( "camp is %s,dbid is %s, playerMB is %s"%( camp, dbid, playerMB ) )
			if battleItem.isCampTotalFull():
				#����������ʾ����Ѿ����Խ�����Ӫ������츱��
				if playerMB:
					playerMB.cell.gotoSpace( CAMP_FENG_HUO_LIAN_TIAN_SPACENAME, ( 0, 0, 0 ), ( 0, 0, 0 ) )
			else:
				#��ʾ��ұ���ս������δ��������δ�ɹ������ܲμӱ���
				if playerMB:
					playerMB.client.onStatusMessage( csstatus.CAMP_FENG_HUO_CANNOT_JOIN, "" )
	
	def noticeTransportPlayer( self ):
		"""
		֪ͨ������ҽ��븱��
		"""
		num = self.campBattleItem.getLastNoFullBattleNum()
		for i in xrange( 1, num ):
			battleItem = self.campBattleItem.getBattleByKey( i )
			if battleItem.isCampTotalFull():
				for info in battleItem.getTaoismCampInfo():
					playerMB = info.getMailBox()
					#�����Ի��������ѡ���Ƿ���
					if playerMB:
						playerMB.client.onCampFengHuoSelectTransportOrNot()
				for info in battleItem.getDemonCampInfo():
					playerMB = info.getMailBox()
					#�����Ի��������ѡ���Ƿ���
					if playerMB:
						playerMB.client.onCampFengHuoSelectTransportOrNot()
	
	def onEnterCampFengHuoSpace( self, spaceDomain, baseMailbox, params ):
		"""
		define method.
		������Ӫ������츱��
		"""
		DEBUG_MSG( "params=",  params )
		
		islogin = params.has_key( "login" )
		camp = params[ "camp" ]
		ename = params[ "ename" ]
		dbid = params[ "dbid" ]
		
		if not self.isRegisterCampFengHuoDomain( spaceDomain.id ):
			self.registerCampFengHuoDomain( spaceDomain )
			
		params[ "left" ] = csdefine.ENTITY_CAMP_TAOISM
		params[ "right" ] = csdefine.ENTITY_CAMP_DEMON
		if self.fengHuoPlayerDBIDToBattleNum.has_key( dbid ):
			battleNum = self.fengHuoPlayerDBIDToBattleNum[ dbid ]
			params[ "spaceKey" ] = "CampFengHuo_" + str( battleNum )
			spaceDomain.onEnterWarSpace( baseMailbox, params )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
	
	def isRegisterCampFengHuoDomain( self, domainID ):
		return domainID in self.fengHuo_domains
		
	def registerCampFengHuoDomain( self, domain ):
		if domain.id not in self.fengHuo_domains:
			self.fengHuo_domains[ domain.id ] = domain
	
	def closeCampFengHuoRooms( self ):
		DEBUG_MSG( "notify close room")
		for domain in self.fengHuo_domains.itervalues():
			domain.closeCampFengHuoRoom()
	
	def campFHLTReward( self, winnerCamp, failureCamp, playerName ):
		"""
		define method
		��Ӫ������콱��
		"""
		if not winnerCamp:
			if failureCamp == csdefine.ENTITY_CAMP_TAOISM:
				winnerCamp = csdefine.ENTITY_CAMP_DEMON
			elif failureCamp == csdefine.ENTITY_CAMP_DEMON:
				winnerCamp = csdefine.ENTITY_CAMP_TAOISM
			self.changeCampMorale( winnerCamp, failureCamp )
		else:
			self.changeCampMorale( winnerCamp, failureCamp )
		#����ɱ����������ұ��䣬�Լ���Ǯ������
		self.sendFirstPlayerReward( playerName )
	
	def sendFirstPlayerReward( self, playerName ):
		itemDatas = []
		item = g_items.createDynamicItem( REWARD_FIRST_PLAYER_ITEM_ID )
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		if len( itemDatas ) != 0:
			title = cschannel_msgs.CAMP_FENG_HUO_REWARD_TITLE
			content = cschannel_msgs.CAMP_FENG_HUO_REWARD_CONTENT
			BigWorld.globalData["MailMgr"].send( None, playerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", title, content, moneyNum, itemDatas )
	
	def changeCampMorale( self, winnerCamp, failureCamp ):
		self.rewardOperateNum = self.rewardOperateNum - 1
		if self.rewardOperateNum < 0:
			self.joinFengHuoChangeMoraleQueue( self.changeCampMorale, [ winnerCamp, failureCamp ] )
			return
		self.addMorale( winnerCamp, 1 )
		self.addMorale( failureCamp, -1 )
		self.rewardOperateNum = self.rewardOperateNum + 1
		if self.rewardOperateNum <= 0:
			self.releaseFengHuoChangeMoraleQueue()
	
	def joinFengHuoChangeMoraleQueue( self, func, args ):
		"""
		��һЩ��������������ĵȴ�����
		"""
		self.fengHuoChangeMoraleQueue.append( ( func, args ) )
		
	def releaseFengHuoChangeMoraleQueue( self ):
		"""
		���ȴ����еĲ����ͷţ�ִ�ж�Ӧ�Ĳ���
		"""
		info = self.fengHuoChangeMoraleQueue.pop( 0 )
		func = info[ 0 ]
		args = info[ 1 ]
		func( *args )