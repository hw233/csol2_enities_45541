# -*- coding: gb18030 -*-

"""
This module implements the invoice data type.

@var instance: InvoiceDataType类型的实例，主要为了在res\entities\defs\alias.xml中实现自定义数据类型——INVOICEITEM
@requires: L{CItemProp<CItemProp>}, L{ItemDataList<ItemDataList>}
"""

from bwdebug import *
import NPCTradePrice
import ItemTypeEnum
import BigWorld
import csconst
import csdefine
import csstatus
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Align import PL_Align

g_midAlign = PL_Align.getSource( lineFlat = "M")

class InvoiceDataType:
	"""
	实现res\entities\defs\alias.xml中的自定义数据类型INVOICEITEM；
	其中包括Database、Stream、XML Data接口以及封装方法实现

	@ivar	maxAmount: 该道具最大出售数量
	@type	maxAmount: UINT16
	@ivar  currAmount: 该道具当前拥有的数量
	@type  currAmount: UINT16
	@ivar     srcItem: 继承于CItemBase的道具实例
	@type     srcItem: class instance
	"""
	def __init__( self ):
		# 基础属性
		self.maxAmount = 0					# 最大数量(UINT16)
		self.currAmount = 0					# 当前数量(UINT16)
		self.itemType = 0					# 按使用者分的商品类型（hyw--08.08.11）
		self.srcItem = None					# 继承于CItemBase的道具实例
		self.priceInstanceList = []			# 交易价格实例
		self.invoiceType = csdefine.INVOICE_CLASS_TYPE_NORMAL

	def getDictFromObj( self, obj ):
		"""
		The method converts a wrapper instance to a FIXED_DICT instance.

		@param obj: The obj parameter is a wrapper instance.
		@return: This method should return a dictionary(or dictionary-like object) that contains the same set of keys as a FIXED_DICT instance.
		"""
		return obj.__dict__.copy()

	def createObjFromDict( self, dict ):
		"""
		This method converts a FIXED_DICT instance to a wrapper instance.

		@param dict: The dict parameter is a FIXED_DICT instance.
		@return: The method should return the wrapper instance constructed from the information in dict.
		"""
		invoice = createInvoiceInstace( dict["invoiceType"] )
		invoice.__dict__.update( dict )
		return invoice

	def isSameType( self, obj ):
		"""
		This method check whether an object is of the wrapper type.

		@param obj: The obj parameter in an arbitrary Python object.
		@return: This method should return true if obj is a wrapper instance.
		"""
		return isinstance( obj, InvoiceDataType )

	def copy( self ):
		"""
		复制自己

		@return: InvoiceDataType实例
		@rtype:  instance of InvoiceDataType
		"""
		obj = createInvoiceInstace( self.invoiceType )
		obj.__dict__.update( self.__dict__ )		# 复制属性
		obj.srcItem = self.srcItem.new()			# 复制源实例
		return obj

	def setAmount( self, argAmount ):
		"""
		设置当前商品的数量

		@param argAmount: 当前的数量
		@type argAmount: int
		@return: 无
		"""
		if self.maxAmount < argAmount:
			self.currAmount = self.maxAmount
		else:
			self.currAmount = argAmount

	def getAmount( self ):
		"""
		获得商品的当前数量

		@return: 商品的当前数量
		@rtype: int
		"""
		return self.currAmount

	def addAmount( self, argAmount ):
		"""
		给当前商品增加一定的数量

		@param argAmount: 要增加的数量
		@type argAmount: int
		@return: 无
		"""
		self.currAmount += argAmount
		if self.currAmount > self.maxAmount:
			self.currAmount = self.maxAmount
		elif self.currAmount < 0:
			self.currAmount = 0

	def getMaxAmount( self ):
		"""
		获取最大可销售数量

		@return: INT32
		@rtype:  INT32
		"""
		return self.maxAmount

	def setMaxAmount( self, argAmount ):
		"""
		给当前商品设置允许存在的最大数量

		@param argAmount: 最大数量
		@type argAmount: int
		@return: 无
		"""
		self.maxAmount = argAmount

	def getItemType( self ) :
		"""
		获取商品类别( hyw -- 08.08.09 )
		"""
		return self.itemType

	def setItemType( self, itype ) :
		"""
		设置商品类别( hyw -- 08.08.09 )
		"""
		self.itemType = itype

	def setSrcItem( self, itemInstance ):
		"""
		设置真正的道具实例。
		注意：本方法并不复制道具实例，而是直接引用。
		这个方法通常是在初始化的时候使用，当已经关联了一个道具实例以后就不应该再改变它了。

		@param itemInstance: 继承于CItemBase的道具实例
		@type  itemInstance: class instance
		@return:             无
		"""
		self.srcItem = itemInstance

	def getSrcItem( self ):
		"""
		取得源始道具实例

		@return: 源始的继承于CItemBase的道具实例
		@rtype:  class instance
		"""
		return self.srcItem

	def checkRequire( self, chapmanEntity, invoiceAmount ):
		"""
		检查玩家是否满足买的需求
		"""
		creditDic = self.srcItem.credit()		# 声望需求检查
		player = BigWorld.player()
		for key in creditDic:
			value = player.getPrestige( key )
			if value is None or value < creditDic[key]:
				return csstatus.NPC_TRADE_NOT_ENOUGH_CREDIT
		for priceInstance in self.priceInstanceList:
			status = priceInstance.checkRequire( player, chapmanEntity, invoiceAmount )
			if status != csstatus.NPC_TRADE_CAN_BUY:
				return status
		return csstatus.NPC_TRADE_CAN_BUY

	def getPrice( self, chapman, amount = 1 ):
		"""
		获得相应数量商品的价格

		rType : [(priceType,price), ... ]
		"""
		priceList = []
		for priceInstance in self.priceInstanceList:
			priceList.append( ( priceInstance.priceType, priceInstance.getPrice( chapman, amount ) ) )
		return priceList

	def getDescription( self, chapman ):
		"""
		获得商品的描述
		"""
		des = self.srcItem.description( BigWorld.player() )			#获取道具的原来的描述
		item_integral = self.srcItem.query("warIntegral")
		tradeObject = chapman.__class__.__name__
		if tradeObject == "Chapman" and item_integral > 0:
			msg = ""
		else:
			msg = ""
			for priceInstance in self.priceInstanceList:
				msg += priceInstance.getDescription( chapman )
		if len( msg ) > 0:
			msg = g_midAlign + PL_Font.getSource( msg, fc = ( 0, 255, 0 ) )
			des.append( msg )
		return des

	def getPriceDescriptions( self, chapman ):
		"""
		获取价格需求描述
		"""
		needTextList = []
		for priceInstance in self.priceInstanceList:
			needTextList.append( priceInstance.getNeedDescription( chapman ) )
		return needTextList


class InvoiceBindItem( InvoiceDataType ):
	"""
	出售后被绑定的商品
	"""
	def __init__( self ):
		"""
		"""
		InvoiceDataType.__init__( self )
		self.invoiceType = csdefine.INVOICE_CLASS_TYPE_BIND


# 构造InvoiceDataType实例，res\entities\defs\alias.xml中使用
instance = InvoiceDataType()


def createInvoiceInstace( invoiceType ):
	"""
	创建商品实例
	"""
	if invoiceType == csdefine.INVOICE_CLASS_TYPE_NORMAL:
		invoice = InvoiceDataType()
	elif invoiceType == csdefine.INVOICE_CLASS_TYPE_BIND:
		invoice = InvoiceBindItem()
	else:
		invoice = InvoiceDataType()
	return invoice

