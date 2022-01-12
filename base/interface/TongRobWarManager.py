# -*- coding: gb18030 -*-
# 帮会掠夺战
# $Id: TongCityWarManager.py,v 1.1 2008-08-25 09:28:44 kebiao Exp $

import time
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import csdefine
import csstatus
import csconst
import random
import Love3
import Const
from bwdebug import *
from Function import Functor
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from MsgLogger import g_logger

CONST_ROB_WAR_TIME 			 		= 19 					# 战争开启时间
REQUEST_OVERDUE_TIME				= 2						# 掠夺战请求过期时间，随意定义的，大概大于两个服务器数据传输时间即可
ROBWAR_FAILURE_PAY_PERCENTAGE		= 0.10					# 帮会掠夺战失败帮会所要支持金钱的比例


class TongRobWarManager:
	def __init__( self ):
		self.robWarTmpData = {}								# 临时数据缓冲
		self.robwar_dataClear_timerID = 0
		self.requestRobTongInfos = {}						# 申请掠夺战的帮会临时数据{(发起帮会dbid,目标帮会dbid):记录时间, ...}
		self.requestRobTongTimer = 0						# 清理申请掠夺战临时数据timer
		self.robWarReset()

	def isInRobWarRequest( self, tongDBID ):
		"""
		是否在帮会掠夺申请中
		"""
		for tongDBIDs in self.requestRobTongInfos:
			if tongDBID in tongDBIDs:
				return True
		return False
		
	def checkRobWarRequest( self ):
		"""
		检查临时掠夺申请数据
		"""
		for tongDBIDs, requestTime in self.requestRobTongInfos.items():
			if time.time() - requestTime > REQUEST_OVERDUE_TIME:
				self.removeRobTongRequest( tongDBIDs[0], tongDBIDs[1] )
				
	def addRequestRobTongInfo( self, srcTongDBID, dstTongDBID ):
		"""
		有新的掠夺战请求
		
		@param srcTongDBID : 发起帮会的dbid
		@param dstTongDBID : 目标帮会的dbid
		"""
		self.requestRobTongInfos[( srcTongDBID, dstTongDBID )] = time.time()
		if not self.requestRobTongTimer:
			self.requestRobTongTimer = self.addTimer( REQUEST_OVERDUE_TIME, REQUEST_OVERDUE_TIME, 0 )
			
	def removeRobTongRequest( self, srcTongDBID, dstTongDBID ):
		"""
		清除一个掠夺战请求
		"""
		try:
			self.requestRobTongInfos.pop( (srcTongDBID, dstTongDBID) )
		except KeyError:
			ERROR_MSG( "there's no request tong: %i and %i" % ( srcTongDBID, dstTongDBID ) )
		if len( self.requestRobTongInfos ) == 0:
			self.delTimer( self.requestRobTongTimer )
			self.requestRobTongTimer = 0
			
	def onManagerInitOver( self ):
		"""
		virtual method.
		管理器初始化完毕
		"""
		# 8小时 查询一次时间
		self.robwar_dataClear_timerID = self.addTimer(  0, 60 * 60 * 8, 0 )
		self.tongRobWarManager_registerCrond()

	def robWarReset( self ):
		"""
		"""
		self.robwar_start_remain30_timerID = 0
		self.robwar_start_timerID = 0
		self.robwar_end30_timerID = 0
		self.robwar_end_timerID = 0
		self.robWarTmpData[ "overTongs" ] = []

	def isRobWarFailure( self, tongDBID ):
		"""
		是否在一个星期内失败过, 因为robWarFailureList周末会清空，因此不必判断时间
		"""
		return tongDBID in self.robWarFailureList

	def hasRobWarLog( self, tongDBID ):
		"""
		是否存在该帮会的战争关系记录
		"""
		for item in self.robWarInfos:
			if tongDBID == item[ "rightTongDBID" ] or tongDBID == item[ "leftTongDBID" ]:
				return True
		return False

	def getRobWarTongEnemyTongDBID( self, tongDBID ):
		"""
		获得某个帮会的敌对帮会
		"""
		for item in self.robWarInfos:
			if tongDBID == item[ "rightTongDBID" ]:
				return item[ "leftTongDBID" ]
			elif tongDBID == item[ "leftTongDBID" ]:
				return item[ "rightTongDBID" ]

		return 0

	def isRobWarRight( self, tongDBID ):
		"""
		是否是被申请战争方
		"""
		for item in self.robWarInfos:
			if tongDBID in item.itervalues():
				if item[ "rightTongDBID" ] == tongDBID:
					return True
				else:
					return False
		return False

	def onRegisterPreMonthRobWarPoint( self ):
		"""
		define method.
		登记上月掠夺战积分
		"""
		tm = time.localtime()

		if self.isRegisterRobWarRecord != tm[1]:
			self.preMonthRobWarTopRecords = self.robWarTopRecords
			self.isRegisterRobWarRecord = tm[1]
			self.robWarTopRecords = {}
			self.robWarGetRewardRecords = []
			self.writeToDB()
			INFO_MSG("Rob war point table update.PreMonth point datas is: ", self.preMonthRobWarTopRecords )

	def queryTongRobWarPoint( self, playerBase, tongDBID, npcID ):
		"""
		define method.
		查询本月掠夺战积分
		"""
		DEBUG_MSG( "view:", playerBase, tongDBID, npcID )
		msg = ""
		datas = sorted(self.preMonthRobWarTopRecords.items(), key=lambda d:d[1])[0:10]
		datas.reverse()
		for item in datas:
			tongName = self.getTongNameByDBID(item[0])
			if tongName == "":
				self.preMonthRobWarTopRecords.pop(item[0])
				continue

			msg += "%s:%i@B" % (tongName, item[1])

		msg += cschannel_msgs.TONG_INFO_19 % self.preMonthRobWarTopRecords.get(tongDBID, 0)
		playerBase.client.onSetGossipText(msg)
		playerBase.client.onGossipComplete( npcID )

	def getTongRobWarPoint( self, playerBase, tongDBID ):
		"""
		define method.
		某帮会帮主获取掠夺战奖励
		"""
		if tongDBID in self.robWarGetRewardRecords:
			self.statusMessage( playerBase, csstatus.TONG_ROB_WAR_REWARD_EXIST )
			return

		datas = sorted(self.preMonthRobWarTopRecords.items(), key=lambda d:d[1])[-3:]
		datas.reverse()
		for idx, item in enumerate(datas):
			if item[0] == tongDBID:
				playerBase.cell.tong_rewardRobWar(idx + 1)
				return

		self.statusMessage( playerBase, csstatus.TONG_ROB_WAR_REWARD_TOP )

	def onRewardRobWarPlayerCB( self, tongDBID, isSuccess ):
		"""
		define method.
		掠夺战奖励给玩家之后是否成功的回调
		"""
		if isSuccess:
			self.robWarGetRewardRecords.append( tongDBID )

	def onRequestRobWar( self, playerBase, playerTongDBID ):
		"""
		define method.
		某帮会玩家申请掠夺战
		"""
		if self.isInRobWarRequest( playerTongDBID ):	# 如果已经在帮会掠夺战申请中，那么忽略本次申请
			return
			
		if self.hasRobWarLog( playerTongDBID ):
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_LOG_EXIST )
			return
		elif self.isRobWarFailure( playerTongDBID ):
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_ISFAILURE )
			return
		elif playerTongDBID in self.tongRequestRecord:
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_HAS_JOIN )
			return
			
		playerBase.client.tong_onRequestRobWar()

	def onAnswerRobWar( self, playerBase, playerDBID, playerTongDBID, targetTongName ):
		"""
		define method.
		客户端确认申请掠夺战目标
		"""
		targetTongDBID = self.getTongDBIDByName( targetTongName )
		if targetTongDBID == 0:
			self.statusMessage( playerBase, csstatus.TONG_TARGET_NOT_EXIST )
			return
		elif targetTongDBID == playerTongDBID:
			self.statusMessage( playerBase, csstatus.TONG_TARGET_INVALID )
			return
		if self.isInRobWarRequest( targetTongDBID ):	# 如果已经在帮会掠夺战申请中，那么忽略本次申请
			return
		elif self.hasRobWarLog( targetTongDBID ):
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_LOG_TARGET_EXIST, targetTongName )
			return
		elif self.isRobWarFailure( targetTongDBID ):
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_TARGET_ISFAILURE )
			return
		elif targetTongDBID not in self.topActivityPointTongDBIDs[0 : Const.TONG_ACTIVITY_POINT_TOP_COUNT]:
			self.statusMessage( playerBase, csstatus.TONG_REQUEST_ROB_WAR_ISFAILURE1 )
			return
		self.addRequestRobTongInfo( playerTongDBID, targetTongDBID )
		
		tongEntity = self.findTong( targetTongDBID )

		if tongEntity:
			tongEntity.onReceiveRequestRobWar( self.findTong( playerTongDBID ), playerDBID, playerBase )
		else:
			cmd = "select sm_level, sm_shenshouType, sm_shenshouReviveTime from tbl_TongEntity where %i = id;" % targetTongDBID
			BigWorld.executeRawDatabaseCommand( cmd, Functor( self.robWarQueryTongLevel_Callback, targetTongName, playerTongDBID, playerDBID ) )

	def robWarQueryTongLevel_Callback( self, targetTongName, playerTongDBID, playerDBID, result, dummy, error ):
		"""
		查询对方帮会级别 数据库回调
		"""
		if (error):
			ERROR_MSG( error )
			return

		tongEntity = self.findTong( playerTongDBID )
		hasShenshou = int( result[0][1] )
		if int( result[0][2] ) > 0:
			hasShenshou = 0
		tongEntity.onAnswerRobWar( playerDBID, targetTongName, int( result[0][0] ), hasShenshou )

	def findRequestRobWar( self, playerBase, targetTongName ):
		"""
		define method.
		玩家查找这个要掠夺的帮会
		"""
		cmd = "select sm_level,sm_shenshouType,id,sm_ssd_level from tbl_TongEntity where sm_playerName = \'%s\';" % BigWorld.escape_string( targetTongName )
		BigWorld.executeRawDatabaseCommand( cmd, Functor( self.findRequestRobWar_Callback, playerBase ) )

	def findRequestRobWar_Callback( self, playerBase, result, dummy, error ):
		"""
		玩家查找这个要掠夺的帮会 数据库回调
		"""
		if (error):
			ERROR_MSG( error )
			return

		if len( result ) <= 0:
			playerBase.client.onfindRequestRobWarCallBack( 0, 0, 0, 0 )

		level = int( result[0][0] )
		shenshouType = int( result[0][1] )
		isRobWarFailure = self.isRobWarFailure( int( result[0][2] ) )
		ssd_level = int( result[0][3] )
		playerBase.client.onfindRequestRobWarCallBack( level, shenshouType, ssd_level, isRobWarFailure )

	def onRequestRobWarSuccessfully( self, playerBase, playerTongDBID, targetTongName ):
		"""
		define method.
		申请掠夺战成功
		"""
		targetTongDBID = self.getTongDBIDByName( targetTongName )
		self.removeRobTongRequest( playerTongDBID, targetTongDBID )
		if targetTongDBID == 0:
			self.statusMessage( playerBase, csstatus.TONG_TARGET_NOT_EXIST )
			return

		tongEntity = self.findTong( playerTongDBID )
		if tongEntity:
			self.statusTongMessage( tongEntity, csstatus.TONG_REQUEST_ROB_WAR_SUCCESS1, targetTongName )

		playerTongName = self.getTongNameByDBID( playerTongDBID )
		tongEntity = self.findTong( targetTongDBID )
		if tongEntity:
			self.statusTongMessage( tongEntity, csstatus.TONG_REQUEST_ROB_WAR_SUCCESS2, playerTongName )

		self.tongRequestRecord.append( playerTongDBID )
		d = { "rightTongDBID" : targetTongDBID, "leftTongDBID" : playerTongDBID, "rightTongName" : targetTongName, "leftTongName" : playerTongName }
		self.robWarInfos.append( d )

		
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_TONG_LUE_DUO, csdefine.ACTIVITY_JOIN_TONG, playerTongDBID )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )


	def onRegisterTerritory( self, tongDBID, territory ):
		"""
		define method.
		@param tongDBID: 帮会DBID
		@param territory:领地副本的basemailbox
		"""
		if not BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
			return
		# 如果该领地上线了， 而且他存在战争记录，则通知该副本 战争已经开始了
		if self.hasRobWarLog( tongDBID ):
			territory.onRobWarStart( self.getRobWarTongEnemyTongDBID( tongDBID ) )

	def onRobWarOver( self, failureTongDBID ):
		"""
		define method.
		掠夺战提前结束
		@param failureTongDBID:失败方帮会DBID
		"""
		warInfos = None
		for item in self.robWarInfos:
			if failureTongDBID == item[ "rightTongDBID" ] or failureTongDBID == item[ "leftTongDBID" ]:
				warInfos = item
				break

		if warInfos is None:
			ERROR_MSG( " not found warInfos, failureTongDBID %i." )
			return

		# 记录该帮会提前结束战争了
		self.robWarTmpData[ "overTongs" ].append( warInfos[ "rightTongDBID" ] )
		self.robWarTmpData[ "overTongs" ].append( warInfos[ "leftTongDBID" ] )
		# 清除所有人的敌对帮会信息
		self.clearAllRobWarTargetTong( item[ "rightTongDBID" ] )
		self.clearAllRobWarTargetTong( item[ "leftTongDBID" ] )

		# 通知领地战争结束， 领地可能会因战争产生一些动作， 如：领地的神兽停止活动
		territory = self.findTerritoryByTongDBID( warInfos[ "rightTongDBID" ] )
		if territory:
			territory.onRobWarStop()
		territory = self.findTerritoryByTongDBID( warInfos[ "leftTongDBID" ] )
		if territory:
			territory.onRobWarStop()

		# 开始支付战争利益
		if failureTongDBID == warInfos[ "rightTongDBID" ]:
			self.payRobWar( warInfos[ "leftTongDBID" ], warInfos[ "leftTongName" ], warInfos[ "rightTongDBID" ], warInfos[ "rightTongName" ] )
		else:
			self.payRobWar( warInfos[ "rightTongDBID" ], warInfos[ "rightTongName" ], warInfos[ "leftTongDBID" ], warInfos[ "leftTongName" ] )

		self.writeToDB()

	def clearAllRobWarTargetTong( self, tongDBID ):
		"""
		清除所有人的敌对帮会信息
		"""
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.setRobWarTargetTong( 0 )

	def onAllRobWarOver( self ):
		"""
		所有战争都结束  因为系统战争结束时间到了
		"""
		overTongs = self.robWarTmpData[ "overTongs" ]
		for item in self.robWarInfos:
			if item[ "rightTongDBID" ] in overTongs:
				continue
			else:
				# 清除所有人的敌对帮会信息
				self.clearAllRobWarTargetTong( item[ "rightTongDBID" ] )
				self.clearAllRobWarTargetTong( item[ "leftTongDBID" ] )
				self.payRobWar( item[ "rightTongDBID" ], item[ "rightTongName" ], \
				item[ "leftTongDBID" ], item[ "leftTongName" ] )
				# 将失败者加入失败名单
				self.robWarFailureList.append( item[ "leftTongDBID" ] )
				# 通知领地战争结束， 领地可能会因战争产生一些动作， 如：领地的神兽停止活动
				territory = self.findTerritoryByTongDBID( item[ "rightTongDBID" ] )
				if territory:
					territory.onRobWarStop()
				territory = self.findTerritoryByTongDBID( item[ "leftTongDBID" ] )
				if territory:
					territory.onRobWarStop()

		self.robWarInfos = []
		self.writeToDB()

	def payRobWar( self, winTongDBID, winTongName, failureTongDBID, failureTongName ):
		"""
		支付掠夺战的利益
		"""
		failureTongEntity = self.findTong( failureTongDBID )
		winTongEntity = self.findTong( winTongDBID )

		if winTongDBID in self.robWarTopRecords:
			self.robWarTopRecords[ winTongDBID ] += 3
		else:
			self.robWarTopRecords[ winTongDBID ] = 3

		if failureTongDBID in self.robWarTopRecords:
			self.robWarTopRecords[ failureTongDBID ] -= 1
		else:
			self.robWarTopRecords[ failureTongDBID ] = -1

		if failureTongEntity:
			failureTongEntity.onRobWarFailed( winTongEntity, winTongDBID, winTongName )
		else:
			cmd = "select sm_money, sm_prestige from tbl_TongEntity where id = %i;" % failureTongDBID
			BigWorld.executeRawDatabaseCommand( cmd, Functor( self.robWarQueryTongMoney_Callback, failureTongDBID, failureTongName, winTongDBID, winTongName ) )

	def robWarQueryTongMoney_Callback( self, failureTongDBID, failureTongName, winTongDBID, winTongName, result, dummy, error ):
		"""
		查询对方帮会金钱等信息  数据库回调
		"""
		if (error):
			ERROR_MSG( error )
			return
		if result is None or len( result ) == 0:
			DEBUG_MSG( "the failure tong( dbid:%i, name:%s ) had been dissmiss.winer dbid:%i,name:%s." % ( failureTongDBID, failureTongName, winTongDBID, winTongName ) )
			return
		money = int( result[0][0] )
		prestige = int( result[0][1] ) - 100
		payMoney = int( money * ROBWAR_FAILURE_PAY_PERCENTAGE )

		money -= payMoney
		if prestige < 0:
			prestige = 0

		cmd = "update tbl_TongEntity set sm_money=%i,sm_prestige=%i  where id = %i;" % ( money, prestige, failureTongDBID )
		BigWorld.executeRawDatabaseCommand( cmd )

		tongEntity = self.findTong( winTongDBID )
		if tongEntity:
			tongEntity.onRobWarSuccessfully( failureTongName, payMoney )
		else:
			cmd = "update tbl_TongEntity set sm_money=sm_money+%i  where id = %i;" % ( payMoney, failureTongDBID )
			BigWorld.executeRawDatabaseCommand( cmd )

	def onWarMessage( self, tongDBID, statusID, *args ):
		"""
		战争相关统一系统通报 向指定帮会通报
		"""
		args = "" if args == () else str( args )
		tongEntity = self.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, args )

	def robWarTimeAlert( self, statusID ):
		"""
		掠夺战时间提示
		"""
		for item in self.robWarInfos:
			if item[ "rightTongDBID" ] in self.robWarTmpData[ "overTongs" ] or item[ "leftTongDBID" ] in self.robWarTmpData[ "overTongs" ]:
				continue
			self.onWarMessage( item[ "rightTongDBID" ], statusID, item[ "leftTongName" ] )
			self.onWarMessage( item[ "leftTongDBID" ], statusID, item[ "rightTongName" ] )

	def initRobWar( self ):
		"""
		初始化掠夺战数据
		"""
		tongList = []
		for item in self.robWarInfos:
			# 通知领地战争开始， 领地可能会因战争产生一些动作， 如：领地的神兽开始活动
			territory = self.findTerritoryByTongDBID( item[ "rightTongDBID" ] )
			if territory:
				territory.onRobWarStart( item[ "leftTongDBID" ] )
			territory = self.findTerritoryByTongDBID( item[ "leftTongDBID" ] )
			if territory:
				territory.onRobWarStart( item[ "rightTongDBID" ] )
			# 设置帮会所有人的敌对帮会信息， 用于客户端显示与战斗惩罚判断等
			tongEntity = self.findTong( item[ "rightTongDBID" ] )
			if tongEntity:
				tongEntity.setRobWarTargetTong( item[ "leftTongDBID" ] )
			tongEntity = self.findTong( item[ "leftTongDBID" ] )
			if tongEntity:
				tongEntity.setRobWarTargetTong( item[ "rightTongDBID" ] )

			tongList.append( item[ "leftTongDBID" ] )
			tongList.append( item[ "rightTongDBID" ] )
			
		BigWorld.globalData[ "TONG_ROB_WAR_START" ] = tongList
		
	def onMemberLoginTong( self, tongDBID, baseEntity, baseEntityDBID ):
		"""
		define method.
		成员登陆通知
		"""
		if not BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
			return
		if tongDBID in self.robWarTmpData[ "overTongs" ]:
			return
		for item in self.robWarInfos:
			if tongDBID == item[ "rightTongDBID" ]:
				baseEntity.cell.tong_setRobWarTargetTong( item[ "leftTongDBID" ] )
				return
			elif tongDBID == item[ "leftTongDBID" ]:
				baseEntity.cell.tong_setRobWarTargetTong( item[ "rightTongDBID" ] )
				return

	#-----------------------------------------------------------------任务计划相关------------------------------------------

	def tongRobWarManager_registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"TongRobWarManager_start_notice" : "onTongRobWarManagerStartNotice",
					  	"TongRobWarManager_start" : "onTongRobWarManagerStart",
					  	"TongRobWarManager_end" : "onTongRobWarManagerEnd",
					  	"TongRobWarManagerSignUp_start" : "onTongRobWarManagerSignUpStart",
					  	"TongRobWarManagerSignUp_end" : "onTongRobWarManagerSignUpEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
		BigWorld.globalData["Crond"].addAutoStartScheme( "TongRobWarManagerSignUp_start", self, "onTongRobWarManagerSignUpStart" )

	def onTongRobWarManagerStartNotice( self ):
		"""
		defined method.
		战争报名开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONG_ROB_WAR_BEGIN_NOTIFY, [] )

	def onTongRobWarManagerSignUpStart( self ):
		"""
		defined method.
		战争报名开始通报
		"""
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
			return
		BigWorld.globalData[ "TONG_ROB_WAR_SIGNUP_START" ] = True

	def onTongRobWarManagerSignUpEnd( self ):
		"""
		defined method.
		战争报名结束通报
		"""
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_SIGNUP_START" ):
			del BigWorld.globalData[ "TONG_ROB_WAR_SIGNUP_START" ]

		for item in self.robWarInfos:
			#(csol-7884) 帮会掠夺站(帮会A的dbid 帮会A的名字 帮会B的dbid 帮会B的名字)
			try:
				g_logger.actDistributionLog( item[ "rightTongDBID" ], item["rightTongName"], item[ "leftTongDBID" ], item["leftTongName"] )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )


	def onTongRobWarManagerStart( self ):
		"""
		defined method.
		战争开始通报
		"""
		# 战争还有一分钟开始
		self.robWarTimeAlert( csstatus.TONG_ROB_WAR_START1 )
		self.robwar_start_remain30_timerID = self.addTimer( 30, 0, 0 )


	def onTongRobWarManagerEnd( self ):
		"""
		defined method.
		结束战争
		"""
		# 战争离结束1分钟
		self.robWarTimeAlert( csstatus.TONG_ROB_WAR_END1 )
		self.robwar_end30_timerID = self.addTimer( 30, 0, 0 )

	#----------------------------------------------------------------------------------------------------------------------

	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if timerID == self.robwar_dataClear_timerID:
			t = time.localtime()
			# 如果是周末则清空本星期的胜败信息
			if t[6] > 4:
				self.robWarFailureList = []
				self.tongRequestRecord = []
		elif timerID == self.robwar_start_remain30_timerID:	# 战争还有30秒开始
			self.robwar_start_remain30_timerID = 0
			self.robwar_start_timerID = self.addTimer( 30, 0, 0 )
			self.robWarTimeAlert( csstatus.TONG_ROB_WAR_START30 )
		elif timerID == self.robwar_start_timerID:			# 战争开始
			DEBUG_MSG( ">>tong of rob war is start!" )
			self.initRobWar()
			self.robwar_start_timerID = 0
			self.robWarTimeAlert( csstatus.TONG_ROB_WAR_START )
		elif timerID == self.robwar_end30_timerID:			# 战争离结束30秒
			self.robwar_end30_timerID = 0
			self.robwar_end_timerID = self.addTimer( 30, 0, 0 )
			self.robWarTimeAlert( csstatus.TONG_ROB_WAR_END30 )
		elif timerID == self.robwar_end_timerID:			# 战争结束
			DEBUG_MSG( ">>tong of rob war is end!" )
			if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ):
				del BigWorld.globalData[ "TONG_ROB_WAR_START" ]

			self.onAllRobWarOver()
			self.robwar_end_timerID = 0
			self.robWarReset()								# 结束重置
		elif timerID == self.requestRobTongTimer:
			self.checkRobWarRequest()
			
#
# $Log: not supported by cvs2svn $
#