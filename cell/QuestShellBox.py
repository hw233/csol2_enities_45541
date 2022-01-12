# -*- coding: gb18030 -*-
#
# 贝壳场景物件 2009-01-16 SongPeifang

from QuestBox import QuestBox


class QuestShellBox( QuestBox ) :
	"""
	贝壳场景物件类
	"""

	def __init__( self ) :
		QuestBox.__init__( self )
		if self.isShow == 0 or self.isShow == None:
			self.addFlag( 0 )	# 箱子专用，可能会与FLAG_*冲突，但如果没有特殊原因，应该没有问题
			self.setTemp( "quest_box_destroyed", 1 )
		
	def spawnShell( self ):
		"""
		Define method.
		让贝壳刷出来
		"""
		self.removeFlag( 0 )	# 箱子专用，可能会与FLAG_*冲突，但如果没有特殊原因，应该没有问题
		self.removeFlag( 1 )	# 针对于不隐藏的场景物件，为了使客户端能得到触发
		self.removeTemp( "quest_box_destroyed" )


	def isMoving( self ):
		"""
		判断entity当前是否正在移动中

		@return: BOOL
		@rtype:  BOOL
		"""
		return False
