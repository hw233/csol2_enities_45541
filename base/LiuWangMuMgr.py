# -*- coding: gb18030 -*-

import BigWorld
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
from NormalActivityManager import NormalActivityManager
import Love3
import cPickle
import csdefine
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
from TimeString import TimeString
from config.server.LiuWangMuReward import Datas as g_rewardDatas
END 			= 2013
FLOORLIMIT		= 2 #目前只开启前两层
NEXTFLOOR		= 2014
bossesInfo = {"0;2;4":cschannel_msgs.LIUWANGMU_BOSS_DIJIANG,"1;3;5":cschannel_msgs.LIUWANGMU_BOSS_WUDANGSHENMU}
class LiuWangMuMgr( BigWorld.Base, NormalActivityManager ):
	#六王墓整个流程流程通过两个参数控制，一个是BigWorld.globalData[self.globalFlagKey]
	#另一个是self.floorTimeLimit(每层开放的时间)
	#有部分boss的逻辑改为AI控制
	def __init__(self):
		"""
		"""
		BigWorld.Base.__init__( self )
		self.noticeMsg 			= cschannel_msgs.BCT_LIUWANGMU_BEGIN_NOTIFY_0
		self.startMsg 			= cschannel_msgs.BCT_LIUWANGMU_BEGIN_NOTIFY
		self.notice_DIJIANG		= cschannel_msgs.LIUWANGMU_BOSS_DIJIANG
		self.notice_WUDANGSHENMU = cschannel_msgs.LIUWANGMU_BOSS_WUDANGSHENMU
		self.endMgs 			= ""
		self.errorStartLog 		= cschannel_msgs.LIUWANGMU_NOTICE_1
		self.errorEndLog 		= cschannel_msgs.LIUWANGMU_NOTICE_2
		self.globalFlagKey		= "AS_LiuWangMu"
		self.managerName 		= "LiuWangMuMgr"
		self.crondNoticeKey		= "liuwangmu_start_notice"
		self.crondStartKey		= "liuwangmu_Start"
		self.crondBoss1NoticeKey = "liuwangmu_DiJiang"
		self.crondBoss2NoticeKey = "liuwangmu_WuDangShenMu"
		self.crondEndKey		= "liuwangmu_End"
		NormalActivityManager.__init__( self )	
		self.spaceBases =[]
		self.floorTimeLimit = 3600
		self.nextFloorTimer = None

	def registerSpace(self, baseMailbox, spaceName):
		"""
		define method 
		保存活动空间的base
		param className:副本空间的名称，可以区分是第几层
		"""
		if baseMailbox not in self.spaceBases:  #只有在第一次进入一个副本空间的时候才加
			self.spaceBases.append(baseMailbox)

	def registerCrond( self ):
		"""
		将自己注册到计划任务服务系统
		"""
		# 活动事件绑定
		taskEvents = {
					  	self.crondNoticeKey : "onStartNotice",
					  	self.crondStartKey : "onStart",
					  	self.crondBoss1NoticeKey: "onNoticeBossDiJiang",
					  	self.crondBoss2NoticeKey: "onNoticeBossWuDangShenMu",
						self.crondEndKey :	"onEnd",
					  }

		for taskName, callbackName in taskEvents.iteritems():
			for cmd in g_CrondDatas.getTaskCmds( taskName ):
				BigWorld.globalData["Crond"].addScheme( cmd, self, callbackName )	
				
		BigWorld.globalData["Crond"].addAutoStartScheme( "liuwangmu_Start", self, "onStart")

		
	def set_floorTimeLimit(self, minutes):
		"""
		define method
		GM测试，用于调整每层开放时间
		"""
		DEBUG_MSG("GM use cmd to set_floorTimeLimit!")
		self.floorTimeLimit = minutes * 60  #每层开放时间
	
	def set_openFloor(self, floorNum):
		"""
		define method
		GM测试，用于调整开放哪几层		
		"""
		BigWorld.globalData[self.globalFlagKey] = floorNum
		self.liuwangmuGlobalFlagKeyChange()
		
	
	def liuwangmuGlobalFlagKeyChange(self):
		#每次BigWorld.globalData[self.globalFlagKey]值变化的时候，会做一些特殊处理
		globalFlagKey = BigWorld.globalData[self.globalFlagKey]
		if globalFlagKey == 2: #当开启第二层时
			#处理boss刷新通告
			#现在直接在活动计划中添加boss刷新的公告任务
			"""
			for key,value in bossesInfo.items():
				if TimeString(key).timeCheck():
					Love3.g_baseApp.anonymityBroadcast( value, [] )
			"""
		elif globalFlagKey == 0: #活动结束
			INFO_MSG("30 seconds later to close activity liuwangmu!")		
			self.addTimer(30, 0, END)	
			#通知副本结束
			for spaceBase in self.spaceBases:			
				spaceBase.cell.activityClosed()
				spaceBase.startCloseCountDownTimer( 30 )#30秒销毁倒计时					
				
	def onStart( self ):
		"""
		define method.
		活动开始
		"""
		if BigWorld.globalData.has_key( self.globalFlagKey ) and BigWorld.globalData[self.globalFlagKey] == True:
			curTime = time.localtime()
			ERROR_MSG( self.errorStartLog%(curTime[3],curTime[4] ) )
			return
		if self.startMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.startMsg, [] )
		BigWorld.globalData[self.globalFlagKey] = 1  #通过这个值的变化控制活动流程
		self.liuwangmuGlobalFlagKeyChange()
		self.nextFloorTimer =  self.addTimer(self.floorTimeLimit, 0, NEXTFLOOR) #定时开启下一层
		INFO_MSG( self.globalFlagKey, "start", "" )

	def onNoticeBossDiJiang( self ):
		"""
		define method 
		"""
		if self.notice_DIJIANG != "":
			Love3.g_baseApp.anonymityBroadcast( self.notice_DIJIANG, [] )
		INFO_MSG( self.globalFlagKey, "noticebossDiJiang", "")
			
	def onNoticeBossWuDangShenMu( self ):
		"""
		define method
		"""
		if self.notice_WUDANGSHENMU != "":
			Love3.g_baseApp.anonymityBroadcast( self.notice_WUDANGSHENMU, [] )
		INFO_MSG(self.globalFlagKey, "noticebossWuDangShenMu", "")
		
	def onEnd( self ):
		"""
		define method.
		活动结束
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.LIUWANGMU_SPACE_CLOSE, [] )
		BigWorld.globalData[self.globalFlagKey] = 0
		self.delTimer(self.nextFloorTimer)   #由于boss死亡会提前结束，这里要把第二层的timer取消。
		self.liuwangmuGlobalFlagKeyChange()
		INFO_MSG( self.globalFlagKey, "end", "")
		

	def onBossDied( self ):
		"""
		define method 
		由于之前的boss死亡触发onEnd,不容易区分是那种情况造成活动
		把boss死亡造成的活动结束流程独立出来
		与活动到了时间自动结束的onEnd不一样的地方是不会通告boss活动结束
		"""
		DEBUG_MSG("liuwangmu boss is killed, turn down the activity!")
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.LIUWANGMU_SPACE_CLOSE, [] )
		BigWorld.globalData[self.globalFlagKey] = 0
		self.delTimer(self.nextFloorTimer)   #由于boss死亡会提前结束，这里要把第二层的timer取消。
		INFO_MSG("30 seconds later to close activity liuwangmu!")		
		self.addTimer(30, 0, END)	
		#通知副本结束
		for spaceBase in self.spaceBases:	
			spaceBase.startCloseCountDownTimer( 30 )#30秒销毁倒计时
		INFO_MSG( self.globalFlagKey, "end", "")

	def onTimer( self, id, userArg ):
		"""
		"""		
		if userArg == END:#最后的清理工作
			DEBUG_MSG("activity liuwangmu over ,clear the liuwangmumgr datas!")
			self.spaceBases = []
		elif userArg == NEXTFLOOR:
			DEBUG_MSG("NEXTFLOOR is %d 。"%BigWorld.globalData[self.globalFlagKey])
			if BigWorld.globalData[self.globalFlagKey] < FLOORLIMIT :   
				BigWorld.globalData[self.globalFlagKey] += 1 #每隔固定时间开启下一层
				self.liuwangmuGlobalFlagKeyChange()
				self.nextFloorTimer = self.addTimer(self.floorTimeLimit, 0, NEXTFLOOR)
			else:
				self.onEnd()
		NormalActivityManager.onTimer( self, id, userArg )

	def sendReward(self, type, playersName, tongsName, msg):
		"""
		define method
		param type:区分boss杀死与未杀死的奖励 1为杀死，0 为未杀死
		param playersName: all players'names which make damage to boss
		param tongsName:  all tongs'names which make damage to boss
		"""	
		INFO_MSG("liuwangmu sendReward type:%d, playersName:%s, tongsName:%s,  msg:%s"%(type, playersName, tongsName, msg))
		self.rankList(msg)
		self.sendPlayersReward(type, playersName)
		self.sendTongsReward(type, tongsName)
		
	
	def rankList(self, msg):
		INFO_MSG("SHOW LIU_WANG_MU_ACTIVITY_RESULT",msg)
		for spaceBase in self.spaceBases:
			spaceBase.cell.rankList(msg)
	
	def sendPlayersReward(self, type, playersName):
		"""
		type == 1 represent BossKilled
		type == 0 represent BossNotKilled
		BossKilled = 1 
		BossNotKilled = 0
		IsPlayerName = 0
		IsTongName = 1
		index 要加1是因为配置的是从1开始，而且计算出的index是从0开始
		g_rewardDatas = {type:playerName:index:{"tongContribute":0, "money":0, "playerExp":0, "playerPotential":0, "itemIDs":[]}}
		"""
		title = cschannel_msgs.LIUWANGMU_REWARD_TITLE
		mailType = csdefine.MAIL_TYPE_QUICK
		senderType = csdefine.MAIL_SENDER_TYPE_NPC
		for playerName in playersName:
			context = ""
			money = 0
			itemIDs = []
			itemDatas = ""
			index = playersName.index(playerName)
			if index <10:
				itemIDs = g_rewardDatas[type][0][index+1]["itemIDs"]
				money = g_rewardDatas[type][0][index+1]["money"]
			else:#从第11名开始的奖励都是一样的
				itemIDs = g_rewardDatas[type][0][11]["itemIDs"] 
				money = g_rewardDatas[type][0][11]["money"]
			for itemID in itemIDs:
				item = g_items.createDynamicItem( itemID )
				if item.isEquip():
					item.createRandomEffect()
				tempDict = item.addToDict()
				del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
				itemData = cPickle.dumps( tempDict, 0 )
				itemDatas.append( itemData )
			if type:  #bosskilled 
				if index <10:
					context = cschannel_msgs.LIUWANGMU_REWARD_PLAYER_KILLEDBOSS_INRANKLIST %(playerName, index+1)
				else:
					context = cschannel_msgs.LIUWANGMU_REWARD_PLAYER_KILLEDBOSS_NOTINRANKLIST %playerName
			else: #boss not killed 
				if index <10:
					context = cschannel_msgs.LIUWANGMU_REWARD_PLAYER_NOTKILLEDBOSS_INRANKLIST %(playerName, index+1)
				else:
					context = cschannel_msgs.LIUWANGMU_REWARD_PLAYER_NOTKILLEDBOSS_NOTINRANKLIST %playerName
			BigWorld.globalData["MailMgr"].send(None, playerName, mailType, senderType,"", title, context, money, itemDatas)
			INFO_MSG("send liuwangmureward mail to %s ,title is %s,context is %s, money is %d, itemDatas is %s "%(playerName, title ,context , money, itemDatas))	
					
		
	def sendTongsReward(self, type, tongsName):
		"""
		type == 1 represent BossKilled
		type == 0 represent BossNotKilled
		BossKilled = 1
		BossNotKilled = 0
		IsPlayerName = 0
		IsTongName = 1
		index 要加1是因为配置的是从1开始，而且计算出的index是从0开始
		g_rewardDatas = {type:tongName:index:{"tongMoney":0, "tongExp":0, "itemIDs":[]}}
		"""
		if tongsName is None:
			return
		for tongName in tongsName:
			index = tongsName.index(tongName)
			BigWorld.globalData["TongManager"].findChiefNameByTongName(type, index, tongName)

	def sendLiuWangMuRewardToTongChief(self, type, index, tongName, chiefName):
		"""
		define method, call by TongManager
		"""
		money = 0
		title = cschannel_msgs.LIUWANGMU_REWARD_TITLE
		mailType = csdefine.MAIL_TYPE_QUICK
		senderType = csdefine.MAIL_SENDER_TYPE_NPC
		context = ""
		itemIDs = []
		itemDatas = ""
		tongExp = 0
		tongMoney = 0
		if index < 3:
			tongExp = g_rewardDatas[type][1][index+1]["tongExp"]
			tongMoney = g_rewardDatas[type][1][index+1]["tongMoney"]
			itemIDs = g_rewardDatas[type][1][index+1]["itemIDs"]
		else:#从第4名开始的奖励都是一样的
			tongExp = g_rewardDatas[type][1][4]["tongExp"]
			tongMoney = g_rewardDatas[type][1][4]["tongMoney"]
			itemIDs = g_rewardDatas[type][1][4]["itemIDs"]				
		for itemID in itemIDs:
			item = g_items.createDynamicItem( itemID )
			if item.isEquip():
				item.createRandomEffect()
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 0 )
			itemDatas.append( itemData )
		if type:  #bosskilled 
			if index <3:
				context = cschannel_msgs.LIUWANGMU_REWARD_TONG_KILLEDBOSS_INRANKLIST %(tongName, index+1,tongExp, tongMoney)
			else:
				context = cschannel_msgs.LIUWANGMU_REWARD_TONG_KILLEDBOSS_NOTINRANKLIST %(tongName,tongExp, tongMoney)
		else: #boss not killed 
			if index <3:
				context = cschannel_msgs.LIUWANGMU_REWARD_TONG_NOTKILLEDBOSS_INRANKLIST %(tongName, index+1,tongExp, tongMoney)
			else:
				context = cschannel_msgs.LIUWANGMU_REWARD_TONG_NOTKILLEDBOSS_NOTINRANKLIST %(tongName,tongExp, tongMoney)
			#if chiefName:  #在通过帮会查找帮主的时候，如果没有找到就不会进入给帮主发邮件奖励
		BigWorld.globalData["MailMgr"].send(None, chiefName, mailType, senderType,"", title, context, money, itemDatas)
		INFO_MSG("send liuwangmureward mail to tong chiefName %s  ,title is %s,,context is %s, money is %d, itemDatas is %s "%(chiefName, title, context, money, itemDatas))					
	
	