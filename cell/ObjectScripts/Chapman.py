# -*- coding: gb18030 -*-

"""
����ȫ��ʵ��������
"""
# $Id: Chapman.py,v 1.8 2008-08-11 07:24:03 huangyongwei Exp $

import Language
import items
import InvoiceDataType
from bwdebug import *
import NPC
from Resource.GoodsLoader import GoodsLoader
import csstatus
import csdefine
import sys

g_goods = GoodsLoader.instance()
g_items = items.instance()

class Chapman( NPC.NPC ):
	"""
	����ȫ��ʵ�������� for cell��

	@ivar      attrInvoices: �����б�
	@type      attrInvoices: dict
	"""

	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )
		self.attrInvoices = {}

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		NPC.NPC.onLoadEntityProperties_( self, section )

		self.setEntityProperty( "invSellPercent",	section["invSellPercent"].asFloat )		# ���۱���������NPCר��
		self.setEntityProperty( "invBuyPercent",	section["invBuyPercent"].asFloat )		# ���ձ���������NPCר��
		self.setEntityProperty( "invRestoreTime",	section["invRestoreTime"].asFloat )		# ��Ʒ�ָ�ʱ�䣻����NPCר��
		self.setEntityProperty( "isJoinRevenue",	section.readInt("isJoinRevenue") )		# �Ƿ����˰��

	def load( self, section ):
		"""
		��ȡ��Ʒ�б������ļ�����ʼ����Ʒ�������ֵ

		@param section: �����ļ���section
		@type  section: Language.PyDataSection
		@return: 		��
		"""
		NPC.NPC.load( self, section )	# �ȼ��ػ��������

	def initEntity( self, selfEntity ):
		"""
		virtual method.
		��ʼ���Լ���entity������
		"""
		NPC.NPC.initEntity( self, selfEntity )
		self.initGoods( selfEntity )
		
	def initGoods( self, selfEntity ):
		"""
		��ʼ��ÿ�����˵���Ʒ
		"""
		g_goods.initGoods( selfEntity, self.className )

	def sellTo( self, selfEntity, playerEntity, argIndex, argAmount ):
		"""
		���˰Ѷ����������

		@param 	 selfEntity	 : NPC����ʵ��
		@param   playerEntity: ���
		@param   argIndex	 : Ҫ��ڼ�������
		@param   argAmount	 : Ҫ�������
		@return: 			��
		"""
		# ȡ����Ҫ�����Ʒ
		try:
			objInvoice = selfEntity.attrInvoices[argIndex]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such invoice(argIndex = %i)." % (selfEntity.getName(), selfEntity.id, playerEntity.id, argIndex) )
			return

		srcItem = objInvoice.getSrcItem()

		if srcItem.getStackable() < argAmount:
			# �����Ƿ�ɵ��ӵ���Ʒ������������ڵ������������
			ERROR_MSG( "stackable less then sell amount" )
			return

		# ���ڿ�ʼ����Ʒ��
		if objInvoice.getMaxAmount() > 0 and argAmount > objInvoice.getAmount():	# ��Ʒ����������
			playerEntity.client.onStatusMessage( csstatus.GOODS_IS_NONE_1, "" )
			ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
			return	# û��ô���������

		newInvoice = objInvoice.copy()
		#itemData.setAmount( argAmount )
		self.onSellItem( selfEntity, playerEntity, newInvoice, argIndex, argAmount )


	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		����ĳ��Ʒ�¼�
		"""
		playerEntity.buyFromNPC( selfEntity, newInvoice, argIndex, argAmount )

	def sellArrayTo( self, selfEntity, playerEntity, argIndices, argAmountList ):
		"""
		Exposed method
		���˰Ѷ����������

		@param 	 selfEntity	  : NPC����ʵ��
		@param   playerEntity : ���
		@param   argIndices  : Ҫ����ĸ���Ʒ
		@type    argIndices  : ARRAY <of> UINT16	</of>
		@param   argAmountList: Ҫ�������
		@type    argAmountList: ARRAY <of> UINT16	</of>
		@return: 			��
		"""
		# ȡ����Ҫ�����Ʒ
		if playerEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			return
		invoiceItems = []
		indices = []
		amountList = []
		totalAmount = {}

		for argIndex, argAmount in zip(argIndices, argAmountList):
			try:
				objInvoice = selfEntity.attrInvoices[argIndex]
			except:
				ERROR_MSG( "%s(%i): srcEntityId = %i, no such invoice(argIndex = %i)." % (selfEntity.getName(), selfEntity.id, playerEntity.id, argIndex) )
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
					playerEntity.client.onStatusMessage( csstatus.GOODS_IS_NONE_2, str(( srcItem.name(), )) )
					selfEntity.sellToCB( argIndex, 0, playerEntity.id )	# ��������Ϊ��֪ͨ�ͻ�����Ʒ�ѱ��������
					ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
					return	# û��������
				elif totalAmount[argIndex] > objInvoice.getAmount():
					playerEntity.client.onStatusMessage( csstatus.GOODS_NOT_ENOUGH, str(( srcItem.name(), )) )
					ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
					return	# û��ô���������

			invoiceData = objInvoice.copy()
			#itemData.setAmount( argAmount )
			invoiceItems.append( invoiceData )
			indices.append( argIndex )
			amountList.append( argAmount )


		if len( invoiceItems ) > 0:
			self.onSellItems( selfEntity, playerEntity, invoiceItems, indices, amountList )

	def onSellItems( self, selfEntity, playerEntity, invoiceItems, argIndices, argAmountList ):
		"""
		����ĳ����Ʒ�¼�
		"""
		playerEntity.buyArrayFromNPC( selfEntity, invoiceItems, argIndices, argAmountList )

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
		playerEntity.sellToNPC( selfEntity, argUid, argAmount )

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
		playerEntity.sellArrayToNPC( selfEntity, argUidList, argAmountList )

# Chapman.py
