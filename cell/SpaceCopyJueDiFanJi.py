# -*- coding: gb18030 -*-


from SpaceCopy import SpaceCopy
import time
import BigWorld
import csconst
import Const


class SpaceCopyJueDiFanJi( SpaceCopy ):
	"""
	绝地反击活动副本
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )

	def onRoleRelive( self, baseMailbox, dbid ):
		if dbid == self.params[ "left" ]:
			baseMailbox.cell.onRoleReviveCallBack( self.className, self.getScript().left_playerEnterPoint[ 0 ], self.getScript().left_playerEnterPoint[ 1 ] )
		elif dbid == self.params[ "right" ]:
			baseMailbox.cell.onRoleReviveCallBack( self.className, self.getScript().right_playerEnterPoint[ 0 ], self.getScript().right_playerEnterPoint[ 1 ]  )
