# -*- coding: gb18030 -*-



import Language
import items
import InvoiceDataType
from bwdebug import *
import Chapman
from Resource.GoodsLoader import GoodsLoader
import csstatus
import csdefine
import Language
import sys

g_goods = GoodsLoader.instance()
g_items = items.instance()

class Merchant( Chapman.Chapman ):
	"""
	"""

	def __init__( self ):
		"""
		"""
		Chapman.Chapman.__init__( self )
		self.yinpiaoSection = Language.openConfigSection( "config/ItemYinpiaoValue.xml" )
		self.attrInvoices = {}

	def initEntity( self, selfEntity ):
		"""
		virtual method.
		��ʼ���Լ���entity������
		"""
		Chapman.Chapman.initEntity( self, selfEntity )
		
	def initGoods( self, selfEntity ):
		"""
		��ʼ��ÿ�����˵���Ʒ
		"""
		argIndex = 0
		for itemID, amount, invoiceType, itemType, itemAttrs, priceData in g_goods.get( self.className ):
			item = g_items.createDynamicItem( itemID )
			if item is None:
				ERROR_MSG( "%s: no such item." % itemID )
				continue
			item.set( 'reqYinpiao', self.yinpiaoSection[str(itemID)].readInt( 'sell' ) )
			
			proPrefixID = 0
			for attrString, value in itemAttrs.iteritems():
				if attrString == "proPrefix":
					# �����������Ʒ������ǰ׺����ô��Ҫ������Ʒ��Ʒ�ʡ�ǰ׺������ǰ׺������Ʒ��������ԣ������뱣֤Ʒ�ʺ�ǰ׺�Ѿ�������
					# "proPrefix":[����ǰ׺id, �Ƿ��ȡ��װ����]
					proPrefixID = value[0]
					isSuitEffect = value[1]
					continue
				item.set( attrString, value )
			if item.isEquip():
				item.fixedCreateRandomEffect( item.getQuality(), None, isSuitEffect )
			proPrefixID = 0
				
			argIndex += 1
			tmpInvData = InvoiceDataType.createInvoiceInstace( invoiceType )
			tmpInvData.setSrcItem( item )
			tmpInvData.setMaxAmount( amount )
			tmpInvData.setAmount( amount )
			tmpInvData.setItemType( itemType )						# ������Ʒ���ͣ�08.08.09��
			for priceItem in priceData:		# �����û���ü۸���ô����Ʒ�����еļ۸�
				if priceItem["priceType"] == csdefine.INVOICE_NEED_MONEY and priceItem["price"] <= 0:
					priceItem["price"] = item.getPrice()
			tmpInvData.initPrice( priceData )
			selfEntity.attrInvoices[argIndex] = tmpInvData
			
	def sellArrayTo( self, selfEntity, playerEntity, argIndices, argAmountList ):
		"""
		���˰Ѷ����������

		@param 	 selfEntity	  : Merchant����ʵ��
		@param   playerEntity : ���
		@param   argIndices  : Ҫ����ĸ���Ʒ
		@type    argIndices  : ARRAY <of> UINT16	</of>
		@param   argAmountList: Ҫ�������
		@type    argAmountList: ARRAY <of> UINT16	</of>
		@return: 			��
		"""
		# ȡ����Ҫ�����Ʒ
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�Merchant�Ի� ��ɲ���
			return
		items = []
		indices = []
		amountList = []
		totalAmount = {}

		for argIndex, argAmount in zip(argIndices, argAmountList):
			try:
				objInvoice = selfEntity.attrInvoices[argIndex]
			except:
				ERROR_MSG( "%s(%i): srcEntityId = %i, no such invoice(index = %i)." % (selfEntity.getName(), selfEntity.id, playerEntity.id, argIndex) )
				return
			# ͳ�Ƹ�����Ʒ�Ĺ�������
			if argIndex in totalAmount:
				totalAmount[argIndex] += argAmount
			else:
				totalAmount[argIndex] = argAmount

			srcItem = objInvoice.getSrcItem()
			if srcItem.getStackable() < argAmount:
				# �����Ƿ�ɵ��ӵ���Ʒ������������ڵ������������
				ERROR_MSG( "stackable less then sell amount" )
				return
			INFO_MSG("%s try to buy %d '%s'from'%s', %d remain.it's maxAmount is %d." % ( playerEntity.getName(), totalAmount[argIndex], srcItem.name(), selfEntity.getName(), objInvoice.getAmount(), objInvoice.getMaxAmount() ) )
			if objInvoice.getMaxAmount() > 0:	# ��Ʒ����������
				if objInvoice.getAmount() <= 0:
					playerEntity.client.onStatusMessage( csstatus.ITEM_ALL_SALE, str(( srcItem.name(), )) )
					selfEntity.sellToCB( argIndex, 0, playerEntity.id )	# ��������Ϊ��֪ͨ�ͻ�����Ʒ�ѱ��������
					ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
					return	# û��������
				elif totalAmount[argIndex] > objInvoice.getAmount():
					playerEntity.client.onStatusMessage( csstatus.ITEM_NO_ENOUGH, str(( srcItem.name(), )) )
					ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
					return	# û��ô���������

			itemData = srcItem.new()
			itemData.setAmount( argAmount )
			items.append( itemData )
			indices.append( argIndex )
			amountList.append( argAmount )
		if len( items ) > 0:
			self.onSellItems( selfEntity, playerEntity, items, indices, amountList )

	def onSellItems( self, selfEntity, playerEntity, items, argIndices, argAmountList ):
		"""
		����ĳ����Ʒ�¼�
		"""
		playerEntity.buyItemFromMerchant( selfEntity, items, argIndices, argAmountList )

	def buyFrom( self, selfEntity, playerEntity, argUid, argAmount ):
		"""
		���˴���������չ�����

		@param 	 selfEntity	  : Merchant����ʵ��
		@param   playerEntity : ���
		@param   argUid: Ҫ����ĸ���Ʒ
		@type    argUid: INT64
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return: 			��
		"""
		# ����������һ�������鲻Ӧ����һ���ӿڣ���Ŀǰ�����ģ��������� -pj
		playerEntity.sellItemToMerchant( selfEntity, [argUid], [argAmount] )

	def buyArrayFrom( self, selfEntity, playerEntity, argUidList, argAmountList ):
		"""
		���˴���������չ�����������
		�����б����ÿһ��Ԫ�ض�Ӧһ����Ʒ���ڱ�������ʶ��������
		�չ�����������Ʒ�������ҿ������Լ������ܼ�ֵ��������Ͻ�Ǯ�ܺͲ��ᳬ���������Я���Ľ�Ǯ����ʱ��������ۣ�����������ۡ�

		@param 	 selfEntity	  : Merchant����ʵ��
		@param   playerEntity : ���
		@param  argUidList: Ҫ����ĸ���Ʒ
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: Ҫ�������
		@type   argAmountList: ARRAY OF UINT16
		@return:               ��
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�Merchant�Ի� ��ɲ���
			return
		playerEntity.sellItemToMerchant( selfEntity, argUidList, argAmountList )

# Chapman.py
