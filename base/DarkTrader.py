# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
"""
DarkTrader类
"""
from NPC import NPC
from Love3 import g_DarkTraderDatas

class DarkTrader( NPC ):
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )
		# g_DarkTraderDatas.genCollectGoodID( self.className )
		self.currentGoodID = g_DarkTraderDatas._currentGoodID
		
	def onGetCell( self ):
		"""
		cell创建好后，发送投机商人收购的物品ID物品
		"""
		self.cell.receiveCurrntCollectGoodID( self.currentGoodID )
