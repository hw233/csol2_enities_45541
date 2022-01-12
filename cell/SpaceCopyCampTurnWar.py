# -*- coding: gb18030 -*-


import time
from SpaceCopy import SpaceCopy
from SpaceCopy import SpaceCopy
from bwdebug import *
import cschannel_msgs
import Love3
import csdefine
import csstatus
import BigWorld

class SpaceCopyCampTurnWar( SpaceCopy ):
	"""
	帮会车轮战空间
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		
	def allWarOver( self ):
		"""
		define method
		副本所有对战结束
		"""
		INFO_MSG( "SpaceCopyTongTurnWar(id: %s) all war over!" % self.id )
		self.getScript().allWarOver( self )
		
	def onActivityOver( self ):
		"""
		define method
		活动时间结束
		"""
		self.getScript().onActivityOver( self )
		
	def telportPlayer( self, playerDBID, position ):
		"""
		define method
		传送玩家到出战点
		"""
		self.getScript().telportPlayer( self, playerDBID, position )
		