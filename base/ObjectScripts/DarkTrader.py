# -*- coding: gb18030 -*-
#
# 2008-12-26 SongPeifang
#
"""
DarkTader类
"""

from NPC import NPC

class DarkTrader( NPC ):
	"""
	投机商人脚本
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )