# -*- coding: gb18030 -*-
#
"""
"""
from Function import Function
import csstatus
import BigWorld

class FuncBuyPointCard( Function ):
	"""
	买点卡界面
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )


	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		if ( BigWorld.globalData.has_key( "pointCardAddr" ) and BigWorld.globalData.has_key( "pointCardWord" ) ):
			player.client.onBuyPointCardInterface()
		else:
			player.statusMessage( csstatus.POINT_CARD_FORBID_CELL_PARAM_NOT_ENOUGH )


	def valid( self, player, talkEntity = None ):
		"""
		"""
		return True


class FuncSellPointCard( Function ):
	"""
	卖点卡界面
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		if ( BigWorld.globalData.has_key( "pointCardAddr" ) and BigWorld.globalData.has_key( "pointCardWord" ) ):
			player.client.onSellPointCardInterface()
		else:
			player.statusMessage( csstatus.POINT_CARD_FORBID_CELL_PARAM_NOT_ENOUGH )

	def valid( self, player, talkEntity = None ):
		"""
		"""
		return True
