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
	�߻������ǣ������ǮС��1������1
	�������1����ȡ��
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
		�������Ƿ��ܹ�����
		"""
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		�������Ƿ��ܹ�����Ʒ
		"""
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, itemInstance, player, chapmanEntity ):
		"""
		���н���
		"""
		pass

	def addToDict( self ):
		"""
		"""
		return { "param": self.getPriceData() }

	def getPriceData( self ):
		"""
		��ü۸�����
		"""
		return {}

	def copy( self ):
		"""
		��������
		"""
		return createPriceInstance( self.getPriceData() )

	def getPrice( self, player, chapmanEntity, invoiceAmount  ):
		"""
		"""
		return 0

	def getRevenueMoney( self, price ):
		"""
		���˰��
		"""
		return 0

class PriceMoney( Price ):
	"""
	��Ǯ����
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
		��������Ƿ��ܹ�����Ʒ
		"""
		price = self.getPrice( player, chapmanEntity, invoiceAmount )
		revenueMoney = self.getRevenueMoney( player, chapmanEntity, price )
		if player.money < price + revenueMoney:
			return csstatus.NPC_TRADE_NOT_ENOUGH_MONEY
		self.tempPrice = price	# ����Ƿ������ʱ��ʱ��¼�۸���Ҹ�Ǯʱ�������¼��㣬�豣֤�����Ϊ�ͽ�����ͬһ��tick����ɡ�
		self.revenueMoney = revenueMoney
		return csstatus.NPC_TRADE_CAN_BUY

	def checkPlayerArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		�������Ƿ��ܹ�����Ʒ
		"""
		totalMoney = player.queryTemp( "npc_trade_money", 0 )
		price = self.getPrice( player, chapmanEntity, invoiceAmount )
		revenueMoney = self.getRevenueMoney( player, chapmanEntity, price )
		totalMoney += price + revenueMoney
		if player.money < totalMoney:
			return csstatus.NPC_TRADE_NOT_ENOUGH_MONEY
		self.tempPrice = price	# ����Ƿ������ʱ��ʱ��¼�۸���Ҹ�Ǯʱ�������¼��㣬�豣֤�����Ϊ�ͽ�����ͬһ��tick����ɡ�
		self.revenueMoney = revenueMoney
		player.setTemp( "npc_trade_money", totalMoney )
		return csstatus.NPC_TRADE_CAN_BUY

	def playerPay( self, itemInstance, player, chapmanEntity ):
		"""
		���н���
		"""
		if not hasattr( self, "tempPrice" ):
			ERROR_MSG( "��Ʒ�۸񲻴��ڡ�player( %s )��npc( %s )������Ʒ( %s )���ɹ���" % ( player.getName(), chapmanEntity.className, itemInstance.name() ) )
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
		���Ҫ�����Ʒ�۸�
		"""
		# ȷ����int���͵�
		return priceCarry( player.calcCastellanPriceRebate( self.money * chapmanEntity.invSellPercent ) ) * invoiceAmount

	def getRevenueMoney( self, player, chapmanEntity, price ):
		"""
		���˰��
		"""
		if chapmanEntity.isJoinRevenue:
			spaceType = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			if player.tong_holdCity != spaceType:		# �������˰��
				if BigWorld.globalData.has_key( spaceType + ".revenueRate" ):
					revenueRate = BigWorld.globalData[ spaceType + ".revenueRate" ]
					return int( price * ( revenueRate / 100.0 ) )
		return 0

	def getPriceData( self ):
		"""
		��ü۸�����
		"""
		return { "priceType":csdefine.INVOICE_NEED_MONEY, "price":self.money }


class PriceItem( Price ):
	"""
	���ﻻ��
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
		���н���
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
		�������Ƿ��ܹ�����Ʒ
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
	������ֻ�ȡ��Ʒ
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
		��ü۸�����
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
		��Ҹ�����
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
	�ﹱ��ȡ��Ʒ
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
		��ü۸�����
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
		# �����Ұ����ռ�������ô�������İ﹩����Ʒ���ۿۣ�
		# �����ƺܲ��������ռ��ĳһ�����к���һ��﹩������Ʒ��û��ϵ�ģ��������ַ�ʽ��ռ����е�����ܹ��õ�һЩ�ô��ǲ������
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
		��Ҹ��ﹱ
		"""
		if not player.addItemAndRadio( item, ItemTypeEnum.ITEM_GET_NPCTRADE, reason = csdefine.ADD_ITEM_BUYFROMNPC ):
			player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return False

		# �����Ұ����ռ�������ô�������İ﹩����Ʒ���ۿۣ�
		# �����ƺܲ��������ռ��ĳһ�����к���һ��﹩������Ʒ��û��ϵ�ģ��������ַ�ʽ��ռ����е�����ܹ��õ�һЩ�ô��ǲ������
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
	��Ӿ������ֻ�ȡ��Ʒ
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
		��ü۸�����
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
		��Ҹ�����
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
	��Ὰ�����ֻ�ȡ��Ʒ
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
		��ü۸�����
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
		��Ҹ�����
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
	���˾������ֻ�ȡ��Ʒ
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
		��ü۸�����
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
		��Ҹ�����
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
	����ֵ����Ʒ
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
		��ü۸�����
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
		��Ҹ�����ֵ
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
	���һ���Ʒ������������ʵҲ�ǲ�������ֵ�������ǽ���ʱ
	���ᾭ����ҵı����������е���Ʒϵͳ������Ӣ�����˸���
	��װ������
	"""
	def getPriceData( self ):
		"""
		��ü۸�����
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
		��Ҹ�����
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
	��Ӫ����
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
		��ü۸�����
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
		֧��
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

