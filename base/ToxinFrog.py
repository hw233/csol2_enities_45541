# -*- coding: gb18030 -*-
#
# 2009-05-25 SongPeifang
#
"""
ToxinFrog��
"""
from Monster import Monster

class ToxinFrog( Monster ):
	"""
	ToxinFrog��
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Monster.__init__( self )
		
	def onFrogDieNotify( self, notifyStr ):
		"""
		����֪ͨ
		"""
		self.getScript().onFrogDieNotify( notifyStr )