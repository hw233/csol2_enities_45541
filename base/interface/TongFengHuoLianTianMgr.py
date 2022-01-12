# -*- coding: gb18030 -*-

import BigWorld
import time
import math
import copy
import Love3
import csconst
import csstatus
import csdefine
import cschannel_msgs
from bwdebug import *
from MsgLogger import g_logger

from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()

TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX = 16				#ÿ�����п��Բμӵİ����������
ENTER_SPACE_PLAYER_LIMIT = 15							#ÿ��������������������
FENG_HUO_LIAN_TIAN_TOTAL_ROUNDS = int( math.log( TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX, 2 ) ) # ��ս�ֶ����ִ�


# fengHuoLianTian stage
FENG_HUO_LIAN_TIAN_STAGE_FREE 			= 0
FENG_HUO_LIAN_TIAN_STAGE_NOTIFY			= 1
FENG_HUO_LIAN_TIAN_STAGE_SIGNUP 			= 2
FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY			= 3
FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FINAL 	= 4
FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE	= 5

FENG_HUO_LIAN_TIAN_TIMER				= 30
FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_1		= 30
FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_2		= 15
FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_3		= 5
FENG_HUO_LIAN_TIAN_NEXT_ROUND_START_TIMER = 10

TIMER_USER_AGR_TOTAL_TIME				= 3001
TIMER_USER_AGR_CLOSE_SPACE_PROCESS			= 3002
TIMER_USER_AGR_JOIN_UP_TIME				= 3003
TIMER_USER_AGR_NOTIFY_1					= 3004
TIMER_USER_AGR_NOTIFY_2					= 3005
TIMER_USER_AGR_NOTIFY_3					= 3006
TIMER_USER_AGR_NEXT_ROUND_START			= 3007


class TimerManager:
	def __init__( self ):
		self.timerExRecord = {}
		self.timerExRepeat = {}
		self.timerExRecordID = {}
	
	def addTimerExtend( self, key, time, repeatTime, func, args ):
		timerID = self.addTimer( time, repeatTime, key )
		self.timerExRecord[ key ] = [ func, args, repeatTime, False ]
		self.timerExRecordID[ key ] = timerID
		
	def popTimerExtend( self, key ):
		if self.timerExRecord.has_key( key ):
			self.timerExRecord[ key ][ 3 ] = True
		
		if self.timerExRecordID.has_key( key ):
			self.delTimer( self.timerExRecordID[ key ] )

	def onTimer( self, tid, key ):
		if self.timerExRecord.has_key( key ):
			func = self.timerExRecord[ key ][0]
			args = copy.deepcopy( self.timerExRecord[ key ][ 1 ] )
			repeatTime = self.timerExRecord[ key ][ 2 ]
			isDel = self.timerExRecord[ key ][ 3 ]
			if isDel:
				self.delTimer( tid )
				self.timerExRecord.pop( key )
				return
				
			if repeatTime:
				if self.timerExRepeat.has_key( key ):
					if self.timerExRepeat[ key ] >= repeat:
						self.timerExRecord.pop( key )
						self.timerExRepeat.pop( key )
						return
					else:
						self.timerExRepeat[ key ] += 1
				else:
					self.timerExRepeat[ key ] = 1
			else:
				self.timerExRecord.pop( key )
				
			func( *args )


class TongFengHuoLianTianMgr( TimerManager ):
	"""
	�����ս������������죩������
	"""
	def __init__( self ):
		"""
		��ʼ����������Ҫ����Ϣ
		"""
		TimerManager.__init__( self )
		self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_FREE							#Ŀǰ�����ı����׶�
		self.fengHuoLianTianEnter = {}											#������¼�����Ӧ�Ľ�����Ϣfor example:{tongDBID1:[playerBaseMB1,playerBaseMB2,...],...}
		self.fengHuoLianTian_spaceDomains = {}									# ����ע��Ӵ����ĳ���ս��������������, ս������ʱ��Ҫ֪ͨ�����������ĳ����Ϊ�����ս��
		self.canJoinFHLTList = {}
		self.fengHuoLianTiancurrentRound = 0
		self.isGetJoinCityWarTongList = {}
		self.currentWarList = {}
		for cityName in csconst.TONG_CITYWAR_CITY_MAPS.iterkeys():
			self.tongFHLTFightInfos.addCity( cityName, csdefine.ENTITY_CAMP_TAOISM )
			self.tongFHLTFightInfos.addCity( cityName, csdefine.ENTITY_CAMP_DEMON )
			
	def onManagerInitOver( self ):
		"""
		virtual method.
		��������ʼ�����
		"""
		self.tongFengHuoLianTianManager_registerCrond()

	def tongFengHuoLianTianManager_registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
		taskEvents = {
						"TongFengHuoLianTian_notice_start" : "onTongFengHuoLianTianNoticeStart",			#��ʼ֪ͨ
						"TongFengHuoLianTian_notice_end" : "onTongFengHuoLianTianNoticeEnd",					#����֪ͨ
						"TongFengHuoLianTian_start" : "onTongFengHuoLianTianStart",						#��ʼһ������
						"TongFengHuoLianTian_end" : "onTongFengHuoLianTianEnd",							#����һ������
						"TongFengHuoLianTian_all_over" : "onTongFengHuoLianTianAllOver",				#������������
					 }
		crond = BigWorld.globalData["Crond"]
		for taskName,callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )
				
	def resetFengHuoLianTian( self ):
		self.tongFHLTFightInfos.reset()
		self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_FREE
		self.canJoinFHLTList = {}
		self.fengHuoLianTianEnter = {}
		self.fengHuoLianTian_spaceDomains = {}
		self.fengHuoLianTiancurrentRound = 0
		self.isGetJoinCityWarTongList = {}
		self.currentWarList = {}

	def onTongFengHuoLianTianNoticeStart( self ):
		"""
		define method
		�֪ͨ��ʼ
		"""
		self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_NOTIFY
		self.resetFengHuoLianTian()
		self.calCanJoinFHLTTong( csdefine.ENTITY_CAMP_TAOISM )
		self.calCanJoinFHLTTong( csdefine.ENTITY_CAMP_DEMON )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_START_NOTIFY_1, [] )
		self.addTimerExtend( TIMER_USER_AGR_NOTIFY_1, FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_1 * 60, 0, self.notifyAllPlayers, [ FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_1, ])
		INFO_MSG( "TongFengHuoLianTianMgr", "notice" )
		
	def notifyAllPlayers( self, intervalTime ):
		if intervalTime == FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_1:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_START_NOTIFY_2, [] )
			self.addTimerExtend( TIMER_USER_AGR_NOTIFY_2, FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_2 * 60, 0, self.notifyAllPlayers, [ FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_2, ])
		elif intervalTime == FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_2:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_START_NOTIFY_3, [] )
			self.addTimerExtend( TIMER_USER_AGR_NOTIFY_3, FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_3 * 60, 0, self.notifyAllPlayers, [ FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_3, ])
		elif intervalTime == FENG_HUO_LIAN_TIAN_NOTIFY_TIMER_3:
			Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_START_NOTIFY_4, [] )
		
	def onTongFengHuoLianTianNoticeEnd( self ):
		"""
		define method
		�֪ͨ����
		"""
		self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE
		INFO_MSG( "TongFengHuoLianTianMgr", "notice end" )
		
	def onTongFengHuoLianTianStart( self ):
		"""
		define method.
		���ʼ
		"""
		if self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE:
			curTime = time.localtime()
			ERROR_MSG( "���ս��������������ڽ���,%i��%i����ͼ�ٴο�ʼ���ս���������������,Ŀǰ�����׶���%s��"%(curTime[3],curTime[4],self.fengHuoLianTianCurrentStage ) )
			return
		#if BigWorld.globalData.has_key( "AS_tongFengHuoLianTianStart" ) and BigWorld.globalData[ "AS_tongFengHuoLianTianStart" ] == True:
		#	curTime = time.localtime()
		#	ERROR_MSG( "���ս��������������ڽ���,%i��%i����ͼ�ٴο�ʼ���ս�����������������"%(curTime[3],curTime[4] ) )
		#	return
		DEBUG_MSG( "fengHuoLianTian is start." )
		self.fengHuoLianTiancurrentRound = self.fengHuoLianTiancurrentRound + 1
		if self.fengHuoLianTiancurrentRound == FENG_HUO_LIAN_TIAN_TOTAL_ROUNDS - 1:
			self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FINAL
			self.tongFHLTRecords = []
		else:
			self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY
		self.tongFHLTFightInfos.startWar( self )
		self.onFengHuoLianTianStart( FENG_HUO_LIAN_TIAN_TIMER )
		self.addTimerExtend( TIMER_USER_AGR_TOTAL_TIME, FENG_HUO_LIAN_TIAN_TIMER * 60, 0, self.onTongFengHuoLianTianEnd, [])
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_START, [] )
		#BigWorld.globalData[ "AS_tongFengHuoLianTianStart" ] = True
		INFO_MSG( "TongFengHuoLianTianMgr", "start" )
	
	
	def onTongFengHuoLianTianEnd( self ):
		"""
		define method
		�����
		"""
		if self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY and self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FINAL:
			ERROR_MSG("���ս�����������,��ͼ��ǰ����,Ŀǰ�����׶���%s"%self.fengHuoLianTianCurrentStage)
			return
		if BigWorld.globalData.has_key( "fengHuoLianTianOverTime" ):
			del BigWorld.globalData[ "fengHuoLianTianOverTime" ]
			
		DEBUG_MSG( "fengHuoLianTian is end." )
		if self.fengHuoLianTianCurrentStage == FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FINAL:
			self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_FREE
			self.fengHuoLianTiancurrentRound = 0
		else:
			self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE
		for cityKey, item in self.tongFHLTFightInfos.infos.iteritems():
			self.closeFengHuoLianTianRooms( cityKey[0], cityKey[1] )
		
		self.addTimerExtend( TIMER_USER_AGR_CLOSE_SPACE_PROCESS, 5, 0, self.onTimerCloseFengHuoLianTian, [ 1,] )
		self.popTimerExtend( TIMER_USER_AGR_TOTAL_TIME )
		self.addTimerExtend( TIMER_USER_AGR_NEXT_ROUND_START, FENG_HUO_LIAN_TIAN_NEXT_ROUND_START_TIMER * 60, 0, self.onTongFengHuoLianTianStart, [])
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_END, [] )
		#BigWorld.globalData[ "AS_tongFengHuoLianTianStart" ] = False
		INFO_MSG( "TongFengHuoLianTianMgr", "end" )
		
	def onTongFengHuoLianTianAllOver( self ):
		if self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE and self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_FREE:
			curTime = time.localtime()
			ERROR_MSG( "���ս��������������ڽ���,%i��%i����ͼ�������ս���������������,Ŀǰ�����׶���%s��"%(curTime[3],curTime[4],self.fengHuoLianTianCurrentStage ) )
			return
		self.resetFengHuoLianTian()
		self.popTimerExtend( TIMER_USER_AGR_TOTAL_TIME )
		self.popTimerExtend( TIMER_USER_AGR_NEXT_ROUND_START )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_ALL_OVER, [] )
		DEBUG_MSG( "fengHuoLianTian is all over." )
		self.initCityWarFinalInfos()
		
		
	def onFengHuoLianTianStart( self, matchTime ):
		"""
		�����жೡ����,ÿ�����б���ʱ�����,�����Ҫÿ�ο�ʼ��������,������ʱ��ɾ�����
		"""
		BigWorld.globalData[ "fengHuoLianTianOverTime" ] = time.time() + matchTime * 60
	
	def onTimerCloseFengHuoLianTian( self, re ):
		"""
		"""
		if self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_FREE and self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE:
			ERROR_MSG("���ս���ս�����������,��ͼ��ǰ�ر�,Ŀǰ�����׶���%s"%self.fengHuoLianTianCurrentStage)
			return
		re += 1
		isAllOver = True
		for cityName, roundFights in self.tongFHLTFightInfos.infos.iteritems():
			if re > 3:			#���3�γ��Թرն�ʧ�ܣ���ǿ�ƹر��ⳡ����
				roundFights.onTimerCloseWar( self )
				continue
				
			if not roundFights.isAllWarOver():
				isAllOver = False
		
		if not isAllOver:
			self.addTimerExtend( TIMER_USER_AGR_CLOSE_SPACE_PROCESS, 5, 0, self.onTimerCloseFengHuoLianTian, [ re, ] )
		else:
			for fights in self.tongFHLTFightInfos.infos.itervalues():
				fights.initRoundWar( fights.currentRound + 1 )
				
			self.writeToDB()

	def onRoleSelectEnterFHLT( self, playerTongDBID, playerBaseMB, cityName ):
		"""
		���������������츱��
		"""
		#����ȡ��������е�����,���û��Ԥ�������ζ�,��ȡԤ������/2����,���еĻ��ٳ���2,ֱ�����ֻ��һ��������û�а�ᡣ
		#�ж�������иð���ܷ�μӱ���,���ܲμ�,��ʾ�����ҡ�����ܽ���,��������Ϣ�����ܹ��μӱ����б�
		if self.fengHuoLianTianCurrentStage < FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY or not BigWorld.globalData.has_key( "fengHuoLianTianOverTime" ):
			playerBaseMB.client.onStatusMessage( csstatus.TONG_FENG_HUO_LIAN_TIAN_NO_WAR, "" )
			return
		
		#cityName = self.tongFHLTFightInfos.getJoinCityName( playerTongDBID )
		#if not cityName:
		#	self.statusMessage( playerBaseMB, csstatus.TONG_CITY_WAR_CANNOT_ENTER )
		#	return
			
		#if len( self.fengHuoLianTianEnter ) >= ENTER_SPACE_PLAYER_LIMIT:
		#	self.statusMessage( playerBaseMB, csstatus.TONG_FENG_HUO_LIAN_TIAN_IS_FULL )
		#	return
		if self.isGetJoinCityWarTongList.has_key( cityName ) and playerTongDBID in self.isGetJoinCityWarTongList[ cityName ]:
			self.statusMessage( playerBaseMB, csstatus.TONG_FENG_HUO_LIAN_TIAN_NOT_NEED_JOIN )
			return
		
		tongCamp  = self.getTongCampByDBID( playerTongDBID )
		cityKey = ( cityName, tongCamp )
		if not self.tongFHLTFightInfos[ cityKey ].checkTongHasWar( playerTongDBID ):
			self.statusMessage( playerBaseMB, csstatus.TONG_FENG_HUO_LIAN_TIAN_CANNOT_ENTER )
			return
			
		if self.tongFHLTFightInfos[ cityKey ].isWinner( playerTongDBID ):
			self.statusMessage( playerBaseMB, csstatus.TONG_FENG_HUO_LIAN_TIAN_IS_WIN )
			return
			
		spaceKey = self.tongFHLTFightInfos[ cityKey ].getSpaceKey( playerTongDBID )
		playerBaseMB.cell.tong_gotoCityWar( spaceKey )
		pass
	
	def fengHuoLianTianAddEnter( self, tongDBID, playerDBID ):
		if self.fengHuoLianTianEnter.has_key( tongDBID ):
			if playerDBID not in self.fengHuoLianTianEnter[ tongDBID ]:
				self.fengHuoLianTianEnter[ tongDBID ].append( playerDBID )
		else:
			self.fengHuoLianTianEnter[ tongDBID ] = [ playerDBID, ]
	
	def fengHuoLianTianLeave( self, tongDBID, playerDBID ):
		if self.fengHuoLianTianEnter.has_key( tongDBID ):
			if playerDBID in self.fengHuoLianTianEnter[ tongDBID ]:
				self.fengHuoLianTianEnter[ tongDBID ].remove( playerDBID )
	
	def onFengHuoLianTianMessage( self, tongDBID, statusID, *args ):
		"""
		ս�����ͳһϵͳͨ�� ��ָ�����ͨ��
		"""
		args = "" if args == () else str( args )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, args )
	
	def registerFengHuoLianTianDomain( self, domain ):
		"""
		����ע��Ӵ����ĳ���ս����������, ս������ʱ��Ҫ֪ͨ�����������ĳ����Ϊ�����ս��
		"""
		self.fengHuoLianTian_spaceDomains[ domain.id ] = domain

	def isRegisterFengHuoLianTianDomain( self, domainID ):
		"""
		�Ƿ�ע�����domain
		"""
		return domainID in self.fengHuoLianTian_spaceDomains

	def getAllFengHuoLianTianDomain( self ):
		"""
		��ȡ����ս��domain
		"""
		return self.fengHuoLianTian_spaceDomains.values()

	def onFengHuoLianTianAllMessage( self, isAll, statusID, *args ):
		"""
		ս�����ͳһϵͳͨ�� ������ս�����ͨ��
		@param isAll:�Ƿ�����а�� �������Ƿ��Ѿ���ǰ����ս���˵İ�ᷢ����Ϣ
		"""
		for item in self.tongFHLTFightInfos.infos.itervalues():
			notifyList = []
			if isAll:
				notifyList = item.canJoinList
			else:
				notifyList = item.getCurrentTong()
				
			for tongDBID in notifyList:
				self.onFengHuoLianTianMessage( tongDBID, statusID, *args )

	def onEnterFengHuoLianTianSpace( self, spaceDomain, baseMailbox, params ):
		# define method.
		# ����һ��entity��ָ����space��
		DEBUG_MSG( "params=",  params )
		# ע��Ӵ�����ս��domain
		if not self.isRegisterFengHuoLianTianDomain( spaceDomain.id ):
			self.registerFengHuoLianTianDomain( spaceDomain )

		islogin = params.has_key( "login" )
		tongDBID = params[ "tongDBID" ]
		ename = params[ "ename" ]
		
		if self.fengHuoLianTianCurrentStage >= FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY:
			if len( self.fengHuoLianTianEnter ) >= ENTER_SPACE_PLAYER_LIMIT: # �ð����������Ѿ���
				if islogin:
					baseMailbox.logonSpaceInSpaceCopy()
					return
					
				baseMailbox.client.onStatusMessage( csstatus.TONG_FENG_HUO_LIAN_TIAN_REACH_PLAYER_LIMIT, "" )
			else:
				cityName = self.tongFHLTFightInfos.getJoinCityName( tongDBID )
				if cityName:
					tongCamp = self.getTongCampByDBID( tongDBID )
					cityKey = ( cityName, tongCamp )
					fengHuoLianTianItem = self.tongFHLTFightInfos[ cityKey ]
					params[ "spaceKey" ] = fengHuoLianTianItem.getSpaceItemKey( tongDBID )
					war = fengHuoLianTianItem.searchWar( tongDBID )
					params[ "left" ] = war.tongDBID_1  # ����Ӫ
					params[ "leftTongName" ] = self.getTongNameByDBID( war.tongDBID_1 )
					params[ "right" ] = war.tongDBID_2 # ����Ӫ
					params[ "rightTongName" ] = self.getTongNameByDBID( war.tongDBID_2 )
					#params[ "isFinal" ] = False
						
					params[ "warRound" ] = fengHuoLianTianItem.getRound() 
					params[ "cityName" ] = cityName
					#self.joinFHLTPlayers[ ename ] = [ baseMailbox, tongDBID ]
					spaceDomain.onEnterWarSpace( baseMailbox, params )
		elif not islogin:
			baseMailbox.client.onStatusMessage( csstatus.TONG_FENG_HUO_LIAN_TIAN_CLOSE, "" )
		else:
			baseMailbox.logonSpaceInSpaceCopy()

	def closeFengHuoLianTianRooms( self, cityName, camp ):
		"""
		�ر���Ӧ���е�SpaceDomain
		"""
		domains = self.getAllFengHuoLianTianDomain()
		for domain in domains:
			domain.closeFengHuoLianTianRoom( cityName, camp )

	def calCanJoinFHLTTong( self, camp ):
		"""
		��ȡ���������ʸ�
		"""
		self.canJoinFHLTList = self.getTurnWarPointTopTable( camp ) #�ӳ���ս��ȡ�����������ʸ�
		if not self.canJoinFHLTList:
			self.addTimerExtend( TIMER_USER_AGR_JOIN_UP_TIME, 30, 0, self.calCanJoinFHLTTong, [ camp, ] )
			return
		if TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX % 2 != 0:
			ERROR_MSG("TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX % 2 != 0")
			return
		tongmMax = TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX #����������
		choiceList = []
		for i in xrange( FENG_HUO_LIAN_TIAN_TOTAL_ROUNDS ): #ÿ������������
			choiceList.append( tongmMax )
			tongmMax = tongmMax/2
			
		for cityName in self.canJoinFHLTList.keys():
			length = len( self.canJoinFHLTList[ cityName ] )
			choiceIndex = -1
			for i,j in enumerate( choiceList ):
				if length >= j:
					choiceIndex = i #ѡ��ֱ�ӽ���������ĵڼ���
					break
			if choiceIndex != -1 and length > 1:
				self.canJoinFHLTList[ cityName ] = self.canJoinFHLTList[ cityName ][ 0:choiceList[ choiceIndex ] ]#choiceList[ choiceIndex ]ȡ�������ж��ٰ�����
				for tongDBID in self.canJoinFHLTList[ cityName ]:
					#tongCamp = self.getTongCampByDBID( tongDBID )
					self.tongFHLTFightInfos.joinUp( self, cityName, camp, tongDBID) #�����б�
			elif choiceIndex == -1 or length == 1:
				#Ӯȡ���,�����ٲμӱ���
				for tongDBID in self.canJoinFHLTList[ cityName ]:
					self.setJoinCityWarTong( cityName, camp, tongDBID, 0 )
				self.isGetJoinCityWarTongList[ cityName ] = self.canJoinFHLTList[ cityName ]
		
	def setJoinCityWarTong( self, cityName, camp, tongDBID, integral ):
		"""
		���ó�ս������
		�����������ߣ�
		"""
		isFind = False
		d = { "tongDBID":tongDBID, "integral" : integral, "date":int(time.time()) }
		for infos in self.tongFHLTRecords:
			if infos[ "spaceName" ] == cityName:
				infos[ "tongInfos" ].append( d )
				isFind = True
				break
				
		if not isFind:
			self.tongFHLTRecords.append( { "spaceName" : cityName, "tongInfos" : [ d ] } )
			
		self.writeToDB()
		
	def onQueryFHLTVersus( self, cityName, camp, playerBaseMB ):
		# Define method.
		# ��ѯ���ж�ս��Ϣ
		cityKey = ( cityName, camp )
		warCity = self.tongFHLTFightInfos[ cityKey ]
		#master = warCity.getMaster()
		#cityMasterName = self.getTongNameByDBID( master )
		#giveClientData = [cityMasterName]
		giveClientData = []
		maxLength = len( self.canJoinFHLTList[ cityName ] )
		
		for roundWars in warCity.roundItemList:
			length = len( roundWars ) * 2
			matchLevel = 0
			if length >= 4 and maxLength / length >= 1:
				matchLevel = int( math.log( maxLength / length, 2 ) ) + 1
			#matchLevel = csdefine.CITY_WAR_LEVEL_NONE
			#if length > 2:
			#	matchLevel = csdefine.CITY_WAR_LEVEL_QUARTERFINAL
			#elif length <= 2 and length > 1:
			#	matchLevel = csdefine.CITY_WAR_LEVEL_SEMIFINAL
			#elif length == 1:
			#	matchLevel = csdefine.CITY_WAR_LEVEL_FINAL
			#	
			for war in roundWars:
				nameVersus = [ self.getTongNameByDBID( tongDBID ) for tongDBID in war.getTongDBIDs() ]
				winner = self.getTongNameByDBID( war.getWinner() )
				giveClientData.append( {"versus":nameVersus, "winner":winner, "matchLevel": matchLevel } )
		
		playerBaseMB.client.tong_onQueryFHLTTable( giveClientData )

			
	def FHLTSetResult( self, cityName, winner, winnerIntegral, failure, faulureIntegral ):
		camp = self.getTongCampByDBID( winner )
		cityKey = ( cityName, camp )
		self.tongFHLTFightInfos[ cityKey ].setWinner( self, winner, winnerIntegral, failure, faulureIntegral )
		try:
			g_logger.actResultLog( cityName, winner, failure,self.fengHuoLianTiancurrentRound )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		
	def setFHLTJoin( self, cityName, tongNameList ):
		for tongName in tongNameList:
			tongDBID = self.getTongDBIDByName( tongName )
			if tongDBID:
				if self.turnWarPointTopTable.has_key( cityName ) and not tongDBID in self.turnWarPointTopTable[ cityName ]:
					self.turnWarPointTopTable[ cityName ].append( tongDBID )
				elif not self.turnWarPointTopTable.has_key( cityName ):
					self.turnWarPointTopTable[ cityName ] = [ tongDBID ]
		DEBUG_MSG( "fengHuoLianTian setFHLTJoin:cityName is %s,tongNameList is %s."%( cityName, tongNameList ) )
					
	def clearFHLTJoin( self, cityName ):
		self.turnWarPointTopTable[ cityName ] = []
	
	def onTimer( self, timerID, cbID ):
		TimerManager.onTimer( self, timerID, cbID )
	
	