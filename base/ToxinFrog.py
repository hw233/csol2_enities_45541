# -*- coding: gb18030 -*-
#
# 2009-05-25 SongPeifang
#
"""
ToxinFrog类
"""
from Monster import Monster

class ToxinFrog( Monster ):
	"""
	ToxinFrog类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Monster.__init__( self )
		
	def onFrogDieNotify( self, notifyStr ):
		"""
		死后通知
		"""
		self.getScript().onFrogDieNotify( notifyStr )