# -*- coding:gb18030 -*-

from SpaceMultiLine import SpaceMultiLine
from bwdebug import *
import Const

DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME = 10


class SpaceCopyFishingJoy( SpaceMultiLine ):
	def __init__( self ):
		SpaceMultiLine.__init__( self )
	
	def onTimer( self, id, userArg ):
		"""
		覆盖底层的onTimer()处理机制
		"""
		if userArg == Const.SPACE_COPY_CLOSE_CBID:
			self.base.closeSpace( True )
			return
		SpaceMultiLine.onTimer( self, id, userArg )
		
	def onLeave( self, baseMailbox, params ):
		SpaceMultiLine.onLeave( self, baseMailbox, params )
		self.playerCount -= 1
		if self.playerCount == 0:
			self.addTimer( DESTROY_SPACE_AFTER_LEAVE_SPACE_TIME, 0, Const.SPACE_COPY_CLOSE_CBID )
			
	def onEnter( self, baseMailbox, params ):
		SpaceMultiLine.onEnter( self, baseMailbox, params )
		self.playerCount += 1
		