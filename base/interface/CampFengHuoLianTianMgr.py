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



CAMP_ROLE_NUM = 2				#阵营烽火连天活动每个阵营玩家数量

NOTICE_TIME_1 = 30 * 60			#通知时间间隔1
NOTICE_TIME_2 = 15 * 60			#通知时间间隔2

MATCH_TIME = 30 * 60			#比赛时间为30分钟
SIGN_UP_TIME = 10 * 60			#报名时间为10分钟

TIMER_NOTICE_1 = 10
TIMER_NOTICE_2 = 11

REWARD_FIRST_PLAYER_ITEM_ID = 60101282	#第一名奖励宝箱ID
CAMP_FENG_HUO_LIAN_TIAN_SPACENAME = "fu_ben_zhen_ying_feng_huo_lian_tian"

class CampInfo:
	"""
	单个阵营成员数据
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
	一场比赛数据
	"""
	def __init__( self ):
		self.taoismCampInfo = []
		self.demonCampInfo = []
	
	def isCampTotalFull( self ):
		"""
		判断魔道以及仙道阵营人数是否已满
		"""
		if self.isTaosimCampFull() and self.isDemonCampFull():
			return True
		else:
			return False
	
	def isCampFull( self, camp ):
		"""
		某个阵营的人数是否已满
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
		判断仙道人数是否已满
		"""
		if len( self.taoismCampInfo ) >= CAMP_ROLE_NUM:
			return True
	
	def isDemonCampFull( self ):
		"""
		判断魔道人数是否已满
		"""
		if len( self.demonCampInfo ) >= CAMP_ROLE_NUM:
			return True
	
	def addCampMember( self, camp, dbid, playerMB ):
		"""
		添加阵营成员
		"""
		campMember = CampInfo( camp, dbid, playerMB )
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			self.taoismCampInfo.append( campMember )
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			self.demonCampInfo.append( campMember )
			
	def delCampMember( self, camp, dbid ):
		"""
		删除阵营成员
		"""
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			for campInfo in self.taoismCampInfo:
				if campInfo.getDBID() == dbid:
					#提示已经退出报名成功，之后将队员删除
					playerMB = campInfo.getMailBox()
					if playerMB:
						playerMB.client.onStatusMessage( csstatus.CAMP_FENG_HUO_EXIT_SUCCESS, "" )
					self.taoismCampInfo.remove( campInfo )
					return
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			for campInfo in self.demonCampInfo:
				if campInfo.getDBID() == dbid:
					#提示已经退出报名成功，之后将队员删除
					playerMB = campInfo.getMailBox()
					if playerMB:
						playerMB.client.onStatusMessage( csstatus.CAMP_FENG_HUO_EXIT_SUCCESS, "" )
					self.demonCampInfo.remove( campInfo )
					return

	def getTaoismCampInfo( self ):
		"""
		获取对应的仙道阵营玩家信息
		"""
		return self.taoismCampInfo
		
	def getDemonCampInfo( self ):
		"""
		获取对应的魔道阵营玩家信息
		"""
		return self.demonCampInfo

	def findCampMemberByDBID( self, camp, dbid ):
		"""
		根据玩家的阵营以及DBID查找对应的CampInfo对象
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
		更新
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
	多场比赛数据
	"""
	def __init__( self ):
		self.maxBattleNum = 0
		self.lastTaoismNoFullBattleNum = 0
		self.lastDemonNoFullBattleNum = 0
		self.lastNoFullBattleNum = 0
		self.battleItems = {}
		
	def getMaxBattleNum( self ):
		"""
		获取目前已经开的最大战场数量
		"""
		return self.maxBattleNum
		
	def getLastNoFullBattleNum( self ):
		"""
		获取目前已经开的最后一个未满的战场数
		"""
		return self.lastNoFullBattleNum
		
	def getLastTaoismNoFullBattleNum( self ):
		"""
		获取目前已经开的最后一个仙道阵营未满战场数
		"""
		return self.lastTaoismNoFullBattleNum
		
	def getLastDemonNoFullBattleNum( self ):
		"""
		获取目前已经开的最后一个魔道阵营未满战场数
		"""
		return self.lastDemonNoFullBattleNum
		
	def getLastCampNoFullBattleNum( self, camp ):
		"""
		获取目前已经开的最后一个某个阵营的未满战场数
		"""
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			return self.getLastTaoismNoFullBattleNum()
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			return self.getLastDemonNoFullBattleNum()
		return -1
		
	def setMaxBattleNum( self, maxBattleNum ):
		"""
		设置目前已经开的最大战场数量
		"""
		self.maxBattleNum = maxBattleNum
		
	def setLastNoFullBattleNum( self, lastNoFullBattleNum ):
		"""
		设置目前已经开的最后一个未满的战场数
		"""
		self.lastNoFullBattleNum = lastNoFullBattleNum
		
	def setLastTaoismNoFullBattleNum( self, lastTaoismNoFullBattleNum ):
		"""
		设置目前已经开的最后一个仙道阵营未满战场数
		"""
		self.lastTaoismNoFullBattleNum = lastTaoismNoFullBattleNum
		
	def setLastDemonNoFullBattleNum( self, lastDemonNoFullBattleNum ):
		"""
		设置目前已经开的最后一个魔道阵营未满战场数
		"""
		self.lastDemonNoFullBattleNum = lastDemonNoFullBattleNum
		
	def setLastCampNoFullBattleNum( self, camp, num ):
		"""
		设置目前已经开的最后一个某个阵营的未满战场数
		"""
		DEBUG_MSG( "camp is %s,num is %s"%( camp, num ) )
		if camp == csdefine.ENTITY_CAMP_TAOISM:
			self.setLastTaoismNoFullBattleNum( num )
		elif camp == csdefine.ENTITY_CAMP_DEMON:
			self.setLastDemonNoFullBattleNum( num )
		
	def findCampLastNoFullBattleNum( self, camp, index ):
		"""
		从当前的战场数往后查找本阵营最后一个未满的战场数
		"""
		num = -1
		for i in xrange( index, self.maxBattleNum + 1 ):
			if not self.battleItems[ i ].isCampFull( camp ):
				num = i
				break
		return num
		
	def newBattle( self ):
		"""
		新建一个战场
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
		通知未满战场更新战场信息
		"""
		lastNoFullBattleNum = self.getLastNoFullBattleNum()
		for i in xrange( lastNoFullBattleNum, self.maxBattleNum + 1 ):
			battleItem = self.getBattleByKey( i )
			if battleItem:
				battleItem.noticePlayerUpdateMaxBattleNum( self.maxBattleNum )
	
	def getBattleByKey( self, key ):
		"""
		根据关键字获取相应的战场实例
		"""
		return self.battleItems.get( key, None )


class CampFengHuoLianTianMgr:
	# 阵营烽火连天活动管理器
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
		管理器初始化完毕
		"""
		taskEvents = {
					  	"CampFHLT_start_notify"	: "fengHuo_onStartNotify",						# 开始通知
					  	"CampFHLT_sign_up_start" : "fengHuo_onSignUpStart",						# 开启报名
					  	"CampFHLT_start" : "fengHuo_onStart",									# 开启活动
					  	"CampFHLT_activity_end"	: "fengHuo_onEnd",								# 活动结束
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )
				
	def fengHuo_onStartNotify( self ):
		"""
		define method
		阵营烽火连天活动开始通知
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_NOTICE_1, [] )
		#self.campBroadcast( cschannel_msgs.CAMP_FENG_HUO_TAOISM_NOTICE_1, cschannel_msgs.CAMP_FENG_HUO_DEMON_NOTICE_1, [] )
		self.resetCampFengHuo()
		self.fengHuoNotifyTimer = self.addTimer( NOTICE_TIME_1, 0, TIMER_NOTICE_1 )
	
	def resetCampFengHuo( self ):
		"""
		重置阵营数据
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
		阵营烽火连天通知结束，开始报名
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
		阵营烽火连天活动开始
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
		#活动开始，通知有资格参赛的玩家弹出传送框，可以选择传送进入副本
		self.noticeTransportPlayer()
		
	def fengHuo_onEnd( self ):
		"""
		define method
		阵营烽火连天活动结束
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.CAMP_FENG_HUO_END, [] )
		#self.campBroadcast( cschannel_msgs.CAMP_FENG_HUO_END, cschannel_msgs.CAMP_FENG_HUO_END, [] )
		if BigWorld.globalData.has_key( "campFengHuo_start" ):
			del BigWorld.globalData[ "campFengHuo_start" ]
		self.closeCampFengHuoRooms()
		
	def onRequestCampFengHuoSignUp( self, camp, dbid, playerMB ):
		"""
		玩家请求报名参加阵营烽火连天活动
		"""
		if self.campBattleItem.getMaxBattleNum() == 0:
			self.campBattleItem.newBattle()
		lastCampNoFullBattleNum = self.campBattleItem.getLastCampNoFullBattleNum( camp )
		if lastCampNoFullBattleNum == -1:
			return
		battleItem = self.campBattleItem.getBattleByKey( lastCampNoFullBattleNum )
		if battleItem:
			if not battleItem.isCampFull( camp ) and BigWorld.globalData.has_key( "campFengHuo_startSignUp" ):
				#模仿操作系统PV操作实现互斥，先进行P操作，将信号量减一，如果对应的信号量小于0，那么加入等待队列中
				self.operateNum = self.operateNum - 1
				if self.operateNum < 0:
					self.joinFengHuoWaitQueue( self.onRequestCampFengHuoSignUp, [ camp, dbid, playerMB ] )
					return
				#临界区代码
				if self.fengHuoPlayerDBIDToBattleNum.has_key( dbid ):
					battleNum = self.fengHuoPlayerDBIDToBattleNum[ dbid ]
					lastBattleItem = self.campBattleItem.getBattleByKey( battleNum )
					campInfo = lastBattleItem.findCampMemberByDBID( camp, dbid )
					if campInfo:
						#更新相应的playerMB信息
						campInfo.setMailBox( playerMB )
					#lastBattleItem.delCampMember( camp, dbid )
					#lastBattleItem.addCampMember( camp, dbid, playerMB )
				else:
					battleItem.addCampMember( camp, dbid, playerMB )
					#需要提示玩家自己当前报名的战场数以及目前最大战场数
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
				#模仿操作系统PV操作实现互斥，进行V操作，将信号量加一，如果对应的信号量小于等于0，那么从中释放出一个等待信号量的操作
				self.operateNum = self.operateNum + 1
				if self.operateNum <= 0:
					self.releaseFengHuoWaitQueue()
	
	def noticePlayerBattleInfo( self, battleNum ):
		"""
		通知相关玩家相应的战场信息
		"""
		battleItem = self.campBattleItem.getBattleByKey( battleNum )
		if battleItem:
			battleItem.noticeCampPlayerInfo()
	
	def onRequestCampFengHuoQuitSignUp( self, camp, dbid, playerMB ):
		"""
		玩家请求退出报名队伍
		"""
		if self.fengHuoPlayerDBIDToBattleNum.has_key( dbid ) and BigWorld.globalData.has_key( "campFengHuo_startSignUp" ):
			battleNum = self.fengHuoPlayerDBIDToBattleNum[ dbid ]
			battleItem = self.campBattleItem.getBattleByKey( battleNum )
			if battleItem.isCampTotalFull():			#人数已满，相当于进行读操作，这个时候不需要进行互斥的处理，只有当人数未满，有人加入的时候，才有必要进行互斥的处理
				#战场双方人数均已满，提示已经报名成功，不能够退出
				if playerMB:
					playerMB.client.onStatusMessage( csstatus.CAMP_FENG_HUO_CANNOT_EXIT, "" )
			else:
				#模仿操作系统PV操作实现互斥，先进行P操作，将信号量减一，如果对应的信号量小于0，那么加入等待队列中
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
		将一些操作加入烽火连天的等待队列
		"""
		self.fengHuoWaitQueue.append( ( func, args ) )
		
	def releaseFengHuoWaitQueue( self ):
		"""
		将等待队列的操作释放，执行对应的操作
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
		产生阵营消息字典
		"""
		dict = { csdefine.ENTITY_CAMP_TAOISM : taoismCampMsg, csdefine.ENTITY_CAMP_DEMON : demonCampMsg }
		return dict
	
	def campBroadcast( self, taoismCampMsg, demonCampMsg, blobArgs ):
		dict = self.produceCampMsgDict( taoismCampMsg, demonCampMsg )
		Love3.g_baseApp.campActivity_broadcast( dict, blobArgs )
	
	def onRoleRequestEnterCampFHLT( self, camp, dbid, playerMB ):
		"""
		玩家请求进入烽火连天副本
		"""
		if self.fengHuoPlayerDBIDToBattleNum.has_key( dbid ):
			battleNum = self.fengHuoPlayerDBIDToBattleNum[ dbid ]
			battleItem = self.campBattleItem.getBattleByKey( battleNum )
			DEBUG_MSG( "camp is %s,dbid is %s, playerMB is %s"%( camp, dbid, playerMB ) )
			if battleItem.isCampTotalFull():
				#人已满，表示玩家已经可以进入阵营烽火连天副本
				if playerMB:
					playerMB.cell.gotoSpace( CAMP_FENG_HUO_LIAN_TIAN_SPACENAME, ( 0, 0, 0 ), ( 0, 0, 0 ) )
			else:
				#提示玩家报名战场人数未满，报名未成功，不能参加比赛
				if playerMB:
					playerMB.client.onStatusMessage( csstatus.CAMP_FENG_HUO_CANNOT_JOIN, "" )
	
	def noticeTransportPlayer( self ):
		"""
		通知传送玩家进入副本
		"""
		num = self.campBattleItem.getLastNoFullBattleNum()
		for i in xrange( 1, num ):
			battleItem = self.campBattleItem.getBattleByKey( i )
			if battleItem.isCampTotalFull():
				for info in battleItem.getTaoismCampInfo():
					playerMB = info.getMailBox()
					#弹出对话框，让玩家选择是否传送
					if playerMB:
						playerMB.client.onCampFengHuoSelectTransportOrNot()
				for info in battleItem.getDemonCampInfo():
					playerMB = info.getMailBox()
					#弹出对话框，让玩家选择是否传送
					if playerMB:
						playerMB.client.onCampFengHuoSelectTransportOrNot()
	
	def onEnterCampFengHuoSpace( self, spaceDomain, baseMailbox, params ):
		"""
		define method.
		进入阵营烽火连天副本
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
		阵营烽火连天奖励
		"""
		if not winnerCamp:
			if failureCamp == csdefine.ENTITY_CAMP_TAOISM:
				winnerCamp = csdefine.ENTITY_CAMP_DEMON
			elif failureCamp == csdefine.ENTITY_CAMP_DEMON:
				winnerCamp = csdefine.ENTITY_CAMP_TAOISM
			self.changeCampMorale( winnerCamp, failureCamp )
		else:
			self.changeCampMorale( winnerCamp, failureCamp )
		#奖励杀敌数最多的玩家宝箱，以及金钱、经验
		self.sendFirstPlayerReward( playerName )
	
	def sendFirstPlayerReward( self, playerName ):
		itemDatas = []
		item = g_items.createDynamicItem( REWARD_FIRST_PLAYER_ITEM_ID )
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
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
		将一些操作加入烽火连天的等待队列
		"""
		self.fengHuoChangeMoraleQueue.append( ( func, args ) )
		
	def releaseFengHuoChangeMoraleQueue( self ):
		"""
		将等待队列的操作释放，执行对应的操作
		"""
		info = self.fengHuoChangeMoraleQueue.pop( 0 )
		func = info[ 0 ]
		args = info[ 1 ]
		func( *args )