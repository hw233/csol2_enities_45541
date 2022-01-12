# -*- coding: gb18030 -*-
# $Id: MoneyTake.py,v 1.12 2008-08-26 02:19:45 huangyongwei Exp $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText
from guis.controls.Button import Button
import BigWorld
import GUIFacade
import csdefine
import csstatus

class BaseBox( Window ):
	"""
	基本输入框
	"""
	def __init__( self ):
		box = GUI.load( "guis/general/tongabout/citywar/biddingbox.gui")
		uiFixer.firstLoadFix( box )
		Window.__init__( self, box )
		self.pyTextBoxs_ = []
		self.__pyActiveBox = None

		self.pyStTitle_ = StaticText( box.stTitle )
		self.pyStTitle_.text = ""

		self.pyGoldBox_ = TextBox( box.goldBox.box, self )
		self.pyGoldBox_.inputMode = InputMode.INTEGER
		self.pyGoldBox_.maxLength = 8
		self.pyGoldBox_.filterChars = ['-', '+']
		self.pyGoldBox_.onTextChanged.bind( self.onTextChange_ )
		self.pyTextBoxs_.append( self.pyGoldBox_ )

		self.pySilverBox_ = TextBox( box.silverBox.box, self )
		self.pySilverBox_.inputMode = InputMode.INTEGER
		self.pySilverBox_.maxLength = 2
		self.pySilverBox_.filterChars = ['-', '+']
		self.pySilverBox_.onTextChanged.bind( self.onTextChange_ )
		self.pyTextBoxs_.append( self.pySilverBox_ )

		self.pyCoinBox_ = TextBox( box.coinBox.box, self )
		self.pyCoinBox_.inputMode = InputMode.INTEGER
		self.pyCoinBox_.maxLength = 2
		self.pyCoinBox_.filterChars = ['-', '+']
		self.pyCoinBox_.onTextChanged.bind( self.onTextChange_ )
		self.pyTextBoxs_.append( self.pyCoinBox_ )

		self.pyBtnCancel_ = Button( box.btnCancel, self )
		self.pyBtnCancel_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnCancel_.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.pyBtnCancel_, "TongAbout:BiddingBox", "btnCancel" )

		self.pyBtnOk_ = Button( box.btnOk, self )
		self.pyBtnOk_.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnOk_, "TongAbout:BiddingBox", "btnOk" )

	def __getActiveBox( self ):
		pyACon = uiHandlerMgr.getTabInUI()
		if pyACon in self.pyTextBoxs_ :
			return pyACon
		return None

	def onTextChange_( self ):
		self.pyBtnOk_.enable = ( self.pyGoldBox_.text != "" and \
		self.pySilverBox_.text != "" and self.pyCoinBox_.text != "" )

	def __onCancel( self ) :
		self.hide()

	def __onMaxPut( self ):
		player = BigWorld.player()

	def __onClear( self ):
		self.__pyActiveBox = self.__getActiveBox()
		if self.__pyActiveBox is None :return
		if self.__pyActiveBox.text == "":return
		self.__pyActiveBox.clear()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self ) :
		for pyBox in self.pyTextBoxs_:
			pyText = pyBox.text.replace( ' ', '' )
			if not pyText.isdigit():
				# "请输入数字"
				showMessage( 0x08c1,"", MB_OK )
				return False
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self, pyOwner = None ) :
		for textBox in self.pyTextBoxs_:
			textBox.text = "0"
		Window.show( self, pyOwner )

	def hide( self ) :
#		self.__onClear()
		Window.hide( self )

	def onLeaveWorld( self ):
		self.__onClear()
		self.hide()
