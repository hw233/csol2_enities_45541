# -*- coding: gb18030 -*-
"""
Ӣ�����˰�ʧ�䱦�ظ�����װ������NPC
"""

import csdefine
from Chapman import Chapman

class YXLMEquipChapman( Chapman ):
	"""
	����������һ�����������
	�������˳��۵���Ʒ��������Ǯ�򣬶��������ң���ʵ��������ֵ������ȡ��
	"""
	def __init__( self ):
		"""
		"""
		Chapman.__init__( self )

	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		����ĳ��Ʒ�¼�
		"""
		playerEntity.buyYXLMEquipFromNPC( selfEntity, newInvoice, argIndex, argAmount )

	def onSellItems( self, selfEntity, playerEntity, invoiceItems, argIndices, argAmountList ):
		"""
		����ĳ����Ʒ�¼�
		"""
		for invoice, argIndex, argAmount in zip( invoiceItems, argIndices, argAmountList ) :
			playerEntity.buyYXLMEquipFromNPC( selfEntity, invoice, argIndex, argAmount )

	def buyFrom( self, selfEntity, playerEntity, argUid, argAmount ):
		"""
		���˴���������չ�����

		@param 	 selfEntity	  	: NPC����ʵ��
		@param   playerEntity	: ���
		@param   argUid			: Ҫ����ĸ���Ʒ
		@type    argUid			: INT64
		@param   argAmount		: Ҫ�������
		@type    argAmount		: UINT16
		@return					: ��
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			return
		playerEntity.sellYXLMEquipToNPC( selfEntity, argUid, argAmount )

	def buyArrayFrom( self, selfEntity, playerEntity, argUidList, argAmountList ):
		"""
		Exposed method
		���˴���������չ�����������
		�����б����ÿһ��Ԫ�ض�Ӧһ����Ʒ���ڱ�������ʶ��������
		�չ�����������Ʒ�������ҿ������Լ������ܼ�ֵ��������Ͻ�Ǯ�ܺͲ��ᳬ���������Я���Ľ�Ǯ����ʱ��������ۣ�����������ۡ�

		@param 	 selfEntity	  : NPC����ʵ��
		@param   playerEntity : ���
		@param  argUidList: Ҫ����ĸ���Ʒ
		@type   argUidList: ARRAY OF UINT64
		@param  argAmountList: Ҫ�������
		@type   argAmountList: ARRAY OF UINT16
		@return:               ��
		"""
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			return
		for argUid, argAmount in zip( argUidList, argAmountList ):
			playerEntity.sellYXLMEquipToNPC( selfEntity, argUid, argAmount )
