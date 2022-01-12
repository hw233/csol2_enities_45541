# -*- coding: gb18030 -*-
#
# $Id: SpaceFace.py,v 1.10 2007-09-24 07:38:39 kebiao Exp $

"""
帮会建筑的接口
"""
import time
import cPickle
import cschannel_msgs
import BigWorld
from bwdebug import *
from MsgLogger import g_logger
import csstatus
import csdefine
import csconst
import random
import Function
import TongBuildingData
tongBuildingDatas = TongBuildingData.instance()
tongBuildingLevel = TongBuildingData.tbl_instance()
from items.ItemDataList import ItemDataList
g_items = ItemDataList.instance()

# 神兽复活时间
NAGUAL_REVIVE_TIME						= 60 * 60 * 2

# 任务定义
TASK_KEY_SHENSHOUTYPE_DATA				= 51						# 帮会神兽类别
TASK_KEY_BUILDLEVEL_DATA				= 53						# 帮会所有建筑的级别信息

#----------------------------------------------------------------------------------------------
CONST_PAY_BUILDING_SPEND_MONEY_TIME 	= 60 * 60					# 检测建筑维护费的收取时间间隔

class TongTerritory:
	"""
	帮会建筑的接口
	"""
	def __init__( self ):
		self.territoryMB = None					# 领地副本的basemailbox
		self._shenshouReviveTimeID = 0

		self.calcBuildingSpendMoney()

		# 复活帮会神兽
		if self.shenshouReviveTime > 0:
			self.addNagualReviveTimer()

		# 请求获得领地副本
		self.getTongManager().onTongEntityRequestTerritory( self, self.databaseID )

	#---------------------------------------------------------------------------------------------------------
	def onRegisterTerritory( self, territory ):
		"""
		define method.
		@param territory:领地副本的basemailbox
		"""
		self.territoryMB = territory
		if self.isLockedTerritoryNPC:
			self.territoryMB.lockTerritoryNPC()
			for itemData in self.items:
				self.territoryMB.onRegisterTongItem( itemData[ "itemID" ], itemData[ "amount" ] )

	def onRequestCreateTongTerritory( self, spaceDomain ):
		"""
		define method.
		帮会成员要求进入领地副本， 副本领域向帮会请求指定数据创建一个领地
		"""
		spaceDomain.onCreateTongTerritory( self.databaseID, self.level, self.jk_level, self.ssd_level, self.ck_level, \
											self.tjp_level, self.sd_level, self.yjy_level, self.shenshouType, self.shenshouReviveTime )

	#---------------------------------------------------------------------------------------------------------
	def createSendDataTask( self, memberDBID ):
		"""
		创建一个成员的异步数据发送任务
		"""
		# 向异步任务数据池添加帮会建设度信息的任务
		self.addSendDataTask( memberDBID, TASK_KEY_SHENSHOUTYPE_DATA, None )
		self.addSendDataTask( memberDBID, TASK_KEY_BUILDLEVEL_DATA, None )

	def onSendClientDelayDatas( self, key, memberBaseMailbox, datas ):
		"""
		发送数据到客户端 主要是异步发送一些帮会的信息
		@param key				: TASK_KEY_*** 定义的一些帮会任务关键字
		@param memberBaseMailbox: 该玩家的mailbox
		@param datas			:任务数据池
		@return type: 成功发送一个任务返回True 否则返回false
		"""
		if key == TASK_KEY_SHENSHOUTYPE_DATA:
			datas[ "tasks" ].pop( 0 )
			memberBaseMailbox.client.tong_onSetShenShouType( self.ssd_level, self.shenshouType )
			return True
			return True
		elif key == TASK_KEY_BUILDLEVEL_DATA:
			datas[ "tasks" ].pop( 0 )
			self.updateBuildingLevelToClient( memberBaseMailbox )
			return True
		return False

	#---------------------------------------------------------------------------------------------------------
	def chargeSpendMoney( self ):
		"""
		define method.
		收维护费
		"""
		if self.spendMoney > 0:
			return
		self.onPayBuildingSpendMoney()
		
	def onPayBuildingSpendMoney( self ):
		"""
		收取维护费
		"""
		tm = time.time()

		# 领地的维护费 = 所有建筑的维护费之和
		payMoney = int( self.buildingSpendMoney )
		
		if payMoney > self.getValidMoney():		# 要动用保底资金了
			for memberDBID, info in self._memberInfos.items():
				self.getMailMgr().send( None,  info.getName(), csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_NPC, \
					cschannel_msgs.SHARE_SYSTEM, cschannel_msgs.TONG_INFO_28, cschannel_msgs.TONG_INFO_29, 0, "" )
			
		if payMoney > self.money:
			self.spendMoney = payMoney - self.money
			if not self.isLockedTerritoryNPC:
				self.isLockedTerritoryNPC = True
				if self.territoryMB:
					self.territoryMB.lockTerritoryNPC()

		self.payMoney( payMoney, False, csdefine.TONG_CHANGE_MONEY_PAYSPENDMONEY )
		DEBUG_MSG( "Tong[%i,%s] PayBuildingSpendMoney: spendMoney=%i, payMoney=%i, time:%i" % ( self.databaseID, self.playerName, self.spendMoney, payMoney, time.time() ) )

		self.statusMessageToOnlineMember( csstatus.TONG_WHF_BU_ZU, Function.switchMoney( payMoney ) )

		self.writeToDB()

	#---------------------------------------------------------------------------------------------------------
	def onMoneyChanged( self ):
		"""
		帮会金钱改变了
		"""
		if self.spendMoney <= 0 or self.money < self.spendMoney:
			return

		self.giveBuildingSpendMoney()

	#---------------------------------------------------------------------------------------------------------
	def giveBuildingSpendMoney( self ):
		"""
		define method.
		补交建筑维护费
		"""
		DEBUG_MSG( "Tong[%i,%s] spendMoney=%i, tongMoney=%i" % ( self.databaseID, self.playerName, self.spendMoney, self.money ) )
		if self.spendMoney <= 0 or self.money < self.spendMoney:
			return

		spendMoney = self.spendMoney
		self.spendMoney = 0
		self.payMoney( spendMoney, False, csdefine.TONG_CHANGE_MONEY_PAYSPENDMONEY )

		# 将领地相关NPC解锁， 允许交互
		if self.isLockedTerritoryNPC:
			self.isLockedTerritoryNPC = False
			if self.territoryMB:
				self.territoryMB.unLockTerritoryNPC()

	#---------------------------------------------------------------------------------------------------------
	def onTimer( self, timerID, cbID ):
		"""
		Timer
		"""
		if self._shenshouReviveTimeID == timerID:
			self._shenshouReviveTimeID = 0
			self.shenshouReviveTime = 0
			if self.territoryMB:
				self.territoryMB.reviveNagual( 1 )

	#---------------------------------------------------------------------------------------------------------
	def onRequestBuildingSpendMoney( self, playerBase ):
		"""
		define method.
		将建筑的维护费发到客户端
		"""
		if self.buildingSpendMoney == 0:
			self.calcBuildingSpendMoney()
		playerBase.client.onGetBuildingSpendMoney( self.buildingSpendMoney )

	def calcBuildingSpendMoney( self ):
		"""
		计算建筑的维护费
		"""
		self.buildingSpendMoney = 0	# 建筑的维护费

		for buildingType, buildingLevel in self.newBuildLevelMapping().iteritems():
			if buildingLevel <= 0:
				continue
				
			try:
				self.buildingSpendMoney += tongBuildingDatas[ buildingType ][ buildingLevel ][ "spendMoney" ]
			except:
				EXCEHOOK_MSG(self.databaseID, buildingType, buildingLevel)

	#---------------------------------------------------------------------------------------------------------
	def newBuildLevelMapping( self ):
		"""
		产生一个实时影射
		"""
		return {
				csdefine.TONG_BUILDING_TYPE_YSDT 	: self.level,		# 议事大厅
				csdefine.TONG_BUILDING_TYPE_JK 		: self.jk_level,	# 金库
				csdefine.TONG_BUILDING_TYPE_SSD 	: self.ssd_level,	# 神兽殿
				csdefine.TONG_BUILDING_TYPE_CK 		: self.ck_level,	# 仓库
				csdefine.TONG_BUILDING_TYPE_TJP 	: self.tjp_level,	# 铁匠铺
				csdefine.TONG_BUILDING_TYPE_SD 		: self.sd_level,	# 商店
				csdefine.TONG_BUILDING_TYPE_YJY 	: self.yjy_level,	# 研究院
			}

	#---------------------------------------------------------------------------------------------------------
	def updateBuildingLevelToClient( self, memberBaseMailbox ):
		"""
		更新帮会建筑的级别信息到某成员客户端
		"""
		for item in self.newBuildLevelMapping().iteritems():
			memberBaseMailbox.client.tong_onReceiveTongBuildInfo( { "type" : item[0], "level" : item[1] } )
	
	def upgradeBuildingLevel( self ):
		"""
		更新帮会建筑等级
		"""
		for buildingType, level in self.newBuildLevelMapping().items():
			newLevel = tongBuildingLevel.getBuildingLevel( self.level, buildingType )
			if newLevel > level:
				self.onBuildingUpgrade( buildingType, level, newLevel )
		# 通知帮会领地
		if self.territoryMB:
			self.territoryMB.onBuildingLevelChanged(  self.level )

	def onBuildingUpgrade( self, buildingType, oldLevel, newLevel ):
		"""
		建筑物升级
		"""
		DEBUG_MSG( "TONG: buildingType,", buildingType, self.newBuildLevelMapping()[buildingType])
		oLevel = oldLevel
		nLevel = newLevel

		if buildingType == csdefine.TONG_BUILDING_TYPE_JK:		# 金库
			self.jk_level = nLevel
		elif buildingType == csdefine.TONG_BUILDING_TYPE_SSD:	# 神兽殿
			self.onShenshouBuildingUpgrade( nLevel - oLevel )
		elif buildingType == csdefine.TONG_BUILDING_TYPE_CK:	# 仓库
			self.ck_level = nLevel
			self.onStorageUpgrade()								# 15:08 2008-12-13,wsf
		elif buildingType == csdefine.TONG_BUILDING_TYPE_TJP:	# 铁匠铺
			self.tjp_level = nLevel
		elif buildingType == csdefine.TONG_BUILDING_TYPE_SD:	# 商店,升级后更新所有商品
			self.sd_level = nLevel
			INFO_MSG( "TONG: %i reset tong items due to tong updating!" % ( self.databaseID ) )
			self.resetTongItems()
		elif buildingType == csdefine.TONG_BUILDING_TYPE_YJY:	# 研究院
			self.yjy_level = nLevel
			INFO_MSG( "TONG: %i update member tong skills due to tong updating! " % ( self.databaseID ) )
			self.updateRoleTongSkills( )
		try:
			g_logger.tongBuildingChangeLog( self.databaseID, self.getName(), buildingType, oLevel, nLevel )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
			
		# 计算出新的建筑维护费
		self.calcBuildingSpendMoney()

		# 将信息更新到客户端
		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			self.updateBuildingLevelToClient( emb )

		# 将数据更新到管理器
		self.getTongManager().updateTongBuildingLevel( self.databaseID, self.jk_level, self.ssd_level, self.ck_level, self.tjp_level, self.sd_level, self.yjy_level )

	def updateRoleTongSkills( self ):
		"""
		更新玩家帮会技能
		"""
		for memberDBID in self._onlineMemberDBID:
			member = self.getMemberInfos( memberDBID ).getBaseMailbox()
			member.cell.tong_updateTongSkills( self.yjy_level )

	#---------------------------------------------------------------------------------------------------------
	def onSelectShouShou( self, playerBase, userGrade, shenshouType ):
		"""
		define method.
		玩家选择帮会神兽
		"""
		#判断掠夺战是否进行中
		if BigWorld.globalData.has_key( "TONG_ROB_WAR_START" ) and self.tid in BigWorld.globalData[ "TONG_ROB_WAR_START" ]:
			self.statusMessage( playerBase, csstatus.TONG_SELECT_SHENSHOU_REVIVE_INVALID1 )
			return
			
		if self.shenshouType == shenshouType:
			self.statusMessage( playerBase, csstatus.TONG_SELECT_SHENSHOU_TYPE_EXIST )
			return
		elif not self.checkMemberDutyRights( userGrade, csdefine.TONG_RIGHT_PET_SELECT ):
			self.statusMessage( playerBase, csstatus.TONG_SELECT_SHENSHOU_GRADE_INVALID )
			return
		elif self.shenshouReviveTime > 0:
			self.statusMessage( playerBase, csstatus.TONG_SELECT_SHENSHOU_REVIVE_INVALID )
			return

		self.selectShenShou( shenshouType )

	def selectShenShou( self, shenshouType ):
		"""
		选择了一只神兽
		"""
		self.territoryMB.onTongSelectNewShenShou( shenshouType, self.shenshouReviveTime > 0 )
		self.shenshouType = shenshouType

		for dbid in self._onlineMemberDBID:
			emb = self.getMemberInfos( dbid ).getBaseMailbox()
			emb.client.tong_onSetShenShouType( self.ssd_level, self.shenshouType )

	def onOpenShenShouSelectWindow( self, memberDBID ):
		"""
		define method.
		服务器通知打开神兽选择界面
		csdefine.TONG_SHENSHOU_TYPE_*
		"""
		player = self.getMemberInfos( memberDBID ).getBaseMailbox()
		player.client.tong_openShenShouSelectWindow( self.ssd_level, self.shenshouType )

	def addNagualReviveTimer( self ):
		"""
		define method.
		神兽被杀了， 开启复活程序
		"""
		addtime = 1
		if self.shenshouReviveTime <= 0:
			self.shenshouReviveTime = time.time() + NAGUAL_REVIVE_TIME
			addtime = NAGUAL_REVIVE_TIME
			if self._shenshouReviveTimeID > 0:
				self.delTimer( self._shenshouReviveTimeID )
		else:
			t = time.time()
			if t < self.shenshouReviveTime:
				addtime = self.shenshouReviveTime - time.time()

		self._shenshouReviveTimeID = self.addTimer( addtime, 0, 0 )

	def onShenshouBuildingUpgrade( self, level ):
		"""
		神兽殿升级了
		"""
		self.ssd_level += level
		# 策划要求神兽殿建成之后默认随机给一个神兽
		if self.ssd_level == 1:
			sstypes = [ csdefine.TONG_SHENSHOU_TYPE_1, csdefine.TONG_SHENSHOU_TYPE_2, \
						csdefine.TONG_SHENSHOU_TYPE_3, csdefine.TONG_SHENSHOU_TYPE_4, ]
			self.selectShenShou( random.choice( sstypes ) )
		else:
			for dbid in self._onlineMemberDBID:
				emb = self.getMemberInfos( dbid ).getBaseMailbox()
				emb.client.tong_onSetShenShouType( self.ssd_level, self.shenshouType )

	#--------------------------------------------商人与领地与帮会之间交流的接口----------------------------------
	def onInitTongItems( self, reset ):
		"""
		初始化帮会物品
		"""
		if self.territoryMB:
			self.territoryMB.onInitTongItems( self.sd_level, reset )

	def onChapmanRequestItems( self, chapmanBase ):
		"""
		define method.
		帮会商人被创建后向帮会获取帮会物品数据
		"""
		for itemData in self.items:
			chapmanBase.cell.onRegisterTongItem( itemData[ "itemID" ], itemData[ "amount" ] )
		# 发送玩家的购买记录
		for record in self.weekMemberBuyItemRecord:
			chapmanBase.cell.onGetMemberBuyRecord( record )

	def onRequestOpenTongShop( self, chapmanBase, playerID, talkID ):
		"""
		define method
		请求与商店NPC对话
		"""
		if self.spendMoney > 0:			# 欠费
			chapmanBase.cell.onRequestOpenTongShop( playerID, talkID, False )
		else:
			chapmanBase.cell.onRequestOpenTongShop( playerID, talkID, True )
		
	def onSellItems( self, roleDBID, itemID, amount ):
		"""
		define method.
		帮会物品被出售了 [ { "dbID": dbid, "record": [ { "itemID" : itemID, "amount": amount ,},  ] }, ]
		"""
		INFO_MSG( "TONG: %s has sold item %s， amount %i to %i" % ( self.getNameAndID(), itemID, amount, roleDBID ) )
		for itemData in self.items:
			if itemData[ "itemID" ] == itemID:
				if itemData[ "amount" ] > amount:
					itemData[ "amount" ] -= amount
				else:
					self.items.remove( itemData )
				break
		
		# 帮会成员购买数据修改
		for item in self.weekMemberBuyItemRecord:
			if item["dbID" ] == roleDBID:
				for record in item[ "record" ]:
					if itemID == record[ "itemID"]:
						record[ "amount" ] += amount
						return
				
				item[ "record" ].append( { "itemID": itemID, "amount": amount} )
				return
		
		buyRecord = {}
		buyRecord[ "dbID" ] = roleDBID
		buyRecord[ "record" ] = []
		buyRecord[ "record" ].append( { "itemID": itemID, "amount": amount} )
		self.weekMemberBuyItemRecord.append( buyRecord )

	#-------------------------------------------------帮会祭祀活动-------------------------------------------------
	def onRequestFeteSuccessfully( self ):
		"""
		申请帮会祭祀成功
		"""
		self.territoryMB.onStartTongFete()

	def onFeteComplete( self ):
		"""
		define method.
		帮会祭祀活动成功完成了
		"""
		self.territoryMB.onTongFeteComplete()

	def onOverFete( self ):
		"""
		define method.
		帮会祭祀活动结束了  时间到了
		"""
		self.territoryMB.onOverTongFete()
	
	# ---------------------------------------------------帮会特殊商城-----------------------------------------------
	def onInitTongSpecialItems( self, reset ):
		"""
		初始化帮会物品
		"""
		if self.territoryMB:
			self.territoryMB.onInitTongSpecialItems( self.level, reset )

	def onChapmanRequestSpecialItems( self, chapmanBase ):
		"""
		define method.
		帮会商人被创建后向帮会获取帮会物品数据
		"""
		for itemData in self.specItems:
			chapmanBase.cell.onRegisterTongSpecialItem( itemData[ "itemID" ], itemData[ "amount" ] )
			
	def onRequestOpenTongSpecialShop( self, chapmanBase, playerID, talkID ):
		"""
		define method
		请求与特殊商店NPC对话
		"""
		if self.spendMoney > 0:			# 欠费
			chapmanBase.cell.onRequestOpenTongSpecialShop( playerID, talkID, False )
		else:
			chapmanBase.cell.onRequestOpenTongSpecialShop( playerID, talkID, True )
	
	def onSellSpecialItems( self, playerBase, memberDBID, itemID, amount ):
		"""
		define method.
		帮会特殊商品被出售
		"""
		#权限检测
		player = BigWorld.entities.get( playerBase.id, None )
		if player is None:return
		playerGrade = self.getMemberInfos( player.databaseID ).getGrade()
		if not self.checkMemberDutyRights( playerGrade, csdefine.TONG_RIGHT_ASSIGN_ITEM ):
			self.statusMessage( playerBase, csstatus.TONG_ASSIGN_ITEM_FAILURE )
			return
		specItem = self.tong_getSpecialItem( itemID )
		if specItem is None:return
		reqMoney = specItem["reqMoney"]*amount
		if reqMoney > 0 :
			if not self.payMoney( reqMoney, True, csdefine.TONG_CHANGE_MONEY_BUY_SPECIAL_ITEM ):
				ERROR_MSG( "buy TongSpecial pay Money Failed." )
				return
		for itemData in self.specItems:
			if itemData[ "itemID" ] == itemID:
				if itemData[ "amount" ] > amount:
					itemData[ "amount" ] -= amount
				else:
					self.specItems.remove( itemData )
				break
		itemDatas = []
		item = g_items.createDynamicItem( itemID, amount )
		tempDict = item.addToDict()
		del tempDict["tmpExtra"]	# 去掉物品不存盘的数据
		itemData = cPickle.dumps( tempDict, 0 )
		itemDatas.append( itemData )
		memberName = self.getMemberInfos( memberDBID ).getName()
		mailMgr = self.getMailMgr()
		mailMgr.send( None, memberName, csdefine.MAIL_TYPE_QUICK, csdefine.MAIL_SENDER_TYPE_PLAYER, self.chiefName, cschannel_msgs.TONG_SPECIALITEM_REWARD_TITLE,"", 0, itemDatas )
		self.statusMessageToOnlineMember( csstatus.TONG_CHIEF_ASSIGN_ITEM_TO_MEMBER, self.chiefName, item.name(), memberName, memberName )
		INFO_MSG( "TONG: %s has sold specialitem %i， amount %i to %i" % ( self.getNameAndID(), itemID, amount, memberDBID ) )
		if self.territoryMB:
			self.territoryMB.onSellSpecialItems( playerBase.id, itemID, amount )
		# 帮主为帮众分配商品数据
		for item in self.chiefBuySpecItemForMemberRecord:
			if item["dbID" ] == memberDBID:
				for record in item[ "record" ]:
					if itemID == record[ "itemID"]:
						record[ "amount" ] += amount
						return
				
				item[ "record" ].append( { "itemID": itemID, "amount": amount} )
				return
		
		buyRecord = {}
		buyRecord[ "dbID" ] = memberDBID
		buyRecord[ "record" ] = []
		buyRecord[ "record" ].append( { "itemID": itemID, "amount": amount} )
		self.chiefBuySpecItemForMemberRecord.append( buyRecord )
		
	def buyTongSpecialArrayFromNPC( self, chapmanBase, playerDBID, memberDBID, invoiceIDs, amountList ):
		"""
		define method.
		购买帮会特殊商品
		"""
		moneys = 0
		invoiceList = zip( invoiceIDs, amountList )
		items = []		# 记录每一个物品
		moneyList = []	# 记录每一个物品的卖出价格
		for invoiceID, amount in invoiceList:
			specItem = self.tong_getSpecialItem( invoiceID )
			if specItem is None:
				ERROR_MSG(  " item %i not in tongsepctiems" %invoiceID )
				return
			if specItem["amount"] < amount:			#数量不够
				ERROR_MSG( "not more item(id = %i), current amount = %i, sell amount = %i." % ( invoiceID, specItem["amount"], amount ) )
				return
			moneys += specItem["reqMoney"]*amount
		if self.money <  moneys:				#帮会资金不够
			ERROR_MSG( "tong not enogh money" )
			return
		playerMailBox = self.getMemberInfos( playerDBID ).getBaseMailbox()
		playerMailBox.cell.buyTongSpecialArrayFromNPC( chapmanBase, memberDBID, invoiceIDs, amountList )
	
	def tong_getSpecialItem( self, itemID ):
		for itemData in self.specItems:
			if itemData["itemID"] == itemID:
				return itemData
	
	def onAddSpecialItemReward( self, itemID, amount ):
		"""
		向帮会领地注册特殊商品
		"""
		if self.territoryMB:
			self.territoryMB.onAddSpecialItemReward( itemID, amount )
#
# $Log: not supported by cvs2svn $
#