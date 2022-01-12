# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.general.spacecopy.spaceCopyJueDiFanJi.CopyJueDiFanJiPanel import CopyJueDiFanJiPanel

class CopyJueDiFanJiBox( RootGUI ):
	def __init__( self ):
		box = GUI.load( "guis/general/spacecopyabout/spaceCopyJueDiFanJi/copyJueDiFanJiBox.gui" )
		uiFixer.firstLoadFix( box )
		RootGUI.__init__( self, box )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "BOTTOM"
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.escHide_ = False
		self.addToMgr()
		self.__flashSign = True # 用于控制窗口闪烁
		self.__initBox( box )
		self.__triggers = {}
		self.__registerTriggers()

	def __initBox( self, box ):
		self.__pyJueDiPanel = CopyJueDiFanJiPanel()
		self.__pyJueDiItem = JueDiItem( box.item.item, self )
		self.__pyJueDiItem.onLClick.bind( self.__showJueDiPanel )

		self.__ringFader = box.fader
		self.__ringFader.speed = 0.4
		self.__ringFader.value = 1.0
		self.__flashID = 0

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_JUEDI_BOX"] = self.__onShow
		self.__triggers["EVT_ON_HIDE_JUEDI_BOX"] = self.__onHide
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# ----------------------------------------------------------
	def __flash( self ):
		"""
		窗口闪烁 淡入淡出
		"""
		BigWorld.cancelCallback( self.__flashID )
		self.__flashID = 0
		if self.__flashSign:
			self.__ringFader.value = 1.0
		else:
			self.__ringFader.value = 0.2
		self.__flashSign = not self.__flashSign
		self.__flashID = BigWorld.callback( self.__ringFader.speed + 0.1, self.__flash )
		
	def __stopFlash( self ):
		"""
		停止闪烁
		"""
		if self.__flashID:
			BigWorld.cancelCallback( self.__flashID )
			self.__flashID = 0
			self.__ringFader.value = 1.0

	def __showJueDiPanel( self, isSelected ):
		if isSelected:
			self.__pyJueDiPanel.clickShow()

	def __onShow( self ):
		self.show()

	def __onHide( self ):
		self.hide()
		ECenter.fireEvent( "EVT_ON_HIDE_JUEDI_PANEL" )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def show( self ):
		RootGUI.show( self )
		self.__flash()

	def hide( self ):
		self.__stopFlash()
		RootGUI.hide( self )

	def onLeaveWorld( self ):
		self.hide()

# -------------------------------------------------------------------------
class JueDiItem( BOItem ):
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.icon = "guis/general/spacecopyabout/spaceCopyJueDiFanJi/tb_jdfj.dds"

	def onDescriptionShow_( self ):
		msg = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiBox", "boxText" )
		toolbox.infoTip.showItemTips( self, msg )
