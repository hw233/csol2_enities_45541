# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
"""
DarkTrader��
"""
from NPC import NPC
from Love3 import g_DarkTraderDatas

class DarkTrader( NPC ):
	"""
	NPC����
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )
		# g_DarkTraderDatas.genCollectGoodID( self.className )
		self.currentGoodID = g_DarkTraderDatas._currentGoodID
		
	def onGetCell( self ):
		"""
		cell�����ú󣬷���Ͷ�������չ�����ƷID��Ʒ
		"""
		self.cell.receiveCurrntCollectGoodID( self.currentGoodID )
