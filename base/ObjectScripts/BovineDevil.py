# -*- coding: gb18030 -*-
#
# 2009-05-25 SongPeifang
#
"""
BovineDevil类
"""

from Monster import Monster
import Love3
import csdefine
import BigWorld

class BovineDevil( Monster ):
	"""
	牛魔王脚本
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
		Love3.g_baseApp.anonymityBroadcast( notifyStr, [] )