# -*- coding: gb18030 -*-
#

from interface.GameObject import *
import event.EventCenter as ECenter
import BigWorld
import ItemTypeEnum
from bwdebug import *
import csdefine
import GUI
import Define

class DroppedBox( GameObject ):
	__cc_valid_range	= 30	#拾取范围
	def __init__( self ):
		GameObject.__init__( self )
		self.setSelectable( True )
		self.canPickUp = False
		self.selectable = False
		self.isLooked = False # 箱子是否被拾取过
		self.boxItems = []

	def receiveDropItems( self, itemBox ):				#[ {'order': 1, 'item':item01 }, ...]
		"""
		define method
		"""
		self.boxItems = itemBox
		BigWorld.player().currentItemBoxID = self.id
		ECenter.fireEvent( "EVT_ON_GET_DROP_ITEMS", itemBox )

	def onCacheCompleted( self ):
		"""
		virtual method.
		EntityCache缓冲完毕
		"""
		if not self.inWorld:
			return

		GameObject.onCacheCompleted( self )
		self.cell.droppedBoxStatus()

	def abandonBoxItems( self ):
		"""
		"""
		self.cell.abandonBoxItems()

	def prerequisites( self ):
		"""
		This method is called before the entity enter the world
		"""
		return ["monster/dm_bxiang_00002/dm_bxiang_00002.model"]

	def receiveDropState( self, visibleState ):
		"""
		"""
		if visibleState:
			if (self.model == None):
				self.canPickUp = True
				rds.effectMgr.createModelBG( ["monster/dm_bxiang_00002/dm_bxiang_00002.model"], self.__onModelLoad )
				self.selectable = True	# 设置能够被选中
				BigWorld.player().onItemDrop( self )
				ECenter.fireEvent( "EVT_ON_ITEM_DROPPED", self )
		else:
			self.model = None
	
	def  __onModelLoad( self, model ):
		"""
		模型加载回调
		"""
		if not self.inWorld : return  # 如果已不在视野则过滤
		self.model = model
		rds.effectMgr.createParticleBG( self.model, "HP_sfx1", "particles/tong_tong/diaoluowupin.xml", type = Define.TYPE_PARTICLE_NPC  )

	def pickUpItemByIndex( self, index ):
		"""
		"""
		self.cell.pickDropItem( index )
		
	def pickUpAllItems( self ):
		"""
		通知服务器拾取全部物品
		"""
		self.cell.pickUpAllItems()

	def onBoxItemRemove( self, index ):
		"""
		define method
		"""
		if BigWorld.player().currentItemBoxID != self.id:
			return
		ECenter.fireEvent( "EVT_ON_PICKUP_ONE_ITEM", index )


	def onTargetFocus( self ):
		if ( self.inWorld ):
			rng = self.distanceBB( BigWorld.player() )
			if rng <= self.__cc_valid_range :					#判断距离 如果可以直接交互显示亮图 否则显示灰图
				rds.ccursor.set( "pickup" )						# modified by hyw( 2008.09.12 )
			else:
				rds.ccursor.set( "pickup", True )				# modified by hd( 2008.09.16 )

	def onTargetBlur( self ):
		rds.ccursor.set( "normal" )

	def filterCreator( self ):
		"""
		template method.
		创建entity的filter模块
		"""
		return BigWorld.AvatarDropFilter()

	def leaveWorld( self ):
		"""
		This method is called when the entity leaves the world
		"""
		GameObject.leaveWorld( self )
		if self.selectable :
			ECenter.fireEvent( "EVT_ON_ITEM_PICKUP", self )

	def onLoseTarget( self ) :
		"""
		"""
		if BigWorld.target.entity != self:
			BigWorld.player().stopPickUp()
		GameObject.onLoseTarget( self )

	def pickUpState( self, item ):
		"""
		"""
		ECenter.fireEvent( "EVT_ON_ROLL_UPDATE_ITEM", item )

