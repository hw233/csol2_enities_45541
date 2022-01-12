# -*- coding: gb18030 -*-
#
# $Id: PasswordSetting.py,v 1.11 2008-07-01 02:51:07 wangshufeng Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common import Window
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import BigWorld
import csdefine
import GUIFacade

class PasswordSetting( TabPanel ):

	def __init__( self, tabPanel, pyBinder ):
		TabPanel.__init__( self, tabPanel, pyBinder )
		self.callback_ = lambda *args : False
		self.__pyTextBoxs = []
		self.lockStatus = -1
		self.__initTabPanel( tabPanel )

	def __initTabPanel( self, tabPanel ):
		self.__pyPassWordBox = TextBox( tabPanel.passwordBox.box, self )
#		self.__pyPassWordBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyPassWordBox.inputMode = InputMode.PASSWORD
		self.__pyPassWordBox.maxLength = 6
		self.__pyPassWordBox.width = 44
		self.__pyTextBoxs.append( self.__pyPassWordBox )

		self.__pyConfirmBox = TextBox( tabPanel.confirmBox.box, self )
#		self.__pyConfirmBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyConfirmBox.inputMode = InputMode.PASSWORD
		self.__pyConfirmBox.maxLength = 6
		self.__pyConfirmBox.width = 44
		self.__pyTextBoxs.append( self.__pyConfirmBox )

		self.__pyBtnConfirm = HButtonEx( tabPanel.btnConfirm, self )
		self.__pyBtnConfirm.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnConfirm.onLClick.bind( self.__onConfirmNew )
		labelGather.setPyBgLabel( self.__pyBtnConfirm, "PasswordBox:PasswordSetting", "btnAffirm" )

		self.__pyOldBox = TextBox( tabPanel.oldBox.box, self )
		self.__pyOldBox.inputMode = InputMode.PASSWORD
		self.__pyOldBox.maxLength = 6
		self.__pyOldBox.width = 44
		self.__pyOldBox.enable = True
		self.__pyTextBoxs.append( self.__pyOldBox )

		self.__pyRtSetPsw = CSRichText( tabPanel.rtSetPsw)
		self.__pyRtSetPsw.maxWidth = 165.0
		self.__pyRtSetPsw.text = PL_Font.getSource( labelGather.getText( "PasswordBox:PasswordSetting", "setPsw" ), fc = ( 255, 0, 0 ) )


		"""
		self.__pyOldBtn = Button( tabPanel.oldBtn )
		self.__pyOldBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyOldBtn.onLClick.bind( self.__onConfirmOld )
		self.__pyOldBtn.visible = False
		"""

		self.__pyActiveBox = None
		self.__initNumBtns( tabPanel )

		labelGather.setLabel( tabPanel.newText, "PasswordBox:PasswordSetting", "newPassword" )
		labelGather.setLabel( tabPanel.againText, "PasswordBox:PasswordSetting", "againText" )
		labelGather.setLabel( tabPanel.oldText, "PasswordBox:PasswordSetting", "oldPassword" )
		labelGather.setLabel( tabPanel.numText, "PasswordBox:PasswordSetting", "tipsText" )

	def __initNumBtns( self, tabPanel ):
		self.__pyNumBtns = {}
		for name, item in tabPanel.numsPanel.children:
			if "num_" not in name:continue
			text = str( name.split( "_" )[1] )
			pyNumBtn = Button( item )
			pyNumBtn.setStatesMapping( UIState.MODE_R2C2 )
			pyNumBtn.num = text
			self.__pyNumBtns[text] = pyNumBtn
			if pyNumBtn.num in [str(i) for i in xrange(0,10)]:
				pyNumBtn.onLClick.bind( self.__onEnterNum )
			else:
				pyNumBtn.onLClick.bind( self.__onClearNum )
#				labelGather.setPyBgLabel( pyNumBtn, "PasswordBox:PasswordSetting", "btnClear" )

	#-------------------------------------------------------
	# pravite
	# ------------------------------------------------------
	def __onEnterNum( self, pyBtn ):
		text = pyBtn.num
		self.__pyActiveBox = self.__onGetActiveBox()
		if self.__pyActiveBox is None:return
		self.__pyActiveBox.notifyInput( text )

	def __onClearNum( self ):
		self.__pyActiveBox = self.__onGetActiveBox()
		if self.__pyActiveBox is None:return
		self.__pyActiveBox.clear()

	def __onGetActiveBox( self ):
		pyACon = uiHandlerMgr.getTabInUI()
#		for pyBox in self.__pyTextBoxs:
	#		if isinstance( pyACon, TextBox ):
		return pyACon

	# ----------------------------------------------
	def __onConfirmNew( self ):
		if self.notifyNew_():
			self.__clearText()
			self.hide()

	def notifyNew_( self ):
		passText = self.__pyPassWordBox.text.replace( ' ', '' )
		oldText = self.__pyOldBox.text.replace( ' ', '' )
		confirmText = self.__pyConfirmBox.text.replace( ' ', '' )
		if not passText.isdigit() or \
			not confirmText.isdigit() or \
			len( passText ) not in range(4, 7):
				# "密码必须为4-6位数字"
				showMessage( 0x0ba1,"", MB_OK, pyOwner = self.pyTopParent )
				self.__clearText()
				return False
		if passText != confirmText:
			# "两次输入密码不一致，请重新输入新密码"
			showMessage( 0x0ba2,"", MB_OK, pyOwner = self.pyTopParent )
			self.__clearText()
			return False
		else:
			try:
				if self.lockStatus&0x01:
					self.callback_( PassResult.CHANGERESULT, oldText, confirmText )
				else:
					self.callback_( PassResult.SETRESULT, "", confirmText )
			except :
				EXCEHOOK_MSG()
			return True

	def __onConfirmOld( self ): # 确认旧密码
		pass

	# --------------------------------------------------
	def __clearText( self ):
		for pyBox in self.__pyTextBoxs:
			pyBox.clear()

	#---------------------------------------------
	# public
	# --------------------------------------------
	def show( self, callback, lockStatus ):
		self.callback_ = callback
		self.lockStatus = lockStatus
		self.updateLockStatus( lockStatus )
		self.__clearText()

	def hide( self ):
		self.pyBinder.hide( )

	def dispose(self):
		self.callback_=None
		self.__clearText()

	def updateLockStatus( self, lockStatus ):
		"""
		更新锁定状态
		"""
		isPswSetted = lockStatus & 0x01 == 0x01
		self.gui.oldBox.visible = isPswSetted
		self.gui.oldText.visible = isPswSetted
		self.__pyRtSetPsw.visible = not isPswSetted

	def keyEventHandler( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了回车键
			if self.__pyBtnConfirm.enable :
				self.__onConfirmNew()
				return True
		return False
