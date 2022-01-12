# -*- coding: gb18030 -*-
#
# 2008-12-31 SongPeifang
#
from Merchant import Merchant
import GUIFacade

class DarkTrader( Merchant ):
	"""
	投机商人NPC类客户端
	"""
	def __init__( self ):
		Merchant.__init__( self )

	def leaveWorld( self ) :
		"""
		离开世界
		"""
		GUIFacade.endTradeWithNPC()	# 关掉与投机商人对话的窗口
		Merchant.leaveWorld( self )