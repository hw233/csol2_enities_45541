# -*- coding: gb18030 -*-
#
# $Id: Chapman.py
"""
Chapman基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from Chapman import Chapman
from TongSpecialItemsData import TongSpecialItemsData
tongSpecialDatats = TongSpecialItemsData.instance()

class TongSpecialChapman( Chapman ):
	"""
	帮会特殊商人,只能帮主购买
	"""
	def __init__( self ):
		Chapman.__init__( self )
		BigWorld.globalData[ "TongManager" ].requestTongSpecialItems( self.ownTongDBID, self.base )
	
	def onRequestOpenTongSpecialShop( self, srcEntityID, talkID, isEnough ):
		"""
		define method
		请求与商店NPC对话
		"""
		self.getScript().onRequestOpenTongSpecialShop( self, srcEntityID, talkID, isEnough )
	
	def lock( self ):
		"""
		define method.
		Chapman被锁住， 帮会成员无法和他交互
		"""
		self.locked = True

	def unlock( self ):
		"""
		define method.
		Chapman被开锁， 帮会成员恢复和他交互
		"""
		self.locked = False
	
	def initTongSpecialItems( self, tongLevel, reset ):
		"""
		初始化特殊商品
		"""
		if reset:
			self.clearTongSpecItems()
		
		items = []
		itemDatas = tongSpecialDatats.getDatas()

		for itemID, item in itemDatas.iteritems():
			# 防止超过物品最大级别
			if tongLevel >= item[ "reqTongLevel" ]:
				self.onRegisterTongSpecialItem( itemID, item["amount"] )

	def onRegisterTongSpecialItem( self, itemID, amount ):
		"""
		define method.
		当领地被创建后， 把商品数据注册到领地的NPC
		"""
		if itemID <= 0 or amount == 0:
			ERROR_MSG( "tong chapman register is fail %i, %i." % ( itemID, amount ) )
			return

		specialItems = self.queryTemp( "specialItems", None )
		if specialItems is None:
			specialItems = []
			self.setTemp( "specialItems", specialItems )

		if not itemID in specialItems:
			specialItems.append( itemID )

		for key, item in self.attrInvoices.iteritems():
			if item.getSrcItem().id == itemID:
				reqMoney = 0
				if tongSpecialDatats.hasSpecialItem( itemID ):
					reqMoney = tongSpecialDatats[itemID]["reqMoney"]
				for priceInstance in item.priceInstanceList:						#转换为所需帮会资金
					if priceInstance.getPriceData()["priceType"] == csdefine.INVOICE_NEED_MONEY:
						priceInstance.money = reqMoney
				if amount < 0:
					item.setMaxAmount( -1 )
				else:
					item.setMaxAmount( amount + 1 )
					item.setAmount( amount )
				return

	def clearTongSpecItems( self ):
		"""
		清除数据
		"""
		specialItems = self.queryTemp( "specialItems", None )
		if specialItems is None:
			return
		for itemID in specialItems:
			self.resetItemAmount( itemID )

	def resetItemAmount( self, itemID ):
		"""
		重置商品数量
		"""
		for key, item in self.attrInvoices.iteritems():
			if item.getSrcItem().id == itemID:
				item.setMaxAmount( 0 )
				item.setAmount( 0 )

	def getSpecialItems( self ):
		"""
		获取商品清单数据
		"""
		return self.queryTemp( "specialItems", [] )

	def removeSpecItem( self, itemID ):
		"""
		从清单中清除一个物品
		"""
		self.queryTemp( "specialItems" ).remove( itemID )


	def sellArrayTo( self, srcEntityId, memberDBID, argIndices, argAmountList ):
		"""
		商人把东西卖给玩家

		@param srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type  srcEntityId: int
		@param argIndices: 要买的哪个商品
		@type  argIndices: ARRAY <of> UINT16	</of>
		@param argAmountList: 要买的数量
		@type  argAmountList: ARRAY <of> UINT16	</of>
		@return: 			无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		self.getScript().sellArrayTo( self, srcEntity, memberDBID, argIndices, argAmountList )

	def sellToCB( self, memberDBID, invoiceID, amount, playerID ):
		"""
		给玩家的回调
		@param   memberDBID: 帮会成员dbid
		@type    argIndex: DATABASE_ID
		@param   argIndex: 要买的哪个商品
		@type    argIndex: itemid
		@param   amount: 要买的数量
		@type    amount: UINT16
		"""
		player = BigWorld.entities.get( playerID, None )
		if player is None:return
		Info = self.getInvoiceByItemInfo( invoiceID )
		if Info is None:return
		argIndex = Info[0]
		objInvoice = Info[1]
		if objInvoice.getAmount() < 0:		# 如果物品的数量为-1，表示可无限购买，所以物品数量改变后不通知客户端
			return
		userDBID = player.databaseID
		BigWorld.globalData[ "TongManager" ].onSellSpecialItems( self.ownTongDBID, player.base, memberDBID, objInvoice.getSrcItem().id, amount )

	
	def getInvoiceByItemInfo( self, itemID ):
		"""
		获取Invoice
		"""
		for index, invoice in self.attrInvoices.iteritems():
			srcItem = invoice.getSrcItem()
			if srcItem.id == itemID:
				return index, invoice

	def requestInvoice( self, srcEntityId, startPos ):
		"""
		Expose method
		请求一批商品
		@param startPos: 商品开始位置
		@type startPos: INT16
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return
		if startPos > len( self.getSpecialItems() ):
			return
		minLen = min( startPos+13, len( self.getSpecialItems() ) )
		clientEntity = srcEntity.clientEntity( self.id )
		for i in xrange( startPos, minLen+1, 1 ):
			try:
				itemID = self.getSpecialItems()[ i - 1 ]
			except IndexError, errstr:
				ERROR_MSG( "%s(%i): no souch index.", errstr )
				continue
			for key, item in self.attrInvoices.iteritems():
				if item.getSrcItem().id == itemID:
					clientEntity.addInvoiceCB( key, item )

	def sendInvoiceListToClient( self, srcEntityId ):
		"""
		提供给client的方法，向client的自己发送商品列表

		@param srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type  srcEntityId: int
		@return: 无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
		#srcEntity.设置状态为交易状态()
		invoices = self.getSpecialItems()
		length = len( invoices )
		clientEntity = srcEntity.clientEntity( self.id )
		clientEntity.resetInvoices( length )
		clientEntity.onInvoiceLengthReceive( length )
	
	def onSellSpecialItems( self, playerID, invoiceID, amount ):
		"""
		define method
		base上购买成功回调
		"""
		player = BigWorld.entities.get( playerID, None )
		if player is None:return
		Info = self.getInvoiceByItemInfo( invoiceID )
		if Info is None:return
		argIndex = Info[0]
		objInvoice = Info[1]
		if objInvoice.getAmount() < 0:		# 如果物品的数量为-1，表示可无限购买，所以物品数量改变后不通知客户端
			return
		objInvoice.addAmount( -amount )
		if objInvoice.getAmount() == 0:
			objInvoice.setAmount( 0 )
			objInvoice.setMaxAmount( 1 )
			self.removeSpecItem( objInvoice.getSrcItem().id )
		else:
			objInvoice.setMaxAmount( objInvoice.getAmount() + 1 )
		if player: # 数量改变通知客户端
			clientChapman = player.clientEntity( self.id )
			clientChapman.onReceiveGoodsAmountChange( argIndex, objInvoice.getAmount() )
