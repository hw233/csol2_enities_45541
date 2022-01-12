# -*- coding: gb18030 -*-
#
# 野外任务怪脚本文件 2009-02-12 SongPeifang
#

from Monster import Monster
import csdefine
import Resource.AIData

class QuestNPCMonster( Monster ):
	"""
	"""	
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		# 初始化附加数据放在前头
		Monster.initEntity( self, selfEntity )
		selfEntity.changeToNPC()