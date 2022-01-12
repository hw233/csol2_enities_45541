# -*- coding: gb18030 -*-

# implement the life fungus item
# written by ganjinxing 2009-12-4


from CItemBase import CItemBase
import csdefine

class CLifeFungus( CItemBase ) :

	def onAdd( self, owner ):
		"""
		玩家获得这个物品时头顶要显示蘑菇标记
		"""
		CItemBase.onAdd( self, owner )
		owner.tong_showFungusFlag()

	def onDelete( self, owner ):
		"""
		玩家删除物品
		"""
		CItemBase.onDelete( self, owner )
		for item in owner.getAllItems() :		# 如果玩家身上没有了生命蘑菇这个物品，则移除头顶蘑菇标记
			if self.id == item.id :
				return
			owner.tong_removeFungusFlag()