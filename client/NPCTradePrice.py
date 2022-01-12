# -*- coding: gb18030 -*-

import csconst
import csdefine
import csstatus
import BigWorld
import ItemTypeEnum
from Message_logger import *
from bwdebug import *
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
import config.client.labels.NPCTradePrice as lbDatas
import items
import GUI
import utils

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

def calcCastellanPriceRebate( money ):
	"""
	����NPC���ڳ��еĳ�������(��ĳ���ռ��ĸó��к�)�Ĺ������
	"""
	player = BigWorld.player()
#	if player.tong_dbID > 0 and player.tong_holdCity == player.getSpaceLabel():
#		return money * 0.9
	return money

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

	def addToDict( self ):
		"""
		"""
		return { "param":{} }

	def getPrice( self, chapmanEntity, invoiceAmount  ):
		"""
		"""
		return 0


class PriceMoney( Price ):
	"""
	��Ǯ����
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_MONEY
		self.money = 0

	def load( self, data ):
		"""
		"""
		self.money = data["price"]

	def checkRequire( self, player, chapmanEntity, invoiceAmount ):
		"""
		��������Ƿ��ܹ�����Ʒ
		"""
		if player.money < self.getDiscountMoney( self.getPrice( chapmanEntity, invoiceAmount ) ):
			return csstatus.NPC_TRADE_NOT_ENOUGH_MONEY
		return csstatus.NPC_TRADE_CAN_BUY

	def getPrice( self, chapmanEntity, invoiceAmount = 1 ):
		"""
		���Ҫ�����Ʒ�۸�
		"""
		# ȷ����int���͵�
		return priceCarry( calcCastellanPriceRebate( self.money ) ) * invoiceAmount

	def getDiscountMoney( self, money ):
		"""
		��ô��ۺ�ļ۸�
		"""
		player = BigWorld.player()
		if player.tong_dbID > 0 and player.tong_holdCity == player.getSpaceLabel():
			return money * 0.9
		return money

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		money = self.getPrice( chapman, 1 )
		msg = lbDatas.PRICE + utils.currencyToViewText( money )
		if chapman.isJoinRevenue == True and BigWorld.player().tong_holdCity != BigWorld.player().getSpaceLabel():
			try:
				revenueRate = int( BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_CITY_REVENUE ) ) / 100.0
			except:
				revenueRate = 0.0
			revenue = int( money * revenueRate )
			msg += lbDatas.TAX + utils.currencyToViewText( revenue )
		return msg

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		money = self.getPrice( chapman )
		return utils.currencyToViewText( money )

	def addToDict( self ):
		"""
		"""
		return { "param":{ "priceType":csdefine.INVOICE_NEED_MONEY, "price":self.money } }


class PriceItem( Price ):
	"""
	���ﻻ��
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_ITEM
		self.itemID = 0
		self.itemCount = 0

	def load( self, data ):
		"""
		"""
		self.itemID = data["itemID"]
		self.itemCount = data["itemCount"]

	def addToDict( self ):
		"""
		"""
		return { "param":
				{ "priceType":csdefine.INVOICE_NEED_ITEM, \
				"itemID":self.itemID, \
				"itemCount":self.itemCount\
				}
			}

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		item = g_items.createDynamicItem( self.itemID )
		return lbDatas.TRADECONDITION % ( item.name(), self.itemCount )

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		item = g_items.createDynamicItem( self.itemID, self.itemCount )
		iconPath = item.icon()
		srcIcon = GUI.load( "guis/general/tradewindow/icon.gui" )
		srcIcon.icon.textureName = iconPath
		srcIcon.save( "guis/general/tradewindow/%s.gui" % item.id )
		return str( item.getAmount() ) + PL_Image.getSource( "guis/general/tradewindow/%s.gui" % item.id )

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		"""
		if player.checkItemFromNKCK_( self.itemID, self.itemCount * invoiceAmount ):
			return csstatus.NPC_TRADE_CAN_BUY
		return csstatus.NPC_TRADE_LACK_ITEM

class PriceDancePoint( Price ):
	"""
	������ֻ�ȡ��Ʒ
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_DANCE_POINT
		self.point = 0

	def load( self, priceData ):
		"""
		"""
		self.point = priceData["point"]

	def addToDict( self ):
		"""
		�������ڴ�����ֵ�
		"""
		return { "param": { "priceType":csdefine.INVOICE_NEED_DANCE_POINT, "point":self.point } }

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		return lbDatas.NEEDPOINT % self.point

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		return lbDatas.NEEDPOINT % self.point

class PriceTongContribute( Price ):
	"""
	�ﹱ����Ʒ
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_TONG_CONTRIBUTE
		self.tongContribute = 0

	def load( self, priceData ):
		"""
		"""
		self.tongContribute = priceData["tongContribute"]

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		�������Ƿ��ܹ�����
		"""
		if player.tong_memberInfos[player.databaseID].getContribute() < self.tongContribute * invoiceAmount:
			return csstatus.NPC_TRADE_NOT_ENOUGH_CONTRIBUTE
		return csstatus.NPC_TRADE_CAN_BUY

	def addToDict( self ):
		"""
		�������ڴ�����ֵ�
		"""
		return { "param": { "priceType":csdefine.INVOICE_NEED_TONG_CONTRIBUTE, "tongContribute":self.tongContribute } }

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		return lbDatas.NEEDTONGPOINT % self.tongContribute

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		return lbDatas.NEEDTONGPOINT % self.tongContribute

class PriceTeamCompetitionPoint( Price ):
	"""
	��Ӿ������ֻ�ȡ��Ʒ
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEDD_TEAM_COMPETITION_POINT
		self.point = 0

	def load( self, priceData ):
		"""
		"""
		self.point = priceData["teamCompetitionPoint"]

	def addToDict( self ):
		"""
		�������ڴ�����ֵ�
		"""
		return { "param": { "priceType":csdefine.INVOICE_NEDD_TEAM_COMPETITION_POINT, "teamCompetitionPoint":self.point } }

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		return lbDatas.NEEDPOINT % self.point

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		return lbDatas.NEEDPOINT % self.point

class PriceTongScore( Price ):
	"""
	��Ὰ�����ֻ�ȡ��Ʒ
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_TONG_SCORE
		self.tongCompetitionScore = 0

	def load( self, priceData ):
		"""
		"""
		self.tongCompetitionScore = priceData["tongCompetitionScore"]

	def addToDict( self ):
		"""
		�������ڴ�����ֵ�
		"""
		return { "param": { "priceType":csdefine.INVOICE_NEED_TONG_SCORE, "tongCompetitionScore":self.tongCompetitionScore } }

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		return lbDatas.NEEDPOINT % self.tongCompetitionScore

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		return lbDatas.NEEDPOINT % self.tongCompetitionScore

class PersonalScore( Price ):
	"""
	���˾������ֻ�ȡ��Ʒ
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_ROLE_PERSONAL_SCORE
		self.personalScore = 0

	def load( self, priceData ):
		"""
		"""
		self.personalScore = priceData["personalScore"]

	def addToDict( self ):
		"""
		�������ڴ�����ֵ�
		"""
		return { "param": { "priceType":csdefine.INVOICE_NEED_ROLE_PERSONAL_SCORE, "personalScore":self.personalScore } }

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		return lbDatas.NEEDPOINT % self.personalScore

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		return lbDatas.NEEDPOINT % self.personalScore

class PriceAccumPoint( Price ):
	"""
	����ֵ����Ʒ
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_ROLE_ACCUM_POINT
		self.accumPoint = 0

	def load( self, priceData ):
		"""
		"""
		self.accumPoint = priceData["accumPoint"]

	def addToDict( self ):
		"""
		�������ڴ�����ֵ�
		"""
		return { "param": { "priceType":csdefine.INVOICE_NEED_ROLE_ACCUM_POINT, "accumPoint":self.accumPoint } }

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		return lbDatas.NEEDACCUMPOINT % self.accumPoint

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		return lbDatas.NEEDACCUMPOINT % self.accumPoint


class PriceSoulCoin( PriceAccumPoint ) :
	"""
	���һ���Ʒ������������ʵҲ�ǲ�������ֵ�������ǽ���ʱ
	���ᾭ����ҵı����������е���Ʒϵͳ������Ӣ�����˸���
	��װ������
	"""
	def __init__( self ) :
		PriceAccumPoint.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_SOUL_COIN
		self.accumPoint = 0

	def load( self, priceData ):
		"""
		"""
		self.accumPoint = priceData["accumPoint"]

	def addToDict( self ):
		"""
		�������ڴ�����ֵ�
		"""
		return { "param": { "priceType":csdefine.INVOICE_NEED_SOUL_COIN, "accumPoint":self.accumPoint } }

	def checkRequire( self, player, chapman, invoiceAmount ):
		"""
		�������Ƿ��ܹ�����
		"""
		if player.accumPoint < self.accumPoint * invoiceAmount:
			return csstatus.NOT_ENOUGH_SOUL_COIN
		return csstatus.NPC_TRADE_CAN_BUY

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		return lbDatas.PRICE + self.getNeedDescription( chapman )

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		return  str( self.accumPoint ) + PL_Image.getSource( "guis/general/specialMerchantWnd/soulcoin.gui" )

class PriceCampHonour( Price ):
	"""
	���˾������ֻ�ȡ��Ʒ
	"""
	def __init__( self ):
		Price.__init__( self )
		self.priceType = csdefine.INVOICE_NEED_CAMP_HONOUR
		self.campHonour = 0

	def load( self, priceData ):
		"""
		"""
		self.campHonour = priceData["campHonour"]

	def addToDict( self ):
		"""
		�������ڴ�����ֵ�
		"""
		return { "param": { "priceType":csdefine.INVOICE_NEED_CAMP_HONOUR, "campHonour":self.campHonour } }

	def getDescription( self, chapman ):
		"""
		��ü۸������
		"""
		return lbDatas.NEEDCAMPHONOUR % self.campHonour

	def getNeedDescription( self, chapman ):
		"""
		��ȡ��������
		"""
		return lbDatas.NEEDCAMPHONOUR % self.campHonour


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

