# -*- coding: gb18030 -*-
#
# $Id: Chapman.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Chapman基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from Chapman import Chapman
from TongItemResearchData import TongItemResearchData
tongItemResearchData = TongItemResearchData.instance()

class TongChapman( Chapman ):
	"""
	帮会领地商人Chapman基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Chapman.__init__( self )
		BigWorld.globalData[ "TongManager" ].requestTongItems( self.ownTongDBID, self.base )
	
	def onRequestOpenTongShop( self, srcEntityID, talkID, isEnough ):
		"""
		define method
		请求与商店NPC对话
		"""
		self.getScript().onRequestOpenTongShop( self, srcEntityID, talkID, isEnough )

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

	def onRestoreInvoices( self, timerID, cbID ):
		"""
		恢复所有商品到最大数量

		@param timerID: 使用addTimer()方法时产生的标志，由onTimer()被触发时自动传递进来
		@type  timerID: int
		@param    cbID: 当前方法所代表的编号，同样由onTimer()被触发时自动传递进来
		@type     cbID: int
		@return: 无
		"""
		self.cancel( timerID )

	def initTongItems( self, sdLevel, reset ):
		"""
		define method
		初始化/重置帮会物品
		"""
		if reset:
			self.clearTongItems()
		
		items = []
		itemDatas = tongItemResearchData.getDatas()

		for itemID, item in itemDatas.iteritems():
			# 防止超过物品最大级别
			if sdLevel >= item[ "repBuildingLevel" ]:
				self.onRegisterTongItem( itemID, item["amount"] )

	def clearTongItems( self ):
		"""
		清除数据
		"""
		sellData = self.queryTemp( "sellData", None )
		if sellData == None:
			return
		for itemID in sellData:
			self.resetItemAmount( itemID )

	def resetItemAmount( self, itemID ):
		"""
		重置商品数量
		"""
		for key, item in self.attrInvoices.iteritems():
			if item.getSrcItem().id == itemID:
				item.setMaxAmount( 0 )
				item.setAmount( 0 )
		
	def onRegisterTongItem( self, itemID, amount ):
		"""
		define method.
		当领地被创建后， 帮会会把自身研发的物品注册到领地的NPC
		"""
		if itemID <= 0 or amount == 0:
			ERROR_MSG( "tong chapman register is fail %i, %i." % ( itemID, amount ) )
			return

		sellData = self.queryTemp( "sellData", None )
		if sellData == None:
			sellData = []
			self.setTemp( "sellData", sellData )

		if not itemID in sellData:
			sellData.append( itemID )

		for key, item in self.attrInvoices.iteritems():
			if item.getSrcItem().id == itemID:
				if amount < 0:
					item.setMaxAmount( -1 )
				else:
					item.setMaxAmount( amount + 1 )
					item.setAmount( amount )
				return

	def onGetMemberBuyRecord( self, record ):
		"""
		define method
		当领地被创建后， 帮会会把帮众购买物品记录发送到领地的NPC
		"""
		memberBuyRecord = self.queryTemp( "memberBuyRecord", {} )
		dbid = record[ "dbID" ]
		if not dbid in memberBuyRecord.keys():
			memberBuyRecord[ dbid] = {}
			for item in record[ "record" ]:
				itemID = item[ "itemID" ]
				amount = item[ "amount"]
				memberBuyRecord[ dbid][ itemID ] = amount
		
		self.setTemp( "memberBuyRecord", memberBuyRecord )

	def getInvoiceData( self ):
		"""
		获取商品清单数据
		"""
		return self.queryTemp( "sellData", [] )

	def removeInvoice( self, itemID ):
		"""
		从清单中清除一个物品
		"""
		self.queryTemp( "sellData" ).remove( itemID )

	def sellToCB( self, argIndex, argAmount, playerEntityID ):
		"""
		给玩家的回调

		@param   argIndex: 要买的哪个商品
		@type    argIndex: UINT16
		@param   argAmount: 要买的数量
		@type    argAmount: UINT16
		"""
		try:
			playerEntity = BigWorld.entities[playerEntityID]
			objInvoice = self.attrInvoices[ argIndex ]
		except IndexError, errstr:
			return
			
		if objInvoice.getAmount() < 0:		# 如果物品的数量为-1，表示可无限购买，所以物品数量改变后不通知客户端
			return
			
		objInvoice.addAmount( -argAmount )
		BigWorld.globalData[ "TongManager" ].onSellItems( self.ownTongDBID, playerEntity.databaseID, objInvoice.getSrcItem().id, argAmount )
		self.updateMemberBuyRecord(  playerEntity.databaseID, objInvoice.getSrcItem().id, argAmount )
		if objInvoice.getAmount() == 0:
			objInvoice.setAmount( 0 )
			objInvoice.setMaxAmount( 1 )
			self.removeInvoice( objInvoice.getSrcItem().id )
		else:
			objInvoice.setMaxAmount( objInvoice.getAmount() + 1 )
		if playerEntity is not None: # 数量改变后通知客户端
			clientMerchant = playerEntity.clientEntity( self.id )
			clientMerchant.onReceiveGoodsAmountChange( argIndex, objInvoice.getAmount() )

	def updateMemberBuyRecord( self, roleDBID, itemID, amount ):
		"""
		更新玩家购买记录{ dbid: { itemID: amount, itemID: amount } }
		"""
		memberBuyRecord = self.queryTemp( "memberBuyRecord", {} )
		if len( memberBuyRecord ) != 0:
			for dbid, record in memberBuyRecord.items():
				if dbid == roleDBID:
					for id, val in record.items():
						if id == itemID:
							memberBuyRecord[ dbid ][ itemID ] += amount
							self.setTemp( "memberBuyRecord", memberBuyRecord )
							return
					
					memberBuyRecord[ dbid ][ itemID ] = amount
					self.setTemp( "memberBuyRecord", memberBuyRecord )
					return
		
		buyRecord = {}
		buyRecord[ itemID ] = amount
		memberBuyRecord[ roleDBID ] = buyRecord
		self.setTemp( "memberBuyRecord", memberBuyRecord )

	def getRoleBoughtNum( self, roleDBID, itemID ):
		"""
		获得玩家已购买数量
		"""
		memberBuyRecord = self.queryTemp( "memberBuyRecord", {} )
		if len( memberBuyRecord ) == 0:					# 没有记录
			return 0
		
		for dbid, record in memberBuyRecord.items():
			if dbid == roleDBID:
				for id, val in record.items():
					if id == itemID:
						return val
		return 0

	def getItemBuyUpperLimit( self, itemID ):
		"""
		获得物品的购买上限
		"""
		upperLimit = int( tongItemResearchData.getDatas()[ itemID ][ 'buyUpperLimit' ] )
		return upperLimit

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
		if startPos > len( self.getInvoiceData() ):
			return
		minLen = min( startPos+13, len( self.getInvoiceData() ) )
		clientEntity = srcEntity.clientEntity( self.id )

		for i in xrange( startPos, minLen+1, 1 ):
			try:
				itemID = self.getInvoiceData()[ i - 1 ]
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

		#if srcEntity.处于与交易相冲的其它状态中():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), state mode not right, perhaps have a deceive." % (srcEntityId) )
		#	return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#srcEntity.设置状态为交易状态()
		invoices = self.getInvoiceData()
		length = len( invoices )
		clientEntity = srcEntity.clientEntity( self.id )
		clientEntity.resetInvoices( length )
		clientEntity.onInvoiceLengthReceive( length )

	#----------------------------------------------帮会修理物品-------------------------------------------------

	def repairOneEquip( self, srcEntityId, kitBagID, orderID, repairLevel ):
		"""
		expose method.
		修理玩家的一个装备一次
		@param    srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type     srcEntityId: int
		@param    kitBagID: 背包索引
		@type     kitBagID: int
		@param    orderID: 物品索引
		@type     orderID: int
		@param    repairLevel: 修理模式
		@type     repairLevel: int
		@return   无
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_REPAIRER ):
			return

		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.tong_repairOneEquip( repairLevel, kitBagID, orderID )

	def repairAllEquip( self, srcEntityId, repairLevel ):
		"""
		expose method.
		修理所有装备
		@param    srcEntityId: 由于使用了<Expose/>，这个是由系统自动传递进来的，表示是哪个client上的调用
		@type     srcEntityId: int
		"""
		# 要是修理NPC将"repair"置为1即可
		#if not self.query("repair"):
		#	return
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_REPAIRER ):
			return

		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
			return

		# 确定用户在你的距离内
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.tong_repairAllEquip( repairLevel )

# Chapman.py
