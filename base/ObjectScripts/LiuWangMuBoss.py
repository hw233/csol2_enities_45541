# -*- coding: gb18030 -*-
#

#
"""

"""

from Monster import Monster
import Love3
import csdefine
import BigWorld

class LiuWangMuBoss( Monster ):
	"""
	地宫六王墓boss脚本
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		Monster.__init__( self )

	def onLiuWangMuBossDieNotify( self, notifyStr ):
		"""
		死后通知
		"""
		Love3.g_baseApp.anonymityBroadcast( notifyStr, [] )