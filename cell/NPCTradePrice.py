# -*- coding: gb18030 -*-

import csconst
import csdefine
import csstatus
import BigWorld
import ItemTypeEnum
from MsgLogger import g_logger
from bwdebug import *
import items
import Const

g_items = items.instance()


def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	策划规则是：如果价钱小于1，就算1
	如果大于1，则取整
	"""
	if price < 1:
		return 1
	return int( price )

class Price:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass

	def load( self, data ):
		"""
		"""
		pass

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		检查玩家是否能够购买
		"""
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		检查玩家是否能够买商品
		"""
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, itemInstance, player, chapmanEntity ):
		"""
		进行交易
		"""
		pass

	def addToDict( self ):
		"""
		"""
		return { "param": self.getPriceData() }

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return {}

	def copy( self ):
		"""
		复制自身
		"""
		return createPriceInstance( self.getPriceData() )

	def getPrice( self, player, chapmanEntity, invoiceAmount  ):
		"""
		"""
		return 0

	def getRevenueMoney( self, price ):
		"""
		获得税金
		"""
		return 0

class PriceMoney( Price ):
	"""
	金钱需求
	"""
	def __init__( self ):
		Price.__init__( self )
		self.money = 0

	def load( self, data ):
		"""
		"""
		self.money = data["price"]

	def checkRequire( self, player, chapmanEntity, invoiceAmount ):
		"""
		检验玩家是否能够买商品
		"""
		price = self.getPrice( player, chapmanEntity, invoiceAmount )
		revenueMoney = self.getRevenueMoney( player, chapmanEntity, price )
		if player.money < price + revenueMoney:
			return csstatus.NPC_TRADE_NOT_ENOUGH_MONEY
		self.tempPrice = price	# 检查是否可以买时临时记录价格，玩家付钱时不需重新计算，需保证检查行为和交易在同一个tick里完成。
		self.revenueMoney = revenueMoney
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		检查玩家是否能够买商品
		"""
		totalMoney = player.queryTemp( "npc_trade_money", 0 )
		price = self.getPrice( player, chapmanEntity, invoiceAmount )
		revenueMoney = self.getRevenueMoney( player, chapmanEntity, price )
		totalMoney += price + revenueMoney
		if player.money < totalMoney:
			return csstatus.NPC_TRADE_NOT_ENOUGH_MONEY
		self.tempPrice = price	# 检查是否可以买时临时记录价格，玩家付钱时不需重新计算，需保证检查行为和交易在同一个tick里完成。
		self.revenueMoney = revenueMoney
		player.setTemp( "npc_trade_money", totalMoney )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, itemInstance, player, chapmanEntity ):
		"""
		进行交易
		"""
		if not hasattr( self, "tempPrice" ):
			ERROR_MSG( "商品价格不存在。player( %s )从npc( %s )购买商品( %s )不成功。" % ( player.getName(), chapmanEntity.className, itemInstance.name() ) )
			return False

		if not player.addItemAndRadio( itemInstance, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ADD_ITEM_BUYFROMNPC  ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False
		totalMoney = self.tempPrice + self.revenueMoney
		player.payMoney( totalMoney, csdefine.CHANGE_MONEY_BUR_FROM_NPC )

		if self.revenueMoney > 0:
			BigWorld.globalData[ "TongManager" ].onTakeCityRevenue( player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), self.revenueMoney )
			
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), totalMoney, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def getPrice( self, player, chapmanEntity, invoiceAmount ):
		"""
		获得要买的商品价格
		"""
		# 确保是int类型的
		return priceCarry( player.calcCastellanPriceRebate( self.money * chapmanEntity.invSellPercent ) ) * invoiceAmount

	def getRevenueMoney( self, player, chapmanEntity, price ):
		"""
		获得税金
		"""
		if chapmanEntity.isJoinRevenue:
			spaceType = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			if player.tong_holdCity != spaceType:		# 计算城市税收
				if BigWorld.globalData.has_key( spaceType + ".revenueRate" ):
					revenueRate = BigWorld.globalData[ spaceType + ".revenueRate" ]
					return int( price * ( revenueRate / 100.0 ) )
		return 0

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEED_MONEY, "price":self.money }


class PriceItem( Price ):
	"""
	以物换物
	"""
	def __init__( self ):
		Price.__init__( self )
		self.itemID = 0
		self.itemCount = 0

	def load( self, data ):
		"""
		"""
		self.itemID = data["itemID"]
		self.itemCount = data["itemCount"]

	def getPrice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		return ( self.itemID, self.itemCount )

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.checkItemFromNKCK_( self.itemID, self.itemCount * invoiceAmount ):
			return csstatus.NPC_TRADE_CAN_BUY
		return csstatus.NPC_TRADE_LACK_ITEM

	def playerPay( self, item, player, chapmanEntity ):
		"""
		进行交易
		"""
		itemAmount = item.getAmount()
		if not player.removeItemTotal( self.itemID, itemAmount*self.itemCount, csdefine.DELETE_ITEM_BUYFROMITEMCHAPMAN ):
			ERROR_MSG( "player( %s ) dont has enough item( itemID:%i, itemAmount:%i )." % ( player.getName(), self.itemID, itemAmount ) )
			return False
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ADD_ITEM_BUYFROMNPC  ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		检查玩家是否能够买商品
		"""
		itemDict = player.queryTemp( "npc_trade_need_items", {} )
		try:
			invoiceInfo = itemDict[self.itemID]
		except KeyError:
			invoiceInfo = [ self.itemID, self.itemCount ]
			itemDict[self.itemID] = invoiceInfo
		else:
			invoiceInfo[1] += self.itemCount * invoiceAmount
		if not player.checkItemFromNKCK_( invoiceInfo[0], invoiceInfo[1] ):
			return csstatus.NPC_TRADE_LACK_ITEM
		player.setTemp( "npc_trade_need_items", itemDict )
		return csstatus.NPC_TRADE_CAN_BUY

	def getPriceData( self ):
		"""
		"""
		return 	{ "priceType":csdefine.INVOICE_NEED_ITEM, \
				"itemID":self.itemID, \
				"itemCount":self.itemCount, \
				}


class PriceDancePoint( Price ):
	"""
	跳舞积分换取物品
	"""
	def __init__( self ):
		Price.__init__( self )
		self.point = 0

	def load( self, priceData ):
		"""
		"""
		self.point = priceData["point"]

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEED_DANCE_POINT, "point":self.point }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.dancePoint < self.point * invoiceAmount:
			return csstatus.JING_WU_SHI_KE_NOT_ENOUGH_POINT
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		totalPoint = player.queryTemp( "npc_trade_need_dancePoint", 0 ) + self.point * invoiceAmount
		if player.dancePoint < totalPoint:
			return csstatus.JING_WU_SHI_KE_NOT_ENOUGH_POINT
		player.setTemp( "npc_trade_need_dancePoint", totalPoint )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, item, player, chapmanEntity ):
		"""
		玩家给积分
		"""
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ADD_ITEM_BUYFROMNPC  ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False
		player.dancePoint -= self.point * item.getAmount()
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True


class PriceTongContribute( Price ):
	"""
	帮贡换取物品
	"""
	def __init__( self ):
		Price.__init__( self )
		self.tongContribute = 0

	def load( self, priceData ):
		"""
		"""
		self.tongContribute = priceData["tongContribute"]

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEED_TONG_CONTRIBUTE, "tongContribute":self.tongContribute }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.tong_contribute < self.tongContribute * invoiceAmount:
			return csstatus.NPC_TRADE_NOT_ENOUGH_CONTRIBUTE
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		# 如果玩家帮会有占领城市那么购买消耗帮供的商品有折扣，
		# 这个设计很不合理，帮会占领某一个城市和玩家花帮供购买物品是没关系的，想用这种方式让占领城市的玩家能够得到一些好处是不合理的
		tongContribute = self.tongContribute
		if player.tong_holdCity:
			tongContribute *= Const.TONG_HOLD_CITY_CONTRIBUT_DISCOUNT

		totalPoint = player.queryTemp( "npc_trade_need_tongContribute", 0 ) + tongContribute * invoiceAmount
		if player.tong_contribute < totalPoint:
			return csstatus.NPC_TRADE_NOT_ENOUGH_CONTRIBUTE
		player.setTemp( "npc_trade_need_tongContribute", totalPoint )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, item, player, chapmanEntity ):
		"""
		玩家给帮贡
		"""
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ADD_ITEM_BUYFROMNPC ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False

		# 如果玩家帮会有占领城市那么购买消耗帮供的商品有折扣，
		# 这个设计很不合理，帮会占领某一个城市和玩家花帮供购买物品是没关系的，想用这种方式让占领城市的玩家能够得到一些好处是不合理的
		tongContribute = self.tongContribute
		if player.tong_holdCity:
			tongContribute *= Const.TONG_HOLD_CITY_CONTRIBUT_DISCOUNT
		player.tong_payContribute( tongContribute * item.getAmount() )
		LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
			%( player.databaseID, player.getName(), chapmanEntity.className, chapmanEntity.getName(), item.id, item.name(), item.amount ) )
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

class PriceTeamCompetitionPoint( Price ):
	"""
	组队竞技积分换取物品
	"""
	def __init__( self ):
		Price.__init__( self )
		self.point = 0

	def load( self, priceData ):
		"""
		"""
		self.point = priceData["teamCompetitionPoint"]

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEDD_TEAM_COMPETITION_POINT, "teamCompetitionPoint":self.point }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.teamCompetitionPoint < self.point * invoiceAmount:
			return csstatus.JING_WU_SHI_KE_NOT_ENOUGH_POINT
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		totalPoint = player.queryTemp( "npc_trade_need_teamCompetitionPoint", 0 ) + self.point * invoiceAmount
		if player.teamCompetitionPoint < totalPoint:
			return csstatus.JING_WU_SHI_KE_NOT_ENOUGH_POINT
		player.setTemp( "npc_trade_need_teamCompetitionPoint", totalPoint )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, item, player, chapmanEntity ):
		"""
		玩家给积分
		"""
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ADD_ITEM_BUYFROMNPC  ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False
			
		player.subTeamCompetitionScore( self.point * item.getAmount(), 0 )
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

class PriceTongScore( Price ):
	"""
	帮会竞技积分换取物品
	"""
	def __init__( self ):
		Price.__init__( self )
		self.tongCompetitionScore = 0

	def load( self, priceData ):
		"""
		"""
		self.tongCompetitionScore = priceData["tongCompetitionScore"]

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEED_TONG_SCORE, "tongCompetitionScore":self.tongCompetitionScore }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.tongCompetitionScore < self.tongCompetitionScore * invoiceAmount:
			return csstatus.NPC_TRADE_NOT_ENOUGH_TONGSCORE
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		totalPoint = player.queryTemp( "npc_trade_need_TongScore", 0 ) + self.tongCompetitionScore * invoiceAmount
		if player.tongCompetitionScore < totalPoint:
			return csstatus.NPC_TRADE_NOT_ENOUGH_TONGSCORE
		player.setTemp( "npc_trade_need_TongScore", totalPoint )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, item, player, chapmanEntity ):
		"""
		玩家给积分
		"""
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ACTIVITY_BANG_HUI_JING_JI  ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False
		player.subTongScore( self.tongCompetitionScore * item.getAmount() )
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True


class PersonalScore( Price ):
	"""
	个人竞技积分换取物品
	"""
	def __init__( self ):
		Price.__init__( self )
		self.personalScore = 0

	def load( self, priceData ):
		"""
		"""
		self.personalScore = priceData["personalScore"]

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEED_ROLE_PERSONAL_SCORE, "personalScore":self.personalScore }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.personalScore < self.personalScore * invoiceAmount:
			return csstatus.ROLE_COMPETITION_NOT_ENOUGH_POINT
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		totalPoint = player.queryTemp( "npc_trade_need_personalScore", 0 ) + self.personalScore * invoiceAmount
		if player.personalScore < totalPoint:
			return csstatus.ROLE_COMPETITION_NOT_ENOUGH_POINT
		player.setTemp( "npc_trade_need_personalScore", totalPoint )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, item, player, chapmanEntity ):
		"""
		玩家给积分
		"""
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ACTIVITY_GE_REN_JING_JI  ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False
		player.subPersonalScore( self.personalScore * item.getAmount(), 0 )
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True


class PriceAccumPoint( Price ):
	"""
	气运值换物品
	"""
	def __init__( self ):
		Price.__init__( self )
		self.accumPoint = 0

	def load( self, priceData ):
		"""
		"""
		self.accumPoint = priceData["accumPoint"]

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEED_ROLE_ACCUM_POINT, "accumPoint":self.accumPoint }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.accumPoint < self.accumPoint * invoiceAmount:
			return csstatus.NOT_ENOUGH_ACCUM_POINT
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		totalPoint = player.queryTemp( "npc_trade_need_accumPoint", 0 ) + self.accumPoint * invoiceAmount
		if player.accumPoint < totalPoint:
			return csstatus.NOT_ENOUGH_ACCUM_POINT
		player.setTemp( "npc_trade_need_accumPoint", totalPoint )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, item, player, chapmanEntity ):
		"""
		玩家给气运值
		"""
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ADD_ITEM_BUYFROMNPC  ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False
		player.accumPoint -= self.accumPoint * item.getAmount()
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

class PriceSoulCoin( PriceAccumPoint ) :
	"""
	灵魂币换物品（交易灵魂币其实也是操作气运值），但是交易时
	不会经过玩家的背包，即现有的物品系统，用于英雄联盟副本
	的装备交易
	"""
	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEED_SOUL_COIN, "accumPoint":self.accumPoint }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.accumPoint < self.accumPoint * invoiceAmount:
			return csstatus.NOT_ENOUGH_SOUL_COIN
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		totalPoint = player.queryTemp( "npc_trade_need_accumPoint", 0 ) + self.accumPoint * invoiceAmount
		if player.accumPoint < totalPoint:
			return csstatus.NOT_ENOUGH_SOUL_COIN
		player.setTemp( "npc_trade_need_accumPoint", totalPoint )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, item, player, chapmanEntity ):
		"""
		玩家给灵魂币
		"""
		if not player.gainYXLMEquipFromNPC( chapmanEntity, item ):
			return False
		player.addAccumPoint( -self.accumPoint * item.getAmount() )
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True

class PriceCampHonour( Price ) :
	"""
	阵营荣誉
	"""
	def __init__( self ):
		Price.__init__( self )
		self.campHonour = 0

	def load( self, priceData ):
		"""
		"""
		self.campHonour = priceData["campHonour"]

	def getPriceData( self ):
		"""
		获得价格数据
		"""
		return { "priceType":csdefine.INVOICE_NEED_CAMP_HONOUR, "campHonour":self.campHonour }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.camp_getHonour() < self.campHonour * invoiceAmount:
			return csstatus.CAMP_NOT_CAMP_HONOUR
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		"""
		totalHonour = player.queryTemp( "npc_trade_need_campHonour", 0 ) + self.campHonour * invoiceAmount
		if player.camp_getHonour() < totalHonour:
			return csstatus.CAMP_NOT_CAMP_HONOUR
		player.setTemp( "npc_trade_need_campHonour", totalHonour )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, item, player, chapmanEntity ):
		"""
		支付
		"""
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ADD_ITEM_BUYFROMNPC  ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False
		player.camp_decHonour( self.campHonour * item.getAmount() )
		try:
			g_logger.tradeNpcBuyLog( player.databaseID, player.getName(), item.uid, item.name(), item.getAmount(), 0, player.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )
		return True


def createPriceInstance( data ):
	"""
	"""
	if data["priceType"] == csdefine.INVOICE_NEED_MONEY:
		instance = PriceMoney()
	elif data["priceType"] == csdefine.INVOICE_NEED_ITEM:
		instance = PriceItem()
	elif data["priceType"] == csdefine.INVOICE_NEED_DANCE_POINT:
		instance = PriceDancePoint()
	elif data["priceType"] == csdefine.INVOICE_NEED_TONG_CONTRIBUTE:
		instance = PriceTongContribute()
	elif data["priceType"] == csdefine.INVOICE_NEDD_TEAM_COMPETITION_POINT:
		instance = PriceTeamCompetitionPoint()
	elif data["priceType"] == csdefine.INVOICE_NEED_TONG_SCORE:
		instance = PriceTongScore()
	elif data["priceType"] == csdefine.INVOICE_NEED_ROLE_PERSONAL_SCORE:
		instance = PersonalScore()
	elif data["priceType"] == csdefine.INVOICE_NEED_ROLE_ACCUM_POINT:
		instance = PriceAccumPoint()
	elif data["priceType"] == csdefine.INVOICE_NEED_SOUL_COIN:
		instance = PriceSoulCoin()
	elif data["priceType"] == csdefine.INVOICE_NEED_CAMP_HONOUR:
		instance = PriceCampHonour()
	
	instance.load( data )
	return instance


class PriceDataType:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass

	def getDictFromObj( self, obj ):
		"""
		"""
		return obj.addToDict()

	def createObjFromDict( self, dictData ):
		"""
		"""
		return createPriceInstance( dictData["param"] )

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, Price )

priceDataInstance = PriceDataType()

