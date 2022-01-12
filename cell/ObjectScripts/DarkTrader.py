# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
from Chapman import Chapman
import csdefine

class DarkTrader( Chapman ):
	"""
	"""

	def __init__( self ):
		"""
		"""
		Chapman.__init__( self )

	def buyFrom( self, selfEntity, playerEntity, argUid, argAmount ):
		"""
		Ͷ�����˴���������չ�����

		@param 	 selfEntity	  : Merchant����ʵ��
		@param   playerEntity : ���
		@param   argUid: Ҫ����ĸ���Ʒ
		@type    argUid: INT64
		@param   argAmount: Ҫ�������
		@type    argAmount: INT64
		@return: 			��
		"""
		playerEntity.sellToDarkTrader( selfEntity, argUid, argAmount )

	def buyArrayFrom( self, selfEntity, playerEntity, argUidList, argAmountList ):
		"""
		Ͷ�����˴���������չ�����������
		�����б����ÿһ��Ԫ�ض�Ӧһ����Ʒ���ڱ�������ʶ��������
		�չ�����������Ʒ�������ҿ������Լ������ܼ�ֵ��������Ͻ�Ǯ�ܺͲ��ᳬ���������Я���Ľ�Ǯ����ʱ��������ۣ�����������ۡ�

		@param 	 selfEntity	  : Merchant����ʵ��
		@param   playerEntity : ���
		@param  argUidList: Ҫ����ĸ���Ʒ
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: Ҫ�������
		@type   argAmountList: ARRAY OF INT64
		@return:               ��
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�Merchant�Ի� ��ɲ���
			return
		playerEntity.sellArrayToDarkTrader( selfEntity, argUidList, argAmountList )

	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		����ĳ��Ʒ�¼�
		"""
		itemData = newInvoice.getSrcItem()
		playerEntity.buyFromDarkTrader( selfEntity, itemData, argIndex, argAmount )

	def onSellItems( self, selfEntity, playerEntity, invoiceItems, argIndices, argAmountList ):
		"""
		����ĳ����Ʒ�¼�
		"""
		zipInvoiceArray = zip( invoiceItems, argAmountList )
		items = []
		for invoiceItem, amount in zipInvoiceArray:
			item = invoiceItem.getSrcItem()
			item.setAmount( amount )
			items.append( item )
		playerEntity.buyArrayFromDarkTrader( selfEntity, items, argIndices, argAmountList )