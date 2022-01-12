# -*- coding: gb18030 -*-

"""This module implements the Chapman for cell.
"""
# $Id: Chapman.py,v 1.33 2008-08-06 07:23:01 kebiao Exp $

import BigWorld
import NPC
from bwdebug import *
from utils import *
import ItemTypeEnum
import csstatus
import ECBExtend

class Chapman( NPC.NPC ):
	"""An Chapman class for cell.
	����NPC

	@ivar      attrInvoices: �����б�
	@type      attrInvoices: INVOICEITEMS
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )
		self.addTimer( self.invRestoreTime, self.invRestoreTime, ECBExtend.CHAPMAIN_RESTOREINVOICE_CBID )

	def onRestoreInvoices( self, timerID, cbID ):
		"""
		�ָ�������Ʒ���������

		@param timerID: ʹ��addTimer()����ʱ�����ı�־����onTimer()������ʱ�Զ����ݽ���
		@type  timerID: int
		@param    cbID: ��ǰ����������ı�ţ�ͬ����onTimer()������ʱ�Զ����ݽ���
		@type     cbID: int
		@return: ��
		"""
		for i in self.attrInvoices.itervalues():
			i.setAmount( i.maxAmount )

	def sendInvoiceListToClient( self, srcEntityId ):
		"""
		Expose method
		�ṩ��client�ķ�������client���Լ�������Ʒ�б�

		@param srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type  srcEntityId: int
		@return: ��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		#if srcEntity.�����뽻����������״̬��():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), state mode not right, perhaps have a deceive." % (srcEntityId) )
		#	return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#srcEntity.����״̬Ϊ����״̬()
		clientEntity = srcEntity.clientEntity(self.id)
		clientEntity.resetInvoices( len(self.attrInvoices) )
		clientEntity.onInvoiceLengthReceive( len( self.attrInvoices ) )
		### end of getInvoiceList() mothed ###

	def requestInvoice( self, srcEntityId, startPos ):
		"""
		Expose method
		����һ����Ʒ
		@param startPos: ��Ʒ��ʼλ��
		@type startPos: INT16
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return
		if startPos > len( self.attrInvoices ):
			return
		minLen = min( startPos+13, len( self.attrInvoices ) )
		clientEntity = srcEntity.clientEntity( self.id )

		for i in xrange( startPos, minLen+1, 1 ):
			try:
				clientEntity.addInvoiceCB( i, self.attrInvoices[i] )
			except KeyError, errstr:
				ERROR_MSG( "%s(%i): no souch index.", errstr )
				continue

	def sellTo( self, srcEntityId, argIndex, argAmount ):
		"""
		���˰Ѷ����������

		@param srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type  srcEntityId: int
		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: UINT16
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return: 			��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if srcEntity.�Ǻ���():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), it's a pker, here perhaps have a deceive." % (srcEntityId) )
		#	return

		self.getScript().sellTo( self, srcEntity, argIndex, argAmount )
	### end of sellTo() method ###

	def sellArrayTo( self, srcEntityId, argIndices, argAmountList ):
		"""
		���˰Ѷ����������

		@param srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type  srcEntityId: int
		@param argIndices: Ҫ����ĸ���Ʒ
		@type  argIndices: ARRAY <of> UINT16	</of>
		@param argAmountList: Ҫ�������
		@type  argAmountList: ARRAY <of> UINT16	</of>
		@return: 			��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if srcEntity.�Ǻ���():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), it's a pker, here perhaps have a deceive." % (srcEntityId) )
		#	return
		self.getScript().sellArrayTo( self, srcEntity, argIndices, argAmountList )

	def sellToCB( self, argIndex, argAmount, playerEntityID ):
		"""
		define method
		����ҵĻص�

		@param   argIndex: Ҫ����ĸ���Ʒ
		@type    argIndex: UINT16
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@param	playerEntityID:	����ӵı���������֪ͨ�ͻ�����Ʒ�����ı�
		@type	playerEntityID:	OBJECT_ID
		"""
		try:
			objInvoice = self.attrInvoices[argIndex]
		except:
			return
		objInvoice.addAmount( -argAmount )

	def buyFrom( self, srcEntityId, argUid, argAmount ):
		"""
		���˴���������չ�����

		@param srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type  srcEntityId: int
		@param   argUid: Ҫ����ĸ���Ʒ
		@type    argUid: INT64
		@param   argAmount: Ҫ�������
		@type    argAmount: UINT16
		@return: 			��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if srcEntity.�Ǻ���():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), it's a pker, here perhaps have a deceive." % (srcEntityId) )
		#	return
		self.getScript().buyFrom( self, srcEntity, argUid, argAmount )

	### end of buyFrom() method ###

	def buyArrayFrom( self, srcEntityId, argUidList, argAmountList ):
		"""
		���˴���������չ�����������
		�����б����ÿһ��Ԫ�ض�Ӧһ����Ʒ���ڱ�������ʶ��������
		�չ�����������Ʒ�������ҿ������Լ������ܼ�ֵ��������Ͻ�Ǯ�ܺͲ��ᳬ���������Я���Ľ�Ǯ����ʱ��������ۣ�����������ۡ�

		@param    srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type     srcEntityId: int
		@param  argUidList: Ҫ����ĸ���Ʒ
		@type   argUidList: ARRAY OF INT64
		@param  argAmountList: Ҫ�������
		@type   argAmountList: ARRAY OF UINT16
		@return:               ��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if srcEntity.�Ǻ���():
		#	ERROR_MSG( "sellTo(srcEntityId = %i), it's a pker, here perhaps have a deceive." % (srcEntityId) )
		#	return

		# ������������ĳ���
		if len(argUidList) != len(argAmountList):
			ERROR_MSG( "%s(%i): param length not right. argUidList = %i, argAmountList = %i" % (srcEntity.playerName, srcEntity.id,  len(argUidList), len(argAmountList)) )
			srcEntity.clientEntity( self.id ).onBuyArrayFromCB( 0 )	# ����ʧ��
			return
		self.getScript().buyArrayFrom( self, srcEntity, argUidList, argAmountList )

	def repairOneEquip( self, srcEntityId, kitBagID, orderID, repairLevel ):
		"""
		expose method.
		������ҵ�һ��װ��һ��
		@param    srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type     srcEntityId: int
		@param    kitBagID: ��������
		@type     kitBagID: int
		@param    orderID: ��Ʒ����
		@type     orderID: int
		@param    repairLevel: ����ģʽ
		@type     repairLevel: int
		@return   ��
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_REPAIRER ):
			return

		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.repairOneEquip( repairLevel, kitBagID, orderID, self.getRevenueRate(), self.className )

	def repairAllEquip( self, srcEntityId, repairLevel ):
		"""
		expose method.
		��������װ��
		@param    srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type     srcEntityId: int
		"""
		# Ҫ������NPC��"repair"��Ϊ1����
		#if not self.query("repair"):
		#	return
		try:
			srcEntity = BigWorld.entities[srcEntityId]
		except:
			ERROR_MSG( "%s(%i): srcEntityId = %i, no such entity, perhaps have a deceive." % (self.getName(), self.id, srcEntityId) )
			return

		if not self.hasFlag( csdefine.ENTITY_FLAG_REPAIRER ):
			return

		if srcEntity.actionSign( csdefine.ACTION_FORBID_TALK ):				#�ж��Ƿ��ܸ�NPC�Ի� ��ɲ���
			return

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > self.attrDistance:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.repairAllEquip( repairLevel, self.getRevenueRate(), self.className )

	def getRevenueRate( self ):
		"""
		��õ�ǰ���е�˰�ձ���
		"""
		if self.isJoinRevenue:
			spaceType = self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			if BigWorld.globalData.has_key( spaceType + ".revenueRate" ):
				return BigWorld.globalData[ spaceType + ".revenueRate" ]
		return 0

### end of class Chapman ###


# Chapman.py
