# -*- coding: gb18030 -*-
#
# 日光浴海滩贝壳场景物件 2009-01-16 SongPeifang
#

import BigWorld
from bwdebug import *
from QuestBox import QuestBox

class QuestShellBox( QuestBox ):
	"""
	QuestShellBox类
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		QuestBox.__init__( self )
	
	def spawnShell( self ):
		"""
		向cell请求进行刷新
		"""
		if hasattr( self, "cell" ):	# 判断一下cell是否已经创建好
			self.cell.spawnShell()