# -*- coding: gb18030 -*-
#
# 赛马
#

import csdefine
import BigWorld
import random
import csstatus
import event.EventCenter as ECenter
from ItemsFactory import ObjectItem as ItemInfo
from gbref import rds

HORSE_MODEL_PATH = "mount/gw0700/gw0700.model"

class HorseRacer:
	"""
	"""
	def __init__( self ):
		"""
		"""
		pass

	def onRacehorseStart( self ):
		"""
		define method
		赛马开始回调
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RACEHORSE_START" )

	def onRacehorseEnd( self ):
		"""
		define method
		赛马结束回调
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RACEHORSE_END" )
		self.hideRaceTime()
		self.createEquipModel()

	def set_affectAfeard( self, oldValue ):
		"""
		惊恐的技能表现
		"""
		def afeardRun():
			"""
			乱跑
			"""
			if self.affectAfeard:
				self.moveTo( ( self.position.x+random.randint(-3,3), self.position.y, self.position.z+random.randint(-3,3)) )
				BigWorld.callback( 0.5, afeardRun )

		if self.affectAfeard:
			afeardRun()
		else: #防止buff结束后，移动尚未结束 add by wuxo 2013-7-25
			self.flushActionByKeyEvent()
			self.stopMove()

	def addRaceItemCB( self, orderID, itemInstance ):
		"""
		define method
		增加赛马物品
		"""
		self.raceItemsBag.add( orderID, itemInstance )
		itemInfo = ItemInfo( itemInstance )
		ECenter.fireEvent( "EVT_ON_RACEBAG_ADD_ITEM", orderID, itemInfo )

	def swapRaceItems( self, srcOrder, destOrder ):
		"""
		 交换道具
		"""
		self.cell.swapRaceItems( srcOrder, destOrder )

	def swapRaceItemCB( self, srcOrder, dstOrder ):
		"""
		交换道具的回调
		"""
		dstItem = self.raceItemsBag.getByOrder( dstOrder )
		srcItem = self.raceItemsBag.getByOrder( srcOrder )
		if srcItem is None: srcItemInfo = None
		else: srcItemInfo = ItemInfo( srcItem )
		if dstItem is None: dstItemInfo = None
		else: dstItemInfo = ItemInfo( dstItem )
		ECenter.fireEvent( "EVT_ON_RACEBAG_SWAP_ITEMS", srcOrder, srcItemInfo, dstOrder, dstItemInfo )
		self.raceItemsBag.swapOrder( srcOrder, dstOrder )

	def useRacehorseItem( self, orderID ):
		"""
		右键点击普通物品栏的某个物品
		@param 			kitOrder	  : 背包位置
		@type  			kitOrder	  : UINT8
		@param  		orderID		  : 物品位置
		@type   		orderID		  : UINT8
		@return						  : 无
		"""
		item = self.getRacehorseItem_( orderID )
		if item is None : return
		if item.isFrozen():
			self.__isFrozenItemMsg()
			return
		type = item.getType()
		target = self.targetEntity
		if target != None:
			if ( self.position - target.position ).length > 100.0:
				self.statusMessage( csstatus.USE_ITEM_TARGET_NOT_FIND )
				return
			self.cell.useRacehorseItem( item.uid, target.id )
		else:
			self.cell.useRacehorseItem( item.uid, self.id )

	def onRemoveRaceItem( self, orderID ):
		"""
		define method
		移除物品回调
		"""
		self.raceItemsBag.removeByOrder( orderID )
		ECenter.fireEvent( "EVT_ON_RACEBAG_REMOVE_ITEM", orderID )

	def showRaceTime( self ):
		"""
		define method
		显示赛马剩余时间
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_RACE_HORSE_TIME" )

	def hideRaceTime( self ):
		"""
		define method
		隐藏赛马剩余时间
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_RACE_HORSE_TIME" )

	def updateRaceCircle( self ):
		"""
		define method
		更新赛马剩余圈数
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_RACE_CIRCLES" )