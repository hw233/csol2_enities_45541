# -*- coding: gb18030 -*-

"""
This module implements the invoice data type.

@var instance: InvoiceDataType���͵�ʵ������ҪΪ����res\entities\defs\alias.xml��ʵ���Զ����������͡���INVOICEITEM
@requires: L{CItemProp<CItemProp>}, L{ItemDataList<ItemDataList>}
"""


from bwdebug import *
import NPCTradePrice
import ItemTypeEnum
import csstatus
import csdefine
import csconst

class InvoiceDataType:
	"""
	ʵ��res\entities\defs\alias.xml�е��Զ�����������INVOICEITEM��
	���а���Database��Stream��XML Data�ӿ��Լ���װ����ʵ��

	@ivar	maxAmount: �õ�������������
	@type	maxAmount: UINT16
	@ivar  currAmount: �õ��ߵ�ǰӵ�е�����
	@type  currAmount: UINT16
	@ivar     srcItem: �̳���CItemBase�ĵ���ʵ��
	@type     srcItem: class instance
	"""
	def __init__( self ):
		# ��������
		self.invoiceType = csdefine.INVOICE_CLASS_TYPE_NORMAL					# ��Ʒ����
		self.maxAmount = 0					# �������(UINT16)
		self.currAmount = 0					# ��ǰ����(UINT16)
		self.itemType = 0					# ��ʹ���߷ֵ���Ʒ���ͣ�hyw--08.08.11��
		self.srcItem = None					# �̳���CItemBase�ĵ���ʵ��
		self.priceInstanceList = []			# ���׼۸�ʵ��
		
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
		�����Լ�
		
		@return: InvoiceDataTypeʵ��
		@rtype:  instance of InvoiceDataType
		"""
		obj = createInvoiceInstace( self.invoiceType )
		obj.__dict__.update( self.__dict__ )		# ��������
		obj.srcItem = self.srcItem.new()			# ����Դʵ��
		obj.priceInstanceList = [priceInstance.copy() for priceInstance in self.priceInstanceList]
		return obj
		
	def setAmount( self, argAmount ):
		"""
		���õ�ǰ��Ʒ������

		@param argAmount: ��ǰ������
		@type argAmount: int
		@return: ��
		"""
		if self.maxAmount < argAmount:
			self.currAmount = self.maxAmount
		else:
			self.currAmount = argAmount
			
	def getAmount( self ):
		"""
		�����Ʒ�ĵ�ǰ����
		
		@return: ��Ʒ�ĵ�ǰ����
		@rtype: int
		"""
		return self.currAmount
		
	def addAmount( self, argAmount ):
		"""
		����ǰ��Ʒ����һ��������

		@param argAmount: Ҫ���ӵ�����
		@type argAmount: int
		@return: ��
		"""
		self.currAmount += argAmount
		if self.currAmount > self.maxAmount:
			self.currAmount = self.maxAmount
		elif self.currAmount < 0:
			self.currAmount = 0

	def getMaxAmount( self ):
		"""
		��ȡ������������

		@return: INT32
		@rtype:  INT32
		"""
		return self.maxAmount

	def setMaxAmount( self, argAmount ):
		"""
		����ǰ��Ʒ����������ڵ��������

		@param argAmount: �������
		@type argAmount: int
		@return: ��
		"""
		self.maxAmount = argAmount

	def getItemType( self ) :
		"""
		��ȡ��Ʒ���( hyw -- 08.08.09 )
		"""
		return self.itemType

	def setItemType( self, itype ) :
		"""
		������Ʒ���( hyw -- 08.08.09 )
		"""
		self.itemType = itype
		
	def initPrice( self, priceData ):
		"""
		��ʼ���۸�
		"""
		for childPrice in priceData:
			self.priceInstanceList.append( NPCTradePrice.createPriceInstance( childPrice ) )
			
	def setSrcItem( self, itemInstance ):
		"""
		���������ĵ���ʵ����
		ע�⣺�������������Ƶ���ʵ��������ֱ�����á�
		�������ͨ�����ڳ�ʼ����ʱ��ʹ�ã����Ѿ�������һ������ʵ���Ժ�Ͳ�Ӧ���ٸı����ˡ�

		@param itemInstance: �̳���CItemBase�ĵ���ʵ��
		@type  itemInstance: class instance
		@return:             ��
		"""
		self.srcItem = itemInstance

	def getSrcItem( self ):
		"""
		ȡ��Դʼ����ʵ��

		@return: Դʼ�ļ̳���CItemBase�ĵ���ʵ��
		@rtype:  class instance
		"""
		return self.srcItem
		
	def checkRequire( self, player, chapmanEntity, invoiceAmount ):
		"""
		�������Ƿ������������
		"""
		creditDic = self.srcItem.credit()		# ����������
		for key in creditDic:
			value = player.getPrestige( key )
			if value is None or value < creditDic[key]:
				return csstatus.NPC_TRADE_NOT_ENOUGH_CREDIT
		for priceInstance in self.priceInstanceList:
			status = priceInstance.checkRequire( player, chapmanEntity, invoiceAmount )
			if status != csstatus.NPC_TRADE_CAN_BUY:
				return status
		return csstatus.NPC_TRADE_CAN_BUY
		
	def checkRequireArrayInvoice( self, player, chapmanEntity, invoiceAmount ):
		"""
		�����������Ƿ���������Ʒ������
		"""
		creditDic = self.srcItem.credit()		# ����������
		for key in creditDic:
			value = player.getPrestige( key )
			if value is None or value < creditDic[key]:
				return csstatus.NPC_TRADE_NOT_ENOUGH_CREDIT
				
		for priceInstance in self.priceInstanceList:
			status = priceInstance.checkPlayerArrayInvoice( player, chapmanEntity, invoiceAmount )
			if status != csstatus.NPC_TRADE_CAN_BUY:
				return status
		return csstatus.NPC_TRADE_CAN_BUY
		
	def doTrade( self, player, chapmanEntity, amount ):
		"""
		���е��������ͨ�����������Ʒ
		"""
		self.srcItem.setAmount( amount )
		for priceInstance in self.priceInstanceList:
			priceInstance.playerPay( self.srcItem, player, chapmanEntity )
			
	def getPrice( self, chapman, amount = 1 ):
		"""
		�����Ӧ������Ʒ�ļ۸�
		"""
		pass
		
		
class InvoiceBindItem( InvoiceDataType ):
	"""
	���ۺ󱻰󶨵���Ʒ
	"""
	def __init__( self ):
		"""
		"""
		InvoiceDataType.__init__( self )
		self.invoiceType = csdefine.INVOICE_CLASS_TYPE_BIND
		
	def doTrade( self, player, chapmanEntity, amount ):
		"""
		"""
		self.srcItem.setBindType( ItemTypeEnum.CBT_PICKUP )
		InvoiceDataType.doTrade( self, player, chapmanEntity, amount )

# ����InvoiceDataTypeʵ����res\entities\defs\alias.xml��ʹ��
instance = InvoiceDataType()


def createInvoiceInstace( invoiceType ):
	"""
	������Ʒʵ��
	"""
	if invoiceType == csdefine.INVOICE_CLASS_TYPE_NORMAL:
		invoice = InvoiceDataType()
	elif invoiceType == csdefine.INVOICE_CLASS_TYPE_BIND:
		invoice = InvoiceBindItem()
	else:
		invoice = InvoiceDataType()
	return invoice


