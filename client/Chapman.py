# -*- coding: gb18030 -*-

"""This module implements the Chapman for client.

@requires: L{ChapmanBase<ChapmanBase>}, L{Role<Role>}
"""
# $Id: Chapman.py,v 1.36 2008-08-11 02:40:55 huangyongwei Exp $

import BigWorld
from bwdebug import *
import InvoicesPackType
import NPC
import Math
import math
import GUI
import GUIFacade

from utils import *

TIME_TO_GET_INVOICE = 0.5
def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	策划规则是：如果价钱小于1，就算1
	如果大于1，则取整
	"""
	if price < 1:
		return 1
	return int( price )

class Chapman( NPC.NPC ):
	"""An Chapman class for client.
	商人NPC

	@ivar      attrInvoices: 货物列表
	@type      attrInvoices: INVOICEITEMS
	@ivar    invSellPercent: 出售价格百份比，例如：1.0表示原价，0.5表示半价，2.0表示双倍价格等，更新由服务器通知
	@type    invSellPercent: float
	@ivar    invBuyPercent: 回收价格百分比，例如：1.0表示原价，0.5表示半价，2.0表示双倍价格等，更新由服务器通知
	@type    invBuyPercent: float
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )
		self.invoiceIndexList = []
		self.__invoiceCount = 0				# 商品数量( hyw -- 2008.09.16 )
		#self.attrInvoices = InvoicesPackType.instance.defaultValue()

	def enterWorld( self ) :
		NPC.NPC.enterWorld( self )

	def leaveWorld( self ) :
		self.__invoiceCount = 0				# 清空商品数量( hyw -- 2008.09.16 )
		NPC.NPC.leaveWorld( self )

	def addInvoiceCB( self, argUid, argInvoice ):
		"""
		增加一个商品

		@param  argUid: 该商品的唯一标识符
		@type   argUid: UINT16
		@param argInvoice: InvoiceDataType类型的商品实例
		@type  argInvoice: class instance
		"""
		item = argInvoice.getSrcItem()
		if item is None: return
		item.set( "price", priceCarry( item.getPrice() * self.invSellPercent ) )		# 计算新价格
		item.set( "invoiceType", argInvoice.getItemType() )								# 商品按使用对象分的类别（hyw--08.08.11）
		item.setAmount( argInvoice.getAmount() )
		argInvoice.uid = argUid														# 记录唯一标识
		#self.attrInvoices[argUid] = argInvoice
		GUIFacade.onInvoiceAdded( self.id, argInvoice )

		if argUid == self.__invoiceCount :											# 表示申请完毕（hyw--2008.06.16）
			self.__invoiceCount = 0

	def resetInvoices( self, space ):
		"""
		清除商品列表

		@param space: 商人的商品数量
		@type  space: INT8
		"""
		#self.attrInvoices.clear()
		GUIFacade.onResetInvoices( space )

	def onBuyArrayFromCB( self, state ):
		"""
		批量物品回收回调

		@param state: 回收状态，1 = 成功， 0 = 失败
		@type  state: UINT8
		@return: 无
		"""
		#INFO_MSG( "state = %i" % state )
		GUIFacade.onSellToNPCReply( state )

	def onInvoiceLengthReceive( self, length ):
		"""
		define method
		获得商品列表长度
		"""
		GUIFacade.setInvoiceAmount( length )
		self.invoiceIndexList = range( 1, length + 1, 1 )
		self.__invoiceCount = length						# 记下商品总数量（hyw -- 2008.09.16）
		if length == 0:
			return
		self.requestInvoice()

	def requestInvoice( self ):
		"""
		获得一批商品列表
		"""
		length = len( self.invoiceIndexList )
		if length > 0:
			self.cell.requestInvoice( self.invoiceIndexList[0] ) #请求一批商品列表， 暂时是 14个
		if length > 14:
			self.invoiceIndexList = self.invoiceIndexList[14:]
			BigWorld.callback( TIME_TO_GET_INVOICE, self.requestInvoice )
		else:
			self.invoiceIndexList = []

	def isRequesting( self ) :
		"""
		是否正在申请商品列表
		hyw -- 2008.09.16
		"""
		return self.__invoiceCount > 0

# end of class Chapman #

