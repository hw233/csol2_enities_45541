# -*- coding: gb18030 -*-

from DroppedBox import DroppedBox
import items
import BigWorld
import csdefine

g_items = items.instance()

ZHAOCAI_ITEM_ID = 60101008						#招财宝箱ID

class DroppedBoxForMonsterAttack( DroppedBox ):
	"""
	"""
	def __init__( self ):
		DroppedBox.__init__( self )
		self.isFixed = False
		self.setEntityType( csdefine.ENTITY_TYPE_MONSTER_ATTACK_BOX )


	def displayOnClient( self, srcEntityID ):
		"""
		是否在客户端显示
		"""
		return True


	def queryDropItems( self, srcEntityID ):
		"""
		"""
		player = BigWorld.entities[srcEntityID]
		if not self.isFixed and player.removeItemTotal( self.key_itemID, 1, csdefine.DELETE_ITEM_MONSTER_ATTACK ):
			self.isFixed = True
			itemList = []
			for i in xrange( 0, 5 ):
				itemList.append( g_items.createDynamicItem( ZHAOCAI_ITEM_ID , 1 ) )
			self.init( ( srcEntityID, 0 ), itemList )
		DroppedBox.queryDropItems( self, srcEntityID )