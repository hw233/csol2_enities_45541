# -*- coding: gb18030 -*-
#

"""
"""
from SpaceCopy import SpaceCopy
import csconst
import BigWorld

class SpaceCopyDanceHall( SpaceCopy ):
	"""
	用于控制SpaceNormal entity的脚本，所有有需要的SpaceNormal方法都会调用此脚本(或继承于此脚本的脚本)的接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		进入舞厅
		"""
		SpaceCopy.onEnter( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.enterWuTing()
		
	def onLeave( self, selfEntity, baseMailbox, params  ):
		"""
		高开舞厅
		"""
		SpaceCopy.onLeave( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.leaveWuTing()
		


