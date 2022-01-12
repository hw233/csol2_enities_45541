# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *
import csdefine
import cschannel_msgs
import Love3
import time
import csstatus
import random
from CrondDatas import CrondDatas
import cPickle
import items
g_items = items.instance()
from MsgLogger import g_logger


g_CrondDatas = CrondDatas.instance()
COMPETITION_MAX_ENTER_PLAYER = 50				# 副本最高限制玩家人数
COMPETITION_MAX_TONG_ENTER_PLAYER = 1			# 每个帮会最高限制玩家人数
SIGNUP_TIME = 55*60		# 55分钟的报名时间
ENTER_TIME = 5*60       # 5分钟的入场准备时间

TONGCOMPETITION_SIGNUP    = 0    # 帮会竞技开始报名时间
TONGCOMPETITION_ENTER     = 1    # 帮会竞技开始入场时间
TONGCOMPETITION_START     = 2    # 帮会竞技比赛开始时间

class TongCompetitionMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		# 把自己注册为globalData全局实体

		self._signUpTime = SIGNUP_TIME  # 从开始报名到开始入场的55分钟
		self._enterTime = ENTER_TIME    # 从开始入场到比赛正式开始的5分钟

		self.registerGlobally( "TongCompetitionMgr", self._onRegisterManager )
		self.entersSpaceTongMember = {}
		self.tempMemberTongInfo = {}
		self.competitionDBIDList = []   # 报名参加帮会竞技的成员列表
		self.TongList = []				# 允许进入竞技场的帮会列表
		self.tongEnterMember = {}		# 保留一份原始进入竞技场的玩家列表
		self.leavePlayerName = []		# 比赛过程中离开副本的玩家名单

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TongCompetitionMgr Fail!" )
			# again
			self.registerGlobally( "TongCompetitionMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["TongCompetitionMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("TongCompetitionMgr Create Complete!")
			self.registerCrond()

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
						"familyCompetition_start_notice" : "onStartNotice",
					  }
		crond = BigWorld.globalData["Crond"]
		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				crond.addScheme( cmd, self, callbackName )

	def onStartNotice( self ):
		"""
		define method.
		活动开始前55分钟开始提示报名
		"""
		self.competitionDBIDList = []
		self.tongEnterMember = {}
		self._signUpTime = SIGNUP_TIME
		self._enterTime  = ENTER_TIME
		self.onTimer( 0, TONGCOMPETITION_SIGNUP )
		INFO_MSG( "TongCompetitionMgr", "notice", "" )

	def onTimer( self, timerID, userArg ):
		"""
		"""
		if userArg == TONGCOMPETITION_SIGNUP:		# 55分钟内报名

			leftSignUpTime = int( int( self._signUpTime ) / 60 )

			if self._signUpTime > 0 and leftSignUpTime in [ 55, 40, 25, 10, 5 ]:
				# 55(40/25/10/5)分钟分别有公告提示
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_BEGIN_NOTIFY_0 % leftSignUpTime, [] )
			BigWorld.globalData[ "AS_TongCompetition_SignUp" ] = True

			if self._signUpTime == 0:
				self.initTongCompetition( self.competitionDBIDList )		# 判断出符合条件的帮会进场
				if not self.TongList:
					return
				tong = BigWorld.globalData["TongManager"]
				b = BigWorld.entities.get( tong.id )
				for dbid in self.TongList:
					tongEntity = b.findTong( dbid )
					tongEntity.tongCompetitionGather( 1 )
				self.addTimer( 0, 0, TONGCOMPETITION_ENTER )
				if BigWorld.globalData.has_key( "AS_TongCompetition_SignUp" ):
					del BigWorld.globalData[ "AS_TongCompetition_SignUp" ]		# 帮会竞技结束报名
			else:
				self.addTimer( 60, 0, TONGCOMPETITION_SIGNUP )

			self._signUpTime -= 60

		elif userArg == TONGCOMPETITION_ENTER:		# 5分钟内入场开始

			leftEnterTime = int( int( self._enterTime ) / 60 )
			
			if self._enterTime > 0 and leftEnterTime in [ 5, 4, 3, 2, 1 ]:
				# 5(4/3/2/1)分钟分别有公告提示
				Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_BEGIN_NOTIFY_1 % leftEnterTime, [] )

			if self._enterTime <= 0:
				if BigWorld.globalData.has_key( "AS_TongCompetition" ):
					del BigWorld.globalData[ "AS_TongCompetition" ]		# 帮会竞技结束进场
				self.onStart( )
			else:
				self.addTimer( 60, 0, TONGCOMPETITION_ENTER )

			self._enterTime -= 60

	def onStart( self ):
		"""
		define method.
		5分钟的入场时间结束了,比赛正式开始。
		"""
		if not self.TongList:
			return
		tong = BigWorld.globalData["TongManager"]
		b = BigWorld.entities.get( tong.id )
		for dbid in self.TongList:
			tongEntity = b.findTong( dbid )
			tongEntity.tongCompetitionCloseGather()
		if  BigWorld.globalData.has_key( "AS_TongCompetition" ):
			curTime = time.localtime()
			ERROR_MSG( "tongCompetition is running，%i:%i try open。"%(curTime[3],curTime[4] ) )
			return
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_BEGIN_NOTIFY, [] )
		INFO_MSG( "TongCompetitionMgr", "start", "" )

	def onEnd( self ):
		"""
		define method.
		帮会竞技活动结束
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_TONGCOMPETITION_END_NOTIFY, [] )
		self.sendAwardToEmail()		# 活动结束后发送参与奖
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.TONGCOMPETITION_MAIL_REWARD_NOTICE, [] )
		if BigWorld.globalData.has_key( "AS_TongCompetition" ):
			del BigWorld.globalData[ "AS_TongCompetition" ]
		self.competitionDBIDList = []   # 报名参加帮会竞技的成员列表清空
		self.TongList = []				# 允许进入竞技场的帮会列表清空
		self.tongEnterMember = {}		# 发送参与奖的成员字典清空
		self.leavePlayerName = []		# 比赛过程中离开副本的玩家列表清空
		INFO_MSG( "TongCompetitionMgr", "end", "" )

	def onEnterSpace(self, spaceMailBox, playerMailBox, TongDBID):
		"""
		define method.
		"""
		if not BigWorld.globalData.has_key( "AS_TongCompetition" ):
			return

		if not self.isTongJoin( TongDBID ):			# 是否符合资格进入帮会竞技场
			return

		if playerMailBox.id not in self.tempMemberTongInfo:
			ERROR_MSG("can't find player:%d tongID "%playerMailBox.id)
			return

		tong_dbID = self.tempMemberTongInfo[playerMailBox.id]		# 玩家所在帮会的mailbox

		if spaceMailBox.id not in self.entersSpaceTongMember:		# 里面增加一个字典
			self.entersSpaceTongMember[spaceMailBox.id] = {}

		if tong_dbID not in self.entersSpaceTongMember[spaceMailBox.id]:		# 里面增加一个列表
			self.entersSpaceTongMember[spaceMailBox.id][tong_dbID] = []

		self.entersSpaceTongMember[spaceMailBox.id][tong_dbID].append(playerMailBox)		# 记录进入副本的帮会成员
		self.tempMemberTongInfo.pop(playerMailBox.id)		# 删除已经进入副本的玩家id

	def onLevelSpace(self, spaceMailBox, playerMailBox):
		"""
		define method.
		"""
		try:
			currentSpaceEnterMember = self.entersSpaceTongMember[spaceMailBox.id]
		except KeyError:
			ERROR_MSG("currentTongEnterMember is key error spaceID:%d"%(spaceMailBox.id))
			return

		for tid, playerList in currentSpaceEnterMember.iteritems():
			for index, pm in enumerate(playerList):
				if pm.id == playerMailBox.id:
					self.entersSpaceTongMember[spaceMailBox.id][tid].pop(index)
					if len( currentSpaceEnterMember[tid] ) == 0:
						self.entersSpaceTongMember[spaceMailBox.id].pop(tid)		# 如果该帮会在副本内人数为0，弹出此帮会ID
					return

	def teleportEntity( self, domainSpaceMailBox, spaceMailBox, position, direction, playerMailBox, params ):
		"""
		define method.
		"""
		if not BigWorld.globalData.has_key( "AS_TongCompetition" ):
			return
		tong_dbID = params.get("tongDBID", 0)
		if tong_dbID not in self.TongList:
			return
		self.tempMemberTongInfo[ playerMailBox.id ] = tong_dbID
		if spaceMailBox == None:
			domainSpaceMailBox.onSpaceItemEnter( position, direction, playerMailBox, params )
			return

		result = self.checkISCanTeleport(spaceMailBox, playerMailBox, tong_dbID)
		if result != 0:
			playerMailBox.client.onStatusMessage( result, "" )
			return

		self.tempMemberTongInfo[ playerMailBox.id ] = tong_dbID
		domainSpaceMailBox.onSpaceItemEnter( position, direction, playerMailBox, params )

	def checkISCanTeleport( self, spaceMailBox, playerMailBox, tong_dbID ):
		result = 0
		while( True ):
			if tong_dbID == 0 or tong_dbID == None:
				result = csstatus.TONG_COMPETITION_FORBID_MEMBER
				break

			if tong_dbID not in self.TongList:		# 如果不在允许进入的帮会列表内将不能进入副本
				result = csstatus.TONG_COMPETETION_NOTICE_10
				break

			if spaceMailBox.id not in self.entersSpaceTongMember:
				break

			if tong_dbID not in self.entersSpaceTongMember[spaceMailBox.id]:
				break

			if len( self.entersSpaceTongMember[spaceMailBox.id][tong_dbID] ) >= COMPETITION_MAX_TONG_ENTER_PLAYER:		# 每个帮会可进入的最高人数不能超过10
				result = csstatus.TONG_COMPETITION_TONG_MEMBER_FULL
				break

			break

		return result

	def countSpaceMember(self, spaceID):
		count = 0
		if spaceID in self.entersSpaceTongMember:
			for pList in self.entersSpaceTongMember[spaceID].values():
				count += len(pList)

		return count

	def onRequestCompetition( self, playerBaseMailbox, tongDBID ):
		"""
		Define method.
		报名参加帮会竞技

		@param playerBaseMailbox : 帮主或者副帮主的base mailbox
		@type playerBaseMailbox : MAILBOX
		@param tongDBID : 申请帮会竞技的dbid
		@type tongDBID : DATABASE_ID
		"""
		allowSignUp = BigWorld.globalData.has_key( "AS_TongCompetition_SignUp" )
		if not allowSignUp:
			self.abaStatusMessage( playerBaseMailbox, csstatus.TONG_COMPETETION_NOTICE_1 )
			return
		if tongDBID in self.competitionDBIDList:
			self.abaStatusMessage( playerBaseMailbox, csstatus.TONG_COMPETETION_NOTICE_8 )
			return

		self.competitionDBIDList.append( tongDBID )
		self.onAbaMessage( tongDBID, csstatus.TONG_COMPETETION_NOTICE_5 )
		
		try:
			g_logger.actJoinLog( csdefine.ACTIVITY_BANG_HUI_JING_JI, csdefine.ACTIVITY_JOIN_TONG, tongDBID, self.getTongNameByDBID( tongDBID ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def onAbaMessage( self, tongDBID, statusID, *args ):
		"""
		帮会竞技相关统一系统通报 向指定帮会通报
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )

		tong = BigWorld.globalData["TongManager"]
		b = BigWorld.entities.get( tong.id )
		tongEntity = b.findTong( tongDBID )
		if tongEntity:
			tongEntity.onStatusMessage( statusID, tempArgs )

	def abaStatusMessage( self, playerBase, statusID, *args ):
		"""
		帮会竞技状态信息发送函数
		"""
		if args == ():
			tempArgs = ""
		else:
			tempArgs = str( args )
		playerBase.client.onStatusMessage( statusID, tempArgs )


	def initTongCompetition( self, competitionDBIDList ):
		"""
		初始化帮会竞技数据，允许符合资格的帮会进入
		"""
		self.TongList = self.randomGetList( competitionDBIDList )
		if not self.TongList:
			return
		for TongDBID in self.TongList:
			BigWorld.globalData[ "AS_TongCompetition" ] = True

	def randomGetList( self, competitionDBIDList ):
		"""
		报名结束后，获取符合资格的帮会列表
		"""
		if 1 <= len( self.competitionDBIDList ) <= 5:		# 5个或5个以内的帮会都有资格
			for tongDBID in competitionDBIDList:
				self.onAbaMessage( tongDBID, csstatus.TONG_COMPETETION_NOTICE_9 )
			return competitionDBIDList

		if len( self.competitionDBIDList ) > 5:				# 随机抽取5个帮会
			TongIDList = random.sample( self.competitionDBIDList, 5 )
			for tongDBID in TongIDList:
				self.onAbaMessage( tongDBID, csstatus.TONG_COMPETETION_NOTICE_9 )		# 通知被抽到的帮会
				for tongDBID in competitionDBIDList:
					if tongDBID not in TongIDList:
						self.onAbaMessage( tongDBID, csstatus.TONG_COMPETETION_NOTICE_10 )		# 通知没被抽到的帮会

			return TongIDList

		else:
			return

	def isTongJoin( self, TongDBID ):
		"""
		TongDBID帮会是否符合资格进入竞技场
		"""
		return TongDBID in self.TongList

	def sendAwardToEmail( self ):
		"""
		副本活动结束后，统一发送奖励到玩家邮箱
		"""
		for e in self.tongEnterMember:
			itemDatas = []
			item = g_items.createDynamicItem( 60101250, 1 )
			if item:
				tempDict = item.addToDict()
				del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
				itemData = cPickle.dumps( tempDict, 2 )
				itemDatas.append( itemData )
				BigWorld.globalData["MailMgr"].send( None, e, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", cschannel_msgs.TONGCOMPETITION_MAIL_REWARD_TITLE, "", 0, itemDatas )

	def setSignUpTime( self, value ):
		"""
		define method.
		设置帮会竞技剩余报名时间，用于GM指令
		"""
		tong = BigWorld.globalData["TongCompetitionMgr"]
		b = BigWorld.entities.get( tong.id )
		b._signUpTime = value

	def saveTongMemberInfo( self, playerName, playerMailbox, tongDBID ):
		"""
		defined method.

		@param playerName			: 玩家姓名
		@type playerName			: STRING
		@param playerMailbox			: 玩家mailbox
		@type playerMailbox			: MAILBOX
		@param tongDBID			: 玩家的帮会ID
		@type tongDBID			: DATABASE_ID

		保存参赛玩家的信息
		"""
		if playerName not in self.tongEnterMember:
			self.tongEnterMember[ playerName ] = [ playerMailbox, tongDBID ]

	def saveLeaveTongMember( self, playerName ):
		"""
		defined method.

		记录比赛中离开的玩家的名字
		"""
		self.leavePlayerName.append( playerName )

	def sendChampionBox( self, tongDBID ):
		"""
		define method.

		给提前离开副本的玩家发放冠军宝箱
		"""
		itemDatas = []
		item = g_items.createDynamicItem( 60101243, 1 )
		if item:
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )

		for e in self.leavePlayerName:
			if e in self.tongEnterMember and self.tongEnterMember[e][1] == tongDBID:
				BigWorld.globalData["MailMgr"].send( None, e, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, cschannel_msgs.TONGCOMPETITION_MAIL_WINNER_TITLE, "", "", 0, itemDatas )
		self.leavePlayerName = []