# -*- coding: gb18030 -*-
# $Id: PasswordOperate.py,v 1.2 2008-06-21 03:14:31 huangyongwei Exp $

from guis import *
from LabelGather import labelGather
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import BigWorld
import csdefine
import GUIFacade

class PasswordOperate( TabPanel ):
	def __init__( self, tabPanel, pyBinder ):
		TabPanel.__init__( self, tabPanel, pyBinder )
		self.lockStatus = -1
		self.callback_ = lambda *args : False
		self.__initTabPanel( tabPanel )

	def __initTabPanel( self, tabPanel ):
		self.__pyPasswordBox = TextBox( tabPanel.pswBox.box, self )
		self.__pyPasswordBox.onTextChanged.bind( self.onTextChange_ )
		self.__pyPasswordBox.inputMode = InputMode.PASSWORD
		self.__pyPasswordBox.maxLength = 6

		self.__pyBtnLock = HButtonEx( tabPanel.btnLock )
		self.__pyBtnLock.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnLock.onLClick.bind( self.__onLock )
		labelGather.setPyBgLabel( self.__pyBtnLock, "PasswordBox:PasswordOperate", "btnLock" )

		self.__pyBtnFore = HButtonEx( tabPanel.btnForever )
		self.__pyBtnFore.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnFore.onLClick.bind( self.__onForeUnlock )
		labelGather.setPyBgLabel( self.__pyBtnFore, "PasswordBox:PasswordOperate", "btnForever" )

		self.__pyBtnUnlock = HButtonEx( tabPanel.btnUnlock )
		self.__pyBtnUnlock.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnUnlock.onLClick.bind( self.__onUnlock )
		labelGather.setPyBgLabel( self.__pyBtnUnlock, "PasswordBox:PasswordOperate", "btnOpen" )

		self.__pyBtnForgetPsw = HButtonEx( tabPanel.btnForgetPsw )
		self.__pyBtnForgetPsw.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnForgetPsw.onLClick.bind( self.__onPswForgot )
		labelGather.setPyBgLabel( self.__pyBtnForgetPsw, "PasswordBox:PasswordOperate", "btnForgetPsw" )

		self.__pyRtLockClew = CSRichText( tabPanel.rtLockClew )
		self.__pyRtLockClew.maxWidth = 165.0
		self.__pyRtLockClew.text = PL_Font.getSource( labelGather.getText( "PasswordBox:PasswordOperate", "lockClew" ),fc = ( 255, 0, 0 ) )

		labelGather.setLabel( tabPanel.passwordText, "PasswordBox:PasswordOperate", "inputText" )


		self.__openTimes = 0
		self.__initNumBtns( tabPanel )

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

	# --------------------------------------------------------
	# private
	#---------------------------------------------------------
	def __onGetActiveBox( self ):
		pyACon = uiHandlerMgr.getTabInUI()

	def __initUIState( self, lockStatus ):	# wsf，初始化按钮状态
		self.lockStatus= lockStatus
		self.__pyPasswordBox.clear()
		self.updateLockStatus( lockStatus )

	# -----------------------------------------------
	def __onEnterNum( self, pyBtn ):
		text = pyBtn.num
		self.__pyPasswordBox.notifyInput( text )

	def __onClearNum( self ):
		self.__pyPasswordBox.clear()

	# ------------------------------------
	def __onLock( self ):
		if self.lockNotify_():
			self.hide( )

	def lockNotify_( self ):
		#text = self.__pyPasswordBox.text.replace( ' ', '' )
		text = ""
		if self.lockStatus == 0:
			# "您还没有设置密码"
			showMessage( 0x0b81,"", MB_OK, pyOwner = self.pyTopParent )
			self.__pyPasswordBox.clear()
			return False
		try:
			self.callback_( PassResult.LOCK, text )
		except :
			EXCEHOOK_MSG()
		self.__pyBtnLock.enable = False
		return True

	# --------------------------------------
	def __onForeUnlock( self ):
		if self.forUnlockNotify_():
			self.hide()

	def forUnlockNotify_( self ):
		passWord = self.__pyPasswordBox.text.replace( ' ', '' )
		if not passWord.isdigit() or len( passWord ) not in range(4, 7):
			# "密码必须为4-6位数字"
			showMessage( 0x0b82,"", MB_OK, pyOwner = self.pyTopParent )
			self.__pyPasswordBox.clear()
			return False
		try:
			self.callback_( PassResult.FOREUNLOCK, passWord )
		except :
			EXCEHOOK_MSG()
		return True
	# ----------------------------------------
	def __onUnlock( self ):
		if self.unLockNotify_():
			self.hide()

	def __onPswForgot( self ) :
		"""
		点击忘记密码按钮
		"""
		showMessage( 0x0b83, "", MB_OK, pyOwner = self )

	def unLockNotify_( self ):
		passWord = self.__pyPasswordBox.text.replace( ' ', '' )
		if not passWord.isdigit() or len( passWord ) not in range(4, 7):
			# "密码必须为4-6位数字"
			showMessage( 0x0b82,"", MB_OK, pyOwner = self.pyTopParent )
			self.__pyPasswordBox.clear()
			return False
		try:
			self.callback_( PassResult.UNLOCK, passWord )
		except :
			EXCEHOOK_MSG()
		return True

	#---------------------------------------------------
	def onTextChange_( self ):	# wsf，文本框状态改变对按钮的影响
		text = self.__pyPasswordBox.text
		self.__pyBtnUnlock.enable = text != "" and self.lockStatus & 0x02 == 0x02
		#self.__pyBtnLock.enable = text != "" and self.lockStatus != 2 and self.lockStatus == 1
		self.__pyBtnFore.enable = text != ""and self.lockStatus & 0x01


	# -------------------------------------------------
	# public
	# -------------------------------------------------
	def show( self, callback, lockStatus ):
		self.callback_ = callback
		self.lockStatus = lockStatus
		self.__initUIState( lockStatus )

	def hide( self ):
		self.pyBinder.hide()

	def updateLockStatus( self, lockStatus ):
		"""
		更新锁定状态
		"""
		isPswSetted = lockStatus & 0x01 == 1
		isLocked = lockStatus & 0x02 == 0x02
		self.__pyBtnLock.enable = isPswSetted and not isLocked 	# 有密码，没有上锁
		self.__pyBtnUnlock.enable = isLocked					# 已经上锁
		self.__pyBtnFore.enable = isLocked
		self.gui.pswBox.visible = isLocked
		self.gui.passwordText.visible = isLocked
		self.__pyRtLockClew.visible = not isLocked

	def keyEventHandler( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了回车键
			if self.__pyBtnUnlock.enable :
				self.__onUnlock()
				return True
		return False