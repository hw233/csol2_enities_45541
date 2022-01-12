# -*- coding: gb18030 -*-
#
# 2009-01-12 SongPeifang
#

"""
此脚本已可以删掉，但由于NPCMonster配置中还大量使用了ItemChapman，暂时保留，待配置更新再删除。9:06 2010-2-23，wsf
"""

from Chapman import Chapman
import csdefine
from bwdebug import *

class ItemChapman( Chapman ):
	"""
	这种商人是一种特殊的商人
	这种商人出售的物品，不是用钱买，而是用物品来换取的
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
