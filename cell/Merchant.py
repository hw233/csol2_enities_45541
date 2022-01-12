# -*- coding: gb18030 -*-



import BigWorld
import Chapman
from bwdebug import *
from utils import *
import ItemTypeEnum
import ECBExtend

class Merchant( Chapman.Chapman ):
	"""
	"""

	def __init__( self ):
		Chapman.Chapman.__init__( self )

	def sendPriceChangeInfo( self, srcEntityId ):
		"""
		�ɿͻ��˵��ã�������Ʒ�۸�䶯��Ϣ
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		incPriceInfo = BigWorld.globalData["MerchantHighText"]
		decPriceInfo = BigWorld.globalData["MerchantLowText"]
		clientMerchant = srcEntity.clientEntity( self.id )
		clientMerchant.onReceivePriceChangeInfo( ( incPriceInfo, decPriceInfo ) )

	def sellToCB( self, argIndex, argAmount, playerEntityID ):
		"""
		����ҵĻص�

		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: UINT16
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@param	playerEntityID:	����ӵı���������֪ͨ�ͻ�����Ʒ�����ı�
		@type	playerEntityID:	OBJECT_ID
		"""
		if playerEntityID is 0:return
		try:
			playerEntity = BigWorld.entities[playerEntityID]
			objInvoice = self.attrInvoices[argIndex]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, playerEntityID ) )
			return

		Chapman.Chapman.sellToCB( self, argIndex, argAmount, playerEntityID )
		# ֪ͨ�ͻ�����Ʒ�����ı�
		if playerEntity is not None:
			clientMerchant = playerEntity.clientEntity( self.id )
			clientMerchant.onReceiveGoodsAmountChange( argIndex, objInvoice.getAmount() )
	
	
	def reqInvoiceAmount( self, srcEntityId, argIndex ):
		"""
		<Expose/>
		@type  srcEntityId: int
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
			objInvoice = self.attrInvoices[argIndex]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return
		if srcEntity is not None:
			clientMerchant = srcEntity.clientEntity( self.id )
			clientMerchant.onReceiveGoodsAmountChange( argIndex, objInvoice.getAmount() )