# -*- coding: gb18030 -*-
import copy
import random
from SpaceCopy import SpaceCopy
import BigWorld
from bwdebug import *

CLOSESPACE = 1
class SpaceCopyLiuWangMu( SpaceCopy ):
	# 六王墓
	def __init__( self ):
		SpaceCopy.__init__( self )
		BigWorld.globalData["LiuWangMuMgr"].registerSpace(self, self.getScript().className)
		DEBUG_MSG("init spacecopy liuwangmu ,spacename is %s"%self.getScript().className)
		
	def startCloseCountDownTimer( self, time ):
		#define method 
		self.addTimer(time, 0, CLOSESPACE)
		
	def onTimer(self, id, userArg):
		SpaceCopy.onTimer(self, id, userArg)
		if userArg == CLOSESPACE:	
			self.cell.readyToClosed()	
			self.closeSpace()
