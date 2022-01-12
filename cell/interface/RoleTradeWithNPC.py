# -*- coding: gb18030 -*-
#
# $Id: RoleTradeWithNPC.py,v 1.23 2008-08-08 06:49:52 kebiao Exp $

"""
"""

import BigWorld
import csdefine
import csconst
import csstatus
from bwdebug import *
from MsgLogger import g_logger
import ItemTypeEnum
import items
import sys
from TongItemResearchData import TongItemResearchData

tongItemResearchData = TongItemResearchData.instance()
g_item = items.instance()


def priceCarry( price ):
	"""
	2008-11-4 11:42 yk
	�߻������ǣ������ǮС��1������1
	�������1����ȡ��
	"""
	if price < 1:
		return 1
	return int( price )

def darkPriceCarry( price ):
	"""
	��������ȡ��
	"""
	return int( price + 0.5 )

JuanZhou = 50101025

class RoleTradeWithNPC:
	"""
	��NPC���˽���
	"""

	#self.redeemItems = []		# �������Ʒ�б�

	def calcCastellanPriceRebate( self, money ):
		"""
		����NPC���ڳ��еĳ�������(��ĳ���ռ��ĸó��к�)�Ĺ������
		"""
#		if self.tong_dbID > 0 and self.tong_holdCity == self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ):
#			return money * 0.9
		return money

	def sellToNPC( self, chapmanEntity, argUid, argAmount ):
		"""
		�������Ʒ
		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param   argUid: ��Ʒ��ΨһID
		@type    argUid: INT64
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return: 			��
		"""
		# ������������
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		# ȡ����Ҫ������Ʒ
		currItem = self.getItemByUid_( argUid )
		if currItem is None:
			ERROR_MSG( "%s(%i): I no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
			return
		# �������Ĳ����Գ���
		if not currItem.canSell():
			ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
			return
		# �ж���Ʒ�Ƿ񱻶��ᡣû��������жϵĻ������Ը�����Ʒʹ��Ч�������������ǣ���Ʒ�ɱ����۸�npc���ˣ���Ʒ����������ʱ�䡣
		# ���Ʒ��������ﵰΪ����ʹ����Ʒ����ʱ����Ʒ���۸�npc��ʹ�óɹ���ó����ʱ�������Ʒ������Ʒ�ֿɱ�ʹ�á�
		# 15:06 2009-10-20��wsf
		if currItem.isFrozen():
			return
		# ƭ�ˣ�������ϸ���û��ô��
		if currItem.getAmount() < argAmount:
			ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
			return
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		buyMoney = priceCarry( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount

		# �����ˡ�����
		if self.testAddMoney( buyMoney ) > 0:
			# �������Ǯ̫����
			ERROR_MSG( "%s(%i): �ֽ�̫����" % (self.playerName) )
			return

		# ��ɾ����Ʒ֮ǰ����Ʒ����������Ʒ�б�
		if currItem.amount == argAmount:
			# �����������Ʒ����ȥ
			tempItem = currItem
		else:
			# ����������Ʒ����ȥ��������Ҫ��new()����һ���µ���Ʒ����
			# �������Ա�֤��ص�ʱ����ƷUID��һ��
			# ��֤��������ͬuid����Ʒ���뵽�����У��Ӷ�����һЩ��ֵĴ���
			tempItem = currItem.new()
			tempItem.setAmount( argAmount )
		tempItem.setPrice( buyMoney )		# ������Ʒ�ļ۸�

		self._addRedeemItem( tempItem )

		# �������������Ʒ������
		#currItem.setAmount( currItem.getAmount() - argAmount, self )
		self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

		# ��Ǯ���
		self.gainMoney( int(buyMoney), csdefine.CHANGE_MONEY_SELLTONPC )
		# д��־
		try:
			g_logger.tradeNpcSellLog( self.databaseID, self.getName(), currItem.id, currItem.name(), currItem.getAmount(), self.grade, chapmanEntity.className )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	### end of buyFrom() method ###

	def sellArrayToNPC( self, chapmanEntity, argUidList, argAmountList ):
		"""
		define method
		�������Ʒ

		@param  chapmanEntity: ����NPC entity or mailbox
		@type   chapmanEntity: MAILBOX
		@param  argUidList: Ҫ����ĸ���Ʒ
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: Ҫ�������
		@type   argAmountList: ARRAY OF UINT16
		@return:               ��
		"""
		# ������������
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		chapmanEntity = BigWorld.entities.get( chapmanEntity.id, None )
		if chapmanEntity is None:
			return

		# �������Ҫ������Ʒ�Ĵ�������Լ����ܳ��ۺ���
		moneys = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# ��¼ÿһ����Ʒ
		moneyList = []	# ��¼ÿһ����Ʒ�������۸�
		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			if not currItem.canSell():	# �������Ĳ����Գ���
				self.statusMessage( csstatus.NPC_TRADE_ITEM_NOT_SELL )
				ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			# �ж���Ʒ�Ƿ񱻶��ᡣû��������жϵĻ������Ը�����Ʒʹ��Ч�������������ǣ���Ʒ�ɱ����۸�npc���ˣ���Ʒ����������ʱ�䡣
			# ���Ʒ��������ﵰΪ����ʹ����Ʒ����ʱ����Ʒ���۸�npc��ʹ�óɹ���ó����ʱ�������Ʒ������Ʒ�ֿɱ�ʹ�á�
			# 15:06 2009-10-20��wsf
			if currItem.isFrozen():
				self.statusMessage( csstatus.NPC_TRADE_ITEM_NOT_SELL )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			if currItem.getAmount() < argAmount:		# ƭ�ˣ�������ϸ���û��ô��
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			#moneys += int( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount

			currMoney = priceCarry( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount
			moneys += currMoney
			moneyList.append( currMoney )
			items.append( currItem )

		# �����ˡ�����
		if self.testAddMoney( moneys ) > 0:
			# �������Ǯ̫����
			ERROR_MSG( "%s(%i): �ֽ�̫����" % (self.playerName, self.id) )
			self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
			return
		for item, argAmount, money, argUid in zip( items, argAmountList, moneyList, argUidList ):
			# ��ɾ����Ʒ֮ǰ����Ʒ����������Ʒ�б�
			if item.amount == argAmount:
				# �����������Ʒ����ȥ
				tempItem = item
			else:
				# ����������Ʒ����ȥ��������Ҫ��new()����һ���µ���Ʒ����
				# �������Ա�֤��ص�ʱ����ƷUID��һ��
				# ��֤��������ͬuid����Ʒ���뵽�����У��Ӷ�����һЩ��ֵĴ���
				tempItem = item.new()
				tempItem.setAmount( argAmount )
			tempItem.setPrice( money )		# ������Ʒ�ļ۸�
			self._addRedeemItem( tempItem )
			#item.setAmount( item.getAmount() - argAmount, self )
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

			LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
				%( self.databaseID, self.getName(), chapmanEntity.className, chapmanEntity.getName(), tempItem.id, tempItem.name(), tempItem.amount ) )
				
			try:
				g_logger.tradeNpcSellLog( self.databaseID, self.getName(), item.uid, item.name(), item.getAmount(), self.grade, chapmanEntity.className )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )

		# ��Ǯ���
		self.gainMoney( int(moneys), csdefine.CHANGE_MONEY_SELLTONPC )
		self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 1 )	# ���۳ɹ�




	def buyFromNPC( self, chapmanEntity, newInvoice, argIndex, argAmount ):
		"""
		�������Ʒ

		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  newInvoice: Ҫ�����Ʒ
		@type   newInvoice: INVOICEITEM
		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: UINT16
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return:              ��
		"""
		# ������������
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		if not self.checkItemFromNKCK_( newInvoice.getSrcItem(), invoiceAmount ):
			self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]

		status = newInvoice.checkRequire( self, chapmanEntity, argAmount )
		if status != csstatus.NPC_TRADE_CAN_BUY:
			self.statusMessage( status )
			return
		newInvoice.doTrade(  self, chapmanEntity, argAmount )
		chapmanEntity.sellToCB( argIndex, argAmount, self.id )

	def haveEnoughCredit( self , item ):
		"""
		����Ƿ����㹻������
		@param  item : ��Ʒʵ��
		@type   item : ITEME
		@RETURN bool : �Ƿ���������������
		"""
		creditDic = item.credit()
		for key in creditDic:
			value = self.getPrestige( key )
			if value is None or value < creditDic[key]:
				return False
		return True

	def buyArrayFromNPC( self, chapmanEntity, invoiceArray, argIndices, argAmountList ):
		"""
		Define method.
		�������Ʒ

		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  invoiceArray: Ҫ�����Ʒʵ������
		@type   invoiceArray: ARRAY OF ITEM
		@param argIndices: Ҫ����ĸ���Ʒ
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: Ҫ�������
		@type  argAmountList: ARRAY OF UINT16
		@return:              ��
		"""
		# ������������
		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return
		zipInvoiceArray = zip( invoiceArray, argAmountList )
		items = []
		for invoiceItem, amount in zipInvoiceArray:
			item = invoiceItem.getSrcItem()
			item.setAmount( amount )
			items.append( item )
		kitbagState = self.checkItemsPlaceIntoNK_( items )
		if kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			return

		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		self.beginArrayBuyFromNPC()
		for invoiceItem, amount in zipInvoiceArray:
			status = invoiceItem.checkRequireArrayInvoice( self, chapmanEntity, amount )
			if status != csstatus.NPC_TRADE_CAN_BUY:
				self.statusMessage( status )
				self.endArrayBuyFromNPC()
				return
		for invoiceItem, amount in zipInvoiceArray:
			invoiceItem.doTrade(  self, chapmanEntity, amount )
			chapmanEntity.sellToCB( argIndices.pop( 0 ), amount, self.id )
		self.endArrayBuyFromNPC()

	def beginArrayBuyFromNPC( self ):
		"""
		��ʼ����������Ʒ��ʼ��
		"""
		self.setTemp( "npc_trade_money", 0 )
		self.setTemp( "npc_trade_need_items", {} )
		self.setTemp( "npc_trade_need_dancePoint", 0 )
		self.setTemp( "npc_trade_need_tongContribute", 0 )
		self.setTemp( "npc_trade_need_personalScore", 0 )
		self.setTemp( "npc_trade_need_teamCompetitionPoint",0 )
		self.setTemp( "npc_trade_need_accumPoint",0 )

	def endArrayBuyFromNPC( self ):
		"""
		����������Ʒ������ʱ������������
		"""
		self.removeTemp( "npc_trade_money" )
		self.removeTemp( "npc_trade_need_items" )
		self.removeTemp( "npc_trade_need_dancePoint" )
		self.removeTemp( "npc_trade_need_tongContribute" )
		self.removeTemp( "npc_trade_need_personalScore" )
		self.removeTemp( "npc_trade_need_teamCompetitionPoint" )
		self.removeTemp( "npc_trade_need_accumPoint" )

	# -------------------------------------------------------------------------------
	# ������Ʒ��ع��ܽӿ�
	# -------------------------------------------------------------------------------
	def _addRedeemItem( self, item ):
		"""
		��������б�������һ����Ʒ

		param item:	�����������Ʒ
		type item:	ITEM
		"""
		if len( self.redeemItems ) < csconst.REDEEM_ITEM_MAX_COUNT:	# ����Ʒ�Ž��������Ʒ�б�
			self.redeemItems.append( item )
		else:		# ����ɵ�����ɾ��
			self.redeemItems.pop( 0 )
			self.redeemItems.append( item )

		self.client.addRedeemItemUpdate( item )	# ֪ͨclient���¿�����б�����


	def redeemItem( self, srcEntityID, uid, entityID ):
		"""
		Exposed method.
		�����Ʒ�Ľӿ�

		param uid:	��Ʒ��Ψһ��ʶ
		type uid:	INT64
		param entityID:	����npc��id
		type entityID:	OBJECT_ID
		"""
		if self.id != srcEntityID:
			HACK_MSG( "�Ƿ�ʹ����, src(%i) calling dst(%i) method" % ( srcEntityID, self.id ) )
			return
		npc = BigWorld.entities.get( entityID )
		if npc == None:
			HACK_MSG( "lawless srcEntityID!, srcEntityID: %i, receiver: %i." % ( srcEntityID, self.id ) )
			return

		# �ж��Ƿ��������׷�Χ��
		if self.position.flatDistTo( npc.position ) > csconst.COMMUNICATE_DISTANCE:
			self.statusMessage( csstatus.BANK_TRADER_TOO_FAR )
			DEBUG_MSG( "too far from trade npc: %i. ( srcEntityID: %s )" % ( entityID, self.playerName ) )
			return

		if self.iskitbagsLocked():
			self.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return

		# ����ͳһ���ж϶�Ӧ�Ľ���npc������

		tempItem = None
		for item in self.redeemItems:
			if item.getUid() == uid:
				tempItem = item
				index = self.redeemItems.index( item )
				break
		if tempItem is None:
			HACK_MSG( "�������Ʒ�����ڡ�" )
			return

		# ����Ʒֱ�Ӷ�ȡ��Ʒ��¼�ļ۸�Ϳ���
		# ������Ҫ����ʲô����ļ���
		money = tempItem.getRecodePrice()
		if money > self.money:
			DEBUG_MSG( "��ҵ�Ǯ��������ش���Ʒ��" )
			return

		# ˢ��һ����Ʒ�ļ۸�
		tempItem.updatePrice()

		if not self.addItemAndNotify_( tempItem, csdefine.ADD_ITEM_REDEEMITEM ):	# ����ص���Ʒ���뱳��
			DEBUG_MSG( "��Ʒ���뱳��ʧ�ܣ���������Ϊ�������޿�λ��" )
			return
		self.redeemItems.pop( index )		# �ӿ�����б���ɾ����Ʒ
		self.payMoney( money, csdefine.CHANGE_MONEY_REDEEMITEM )				# �۳������Ӧ��Ǯ

		self.client.delRedeemItemUpdate( uid )	# ����client����

		LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
			%( self.databaseID, self.getName(), npc.className, npc.getName(), tempItem.id, tempItem.name(), tempItem.amount ) )

	def sellToDarkTrader( self, chapmanEntity, argUid, argAmount ):
		"""
		�������Ʒ��Ͷ������
		@param chapmanEntity: Ͷ������NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param   argUid: Ҫ�����ĸ���Ʒ
		@type    argUid: INT64
		@param   argAmount: Ҫ��������
		@type    argAmount: UINT16
		@return: 			��
		"""
		# ȡ����Ҫ������Ʒ
		currItem = self.getItemByUid_( argUid )
		if currItem is None:
			ERROR_MSG( "%s(%i): I no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
			return
		# ƭ�ˣ�������ϸ���û��ô��
		if currItem.getAmount() < argAmount:
			ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
			return
		itemPrice = currItem.getPrice()
		sellMoney = darkPriceCarry(  itemPrice * chapmanEntity.invBuyPercent ) * argAmount

		# ��ҳ��۵Ķ���������Ͷ���������չ���
		if currItem.id != chapmanEntity.currentGoodID:
			self.statusMessage( csstatus.NOT_DARK_TRADER_ITEM )
			return

		# �����ˡ�����
		if self.testAddMoney( sellMoney ) > 0:
			# �������Ǯ̫����
			ERROR_MSG( "%s(%i): �ֽ�̫����" % (self.playerName) )
			return

		# �������������Ʒ������
		self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

		# ��Ǯ���
		self.gainMoney( int( sellMoney ), csdefine.CHANGE_MONEY_SELLTONPC )

	def sellArrayToDarkTrader( self, chapmanEntity, argUidList, argAmountList ):
		"""
		�������Ʒ

		@param  chapmanEntity: ����NPC entity or mailbox
		@type   chapmanEntity: MAILBOX
		@param  argUidList: Ҫ����ĸ���Ʒ
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: Ҫ�������
		@type   argAmountList: ARRAY OF UINT16
		@return:               ��
		"""
		# �������Ҫ������Ʒ�Ĵ�������Լ����ܳ��ۺ���
		moneys = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# ��¼ÿһ����Ʒ
		moneyList = []	# ��¼ÿһ����Ʒ�������۸�
		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			if currItem.getAmount() < argAmount:		# ƭ�ˣ�������ϸ���û��ô��
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			# ��ҳ��۵Ķ���������Ͷ���������չ���
			if currItem.id != chapmanEntity.currentGoodID:
				self.statusMessage( csstatus.NOT_DARK_TRADER_ITEM )
				return

			itemPrice = currItem.getPrice()
			currMoney = darkPriceCarry( itemPrice * chapmanEntity.invBuyPercent ) * argAmount
			moneys += currMoney
			moneyList.append( currMoney )
			items.append( currItem )

		# �����ˡ�����
		if self.testAddMoney( moneys ) > 0:
			# �������Ǯ̫����
			ERROR_MSG( "%s(%i): �ֽ�̫����" % (self.playerName, self.id) )
			self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
			return
		for item, argAmount, money, argUid in zip( items, argAmountList, moneyList, argUidList ):
			# ��ɾ����Ʒ֮ǰ����Ʒ����������Ʒ�б�
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )	# �Ƴ���������Ʒ
			LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
				%( self.databaseID, self.getName(), chapmanEntity.className, chapmanEntity.getName(), item.id, item.name(), item.amount ) )
		# ��Ǯ���
		self.gainMoney( int(moneys), csdefine.CHANGE_MONEY_SELLTONPC )
		self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 1 )	# ���۳ɹ�

	def buyFromDarkTrader( self, chapmanEntity, itemInstance, argIndex, argAmount ):
		"""
		�������Ʒ

		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  itemInstance: Ҫ�����Ʒʵ��
		@type   itemInstance: ITEM
		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: UINT16
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return:              ��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		# ȷ����int���͵�
		moneys = priceCarry(self.calcCastellanPriceRebate( itemInstance.getPrice() * chapmanEntity.invSellPercent ) ) * itemInstance.getAmount()

		# Ǯ����
		if moneys > self.money:
			ERROR_MSG( "%s(%i): no enough money." % (self.playerName, self.id) )
			return
		# �̻���᲻��
		if not self.checkItemFromNKCK_( JuanZhou, argAmount ):
			self.statusMessage( csstatus.NOT_ENOUGH_DARK_TRADER_JUANZHOU )
			return

		if not self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_BUYFROMDARKTRADER ):
			self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
			return

		# ��Ҹ�Ǯ
		self.payMoney( moneys, csdefine.CHANGE_MONEY_BUY_FROM_DARKTRADER )
		# ��������̻����
		self.removeItemTotal( JuanZhou, argAmount, csdefine.DELETE_ITEM_BUYFROMDARKTRADER )
		chapmanEntity.sellToCB( argIndex, argAmount, self.id )
		try:
			g_logger.tradeNpcBuyLog( self.databaseID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), self.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		except:
			g_logger.logExceptLog( GET_ERROR_MSG() )

	def buyArrayFromDarkTrader( self, chapmanEntity, itemArray, argIndices, argAmountList ):
		"""
		�������Ʒ

		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  itemArray: Ҫ�����Ʒʵ������
		@type   itemArray: ARRAY OF ITEM
		@param argIndices: Ҫ����ĸ���Ʒ
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: Ҫ�������
		@type  argAmountList: ARRAY OF UINT16
		@return:              ��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		moneys = 0
		juanzhouAmount = 0
		for itemInstance in itemArray:
			# ȷ����int���͵�
			moneys += priceCarry( self.calcCastellanPriceRebate( itemInstance.getPrice() * chapmanEntity.invSellPercent ) ) * itemInstance.getAmount()
			juanzhouAmount += itemInstance.getAmount()

		if moneys > self.money:
			ERROR_MSG( "%s(%i): no enough money." % (self.playerName, self.id) )
			return

		if not self.haveEnoughCredit( itemArray[0] ): #ʹ��itemArray[0]����ΪLIST�ж�����ͬ����Ʒ,LISTһ������Ϊ��
			ERROR_MSG( "%s(%i): no enough credit." % (self.playerName, self.id) )
			return

		# �̻���᲻��
		if not self.checkItemFromNKCK_( JuanZhou, juanzhouAmount ):
			self.statusMessage( csstatus.NOT_ENOUGH_DARK_TRADER_JUANZHOU )
			return

		kitbagState = self.checkItemsPlaceIntoNK_( itemArray )

		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			return

		for itemInstance in itemArray:
			if not self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_BUYFROMDARKTRADER ):
				ERROR_MSG( "%s(%i): ���ش���'%s' ���ܷ��뱳���У�������ʵ�ʲ�����ͬ�����" % (self.playerName, self.id, itemInstance.id) )
				moneys -= priceCarry(itemInstance.getPrice() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
			try:
				g_logger.tradeNpcBuyLog( self.databaseID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), self.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		
		# ��Ҹ�Ǯ
		self.payMoney( moneys, csdefine.CHANGE_MONEY_BUY_FROM_DARKTRADER )
		# ������Ҿ���
		self.removeItemTotal( JuanZhou, juanzhouAmount, csdefine.DELETE_ITEM_BUYFROMDARKTRADER )
		# ������һ�������ܹ���ɹ�ʧ�ܣ��������ɹ�
		for argIndex, argAmount in zip( argIndices, argAmountList ):
			chapmanEntity.sellToCB( argIndex, argAmount, self.id )

	#--------------------------------�����̨-----------------------------------------
	def tongAbaBuyFromNPC( self, chapmanEntity, itemInstance, argIndex, argAmount ):
		"""
		���������̨��Ʒ

		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  itemInstance: Ҫ�����Ʒʵ��
		@type   itemInstance: ITEM
		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: UINT16
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return:              ��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_TONG_ABA:
			return False

		# ȷ����int���͵�
		mark = priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
		self.setTemp( "onTongAbabuyData", ( chapmanEntity, itemInstance, argIndex, argAmount ) )
		spaceBase = self.getCurrentSpaceBase()
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity and spaceEntity.isReal():
			spaceEntity.getScript().onNPCDealItemChangeAbaMark( spaceEntity, self, self.databaseID, mark, 0 )
		else:
			spaceBase.cell.remoteScriptCall( "onNPCDealItemChangeAbaMark", ( self, self.databaseID, mark, 0, ) )

	def onTongAbaBuyFromNPCCallBack( self, state ):
		"""
		��������̨��Ʒ�Ļص�
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_TONG_ABA:
			return False

		if state == 1:
			chapmanEntity, itemInstance, argIndex, argAmount = self.popTemp( "onTongAbabuyData" )
			if not self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_TONGABABUYFROMNPC ):
				self.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )
				return
						
			mark = priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
			chapmanEntity.sellToCB( argIndex, argAmount, self.id )
			tong = self.tong_getTongEntity( self.tong_dbID )
			tong.onWarBuyItemsMessage( self.databaseID, argAmount, itemInstance.name(), mark )
			#д��־
			try:
				g_logger.tradeNpcBuyLog( self.databaseID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), self.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
			except:
				g_logger.logExceptLog( GET_ERROR_MSG() )
		else:
			self.statusMessage( csstatus.TONG_WAR_BUY_INVALID )

	def tongAbaBuyArrayFromNPC( self, chapmanEntity, itemArray, argIndices, argAmountList ):
		"""
		���������̨��Ʒ
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_TONG_ABA:
			return False

		mark = 0
		for itemInstance in itemArray:
			# ȷ����int���͵�
			mark += priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()

		self.setTemp( "onTongAbabuyData", ( chapmanEntity, itemArray, argIndices, argAmountList ) )
		spaceBase = self.getCurrentSpaceBase()
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity and spaceEntity.isReal():
			spaceEntity.getScript().onNPCDealItemChangeAbaMark( spaceEntity, self, self.databaseID, mark, 1 )
		else:
			spaceBase.cell.remoteScriptCall( "onNPCDealItemChangeAbaMark", ( self, self.databaseID, mark, 1, ) )

	def onTongAbaBuyArrayFromNPCCallBack( self, state ):
		"""
		������ս����Ʒ�Ļص�
		"""
		spaceType = self.getCurrentSpaceType()
		if spaceType != csdefine.SPACE_TYPE_TONG_ABA:
			return False

		if state == 1:
			mark = 0
			tong= self.tong_getTongEntity( self.tong_dbID )
			chapmanEntity, itemArray, argIndices, argAmountList = self.popTemp( "onTongAbabuyData" )

			for itemInstance in itemArray:
				# ȷ����int���͵�
				mark += priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
			kitbagState = self.checkItemsPlaceIntoNK_( itemArray )

			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
				return
			if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
				self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
				return

			for itemInstance in itemArray:
				if not self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_TONGABABUYFROMNPC ):
					ERROR_MSG( "%s(%i): ���ش���'%s' ���ܷ��뱳���У�������ʵ�ʲ�����ͬ�����" % (self.playerName, self.id, itemInstance.id) )
					mark -= priceCarry(itemInstance.getWarIntegral() * chapmanEntity.invSellPercent) * itemInstance.getAmount()
				else:
					# tong.onWarBuyItemsMessage( self.databaseID, itemInstance.amount, itemInstance.name(), mark )
					pass
				LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
					%( self.databaseID, self.getName(), chapmanEntity.className, chapmanEntity.getName(), itemInstance.id, itemInstance.name(), itemInstance.amount ) )
				try:
					g_logger.tradeNpcBuyLog( self.databaseID, self.getName(), itemInstance.uid, itemInstance.name(), itemInstance.getAmount(), self.grade, chapmanEntity.className, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
				except:
					g_logger.logExceptLog( GET_ERROR_MSG() )
				
			# ������һ�������ܹ���ɹ�ʧ�ܣ��������ɹ�
			for argIndex, argAmount in zip( argIndices, argAmountList ):
				chapmanEntity.sellToCB( argIndex, argAmount, self.id )
			tong = self.tong_getTongEntity( self.tong_dbID )
			tong.onWarBuyItemsMessage( self.databaseID, argAmount, itemInstance.name(), mark )
		else:
			self.statusMessage( csstatus.TONG_WAR_BUY_INVALID )

	def sellTongAbaItemArrayToNPC( self, chapmanEntity, argUidList, argAmountList ):
		"""
		�������Ʒ

		@param  chapmanEntity: ����NPC entity or mailbox
		@type   chapmanEntity: MAILBOX
		@param  argUidList: Ҫ����ĸ���Ʒ
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: Ҫ�������
		@type   argAmountList: ARRAY OF UINT16
		@return:               ��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		# �������Ҫ������Ʒ�Ĵ�������Լ����ܳ��ۺ���
		moneys = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# ��¼ÿһ����Ʒ
		moneyList = []	# ��¼ÿһ����Ʒ�������۸�

		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			if not currItem.canSell():	# �������Ĳ����Գ���
				ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			# �ж���Ʒ�Ƿ񱻶��ᡣû��������жϵĻ������Ը�����Ʒʹ��Ч�������������ǣ���Ʒ�ɱ����۸�npc���ˣ���Ʒ����������ʱ�䡣
			# ���Ʒ��������ﵰΪ����ʹ����Ʒ����ʱ����Ʒ���۸�npc��ʹ�óɹ���ó����ʱ�������Ʒ������Ʒ�ֿɱ�ʹ�á�
			# 15:06 2009-10-20��wsf
			if currItem.isFrozen():
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			if currItem.getAmount() < argAmount:		# ƭ�ˣ�������ϸ���û��ô��
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			currMoney = priceCarry( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount
			moneys += currMoney
			moneyList.append( currMoney )
			items.append( currItem )

		# �����ˡ�����
		if self.testAddMoney( moneys ) > 0:
			# �������Ǯ̫����
			ERROR_MSG( "%s(%i): �ֽ�̫����" % (self.playerName, self.id) )
			self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
			return

		for item, argAmount, money, argUid in zip( items, argAmountList, moneyList, argUidList ):
			# ��ɾ����Ʒ֮ǰ����Ʒ����������Ʒ�б�
			if item.amount == argAmount:
				# �����������Ʒ����ȥ
				tempItem = item
			else:
				# ����������Ʒ����ȥ��������Ҫ��new()����һ���µ���Ʒ����
				# �������Ա�֤��ص�ʱ����ƷUID��һ��
				# ��֤��������ͬuid����Ʒ���뵽�����У��Ӷ�����һЩ��ֵĴ���
				tempItem = item.new()
				tempItem.setAmount( argAmount )
			tempItem.setPrice( money )		# ������Ʒ�ļ۸�
			self._addRedeemItem( tempItem )
			#item.setAmount( item.getAmount() - argAmount, self )
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

			LOG_MSG( "databaseID(%i), playerName(%s), NPCClass(%s), NPCName(%s), itemID(%s), itemName(%s), itemAmount(%i)"\
				%( self.databaseID, self.getName(), chapmanEntity.className, chapmanEntity.getName(), tempItem.id, tempItem.name(), tempItem.amount ) )

		# ��Ǯ���
		self.gainMoney( int(moneys), csdefine.CHANGE_MONEY_SELLTONPC )
		self.clientEntity(chapmanEntity.id).onBuyArrayFromCB( 1 )	# ���۳ɹ�

	def sellTongAbaItemToNPC( self, chapmanEntity, argUid, argAmount ):
		"""
		�������Ʒ
		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param   argUid: Ҫ����ĸ���Ʒ
		@type    argUid: INT64
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return: 			��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
		# ȡ����Ҫ������Ʒ
		currItem = self.getItemByUid_( argUid )
		if currItem is None:
			ERROR_MSG( "%s(%i): I no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
			return
		# �������Ĳ����Գ���
		if not currItem.canSell():
			ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
			return
		# �ж���Ʒ�Ƿ񱻶��ᡣû��������жϵĻ������Ը�����Ʒʹ��Ч�������������ǣ���Ʒ�ɱ����۸�npc���ˣ���Ʒ����������ʱ�䡣
		# ���Ʒ��������ﵰΪ����ʹ����Ʒ����ʱ����Ʒ���۸�npc��ʹ�óɹ���ó����ʱ�������Ʒ������Ʒ�ֿɱ�ʹ�á�
		# 15:06 2009-10-20��wsf
		if currItem.isFrozen():
			self.statusMessage( csstatus.NPC_TRADE_ITEM_NOT_SELL )
			return
		# ƭ�ˣ�������ϸ���û��ô��
		if currItem.getAmount() < argAmount:
			ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
			return
		buyMoney = priceCarry( currItem.getPrice() * chapmanEntity.invBuyPercent ) * argAmount

		# �����ˡ�����
		if self.testAddMoney( buyMoney ) > 0:
			# �������Ǯ̫����
			ERROR_MSG( "%s(%i): �ֽ�̫����" % (self.playerName) )
			return

		# ��ɾ����Ʒ֮ǰ����Ʒ����������Ʒ�б�
		if currItem.amount == argAmount:
			# �����������Ʒ����ȥ
			tempItem = currItem
		else:
			# ����������Ʒ����ȥ��������Ҫ��new()����һ���µ���Ʒ����
			# �������Ա�֤��ص�ʱ����ƷUID��һ��
			# ��֤��������ͬuid����Ʒ���뵽�����У��Ӷ�����һЩ��ֵĴ���
			tempItem = currItem.new()
			tempItem.setAmount( argAmount )
		tempItem.setPrice( buyMoney )		# ������Ʒ�ļ۸�

		self._addRedeemItem( tempItem )

		# �������������Ʒ������
		#currItem.setAmount( currItem.getAmount() - argAmount, self )
		self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )
		
		# ��Ǯ���
		self.gainMoney( int(buyMoney), csdefine.CHANGE_MONEY_SELLTONPC )


	
	# ----------------------------------------------------------------
	# Ӣ�����˰�ʧ�䱦�ظ���NPCװ�����׹���
	# ----------------------------------------------------------------
	def buyYXLMEquipFromNPC( self, chapmanEntity, newInvoice, argIndex, argAmount ):
		"""
		��ҹ���Ӣ�����˸�����װ��
		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param  newInvoice: Ҫ�����Ʒ
		@type   newInvoice: INVOICEITEM
		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: UINT16
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return:              ��
		"""
		chapmanEntity = BigWorld.entities.get( chapmanEntity.id )
		if chapmanEntity is None or chapmanEntity.isDestroyed :
			ERROR_MSG("Chapman(ID %i) is lose." % chapmanEntity.id)
			return
		status = newInvoice.checkRequire( self, chapmanEntity, argAmount )
		if status != csstatus.NPC_TRADE_CAN_BUY:
			self.statusMessage( status )
			return
		newInvoice.doTrade(  self, chapmanEntity, argAmount )
		chapmanEntity.sellToCB( argIndex, argAmount, self.id )

	def sellYXLMEquipToNPC( self, chapmanEntity, argUid, argAmount ) :
		"""
		��ҳ�����Ӣ�����˸�����װ��
		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@param   argUid: ��Ʒ��ΨһID
		@type    argUid: INT64
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return: 			��
		"""
		equip = self.getYXLMEquipByUid( argUid )
		if equip :
			if equip.getAmount() < argAmount:
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % \
					(self.playerName, self.id, equip.name, equip.getAmount(), argAmount) )
				return
			chapmanEntity = BigWorld.entities[ chapmanEntity.id ]
			income = priceCarry( equip.getPrice() * chapmanEntity.invBuyPercent ) * argAmount
			self.addAccumPoint( income )
			self.removeYXLMEquip( argUid )
			currSpace = self.getCurrentSpaceBase().cell
			if hasattr( currSpace, "onPlayerRemoveEquip" ) :
				currSpace.onPlayerRemoveEquip( self.databaseID, argUid )
		else :
			ERROR_MSG( "Player(name:%s) don't have yxlm equip of uid %i" % ( self.playerName, argUid ) )

	def gainYXLMEquipFromNPC( self, chapmanEntity, equipItem ) :
		"""
		֧�����ҹ���Ӣ�����˸�����װ��
		���ﲻ���ж��Ƿ�Ǯ����Ϊǰ��������Ѿ������ж�
		"""
		if self.addYXLMEquip( equipItem ):
			currSpace = self.getCurrentSpaceBase().cell
			if hasattr( currSpace, "onPlayerAddEquip" ) :
				currSpace.onPlayerAddEquip( self.databaseID, equipItem )
			return True
		return False
	
	def addYXLMEquip( self, equipItem ) :
		"""
		<Define method>
		���һ��Ӣ�����˸�����װ��
		@type	equipItem : ITEM
		@param	equipItem : �̳���CItemBase����Ʒʵ��
		"""
		if self.storeYXLMEquip( equipItem ) :
			if self.putOnYXLMEquip( equipItem ) :
				self.client.onAddYXLMEquip( equipItem )
				return True
			else :
				self.dropYXLMEquip( equipItem.uid )
				return False
		else :
			return False

	def removeYXLMEquip( self, equipUid ) :
		"""
		<Define method>
		@type	equipUid : UID
		@param	equipUid : ��Ʒʵ����UID
		"""
		equipID = self.getYXLMEquipIDByUid( equipUid )
		self.putOffYXLMEquip( equipUid )
		self.dropYXLMEquip( equipUid )
		self.refreshYXLMEquips( equipID )		# ɾ��һ��װ������ͬIDװ����ӵ�buffҲ�ᱻɾ������������ˢ����ͬID��װ��
		self.client.onRemoveYXLMEquip( equipUid )

	def putOnYXLMEquip( self, equipItem ):
		"""
		����Ӣ�����˸�����װ��
		"""
		useResult = equipItem.use( self, self )
		if useResult != csstatus.SKILL_GO_ON and useResult is not None:
			self.statusMessage( useResult )
			return False
		return True

	def putOffYXLMEquip( self, equipUid ):
		"""
		����Ӣ�����˸�����װ��
		"""
		self.removeAllBuffsBySkillID( self.querySpellIDByYXLMEquipUid( equipUid ), [csdefine.BUFF_INTERRUPT_NONE] )

	def storeYXLMEquip( self, equipItem ) :
		"""
		�ղ�Ӣ�����˸�����װ��
		"""
		yxlmEqBag = self.getYXLMEquipBag( True )
		if len( yxlmEqBag ) >= csdefine.YXLM_MAX_EQUIP_AMOUNT :
			self.statusMessage( csstatus.YXLM_EQUIP_BAG_FULL )
			return False
		else :
			yxlmEqBag[equipItem.uid] = equipItem
			return True

	def dropYXLMEquip( self, equipUid ) :
		"""
		����Ӣ�����˸�����װ��
		"""
		yxlmEqBag = self.getYXLMEquipBag()
		if yxlmEqBag and equipUid in yxlmEqBag :
			del yxlmEqBag[equipUid]

	def refreshYXLMEquips( self, equipID ):
		"""
		ˢ������ID��equipID��װ��
		"""
		for equip in self.getYXLMEquipsByID(equipID):
			self.putOnYXLMEquip(equip)

	def getYXLMEquipByUid( self, equipUid ) :
		"""
		����uid��ȡ���ϵ�Ӣ�����˸���װ��
		"""
		yxlmEqBag = self.getYXLMEquipBag()
		if yxlmEqBag and equipUid in yxlmEqBag :
			return yxlmEqBag[equipUid]
		else :
			return None

	def getYXLMEquipsByID( self, equipID ):
		"""
		����uid��ȡ���ϵ�Ӣ�����˸���װ��
		"""
		result = []
		yxlmEqBag = self.getYXLMEquipBag()
		if yxlmEqBag:
			for equip in yxlmEqBag.itervalues():
				if equip.id == equipID:
					result.append( equip )
		return result

	def getYXLMEquipIDByUid( self, equipUid ):
		"""
		����uid��ȡ���ϵ�Ӣ�����˸���װ����ID
		"""
		equip = self.getYXLMEquipByUid( equipUid )
		if equip:
			return equip.id
		else:
			return None

	def querySpellIDByYXLMEquipUid( self, equipUid ) :
		"""
		��ѯӢ������װ����Ӧ�ļ���ID
		"""
		equip = self.getYXLMEquipByUid( equipUid )
		if equip :
			return equip.getSpellID()
		else :
			return 0

	def getYXLMEquipBag( self, createIfNotExist=False ) :
		"""
		��ȡӢ�����˸���װ���İ���
		"""
		yxlmEqBag = self.queryTemp( "YXLM_EQUIPS_BAG" )
		if yxlmEqBag :
			return yxlmEqBag
		elif createIfNotExist :
			yxlmEqBag = {}
			self.setTemp( "YXLM_EQUIPS_BAG", yxlmEqBag )
			return yxlmEqBag
		else :
			return None

	def hasYXLMEquip( self, equipUid ) :
		"""
		�Ƿ�ӵ��ָ��uid��Ӣ������װ��
		"""
		return self.getYXLMEquipByUid(equipUid) is not None




	# ---------------------------------------------��������̳�------------------------------------------
	def buyTongSpecialArrayFromNPC( self, chapman, memberDBID, invoiceIDs, amountList ):
		"""
		������������Ʒ
		@param chapmanEntity: ����NPC entity or mailbox
		@type  chapmanEntity: MAILBOX
		@ param memberDBID: ����Ա��dbid
		@type  memberDBID: BASE_DBID
		@param  itemArray: Ҫ�����Ʒʵ������
		@type   itemArray: ARRAY OF ITEM
		@param argIndices: Ҫ����ĸ���Ʒ
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: Ҫ�������
		@type  argAmountList: ARRAY OF UINT16
		@return:              ��
		"""
		chapman = BigWorld.entities.get( chapman.id, None )
		if chapman is None:
			return
		zipInvoiceArray = zip( invoiceIDs, amountList )
		for invoiceID, amount in zipInvoiceArray:
			chapman.sellToCB( memberDBID, invoiceID, amount, self.id )
