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

TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX = 16				#每个城市可以参加的帮会的最大数量
ENTER_SPACE_PLAYER_LIMIT = 15							#每个帮会允许进入的最大人数
FENG_HUO_LIAN_TIAN_TOTAL_ROUNDS = int( math.log( TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX, 2 ) ) # 城战分多少轮打


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
	帮会夺城战复赛（烽火连天）管理器
	"""
	def __init__( self ):
		"""
		初始化管理器需要的信息
		"""
		TimerManager.__init__( self )
		self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_FREE							#目前所出的比赛阶段
		self.fengHuoLianTianEnter = {}											#用来记录玩家相应的进入信息for example:{tongDBID1:[playerBaseMB1,playerBaseMB2,...],...}
		self.fengHuoLianTian_spaceDomains = {}									# 永久注册接触过的城市战场复赛副本的域, 战争结束时需要通知所有域结束以某城市为争夺的战争
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
		管理器初始化完毕
		"""
		self.tongFengHuoLianTianManager_registerCrond()

	def tongFengHuoLianTianManager_registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"TongFengHuoLianTian_notice_start" : "onTongFengHuoLianTianNoticeStart",			#开始通知
						"TongFengHuoLianTian_notice_end" : "onTongFengHuoLianTianNoticeEnd",					#结束通知
						"TongFengHuoLianTian_start" : "onTongFengHuoLianTianStart",						#开始一场比赛
						"TongFengHuoLianTian_end" : "onTongFengHuoLianTianEnd",							#结束一场比赛
						"TongFengHuoLianTian_all_over" : "onTongFengHuoLianTianAllOver",				#结束整个比赛
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
		活动通知开始
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
		活动通知结束
		"""
		self.fengHuoLianTianCurrentStage = FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE
		INFO_MSG( "TongFengHuoLianTianMgr", "notice end" )
		
	def onTongFengHuoLianTianStart( self ):
		"""
		define method.
		活动开始
		"""
		if self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE:
			curTime = time.localtime()
			ERROR_MSG( "夺城战——烽火连天活动正在进行,%i点%i分试图再次开始夺城战——烽火连天活动副本,目前所处阶段是%s。"%(curTime[3],curTime[4],self.fengHuoLianTianCurrentStage ) )
			return
		#if BigWorld.globalData.has_key( "AS_tongFengHuoLianTianStart" ) and BigWorld.globalData[ "AS_tongFengHuoLianTianStart" ] == True:
		#	curTime = time.localtime()
		#	ERROR_MSG( "夺城战——烽火连天活动正在进行,%i点%i分试图再次开始夺城战——烽火连天活动副本。"%(curTime[3],curTime[4] ) )
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
		活动结束
		"""
		if self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY and self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FINAL:
			ERROR_MSG("夺城战——烽火连天活动,试图提前结束,目前所处阶段是%s"%self.fengHuoLianTianCurrentStage)
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
			ERROR_MSG( "夺城战——烽火连天活动正在进行,%i点%i分试图结束夺城战——烽火连天活动副本,目前所处阶段是%s。"%(curTime[3],curTime[4],self.fengHuoLianTianCurrentStage ) )
			return
		self.resetFengHuoLianTian()
		self.popTimerExtend( TIMER_USER_AGR_TOTAL_TIME )
		self.popTimerExtend( TIMER_USER_AGR_NEXT_ROUND_START )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONG_FENG_HUO_LIAN_TIAN_ALL_OVER, [] )
		DEBUG_MSG( "fengHuoLianTian is all over." )
		self.initCityWarFinalInfos()
		
		
	def onFengHuoLianTianStart( self, matchTime ):
		"""
		由于有多场比赛,每个城市比赛时间结束,因此需要每次开始重新设置,结束的时候删除标记
		"""
		BigWorld.globalData[ "fengHuoLianTianOverTime" ] = time.time() + matchTime * 60
	
	def onTimerCloseFengHuoLianTian( self, re ):
		"""
		"""
		if self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_FREE and self.fengHuoLianTianCurrentStage != FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY_FREE:
			ERROR_MSG("夺城战夺城战——烽火连天活动,试图提前关闭,目前所处阶段是%s"%self.fengHuoLianTianCurrentStage)
			return
		re += 1
		isAllOver = True
		for cityName, roundFights in self.tongFHLTFightInfos.infos.iteritems():
			if re > 3:			#如果3次尝试关闭都失败，那强制关闭这场比赛
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
		玩家请求进入烽火连天副本
		"""
		#首先取出这个城市的排名,如果没有预定的名次多,则取预定名次/2尝试,不行的话再除以2,直到最后只有一个帮会或者没有帮会。
		#判断这个城市该帮会能否参加比赛,不能参加,提示帮会玩家。如果能进入,将帮会的信息加入能够参加比赛列表。
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
		战争相关统一系统通报 向指定帮会通报
		"""
		args = "" if args == () else str( args )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, args )
	
	def registerFengHuoLianTianDomain( self, domain ):
		"""
		永久注册接触过的城市战场副本的域, 战争结束时需要通知所有域结束以某城市为争夺的战争
		"""
		self.fengHuoLianTian_spaceDomains[ domain.id ] = domain

	def isRegisterFengHuoLianTianDomain( self, domainID ):
		"""
		是否注册过此domain
		"""
		return domainID in self.fengHuoLianTian_spaceDomains

	def getAllFengHuoLianTianDomain( self ):
		"""
		获取所有战场domain
		"""
		return self.fengHuoLianTian_spaceDomains.values()

	def onFengHuoLianTianAllMessage( self, isAll, statusID, *args ):
		"""
		战争相关统一系统通报 向所有战争帮会通报
		@param isAll:是否对所有帮会 不管他是否已经提前结束战争了的帮会发送信息
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
		# 传送一个entity到指定的space中
		DEBUG_MSG( "params=",  params )
		# 注册接触过的战场domain
		if not self.isRegisterFengHuoLianTianDomain( spaceDomain.id ):
			self.registerFengHuoLianTianDomain( spaceDomain )

		islogin = params.has_key( "login" )
		tongDBID = params[ "tongDBID" ]
		ename = params[ "ename" ]
		
		if self.fengHuoLianTianCurrentStage >= FENG_HUO_LIAN_TIAN_STAGE_UNDERWAY:
			if len( self.fengHuoLianTianEnter ) >= ENTER_SPACE_PLAYER_LIMIT: # 该帮会进入人数已经满
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
					params[ "left" ] = war.tongDBID_1  # 左阵营
					params[ "leftTongName" ] = self.getTongNameByDBID( war.tongDBID_1 )
					params[ "right" ] = war.tongDBID_2 # 右阵营
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
		关闭相应城市的SpaceDomain
		"""
		domains = self.getAllFengHuoLianTianDomain()
		for domain in domains:
			domain.closeFengHuoLianTianRoom( cityName, camp )

	def calCanJoinFHLTTong( self, camp ):
		"""
		获取烽火连天的资格
		"""
		self.canJoinFHLTList = self.getTurnWarPointTopTable( camp ) #从车轮战获取烽火连天参与资格
		if not self.canJoinFHLTList:
			self.addTimerExtend( TIMER_USER_AGR_JOIN_UP_TIME, 30, 0, self.calCanJoinFHLTTong, [ camp, ] )
			return
		if TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX % 2 != 0:
			ERROR_MSG("TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX % 2 != 0")
			return
		tongmMax = TONG_FENG_HUO_LIAN_TIAN_JOIN_TONG_MAX #最大帮会参与数
		choiceList = []
		for i in xrange( FENG_HUO_LIAN_TIAN_TOTAL_ROUNDS ): #每轮最大参与数量
			choiceList.append( tongmMax )
			tongmMax = tongmMax/2
			
		for cityName in self.canJoinFHLTList.keys():
			length = len( self.canJoinFHLTList[ cityName ] )
			choiceIndex = -1
			for i,j in enumerate( choiceList ):
				if length >= j:
					choiceIndex = i #选择直接进入烽火连天的第几轮
					break
			if choiceIndex != -1 and length > 1:
				self.canJoinFHLTList[ cityName ] = self.canJoinFHLTList[ cityName ][ 0:choiceList[ choiceIndex ] ]#choiceList[ choiceIndex ]取出本轮有多少帮会参与
				for tongDBID in self.canJoinFHLTList[ cityName ]:
					#tongCamp = self.getTongCampByDBID( tongDBID )
					self.tongFHLTFightInfos.joinUp( self, cityName, camp, tongDBID) #加入列表
			elif choiceIndex == -1 or length == 1:
				#赢取帮会,不用再参加比赛
				for tongDBID in self.canJoinFHLTList[ cityName ]:
					self.setJoinCityWarTong( cityName, camp, tongDBID, 0 )
				self.isGetJoinCityWarTongList[ cityName ] = self.canJoinFHLTList[ cityName ]
		
	def setJoinCityWarTong( self, cityName, camp, tongDBID, integral ):
		"""
		设置城战参与者
		（决赛参与者）
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
		# 查询城市对战信息
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
	
	