# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar

class SpaceCopyPlotLv40( RootGUI ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyPlotLv40/showHP.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = False
		self.focus = False
		self.addToMgr( "spaceCopyPlotLv40" )
		self.__triggers = {}
		self.__registerTriggers()
		
		self.__pyStStone = StaticText( wnd.stStone )
		self.__pyStStone.text =  labelGather.getText( "SpaceCopyPlotLv40:main", "stStone" )
		
		self.__pyCover = StaticText( wnd.stCover )
		self.__pyCover.text = labelGather.getText( "SpaceCopyPlotLv40:main", "stCover" )
		
		self.__pySTStoneDie = StaticText( wnd.stoneDie )
		self.__pySTStoneDie.text = ""
		
		self.__pySTCoverDie = StaticText( wnd.coverDie )
		self.__pySTCoverDie.text = ""
		
		self.__pySTStoneValue = StaticText( wnd.stonevalue)
		self.__pySTStoneValue.text = ""
		
		self.__pySTCoverValue = StaticText( wnd.covervalue )
		self.__pySTCoverValue.text = ""
		
		self.__pyHBarStone = HProgressBar( wnd.stone )
		self.__pyHBarStone.clipMode ="RIGHT"
		
		self.__pyHBarCover = HProgressBar( wnd.cover )
		self.__pyHBarCover.clipMode = "RIGHT"
		
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_STONE_AND_COVER_SHOW"] = self.show		#显示炉鼎和保护罩血条
		self.__triggers["EVT_ON_STONE_AND_COVER_HIDE"] = self.hide		#隐藏炉鼎和保护罩血条
		self.__triggers["EVT_ON_STONE_UPDATE"] = self.__updateStone			#更新炉鼎血条
		self.__triggers["EVT_ON_COVER_UPDATE"] = self.__updateCover			#更新保护罩血条
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )
			
	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
			
	def __updateStone( self, hp, hpMax ):
		rate = hpMax > 0 and float( hp ) / hpMax or 0
		self.__pySTStoneValue.text = str( hp )
		self.__pyHBarStone.value = rate
		self.__pySTStoneDie.text = ""
		if rate == 0:
			self.__pySTStoneDie.text = labelGather.getText( "SpaceCopyPlotLv40:main", "die" )
			self.__pySTStoneValue.text = ""
		
	def __updateCover( self, hp, hpMax ):
		rate = hpMax > 0 and float( hp ) / hpMax or 0
		self.__pySTCoverValue.text = str( hp )
		self.__pyHBarCover.value = rate
		self.__pySTCoverDie.text = ""
		if rate == 0:
			self.__pySTCoverDie.text = labelGather.getText( "SpaceCopyPlotLv40:main", "die" )
			self.__pySTCoverValue.text = ""
						
	def show( self ):
		RootGUI.show( self )
		self.__pyHBarCover.value = 1.0
		self.__pyHBarStone.value = 1.0	
		
	def hide( self ):
		RootGUI.hide( self )
		self.__pyHBarCover.value = 1.0
		self.__pyHBarStone.value = 1.0
		self.__pySTCoverDie.text = ""
		self.__pySTStoneDie.text = ""
		self.__pySTStoneValue.text = ""
		self.__pySTCoverValue.text = ""	
		
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
				