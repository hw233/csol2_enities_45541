# -*- coding:gb18030 -*-

import BigWorld
from gbref import rds
from StatusMgr import BaseStatus
from FishingEngine import FishingEngine
from FishingConsole import FishingConsole
from event import EventCenter as ECenter

# -----------------------------------------------------
# 定义一个捕鱼子状态
# -----------------------------------------------------
class FishingStatus( BaseStatus ):

	def __init__( self ):
		BaseStatus.__init__( self )
		self.fishingConsole = FishingConsole()
		self.fishingEngine = FishingEngine(self.fishingConsole)

	def onEnter( self, oldStatus ):
		"""进入捕鱼状态"""
		self.fishingConsole.init()
		self.fishingEngine.start()
		ECenter.fireEvent("EVT_ON_VISIBLE_ROOTUIS", False)

	def onLeave( self, newStatus ):
		"""离开捕鱼状态"""
		self.fishingEngine.stop()
		self.fishingConsole.release()
		ECenter.fireEvent("EVT_ON_VISIBLE_ROOTUIS", True)

	def handleKeyEvent( self, down, key, mods ) :
		if not rds.uiHandlerMgr.handleKeyEvent(down, key, mods):
			self.fishingConsole.handleKeyEvent(down, key, mods)
		return True
