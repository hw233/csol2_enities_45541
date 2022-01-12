# -*- coding: gb18030 -*-
#
"""
This module implements the DroppedItem entity type.
"""
#$Id: DroppedItem.py,v 1.31 2008-02-15 02:33:32 phw Exp $
import BigWorld
import ItemTypeEnum
import csstatus
from bwdebug import *
from interface.GameObject import GameObject
import csdefine

# C_PICKUP_TIME ����Ҫ�� C_DESTROY_TIME ��
C_DESTROY_TIME = 150.0		# ����ʱ��
C_PICKUP_TIME = 30.0		# ӵ����ʰȡʱ��

class DroppedItem( GameObject ):
	"""
	��Ʒ��ʵ����
	@ivar     itemProp: ��Ʒ�������б�
	@type     itemProp: ITEM
	@ivar lockEntityID: ���ڼ��ֻ�ܼ����
	@type lockEntityID: OBJECT_ID
	"""
	def __init__(self):
		"""
		@summary:	��ʼ��
		"""
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_DROPPED_ITEM )
		#self.addTimer( C_PICKUP_TIME, 0, 1 )	# the first, check pickup time

	def onTimer( self, controllerID, userData ):
		"""
		@summary:	��ʱ����
		@type	controllerID	:	int32
		@type	userData		:	int32
		@param	controllerID	:	ʱ�������ID
		@param	userData		:	�û�����
		"""
		if userData == 1:
			self.ownerIDs = []						# reset to accept all player pickup
			if not self.queryTemp( 'spawnMB', None ):
				self.addTimer( C_DESTROY_TIME, 0, 2 )	# the second, will destroy myself
		else:
			self.destroy()

	def addPickupID( self, ownerID ):
		self.ownerIDs.append( ownerID )

	def pickup( self, srcEntityID ):
		"""
		ʰȡһ����ƷEntity��

		@param  srcEntityID: ����ʵ���ID��
		@type   srcEntityID: OBJECT_ID
		@return:             �������ķ�����û�з���ֵ
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityID]
		except:
			return	# �Ҳ��������ߣ�ʲô������˵

		# if not srcEntity.isRole():	# �������жϵ�����
		#	return

		if self.isDestroyed:
			ERROR_MSG( "target destroyed." )
			return

		if self.position.flatDistTo( srcEntity.position ) > 5.2:	# 5�����ⲻ�ܼ�
			ERROR_MSG( "too far." + str(self.position) + str(srcEntity.position) )
			return

		item = self.itemProp	# ����Զ�������ʵ��

		if self.pickupEntityID != 0:
			ERROR_MSG( "It's used." )
			return
		if len( self.ownerIDs ) > 0:
			if srcEntityID not in self.ownerIDs:
				srcEntity.statusMessage( csstatus.CIB_MSG_ITEM_NOT_YOUR )
				return

		if self.queryTemp( 'spawnMB', None ) is not None:
			self.queryTemp('spawnMB').cell.entityDead()

		self.pickupEntityID = srcEntityID	# ����ʰȡ�ߣ������������ټ���ظ���
		#����ǽ�Ǯ
		if item.isType( ItemTypeEnum.ITEM_MONEY ):
			srcEntity.pickupMoney( self, item.amount )
		else:
			srcEntity.pickupItem( self, item )


	def pickupCB( self, state ):
		"""
		@param itemEntityID: ʰȡ��Ʒʵ���ID��
		@type  itemEntityID: OBJECT_ID
		@param        state: base����cell����Ʒ��״̬��1 �ɹ���0 ʧ��
		@type         state: UINT8
		"""
		if self.isDestroyed:
			return
		if state:
			self.destroy()
		else:
			self.pickupEntityID = 0	# �������ü�ʰ�ߣ��������˿��Լ�


	### end of method: pickupCB() ###

# DroppedItem.py
