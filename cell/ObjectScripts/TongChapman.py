# -*- coding: gb18030 -*-

"""
����ȫ��ʵ��������
"""
# $Id: Chapman.py,v 1.8 2008-08-11 07:24:03 kebiao Exp $
from bwdebug import *
import Chapman
import csstatus
import csdefine
import cschannel_msgs

class TongChapman( Chapman.Chapman ):
	"""
	����ȫ��ʵ�������� for cell��

	@ivar      attrInvoices: �����б�
	@type      attrInvoices: dict
	"""

	def __init__( self ):
		"""
		"""
		Chapman.Chapman.__init__( self )

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
		if selfEntity.ownTongDBID != playerEntity.tong_dbID:
			playerEntity.statusMessage( csstatus.TONG_NPC_IS_TARGET_TONG_NPC )
			return
		elif selfEntity.locked:
			playerEntity.statusMessage( csstatus.TONG_NPC_LOCKED )
			return
		if selfEntity.className == "10111135":		# �������Ҫ��֤����ʽ𣬿��ܲ��ܶԻ�
			tongMailbox = playerEntity.tong_getSelfTongEntity()
			if tongMailbox:
				tongMailbox.onRequestOpenTongShop( selfEntity.base, playerEntity.id, dlgKey )
		else:
			Chapman.Chapman.gossipWith( self, selfEntity, playerEntity, dlgKey )
	
	def onRequestOpenTongShop( self, selfEntity, srcEntityID, talkID, isEnough ):
		"""
		�������˶Ի�
		"""
		try:
			playerEntity = BigWorld.entities[srcEntityID]
		except KeyError:
			INFO_MSG( "entity %i not exist in world" % srcEntityID )	# ���Ӧ����Զ�������ܵ���
			return
		if isEnough:
			Chapman.Chapman.gossipWith( self, selfEntity, playerEntity, talkID )
		else:
			playerEntity.setGossipText( cschannel_msgs.TONG_INFO_27 )
			playerEntity.sendGossipComplete( selfEntity.id )

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
		upperLimit = selfEntity.getItemBuyUpperLimit( srcItem.id )							# ��������
		boughtNum = selfEntity.getRoleBoughtNum( playerEntity.databaseID, srcItem.id )	# �ѹ�������

		if srcItem.getStackable() < argAmount:
			# �����Ƿ�ɵ��ӵ���Ʒ������������ڵ������������
			ERROR_MSG( "stackable less then sell amount" )
			return
		
		# �Ƿ񳬹�ÿ�ܹ�������
		if argAmount + boughtNum > upperLimit:
			allowNum = upperLimit - boughtNum if upperLimit > boughtNum else 0
			playerEntity.statusMessage( csstatus.TONG_WEEK_BUY_TONG_ITEM_MAX, boughtNum, allowNum )
			return

		# ���ڿ�ʼ����Ʒ��
		if objInvoice.getMaxAmount() > 0 and argAmount > objInvoice.getAmount():	# ��Ʒ����������
			playerEntity.client.onStatusMessage( csstatus.GOODS_IS_NONE_1, "" )
			ERROR_MSG( "%s(%i): %s(%i) buy %i '%s', %i only." % ( selfEntity.getName(), selfEntity.id, playerEntity.playerName, playerEntity.id, srcItem.id, argAmount, objInvoice.getAmount() ) )
			return	# û��ô���������
		
		newInvoice = objInvoice.copy()
		self.onSellItem( selfEntity, playerEntity, newInvoice, argIndex, argAmount )

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
			
			upperLimit = selfEntity.getItemBuyUpperLimit( srcItem.id )							# ��������
			boughtNum = selfEntity.getRoleBoughtNum( playerEntity.databaseID, srcItem.id )	# �ѹ�������
			
			if srcItem.getStackable() < argAmount:
				# �����Ƿ�ɵ��ӵ���Ʒ������������ڵ������������
				ERROR_MSG( "stackable less then sell amount" )
				return

			# �Ƿ񳬹�ÿ�ܹ�������
			if totalAmount[argIndex] + boughtNum > upperLimit:
				allowNum = upperLimit - boughtNum if upperLimit > boughtNum else 0
				playerEntity.statusMessage( csstatus.TONG_WEEK_BUY_TONG_ITEM_MAX, boughtNum, allowNum )
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


# Chapman.py
