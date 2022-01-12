# -*- coding: gb18030 -*-
#
# ����
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
		����ʼ�ص�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RACEHORSE_START" )

	def onRacehorseEnd( self ):
		"""
		define method
		��������ص�
		"""
		ECenter.fireEvent( "EVT_ON_ROLE_RACEHORSE_END" )
		self.hideRaceTime()
		self.createEquipModel()

	def set_affectAfeard( self, oldValue ):
		"""
		���ֵļ��ܱ���
		"""
		def afeardRun():
			"""
			����
			"""
			if self.affectAfeard:
				self.moveTo( ( self.position.x+random.randint(-3,3), self.position.y, self.position.z+random.randint(-3,3)) )
				BigWorld.callback( 0.5, afeardRun )

		if self.affectAfeard:
			afeardRun()
		else: #��ֹbuff�������ƶ���δ���� add by wuxo 2013-7-25
			self.flushActionByKeyEvent()
			self.stopMove()

	def addRaceItemCB( self, orderID, itemInstance ):
		"""
		define method
		����������Ʒ
		"""
		self.raceItemsBag.add( orderID, itemInstance )
		itemInfo = ItemInfo( itemInstance )
		ECenter.fireEvent( "EVT_ON_RACEBAG_ADD_ITEM", orderID, itemInfo )

	def swapRaceItems( self, srcOrder, destOrder ):
		"""
		 ��������
		"""
		self.cell.swapRaceItems( srcOrder, destOrder )

	def swapRaceItemCB( self, srcOrder, dstOrder ):
		"""
		�������ߵĻص�
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
		�Ҽ������ͨ��Ʒ����ĳ����Ʒ
		@param 			kitOrder	  : ����λ��
		@type  			kitOrder	  : UINT8
		@param  		orderID		  : ��Ʒλ��
		@type   		orderID		  : UINT8
		@return						  : ��
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
		�Ƴ���Ʒ�ص�
		"""
		self.raceItemsBag.removeByOrder( orderID )
		ECenter.fireEvent( "EVT_ON_RACEBAG_REMOVE_ITEM", orderID )

	def showRaceTime( self ):
		"""
		define method
		��ʾ����ʣ��ʱ��
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_RACE_HORSE_TIME" )

	def hideRaceTime( self ):
		"""
		define method
		��������ʣ��ʱ��
		"""
		ECenter.fireEvent( "EVT_ON_HIDE_RACE_HORSE_TIME" )

	def updateRaceCircle( self ):
		"""
		define method
		��������ʣ��Ȧ��
		"""
		ECenter.fireEvent( "EVT_ON_UPDATE_RACE_CIRCLES" )