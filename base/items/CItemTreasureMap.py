# -*- coding: gb18030 -*-
"""
藏宝图物品类。
"""
import ItemAttrClass
import Love3
from CItemBase import CItemBase

class CItemTreasureMap( CItemBase ):
	"""
	自定义类型道具实例，主要用于保存和传输一些道具的易变属性
	"""
	def __init__( self, srcData ):
		"""
		@param srcData: 物品的原始数据
		"""
		CItemBase.__init__( self, srcData )