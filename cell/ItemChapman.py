# -*- coding: gb18030 -*-

from Chapman import Chapman

class ItemChapman( Chapman ):

	def __init__( self ):
		Chapman.__init__( self )

	def buyArrayFrom( self, srcEntityId, argUidList, argAmountList ):
		"""
		ItemChapman不能出售物品
		"""
		pass