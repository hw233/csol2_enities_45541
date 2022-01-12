# -*- coding: gb18030 -*-
#


"""
"""

import BigWorld
import csdefine
import csconst
import csstatus
from bwdebug import *
import ItemTypeEnum
import items


g_item = items.instance()

YINPIAO = 50101024													#��Ʊ
DARK_MERCHANT_RATE = 0.25											#�������˻�����Ʒ�۸����

class RoleTradeWithMerchant:
	"""
	�����˽���
	"""
	def __init__( self ):
		pass

	def sellItemToMerchant( self, merchantEntity, argUidList, argAmountList ):
		"""
		define method
		�������Ʒ
		"""
		yinpiao = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# ��¼ÿһ����Ʒ
		yinpiaoList = []	# ��¼ÿһ����Ʒ��������Ʊ�۸�

		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			#if not currItem.canSell():	# �������Ĳ����Գ���
			#	ERROR_MSG( "%s(%i): item(name = %s) can't sell." % (self.playerName, self.id, currItem.name) )
			#	self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
			#	return
			if currItem.isFrozen():
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			if not str(currItem.id) in merchantEntity.getScript().yinpiaoSection.keys():
				# "���˲��չ������Ʒ��"
				self.statusMessage( csstatus.MERCHANT_NO_BUY_THIS_ITEM )
				return
			if self.findItemsByIDFromNKCK( YINPIAO ) == [] :
				#����״̬�ж�
				self.statusMessage( csstatus.ROLE_NOT_IN_RUN_MERCHANT )
				return
			if not self.isInMerchantQuest():
				#����״̬�ж�
				self.statusMessage( csstatus.ROLE_NOT_IN_RUN_MERCHANT )
				return
			if currItem.getAmount() < argAmount:		# ƭ�ˣ�������ϸ���û��ô��
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			#moneys += int( currItem.getPrice() * merchantEntity.invBuyPercent ) * argAmount
			#currMoney = priceCarry( currItem.getPrice() * merchantEntity.invBuyPercent ) * argAmount

			spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			areaYinpiao = merchantEntity.getScript().yinpiaoSection[str(currItem.id)].readInt( spaceLabel )
			sellYinpiao = merchantEntity.getScript().yinpiaoSection[str(currItem.id)].readInt( 'sell' )

			changeValue = False
			#�ж��Ƿ��Ǹ߼۵�������
			if BigWorld.globalData['MerchantHighArea'] == spaceLabel:
				if BigWorld.globalData['MerchantHighItem'] == currItem.id:
					yinpiao += ( areaYinpiao - sellYinpiao ) * BigWorld.globalData['MerchantHighPercent'] + areaYinpiao * argAmount
					changeValue = True


			#�ж��Ƿ��ǵͼ۵�������
			if BigWorld.globalData['MerchantLowArea'] == spaceLabel:
				if BigWorld.globalData['MerchantLowItem'] == currItem.id:
					yinpiao += ( ( areaYinpiao - sellYinpiao ) * BigWorld.globalData['MerchantLowPercent'] + areaYinpiao ) * argAmount
					changeValue = True

			if not changeValue:
				yinpiao += areaYinpiao * argAmount

			yinpiaoList.append( yinpiao )
			items.append( currItem )

		for argAmount, argUid in zip( argAmountList, argUidList ):
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

		# ��Ǯ���
		self.gainYinpiao( int(yinpiao) )
		self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 1 )	# ���۳ɹ�


	def buyItemFromMerchant( self, merchantEntity, itemArray, argIndices, argAmountList ):
		"""
		�������Ʒ

		@param merchantEntity: ����NPC entity or mailbox
		@type  merchantEntity: MAILBOX
		@param  itemArray: Ҫ�����Ʒʵ������
		@type   itemArray: ARRAY OF ITEM
		@param argIndices: Ҫ����ĸ���Ʒ
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: Ҫ�������
		@type  argAmountList: ARRAY OF UINT16
		@param	playerEntityID:	����ӵı���������֪ͨ�ͻ�����Ʒ�����ı�
		@type	playerEntityID:	OBJECT_ID
		@return:              ��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		merchantEntity = BigWorld.entities[ merchantEntity.id ]
		yinpiao = 0
		for itemInstance in itemArray:
			# ȷ����int���͵�
			yinpiao += itemInstance.reqYinpiao() * itemInstance.amount

		if yinpiao > self.getAllYinpiaoValue():
			ERROR_MSG( "%s(%i): no enough yinpiao." % (self.playerName, self.id) )
			self.statusMessage( csstatus.NPC_TRADE_NOT_ENOUGH_YINPIAO )
			return
		if not self.isInMerchantQuest():		#����״̬�ж�
			self.statusMessage( csstatus.ROLE_NOT_IN_RUN_MERCHANT )
			return

		kitbagState = self.checkItemsPlaceIntoNK_( itemArray )

		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			return

		for itemInstance in itemArray:
			self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_BUYITEMFROMMERCHANT )

		# ��Ҹ�Ǯ
		self.payYinpiao( yinpiao )

		# ������һ�������ܹ���ɹ�ʧ�ܣ��������ɹ�
		for argIndex, argAmount in zip( argIndices, argAmountList ):
			merchantEntity.sellToCB( argIndex, argAmount, self.id )


	def getAllYinpiaoValue( self ):
		"""
		��ȡ����������Ʊ����ֵ
		"""
		itemList = self.findItemsByIDFromNKCK( YINPIAO )			# ��ƱID
		if len( itemList ) <= 0 :
			return -1									# ����û����Ʊʱ���� -1
		yinpiao = 0
		for i in itemList:
			yinpiao += i.yinpiao()
		return yinpiao

	def payYinpiao( self, amount ):
		"""
		������Ʊ
		"""
		itemList = self.findItemsByIDFromNKCK( YINPIAO )			#��ƱID
		for i in itemList:
			if amount > i.yinpiao():
				amount -= i.yinpiao()
				self.removeItemByUid_( i.uid, 1, csdefine.DELETE_ITEM_PAYYINPIAO )
			else:
				i.set( 'yinpiao', i.yinpiao() - amount, self )
				self.questYinpiaoValueChange( i )
		self.statusMessage( csstatus.MERCHANT_YINPIAO_SUB, amount, self.getAllYinpiaoValue() )

	def gainYinpiao( self, amount ):
		"""
		�����Ʊ
		"""
		itemList = self.findItemsByIDFromNKCK( YINPIAO )
		itemList[0].set( 'yinpiao', ( itemList[0].yinpiao() + amount ), self )
		self.statusMessage( csstatus.MERCHANT_YINPIAO_ADD, amount, self.getAllYinpiaoValue() )
		self.questYinpiaoValueChange( itemList[0] )

	def sellItemToDarkMerchant( self, merchantEntity, argUidList, argAmountList ):
		"""
		�������Ʒ����������
		"""
		yinpiao = 0
		invoiceList = zip( argUidList, argAmountList )
		items = []		# ��¼ÿһ����Ʒ
		moneyList = []	# ��¼ÿһ����Ʒ��������Ʊ�۸�

		#if self.findItemsByIDFromNKCK( YINPIAO ) == [] :
		#	return


		for argUid, argAmount in invoiceList:
			currItem = self.getItemByUid_( argUid )
			if currItem is None:
				ERROR_MSG( "%s(%i): no such item(argUid = %i)" % (self.playerName, self.id, argUid) )
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			if currItem.getAmount() < argAmount:		# ƭ�ˣ�������ϸ���û��ô��
				ERROR_MSG( "%s(%i): not more item(name = %s), current amount = %i, sell amount = %i." % (self.playerName, self.id, currItem.name, currItem.getAmount(), argAmount) )
				self.clientEntity(merchantEntity.id).onBuyArrayFromCB( 0 )	# ����ʧ��
				return
			#moneys += int( currItem.getPrice() * merchantEntity.invBuyPercent ) * argAmount
			#currMoney = priceCarry( currItem.getPrice() * merchantEntity.invBuyPercent ) * argAmount
			#spaceLabel = BigWorld.getSpaceDataFirstForKey( self.spaceID, csconst.SPACE_SPACEDATA_KEY )
			#areaYinpiao = merchantEntity.getScript().yinpiaoSection[str(currItem.id)].readInt( spaceLabel )
			sellYinpiao = 0
			try:
				sellYinpiao = merchantEntity.getScript().yinpiaoSection[str(currItem.id)].readInt( 'DarkMerchant' )
			except AttributeError, err:
				self.statusMessage( csstatus.NOT_RUN_MERCHANT_ITEM )
				ERROR_MSG( err )
				return
			if sellYinpiao == 0:
				ERROR_MSG( "Please check whether the config of item %s is wrong!" % currItem.name )
				return
			#changeValue = False
			##�ж��Ƿ��Ǹ߼۵�������
			#if BigWorld.globalData['MerchantHighArea'] == spaceLabel:
			#	if BigWorld.globalData['MerchantHighItem'] == currItem.id:
			#		yinpiao += ( areaYinpiao - sellYinpiao ) * BigWorld.globalData['MerchantHighPercent'] + sellYinpiao * argAmount
			#		changeValue = True


			##�ж��Ƿ��ǵͼ۵�������
			#if BigWorld.globalData['MerchantLowArea'] == spaceLabel:
			#	if BigWorld.globalData['MerchantLowItem'] == currItem.id:
			#		yinpiao += ( ( areaYinpiao - sellYinpiao ) * BigWorld.globalData['MerchantLowPercent'] + sellYinpiao ) * argAmount
			#		changeValue = True

			#if not changeValue:
			#	yinpiao += sellYinpiao * argAmount

			yinpiao += sellYinpiao * DARK_MERCHANT_RATE * argAmount
			items.append( currItem )

		for argAmount, argUid in zip( argAmountList, argUidList ):
			self.removeItemByUid_( argUid, argAmount, csdefine.DELETE_ITEM_SELLTONPC )

		# ��Ǯ���
		self.gainMoney( int( yinpiao ), csdefine.CHANGE_MONEY_SELLITEMTODARKMERCHANT )
		self.clientEntity( merchantEntity.id ).onBuyArrayFromCB( 1 )	# ���۳ɹ�


	def buyItemFromDarkMerchant( self, merchantEntity, itemArray, argIndices, argAmountList ):
		"""
		�������Ʒ

		@param merchantEntity: ����NPC entity or mailbox
		@type  merchantEntity: MAILBOX
		@param  itemArray: Ҫ�����Ʒʵ������
		@type   itemArray: ARRAY OF ITEM
		@param argIndices: Ҫ����ĸ���Ʒ
		@type  argIndices: ARRAY OF UINT16
		@param argAmountList: Ҫ�������
		@type  argAmountList: ARRAY OF UINT16
		@param	playerEntityID:	����ӵı���������֪ͨ�ͻ�����Ʒ�����ı�	add by gjx 2009-1-12
		@type	playerEntityID:	OBJECT_ID
		@return:              ��
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		merchantEntity = BigWorld.entities[ merchantEntity.id ]
		money = 0
		for itemInstance in itemArray:
			# ȷ����int���͵�
			money += merchantEntity.getScript().yinpiaoSection[str(itemInstance.id)].readInt( 'DarkMerchant' ) * itemInstance.amount

		if money > self.money:
			ERROR_MSG( "%s(%i): no enough money." % (self.playerName, self.id) )
			self.statusMessage( csstatus.NPC_TRADE_NOT_ENOUGH_MONEY )
			return

		kitbagState = self.checkItemsPlaceIntoNK_( itemArray )

		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			self.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		if kitbagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
			self.statusMessage( csstatus.NPC_TRADE_ITEM_LIMIT_COUNT )
			return

		for itemInstance in itemArray:
			self.addItemAndNotify_( itemInstance, csdefine.ADD_ITEM_BUYITEMFROMDARKMERCHANT )

		# ��Ҹ�Ǯ
		self.payMoney( money, csdefine.CHANGE_MONEY_BUYITEMFROMDARKMERCHANT )

		# ������һ�������ܹ���ɹ�ʧ�ܣ��������ɹ�
		for argIndex, argAmount in zip( argIndices, argAmountList ):
			merchantEntity.sellToCB( argIndex, argAmount, self.id )
