# -*- coding: gb18030 -*-
#

"""
"""
from Space import Space
import csconst

class SpaceDance( Space ):
	"""
	用于控制SpaceNormal entity的脚本，所有有需要的SpaceNormal方法都会调用此脚本(或继承于此脚本的脚本)的接口
	"""
	def __init__( self ):
		"""
		初始化
		"""
		Space.__init__( self )

	def onEnter( self, selfEntity, baseMailbox, params ):
		"""
		进入舞厅
		"""
		Space.onEnter( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.addWuTingBuff()
		baseMailbox.cell.enterWuTing()
		
	def onLeave( self, selfEntity, baseMailbox, params  ):
		"""
		高开舞厅
		"""
		Space.onLeave( self, selfEntity, baseMailbox, params )
		baseMailbox.cell.leaveWuTing()


