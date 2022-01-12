# -*- coding: gb18030 -*-

import random
import time
import BigWorld
import Love3
from bwdebug import *
import csconst
import csdefine
import cschannel_msgs
import cPickle
import items
from CrondDatas import CrondDatas
g_CrondDatas = CrondDatas.instance()
g_items = items.instance()
from NormalActivityManager import NormalActivityManager
from config.server.TDBattleRewardConfig import Datas as rewardDatas

T_BOSS_DIE = 1111
D_BOSS_DIE = 2222
T_CLEAR_RESULT = 3333
D_CLEAR_RESULT = 4444

class PlayerDataItem:
	"""
	一个参与玩家的数据记录
	"""
	def __init__( self, playerName, playerLevel, playerBase, playerTongName, bossID, monsterIDs ):
		self.playerName = playerName
		self.playerLevel = playerLevel
		self.playerTongName = playerTongName
		self.base = playerBase
		self.bossID = bossID
		self.monsterIDs = monsterIDs
		self.isFirstDamager = False
		self.damageRecord = {}
		self.totalDamage = 0
		self.totalCureHP = 0
		self.dieCount = 0
		self.damageOrder = 0
		self.cureOrder = 0
		self.dieOrder = 0
		self.damageReward = []
		self.cureReward = []
		self.dieReward = []
		self.firDamageReward = []
	
	def recordDamageData( self, m_className, damage ):
		"""
		"""
		if self.damageRecord.has_key( m_className ):
			self.damageRecord[ m_className ] += damage
		else:
			self.damageRecord[ m_className ] = damage
	
	def recordCureData( self, cureHP ):
		"""
		"""
		self.totalCureHP += cureHP
	
	def recordDieData( self, playerName ):
		"""
		"""
		self.dieCount += 1
	
	def hasBossDamage( self ):
		"""
		是否对Boss有伤害
		"""
		return self.bossID in self.damageRecord.keys()
	
	def calTotalDamage( self ):
		"""
		计算总伤害值
		"""
		for className, damage in self.damageRecord.iteritems():
			if className == self.bossID:
				self.totalDamage += damage
			else:
				self.totalDamage += damage / 2
	
	def updateBase( self, playerBase ):
		"""
		更新玩家base
		"""
		self.base = playerBase
	
class CampWarItem:
	"""
	一个阵营的活动数据
	"""
	def __init__( self, mgr, camp, bossID, monsterIDs ):
		self.mgr = mgr
		self.camp = camp
		self.bossID = bossID
		self.monsterIDs = monsterIDs
		self.firstDamager = None				# 首触玩家
		self.playerDataItems = []			# 玩家数据实例列表
		self.resultList = []
		self.clearTimer = 0					# 清除数据timer
	
	def onBossChangeFree( self ):
		"""
		boss脱离清空数据
		"""
		self.firstDamager = None
		self.playerDataItems = []

	def getPlyerDataItem( self, playerName ):
		"""
		获取某个玩家的数据
		"""
		for i in self.playerDataItems:
			if i.playerName == playerName:
				return i
		return None
	
	def addPlayerDataItem( self, playerDataItem ):
		"""
		"""
		self.playerDataItems.append( playerDataItem )
		num = len( self.playerDataItems )
		if num in [ 50, 100, 150, 200 ]:
			WARNING_MSG( "XianMoLunZhan: Joined player num is %i." % num )

	def recordDamageData( self, m_className, playerBase, playerName, playerLevel, playerTongName, damage ):
		"""
		记录伤害数据
		"""
		playerDataItem = self.getPlyerDataItem( playerName )
		if not playerDataItem:
			playerDataItem = PlayerDataItem( playerName, playerLevel, playerBase, playerTongName, self.bossID, self.monsterIDs )
			self.addPlayerDataItem( playerDataItem )
		
		playerDataItem.recordDamageData( m_className, damage )
			
		if self.firstDamager == None and m_className == self.bossID and playerLevel >= csconst.TDB_FIRDAMAGE_LEVEL_LIMIT:
			playerDataItem.isFirstDamager = True
			self.firstDamager = playerDataItem
			playerDataItem.firDamageReward = self.getReward( csdefine.TDB_FIRST_DAMAGE_REWARD )
	
	def recordCureData( self, curePlayerName, playerLevel, playerBase, playerTongName, cureHP ):
		"""
		"""
		playerDataItem = self.getPlyerDataItem( curePlayerName )
		if not playerDataItem:
			playerDataItem = PlayerDataItem( curePlayerName, playerLevel, playerBase, playerTongName, self.bossID, self.monsterIDs )
			self.addPlayerDataItem( playerDataItem )
		playerDataItem.recordCureData( cureHP )

	def recordDieData( self, playerName, playerLevel, playerBase, playerTongName ):
		"""
		记录死亡数据
		"""
		playerDataItem = self.getPlyerDataItem( playerName )
		if not playerDataItem:
			playerDataItem = PlayerDataItem( playerName, playerLevel, playerBase, playerTongName, self.bossID, self.monsterIDs )
			self.addPlayerDataItem( playerDataItem )
		
		playerDataItem.recordDieData( playerName )

	def onPlayerLogin( self, playerBase, playerName ):
		"""
		玩家登录
		"""
		playerBase.client.TDB_showActButton()		# 显示活动图标
		playerDataItem = self.getPlyerDataItem( playerName )
		if playerDataItem:
			playerDataItem.updateBase( playerBase )
	
	def onClickActButton( self, playerBase ):
		"""
		"""
		if self.clearTimer > 0:			# 战斗已经结束
			playerBase.client.TDB_receiveReslut( self.resultList )
		else:
			playerBase.cell.TDB_showTransWindow()

	def createDamageTop( self ):
		"""
		生成伤害排名
		"""
		for playerData in self.playerDataItems:
			if not playerData.hasBossDamage() or playerData.totalDamage < csconst.TDB_TOP_DAMAGE_LIMIT:			#必须有boss伤害且达到最低伤害量
				continue
			
			order = 1
			for i in self.playerDataItems:
				if i.totalDamage > playerData.totalDamage:
					order += 1
			if order <= csconst.TDB_TOP_DAMAGE_ORDER_LIMIT:					# 只排20名
				playerData.damageOrder = order
				playerData.damageReward = self.getReward( csdefine.TDB_DAMAGE_REWARD, order )

	def createCureTop( self ):
		"""
		生成治疗排名
		"""
		for playerData in self.playerDataItems:
			if not playerData.hasBossDamage() or playerData.totalCureHP < csconst.TDB_TOP_DAMAGE_LIMIT:			# 必须对boss有伤害且达到最低治疗量
				continue
				
			order = 1
			for i in self.playerDataItems:
				if i.totalCureHP > playerData.totalCureHP:
					order += 1
			if order <= csconst.TDB_TOP_CURE_ORDER_LIMIT:					# 只排3名
				playerData.cureOrder = order
				playerData.cureReward = self.getReward( csdefine.TDB_CURE_REWARD, order )

	def createDieTop( self ):
		"""
		生成死亡次数排名
		"""
		for playerData in self.playerDataItems:
			if playerData.damageOrder == 0:		# 在伤害榜中取死亡排名
				continue
			
			order = 1
			for pData in self.playerDataItems:
				if pData.damageOrder == 0:
					continue
				if pData.dieCount < playerData.dieCount:
					order += 1
				elif pData.dieCount == playerData.dieCount:
					if pData.totalDamage > playerData.totalDamage:
						order += 1
			if order <= csconst.TDB_TOP_DIE_ORDER_LIMIT:					# 只排20名
				playerData.dieOrder = order
				playerData.dieReward = self.getReward( csdefine.TDB_DEATH_REWARD, order )

	def createBattleResult( self ):
		"""
		生成界面需要的结果数据
		"""
		for playerData in self.playerDataItems:
			# 过滤掉不上榜的数据
			if playerData.damageOrder == 0 and playerData.cureOrder == 0 and playerData.dieOrder == 0 and not playerData.isFirstDamager:
				continue
			resultDict = {}
			resultDict[ "tongName" ] = playerData.playerTongName
			resultDict[ "damageOrder" ] = playerData.damageOrder
			resultDict[ "playerName" ] = playerData.playerName
			resultDict[ "totalDamage" ] = playerData.totalDamage
			resultDict[ "cureOrder" ] = playerData.cureOrder
			resultDict[ "totalCureHP" ] = playerData.totalCureHP
			resultDict[ "dieOrder" ] = playerData.dieOrder
			resultDict[ "dieCount" ] = playerData.dieCount
			resultDict[ "isFirstDamager" ] = playerData.isFirstDamager
			resultDict[ "damageReward" ] = playerData.damageReward
			resultDict[ "cureReward" ] = playerData.cureReward
			resultDict[ "dieReward" ] = playerData.dieReward
			resultDict[ "firDamageReward" ] = playerData.firDamageReward
			self.resultList.append( resultDict.copy() )
	
	def clearResult( self, timerID ):
		"""
		清除结果
		"""
		INFO_MSG( "XianMoLunZhan: Clear result( camp: %s )." % self.camp )
		Love3.g_baseApp.globalRemoteCallCampClient( self.camp, "TDB_hideActButton", () )		# 隐藏活动图标
	
	def onEnd( self ):
		"""
		活动结束
		"""
		if self.clearTimer > 0:
			return
			
		if self.camp == csdefine.ENTITY_CAMP_TAOISM:
			self.clearTimer = self.mgr.addTimer( 20, 0, T_CLEAR_RESULT )			# 因为客户端显示传送确认框是15秒，这里给个20秒的延时
		else:
			self.clearTimer = self.mgr.addTimer( 20, 0, D_CLEAR_RESULT )
		# 显示传送确认框
		Love3.g_baseApp.globalRemoteCallCampCell( self.camp, "TDB_onBattleOver", ( int( BigWorld.globalData[ "TDBattleEndTime" ] ), ) )
		
	def onBossDie( self ):
		"""
		boss死了就显示结果并给奖励(活动结束销毁boss时不会调用到这个接口)
		"""
		INFO_MSG( "XianMoLunZhan: Boss die( camp: %s )" % self.camp )
		Love3.g_baseApp.globalRemoteCallCampCell( self.camp, "TDB_onBattleOver", ( int( BigWorld.globalData[ "TDBattleEndTime" ] ), ) )
		
		if self.camp == csdefine.ENTITY_CAMP_TAOISM:
			self.clearTimer = self.mgr.addTimer( 10 * 60, 0, T_CLEAR_RESULT )			# 10分中后清除结果
		else:
			self.clearTimer = self.mgr.addTimer( 10 * 60, 0, D_CLEAR_RESULT )
			
		# 这几步必须先做，而且顺序不能乱
		for playerData in self.playerDataItems:
			playerData.calTotalDamage()
		self.createDamageTop()
		self.createCureTop()
		self.createDieTop()
		self.createBattleResult()
			
		mostDamageRole = None				# 伤害首位玩家
		for playerData in self.playerDataItems:
			try:
				playerData.base.client.TDB_receiveReslut( self.resultList )
			except:
				pass
				
			# 发首触奖励
			if playerData.isFirstDamager:
				money = 0.8 * 100 * playerData.playerLevel * 1.5 ** ( 0.1 * playerData.playerLevel - 1 )
				content = cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_CONTENT_5
				self.sendReward( cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_TITLE_1, playerData.playerName, playerData.firDamageReward, money, content )
				
			# 发参与奖励
			if playerData.hasBossDamage():
				money = 0.6 * 100 * playerData.playerLevel * 1.5 ** ( 0.1 * playerData.playerLevel - 1 )
				items = self.getReward( csdefine.TDB_JOIN_REWARD )
				content = cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_CONTENT_4
				self.sendReward( cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_TITLE_2, playerData.playerName, items, money, content )
				# 只获得参与奖的话给个奖励提示
				if not playerData.isFirstDamager and playerData.damageOrder == 0 and playerData.dieOrder == 0 and playerData.cureOrder == 0:
					try:
						playerData.base.client.chat_onChannelMessage(csdefine.CHAT_CHANNEL_SC_HINT, 0, "", cschannel_msgs.TAOISM_AND_DEMON_BATTLE_JOIN_REWARD_NOTITY, [])
					except:
						pass
						
			# 发伤害奖励
			a = 0
			if  playerData.damageOrder != 0:
				if playerData.damageOrder == 1:
					a = 2
					mostDamageRole = playerData
				if 2 <= playerData.damageOrder <= 3:
					a = 1.5
				if 4 <= playerData.damageOrder <= 10:
					a = 1.2
				if 11 <= playerData.damageOrder <= 20:
					a = 1
				money = a * 100 * playerData.playerLevel * 1.5 ** ( 0.1 * playerData.playerLevel - 1 )
				content = cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_CONTENT_1 % playerData.damageOrder
				self.sendReward( cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_TITLE_3, playerData.playerName, playerData.damageReward, money, content )
			
			# 发死亡奖励
			if playerData.dieOrder != 0:
				if playerData.dieOrder == 1:
					money = 0.8 * 100 * playerData.playerLevel * 1.5 ** ( 0.1 * playerData.playerLevel - 1 )
				else:
					money = 0
				content = cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_CONTENT_3 % playerData.dieOrder
				self.sendReward( cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_TITLE_4, playerData.playerName, playerData.dieReward, money, content )
			
			# 发治疗奖励
			if playerData.cureOrder != 0:
				if playerData.cureOrder == 1:
					money = 1.4 * 100 * playerData.playerLevel * 1.5 ** ( 0.1 * playerData.playerLevel - 1 )
				else:
					money = 0
				content = cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_CONTENT_2 % playerData.cureOrder
				self.sendReward( cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_TITLE_5, playerData.playerName, playerData.cureReward, money, content )
					
		if self.firstDamager and mostDamageRole:
			if self.camp == csdefine.ENTITY_CAMP_TAOISM:
				msg = cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_NOTICE_T
			else:
				msg = cschannel_msgs.TAOISM_AND_DEMON_BATTLE_REWARD_NOTICE_D
			Love3.g_baseApp.anonymityBroadcast( msg % ( self.firstDamager.playerName, mostDamageRole.playerName ), [] )
			
	def getReward( self, rewardType, order = None ):
		"""
		从配置获取奖励
		@rewardType : 奖励类型 int
		@order : 名次 int
		"""
		def getOneParamItem( tupleList ):
			tempItems = []
			odds = random.random()
			rate = 0 
			for itemTuple in tupleList:
				if 0 <= odds < rate + itemTuple[2]:
					item = g_items.createDynamicItem( itemTuple[0], itemTuple[1] )
					if item:
						if item.isEquip():
							item.createRandomEffect()
						tempItems.append( item )
					break
				else:
					rate += itemTuple[2]
			return tempItems
		
		items = []				# [( id, amount ),...]
		for reward in rewardDatas:		# reward格式 { "RewardType": 1, "RewardOrderRange": (minOrder,maxOrder), "ItemsProbability": ( rate1, rate2,... ), "Param1": (( itemID, itemAmount, itemRate ),()), "Param2":(),... }
			if reward["RewardType"] != rewardType:
				continue
			configRan = reward["RewardOrderRange"]
			if len( configRan ) == 0 or order in range( configRan[ 0 ], configRan[ 1 ] + 1 ):
				odds = random.random()
				rateList = reward["ItemsProbability"]
				for index, rate in enumerate( rateList ):
					if odds <= rate:
						paramStr = "Param" + str( index + 1 )
						if not reward.has_key( paramStr ):
							continue
						oneParamList = reward[ paramStr ]
						items.extend( getOneParamItem( oneParamList ) )
		return items

	def sendReward( self, title, playerName, items, money, content = "" ):
		"""
		邮件发奖励
		"""
		if len( items ) == 0:
			return
		itemDatas = []
		for i in items:
			tempDict = i.addToDict()
			del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
			itemData = cPickle.dumps( tempDict, 2 )
			itemDatas.append( itemData )
		if len( itemDatas ) != 0:
			BigWorld.globalData["MailMgr"].send( None, playerName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC,"", title, content, money, itemDatas )



class TaoismAndDemonBattleMgr( BigWorld.Base, NormalActivityManager ):

	def __init__(self):
		"""
		仙魔论战活动
		"""
		BigWorld.Base.__init__( self )
		
		self.noticeMsg 			= cschannel_msgs.TAOISM_AND_DEMON_BATTLE_PRE_NOTICE
		self.startMsg			= cschannel_msgs.TAOISM_AND_DEMON_BATTLE_START_NOTICE
		self.endMgs				= cschannel_msgs.TAOISM_AND_DEMON_BATTLE_END_NOTICE
		self.errorStartLog 		= cschannel_msgs.TAOISM_AND_DEMON_BATTLE_START_ERROR_NOTICE
		self.errorEndLog 		= cschannel_msgs.TAOISM_AND_DEMON_BATTLE_END_ERROR_NOTICE
		self.spawnMonsterCount  = 2
		self.globalFlagKey		= "AS_TaoismDemonBattle"
		self.managerName 		= "TaoismAndDemonBattleMgr"
		self.crondNoticeKey		= "TaoismDemonBattle_Notice"
		self.crondStartKey		= "TaoismDemonBattle_Start"
		self.crondEndKey		= "TaoismDemonBattle_End"

		NormalActivityManager.__init__( self )
		
		self.taoismWarItem = None
		self.demonWarItem = None
		
	def onStart( self ):
		"""
		"""
		NormalActivityManager.onStart( self )
		persistSecond = g_CrondDatas.getTaskPersist( self.crondStartKey ) * 60
		if persistSecond == 0:
			persistSecond = 4 * 60 * 60
		BigWorld.globalData["TDBattleEndTime"] = time.time() + persistSecond
		Love3.g_baseApp.globalRemoteCallClient( "TDB_showActButton" )
		self.taoismWarItem = CampWarItem( self, csdefine.ENTITY_CAMP_TAOISM, csconst.TDB_BOSS_CLASSNAME_T, csconst.TDB_MONSTER_CLASSNAMES_T )
		self.demonWarItem = CampWarItem( self, csdefine.ENTITY_CAMP_DEMON, csconst.TDB_BOSS_CLASSNAME_D, csconst.TDB_MONSTER_CLASSNAMES_D )
	
	def onEnd( self ):
		"""
		"""
		NormalActivityManager.onEnd( self )
		if self.taoismWarItem:
			self.taoismWarItem.onEnd()
		if self.demonWarItem:
			self.demonWarItem.onEnd()
		if BigWorld.globalData.has_key( "TDBattleEndTime" ):
			del BigWorld.globalData["TDBattleEndTime"]
	
	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == T_BOSS_DIE:
			self.taoismWarItem.onBossDie()
		if userArg == D_BOSS_DIE:
			self.demonWarItem.onBossDie()
		if userArg == T_CLEAR_RESULT:
			if self.taoismWarItem and self.taoismWarItem.clearTimer == id:
				self.taoismWarItem.clearResult( id )
				self.taoismWarItem = None
		if userArg == D_CLEAR_RESULT:
			if self.demonWarItem and self.demonWarItem.clearTimer == id:
				self.demonWarItem.clearResult( id )
				self.demonWarItem = None
			
		NormalActivityManager.onTimer( self, id, userArg )
		
	def recordDamageData( self, m_className, playerCamp, playerBase, playerName, playerLevel, playerTongName, damage ):
		"""
		define method
		记录伤害数据
		"""
		if playerCamp == csdefine.ENTITY_CAMP_TAOISM and self.taoismWarItem:
			self.taoismWarItem.recordDamageData( m_className, playerBase, playerName, playerLevel, playerTongName, damage )
		elif playerCamp == csdefine.ENTITY_CAMP_DEMON and self.demonWarItem:
			self.demonWarItem.recordDamageData( m_className, playerBase, playerName, playerLevel, playerTongName, damage )
	
	def recordCureData( self, curePlayerName, playerLevel, playerCamp, playerBase, playerTongName,  cureHP ):
		"""
		define method
		记录治疗数据
		"""
		if playerCamp == csdefine.ENTITY_CAMP_TAOISM and self.taoismWarItem:
			self.taoismWarItem.recordCureData( curePlayerName, playerLevel, playerBase, playerTongName, cureHP )
		elif playerCamp == csdefine.ENTITY_CAMP_DEMON and self.demonWarItem:
			self.demonWarItem.recordCureData( curePlayerName, playerLevel, playerBase, playerTongName, cureHP )
		
	def recordDieData( self, playerCamp, playerBase, playerName, playerLevel, playerTongName ):
		"""
		define method
		记录玩家活动中死亡次数
		"""
		if playerCamp == csdefine.ENTITY_CAMP_TAOISM and self.taoismWarItem:
			self.taoismWarItem.recordDieData( playerName, playerLevel, playerBase, playerTongName )
		elif playerCamp == csdefine.ENTITY_CAMP_DEMON and self.demonWarItem:
			self.demonWarItem.recordDieData( playerName, playerLevel, playerBase, playerTongName )
			
	def onPlayerLogin( self, playerBase, playerName ):
		"""
		define method
		玩家登录
		"""
		if self.taoismWarItem:
			self.taoismWarItem.onPlayerLogin( playerBase, playerName )
		if self.demonWarItem:
			self.demonWarItem.onPlayerLogin( playerBase, playerName )
	
	def onBossChangeFree( self, bossClassName ):
		"""
		define method
		boss脱离战斗
		"""
		if self.taoismWarItem and self.taoismWarItem.bossID == bossClassName:
			self.taoismWarItem.onBossChangeFree()
		elif  self.demonWarItem and self.demonWarItem.bossID == bossClassName:
			self.demonWarItem.onBossChangeFree()
	
	def onBossDie( self, bossClassName ):
		"""
		define method
		boss死了
		"""
		if BigWorld.globalData["AS_TaoismDemonBattle"] == False:			# 活动已结束，boss自动销毁不做任何事情
			return
		if self.taoismWarItem and self.taoismWarItem.bossID == bossClassName:
			self.addTimer( 3, 0, T_BOSS_DIE )			# 显示榜单
		elif self.demonWarItem and self.demonWarItem.bossID == bossClassName:
			self.addTimer( 3, 0, D_BOSS_DIE )
			
	def onClickActButton( self, playerBase, playerCamp ):
		"""
		define method
		玩家点击活动图标
		"""
		if playerCamp == csdefine.ENTITY_CAMP_TAOISM and self.taoismWarItem:
			self.taoismWarItem.onClickActButton( playerBase )
		elif playerCamp == csdefine.ENTITY_CAMP_DEMON and self.demonWarItem:
			self.demonWarItem.onClickActButton( playerBase )
		else:
			ERROR_MSG( "XianMoLunZhan: Activity flag invalid! ( playerCamp: %s )" % playerCamp )
		