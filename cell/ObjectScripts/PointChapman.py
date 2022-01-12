# -*- coding: gb18030 -*-
#
# 2009-01-12 SongPeifang
#

"""
此脚本可以不需要了，但配置中还有用到，暂时保留，等配置更新再删除。12:00 2010-2-26，wsf
"""

from Chapman import Chapman
import csdefine

class PointChapman( Chapman ):
	"""
	这种商人是一种特殊的商人
	这种商人出售的物品，不是用钱买，而是用跳舞积分来换取的
	"""

	def __init__( self ):
		"""
		"""
		Chapman.__init__( self )

	def onSellItem( self, selfEntity, playerEntity, newInvoice, argIndex, argAmount ):
		"""
		销售某物品事件
		"""
		playerEntity.buyFromNPC( selfEntity, newInvoice, argIndex, argAmount )

	def onSellItems( self, selfEntity, playerEntity, invoiceItems, argIndices, argAmountList ):
		"""
		销售某类物品事件
		"""
		playerEntity.buyArrayFromNPC( selfEntity, invoiceItems, argIndices, argAmountList )
