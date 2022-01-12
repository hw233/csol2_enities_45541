# -*- coding: gb18030 -*-
#

from Quest import Quest
import csdefine

class Quest108Star( Quest ):
	"""
	只能完成指定次数的任务
	"""
	def __init__( self ):
		Quest.__init__( self )
		self._style =  csdefine.QUEST_STYLE_108_STAR		# 任务类别

