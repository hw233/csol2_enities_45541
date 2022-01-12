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

# C_PICKUP_TIME 必须要比 C_DESTROY_TIME 大
C_DESTROY_TIME = 150.0		# 销毁时间
C_PICKUP_TIME = 30.0		# 拥有者拾取时间

class DroppedItem( GameObject ):
	"""
	物品的实体类
	@ivar     itemProp: 物品的属性列表
	@type     itemProp: ITEM
	@ivar lockEntityID: 正在捡或只能捡的人
	@type lockEntityID: OBJECT_ID
	"""
	def __init__(self):
		"""
		@summary:	初始化
		"""
		GameObject.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_DROPPED_ITEM )
		#self.addTimer( C_PICKUP_TIME, 0, 1 )	# the first, check pickup time

	def onTimer( self, controllerID, userData ):
		"""
		@summary:	定时销毁
		@type	controllerID	:	int32
		@type	userData		:	int32
		@param	controllerID	:	时间控制器ID
		@param	userData		:	用户数据
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
		拾取一个物品Entity；

		@param  srcEntityID: 调用实体的ID号
		@type   srcEntityID: OBJECT_ID
		@return:             被声明的方法，没有返回值
		"""
		try:
			srcEntity = BigWorld.entities[srcEntityID]
		except:
			return	# 找不到调用者，什么都不用说

		# if not srcEntity.isRole():	# 在这里判断调用者
		#	return

		if self.isDestroyed:
			ERROR_MSG( "target destroyed." )
			return

		if self.position.flatDistTo( srcEntity.position ) > 5.2:	# 5米以外不能捡
			ERROR_MSG( "too far." + str(self.position) + str(srcEntity.position) )
			return

		item = self.itemProp	# 获得自定义类型实例

		if self.pickupEntityID != 0:
			ERROR_MSG( "It's used." )
			return
		if len( self.ownerIDs ) > 0:
			if srcEntityID not in self.ownerIDs:
				srcEntity.statusMessage( csstatus.CIB_MSG_ITEM_NOT_YOUR )
				return

		if self.queryTemp( 'spawnMB', None ) is not None:
			self.queryTemp('spawnMB').cell.entityDead()

		self.pickupEntityID = srcEntityID	# 锁定拾取者，不让其它人再捡或重复捡
		#如果是金钱
		if item.isType( ItemTypeEnum.ITEM_MONEY ):
			srcEntity.pickupMoney( self, item.amount )
		else:
			srcEntity.pickupItem( self, item )


	def pickupCB( self, state ):
		"""
		@param itemEntityID: 拾取物品实体的ID号
		@type  itemEntityID: OBJECT_ID
		@param        state: base告诉cell捡物品的状态，1 成功，0 失败
		@type         state: UINT8
		"""
		if self.isDestroyed:
			return
		if state:
			self.destroy()
		else:
			self.pickupEntityID = 0	# 重新设置捡拾者，让其它人可以捡


	### end of method: pickupCB() ###

# DroppedItem.py
