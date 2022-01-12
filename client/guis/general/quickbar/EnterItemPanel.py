# -*- coding: gb18030 -*-
# fangpengjun
#

from guis import *
import event.EventCenter as ECenter
from guis.common.PyGUI import PyGUI
from guis.controls.Icon import Icon
from Function import Functor
from Time import Time
import Timer

PLAY_REMAIN_TIME = 1.2
class EnterItemPanel( PyGUI ):
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.visible = True
		self.__pyEnterIcon = Icon( panel.enterIcon )
		self.__pyEnterIcon.visible = True
		self.__pyEnterIcon.icon = ""
		self.playTimerID = 0
		self.isPlaying = False

	# -------------------------------------------------
	def onPlayIcon( self, itemInfo ):
		if itemInfo is None:return
		if not rds.statusMgr.isInWorld():return
		self.isPlaying = True
		self.__pyEnterIcon.visible = True
		self.__pyEnterIcon.icon = itemInfo.icon
		self.endTime = Time.time() + PLAY_REMAIN_TIME
		self.playTimerID = Timer.addTimer( 0.0, 0.1, Functor( self.__playIconEnter, itemInfo ) )

	def __playIconEnter( self, itemInfo ):
		if not self.rvisible:
			self.__cancelPlayTimer()
			return
		remainTime = self.endTime - Time.time()
		self.__pyEnterIcon.top += 8.0
		self.__pyEnterIcon.left += 8.0
		self.__pyEnterIcon.alpha -= 20
		self.__pyEnterIcon.width -= 5.0
		self.__pyEnterIcon.height -= 5.0
		if remainTime <= 0.0:
			name = rds.iconsSound.getDragDownSound( itemInfo.icon[0] )
			rds.soundMgr.playUI( name )
			self.isPlaying = False
			self.__cancelPlayTimer( )

	def __cancelPlayTimer( self ):
		Timer.cancel( self.playTimerID )
		self.__resetIcon()
		self.playTimerID = 0

	def __resetIcon( self ):
		self.__pyEnterIcon.top = 0
		self.__pyEnterIcon.left = 0
		self.__pyEnterIcon.alpha = 255
		self.__pyEnterIcon.size = 48.0, 48.0
		self.__pyEnterIcon.icon = ""

	def reset( self ):
		self.__resetIcon()