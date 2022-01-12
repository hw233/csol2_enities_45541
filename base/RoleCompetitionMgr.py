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


ROLECOMPETITION_STATE_FREE			= 0		#空闲期
ROLECOMPETITION_STATE_SIANUP		= 1		#报名期
ROLECOMPETITION_STATE_READY			= 2		#准备期
ROLECOMPETITION_STATE_ADMISSION		= 3		#入场期
ROLECOMPETITION_STATE_END			= 4		#结束期
ROLECOMPETITION_ADMISSION1			= 5		#个人竞技开始入场通知
ROLECOMPETITION_ADMISSION2			= 6		#个人竞技开始入场通知
ROLECOMPETITION_ADMISSION3			= 7		#个人竞技开始入场通知
ROLECOMPETITION_READY				= 8		#个人竞技玩家抽取通知
ROLE_COMPETITION_SELECT				= 9		#随机抽取间隔时间
ROLECOMPETITION_TEST				= 10	#供GM指令删除进入用
ROLECOMPETITION_BEGIN_SINGUP		= [ 1, 2, 3, 4]
ROLECOMPETITION_BEGIN_SINGUP_TIME	= [ 55, 40, 25, 10, 5]	#个人竞技报名通知时间表
ROLECOMPETITION_ADMISSION1_TIME		= [ 5, 4, 3, 2, 1]		#个人竞技入场通知时间表
NOTICE_TIMES2			= [ ( 4, 30), ( 3, 30), ( 2, 30), ( 1, 30)]
NOTICE_TIMES3			= [ 30]
REWARD_EXP_ITEM_ID = 60101248


class RoleCompetitionMgr( BigWorld.Base ):

	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.hasSignUpNames = []		# 在一次比赛中，已经报名的玩家名字
		self.hasEnterNameDict = {}		#进入的玩家字典 such as {playerName：level}
		self.roleCompetitionNameDict = {}		# 报名参加个人竞技角色name字典(根据角色等级分类) such as { level/10 : [playerName,...],... }
		self.hasSelectedNameDict = {}			# 选中参加个人竞技角色name字典(根据角色等级分类) such as { level/10 : [playerName,...],... }
		self.DBIDToBaseMailbox = {}				# 根据角色name找到个人竞技角色的baseMailbox
		self.hasSelectedBaseMailbox = {}		# 在一次比赛中被选中的角色baseMailbox字典 such as { name:baseMailbox,...}
		self.nameToDBIDDict = {}				#根据角色name找到个人竞技角色的DBID
		self.currentStage = ROLECOMPETITION_STATE_FREE
		self.levelList = []
		# 把自己注册为globalData全局实体
		self.registerGlobally( "RoleCompetitionMgr", self._onRegisterManager )

	def _onRegisterManager( self, complete ):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register RoleCompetitionMgr Fail!" )
			# again
			self.registerGlobally( "RoleCompetitionMgr", self._onRegisterManager )
		else:
			BigWorld.globalData["RoleCompetitionMgr"] = self		# 注册到所有的服务器中
			INFO_MSG("RoleCompetitionMgr Create Complete!")
			self.registerCrond()



	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
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
		活动报名开始
		"""
		if BigWorld.globalData.has_key( "AS_RoleCompetition" ) and BigWorld.globalData[ "AS_RoleCompetition" ] == True:
			curTime = time.localtime()
			ERROR_MSG( "个人竞赛副本活动正在进行，%i点%i分试图再次开始个人竞赛副本。"%(curTime[3],curTime[4] ) )
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
		活动开始通知
		"""
		temp = cschannel_msgs.BCT_ROLECOMPETITION_BEGIN_NOTIFY_0 %ROLECOMPETITION_BEGIN_SINGUP_TIME[0]
		Love3.g_baseApp.anonymityBroadcast( temp, [] )
		BigWorld.globalData[ "AS_RoleCompetitionSignUp" ] = True
		self.addTimer( 15*60, 0, ROLECOMPETITION_BEGIN_SINGUP[0] )
		INFO_MSG( "RoleCompetitionMgr", "notice", "" )

	def onEnd( self ):
		"""
		define method.
		活动报名结束
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.BCT_ROLECOMPETITION_END_NOTIFY, [] )
		if BigWorld.globalData.has_key( "AS_RoleCompetition" ):
			del BigWorld.globalData[ "AS_RoleCompetition" ]
		self.end_roleCompetition()
		INFO_MSG( "RoleCompetitionMgr", "end", "" )

	def onGMStartNotice( self ):
		"""
		define method.
		GM命令开启活动通知
		"""
		if self.currentStage != ROLECOMPETITION_STATE_FREE:
			curTime = time.localtime()
			ERROR_MSG( "个人竞赛副本活动正在进行，%i点%i分试图再次开始个人竞赛副本。"%(curTime[3],curTime[4] ) )
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
		供GM指令调试使用
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
		执行个人竞技相关操作
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
			self.addTimer( 0, 0, ROLE_COMPETITION_SELECT)			#随机抽取在线玩家
			
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
			step = level/10		# 每10级为一个赛场
		if self.roleCompetitionNameDict.has_key(step) and playerName in self.roleCompetitionNameDict[step]:
			return True
		else:
			return False
	
	def requestSignUp( self, level, playerBaseMailBox, playerName ):
		"""
		define method
		请求报名
		"""
		if level == csconst.ROLE_LEVEL_UPPER_LIMIT:
			step = (csconst.ROLE_LEVEL_UPPER_LIMIT - 1)/10
		else:
			step = level/10		# 每10级为一个赛场
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
		得到报名情况回复
		@param:		playerFull	(场地是否满员)
		@type：		BOOL
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
		请求加入个人竞技
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
		获取玩家的MAILBOX的回调
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
		随机抽取玩家
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
		定时向服务器发送请求
		"""
		if self.levelList == []:
			return
		else:
			level = self.levelList.pop(0)
			self.randomSelect( level )
			self.addTimer( 3, 0, ROLE_COMPETITION_SELECT)
		

	def noticePlayer( self ):
		"""
		通知被抽取的玩家
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
		结束时的操作
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
		玩家进入副本之前的操作，符合条件允许进入副本
		"""
		if BigWorld.globalData.has_key("AS_RoleCompetitionAdmission"):
			if self.hasSelectedBaseMailbox.has_key(playerName):
				playerBaseMB.cell.gotoSpace( mapName, position, direction )
				self.hasEnterNameDict[playerName] = level
			else:
				playerBaseMB.client.onStatusMessage( csstatus.ROLE_COMPETITION_VOICE_5, "")

	def addRoleCompetitionReward( self, playerName, level):
		"""
		通过邮件形式给玩家发送参与奖励
			参与奖励经验值=1404*（25+5*角色等级^1.2）
		"""

		itemDatas = []
		item = g_items.createDynamicItem( REWARD_EXP_ITEM_ID )
		#改变物品的经验值
		#pass
		if item:
			item.setLevel( level )
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )

		# 把信件发给邮件管理器
		BigWorld.globalData["MailMgr"].send(None, playerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", cschannel_msgs.FCWR_MAIL_ROLECOMPETITION_REWARD_TITLE, "", 0, itemDatas)
		
	def roleCompetition_Record( self, playerDBID, matchType, scoreOrRound, playerBase ):
		"""
		记录一次比赛信息
		"""
		RoleMatchRecorder.update( playerDBID, matchType, scoreOrRound, playerBase )
		
	def roleCompetition_end( self, notice):
		"""
		供GM指令结束比赛用
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