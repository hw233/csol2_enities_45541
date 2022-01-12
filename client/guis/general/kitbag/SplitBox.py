# -*- coding: gb18030 -*-
#
# $Id: SplitBox.py,v 1.12 2008-06-27 03:17:31 huangyongwei Exp $

"""
implement SplitBox
"""

import csdefine
import GUIFacade
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem

class SplitBox( Window ):
	__instance=None
	def __init__( self ):
		assert SplitBox.__instance is None,"SplitBox instance has been created"
		SplitBox.__instance=self
		panel = GUI.load("guis/general/kitbag/splitbox.gui")
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.posZSegment = ZSegs.L3
		self.activable_ = True
		self.itemInfo = None
		self.__triggers = {}
		self.__registerTriggers()

		self.__pyNumBox = TextBox( panel.splitBox.box )
		self.__pyNumBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyNumBox.inputMode = InputMode.INTEGER
		self.__pyNumBox.filterChars = ['-', '+']
		self.maxLength = 2

		self.__pyBtnOk = Button( panel.btnOk )
		self.__pyBtnOk.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		self.setOkButton( self.__pyBtnOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "KitBag:SplitBox", "btnOk" )

		self.__pyBtnCancel = Button( panel.btnCancel )
		self.__pyBtnCancel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "KitBag:SplitBox", "btnCancel" )

		self.__pySplitItem = SplitItem( panel.splitItem.item )
		labelGather.setLabel( panel.lbTitle, "KitBag:SplitBox", "lbTitle" )
		labelGather.setLabel( panel.splitText, "KitBag:SplitBox", "splitText" )
		self.addToMgr( "splitBox" )

	@staticmethod
	def instance():
		if SplitBox.__instance is None:
			SplitBox.__instance=SplitBox()
		return SplitBox.__instance

	@staticmethod
	def getInstance():
		"""
		return the SplitBox.__instance,there are two
		"""
		return SplitBox.__instance

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass

	# --------------------------------------------------
	# private
	# --------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_UPDATE_SPLIT_ITEM"] = self.__onSetSplitItem
		for trigger in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( trigger, self )

	def __deregisterTriggers( self ) :
		for trigger in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( trigger,self )
	# --------------------------------------------------
	def __onSetSplitItem( self, itemInfo ):
		self.itemInfo = itemInfo
		self.__pySplitItem.update( itemInfo )
		self.__pyBtnOk.enable = self.__pyNumBox.text != "" and self.__pySplitItem.itemInfo is not None
		self.__pyNumBox.tabStop = True


	def __onOk( self ):
		if self.notify_():
			self.hide()

	def __onCancel( self ):
		self.hide()

	def onTextChange_( self ):
		self.__pyBtnOk.enable = self.__pyNumBox.text != "" and self.__pySplitItem.itemInfo is not None

	def notify_( self ):
		numText = self.__pyNumBox.text.replace( ' ', '' )
		if not numText.isdigit():
			return False
		amout = int( numText )
		uid = self.itemInfo.baseItem.uid
		GUIFacade.splitKitbagItem( uid, amout )
		return True

	def onActivated( self ):
		"""
		当窗口激活时被调用
		"""
		self.__pyNumBox.tabStop = True
		Window.onActivated( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def updateSplitItem( self, itemInfo ):
		self.itemInfo = itemInfo
		self.__pySplitItem.update( itemInfo )

	def show( self, pyOwner = None ):
		self.__pyBtnOk.enable = self.__pyNumBox.text != "" and self.__pySplitItem.itemInfo is not None
		Window.show( self, pyOwner )
		self.__pyNumBox.tabStop = True

	def hide( self ):
		self.__pySplitItem.update( None )
		self.__pyNumBox.clear()
		Window.hide( self )
		self.dispose()
		self.removeFromMgr()
		SplitBox.__instance=None
		self.__deregisterTriggers()
		self.__triggers=None

# ------------------------------------------------------------ ---------
class SplitItem( BOItem ):
	def __init__( self, item = None, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.__itemInfo = None
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __addSplitItem( self, pyItem ) :
		GUIFacade.addSplitItem( pyItem.itemInfo.baseItem.uid )

	def __del__(self):
		"""
		just for testing memory leak
		"""
		pass

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		GUIFacade.removeSplitItem( )
		return True

	def onDragStop_( self, pyDrogged ) :
		BOItem.onDragStop_( self, pyDrogged )
		if ruisMgr.isMouseHitScreen() :
			GUIFacade.removeSplitItem( )
		return True

	def onDrop_( self,  pyTarget, pyDropped ) :
		if pyDropped.dragMark != DragMark.KITBAG_WND : return
		self.__addSplitItem( pyDropped )
		BOItem.onDrop_( self, pyTarget, pyDropped )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BOItem.update( self, itemInfo )
#		if itemInfo is not None :
		self.itemInfo = itemInfo
#		self.description = GUIFacade.getSplitDescription( self.index )



	def _getItemInfo( self ):

		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )			# get or set the checking state of the checkbox