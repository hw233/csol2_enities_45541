# -*- coding: gb18030 -*-
#
# 2008-12-31 SongPeifang
#
from Merchant import Merchant
import GUIFacade

class DarkTrader( Merchant ):
	"""
	Ͷ������NPC��ͻ���
	"""
	def __init__( self ):
		Merchant.__init__( self )

	def leaveWorld( self ) :
		"""
		�뿪����
		"""
		GUIFacade.endTradeWithNPC()	# �ص���Ͷ�����˶Ի��Ĵ���
		Merchant.leaveWorld( self )