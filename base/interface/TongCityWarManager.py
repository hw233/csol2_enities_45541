# -*- coding: gb18030 -*-
#
# $Id: TongCityWarManager.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

import time
import random
import copy
import cPickle

import BigWorld
import ShareTexts as ST
import csdefine
import csstatus
import csconst
import Function
import Love3
import cschannel_msgs
from bwdebug import *
from MsgLogger import g_logger
from Function import Functor
from ObjectScripts.GameObject import GameObject
from ObjectScripts.GameObjectFactory import g_objFactory
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from items.ItemDataList import ItemDataList
g_items = ItemDataList.instance()


CONST_CITY_GET_SIGN_CLEAR_TIME 			= 24 			# 城市NPC领取记录清除时间
SIGN_UP_TONG_LIMIT						= 8				# 每一城市允许的报名帮会数量

# 战争结果定义
WAR_RESULT_NONE = -1
WAR_RESULT_WINNER = 1
WAR_RESULT_LOSER = 0

FINAL_TONG_COUNT = 2					# 进入决赛帮会数目

PRE_WAR_ENTER_SPACE_PLAYER_LIMIT = 15	# 城战预赛，进入战场的帮会成员个数限制
FINAL_WAR_RIGHT_PLAYER_LIMIT = 20	# 城战决赛，进入战场的守方帮会成员个数限制
FINAL_WAR_HAS_MAYOR_LEFT_PLAYER_LIMIT = 15	# 有原城主，城战决赛，攻方进入战场的进攻方帮会成员个数限制
FINAL_WAR_NO_MAYOR_LEFT_PLAYER_LIMIT	= 20	# 没原城主的城战决赛，攻方进入战场的人数限制

# 定时器进行次数
SINGUP_NOTIFY_WILL_NUM 	= 4
SINGUP_NOTIFY_NUM 		= 3
NOTIFY_WAR_START_NUM 	= 2

# time user arg
TIME_USER_ARG_NOTIFY_WILL_SIGNUP  		= 1
TIME_USER_ARG_NOTIFY_SIGNUP 			= 2
TIME_USER_ARG_NOTIFY_WAR_START			= 3
TIME_USER_ARG_NOTIFY_FINAL_RESULT		= 4
TIME_USER_ARG_WAR_END_BE_30				= 5
TIME_USER_ARG_SIGNUP_PROGRESS			= 6
TIME_USER_ARG_CLOSE_WAR_PROGRESS		= 7
TIME_USER_ARG_PRE_WAR					= 8 # 预赛 
TIME_USER_ARG_FINAL_WAR					= 9 # 决赛

# time define 
TIME_NOTIFY_WILL_SIGNUP = 15
TIME_NOTIFY_SIGNUP		= 5
TIME_NOTIFY_WAR_START	= 1
TIME_WAR_PRE			= 20			# 预赛时间
TIME_WAR_FINAL			= 30 			# 决赛时间

# 某阶段一共用多少时间
TIME_NOTIFY_WILL_SIGNUP_LONG		= TIME_NOTIFY_WILL_SIGNUP * SINGUP_NOTIFY_WILL_NUM
TIME_NOTIFY_SIGNUP_LONG				= TIME_NOTIFY_SIGNUP * SINGUP_NOTIFY_NUM
TIME_NOTIFY_WAR_START_LONG			= TIME_NOTIFY_WAR_START * NOTIFY_WAR_START_NUM

# city war stage
CITY_WAR_STAGE_FREE 			= 0
CITY_WAR_STAGE_NOTIFY			= 1
CITY_WAR_STAGE_SIGNUP 			= 2
CITY_WAR_STAGE_UNDERWAY			= 3
CITY_WAR_STAGE_UNDERWAY_FINAL 	= 4
CITY_WAR_STAGE_UNDERWAY_FREE	= 5

# enter num
CITY_WAR_MAX_ENTER = 15
CITY_WAR_FINAL_MAX_ENTER_HAS_MASTER = 15
CITY_WAR_FINAL_MAX_ENTER_NOT_MASTER = 20
CITY_WAR_FINAL_MAX_ENTER_MASTER		= 20

JOIN_REWAR_ITEMS = [ 60101264, 60101251 ]

class TimeControl:
	def __init__( self ):
		self.timerExRecord = {}
		self.timerExRepeat = {}
		self.timerExRecordID = {}
	
	def addTimerEx( self, key, time, func, args ):
		timerID = self.addTimer( time, 0, key )
		self.timerExRecord[ key ] = [ func, args, 0, False ]
		self.timerExRecordID[ key ] = timerID
		
	def addtimerExRepeat( self, key, time, repeatTime, repeat, func, args ):
		self.addTimer( time, repeatTime, key )
		self.timerExRecord[ key ] = [ func, args, repeat, False ]
	
	def popTimerEx( self, key ):
		if self.timerExRecord.has_key( key ):
			self.timerExRecord[ key ][ 3 ] = True
		
		if self.timerExRecordID.has_key( key ):
			self.delTimer( self.timerExRecordID[ key ] )
			
	def onTimer( self, tid, key ):
		if self.timerExRecord.has_key( key ):
			func = self.timerExRecord[ key ][ 0 ]
			args = copy.deepcopy( self.timerExRecord[ key ][ 1 ] )
			repeat = self.timerExRecord[ key ][ 2 ]
			isDel = self.timerExRecord[ key ][ 3 ]
			if isDel:
				self.delTimer( tid )
				self.timerExRecord.pop( key )
				return
				
			if repeat:
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

class TongCityWarManager( TimeControl ):
	def __init__( self ):
		TimeControl.__init__( self )
		self.cityWarCurrentStage = CITY_WAR_STAGE_FREE
		self.cityWarTmpData = {}									# 城市战的临时数据缓冲
		self.cwar_spaceDomains = {}									# 永久注册接触过的城市战场副本的域， 战争结束时需要通知所有域结束以某城市为争夺的战争
		self.cityWarStarTime = 0
		
		# 城战管理器是否在报名处理中，如果帮会申请城战时在报名处理中，那么暂时把报名数据放入缓冲区，等处理完上一个报名再接着处理此次申请。
		# 如此让报名顺序进行，避免报名时的数据异步处理造成报名数超过限制个数的问题。
		self.signUpProgressTong = None
		self.cityWarSignUpBuffer = []		# array of (tongDBID, memberDBID, replevel, repMoney, spaceName, playerBase)
		self.cityWarEnter = {} 				# { 帮会ID：人数 }
		self.joinActivityPlayers = {}
		for cityName in csconst.TONG_CITYWAR_CITY_MAPS.iterkeys():
			self.tongCityWarFightInfos.addCity( cityName )
				
		self.cityWarReset()
	def onManagerInitOver( self ):
		"""
		virtual method.
		管理器初始化完毕
		"""
		self.tongCityWarManager_registerCrond()		

	def tongCityWarManager_registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
					  	"TongCityWarManager_start" 					: "onTongCityWarStart", 					# 城战开始
					  	"TongCityWarManager_end" 					: "onTongCityWarEnd", 						# 城战结束，决赛和预赛都使用同样的入口
					  	"TongCityWarFinal_start"					: "onTongCityWarFinalStart",				# 城战决赛开始
					  	"TongCityWarFinal_end"						: "onTongCityWarEnd",						# 城战结束，决赛和预赛都使用同样的入口
					  	"TongCityWarManager_signup_start" 			: "onTongCityWarSignUpStart", 				# 报名开始
					  	"TongCityWarManager_signup_end" 			: "onTongCityWarSignUpEnd", 				# 报名结束
					  	"TongCityWarManager_signupNotify" 			: "onCityWarWillSignUpNotify",			 	# 战争可参加报名通报
					  	"TongCityWarManager_calcCityRevenue"		: "onCalcAllCityRevenue",					# 计算城市消费税
					  	"TongCityWarManager_final_startNotify"		: "onCityWarFinalStartNotify",				# 决赛10分钟前开始的通知
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )

	def onCityWarWillSignUpNotify( self ):
		# define method.
		# 开启城战可报名通告
		self.tongChiefRewardRecords = []
		self.cityWarStarTime = time.time()
		self.onTimerCityWarWillSignUp()
	
	def onCityWarFinalStartNotify( self ):
		# define method.
		# 决赛10分钟后开始的通知
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_FINAL_START_NOTIFY, [] )

	def onTongEntityLoadMemberInfoComplete( self, tongDBID, tongEntity, chiefName ):
		"""
		virtual method.
		帮会实体加载完成员数据了
		"""
		for info in self.tongCityWarFightInfos.infos.itervalues():
			if self.hasTongEntity( info.master ):
				self.registerToCityManager( info.master, info.getCityName(), True )
			
	def cityWarReset( self ):
		self.cityWarTmpData[ "tong_war_data" ] = {}					# 战争中各帮会的战争数据 里面包括 敌对帮会关系 和 自身为守方或攻方标志 以及其他战争需要的
		self.cityWarTmpData[ "getItem_record" ] = {}				# 领取经验果实记录
		self.cityWarTmpData[ "getSkill_record" ] = {}				# 领取技能记录
		
		self.signUpProgressTong = None
		
		self.cityWarSignUpBuffer = []		# array of (tongDBID, memberDBID, replevel, repMoney, spaceName, playerBase)
		self.tongCityWarFightInfos.reset()
		self.cityWarCurrentStage = CITY_WAR_STAGE_FREE
				
	def registerCityWarDomain( self, domain ):
		"""
		永久注册接触过的城市战场副本的域， 战争结束时需要通知所有域结束以某城市为争夺的战争
		"""
		self.cwar_spaceDomains[ domain.id ] = domain

	def isRegisterCityWarDomain( self, domainID ):
		"""
		是否注册过此domain
		"""
		return domainID in self.cwar_spaceDomains

	def onTakeCityRevenue( self, city, money ):
		"""
		define method.
		收取城市消费税
		"""
		DEBUG_MSG("recv Revenue:", city, money)
		for info in self.cityRevenue:
			if info[ "spaceName" ] == city:
				info[ "todayRevenue" ] += money
				try:
					tongDBID = self.getCityMasterTongDBID( city )
					item = self._tongBaseDatas.get( tongDBID )
					if item:
						tongName = item[ "tongName" ]
						g_logger.tongReceiveRevenueLog( tongDBID, tongName, city, money )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				return

	def onRequestSetCityRevenueRate( self, playerBase, tongDBID, cityName ):
		"""
		define method.
		申请修改城市消费税率
		"""
		for info in self.cityRevenue:
			if info[ "spaceName" ] == cityName:
				playerBase.client.tong_onRequestSetCityRevenueRate( info[ "revenueRate" ] )
				return

		playerBase.client.tong_onRequestSetCityRevenueRate( 0 )

	def onSetCityRevenueRate( self, playerBase, playerName, tongDBID, cityName, rate ):
		"""
		define method.
		修改城市消费税率
		"""
		if rate < 0:
			rate = 0
		elif rate > 50:
			rate = 50

		day = time.localtime()[6]
		for info in self.cityRevenue:
			if info[ "spaceName" ] == cityName:
				if info[ "modifyRevenueDay" ] != day:
					info[ "revenueRate" ] = rate
					BigWorld.globalData[cityName + ".revenueRate"] = rate
					playerBase.cell.tong_onSetCityRevenueRateSuccessfully( cityName, rate )
					Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONGCITYWAR_VOICE_2 % ( playerName, csconst.TONG_CITYWAR_CITY_MAPS[cityName], rate ), [] )
				else:
					self.statusMessage( playerBase, csstatus.TONG_CITY_REVENUE_NO )
				return

		self.writeToDB()

	def updateNewCityRevenueInfo( self, cityName ):
		"""
		更新新城市消费税信息
		"""
		for info in self.cityRevenue:
			if info[ "spaceName" ] == cityName:
				#info[ "todayRevenue" ] = 0
				#info[ "yesterdayRevenue" ] = 0
				info[ "getWeek" ] = 0
				#info[ "revenueRate" ] = 10
				info[ "modifyRevenueDay" ] = 10
				return

		info = { "spaceName" : cityName,  "todayRevenue" : 0,  \
				"yesterdayRevenue" : 0, "getWeek" : 0, "revenueRate" : 10, "modifyRevenueDay" : 10 }

		self.cityRevenue.append( info )
		BigWorld.globalData[cityName + ".revenueRate"] = 10

	def onInitAllCityRevenueRate( self ):
		"""
		服务器启动时初始化所有的消费税
		"""
		for info in self.cityRevenue:
			BigWorld.globalData[info[ "spaceName" ] + ".revenueRate"] = info[ "revenueRate" ]

	def onCalcAllCityRevenue( self ):
		"""
		define method.
		计算所有城市消费税
		"""
		for info in self.cityRevenue:
			info[ "yesterdayRevenue" ] = info[ "todayRevenue" ]
			info[ "todayRevenue" ] = 0
			DEBUG_MSG( "calc cityRevenue:%s--%d" % ( info[ "spaceName" ], info[ "yesterdayRevenue" ] ) )

		self.writeToDB()

	def onViewCityRevenue( self, playerBase, tongDBID, city, npcID ):
		"""
		define method.
		查看城市税收
		"""
		DEBUG_MSG( "view Revenue:", playerBase, city, npcID )
		if tongDBID <= 0 or tongDBID != self.getCityMasterTongDBID( city ):
			playerBase.client.onSetGossipText( cschannel_msgs.TONGCITYWAR_VOICE_3)
			playerBase.client.onGossipComplete( npcID )
			return

		isfind = False
		for info in self.cityRevenue:
			if info[ "spaceName" ] == city:
				playerBase.client.onSetGossipText( cschannel_msgs.TONGCITYWAR_VOICE_4 % Function.switchMoney( info[ "yesterdayRevenue" ] ) )
				isfind = True
				break

		if not isfind:
			playerBase.client.onSetGossipText( cschannel_msgs.TONGCITYWAR_VOICE_5)
		playerBase.client.onGossipComplete( npcID )

	def onGetCityTongRevenue( self, city, playerDBID, tongDBID, playerBase ):
		"""
		define method.
		领取城市税收
		"""
		if tongDBID <= 0 or tongDBID != self.getCityMasterTongDBID( city ):
			self.statusMessage( playerBase, csstatus.TONG_GET_CITY_REVENUE_GRADE_VALID )
			return

		tongEntity = self.findTong( tongDBID )
		tongEntity.onGetCityTongRevenue( playerDBID )
	
	def getCityTongChiefReward( self, tongIDBID, chiefMailBox ):
		# define method
		# 帮主领取奖励
		if tongIDBID in self.tongChiefRewardRecords:
			chiefMailBox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CHIEF_REWARD_ALREADY, "" )
			return 
		
		cityName = self.tongCityWarFightInfos.getJoinCityName( tongIDBID )
		if cityName == "":
			chiefMailBox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CHIEF_NOT_JOIN, "" )
			return
			
		winNum = self.tongCityWarFightInfos[ cityName ].getTongWinNum( tongIDBID )
		chiefMailBox.cell.tong_cityWarGetChiefReward( self.tongCityWarFightInfos[ cityName ].getMaster() == tongIDBID, winNum )
	
	def onGetCityTongChiefRewardSuccess( self, tongIDBID ):
		# define method
		# 帮主领取奖励成功
		self.tongChiefRewardRecords.append( tongIDBID )
				
	def getCityTongItem( self, playerDBID, playerTongDBID, playerBaseMB, cityName ):
		# define method.
		# 领取城市占领帮会的经验果实
		if not self.tongCityWarFightInfos[ cityName ].isMaster( playerTongDBID ):
			playerBaseMB.client.onStatusMessage( csstatus.TONG_JYGS_ITEM_GET_INVALIDE, "" )
			return

		t = time.localtime()
		if playerDBID in self.cityWarTmpData[ "getItem_record" ]:
			if self.cityWarTmpData[ "getItem_record" ][ playerDBID ] == t[0] + t[1] + t[2]:
				playerBaseMB.client.onStatusMessage( csstatus.TONG_JYGS_ITEM_GET_OVER, "" )
				return

		playerBaseMB.cell.tong_getCityTongItem()

	def onGetCityTongItemSuccess( self, playerDBID ):
		# define method.
		# 领取城市占领帮会的经验果实成功回调
		t = time.localtime()
		self.cityWarTmpData[ "getItem_record" ][ playerDBID ] = t[0] + t[1] + t[2]
	
	def cityWarIntegralReward( self, tongDBID, integral ):
		# define method.
		# 决赛积分兑换帮会资金
		if self._tongEntitys.has_key( tongDBID ):
			self._tongEntitys[ tongDBID ].onCityWarIntegralRewar( integral )

	def getCityTongSkill( self, playerDBID, playerTongDBID, playerBaseMB, spaceName ):
		# define method.
		# 领取城市占领帮会的技能
		if playerTongDBID == 0 or playerTongDBID != self.getCityMasterTongDBID( spaceName ):
			playerBaseMB.client.onStatusMessage( csstatus.TONG_CITY_SKILL_GET_NONE, "" )
			return

		t = time.localtime()
		if playerDBID in self.cityWarTmpData[ "getSkill_record" ]:
			if self.cityWarTmpData[ "getSkill_record" ][ playerDBID ] == t[0] + t[1] + t[2]:
				playerBaseMB.client.onStatusMessage( csstatus.TONG_CITY_SKILL_GET_OVER, "" )
				return

		playerBaseMB.cell.spellTarget( 730019001, playerBaseMB.id )
		self.cityWarTmpData[ "getSkill_record" ][ playerDBID ] = t[0] + t[1] + t[2]

	def getAllCityWarDomain( self ):
		"""
		获取所有战场domain
		"""
		return self.cwar_spaceDomains.values()
		
	def onLoadAllTongOver( self ):
		#virtual method.
		#所有帮会加载完毕.
		pass
		
	def getCityMasterTongDBID( self, cityName ):
		"""
		获取某个城市的主人 帮会DBID
		"""
		return self.tongCityWarFightInfos[ cityName ].getMaster()

	def onTongDismiss( self, tongDBID ):
		"""
		有帮会解散了，清理城战中此帮会的相关数据
		
		@param tongDBID : 解散帮会的dbid
		@type tongDBID : DATABASE_ID
		"""
		self.tongCityWarFightInfos.onTongDismiss( tongDBID, self.cityWarCurrentStage == CITY_WAR_STAGE_UNDERWAY or self.cityWarCurrentStage == CITY_WAR_STAGE_UNDERWAY_FINAL )

	def updateTongChiefName( self, tongDBID ):
		"""
		帮主更换
		"""
		self.findTong( tongDBID ).queryTongChiefInfos()  # 更换城主雕像

	def cityWarQueryIsCanSignUp( self, playerBase, tongDBID, tonglevel, repMoney, cityName ):
		# define method.
		# 申请城市战，检查条件
		if self.cityWarCurrentStage != CITY_WAR_STAGE_SIGNUP:
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_NOT_SIGN_UP_TIME )
			return
			
		if self.tongCityWarFightInfos.isMaster( tongDBID ):# 已占领了一个城市
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_EXIST_INVALID )
			return
		
		otherSinUpCity = self.tongCityWarFightInfos.isSignUp( tongDBID )
		if otherSinUpCity:# 已经报名
			if otherSinUpCity == cityName: # 已经同报同一城市
				self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_HAS_INVALID )
			else:
				self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_SINUP_OTHER )
			return
		
		playerBase.client.tong_onQueryContest( tonglevel, repMoney )	
	
	def requestContestCityWar( self, playerBase, tongDBID, memberDBID, replevel, repMoney, cityName ):
		"""
		define mothod.
		玩家申请争夺城市 (申请竞拍)，检查帮会条件，
		@param replevel		: 帮会级别需求
		@param cityName	: 申请争夺的城市地图名称
		"""
		DEBUG_MSG( "tongDBID=%i, memberDBID=%i, cityName=%s" % ( tongDBID, memberDBID, cityName ) )
		if self.cityWarCurrentStage != CITY_WAR_STAGE_SIGNUP:
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_NOT_SIGN_UP_TIME )
			return
			
		if self.tongCityWarFightInfos.isMaster( tongDBID ):# 已占领了一个城市
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_EXIST_INVALID )
			return
		
		otherSinUpCity = self.tongCityWarFightInfos.isSignUp( tongDBID )
		if otherSinUpCity:# 已经报名
			if otherSinUpCity == cityName: # 已经同报同一城市
				self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_HAS_INVALID )
			else:
				self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_SINUP_OTHER )
			return
			
		self.cityWarSignUpBuffer.append( ( tongDBID, memberDBID, replevel, repMoney, cityName, playerBase ) )	# 把申请放入缓存
		self.signUpProgress()
		
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_TONG_DUO_CHENG, csdefine.ACTIVITY_JOIN_TONG, tongDBID, self.getTongNameByDBID( tongDBID ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		
	def signUpProgress( self ):
		# self.cityWarSignUpBuffer : array of (tongDBID, memberDBID, replevel, repMoney, cityName, playerBase)
		#处理报名事务，须保证有报名数据
		if not len( self.cityWarSignUpBuffer ):
			return			
		if self.cityWarCurrentStage != CITY_WAR_STAGE_SIGNUP: # 当前不能报名
			return
						
		info = self.cityWarSignUpBuffer.pop( 0 )
		tongDBID = info[0]
		cityName = info[4]
		playerBase = info[5]
		# 已经报名
		if self.tongCityWarFightInfos.isSignUp( tongDBID ): # 已经报名
			DEBUG_MSG( "tong( %i ) had been signed up." % ( tongDBID ) )
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_HAS_INVALID )
			self.signUpProgress()	# 处理下一个报名
			return
		if self.tongCityWarFightInfos.isFull( cityName ):
			DEBUG_MSG( "%s 报名帮会个数达到上限。" % cityName )
			self.statusMessage( playerBase, csstatus.TONG_CITY_WAR_SIGN_UP_FULL )
			self.signUpProgress()	# 处理下一个报名
			return
			
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			memberDBID = info[1]
			replevel = info[2]
			repMoney = info[3]
			self.signUpProgressTong = ( tongDBID, cityName )
			tongEntity.onContestCityWar( memberDBID, replevel, repMoney, cityName )
			self.addTimerEx( TIME_USER_ARG_SIGNUP_PROGRESS, 1, self.signUpProgress, [] )
			
	def onSignUpCityWarResult( self, tongDBID, succeeded ):
		"""
		define mothod.
		帮会报名城战的结果返回
		"""
		DEBUG_MSG( "sign up result", tongDBID, succeeded )
		if succeeded:	# 报名成功
			self.tongCityWarFightInfos.signUp( self, self.signUpProgressTong[ 1 ], self.signUpProgressTong[ 0 ] )
			
		self.signUpProgressTong = None
		self.signUpProgress()
		
	def onQueryCityTong( self, city, playerBaseMB ):
		"""
		define method.
		查询被占领城市英雄榜
		@param city: 城市的fengming 名称
		@param playerBaseMB:玩家的basemailbox
		"""
		for infos in self.tongCityRecords:
			if infos[ "spaceName" ] == city:
				if len( infos[ "tongInfos" ] ) <= 0:
					break
				for idx, info in enumerate( infos[ "tongInfos" ] ):
					playerBaseMB.client.tong_onQueryCityTongMasters( idx, info[ "tongName" ], info[ "date" ], info[ "chiefName" ] )
				playerBaseMB.client.tong_onQueryCityChanged( city )
				tongDBID = self.getCityMasterTongDBID( city )
				tongName = self.getTongNameByDBID( tongDBID )
				playerBaseMB.client.tong_onQueryCurMaster( tongName )
				return

		playerBaseMB.client.onStatusMessage( csstatus.TONG_QUERY_HOLD_CITY_NONE, "" )

	def onQeryCityWarVersus( self, cityName, playerBaseMB ):
		# Define method.
		# 查询城市对战信息
		warCity = self.tongCityWarFightInfos[ cityName ]
		master = warCity.getMaster()
		cityMasterName = self.getTongNameByDBID( master )
		giveClientData = [cityMasterName]
		
		for roundWars in warCity.roundItemList:
			length = len( roundWars )
			matchLevel = csdefine.CITY_WAR_LEVEL_NONE
			if length > 2:
				matchLevel = csdefine.CITY_WAR_LEVEL_QUARTERFINAL
			elif length <= 2 and length > 1:
				matchLevel = csdefine.CITY_WAR_LEVEL_SEMIFINAL
			elif length == 1:
				matchLevel = csdefine.CITY_WAR_LEVEL_FINAL
				
			for war in roundWars:
				nameVersus = [ self.getTongNameByDBID( tongDBID ) for tongDBID in war.getTongDBIDs() ]
				winner = self.getTongNameByDBID( war.getWinner() )
				giveClientData.append( {"versus":nameVersus, "winner":winner, "matchLevel": matchLevel } )
		
		playerBaseMB.client.tong_onQueryCityWarTable( giveClientData )
		
	def onQueryCurMasterByCityName( self, cityName, playerBaseMB ):
		"""
		查询城市当前的占领者
		"""
		warCity = self.tongCityWarFightInfos[ cityName ]
		master = warCity.getMaster()
		cityMasterName = self.getTongNameByDBID( master )
		playerBaseMB.client.tong_onReceiveCurMaster( cityMasterName )
		
	def onRoleSelectEnterWar( self, playerTongDBID, playerBaseMB ):
		# define mothod.
		# 玩家申请进入战场，告诉玩家要进入的地图
		if self.cityWarCurrentStage < CITY_WAR_STAGE_UNDERWAY:
			playerBaseMB.client.onStatusMessage( csstatus.TONG_CITY_WAR_NO_WAR, "" )
			return
			
		cityName = self.tongCityWarFightInfos.getJoinCityName( playerTongDBID )
		if not cityName:
			self.statusMessage( playerBaseMB, csstatus.TONG_CITY_WAR_CANNOT_ENTER )
			return 
		
		if not self.tongCityWarFightInfos[ cityName ].checkTongHasWar( playerTongDBID ):
			self.statusMessage( playerBaseMB, csstatus.TONG_CITY_WAR_CANNOT_ENTER )
			return
		
		if self.tongCityWarFightInfos[ cityName ].isWinner( playerTongDBID ):
			self.statusMessage( playerBaseMB, csstatus.TONG_CITY_WAR_IS_WIN )
			return

		if self.cityWarCurrentStage < CITY_WAR_STAGE_UNDERWAY:
			baseMailbox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CLOSE, "" )
			return
		
		spaceKey = self.tongCityWarFightInfos[ cityName ].getSpaceKey( playerTongDBID )
		playerBaseMB.cell.tong_gotoCityWar( spaceKey )

	def rewardJoin( self ):
		# 给所有参与玩家参与奖励
		mailMgr = BigWorld.globalData[ "MailMgr" ]
		itemDatas = []
		for itemID in JOIN_REWAR_ITEMS:
			item = g_items.createDynamicItem( itemID )
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 0 )
			itemDatas.append( itemData )
		
		for ename, inf in self.joinActivityPlayers.iteritems():
			mailMgr.sendWithMailbox( 
				None, \
				inf[ 0 ], \
				ename, \
				csdefine.MAIL_TYPE_QUICK, \
				csdefine.MAIL_SENDER_TYPE_NPC, \
				cschannel_msgs.TONGCITYWAR_MAIL_MAIL_SEND_NAME, \
				cschannel_msgs.TONGCITYWAR_MAIL_TITILE, \
				"", \
				0, \
				itemDatas\
			)
			
		self.joinActivityPlayers = {}
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_NOTIFY_END, [] )
	# -----------------------------------------------------
	# callback
	# -----------------------------------------------------
	def onEnterCityWarSpace( self, spaceDomain, baseMailbox, params ):
		# define method.
		# 传送一个entity到指定的space中
		DEBUG_MSG( "params=",  params )
		# 注册接触过的战场domain
		if not self.isRegisterCityWarDomain( spaceDomain.id ):
			self.registerCityWarDomain( spaceDomain )

		islogin = params.has_key( "login" )
		tongDBID = params[ "tongDBID" ]
		ename = params[ "ename" ]
		
		if self.cityWarCurrentStage >= CITY_WAR_STAGE_UNDERWAY:
			if self.cityWarCheckFull( tongDBID ): # 该帮会进入人数已经满
				if islogin:
					baseMailbox.logonSpaceInSpaceCopy()
					return
					
				baseMailbox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CANT_ENTER_PLAYER_LIMIT, "" )
			else:
				cityName = self.tongCityWarFightInfos.getJoinCityName( tongDBID )
				if cityName:
					cityWarItem = self.tongCityWarFightInfos[ cityName ]
					params[ "spaceKey" ] = cityWarItem.getSpaceItemKey( tongDBID )
					war = cityWarItem.searchWar( tongDBID )
					params[ "left" ] = war.tongDBID_1  # 左阵营
					params[ "leftTongName" ] = self.getTongNameByDBID( war.tongDBID_1 )
					params[ "right" ] = war.tongDBID_2 # 右阵营
					params[ "rightTongName" ] = self.getTongNameByDBID( war.tongDBID_2 )
					if self.tongCityWarFightInfos[ cityName ].isFinal() and cityWarItem.getMaster() :
						params[ "defend" ] = cityWarItem.getMaster()  # 防守
						params[ "defendTongName" ] = self.getTongNameByDBID( cityWarItem.getMaster() )
						params[ "occupyNum" ] = self._getTongOccupyCityNum( cityName, cityWarItem.getMaster() )
					
					if self.cityWarCurrentStage == CITY_WAR_STAGE_UNDERWAY_FINAL:
						params[ "isFinal" ] = True
						starTime = self.cityWarStarTime if self.cityWarStarTime else time.time()
						params[ "finalRewardTime" ] = starTime + csconst.TONG_CITY_WAR_CHAMPION_REWARD_LIVING
					else:
						params[ "isFinal" ] = False
						
					params[ "warRound" ] = cityWarItem.getRound() 
					params[ "cityName" ] = cityName
					self.joinActivityPlayers[ ename ] = [ baseMailbox, tongDBID ]
					spaceDomain.onEnterWarSpace( baseMailbox, params )
		elif not islogin:
			baseMailbox.client.onStatusMessage( csstatus.TONG_CITY_WAR_CLOSE, "" )
		else:
			baseMailbox.logonSpaceInSpaceCopy()
	
	def _getTongOccupyCityNum( self, cityName, tongDBID ):
		# 获取最后几次占领是否为同一城市
		num = 0
		for infos in self.tongCityRecords:
			if infos[ "spaceName" ] == cityName:
				if len( infos[ "tongInfos" ] ) <= 0:
					break
				
				if len( infos[ "tongInfos" ] ) < 2:
					return num
					
				masterInfo_1 = infos[ "tongInfos" ][ -1 ]
				masterInfo_2 = infos[ "tongInfos" ][ -2 ]
				if masterInfo_1[ "tongDBID" ] == tongDBID:
					num += 1
					
				if masterInfo_2[ "tongDBID" ] == tongDBID:
					num += 1
		return num
	
	def onWarMessage( self, tongDBID, statusID, *args ):
		"""
		战争相关统一系统通报 向指定帮会通报
		"""
		args = "" if args == () else str( args )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, args )

	def onWarAllMessage( self, isAll, statusID, *args ):
		"""
		战争相关统一系统通报 向所有战争帮会通报
		@param isAll:是否对所有帮会 不管他是否已经提前结束战争了的帮会发送信息
		"""
		for item in self.tongCityWarFightInfos.infos.itervalues():
			notifyList = []
			if isAll:
				notifyList = item.signUpList
			else:
				notifyList = item.getCurrentTong()
				
			for tongDBID in notifyList:
				self.onWarMessage( tongDBID, statusID, *args )
	
	def onCeaseMatchMessage( self, tongDBIDs ):
		# 通知没有后继比赛的帮会，比赛后领奖励
		for inf in self.joinActivityPlayers.itervalues():
			if inf[ 1 ] in tongDBIDs:
				inf[ 0 ].client.onStatusMessage( csstatus.TONG_CITY_WAR_NOTIFY_JOIN, "" )
			
	def registerToCityManager( self, tongDBID, city, isInit ):
		"""
		将城市控制帮会信息注册到城市管理者
		"""
		# 城市管理者会从这里面取数据， 取到则记录该城市控制帮会
		BigWorld.globalData[ "holdCity.%s" % city ] = ( tongDBID, self.getTongNameByDBID( tongDBID ) )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.setHoldCity( city, isInit )
	
	def onTongCityWarSignUpStart( self ):
		"""
		defined method.
		报名开始
		"""
		DEBUG_MSG( "issue jingpai signup start notify!" )
		if self.cityWarCurrentStage > CITY_WAR_STAGE_SIGNUP:
			return
		self.cityWarReset()
		self.cityWarCurrentStage = CITY_WAR_STAGE_SIGNUP
		self.onTimerCityWarSignUp()
			
	def onTongCityWarSignUpEnd( self ):
		"""
		defined method.
		报名结束
		"""
		self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY_FREE
		DEBUG_MSG( "issue jingpai signup over notify!" )
			
	def onTongCityWarStart( self ):
		# defined method.
		# 帮会城战预赛开始
		if self.cityWarCurrentStage != CITY_WAR_STAGE_UNDERWAY_FREE:
			return
		self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY
		self.tongCityWarFightInfos.startWar( self )
		self.onCityWarStart( TIME_WAR_PRE )
		self.addTimerEx( TIME_USER_ARG_PRE_WAR, TIME_WAR_PRE * 60 , self.onTongCityWarEnd, [] )
		
	def onTongCityWarFinalStart( self ):
		# defined method.
		# 城战决赛开始
		if self.cityWarCurrentStage != CITY_WAR_STAGE_UNDERWAY_FREE:
			return
			
		self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY_FINAL
		self.tongCityWarFightInfos.startFinalWar( self )
		self.onCityWarStart( TIME_WAR_FINAL )
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_START_NOTIFY, [] )
		self.addTimerEx( TIME_USER_ARG_FINAL_WAR, TIME_WAR_FINAL * 60, self.onTongCityWarEnd, [] )
		
	def onCityWarStart( self, protime ):
		"""
		战争开始的处理
		设置timer，设置全局标记，历史原因，决赛与预赛使用同一套timer和globalData全局标记
		"""
		BigWorld.globalData[ "CityWarOverTime" ] = time.time() + protime * 60
		
	def onTongCityWarEnd( self ):
		"""
		defined method.
		结束战争
		"""
		if BigWorld.globalData.has_key( "CityWarOverTime" ):
			del BigWorld.globalData[ "CityWarOverTime" ]
		
		DEBUG_MSG( "tigger citywar over event!" )
		for cityName, item in self.tongCityWarFightInfos.infos.iteritems():
			self.closeCityWarRooms( cityName )
		
		self.addTimerEx( TIME_USER_ARG_CLOSE_WAR_PROGRESS, 0, self.onTimerCloseCityWar, [ 1, ] )
		
		if self.cityWarCurrentStage == CITY_WAR_STAGE_UNDERWAY_FINAL: # 决赛结束
			self.cityWarCurrentStage = CITY_WAR_STAGE_FREE
			self.rewardJoin()
			for tongEntity in self._tongEntitys.itervalues():
				tongEntity.onNotifyTongCityWarEnd()
		else:
			self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY_FREE
		
		self.popTimerEx( TIME_USER_ARG_FINAL_WAR )
		self.popTimerEx( TIME_USER_ARG_PRE_WAR )
		
			
	def onTimerCloseCityWar( self, re ):
		# define method. 
		# cityName: 争夺城市， tongDBID： 获胜帮会
		# 比赛结束，设置本场比赛胜者
		re += 1
		isAllOver = True
		for cityName, roundFights in self.tongCityWarFightInfos.infos.iteritems():
			if re > 3:
				roundFights.onTimerCloseWar( self )
				continue
				
			if not roundFights.isAllWarOver():
				isAllOver = False
		
		if not isAllOver:
			self.addTimerEx( TIME_USER_ARG_CLOSE_WAR_PROGRESS, 0, self.onTimerCloseCityWar, [ re, ] )
		else:
			for fights in self.tongCityWarFightInfos.infos.itervalues():
				fights.initRoundWar( fights.currentRound + 1 )
				
			self.writeToDB()
	
	def closeCityWarRooms( self, cityName ):
		"""
		关闭某个城战的房间
		"""
		domains = self.getAllCityWarDomain()
		for d in domains:
			d.closeCityWarRoom( cityName )
	
	def setCityNewMaster( self, cityName, tongDBID ):
		"""
		设置城市的新主人
		oldCityMasterTongDBID: -1 
			表示不确定是否有原城主，需要这个函数内部处理。
		"""
		t = 0
		oldCityMasterTongDBID = -1
		for infos in self.tongCityRecords:
			if infos[ "spaceName" ] == cityName:
				for info in infos[ "tongInfos" ]:
					if info["date"] > t:
						t = info["date"]
						oldCityMasterTongDBID = info["tongDBID"]

		DEBUG_MSG( "set City master:%s  %i %i" % ( cityName, tongDBID, oldCityMasterTongDBID ) )
		try:
			chiefName = self._tongBaseDatas[ tongDBID ][ "chiefName" ]
		except:
			chiefName = cschannel_msgs.TONGCITYWAR_VOICE_9 % tongDBID
		
		tongName = self.getTongNameByDBID( tongDBID )
		isFind = False
		d = { "tongDBID" : tongDBID, "tongName" : tongName, "chiefName" : chiefName, "date" : int( time.time() ) }
		for infos in self.tongCityRecords:
			if infos[ "spaceName" ] == cityName:
				infos[ "tongInfos" ].append( d )
				isFind = True
				break

		if not isFind:
			self.tongCityRecords.append( { "spaceName" : cityName, "tongInfos" : [ d ] } )
				
		if tongDBID != oldCityMasterTongDBID:
			tongEntity = self.findTong( oldCityMasterTongDBID )
			if tongEntity:
				tongEntity.setHoldCity("", False)

		self.registerToCityManager( tongDBID, cityName, False )
		# 设置城市消费税
		self.updateNewCityRevenueInfo( cityName )
		DEBUG_MSG( "success set to city master[%s] new master[%i]." % ( cityName, tongDBID ) )

		cityNameWord = csconst.TONG_CITYWAR_CITY_MAPS.get( cityName, "test" )
		self.onWarMessage( tongDBID, csstatus.TONG_CITY_WAR_FINAL_WIN, cityNameWord )
		tempString = cschannel_msgs.BCT_CITY_WAR_FINAL_RESULT_NOTIFY % ( tongName, cityNameWord, tongName )
		
		# 请求帮主信息
		self.findTong( tongDBID ).queryTongChiefInfos()
		
		try:
			g_logger.tongCityWarSetMasterLog( tongDBID, tongName, cityName )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
		self.writeToDB()
	
	def cityWarSetResult( self, cityName, winner, failure ):
		# define method.
		# 设置一场比赛的胜利者
		self.tongCityWarFightInfos[ cityName ].setWinner( self, winner, failure )
		g_logger.actResultLog( csdefine.ACTIVITY_TONG_DUO_CHENG, cityName, winner, failure, self.tongCityWarFightInfos[ cityName ].getRound() )
	
	def cityWarCheckFull( self, tongDBID ):
		# 检查该帮会进入人数是否已满
		if self.cityWarEnter.has_key( tongDBID ):
			if self.cityWarCurrentStage != CITY_WAR_STAGE_UNDERWAY_FINAL: # 不是决赛
				return len( self.cityWarEnter ) >= CITY_WAR_MAX_ENTER
			else:
				cityName = self.tongCityWarFightInfos.getJoinCityName( tongDBID )
				if self.tongCityWarFightInfos[ cityName ].getMaster(): # 有城主
					if tongDBID == self.tongCityWarFightInfos[ cityName ].getMaster():
						return len( self.cityWarEnter ) >= CITY_WAR_FINAL_MAX_ENTER_MASTER # 守城方
					else:
						return len( self.cityWarEnter ) >= CITY_WAR_FINAL_MAX_ENTER_HAS_MASTER
				else:
					return len( self.cityWarEnter ) >= CITY_WAR_FINAL_MAX_ENTER_NOT_MASTER
		else:
			return False
	
	def cityWarAddEnter( self, tongDBID, playerDBID ):
		if self.cityWarEnter.has_key( tongDBID ):
			if playerDBID not in self.cityWarEnter[ tongDBID ]:
				self.cityWarEnter[ tongDBID ].append( playerDBID )
		else:
			self.cityWarEnter[ tongDBID ] = [ playerDBID, ]
		
	def cityWarLeave( self, tongDBID, playerDBID ):
		# define method
		# 玩家离开城战
		if self.cityWarEnter.has_key( tongDBID ):
			if playerDBID in self.cityWarEnter[ tongDBID ]:
				self.cityWarEnter[ tongDBID ].remove( playerDBID )
	
	def cityWarOnQueryMasterInfo( self, tongDBID, masterInfo ):
		# define method
		# 回调查询帮主信息
		self.tongCityWarFightInfos.setMasterChiefInfo( tongDBID, masterInfo )
		self.writeToDB()
	
	def cityWarDelMaster( self, cityNameCN ):
		# define method.
		# 删除一个城市的城主 for GM
		cityName = ""
		for key, value in csconst.TONG_CITYWAR_CITY_MAPS.iteritems():
			if cityNameCN == value:
				cityName = key
		
		if self.tongCityWarFightInfos.infos.has_key( cityName ):
			masterDBID = self.tongCityWarFightInfos[ cityName ].getMaster()
			tongMB = self.findTong( masterDBID )
			tongName = self.getTongNameByDBID( masterDBID )
			if tongMB:
				tongMB.setHoldCity("", False)
				tongMB.onStatusMessage( csstatus.TONG_CITY_WAR_ABANDON_HOLD_CITY, str(( cityNameCN, )) )
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_ABANDON_HOLD_CITY%( tongName, cityNameCN ), [] )
			self.tongCityWarFightInfos[ cityName ].delCityMaster()
			self.registerToCityManager( 0, cityName, False )
			self.writeToDB()
	
	def cityWarRegisterMasterSpawnPoint( self, cityName, mailbox ):
		# define method
		# 城主刷新点注册
		if self.tongCityWarFightInfos.infos.has_key( cityName ):
			self.tongCityWarFightInfos[ cityName ].addSpawnMaster( mailbox )
	
	# -----------------------------------------------------
	# time callback
	# -----------------------------------------------------
	def onTimerCityWarWillSignUp( self, notifyTime = TIME_NOTIFY_WILL_SIGNUP_LONG ):
		# 城战将要多少时间后报名通告
		if self.cityWarCurrentStage > CITY_WAR_STAGE_NOTIFY:
			return
			
		self.cityWarCurrentStage = CITY_WAR_STAGE_NOTIFY
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_WILL_SIGNUP_NOTIFY % ( notifyTime, ), [] )
		if notifyTime == 1:
			self.cityWarCurrentStage = CITY_WAR_STAGE_UNDERWAY_FREE
			return
			
		nextTime = notifyTime - TIME_NOTIFY_WILL_SIGNUP
		if nextTime <= 0:
			self.addTimerEx( TIME_USER_ARG_NOTIFY_WILL_SIGNUP, ( TIME_NOTIFY_WILL_SIGNUP -1 ) * 60, self.onTimerCityWarWillSignUp, [ 1, ] )
		else:
			self.addTimerEx( TIME_USER_ARG_NOTIFY_WILL_SIGNUP, TIME_NOTIFY_WILL_SIGNUP * 60, self.onTimerCityWarWillSignUp, [ nextTime, ] )
			
	def onTimerCityWarSignUp( self, notifyTime = TIME_NOTIFY_SIGNUP_LONG ):
		# 报名开始
		if self.cityWarCurrentStage != CITY_WAR_STAGE_SIGNUP:
			return
		
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_CITY_WAR_SIGNUP_NOTIFY % ( notifyTime, ), [] )
		if notifyTime == 1:
			return
		
		nextTime = notifyTime - TIME_NOTIFY_SIGNUP
		if nextTime <= 0:
			self.addTimerEx( TIME_USER_ARG_NOTIFY_SIGNUP, ( TIME_NOTIFY_SIGNUP-1 )*60, self.onTimerCityWarSignUp, [ 1, ] )
		else:
			self.addTimerEx( TIME_USER_ARG_NOTIFY_SIGNUP, TIME_NOTIFY_SIGNUP * 60, self.onTimerCityWarSignUp, [ nextTime, ]  )
	
	def onTimer( self, timerID, cbID ):
		TimeControl.onTimer( self, timerID, cbID )