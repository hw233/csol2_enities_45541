# -*- coding: gb18030 -*-

import time
import BigWorld
from bwdebug import *
import csdefine
import csconst
import csstatus
from NPC import NPC
import ECBExtend
import Math


DESTROY_DELAY_TIME = 1
GOTO_OWNER_TRY_COUNT = 5

class EidolonNPC( NPC ):
	"""
	С����NPC
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_EIDOLON_NPC )
		if self.ownerLevel > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:
			self.bornTime = int( time.time() )	# ����ʱ�䣬all_clients,��֪ͨ�����ͻ���
			self.lifetime = csconst.VIP_EIDOLON_LIVE_TIME
			self.addTimer( self.lifetime, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )

	def onDestroySelfTimer( self, timerID, cbID ):
		"""
		virtual method.
		ɾ������
		"""
		if not self.queryTemp( "isLock", False ):	# ��û������ô�������ٴ���������timer������С�����ں���ҽ�����������ɵ�����
			self.addTimer( DESTROY_DELAY_TIME, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
			self.setTemp( "isLock", True )
			return
		self._destroy()

	def giveControlToOwner( self ):
		"""
		Define method.
		����Ȩ��������
		"""
		self.controlledBy = None
		self.controlledBy = self.baseOwner

	def clientReady( self, srcEntityID ):
		"""
		Exposed method.
		owner�Ŀͻ���֪ͨС�����client׼�����˿��Խ���controlledBy��
		"""
		if srcEntityID != self.ownerID:
			return
		try:
			owner = BigWorld.entities[self.ownerID]
		except KeyError:
			self.baseOwner.cell.conjureEidolonSuccess( self.base ) # ֪ͨ�����ٻ��ɹ�
		else:
			owner.conjureEidolonSuccess( self.base )

	def getOwnerID( self ):
		"""
		����Լ����˵� id
		"""
		return self.ownerID
	
	def getOwner( self ):
		if BigWorld.entities.get( self.getOwnerID() ):
			owner = BigWorld.entities[ self.getOwnerID() ]
			if owner.isReal():
				return owner
		
		return self.baseOwner.cell
		
	def gotoOwner( self ):
		"""
		for real
		"""
		self.controlledBy = None
		self.addTimer( 2.0, 0.0, ECBExtend.FLY_TO_MASTER_CB )
	
	def flyToMasterCB( self, controllerID, userData ):
		"""
		timer callback
		use arg ECBExtend.FLY_TO_MASTER_CB
		"""
		count = self.queryTemp( "gotoOwnerTryCount", 0 )
		if count >= GOTO_OWNER_TRY_COUNT:			# ����GOTO_OWNER_TRY_COUNT�Σ�����޷����ͣ���ô��������
			self.destroyEidolon()
			return
			
		self.setTemp( "gotoOwnerTryCount", count+1 )
		self.getOwner().eidolonTeleport()
		
	def teleportToOwner( self, owner, spaceID, position, direction ):
		"""
		define method
		���鴫��
		"""
		# ���ڵ�ǰ cellapp �ҵ�ָ���� entity ������ entity ��ͬһ�� space �����ͬ��ͼ����
		# Ŀ��spaceID�뵱ǰ��ͼ��spaceID��ͬ������ͬ��ͼ����
		self.openVolatileInfo()
		if spaceID == self.spaceID:
			self.teleport( None, position + Math.Vector3( 0, 2, 0), direction )
		else:
			self.teleport( owner, position + Math.Vector3( 0, 2, 0), direction )
		self.giveControlToOwner()
		self.removeTemp( "gotoOwnerTryCount" )
		
	def onDestroy( self ):
		"""
		entity ���ٵ�ʱ����BigWorld.Entity�Զ�����
		"""
		self.baseOwner = None # ԭ���pet.onDestroy
		NPC.onDestroy( self )

	def destroyEidolon( self ):
		"""
		define method
		����С����
		"""
		if self.ownerLevel > csconst.AUTO_CREATE_EIDOLON_NPC_LEVEL:
			self.onDestroySelfTimer( 0 ,0 )
		else:
			self._destroy()

	def _destroy( self ):
		self.controlledBy = None	# ���PlayerRole�ͻ��˲Ż�����С����(���ɣ�����һ��)
		self.baseOwner.cell.onEidolonDestory()
		self.destroy()

	def doRandomWalk( self ):
		"""
		С���鲻��Ҫ����߶�������֮
		"""
		pass

	def onThink( self ):
		"""
		virtual method.
		"""
		if not self.canThink():
			return

		if self.state == csdefine.ENTITY_STATE_FIGHT:
			self.onFightAIHeartbeat_AIInterface_cpp()
		else:
			self.onNoFightAIHeartbeat()

		self.think( 1.0 )

	def changeModel( self, modelNum, modelScale ):
		"""
		Define method.
		�ı�ģ��

		@param modelNum : ģ�ͱ��
		@type modelNum : STRING
		@pram modelScale : ģ�����ű���
		@type modelScale : FLOAT
		"""
		self.modelNumber = modelNum
		self.modelScale = modelScale

	def vipShare( self, shareVIPLevel ):
		"""
		Define method.
		����vip����

		@param isOpen : �Ƿ񿪹���
		@type isOpen : BOOL
		"""
		self.isShare = True
		self.shareVIPLevel = shareVIPLevel

	def stopShare( self ):
		"""
		Define method.
		ֹͣ����
		"""
		self.isShare = False
		self.shareVIPLevel = csdefine.ROLE_VIP_LEVEL_NONE

	def onOwnerVIPLevelChange( self, ownerVIPLevel ):
		"""
		Define method.
		���˵�vip����ı���

		@param ownerVIPLevel
		"""
		self.shareVIPLevel = ownerVIPLevel

	def onOwnerLeaveTeam( self ):
		"""
		Define method.
		�����뿪�˶���
		"""
		self.ownerTeamID = -1

	def onOwnerJoinTeam( self, ownerTeamID ):
		"""
		Define method.
		���˼����˶���

		@param captainID : ����Ķӳ�id
		"""
		self.ownerTeamID = ownerTeamID

	# --------------------------------------------------------------------------
	# ���ܵ�ʦ����
	# --------------------------------------------------------------------------
	def trainPlayer( self, srcEntityId, skillID ):
		"""
		ѵ�����

		@param srcEntityId: ����ʹ����<Expose/>���������ϵͳ�Զ����ݽ����ģ���ʾ���ĸ�client�ϵĵ���
		@type  srcEntityId: int
		@param     skillID: Ҫѵ���ļ���
		@type      skillID: INT
		@return: 			��
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		#if not self.validLearn( srcEntity, skillID ):
		if not self.getScript().validLearn( srcEntity, skillID ):
			srcEntity.statusMessage( csstatus.LEARN_SKILL_FAIL )		# hyw
			return

		state = self.spellTarget( skillID, srcEntityId )
		if state != csstatus.SKILL_GO_ON:
			INFO_MSG( "%i: skill %i use state = %i." % ( self.id, skillID, state ) )

	def sendTrainInfoToPlayer( self, srcEntityId, researchType ):
		"""
		"""
		srcEntity = BigWorld.entities[srcEntityId]

		# ȷ���û�����ľ�����
		if self.position.flatDistTo( srcEntity.position ) > 10:
			ERROR_MSG( "%s(%i): srcEntityId = %i, distance too far(%i meter), perhaps have a deceive." % (self.getName(), self.id, srcEntityId, self.position.flatDistTo( srcEntity.position )) )
			return

		srcEntity.clientEntity( self.id ).receiveTrainInfos( list( self.getScript().attrTrainInfo )	)	# attrTrainInfo declare in srcClass()


	# --------------------------------------------------------------------------
	# ���˹���
	# --------------------------------------------------------------------------
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
		clientEntity.resetInvoices( len(self.getScript().attrInvoices) )
		clientEntity.onInvoiceLengthReceive( len( self.getScript().attrInvoices ) )
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
		if startPos > len( self.getScript().attrInvoices ):
			return
		minLen = min( startPos+13, len( self.getScript().attrInvoices ) )
		clientEntity = srcEntity.clientEntity( self.id )

		for i in xrange( startPos, minLen+1, 1 ):
			try:
				clientEntity.addInvoiceCB( i, self.getScript().attrInvoices[i] )
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
			objInvoice = self.getScript().attrInvoices[argIndex]
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