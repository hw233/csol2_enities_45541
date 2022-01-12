# -*- coding: gb18030 -*-

"""
����ȫ��ʵ��������
"""

import Language
import cschannel_msgs
import ShareTexts as ST
import items
import InvoiceDataType
from bwdebug import *
import Chapman
from Resource.GoodsLoader import GoodsLoader

g_goods = GoodsLoader.instance()
g_items = items.instance()

class TongAbaChapman( Chapman.Chapman ):
	"""
	����ȫ��ʵ�������� for cell��

	@ivar      attrInvoices: �����б�
	@type      attrInvoices: dict
	"""

	def __init__( self ):
		"""
		"""
		Chapman.Chapman.__init__( self )

	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		����ĳ��Ʒ�¼�
		"""
		itemData = newInvoice.getSrcItem()
		playerEntity.tongAbaBuyFromNPC( selfEntity, itemData, argIndex, argAmount )

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
		playerEntity.tongAbaBuyArrayFromNPC( selfEntity, items, argIndices, argAmountList )

	def buyFrom( self, selfEntity, playerEntity, argUid, argAmount ):
		"""
		���˴���������չ�����

		@param 	 selfEntity	  : NPC����ʵ��
		@param   playerEntity : ���
		@param   argUid: Ҫ�����ĸ���Ʒ
		@type    argUid: INT64
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return: 			��
		"""
		playerEntity.sellTongAbaItemToNPC( selfEntity, argUid, argAmount )

	def buyArrayFrom( self, selfEntity, playerEntity, argUidList, argAmountList ):
		"""
		���˴���������չ�����������
		�����б����ÿһ��Ԫ�ض�Ӧһ����Ʒ���ڱ�������ʶ��������
		�չ�����������Ʒ�������ҿ������Լ������ܼ�ֵ��������Ͻ�Ǯ�ܺͲ��ᳬ���������Я���Ľ�Ǯ����ʱ��������ۣ�����������ۡ�

		@param 	 selfEntity	  : NPC����ʵ��
		@param   playerEntity : ���
		@param  argUidList: Ҫ����ĸ���Ʒ
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: Ҫ�������
		@type   argAmountList: ARRAY OF UINT16
		@return:               ��
		"""
		playerEntity.sellTongAbaItemArrayToNPC( selfEntity, argUidList, argAmountList )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ˵�������
		@type  playerEntity: Entity
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: str
		@return: ��
		"""
		if dlgKey == "Talk":
			if selfEntity.isReal():
				self.checkPlayerIsRight( selfEntity, playerEntity, playerEntity.queryTemp( "aba_right", False )  )
			else:
				selfEntity.remoteScriptCall( "checkPlayerIsRight", ( playerEntity.base, playerEntity.queryTemp( "aba_right", False ) ) )
		elif dlgKey == "NO":
			playerEntity.setGossipText(cschannel_msgs.NIU_MO_WANG_VOICE_9)
			playerEntity.sendGossipComplete( selfEntity.id )
		elif dlgKey == "OK":
			Chapman.Chapman.gossipWith( self, selfEntity, playerEntity, "Talk" )
		else:
			Chapman.Chapman.gossipWith( self, selfEntity, playerEntity, dlgKey )

	def checkPlayerIsRight( self, selfEntity, playerEntity, isRight ):
		"""
		�������Ƿ��Ƿ��ط� Ȼ������Ӧ�Ĳ���
		"""
		if selfEntity.queryTemp( "isRight", False ) == isRight:
			selfEntity.gossipWith( playerEntity.id, "OK" )
		else:
			selfEntity.gossipWith( playerEntity.id, "NO" )
#