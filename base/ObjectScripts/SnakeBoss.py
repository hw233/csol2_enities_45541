# -*- coding: gb18030 -*-
#
# 2009-05-25 SongPeifang
#
"""
SnakeBoss类
"""

from Monster import Monster
import Love3
import csdefine
import BigWorld

class SnakeBoss( Monster ):
	"""
	白蛇妖脚本
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Monster.__init__( self )