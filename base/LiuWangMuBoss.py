# -*- coding: gb18030 -*-
#
# 2009-05-25 SongPeifang
#
"""
ToxinFrog��
"""
from Monster import Monster

class LiuWangMuBoss( Monster ):
	"""
	�ع�����ĹBoss
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		Monster.__init__( self )
		
	def onLiuWangMuMonsterDieNotify( self, notifyStr ):
		"""
		����֪ͨ
		"""
		self.getScript().onLiuWangMuMonsterDieNotify( notifyStr )
		
