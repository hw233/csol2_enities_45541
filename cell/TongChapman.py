# -*- coding: gb18030 -*-
#
# $Id: Chapman.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
Chapman����
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
	����������Chapman����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Chapman.__init__( self )
		BigWorld.globalData[ "TongManager" ].requestTongItems( self.ownTongDBID, self.base )
	
	def onRequestOpenTongShop( self, srcEntityID, talkID, isEnough ):
		"""
		define method
		�������̵�NPC�Ի�
		"""
		self.getScript().onRequestOpenTongShop( self, srcEntityID, talkID, isEnough )

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

	def onRestoreInvoices( self, timerID, cbID ):
		"""
		�ָ�������Ʒ���������

		@param timerID: ʹ��addTimer()����ʱ�����ı�־����onTimer()������ʱ�Զ����ݽ���
		@type  timerID: int
		@param    cbID: ��ǰ����������ı�ţ�ͬ����onTimer()������ʱ�Զ����ݽ���
		@type     cbID: int
		@return: ��
		"""
		self.cancel( timerID )

	def initTongItems( self, sdLevel, reset ):
		"""
		define method
		��ʼ��/���ð����Ʒ
		"""
		if reset:
			self.clearTongItems()
		
		items = []
		itemDatas = tongItemResearchData.getDatas()

		for itemID, item in itemDatas.iteritems():
			# ��ֹ������Ʒ��󼶱�
			if sdLevel >= item[ "repBuildingLevel" ]:
				self.onRegisterTongItem( itemID, item["amount"] )

	def clearTongItems( self ):
		"""
		�������
		"""
		sellData = self.queryTemp( "sellData", None )
		if sellData == None:
			return
		for itemID in sellData:
			self.resetItemAmount( itemID )

	def resetItemAmount( self, itemID ):
		"""
		������Ʒ����
		"""
		for key, item in self.attrInvoices.iteritems():
			if item.getSrcItem().id == itemID:
				item.setMaxAmount( 0 )
				item.setAmount( 0 )
		
	def onRegisterTongItem( self, itemID, amount ):
		"""
		define method.
		����ر������� ����������з�����Ʒע�ᵽ��ص�NPC
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
		����ر������� ����Ѱ��ڹ�����Ʒ��¼���͵���ص�NPC
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
		��ȡ��Ʒ�嵥����
		"""
		return self.queryTemp( "sellData", [] )

	def removeInvoice( self, itemID ):
		"""
		���嵥�����һ����Ʒ
		"""
		self.queryTemp( "sellData" ).remove( itemID )

	def sellToCB( self, argIndex, argAmount, playerEntityID ):
		"""
		����ҵĻص�

		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: UINT16
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		"""
		try:
			playerEntity = BigWorld.entities[playerEntityID]
			objInvoice = self.attrInvoices[ argIndex ]
		except IndexError, errstr:
			return
			
		if objInvoice.getAmount() < 0:		# �����Ʒ������Ϊ-1����ʾ�����޹���������Ʒ�����ı��֪ͨ�ͻ���
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
		if playerEntity is not None: # �����ı��֪ͨ�ͻ���
			clientMerchant = playerEntity.clientEntity( self.id )
			clientMerchant.onReceiveGoodsAmountChange( argIndex, objInvoice.getAmount() )

	def updateMemberBuyRecord( self, roleDBID, itemID, amount ):
		"""
		������ҹ����¼{ dbid: { itemID: amount, itemID: amount } }
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
		�������ѹ�������
		"""
		memberBuyRecord = self.queryTemp( "memberBuyRecord", {} )
		if len( memberBuyRecord ) == 0:					# û�м�¼
			return 0
		
		for dbid, record in memberBuyRecord.items():
			if dbid == roleDBID:
				for id, val in record.items():
					if id == itemID:
						return val
		return 0

	def getItemBuyUpperLimit( self, itemID ):
		"""
		�����Ʒ�Ĺ�������
		"""
		upperLimit = int( tongItemResearchData.getDatas()[ itemID ][ 'buyUpperLimit' ] )
		return upperLimit

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

		#if srcEntity.�����뽻����������״̬��():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), state mode not right, perhaps have a deceive." % (srcEntityId) )
		#	return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#srcEntity.����״̬Ϊ����״̬()
		invoices = self.getInvoiceData()
		length = len( invoices )
		clientEntity = srcEntity.clientEntity( self.id )
		clientEntity.resetInvoices( length )
		clientEntity.onInvoiceLengthReceive( length )

	#----------------------------------------------���������Ʒ-------------------------------------------------

	def repairOneEquip( self, srcEntityId, kitBagID, orderID, repairLevel ):
		"""
		expose method.
		������ҵ�һ��װ��һ��
		@param    srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type     srcEntityId: int
		@param    kitBagID: ��������
		@type     kitBagID: int
		@param    orderID: ��Ʒ����
		@type     orderID: int
		@param    repairLevel: ����ģʽ
		@type     repairLevel: int
		@return   ��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_REPAIRER ):
			return

		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.tong_repairOneEquip( repairLevel, kitBagID, orderID )

	def repairAllEquip( self, srcEntityId, repairLevel ):
		"""
		expose method.
		��������װ��
		@param    srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type     srcEntityId: int
		"""
		# Ҫ������NPC��"repair"��Ϊ1����
		#if not self.query("repair"):
		#	return
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_REPAIRER ):
			return

		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.tong_repairAllEquip( repairLevel )

# Chapman.py
