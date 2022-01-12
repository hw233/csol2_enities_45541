# -*- coding: gb18030 -*-
#
# $Id: Chapman.py
"""
Chapman����
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
	�����������,ֻ�ܰ�������
	"""
	def __init__( self ):
		Chapman.__init__( self )
		BigWorld.globalData[ "TongManager" ].requestTongSpecialItems( self.ownTongDBID, self.base )
	
	def onRequestOpenTongSpecialShop( self, srcEntityID, talkID, isEnough ):
		"""
		define method
		�������̵�NPC�Ի�
		"""
		self.getScript().onRequestOpenTongSpecialShop( self, srcEntityID, talkID, isEnough )
	
	def lock( self ):
		"""
		define method.
		Chapman����ס�� ����Ա�޷���������
		"""
		self.locked = True

	def unlock( self ):
		"""
		define method.
		Chapman�������� ����Ա�ָ���������
		"""
		self.locked = False
	
	def initTongSpecialItems( self, tongLevel, reset ):
		"""
		��ʼ��������Ʒ
		"""
		if reset:
			self.clearTongSpecItems()
		
		items = []
		itemDatas = tongSpecialDatats.getDatas()

		for itemID, item in itemDatas.iteritems():
			# ��ֹ������Ʒ��󼶱�
			if tongLevel >= item[ "reqTongLevel" ]:
				self.onRegisterTongSpecialItem( itemID, item["amount"] )

	def onRegisterTongSpecialItem( self, itemID, amount ):
		"""
		define method.
		����ر������� ����Ʒ����ע�ᵽ��ص�NPC
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
				for priceInstance in item.priceInstanceList:						#ת��Ϊ�������ʽ�
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
		�������
		"""
		specialItems = self.queryTemp( "specialItems", None )
		if specialItems is None:
			return
		for itemID in specialItems:
			self.resetItemAmount( itemID )

	def resetItemAmount( self, itemID ):
		"""
		������Ʒ����
		"""
		for key, item in self.attrInvoices.iteritems():
			if item.getSrcItem().id == itemID:
				item.setMaxAmount( 0 )
				item.setAmount( 0 )

	def getSpecialItems( self ):
		"""
		��ȡ��Ʒ�嵥����
		"""
		return self.queryTemp( "specialItems", [] )

	def removeSpecItem( self, itemID ):
		"""
		���嵥�����һ����Ʒ
		"""
		self.queryTemp( "specialItems" ).remove( itemID )


	def sellArrayTo( self, srcEntityId, memberDBID, argIndices, argAmountList ):
		"""
		���˰Ѷ����������

		@param srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type  srcEntityId: int
		@param argIndices: Ҫ����ĸ���Ʒ
		@type  argIndices: ARRAY <of> UINT16	</of>
		@param argAmountList: Ҫ�������
		@type  argAmountList: ARRAY <of> UINT16	</of>
		@return: 			��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		self.getScript().sellArrayTo( self, srcEntity, memberDBID, argIndices, argAmountList )

	def sellToCB( self, memberDBID, invoiceID, amount, playerID ):
		"""
		����ҵĻص�
		@param   memberDBID: ����Աdbid
		@type    argIndex: DATABASE_ID
		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: itemid
		@param   amount: Ҫ�������
		@type    amount: UINT16
		"""
		player = BigWorld.entities.get( playerID, None )
		if player is None:return
		Info = self.getInvoiceByItemInfo( invoiceID )
		if Info is None:return
		argIndex = Info[0]
		objInvoice = Info[1]
		if objInvoice.getAmount() < 0:		# �����Ʒ������Ϊ-1����ʾ�����޹���������Ʒ�����ı��֪ͨ�ͻ���
			return
		userDBID = player.databaseID
		BigWorld.globalData[ "TongManager" ].onSellSpecialItems( self.ownTongDBID, player.base, memberDBID, objInvoice.getSrcItem().id, amount )

	
	def getInvoiceByItemInfo( self, itemID ):
		"""
		��ȡInvoice
		"""
		for index, invoice in self.attrInvoices.iteritems():
			srcItem = invoice.getSrcItem()
			if srcItem.id == itemID:
				return index, invoice

	def requestInvoice( self, srcEntityId, startPos ):
		"""
		Expose method
		����һ����Ʒ
		@param startPos: ��Ʒ��ʼλ��
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
		�ṩ��client�ķ�������client���Լ�������Ʒ�б�

		@param srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type  srcEntityId: int
		@return: ��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
		#srcEntity.����״̬Ϊ����״̬()
		invoices = self.getSpecialItems()
		length = len( invoices )
		clientEntity = srcEntity.clientEntity( self.id )
		clientEntity.resetInvoices( length )
		clientEntity.onInvoiceLengthReceive( length )
	
	def onSellSpecialItems( self, playerID, invoiceID, amount ):
		"""
		define method
		base�Ϲ���ɹ��ص�
		"""
		player = BigWorld.entities.get( playerID, None )
		if player is None:return
		Info = self.getInvoiceByItemInfo( invoiceID )
		if Info is None:return
		argIndex = Info[0]
		objInvoice = Info[1]
		if objInvoice.getAmount() < 0:		# �����Ʒ������Ϊ-1����ʾ�����޹���������Ʒ�����ı��֪ͨ�ͻ���
			return
		objInvoice.addAmount( -amount )
		if objInvoice.getAmount() == 0:
			objInvoice.setAmount( 0 )
			objInvoice.setMaxAmount( 1 )
			self.removeSpecItem( objInvoice.getSrcItem().id )
		else:
			objInvoice.setMaxAmount( objInvoice.getAmount() + 1 )
		if player: # �����ı�֪ͨ�ͻ���
			clientChapman = player.clientEntity( self.id )
			clientChapman.onReceiveGoodsAmountChange( argIndex, objInvoice.getAmount() )
