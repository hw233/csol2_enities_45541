# -*- coding: gb18030 -*-
# 特殊隐藏型Entity 2009-01-19 SongPeifang & LinQing
"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine

class SpecialHideEntity( NPCObject ):
	"""
	特殊隐藏型Entity。
	最初设计目的：供给玩家钓鱼用。
	玩家钓鱼时，需要知道是否满足在海边的条件，专门供玩家搜索附近的Entity
	这个Entity需要由策划合理的布置一批在海边
	"""
	def __init__( self ):
		"""
		初始化
		"""
		NPCObject.__init__( self )