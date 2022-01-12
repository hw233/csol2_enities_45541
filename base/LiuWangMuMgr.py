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
FLOORLIMIT		= 2 #Ŀǰֻ����ǰ����
NEXTFLOOR		= 2014
bossesInfo = {"0;2;4":cschannel_msgs.LIUWANGMU_BOSS_DIJIANG,"1;3;5":cschannel_msgs.LIUWANGMU_BOSS_WUDANGSHENMU}
class LiuWangMuMgr( BigWorld.Base, NormalActivityManager ):
	#����Ĺ������������ͨ�������������ƣ�һ����BigWorld.globalData[self.globalFlagKey]
	#��һ����self.floorTimeLimit(ÿ�㿪�ŵ�ʱ��)
	#�в���boss���߼���ΪAI����
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
		�����ռ��base
		param className:�����ռ�����ƣ����������ǵڼ���
		"""
		if baseMailbox not in self.spaceBases:  #ֻ���ڵ�һ�ν���һ�������ռ��ʱ��ż�
			self.spaceBases.append(baseMailbox)

	def registerCrond( self ):
		"""
		���Լ�ע�ᵽ�ƻ��������ϵͳ
		"""
		# ��¼���
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
		GM���ԣ����ڵ���ÿ�㿪��ʱ��
		"""
		DEBUG_MSG("GM use cmd to set_floorTimeLimit!")
		self.floorTimeLimit = minutes * 60  #ÿ�㿪��ʱ��
	
	def set_openFloor(self, floorNum):
		"""
		define method
		GM���ԣ����ڵ��������ļ���		
		"""
		BigWorld.globalData[self.globalFlagKey] = floorNum
		self.liuwangmuGlobalFlagKeyChange()
		
	
	def liuwangmuGlobalFlagKeyChange(self):
		#ÿ��BigWorld.globalData[self.globalFlagKey]ֵ�仯��ʱ�򣬻���һЩ���⴦��
		globalFlagKey = BigWorld.globalData[self.globalFlagKey]
		if globalFlagKey == 2: #�������ڶ���ʱ
			#����bossˢ��ͨ��
			#����ֱ���ڻ�ƻ������bossˢ�µĹ�������
			"""
			for key,value in bossesInfo.items():
				if TimeString(key).timeCheck():
					Love3.g_baseApp.anonymityBroadcast( value, [] )
			"""
		elif globalFlagKey == 0: #�����
			INFO_MSG("30 seconds later to close activity liuwangmu!")		
			self.addTimer(30, 0, END)	
			#֪ͨ��������
			for spaceBase in self.spaceBases:			
				spaceBase.cell.activityClosed()
				spaceBase.startCloseCountDownTimer( 30 )#30�����ٵ���ʱ					
				
	def onStart( self ):
		"""
		define method.
		���ʼ
		"""
		if BigWorld.globalData.has_key( self.globalFlagKey ) and BigWorld.globalData[self.globalFlagKey] == True:
			curTime = time.localtime()
			ERROR_MSG( self.errorStartLog%(curTime[3],curTime[4] ) )
			return
		if self.startMsg != "":
			Love3.g_baseApp.anonymityBroadcast( self.startMsg, [] )
		BigWorld.globalData[self.globalFlagKey] = 1  #ͨ�����ֵ�ı仯���ƻ����
		self.liuwangmuGlobalFlagKeyChange()
		self.nextFloorTimer =  self.addTimer(self.floorTimeLimit, 0, NEXTFLOOR) #��ʱ������һ��
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
		�����
		"""
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.LIUWANGMU_SPACE_CLOSE, [] )
		BigWorld.globalData[self.globalFlagKey] = 0
		self.delTimer(self.nextFloorTimer)   #����boss��������ǰ����������Ҫ�ѵڶ����timerȡ����
		self.liuwangmuGlobalFlagKeyChange()
		INFO_MSG( self.globalFlagKey, "end", "")
		

	def onBossDied( self ):
		"""
		define method 
		����֮ǰ��boss��������onEnd,���������������������ɻ
		��boss������ɵĻ�������̶�������
		������ʱ���Զ�������onEnd��һ���ĵط��ǲ���ͨ��boss�����
		"""
		DEBUG_MSG("liuwangmu boss is killed, turn down the activity!")
		Love3.g_baseApp.anonymityBroadcast( cschannel_msgs.LIUWANGMU_SPACE_CLOSE, [] )
		BigWorld.globalData[self.globalFlagKey] = 0
		self.delTimer(self.nextFloorTimer)   #����boss��������ǰ����������Ҫ�ѵڶ����timerȡ����
		INFO_MSG("30 seconds later to close activity liuwangmu!")		
		self.addTimer(30, 0, END)	
		#֪ͨ��������
		for spaceBase in self.spaceBases:	
			spaceBase.startCloseCountDownTimer( 30 )#30�����ٵ���ʱ
		INFO_MSG( self.globalFlagKey, "end", "")

	def onTimer( self, id, userArg ):
		"""
		"""		
		if userArg == END:#����������
			DEBUG_MSG("activity liuwangmu over ,clear the liuwangmumgr datas!")
			self.spaceBases = []
		elif userArg == NEXTFLOOR:
			DEBUG_MSG("NEXTFLOOR is %d ��"%BigWorld.globalData[self.globalFlagKey])
			if BigWorld.globalData[self.globalFlagKey] < FLOORLIMIT :   
				BigWorld.globalData[self.globalFlagKey] += 1 #ÿ���̶�ʱ�俪����һ��
				self.liuwangmuGlobalFlagKeyChange()
				self.nextFloorTimer = self.addTimer(self.floorTimeLimit, 0, NEXTFLOOR)
			else:
				self.onEnd()
		NormalActivityManager.onTimer( self, id, userArg )

	def sendReward(self, type, playersName, tongsName, msg):
		"""
		define method
		param type:����bossɱ����δɱ���Ľ��� 1Ϊɱ����0 Ϊδɱ��
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
		index Ҫ��1����Ϊ���õ��Ǵ�1��ʼ�����Ҽ������index�Ǵ�0��ʼ
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
			else:#�ӵ�11����ʼ�Ľ�������һ����
				itemIDs = g_rewardDatas[type][0][11]["itemIDs"] 
				money = g_rewardDatas[type][0][11]["money"]
			for itemID in itemIDs:
				item = g_items.createDynamicItem( itemID )
				if item.isEquip():
					item.createRandomEffect()
				tempDict = item.addToDict()
				del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
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
		index Ҫ��1����Ϊ���õ��Ǵ�1��ʼ�����Ҽ������index�Ǵ�0��ʼ
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
		else:#�ӵ�4����ʼ�Ľ�������һ����
			tongExp = g_rewardDatas[type][1][4]["tongExp"]
			tongMoney = g_rewardDatas[type][1][4]["tongMoney"]
			itemIDs = g_rewardDatas[type][1][4]["itemIDs"]				
		for itemID in itemIDs:
			item = g_items.createDynamicItem( itemID )
			if item.isEquip():
				item.createRandomEffect()
			tempDict = item.addToDict()
			del tempDict["tmpExtra"]	# ȥ����Ʒ�����̵�����
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
			#if chiefName:  #��ͨ�������Ұ�����ʱ�����û���ҵ��Ͳ��������������ʼ�����
		BigWorld.globalData["MailMgr"].send(None, chiefName, mailType, senderType,"", title, context, money, itemDatas)
		INFO_MSG("send liuwangmureward mail to tong chiefName %s  ,title is %s,,context is %s, money is %d, itemDatas is %s "%(chiefName, title, context, money, itemDatas))					
	
	