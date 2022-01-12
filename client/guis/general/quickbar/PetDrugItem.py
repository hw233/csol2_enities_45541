# -*- coding: gb18030 -*-

import Define
from guis.ItemsBrush import itemsBrush
from AutoFightItem import AutoFightItem

class PetDrugItem( AutoFightItem ) :
	"""
	宠物自动战斗快捷栏药物Item
	"""
	def update( self, itemInfo, isNotInit = True ) :
		AutoFightItem.update( self, itemInfo )
		if itemInfo is not None :
			itemsBrush.attach( self )							# 尝试将道具格子绑定到物品刷
			self.updateUseStatus( itemInfo.checkUseStatus() )	# 更新物品的可使用状态
		else:
			itemsBrush.detach( self )							# 将道具格子从物品刷解绑
			self.updateUseStatus( Define.ITEM_STATUS_NATURAL )
	
	def updateUseStatus( self, itemStatus ) :
		"""
		更新物品可使用状态的表现
		"""
		self.color = Define.ITEM_STATUS_TO_COLOR[ itemStatus ]