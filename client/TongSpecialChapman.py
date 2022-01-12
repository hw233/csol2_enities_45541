# -*- coding: gb18030 -*-
#
# $Id: TongSpecialChapman.py

"""
Chapman基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
import GUIFacade
from Chapman import Chapman

class TongSpecialChapman( Chapman ):
	"""
	帮会领地商人NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Chapman.__init__( self )
		self.invoiceIndexList = []
		self.__invoiceCount = 0				# 商品数量( hyw -- 2008.09.16 )

	def enterWorld( self ) :
		Chapman.enterWorld( self )

	def leaveWorld( self ) :
		Chapman.leaveWorld( self )

	def addInvoiceCB( self, argUid, argInvoice ):
		"""
		增加一个商品

		@param  argUid: 该商品的唯一标识符
		@type   argUid: UINT16
		@param argInvoice: InvoiceDataType类型的商品实例
		@type  argInvoice: class instance
		"""
		item = argInvoice.getSrcItem()
		argInvoice.uid = argUid													# 记录唯一标识
		item.set( "invoiceType", argInvoice.getItemType() )
		item.setAmount( argInvoice.getAmount() )
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

	def onReceivePriceChangeInfo( self, priceChangeInfo ):
		"""
		接收到服务器发送过来的价格变动信息
		"""
		ECenter.fireEvent( "EVT_ON_RECEIVE_PRICE_CHANGE_INFO", priceChangeInfo )

	def onReceiveGoodsAmountChange( self, index, currAmount ):
		"""
		接受到服务器商品数量改变通知

		@param	uid:		商品ID
		@type	uid:		UINT16
		@param	currAmount:	商品剩余数量
		@param	currAmount:	UINT16
		"""
		GUIFacade.updateInvoiceAmount( index, currAmount )

	def onReceiveSpecialItems( self, itemDatas ):
		"""
		接收商品数据
		"""
		pass
	